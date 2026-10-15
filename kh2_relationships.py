"""KH2 stock/equipment transactions and recognized standard-data AP budgets.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from collections import Counter
import struct
from kh2_items import STOCK_ITEMS, ITEM_TO_STOCK
from kh2_ap_tables import ABILITY_AP, EQUIPMENT, EQUIPMENT_STATS, LEVEL_AP
from kh2_acquisition import Kh2Acquisition, MAGIC_STOCK


def stock_section(kind):
    if kind in (0,1):return 'Items'
    if 2<=kind<=13:return 'Weapons'
    if kind in (14,15):return 'Equipment'
    if kind==16:return 'Materials'
    return 'Special items'


class Kh2Relationships:
    def __init__(self,raw,field_type,names):
        self.raw,self.field_type,self.names=raw,field_type,names
        self.records={}
        self.slots={}
        self.acquisition=Kh2Acquisition(raw,field_type)

    @staticmethod
    def word(raw,offset):return struct.unpack_from('<H',raw,offset)[0]

    def record(self,fields,slot,record):
        self.records[slot]=record
        self.acquisition.record(fields,slot,record)
        for position in range(320):
            if position in MAGIC_STOCK:continue
            offset=record+0x3580+position;value=self.raw[offset]
            item=STOCK_ITEMS.get(position)
            label=item[1] if item else f'Unidentified stock position {position:03d}'
            fields.append(self.field_type(f'inventory:{position}',label,value,offset,'<B',0,
                99 if value<=99 else 255,'Inventory',readonly=not item or value>99,
                item_id=item[0] if item else None,
                collection=stock_section(item[2]) if item else 'Other entries',
                note=('Bag quantity before equipment transfers. Equipping consumes one bag copy; replacing equipment returns its old copy. Story rewards are not synthesized.'
                      if item and value<=99 else 'Unmapped or unsupported stock is preserved without guessing an item identity or quantity rule.')))
        tracked={}
        for character,name in enumerate(self.names):
            base=record+0x24f0+character*0x114
            if character>=3 and not self.raw[base+15]:continue
            if character<3:tracked[f'character:{character}:weapon']=(base,({2},{3},{4})[character])
            for count_delta,array_delta,kind,title in ((16,20,14,'armor'),(17,36,15,'accessory'),(18,52,0,'item')):
                count=self.raw[base+count_delta]
                if count>8:continue
                for n in range(count):tracked[f'character:{character}:{title}:{n}']=(base+array_delta+n*2,{kind})
            budget=self.budget(self.raw,record,character)
            if budget is not None:
                used,capacity=budget
                for key,label,value in (('ap_used','Equipped ability AP',used),('ap_capacity','Available AP',capacity)):
                    fields.append(self.field_type(f'character:{character}:{key}',name+' · '+label,value,0,'',0,1024,'Abilities',readonly=True,
                        note='Calculated from standard Final Mix level, boost, equipment and ability tables. Equipment-granted abilities do not consume learned-ability AP. Modified game tables can differ.'))
        for form in (0,3,4):tracked[f'form:{form}:weapon']=(record+0x32f4+form*0x38,{2})
        self.slots[slot]=tracked

    def budget(self,raw,record,character):
        base=record+0x24f0+character*0x114;level=raw[base+15]
        if not 1<=level<=99:return None
        counts=raw[base+16:base+18]
        if any(n>8 for n in counts):return None
        equipped=[(self.word(raw,base),({2},{3},{4})[character] if character<3 else set(range(2,14)))]
        for count,delta,kind in zip(counts,(20,36),(14,15)):
            equipped.extend((self.word(raw,base+delta+n*2),{kind}) for n in range(count))
        bonus=0
        for identifier,kinds in equipped:
            if not identifier:continue
            entry=EQUIPMENT.get(identifier)
            if entry is None or entry[0] not in kinds or entry[1] not in EQUIPMENT_STATS:return None
            bonus+=EQUIPMENT_STATS[entry[1]][1]
        used=0
        for n in range(80):
            word=self.word(raw,base+84+n*2)
            if not word&0x8000:continue
            identifier=word&0x7fff
            if identifier==0:continue
            if identifier not in ABILITY_AP:return None
            used+=ABILITY_AP[identifier]
        capacity=LEVEL_AP[character][level-1]+raw[base+8]+bonus
        # Do not infer a runtime representation beyond the normal byte budget.
        if capacity>255:return None
        return used,capacity

    def finish(self,result,changes):
        for slot,record in self.records.items():
            edits={key for (i,key) in changes if i==slot}
            delta=Counter()
            for key,(offset,kinds) in self.slots[slot].items():
                if key not in edits:continue
                old,new=self.word(self.raw,offset),self.word(result,offset)
                if old==new:continue
                for identifier in (old,new):
                    if not identifier:continue
                    if identifier not in ITEM_TO_STOCK or EQUIPMENT.get(identifier,(None,))[0] not in kinds:
                        raise ValueError('Cannot transfer unsupported KH2 equipment between the bag and this slot.')
                if old:delta[old]+=1
                if new:delta[new]-=1
            # All slot changes are one transaction, permitting swaps without a spare bag copy.
            for identifier,amount in delta.items():
                if not amount:continue
                offset=record+0x3580+ITEM_TO_STOCK[identifier]
                original=self.raw[offset];available=result[offset]
                if original>99 or not 0<=available+amount<=99:
                    label=STOCK_ITEMS[ITEM_TO_STOCK[identifier]][1]
                    raise ValueError(f'KH2 bag transfer for {label} needs available stock and space (0–99). Adjust its bag quantity before equipping.')
                result[offset]=available+amount
            weapon_offsets=[record+0x24f0]+[record+0x32f4+n*0x38 for n in (0,3,4)]
            old=Counter(self.word(self.raw,o) for o in weapon_offsets)
            new=Counter(self.word(result,o) for o in weapon_offsets)
            if any(i and n>max(1,old[i]) for i,n in new.items()):
                raise ValueError('KH2 Sora and dual-wield forms must use different Keyblades. Swap both weapon slots together.')
            for character,name in enumerate(self.names):
                prefix=f'character:{character}:'
                affected=any(k in {prefix+'level',prefix+'ap_boost',prefix+'weapon'} or
                             any(k.startswith(prefix+part) for part in ('ability:','armor:','accessory:')) for k in edits)
                if not affected:continue
                before=self.budget(self.raw,record,character);after=self.budget(result,record,character)
                if before is None or after is None:continue
                excess=max(0,after[0]-after[1]);original_excess=max(0,before[0]-before[1])
                if excess>original_excess:
                    raise ValueError(f'KH2 AP budget: {name} equipped abilities need {after[0]} AP but only {after[1]} AP is available. Increase AP boosts or unequip abilities.')
        return self.acquisition.finish(result,changes)

    def expected_stock(self,slot,key,value,changes,encodings):
        """Verify the requested bag amount plus explicitly selected slot transfers."""
        identifier=STOCK_ITEMS[int(key.split(':')[1])][0]
        adjustment=0
        for equipment_key,(offset,_) in self.slots[slot].items():
            pair=slot,equipment_key
            if pair not in changes:continue
            before=self.word(self.raw,offset)
            after=encodings[pair][2][changes[pair]]
            adjustment+=int(before==identifier)-int(after==identifier)
        return value+adjustment

"""Owned native armament/armor assignments; no item or placeholder synthesis.

Independent implementation from the attributed native layout facts in SOURCES.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from collections import Counter
import struct,zlib
from elden_weapons import WEAPONS
from elden_equipment_tables import ARMOR

SLOTS={0:('Left hand 1','Weapons'),1:('Right hand 1','Weapons'),
       2:('Left hand 2','Weapons'),3:('Right hand 2','Weapons'),
       4:('Left hand 3','Weapons'),5:('Right hand 3','Weapons'),
       12:('Head','Head armor'),13:('Chest','Chest armor'),
       14:('Arms','Arm armor'),15:('Legs','Leg armor')}
BARE={0:110000,12:0x10002710,13:0x10002774,14:0x100027d8,15:0x1000283c}

def u32(raw,at):return struct.unpack_from('<I',raw,at)[0]
def fingerprint(raw,base,indices):
    return 2*zlib.adler32(b''.join(raw[base+n*4:base+n*4+4] for n in indices))&0xffffffff


class EquipmentLoadout:
    def __init__(self,raw,character,armaments,Field):
        self.raw,self.c,self.armaments=raw,character,armaments
        self.fields=[];self.options={};self.current={};self.owned={};self.reasons={}
        p=character.start+32;physical={};duplicates=set()
        for _ in range(5118 if u32(raw,character.start)<=81 else 5120):
            h,item=struct.unpack_from('<2I',raw,p)
            if h:
                if h in physical:duplicates.add(h)
                physical[h]=item
            p+=21 if h>>28==8 else 16 if h>>28==9 else 8
        rows=[struct.unpack_from('<3I',raw,character.held+4+n*12) for n in range(2688)]
        storage=armaments+156+12+303
        stored=[struct.unpack_from('<3I',raw,storage+4+n*12) for n in range(1920)]
        counts=Counter(h for h,q,a in rows+stored if q)
        self.inventory_ok=u32(raw,character.held)==sum(h not in (0,0xffffffff) for h,q,a in rows)
        for row,(h,q,a) in enumerate(rows):
            item=physical.get(h)
            if q!=1 or counts[h]!=1 or h in duplicates or item is None:continue
            base=item//10000*10000
            if h>>28==8 and (base in WEAPONS or item==BARE[0]) and item>>28==0:
                maximum=0 if base==33250000 else WEAPONS.get(base,('',0))[1]
                affinity=(item-base)//100
                if item!=BARE[0] and (item%100>maximum or affinity>12 or maximum in (0,10) and affinity):continue
                title='Unarmed' if item==BARE[0] else WEAPONS[base][0]+f' +{item%100}'
                if item!=BARE[0] and affinity:title+=f' · affinity {affinity}'
                self.owned[h]=(row,item,'Weapons',title)
            elif h>>28==9 and item in ARMOR:
                title,kind=ARMOR[item];self.owned[h]=(row,item,kind,title)
            elif h>>28==9 and item in tuple(BARE.values())[1:]:
                n=next(n for n,v in BARE.items() if n and v==item)
                self.owned[h]=(row,item,SLOTS[n][1],'No '+SLOTS[n][0].lower()+' armor')
        for slot,(title,kind) in SLOTS.items():
            h=u32(raw,character.player+0x34c+slot*4);self.current[slot]=h
            reason=self._reason(raw,slot,h)
            candidates=sorted((h for h,v in self.owned.items() if v[2]==kind),key=lambda h:(self.owned[h][3],h))
            if h not in candidates:candidates.insert(0,h)
            labels=tuple((self.owned[v][3]+f' · copy {self.owned[v][0]+1}') if v in self.owned else 'Current assignment (unresolved)' for v in candidates)
            key='equipment_slot:'+str(slot);self.options[key]=tuple(candidates);self.reasons[slot]=reason
            self.fields.append(Field(key,title,candidates.index(h),character.player+0x34c+slot*4,'',0,len(candidates)-1,
                'Equipment loadout',choices=labels,readonly=bool(reason) or len(candidates)<2,collection=kind,
                note=reason or 'Select a copy already in held inventory. Inventory index, bare identity, physical handle, dynamic equipment and the corresponding fingerprint synchronize. Storage, active hand, menu snapshots and unknown state are preserved.'))

    def _reason(self,raw,slot,h):
        if not self.inventory_ok:return 'The held inventory count is inconsistent. Equipment is preserved.'
        if h not in self.owned:return 'The current assignment is not a uniquely owned supported held item. It is preserved.'
        row,item,kind,title=self.owned[h];p=self.c.player
        if kind!=SLOTS[slot][1]:return 'The current equipment category does not match this slot.'
        if (u32(raw,p+0x280+slot*4),u32(raw,p+0x2f4+slot*4),u32(raw,self.armaments+slot*4))!=(row+0x180,item&0x0fffffff,item):
            return 'The native equipment representations disagree. Save again after equipping this slot in the game.'
        indices=(0,2,4,1,3,5,6,8,7,9) if slot<6 else (12,13,14,15,17,18,19,20,21)
        at=self.c.fingerprints+(28 if slot<6 else 32)
        if u32(raw,at)!=fingerprint(raw,p+0x2f4,indices):return 'The equipment fingerprint does not match; its dependent state is protected.'
        return ''

    def patch(self,result,changes):
        requested={int(k.split(':')[1]):self.options[k][v] for k,v in changes.items() if k in self.options}
        if not requested:return False
        final=dict(self.current);final.update(requested)
        seen={}
        for slot,h in final.items():
            if h not in self.owned:continue
            item=self.owned[h][1]
            if item==BARE[0]:continue
            if h in seen and (slot in requested or seen[h] in requested):
                raise ValueError('The same physical equipment copy cannot occupy two slots. Choose another owned copy or swap both slots together.')
            seen[h]=slot
        for slot,h in requested.items():
            if self.reasons[slot]:raise ValueError(self.reasons[slot])
            row,original,kind,title=self.owned[h]
            # Existing weapon upgrades are applied before assignments. Resolve
            # their resulting identity from the already synchronized old slot
            # when available, or directly from the physical table.
            p=self.c.start+32;item=None
            for _ in range(5118 if u32(result,self.c.start)<=81 else 5120):
                handle,identifier=struct.unpack_from('<2I',result,p)
                if handle==h:item=identifier;break
                p+=21 if handle>>28==8 else 16 if handle>>28==9 else 8
            if item is None:raise ValueError('The selected equipment copy is no longer available.')
            for at,value in ((self.c.player+0x280+slot*4,row+0x180),(self.c.player+0x2f4+slot*4,item&0x0fffffff),
                             (self.c.player+0x34c+slot*4,h),(self.armaments+slot*4,item)):
                struct.pack_into('<I',result,at,value)
        for slots,offset in (((0,2,4,1,3,5,6,8,7,9),28),((12,13,14,15,17,18,19,20,21),32)):
            if any((slot<6)==(offset==28) for slot in requested):
                struct.pack_into('<I',result,self.c.fingerprints+offset,fingerprint(result,self.c.player+0x2f4,slots))
        return True

    def verifies(self,other,key,value):
        slot=int(key.split(':')[1]);handle=self.options[key][value]
        return other.current.get(slot)==handle and not other.reasons.get(slot)

    def upgrade_mirrors(self,handle):
        slots=[n for n,h in self.current.items() if n<6 and h==handle]
        if not slots or any(self.reasons[n] for n in slots):return None
        return tuple(at for n in slots for at in (self.c.player+0x2f4+n*4,self.armaments+n*4))

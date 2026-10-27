"""Owned talisman assignments with slot, family and native-reference checks.

SPDX-License-Identifier: GPL-3.0-or-later
Independent writer from documented format/parameter facts; see SOURCES.md.
"""
from collections import Counter,defaultdict
import struct
from elden_loadouts import fingerprint,u32
from elden_talisman_tables import TALISMANS
from elden_registry import registry_records,register_item

SLOTS=(17,18,19,20)
HASH_INDICES=(12,13,14,15,17,18,19,20,21)
INVALID=0xffffffff


class TalismanLoadout:
    def __init__(self,raw,character,armaments,Field):
        self.raw,self.c,self.armaments=raw,character,armaments
        self.fields=[];self.options={};self.reasons={};self.additions={}
        self.current={n:u32(raw,character.player+0x34c+n*4) for n in SLOTS}
        held=[struct.unpack_from('<3I',raw,character.held+4+n*12) for n in range(2688)]
        storage=armaments+156+12+303
        stored=[struct.unpack_from('<3I',raw,storage+4+n*12) for n in range(1920)]
        candidates=defaultdict(list)
        for n,(handle,quantity,_) in enumerate(held):
            if handle>>28==10 and quantity==1 and (0x20000000|(handle&0x0fffffff)) in TALISMANS:
                candidates[handle].append(n)
        self.owned={}
        for handle,rows in candidates.items():
            # Accessory handles identify an item type, not a physical copy.
            # Preserve a valid currently referenced held row; otherwise use a
            # deterministic held copy. Storage copies cannot supply equipment.
            referenced={u32(raw,character.player+0x280+slot*4)-0x180
                for slot,h in self.current.items() if h==handle}
            matching=referenced.intersection(rows)
            row=next(iter(matching)) if len(matching)==1 else rows[0]
            self.owned[handle]=(row,0x20000000|(handle&0x0fffffff))
        self.unlocked=raw[character.player+0xbe]+1
        inventory_ok=u32(raw,character.held)==sum(h not in (0,INVALID) for h,q,a in held)
        hash_ok=u32(raw,character.fingerprints+32)==fingerprint(raw,character.player+0x2f4,HASH_INDICES)
        unknown=any(h and h not in self.owned for n,h in self.current.items() if n-17<self.unlocked)
        for slot,handle in self.current.items():
            reason=''
            if not 1<=self.unlocked<=4:reason='The saved talisman capacity is not recognized.'
            elif not inventory_ok:reason='The held inventory count is inconsistent.'
            elif not hash_ok:reason='The armor/talisman fingerprint does not match.'
            elif slot-17>=self.unlocked:reason='This talisman slot is locked. Apply a supported capacity increase first.'
            elif unknown:reason='An active talisman is not a mapped held item. Its dependencies are protected.'
            elif handle and handle not in self.owned:reason='The current talisman is not a mapped held item.'
            if not reason:
                expected=((self.owned[handle][0]+0x180,handle&0x0fffffff,self.owned[handle][1]) if handle else (INVALID,)*3)
                actual=(u32(raw,character.player+0x280+slot*4),u32(raw,character.player+0x2f4+slot*4),u32(raw,armaments+slot*4))
                if actual!=expected:reason='The native talisman representations disagree. Equip and save again in the game.'
            choices=[0]+sorted(self.owned,key=lambda h:(TALISMANS[self.owned[h][1]][0],h))
            if handle not in choices:choices.insert(1,handle)
            key=f'talisman_slot:{slot-17}';self.options[key]=tuple(choices);self.reasons[slot]=reason
            labels=tuple('Empty' if h==0 else TALISMANS[self.owned[h][1]][0] if h in self.owned else 'Current talisman (unresolved)' for h in choices)
            self.fields.append(Field(key,f'Talisman {slot-16}',choices.index(handle),character.player+0x34c+slot*4,
                '',0,len(choices)-1,'Equipment loadout',choices=labels,readonly=bool(reason) or len(choices)<2,
                collection='Talismans',note=reason or 'Choose a talisman already in held inventory. Slot capacity, exclusive accessory groups and all four native references are checked. Inventory, derived stats and unknown state are preserved.'))
        try:registry_records(raw,character.registry)
        except ValueError:return
        if not inventory_ok or not any(entry==(0,0,0) for entry in held):return
        present={h for h,q,a in held+stored if h not in (0,INVALID)}
        for identity,(name,group) in TALISMANS.items():
            # Base-game accessory identities are below the DLC's 7000 range.
            # Existing held/storage entries (even depleted/ambiguous ones) are
            # preserved; this path acquires one entirely missing identity.
            if (identity&0x0fffffff)>=7000:continue
            handle=0xa0000000|(identity&0x0fffffff)
            if handle in present:continue
            key=f'add_talisman:{identity}';self.additions[key]=identity
            self.fields.append(Field(key,name,0,character.held,'',0,1,'Add items',boolean=True,
                collection='Add talismans',note='Acquire one missing base-game talisman in held inventory. Existing held/storage copies are preserved. Item registration and acquisition counters synchronize; the item is not equipped and no quest or achievement reward is granted.'))

    def patch(self,result,changes):
        for key,identity in self.additions.items():
            if changes.get(key):self.acquire(result,identity)
        requested={17+int(k.split(':')[1]):self.options[k][value] for k,value in changes.items() if k in self.options}
        if not requested:return False
        final={**self.current,**requested}
        for slot in requested:
            if self.reasons[slot]:raise ValueError(self.reasons[slot])
        def groups(values):
            return Counter(TALISMANS[self.owned[h][1]][1] for slot,h in values.items()
                if slot-17<self.unlocked and h in self.owned)
        before,after=groups(self.current),groups(final)
        if any(count>max(1,before[group]) for group,count in after.items()):
            raise ValueError('These talismans belong to the same exclusive accessory group. Replace or clear the other slot in the same change.')
        for slot,handle in requested.items():
            row,identity=self.owned.get(handle,(-385,INVALID))
            for at,value in ((self.c.player+0x280+slot*4,row+0x180 if handle else INVALID),
                    (self.c.player+0x2f4+slot*4,handle&0x0fffffff if handle else INVALID),
                    (self.c.player+0x34c+slot*4,handle),(self.armaments+slot*4,identity)):
                struct.pack_into('<I',result,at,value)
        struct.pack_into('<I',result,self.c.fingerprints+32,fingerprint(result,self.c.player+0x2f4,HASH_INDICES))
        return True

    def acquire(self,result,identity):
        c=self.c;handle=0xa0000000|(identity&0x0fffffff)
        held=[struct.unpack_from('<3I',result,c.held+4+n*12) for n in range(2688)]
        storage=self.armaments+156+12+303
        stored=[struct.unpack_from('<3I',result,storage+4+n*12) for n in range(1920)]
        if any(h==handle for h,q,a in held+stored):
            raise ValueError('This talisman already has a held or storage record. No duplicate was added.')
        count=u32(result,c.held)
        if count!=sum(h not in (0,INVALID) for h,q,a in held):
            raise ValueError('The held inventory count is inconsistent. No talisman was added.')
        empty=next((n for n,entry in enumerate(held) if entry==(0,0,0)),None)
        if empty is None:raise ValueError('No clean empty held-inventory record is available for this talisman.')
        counter=c.held+8+3072*12;equip,acquisition=struct.unpack_from('<2I',result,counter)
        keys=[struct.unpack_from('<3I',result,c.held+8+2688*12+n*12) for n in range(384)]
        mark=max(432,acquisition,max((a for h,q,a in held+keys if h not in (0,INVALID)),default=0)+1)
        mark+=mark%2
        if equip==INVALID or mark>0xfffffffc:raise ValueError('Talisman acquisition counters would overflow.')
        register_item(result,c.registry,identity)
        struct.pack_into('<3I',result,c.held+4+empty*12,handle,1,mark+1)
        struct.pack_into('<2I',result,counter,equip+1,mark+2)
        struct.pack_into('<I',result,c.held,count+1)

    def verifies_addition(self,other,key,value):
        if not value:return True
        identity=self.additions[key];handle=0xa0000000|(identity&0x0fffffff)
        if handle not in other.owned:return False
        return any(item==identity for item,flag in registry_records(other.raw,other.c.registry))

    def verifies(self,other,key,value):
        slot=17+int(key.split(':')[1])
        return other.current[slot]==self.options[key][value] and not other.reasons[slot]

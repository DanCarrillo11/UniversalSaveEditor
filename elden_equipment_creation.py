"""Bounded physical equipment acquisition and variable GaItem serialization.

Independent implementation from pinned native format facts; see SOURCES.md.
Existing records remain byte-exact, including custom Ash references. Only proven
zero padding may be consumed; the final 178-byte block remains anchored.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from bisect import bisect_left
from collections import Counter
import struct
from elden_registry import registry_records, register_item
from elden_equipment_tables import WEAPON_CREATION, ARMOR

HELD, KEYS = 2688, 384
SLOT_SIZE = 0x280000


def integer(raw, at):return struct.unpack_from('<I',raw,at)[0]


class PhysicalEquipment:
    def __init__(self,raw,character,storage,Field):
        self.character,self.storage,self.raw=character,storage,raw
        self.records=[];self.handles={};self.operations={};self.fields=[]
        self.reason='';self.growth=0
        try:self._inspect(raw)
        except ValueError as error:self.reason=str(error)
        self.fields.append(Field('equipment_creation_status','Equipment creation',
            0 if self.reason else self.free,character.start,'',0,5120,'Add equipment',readonly=True,
            collection='Equipment creation capacity',note=self.reason or
            f'{self.free} free physical records; {self.growth} bytes of verified padding. New pieces enter held inventory unequipped. Existing equipment, story and DLC ownership stay unchanged.'))
        # Keep the complete catalogue visible even when this representation cannot
        # be modified; each disabled control explains the structural constraint.
        for prefix,items in (('create_weapon:',WEAPON_CREATION),('create_armor:',ARMOR)):
            for identifier,entry in items.items():
                title,category=(entry,'Weapons') if prefix=='create_weapon:' else entry
                size=13 if prefix=='create_weapon:' else 8
                maximum=min(10,self.free,self.empty_inventory,self.growth//size) if not self.reason else 0
                key=prefix+str(identifier)
                self.fields.append(Field(key,title,0,character.held,'',0,maximum,'Add equipment',
                    collection='Add '+category.lower(),readonly=maximum==0,item_id=identifier,
                    note=self.reason or ('Adds separate +0 copies, unequipped and without a custom Ash. Existing pieces are retained.'
                                        if maximum else 'No free physical/inventory capacity or verified zero padding for this item. No data is discarded.')))
                if maximum:self.operations[key]=(identifier,8 if prefix=='create_weapon:' else 9)

    def _inspect(self,raw):
        c=self.character;start=c.start+32;p=start
        count=5118 if integer(raw,c.start)<=81 else 5120
        used=set();ashes=[];generations=[]
        for position in range(count):
            h,item=struct.unpack_from('<2I',raw,p);kind=h>>28
            size=21 if kind==8 else 16 if kind==9 else 8
            self.records.append((p,size,h,item))
            if item in (0,0xffffffff):
                if h:raise ValueError('An empty physical record has a nonempty handle. Existing records are preserved.')
            else:
                if kind not in (8,9,12) or item>>28!={8:0,9:1,12:8}[kind] or not h&0x800000:
                    raise ValueError('Unrecognized physical item type or handle generation. Existing records are preserved.')
                index=h&65535
                if index>=count or index in used:raise ValueError('Physical item indices are duplicated or out of bounds.')
                used.add(index);self.handles[h]=item;generations.append((h>>16)&255)
                if kind==12:ashes.append(index)
            p+=size
        if p!=c.player:raise ValueError('The physical item table does not end at the recognized player record.')
        ashes.sort();self.free_indices=[i for i in range(count) if i not in used]
        self.free=len(self.free_indices);self.ashes=ashes
        self.generation=generations[0] if generations else 128
        # Menu snapshots can retain runtime encodings unrelated to native GaItem
        # handles. Preserve them, and reserve any exact candidate collision.
        menu={integer(raw,c.profile+382+n*4) for n in range(21)}
        self.free_indices=[i for i in self.free_indices if all((kind<<28)|(self.generation<<16)|i not in menu for kind in (8,9))]
        self.free=len(self.free_indices)
        for position,(_,_,h,item) in enumerate(self.records):
            if item in (0,0xffffffff):continue
            index=h&65535;before=bisect_left(ashes,index)
            expected=before if h>>28==12 else len(ashes)+index-before
            if position!=expected:raise ValueError('The physical item order is not the recognized native two-pass layout.')
        for at,_,h,item in self.records:
            if h>>28==8:
                custom=integer(raw,at+16)
                if custom not in (0,0xffffffff) and (custom>>28!=12 or custom not in self.handles):
                    raise ValueError('An existing weapon references an unresolved Ash of War. Its data is preserved.')
        for first,indices in ((c.player+0x34c,tuple(range(10))+tuple(range(12,16))),):
            for n in indices:
                handle=integer(raw,first+n*4)
                if handle not in (0,0xffffffff) and handle>>28 in (8,9,12) and handle not in self.handles:
                    raise ValueError('An equipped item references a missing physical record. Its assignment is preserved.')
        for inv,capacity,key_capacity in ((c.held,HELD,KEYS),(self.storage,1920,128)):
            for first,length in ((inv+4,capacity),(inv+8+capacity*12,key_capacity)):
                for n in range(length):
                    h,q,order=struct.unpack_from('<3I',raw,first+n*12)
                    if h>>28 in (8,9,12) and h not in self.handles:
                        raise ValueError('Inventory or storage references a missing physical item record.')
        entries=self._entries(raw,c.held)
        if integer(raw,c.held)!=sum(h not in (0,0xffffffff) for h,q,a in entries):
            raise ValueError('The held inventory count disagrees with its records.')
        self.empty_inventory=sum(entry==(0,0,0) for entry in entries)
        registry_records(raw,c.registry)
        # The parser identifies every section through its 128-byte fingerprint
        # record. No trailing bytes outside that parsed span are assumed empty.
        self.anchor=c.start+SLOT_SIZE-178
        self.parsed_end=c.fingerprints+128
        if self.parsed_end>self.anchor:raise ValueError('The parsed character sections overlap the anchored tail.')
        tail=raw[self.parsed_end:self.anchor]
        self.growth=len(tail)-len(tail.rstrip(b'\0'))
        if not self.free:raise ValueError('No free physical item records are available.')
        if not self.empty_inventory:raise ValueError('No clean empty held-inventory record is available.')
        if self.growth<8:raise ValueError('No verified zero padding is available before the anchored tail. Existing data is preserved.')

    @staticmethod
    def _entries(raw,held):
        return [struct.unpack_from('<3I',raw,held+4+n*12) for n in range(HELD)]

    def patch(self,result,changes):
        requested=[(key,amount,*self.operations[key]) for key,amount in sorted(changes.items()) if key in self.operations and amount]
        if not requested:return
        total=sum(amount for _,amount,_,_ in requested)
        delta=sum(amount*(13 if kind==8 else 8) for _,amount,_,kind in requested)
        if total>self.free or total>self.empty_inventory or delta>self.growth:
            raise ValueError('The combined equipment additions exceed available records, inventory capacity or verified padding. Add fewer pieces.')
        c=self.character;entries=self._entries(result,c.held)
        empty=[i for i,v in enumerate(entries) if v==(0,0,0)]
        if len(empty)<total:raise ValueError('Other additions used the available held-inventory capacity. Add fewer pieces.')
        counter=c.held+8+(HELD+KEYS)*12;equip,mark=struct.unpack_from('<2I',result,counter)
        key_start=c.held+8+HELD*12
        key_orders=[integer(result,key_start+i*12+8) for i in range(KEYS) if integer(result,key_start+i*12) not in (0,0xffffffff)]
        mark=max(432,mark,max((a+1 for h,q,a in entries if h not in (0,0xffffffff)),default=0),max((a+1 for a in key_orders),default=0))
        mark+=mark%2
        if mark+2*total>0xfffffffe or equip+total>0xffffffff:raise ValueError('Equipment acquisition counters would overflow.')
        physical={};new_index=0
        for key,amount,identifier,kind in requested:
            for _ in range(amount):
                index=self.free_indices[new_index];h=(kind<<28)|(self.generation<<16)|index
                position=len(self.ashes)+index-bisect_left(self.ashes,index)
                at,size,old_handle,old_item=self.records[position]
                if size!=8 or old_handle or old_item not in (0,0xffffffff):raise ValueError('The selected native physical hole is not empty.')
                physical[position]=struct.pack('<5IB',h,identifier,0,0,0,0) if kind==8 else struct.pack('<4I',h,identifier,0,0)
                struct.pack_into('<3I',result,c.held+4+empty[new_index]*12,h,1,mark+1)
                register_item(result,c.registry,identifier)
                mark+=2;new_index+=1
        struct.pack_into('<2I',result,counter,equip+total,mark)
        struct.pack_into('<I',result,c.held,integer(result,c.held)+total)
        records=b''.join(physical.get(i,bytes(result[at:at+size])) for i,(at,size,h,item) in enumerate(self.records))
        if len(records)-(c.player-(c.start+32))!=delta:raise ValueError('Unexpected physical item serialization size.')
        if any(result[self.anchor-delta:self.anchor]):raise ValueError('The required character padding is not empty.')
        # All same-size edits were applied before this final structural change.
        # Keep opaque bytes in order; discard only validated terminal zero slack.
        following=bytes(result[c.player:self.anchor-delta])
        result[c.start+32:self.anchor]=records+following

    def verifies(self,other,key,amount):
        identifier,kind=self.operations[key]
        new={h:item for h,item in other.handles.items() if h not in self.handles}
        handles={h for h,item in new.items() if item==identifier and h>>28==kind}
        held=Counter(h for h,q,a in self._entries(other.raw,other.character.held) if q==1)
        return len(handles)==amount and all(held[h]==1 for h in handles)

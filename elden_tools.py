"""Owned quick/pouch assignments and Wondrous Physick mixtures.

SPDX-License-Identifier: GPL-3.0-or-later
Independent bounded writer; factual references and native checks: SOURCES.md.
"""
from collections import Counter
import struct,zlib
from elden_tool_tables import QUICK_ITEMS,PHYSICK_TEARS

INVALID=0xffffffff
def integer(raw,at):return struct.unpack_from('<I',raw,at)[0]
def quick_hash(raw,armaments):
    values=[integer(raw,armaments+88+n*4) for n in range(16)]
    return 2*zlib.adler32(struct.pack('<16I',*(v if v==INVALID else v&0x0fffffff for v in values)))&INVALID

def family(handle):
    if not handle:return 0
    identity=0x40000000|(handle&0x0fffffff)
    for base in (0x400003e9,0x4000041b):
        if base-1<=identity<=base+24:return base
    return 0x400000fa if identity in (0x400000fa,0x400000fb) else identity


class ToolLoadout:
    def __init__(self,raw,character,spells,armaments,Field):
        self.raw,self.c,self.spells,self.armaments=raw,character,spells,armaments
        self.fields=[];self.options={};self.current={};self.reasons={};self.positions={}
        held=character.held
        rows=[struct.unpack_from('<3I',raw,held+4+n*12) for n in range(2688)]
        counts=Counter(h for h,q,a in rows if q)
        self.tools={h:(row,0x40000000|(h&0x0fffffff)) for row,(h,q,a) in enumerate(rows)
                    if q>0 and h>>28==11 and counts[h]==1 and 0x40000000|(h&0x0fffffff) in QUICK_ITEMS}
        held_ok=integer(raw,held)==sum(h not in (0,INVALID) for h,q,a in rows)
        fingerprint_ok=integer(raw,character.fingerprints+36)==quick_hash(raw,armaments)
        keys=[struct.unpack_from('<3I',raw,held+8+2688*12+n*12) for n in range(384)]
        key_ok=integer(raw,held+4+2688*12)==sum(h not in (0,INVALID) for h,q,a in keys)
        tear_counts=Counter(0x40000000|(h&0x0fffffff) for h,q,a in rows+keys if q and h>>28==11)
        self.tears={i for i,n in tear_counts.items() if n==1 and i in PHYSICK_TEARS}
        self.has_flask=any(i in (0x400000fa,0x400000fb) for row,i in self.tools.values())
        ordered=tuple(sorted(self.tools,key=lambda h:(QUICK_ITEMS[self.tools[h][1]],h)))
        pair_base=spells+116
        for n in range(16):
            pair=pair_base+(n*8 if n<10 else 84+(n-10)*8);dynamic=armaments+88+n*4
            handle,index=struct.unpack_from('<2I',raw,pair);identifier=integer(raw,dynamic)
            key='quick_slot:'+str(n);self.current[key]=handle;self.positions[key]=(pair,dynamic)
            valid=((handle,index,identifier)==(0,INVALID,INVALID) or
                handle in self.tools and (index,identifier)==(self.tools[handle][0]+384,self.tools[handle][1]))
            reason=('The held inventory count is inconsistent.' if not held_ok else
                    'The quick-item fingerprint does not match. Existing quick/pouch state is protected.' if not fingerprint_ok else
                    'The saved quick-item representations disagree or reference an unsupported/unowned item.' if not valid else '')
            values=(0,)+ordered
            if handle not in values:values+=(handle,)
            self.options[key]=values;self.reasons[key]=reason
            labels=tuple('Empty' if h==0 else QUICK_ITEMS[self.tools[h][1]] if h in self.tools else 'Current assignment (preserved)' for h in values)
            self.fields.append(Field(key,('Quick item '+str(n+1) if n<10 else 'Pouch '+str(n-9)),values.index(handle),pair,'',0,len(values)-1,
                'Tool loadout',choices=labels,readonly=bool(reason),collection='Quick items' if n<10 else 'Pouch',
                note=reason or 'Uses an existing held tool or Spirit Ash. Handle, inventory-row index, dynamic identity and checked fingerprint synchronize. Quantities, active selection, events and unrecognized entries are preserved.'))
        choices=(INVALID,)+tuple(sorted(self.tears,key=lambda i:(PHYSICK_TEARS[i],i)))
        for n in range(2):
            key='physick_slot:'+str(n);at=armaments+156+n*4;value=integer(raw,at)
            self.current[key]=value;self.positions[key]=at
            values=choices if value in choices else choices+(value,)
            reason=('The held/key inventory count is inconsistent.' if not held_ok or not key_ok else
                    'The Flask of Wondrous Physick is not present in held inventory.' if not self.has_flask else
                    'The current tear is unknown or not uniquely owned. It is preserved.' if value not in choices else '')
            self.options[key]=values;self.reasons[key]=reason
            self.fields.append(Field(key,'Mixture '+str(n+1),values.index(value),at,'',0,len(values)-1,'Tool loadout',
                choices=tuple('Empty' if i==INVALID else PHYSICK_TEARS.get(i,'Current tear (preserved)')+f' · {i:08x}' for i in values),
                readonly=bool(reason),collection='Wondrous Physick',
                note=reason or 'Select a uniquely owned Crystal Tear. Changes this mixture field only; no item, pickup, quest, flask charge or DLC access is created. The other mixture position is retained.'))

    def patch(self,result,changes):
        requested={key:self.options[key][value] for key,value in changes.items() if key in self.options}
        if not requested:return
        for key in requested:
            if self.reasons[key]:raise ValueError(self.reasons[key])
        final={**self.current,**requested}
        for names in ([f'quick_slot:{i}' for i in range(10)],[f'quick_slot:{i}' for i in range(10,16)]):
            if not any(k in requested for k in names):continue
            seen={}
            for key in names:
                h=final[key]
                if h in (0,INVALID):continue
                group=family(h)
                if group in seen:raise ValueError('A tool or flask family cannot occupy two positions in the same quick-item or pouch group. Swap both positions together.')
                seen[group]=key
        if any(k.startswith('physick_slot:') for k in requested):
            first,second=(final['physick_slot:'+str(i)] for i in range(2))
            if first!=INVALID and first==second:raise ValueError('The same Crystal Tear cannot occupy both Physick positions.')
        for key,value in requested.items():
            if key.startswith('quick_slot:'):
                pair,dynamic=self.positions[key]
                row,identifier=self.tools[value] if value else (INVALID,INVALID)
                struct.pack_into('<2I',result,pair,value,row+384 if value else INVALID)
                struct.pack_into('<I',result,dynamic,identifier)
            else:struct.pack_into('<I',result,self.positions[key],value)
        if any(k.startswith('quick_slot:') for k in requested):
            struct.pack_into('<I',result,self.c.fingerprints+36,quick_hash(result,self.armaments))

    def verifies(self,other,key,value):
        return other.current.get(key)==self.options[key][value] and not other.reasons.get(key)

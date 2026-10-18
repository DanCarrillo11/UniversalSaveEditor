"""Existing horse names, synchronized between typed inventory and script state.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from collections import Counter
from rockstar_container import u32
from rdr2_features import parser_hash,member
from rdr2_campaign import ROOT,HORSE_SLOTS,scalar_paths


def saved_name(raw):
    if len(raw)!=64 or b'\0' not in raw:return None
    text,padding=raw.split(b'\0',1)
    if any(padding):return None
    try:return text.decode('utf-8')
    except UnicodeDecodeError:return None


class HorseNames:
    def __init__(self,campaign):
        self.campaign=campaign;self.positions={};f=campaign.f;raw=f.raw
        if not campaign.root:return
        rows=[]
        for frame,h,b,m in f.active_items():
            if h!=parser_hash('CPedInventorySaveStructure__HorseItem'):continue
            slot=member(frame,h,'SlotId',6)
            names=[(off,ref) for key,t,sub,off,ref in frame.structures[h][1]
                   if key==parser_hash('Name') and t==11 and sub==0 and off+64<=frame.structures[h][0] and ref==64<<16]
            if slot and len(names)==1:rows.append((b+names[0][0],u32(raw,b+slot[0]),m))
        slots=Counter(slot for at,slot,m in rows)
        for at,slot,m in rows:
            n=HORSE_SLOTS.get(slot)
            if n is None or slots[slot]!=1:continue
            model=campaign.scalar(1097+n*436+9,5)
            if model is None or not u32(raw,model) or raw[campaign.root[1]+1096*8]!=7:continue
            delta=(1097+n*436)*8;frame,base,length=campaign.root
            if delta+64>length:continue
            paths=scalar_paths(frame,ROOT,delta,11)
            if len(paths)!=1:continue
            identity,key,t,sub,off,ref=paths[0][-1]
            if ref!=64<<16 or off+64>frame.structures[identity][0]:continue
            script=base+delta;value=saved_name(raw[at:at+64]);other=saved_name(raw[script:script+64])
            if value is None or other is None:continue
            prefix='item:'+raw[m['Guid']:m['Guid']+8].hex();key=prefix+':name'
            existing=next((x for x in f.fields if x.key==prefix+':bondingxp'),None)
            collection=existing.collection if existing else f'Horse slot {n+1}'
            field=f.Field(key,'Horse name',value,at,'',0,63,'Horses',collection=collection,text=True,
                readonly=value!=other,note='Rename this existing horse in both the inventory and saved horse slot. Up to 63 UTF-8 bytes. An empty name clears the custom name. Breed, appearance, ownership and bonding are preserved. In-game loading has not been verified.' if value==other else
                'The inventory name and saved horse-slot name differ. Both original values are protected.')
            try:field.validate(value)
            except ValueError:continue
            f.fields.append(field)
            if not field.readonly:self.positions[key]=(at,script)

    def patch(self,plain,changes):
        for key,value in changes.items():
            if key not in self.positions:continue
            encoded=value.encode('utf-8')+b'\0'
            if len(encoded)>64:raise ValueError('Horse name exceeds its saved string capacity.')
            for at in self.positions[key]:plain[at:at+64]=encoded.ljust(64,b'\0')

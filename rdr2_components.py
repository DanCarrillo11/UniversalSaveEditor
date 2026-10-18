"""Typed RDR2 weapon-component selection and compatible leaf replacements.

SPDX-License-Identifier: GPL-3.0-or-later
No weapon spawning, guessed component slots or new ownership GUIDs.
"""
from collections import defaultdict,Counter
from functools import lru_cache
import re,struct
from rockstar_container import u32
from rdr2_features import parser_hash,member,labels,item_name


def family(name):
    if re.fullmatch(r'COMPONENT_.+_(?:MATERIAL|TINT_[A-Z]|ENGRAVING|RIFLING)_\d+',name):
        return name.rsplit('_',1)[0]
    if re.fullmatch(r'COMPONENT_.+_(?:BARREL|SIGHT)_(?:SHORT|LONG|NARROW|WIDE)',name):
        return name.rsplit('_',1)[0]
    return None


def natural(text):
    return tuple(int(s) if s.isdigit() else s for s in re.split(r'(\d+)',text))


@lru_cache(maxsize=1)
def families():
    result=defaultdict(list)
    for h,name in labels().items():
        f=family(name)
        if f:result[f].append(int(h,16))
    return dict(result)


def choice_name(h,prefix=None):
    name=labels()[f'{h:08x}']
    if prefix and name.startswith(prefix+'_'):
        suffix=name[len(prefix)+1:]
        if suffix.isdigit():
            part='Material' if 'MATERIAL' in prefix else 'Tint' if 'TINT' in prefix else 'Variant'
            return part+' '+suffix
        return suffix.replace('_',' ').title()
    return name.removeprefix('COMPONENT_').replace('_',' ').title()


class ComponentFields:
    def __init__(self,features):
        self.f=features;self.groups={};raw=features.raw;items=features.active_items()
        weapon_counts=Counter(u32(raw,m['ItemId']) for frame,h,b,m in items if h==parser_hash('CPedInventorySaveStructure__WeaponItem'))
        byguid={raw[m['Guid']:m['Guid']+8]:(frame,h,b,m) for frame,h,b,m in items}
        children=defaultdict(list);slots=defaultdict(list)
        for frame,h,b,m in items:
            parent=raw[m['ParentGuid']:m['ParentGuid']+8];children[parent].append(b)
            slot=member(frame,h,'SlotId',6)
            if slot:slots[parent,u32(raw,b+slot[0])].append((frame,h,b,m))
        def weapon(parent):
            seen=set()
            for depth in range(8):
                if parent in seen or parent not in byguid:return None
                seen.add(parent);frame,h,b,m=byguid[parent]
                if h==parser_hash('CPedInventorySaveStructure__WeaponItem'):
                    identity=u32(raw,m['ItemId']);name=labels().get(f'{identity:08x}','')
                    title=item_name(identity)+(f' · copy {parent.hex()[-4:]}' if weapon_counts[identity]>1 else '')
                    return (parent,title) if name.startswith('WEAPON_') else None
                if h!=parser_hash('SavegameInventoryItem') or not labels().get(f'{u32(raw,m["ItemId"]):08x}','').startswith('COMPONENT_'):return None
                parent=raw[m['ParentGuid']:m['ParentGuid']+8]
            return None
        for (parent,slot),rows in slots.items():
            owner=weapon(parent)
            if not owner:continue
            candidates=[]
            for frame,h,b,m in rows:
                name=labels().get(f'{u32(raw,m["ItemId"]):08x}','');equipped=member(frame,h,'Equipped',0)
                if h!=parser_hash('SavegameInventoryItem') or not name.startswith('COMPONENT_') or 'VERTDATA' in name or not equipped or raw[b+equipped[0]] not in (0,1) or struct.unpack_from('>q',raw,m['Quantity'])[0]!=1:
                    candidates=[];break
                candidates.append((u32(raw,m['ItemId']),b+equipped[0],m['ItemId'],raw[m['Guid']:m['Guid']+8]))
            if not candidates or len({h for h,flag,at,guid in candidates})!=len(candidates):continue
            active=[r for r in candidates if raw[r[1]]==1]
            if len(active)!=1:continue
            current=active[0];owned={h for h,flag,at,guid in candidates};options=set(owned)
            f=family(labels()[f'{current[0]:08x}'])
            extend=f and all(family(labels()[f'{h:08x}'])==f and not children[guid]
                and f'unlock:{h:08x}:apply' in features.unlocks.positions for h,flag,at,guid in candidates)
            if extend:
                options.update(h for h in families().get(f,()) if f'unlock:{h:08x}:apply' in features.unlocks.positions)
            if len(options)<2:continue
            options=tuple(sorted(options,key=lambda h:natural(labels()[f'{h:08x}'])))
            key=f'component:{parent.hex()}:{slot:08x}'
            title=(f.removeprefix('COMPONENT_').replace('_',' ').title() if extend else 'Owned component')
            # Nested grips retain their own independent stored finish controls.
            collection=owner[1]
            if parent!=owner[0]:collection+=' · '+item_name(u32(raw,byguid[parent][3]['ItemId']))
            self.groups[key]=(candidates,current,options,bool(extend))
            features.fields.append(features.Field(key,title,options.index(current[0]),current[2],'',0,len(options)-1,
                'Weapon customization',choices=tuple(choice_name(h,f if extend else None) for h in options),collection=collection,
                note='Select an owned component, or replace this existing part with a compatible named variant. Other parts and weapon identity are preserved. Selecting a new variant also applies its existing catalog unlock. This does not create a weapon or add missing component slots. In-game loading has not been verified.'))

    def patch(self,plain,changes):
        for key,value in changes.items():
            if key not in self.groups:continue
            rows,current,options,extend=self.groups[key]
            if type(value) is not int or not 0<=value<len(options):raise ValueError('Unsupported RDR2 component choice.')
            target=options[value];existing=[r for r in rows if r[0]==target]
            if existing:
                for h,flag,at,guid in rows:plain[flag]=int(h==target)
            elif extend:
                struct.pack_into('>I',plain,current[2],target)
                unlock=f'unlock:{target:08x}:apply'
                if unlock in self.f.unlocks.positions:plain[self.f.unlocks.positions[unlock]]|=7
            else:raise ValueError('The selected RDR2 component is not owned.')

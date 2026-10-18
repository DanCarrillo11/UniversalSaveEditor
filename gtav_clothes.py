"""Typed story wardrobe banks and synchronized known clothing selections.

SPDX-License-Identifier: GPL-3.0-or-later
Only static, named single-player catalogue entries qualify; see SOURCES.md.
"""
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import json
import struct
import sys
from rockstar_container import name_hash, u32
from gtav_weapons import CHARACTERS, SCRIPT, embedded
from gtav_vehicles import array, exact

COMPONENTS = ('HEAD','BERD','HAIR','UPPR','LOWR','HAND','FEET','TEEF','ACCS','TASK','DECL','JBIB')
DRAW_PAIR = (12, ((1620616462,11,7,0,0),(104834034,12,0,4,4029920929)))
TEX_PAIR = (8, ((1620616462,11,7,0,0),(104834034,2,0,4,0)))
DRAW_VALUE = (8, ((1048674328,6,0,0,0),(1588979285,6,0,4,0)))


@lru_cache(maxsize=1)
def catalog():
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
    data=json.loads((root/'assets/gtav-clothes.json').read_text(encoding='utf8'))
    data['schemas']={int(h):(v[0],tuple(tuple(e) for e in v[1])) for h,v in data['schemas'].items()}
    return data


class ClothingFields:
    def __init__(self,feature,Field):
        self.owner=feature.owner
        self.bits={}
        self.purchases={}
        self.outfits={}
        self.acquisition={}
        raw=self.owner.container.plain
        roots=[(f,at,length) for f in self.owner.container.frames for h,at,length in f.blocks if h==SCRIPT]
        if len(roots)!=1:return
        frame,base,length=roots[0]
        if not frame.structures.get(SCRIPT) or frame.structures[SCRIPT][0]!=length:return
        spans=sorted((at,at+n) for h,at,n in frame.blocks if n)
        if any(a[1]>b[0] for a,b in zip(spans,spans[1:])):return
        data=catalog()
        try:
            main=embedded(frame,SCRIPT,base,0x622852C8,0x77714E0A)
            size=frame.structures[0x77714E0A][0]
            if size not in (25728,28416,34592):return
            rows=data['versions']['modern' if size==34592 else 'legacy']
            banks=embedded(frame,SCRIPT,base,101016013,0x77714DDF)
            if banks<main+size and main<banks+3944:return
            if raw[banks]!=3:return
            bank_schemas=[0x77714DDF,0x77714DE0]+list(range(0x77714DE1,0x77714E0A))
            if any(frame.structures.get(h)!=data['schemas'][h] for h in bank_schemas):return
            if any(raw[banks+8+c*1312+b*32]!=3 for c in range(3) for b in range(41)):return
        except (ValueError,KeyError,struct.error):return
        for row in rows:
            char,cat,index=row['character'],row['category'],row['index']
            start,count=data['bankStarts'][str(cat)]
            if not 0<=index//32<count:continue
            at=banks+8+char*1312+(start+index//32)*32+8
            bit=index%32
            prefix=f'clothes:{char}:{cat}:{index}'
            for state,title in enumerate(('Available','Purchased','Seen')):
                key=prefix+':'+str(state)
                self.bits[key]=(at+state*8,bit)
                self.owner.fields.append(Field(key,row['label']+' · '+title,
                    (u32(raw,at+state*8)>>bit)&1,at+state*8,'',0,1,
                    'Wardrobe · '+data['categories'][str(cat)],boolean=True,collection=CHARACTERS[char],
                    note=('Purchase also makes this item available, without charging money. Story and edition restrictions can still apply.' if state==1 else '')))
            self.purchases[prefix]=(prefix+':0',prefix+':1')
        try:
            outfits=embedded(frame,0x77714E0A,main,274315432,0x77714E0B)
            if raw[outfits]!=3 or any(frame.structures.get(h)!=data['schemas'][h]
                    for h in (0x77714E0B,0x77714E0C,0x77714E0D,0x77714E0E,0x77714E0F)):
                return
            if any(raw[outfits+8+c*520+delta]!=12 for c in range(3) for delta in (0,104,208)):return
        except (ValueError,KeyError,struct.error):return
        active,maps=self.active_maps(frame)
        grouped=defaultdict(list)
        for row in rows:
            # Hair/beard growth has additional script state; purchase flags
            # alone are mapped, so those styles are not equipped here.
            if 3<=row['category']<12:grouped[row['character'],row['category']].append(row)
        for (char,cat),items in grouped.items():
            draw_at=outfits+8+char*520+104+8+cat*8
            tex_at=outfits+8+char*520+8+cat*8
            current=(u32(raw,draw_at),u32(raw,tex_at))
            # Unknown models, missing maps or a stale active snapshot must not
            # leave an independently serialized current outfit out of sync.
            if active is None or char==active and (cat not in maps or current!=(u32(raw,maps[cat][0]),raw[maps[cat][1]])):
                continue
            options={}
            for row in items:
                options.setdefault((row['drawable'],row['texture']),row)
            if current not in options:continue
            options=sorted(options.items())
            key=f'clothes_worn:{char}:{cat}'
            choices=tuple(f'{r["label"]} [style {pair[0]}, variant {pair[1]}]' for pair,r in options)
            self.outfits[key]=(draw_at,tex_at,maps.get(cat) if char==active else None,tuple(pair for pair,r in options))
            self.acquisition[key]=tuple(f'clothes:{char}:{cat}:{r["index"]}' for pair,r in options)
            self.owner.fields.append(Field(key,data['categories'][str(cat)],
                [pair for pair,r in options].index(current),draw_at,'',0,len(options)-1,
                'Current clothes',choices=choices,collection=CHARACTERS[char],
                note=('Updates the saved outfit and acquires the selected garment. Mission outfits, props and incompatible layers are not assembled automatically.' if cat==3 else '')))

    def active_maps(self,frame):
        raw=self.owner.container.plain
        players=[(f,at,n) for f in self.owner.container.frames for h,at,n in f.blocks if h==2383497134]
        if len(players)!=1 or players[0][0] is not frame:return None,{}
        _,base,length=players[0]
        schema=frame.structures.get(2383497134)
        if not schema or schema[0]!=208 or length!=208:return None,{}
        names=[name_hash('player_'+n) for n in ('zero','one','two')]
        model=u32(raw,base+32)
        if model not in names or not exact(schema[1],(1442269562,6,0,32,0)):return None,{}
        active=names.index(model)
        if (not exact(schema[1],(3613884743,16,1,144,1507352))
            or not exact(schema[1],(3504215824,16,1,168,1703963))
            or frame.structures.get(0x100)!=DRAW_PAIR or frame.structures.get(0x101)!=TEX_PAIR
            or frame.structures.get(4029920929)!=DRAW_VALUE):return active,{}
        try:
            draw=array(raw,frame,base+152,0x100,12,16)
            tex=array(raw,frame,base+176,0x101,8,16)
            keys=sorted(name_hash('PV_COMP_'+n) for n in COMPONENTS)
            if len(draw)!=12 or len(tex)!=12 or [u32(raw,at) for at in draw]!=keys or [u32(raw,at) for at in tex]!=keys:return active,{}
            # Dedicated blocks with exactly twelve nodes cannot share interior
            # records with another map of the same identity.
            for ident,nodes,stride in ((0x100,draw,12),(0x101,tex,8)):
                blocks=[(b,n) for h,b,n in frame.blocks if h==ident]
                if blocks!=[(nodes[0],12*stride)]:return active,{}
            d={u32(raw,at):at for at in draw};t={u32(raw,at):at for at in tex}
            return active,{i:(d[name_hash('PV_COMP_'+name)]+8,t[name_hash('PV_COMP_'+name)]+4)
                for i,name in enumerate(COMPONENTS) if u32(raw,d[name_hash('PV_COMP_'+name)]+4)==0}
        except (ValueError,struct.error):return active,{}

    def patch(self,plain,changes):
        changes=dict(changes)
        for key,(draw_at,tex_at,active,options) in self.outfits.items():
            if key not in changes:continue
            choice=changes[key]
            draw,tex=options[choice]
            original=self.owner.container.plain
            if (draw,tex)==(u32(original,draw_at),u32(original,tex_at)):
                continue
            struct.pack_into('>I',plain,draw_at,draw)
            struct.pack_into('>I',plain,tex_at,tex)
            if active:
                struct.pack_into('>I',plain,active[0],draw)
                plain[active[1]]=tex
            prefix=self.acquisition[key][choice]
            for suffix in (':0',':1'):
                if changes.get(prefix+suffix,1)==0:raise ValueError('Conflicting clothing selection and acquisition.')
                changes[prefix+suffix]=1
        for available,purchase in self.purchases.values():
            if changes.get(purchase)==1:
                if changes.get(available,1)==0:raise ValueError('Conflicting clothing purchase and availability.')
                changes[available]=1
            elif changes.get(available)==0:
                changes[purchase]=0
        for key,(at,bit) in self.bits.items():
            if key in changes:
                word=u32(plain,at)
                struct.pack_into('>I',plain,at,(word|(1<<bit)) if changes[key] else (word&~(1<<bit)))

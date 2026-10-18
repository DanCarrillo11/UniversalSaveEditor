"""Existing GTA V garage appearance and bounded performance modifications.

SPDX-License-Identifier: GPL-3.0-or-later
Only recognized native records are edited; no model/slot acquisition is inferred.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json
import struct
import sys
from rockstar_container import name_hash, u32
from gtav_vehicles import array, exact

VARIATION = 2181085963
PAIR = 0x102
PAIR_SCHEMA = (8, ((1620616462,11,7,0,0),(104834034,2,0,4,0)))
PERFORMANCE = ((11,'VMT_ENGINE','Engine'),(12,'VMT_BRAKES','Brakes'),
               (13,'VMT_GEARBOX','Transmission'),(15,'VMT_SUSPENSION','Suspension'),
               (16,'VMT_ARMOUR','Armor'))


@lru_cache(maxsize=1)
def catalog():
    root = Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
    data=json.loads((root/'assets/gtav-vehicles.json').read_text(encoding='utf8'))
    return data['colors'],{v['hash']:v for v in data['vehicles']}


class VehicleStyleFields:
    def __init__(self,feature,Field,rows):
        self.modifications={}
        raw=feature.owner.container.plain
        colors,models=catalog()
        def nodes_at(frame,b,size):
            variation=frame.structures.get(VARIATION)
            if not variation or variation[0]!=(48 if size==112 else 40):
                return None
            if not exact(variation[1],(3207858859,16,1,0,917519 if size==112 else 786445)) or frame.structures.get(PAIR)!=PAIR_SCHEMA:
                return None
            try:
                return array(raw,frame,b+8,PAIR,8,256)
            except (ValueError,struct.error):
                return None
        # Include inactive/unlinked vehicle records when counting heap owners.
        # A shared mod map is protected even if only one owner is in a garage.
        all_cars=[]
        oversized=False
        for frame in feature.owner.container.frames:
            vehicle=frame.structures.get(2541711729)
            if not vehicle or vehicle[0] not in (96,112) or not exact(vehicle[1],(3489090097,12,0,0,VARIATION)):
                continue
            for identity,b,length in frame.blocks:
                if identity==2541711729 and length%vehicle[0]==0:
                    if length//vehicle[0]>8192-len(all_cars):
                        oversized=True
                        break
                    all_cars.extend((frame,at,vehicle[0]) for at in range(b,b+length,vehicle[0]))
            if oversized:
                break
        references=Counter()
        if not oversized:
            total=0
            for frame,b,size in all_cars:
                nodes=nodes_at(frame,b,size) or ()
                total+=len(nodes)
                if total>262144:
                    references.clear()
                    break
                references.update(nodes)
        candidates=[]
        for prefix,collection,b,frame,vehicle_size in rows:
            vehicle=frame.structures.get(2541711729)
            variation=frame.structures.get(VARIATION)
            if (not vehicle or not variation or not exact(vehicle[1],(3489090097,12,0,0,VARIATION))
                or variation[0] != (48 if vehicle_size==112 else 40)):
                continue
            size,entries=variation
            # Only the two known layouts qualify. A member hash alone cannot
            # turn an unrelated byte in a future revision into a writable value.
            modern=size==48
            shift=2 if modern else 0
            specs=[('primary','Primary paint',339378721,27,colors),
                   ('secondary','Secondary paint',2286316087,28,colors),
                   ('pearl','Pearlescent paint',2129614729,29,colors),
                   ('wheel_color','Wheel paint',1809854827,30,colors)]
            for key,title,h,off in (('smoke_r','Tire smoke · red',3809562301,31),
                    ('smoke_g','Tire smoke · green',4163041496,32),
                    ('smoke_b','Tire smoke · blue',2428283409,33),
                    ('neon_r','Neon color · red',1346029982,34),
                    ('neon_g','Neon color · green',2890957252,35),
                    ('neon_b','Neon color · blue',117552945,36)):
                specs.append((key,title,h,off+shift,()))
            specs.append(('window_tint','Window tint',3806865411,38+shift,
                ('None','Pure black','Dark smoke','Light smoke','Stock','Limo','Green')))
            for key,title,h,off,choices in specs:
                if not exact(entries,(h,2,0,off,0)):
                    continue
                value=raw[b+off]
                if choices and value>=len(choices):
                    continue
                key=prefix+':'+key
                feature.formats[key]=('>B',b+off)
                feature.owner.fields.append(Field(key,title,value,b+off,'',0,len(choices)-1 if choices else 255,
                    'Vehicle appearance',choices=tuple(choices),collection=collection,
                    note='Saved appearance only. Smoke/neon color does not install or enable its corresponding lighting modification.' if key.endswith(('smoke_r','neon_r')) else ''))
            modeloff=64 if vehicle_size==112 else 56
            meta=models.get(u32(raw,b+modeloff))
            if not meta:
                continue
            feature.owner.fields.append(Field(prefix+':model_name','Vehicle',meta['label'],b+modeloff,'',
                0,256,'Saved vehicle',collection=collection,text=True,readonly=True))
            if (meta['type']!='CAR' or not exact(entries,(2393392848,2,0,26,0))
                or not exact(entries,(3207858859,16,1,0,917519 if modern else 786445))
                or frame.structures.get(PAIR)!=PAIR_SCHEMA):
                continue
            kit=raw[b+26]
            # 255 means no installed kit. Only a model with one known kit may
            # initialize it; multiple/unknown kit choices cannot be guessed.
            kits=meta['kits'] if kit==255 and meta['kit_count']==1 else [k for k in meta['kits'] if k['id']==kit]
            if len(kits)!=1:
                continue
            nodes=nodes_at(frame,b,vehicle_size)
            if nodes is None or raw[b:b+8]!=b'\x01'+bytes(7):
                continue
            keys=[u32(raw,p) for p in nodes]
            if len(set(keys))!=len(keys) or keys!=sorted(keys):
                continue
            candidates.append((prefix,collection,b,kits[0],dict(zip(keys,nodes))))
        for prefix,collection,b,kit,nodes in candidates:
            if any(references[p]!=1 for p in nodes.values()):
                continue
            for kind,name,title in PERFORMANCE:
                at=nodes.get(name_hash(name))
                count=kit['stats'].get(str(kind),0)
                saved=kit.get('saved',{}).get(str(kind),())
                if at is None or not 1<=count<=16 or len(saved)!=count:
                    continue
                current=raw[at+4]
                if current!=255 and current not in saved:
                    continue
                key=prefix+':mod_'+str(kind)
                options=(255,)+tuple(saved)
                self.modifications[key]=(at+4,b+26,kit['id'],options)
                feature.owner.fields.append(Field(key,title,options.index(current),at+4,'',0,len(options)-1,
                    'Vehicle performance',choices=('Stock',)+tuple(f'Stage {i+1}' for i in range(count)),
                    collection=collection,note='Uses the matching vehicle kit, initializing it when needed. Unknown entries are preserved. Game loading remains unverified.'))

    def patch(self,plain,changes):
        for key,(at,kit_at,kit,options) in self.modifications.items():
            if key in changes:
                plain[at]=options[changes[key]]
                if options[changes[key]]!=255:
                    plain[kit_at]=kit

"""PC story-mode GTA V/RDR2 fields; unrelated state is opaque.

SPDX-License-Identifier: GPL-3.0-or-later
No game assets, online profiles or native samples are included. See SOURCES.md.
"""
from collections import defaultdict
from decimal import Decimal
import struct
from rockstar_container import RockstarContainer,name_hash,u32

CHARACTERS=('Michael','Franklin','Trevor')
SKILLS=(('STAMINA','Stamina'),('SHOOTING_ABILITY','Shooting'),('STRENGTH','Strength'),
        ('STEALTH_ABILITY','Stealth'),('FLYING_ABILITY','Flying'),('WHEELIE_ABILITY','Driving'),
        ('LUNG_CAPACITY','Lung capacity'),('SPECIAL_ABILITY','Special ability'))


class RockstarSave:
    def __init__(self,raw,game,Field):
        self.container=RockstarContainer(raw,game);self.fields=[];self.positions={}
        self.warnings=self.container.warnings;plain=self.container.plain
        if game=='gtav':
            found=defaultdict(list)
            # Native signed-int statistic pairs: exact structure, field names,
            # types and offsets, not a first-match search across opaque bytes.
            schema=(8,((3742647683,5,0,0,0),(3021077118,5,0,4,0)))
            for frame in self.container.frames:
                if frame.structures.get(2199017832)!=schema:continue
                for identity,start,length in frame.blocks:
                    if identity!=2199017832 or length%8:continue
                    for at in range(start,start+length,8):found[u32(plain,at)].append(at+4)
            for n,name in enumerate(CHARACTERS):
                for stat,title in (('TOTAL_CASH','Cash ($)'),)+SKILLS:
                    matches=found[name_hash(f'sp{n}_{stat}')]
                    if len(matches)!=1:continue
                    at=matches[0];value=struct.unpack_from('>i',plain,at)[0];maximum=2147483647 if stat=='TOTAL_CASH' else 100
                    key=f'character:{n}:{stat.lower()}';self.positions[key]=at
                    self.fields.append(Field(key,title,value,at,'',0,max(maximum,value),
                        'Currency' if stat=='TOTAL_CASH' else 'Skills',collection=name,readonly=not 0<=value<=maximum,
                        note='Existing saved story-mode statistic only. Character availability, missions, rewards, inventory and unrelated statistics are preserved. Values outside the recognized range remain read-only.'))
        else:
            from rdr2_features import Rdr2Features
            self.rdr2=Rdr2Features(self,Field)
        if not self.fields:raise ValueError('No uniquely identified supported Rockstar story fields were found. This save variant is protected.')

    def patch(self,changes):
        plain=bytearray(self.container.plain)
        for key,value in changes.items():
            if key=='cash':
                cents=Decimal(str(value))*100
                if cents!=cents.to_integral_value():raise ValueError('Cash accepts at most two decimal places.')
                struct.pack_into('>I',plain,self.positions[key],int(cents))
            elif not hasattr(self,'rdr2'):struct.pack_into('>i',plain,self.positions[key],value)
        if hasattr(self,'rdr2'):self.rdr2.patch(plain,changes)
        result=self.container.encode(plain)
        return self.rdr2.supplies.finish(result,changes) if hasattr(self,'rdr2') else result

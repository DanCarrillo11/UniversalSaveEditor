"""Schema-checked regional monetary bounties and their current-bounty mirror.

SPDX-License-Identifier: GPL-3.0-or-later
Script references and limits are documented in SOURCES.md.
"""
from decimal import Decimal
import struct
from rockstar_container import u32

REGIONS=('Ambarino','New Hanover','Lemoyne','West Elizabeth','New Austin','Guarma')


class BountyFields:
    def __init__(self,campaign):
        self.campaign=campaign;self.f=campaign.f;self.raw=campaign.raw
        self.amounts={};self.flags={};self.current=None;self.candidates=();self.paused=False
        self.spans=();self.enabled=False
        # Build-1491 Global_40.f_358 has six 12-cell region records.
        if not campaign.root:return
        frame,root,length=campaign.root
        if length<359*8 or self.raw[root+358*8]!=6:return
        amounts=[campaign.scalar(359+n*12,5) for n in range(6)]
        flags=[campaign.scalar(359+n*12+5,5) for n in range(6)]
        temporary=campaign.scalar(11957,5)
        native=self.f.rows('CBountySaveStructure',(('CurrentBounty',6,0),))
        if any(at is None for at in amounts+flags) or temporary is None or len(native)!=1:return
        current=native[0][2]['CurrentBounty']
        values=[struct.unpack_from('>i',self.raw,at)[0] for at in amounts]
        live=u32(self.raw,current)
        if any(not 0<=v<=150000 for v in values) or live>150000:return
        self.current=current;self.values=values;self.enabled=True
        self.paused=struct.unpack_from('>i',self.raw,temporary)[0]!=0
        self.candidates=tuple(i for i,v in enumerate(values) if v==live)
        self.spans=tuple(amounts+flags+[current])
        note=('Saved monetary bounty in dollars/cents. The game may apply chapter-specific caps. '
              'Story restrictions, dead-or-alive regions, active pursuit, incidents and timers are preserved. '
              'If several regions match the native current bounty, those regions must retain a matching final amount; use Clear regional bounties to clear them together.')
        if self.paused:note='A mission has temporarily stored a bounty. Bounty editing is protected until that state ends.'
        for n,title in enumerate(REGIONS):
            key=f'bounty:region:{n}';at=amounts[n]
            self.amounts[key]=at;self.flags[key]=flags[n];self.f.positions[key]=at
            campaign.money[key]=(at,)
            self.f.fields.append(self.f.Field(key,title+' ($)',values[n]/100,at,'',0,1500,'Bounties',decimal=True,
                readonly=self.paused or not self.candidates,note=note))
        self.f.fields.append(self.f.Field('bounty:current','Native current bounty ($)',live/100,current,'',0,1500,'Bounties',decimal=True,
            readonly=True,note='Read-only mirror. The current region is not guessed from a shared amount. Consistent regional edits synchronize this value.'))
        clear=not live and not any(values) and not any(u32(self.raw,at)&4 for at in flags)
        self.f.positions['bounty:clear']=current
        self.f.fields.append(self.f.Field('bounty:clear','Clear regional bounties',int(clear),current,'',0,1,'Bounties',boolean=True,
            readonly=self.paused or clear,note=('Already clear. ' if clear else '')+
            ('A mission has temporarily stored a bounty; clearing is protected.' if self.paused else
            'Clears all six saved monetary bounties, the native current amount and only the regional monetary-wanted bit. Story lockdowns, dead-or-alive flags, active incidents and mission state remain unchanged. This is a clearing action; unchecking cannot restore previously applied bounties.')))

    def patch(self,plain,changes):
        edited={key:value for key,value in changes.items() if key in self.amounts}
        clear=changes.get('bounty:clear')==1
        if not edited and not clear:return
        if not self.enabled or self.paused:raise ValueError('Bounty editing is protected by the saved mission state.')
        if clear:
            if edited:raise ValueError('Clear regional bounties cannot be combined with individual bounty amounts. Reset the amounts first.')
            for key,at in self.amounts.items():
                struct.pack_into('>i',plain,at,0)
                flag=self.flags[key];struct.pack_into('>I',plain,flag,u32(self.raw,flag)&~4)
            struct.pack_into('>I',plain,self.current,0)
            return
        values=list(self.values)
        for key,value in edited.items():
            cents=Decimal(str(value))*100
            if cents!=cents.to_integral_value():raise ValueError('Bounties accept at most two decimal places.')
            values[int(key.rsplit(':',1)[1])]=int(cents)
        possible={values[n] for n in self.candidates}
        if len(possible)!=1:
            raise ValueError('The current region is ambiguous. Keep regions with the same original current bounty at the same final amount, or use Clear regional bounties.')
        struct.pack_into('>I',plain,self.current,possible.pop())
        for key in edited:
            if values[int(key.rsplit(':',1)[1])]==0:
                at=self.flags[key];struct.pack_into('>I',plain,at,u32(self.raw,at)&~4)

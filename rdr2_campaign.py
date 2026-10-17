"""Schema-checked build-1491 campaign globals and their native mirrors.

SPDX-License-Identifier: GPL-3.0-or-later
References: SOURCES.md. These are save fields, not live-memory addresses.
"""
from decimal import Decimal
import struct
from rockstar_container import u32,name_hash

ROOT=0x41d6f894
HORSE_SLOTS={name_hash('SLOTID_ACTIVE_HORSE'):0,(-832337898)&0xffffffff:1,
             1271463052:2,1983140194:3,677262775:4}


def scalar_paths(frame,identity,delta,kind,base=0,path=(),depth=0):
    """Resolve only inline structures, including extended PSCH byte offsets."""
    if depth>16 or identity not in frame.structures:return []
    size,fields=frame.structures[identity];out=[]
    if not base<=delta<base+size:return []
    for key,t,sub,off,ref in fields:
        if sub&0x80:continue
        off+=(sub&0x40)<<10
        if off>=size:continue
        route=path+((identity,key,t,sub,off,ref),)
        if t==kind and sub&0x3f==0 and base+off==delta and off+4<=size:out.append(route)
        if t==12 and sub&0x3f==0 and ref in frame.structures:
            child_size=frame.structures[ref][0]
            if child_size<=size-off and base+off<=delta<base+off+child_size:
                out+=scalar_paths(frame,ref,delta,kind,base+off,route,depth+1)
    return out


class CampaignFields:
    def __init__(self,features):
        self.f=features;self.raw=features.raw;self.money={};self.mirrors={};self._stats=None
        roots=[(frame,at,length) for frame in features.c.frames for h,at,length in frame.blocks if h==ROOT]
        self.root=roots[0] if len(roots)==1 else None
        self.camp_money();self.horse_mirrors();self.statistics()
        from rdr2_bounties import BountyFields
        self.bounties=BountyFields(self)

    def scalar(self,index,kind):
        if not self.root:return None
        frame,at,length=self.root;delta=index*8
        if delta<0 or delta+4>length:return None
        paths=scalar_paths(frame,ROOT,delta,kind)
        if len(paths)!=1:return None
        return at+delta

    def integer_stat(self,name):
        from rdr2_features import parser_hash,member
        if self._stats is None:
            self._stats={}
            rows=self.f.rows('CBaseStatsSaveStructure__CIntStatStruct',(('statId',12,0),('Data',5,0)))
            for frame,b,m in rows:
                if (member(frame,parser_hash('CBaseStatsSaveStructure__CIntStatStruct'),'statId',12)[1]==parser_hash('StatId')
                    and u32(self.raw,m['statId']+4)==0):
                    self._stats.setdefault(u32(self.raw,m['statId']),[]).append(m['Data'])
        matches=self._stats.get(name_hash(name),())
        return matches[0] if len(matches)==1 else None

    def camp_money(self):
        at=self.scalar(4283+325,5);stat=self.integer_stat('GANG_SAVINGS_CASH')
        if at is None or stat is None:return
        value=struct.unpack_from('>i',self.raw,at)[0]
        if not 0<=value<=2147483647 or struct.unpack_from('>i',self.raw,stat)[0]!=value:return
        key='camp:cash';self.money[key]=(at,stat);self.f.positions[key]=at
        self.f.fields.append(self.f.Field(key,'Camp funds ($)',value/100,at,'',0,21474836.47,'Camp',decimal=True,
            note='Changes the camp ledger balance and its saved statistic together. Two decimal places maximum. Donations, purchases, camp upgrades and chapter availability are preserved.'))

    def statistics(self):
        # Explicit scalar history counters only. Mission progress, economy,
        # challenge delivery, honor and names/hashes are deliberately excluded.
        specs=(('HEADSHOTS','Headshots'),('KILLS','Kills'),('DEATHS','Deaths'),
            ('FISH_ESCAPED','Fish escaped'),('HORSES_BROKEN','Horses broken'),
            ('STOLEN_HORSES_SOLD','Stolen horses sold'),('STOLEN_WAGONS_SOLD','Stolen wagons sold'),
            ('HORSE_STABLE_VISITS','Stable visits'),('BATHS_TAKEN','Baths taken'),
            ('BAR_DRINKS_CONSUMED','Bar drinks consumed'),('BAR_MEALS_CONSUMED','Bar meals consumed'),
            ('THEATRE_VISITS','Theatre visits'),('SHOWS_SEEN','Shows seen'),
            ('MEDICINE_ITEMS_USED','Medicine items used'),('DEADEYE_ITEMS_USED','Dead Eye items used'),
            ('PROVISION_ITEMS_USED','Provision items used'),('NUM_PEDS_ANTAGONIZED','People antagonized'))
        for name,title in specs:
            at=self.integer_stat(name)
            if at is not None:
                self.f.add('stat:'+name,title,at,'>i',0,2147483647,'Statistics',
                    note='Existing saved history counter only. Does not perform actions, change owned items, complete challenges, grant rewards or unlock platform achievements.')

    def horse_mirrors(self):
        from rdr2_features import parser_hash,member
        horses=[]
        for frame,h,b,m in self.f.active_items():
            if h!=parser_hash('CPedInventorySaveStructure__HorseItem'):continue
            slot=member(frame,h,'SlotId',6)
            if slot:horses.append((b,u32(self.raw,b+slot[0]),m))
        for b,slot,m in horses:
            key='item:'+self.raw[m['Guid']:m['Guid']+8].hex()+':bondingxp'
            field=next((f for f in self.f.fields if f.key==key),None)
            if field is None:continue
            n=HORSE_SLOTS.get(slot)
            if n is None or sum(s==slot for _,s,_ in horses)!=1:
                field.readonly=True;field.note='The horse script slot could not be identified uniquely; bonding XP is protected.';continue
            model=self.scalar(1097+n*436+9,5)
            if model is None or u32(self.raw,model)==0 or self.raw[self.root[1]+1096*8]!=7:
                field.readonly=True;field.note='The saved horse model is absent; bonding XP is protected.';continue
            # player_horse.c: f398 is an inline array with a header cell;
            # elements have four script cells, core indexes 0/1 are health/stamina.
            from rdr2_features import item_name,labels
            model_id=u32(self.raw,model)
            collection=f'Horse slot {n+1}'+(' · '+item_name(model_id) if f'{model_id:08x}' in labels() else '')
            for existing in self.f.fields:
                if existing.key.startswith(key.rsplit(':',1)[0]+':'):
                    existing.collection=collection
            for delta,title in ((399,'Health core'),(403,'Stamina core')):
                core=self.scalar(1097+n*436+delta,5)
                if core is not None and self.raw[self.root[1]+(1097+n*436+398)*8]==2:
                    self.f.add(key.rsplit(':',1)[0]+':'+title.lower().replace(' ','_'),title,core,'>i',0,100,'Horses',collection,
                        'Saved horse core (0–100), matched to an existing inventory horse by its unique slot. Temporary overpower effects, timers, breed and ownership are preserved.')
            at=self.scalar(1097+n*436+373,7)
            if at is None or struct.unpack_from('>f',self.raw,at)[0]!=field.value:
                field.readonly=True;field.note='Inventory and script bonding XP could not be matched; both copies are preserved.';continue
            self.mirrors[key]=((at,'>f'),)
            field.note='Synchronizes the existing horse’s inventory XP and saved script XP, matched by its unique horse slot. Breed, stable ownership and reward flags are preserved. The game determines rank from the horse’s own progression rules.'

    def patch(self,plain,changes):
        self.bounties.patch(plain,changes)
        for key,value in changes.items():
            if key in self.money:
                cents=Decimal(str(value))*100
                if cents!=cents.to_integral_value():raise ValueError('Camp funds accept at most two decimal places.')
                for at in self.money[key]:struct.pack_into('>i',plain,at,int(cents))
            for at,fmt in self.mirrors.get(key,()):struct.pack_into(fmt,plain,at,value)

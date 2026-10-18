"""Schema-gated RDR2 PC story fields and separately gated acquisition actions.

SPDX-License-Identifier: GPL-3.0-or-later
Format evidence and limitations: docs/RDR2_FIELDS.md and SOURCES.md.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json, math, struct, sys
from rockstar_container import checksum,u32,name_hash


@lru_cache(maxsize=4096)
def parser_hash(text):
    """Parser member names are case-sensitive, unlike game item/stat names."""
    return checksum(text.encode('ascii'),0)


@lru_cache(maxsize=1)
def labels():
    root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
    return json.loads((root/'assets/rdr2-labels.json').read_text(encoding='utf8'))


def item_name(identity):
    raw=labels().get(f'{identity:08x}')
    if not raw:return f'Unidentified entry · {identity:08X}'
    for prefix in ('A_C_HORSE_','CLOTHING_ITEM_','CLOTHING_','CONSUMABLE_','PROVISION_','WEAPON_','AMMO_','KIT_','AT_','HERB_'):
        if raw.startswith(prefix):raw=raw[len(prefix):];break
    return raw.replace('_',' ').title()


def member(frame,identity,name,kind,subtype=0):
    schema=frame.structures.get(identity)
    if not schema:return None
    matches=[(off+((sub&0x40)<<10),ref) for h,t,sub,off,ref in schema[1]
             if h==parser_hash(name) and t==kind and sub&0x3f==subtype and not sub&0x80]
    if len(matches)!=1:return None
    off,ref=matches[0]
    width={0:1,2:1,4:2,5:4,6:4,7:4,11:4,12:8,13:16,31:8}.get(kind)
    return (off,ref) if width and 0<=off<=schema[0]-width else None


class Rdr2Features:
    def __init__(self,owner,Field):
        self.owner,self.Field=owner,Field;self.c=owner.container;self.raw=self.c.plain
        self.formats={};self.related={};self.fields=owner.fields;self.positions=owner.positions
        self.cash();self.character();self.inventory();self.compendium();self.compendium_records();self.world()
        from rdr2_unlocks import UnlockFields
        self.unlocks=UnlockFields(self)
        from rdr2_components import ComponentFields
        self.components=ComponentFields(self)
        from rdr2_supplies import SupplyFields
        self.supplies=SupplyFields(self)
        from rdr2_campaign import CampaignFields
        self.campaign=CampaignFields(self)

    def rows(self,name,required):
        identity=parser_hash(name);result=[]
        for f in self.c.frames:
            schema=f.structures.get(identity)
            if not schema or not 1<=schema[0]<=4096:continue
            members={key:member(f,identity,key,kind,sub) for key,kind,sub in required}
            if any(v is None for v in members.values()):continue
            size=schema[0]
            for h,at,length in f.blocks:
                if h==identity and length%size==0 and length//size<=8192:
                    result.extend((f,i,{k:i+v[0] for k,v in members.items()}) for i in range(at,at+length,size))
        return result

    def add(self,key,title,at,fmt,minimum,maximum,group,collection='',note='',readonly=False,boolean=False):
        value=struct.unpack_from(fmt,self.raw,at)[0]
        if isinstance(value,float) and not math.isfinite(value):return
        if boolean and value not in (0,1):return
        readonly=readonly or not minimum<=value<=maximum
        # A nonstandard original remains visible and immutable, never normalized.
        low,high=min(minimum,value),max(maximum,value)
        self.positions[key]=at;self.formats[key]=fmt
        self.fields.append(self.Field(key,title,value,at,'',low,high,group,
            decimal=fmt.endswith('f'),boolean=boolean,collection=collection,readonly=readonly,note=note))

    def cash(self):
        # CE548CF5 is SLOTID_CURRENCY, not an item identity. Resolve the
        # CURRENCY_CASH item through the typed graph; never scan orphan bytes.
        root=parser_hash('CPedInventorySaveStructure')
        has_graph=any(h==root for frame in self.c.frames for h,b,length in frame.blocks)
        if has_graph:
            rows=[(frame,b,m) for frame,h,b,m in self.active_items() if h==parser_hash('SavegameInventoryItem')]
        else:
            rows=self.rows('SavegameInventoryItem',(('ItemId',11,7),('Quantity',31,0),('Guid',31,0),('ParentGuid',31,0)))
        matches=[]
        for frame,b,m in rows:
            slot=member(frame,parser_hash('SavegameInventoryItem'),'SlotId',6)
            if slot and u32(self.raw,m['ItemId'])==name_hash('CURRENCY_CASH') and u32(self.raw,b+slot[0])==name_hash('SLOTID_CURRENCY'):
                value=struct.unpack_from('>q',self.raw,m['Quantity'])[0]
                if 0<=value<=2147483647:matches.append((m['Quantity']+4,value))
        if len(matches)!=1:return
        at,value=matches[0];self.positions['cash']=at
        self.fields.append(self.Field('cash','Cash ($)',value/100,at,'',0,21474836.47,'Currency',decimal=True,
            note='Current carried cash, stored in cents. Requires a unique typed CURRENCY_CASH item in SLOTID_CURRENCY. When an inventory graph exists, only its active membership is used. Two decimal places maximum. Camp funds, historical income and rewards remain separate.'))

    def character(self):
        # Build 1491 script save root and attribute member are identified by
        # both type/member hashes. Bit 6 extends the 16-bit schema offset.
        candidates=[]
        for f in self.c.frames:
            root=0x41d6f894
            links=[(off+((sub&0x40)<<10),ref) for h,t,sub,off,ref in f.structures.get(root,(0,()))[1]
                   if (h,t,sub,ref)==(0xb5d75947,12,64,0x41d6f933)]
            if len(links)!=1:continue
            delta,identity=links[0];schema=f.structures.get(identity)
            if not schema or schema[0]!=568:continue
            for h,at,length in f.blocks:
                if h==root and delta+568<=length:candidates.append((f,at+delta,identity))
        if len(candidates)!=1:return
        f,base,identity=candidates[0];schema=f.structures[identity]
        def typed(h,t,off,ref=0):return (h,t,0,off,ref) in schema[1]
        # Honor requires a unique matching canonical value and persistent stat.
        if typed(0xa53cde40,5,280):
            stats=self.rows('CBaseStatsSaveStructure__CIntStatStruct',(('statId',12,0),('Data',5,0)))
            matches=[m['Data'] for sf,b,m in stats if u32(self.raw,m['statId'])==0x89587b4e and u32(self.raw,m['statId']+4)==0]
            at=base+280;value=struct.unpack_from('>i',self.raw,at)[0]
            if len(matches)==1 and struct.unpack_from('>i',self.raw,matches[0])[0]==value:
                self.add('honor','Honor',at,'>i',-320,320,'Honor',note='Synchronizes current honor and its saved statistic. Early story progression can clamp honor to ±240. Story milestones and rewards are preserved.')
                self.related['honor']=(matches[0],)
        # Serialized script arrays use eight-byte cells. Require the exact
        # child schema, float element, byte count and native count before use.
        for link,child,baseoff,count,group,entries in (
            (0xc3364edc,0x41d6f934,0,3,'Player cores',((0,'Health core',0,100),(1,'Stamina core',0,100),(2,'Dead Eye core',0,100))),
            (0x18d8e817,0x41d6f938,88,23,'Player progression',((0,'Health XP',0,1100),(1,'Stamina XP',0,1100),(2,'Dead Eye XP',0,1100),(13,'Weight',-100,100))),
        ):
            cs=f.structures.get(child)
            if not typed(link,12,baseoff,child) or not cs or cs[0]!=8+count*8 or self.raw[base+baseoff]!=count:continue
            for index,title,lo,hi in entries:
                offset=8+index*8
                direct=any(t==7 and sub==0 and off==offset for h,t,sub,off,ref in cs[1])
                wrapped=[ref for h,t,sub,off,ref in cs[1] if t==12 and sub==0 and off==offset]
                if not direct and not (len(wrapped)==1 and f.structures.get(wrapped[0],(0,()))[0]==8 and
                    any(t==7 and sub==0 and off==0 for h,t,sub,off,ref in f.structures[wrapped[0]][1])):continue
                key=f'player:{title.lower().replace(" ","_")}'
                self.add(key,title,base+baseoff+offset,'>f',lo,hi,group,
                    note='Saved Story Mode attribute. XP controls the base progression; challenge equipment bonuses and story-specific Dead Eye abilities remain separate.' if title.endswith('XP') else 'Saved Story Mode attribute, restored by the game on loading. Temporary core overpower effects are preserved.')
        players=self.rows('CPlayerPedSaveStructure',(('fHealth',7,0),))
        if len(players)==1:
            self.add('player:health','Saved health',players[0][2]['fHealth'],'>f',0,1000,'Player cores',
                note='Saved health on loading; the game can clamp it to its runtime maximum. Does not change core XP, equipment bonuses or maximum-health rules.')

    def pointer(self,frame,at,width):
        # PC RDR2 extended PSO pointers: low 12 bits select the block,
        # bits 12..19 are reserved, offset low 12 bits occupy bits 20..31;
        # the next little-endian word extends the byte offset.
        word=u32(self.raw,at);block=word&0xfff
        offset=(word>>20)|(struct.unpack_from('<I',self.raw,at+4)[0]<<12)
        if word&0xff000 or not 1<=block<=len(frame.blocks):raise ValueError('Unrecognized RDR2 inventory pointer.')
        h,start,length=frame.blocks[block-1]
        if offset>length or width>length-offset:raise ValueError('RDR2 inventory pointer exceeds its mapped block.')
        return h,start+offset,length-offset

    def active_items(self):
        # A parsed save is immutable. Reuse the validated graph for cash,
        # quantity controls, horse mirrors and acquisition instead of walking
        # the same hundreds of pointers separately for each feature.
        if not hasattr(self,'_inventory_rows'):self._inventory_rows=self._read_active_items()
        return self._inventory_rows

    def _read_active_items(self):
        rows=self.rows('CPedInventorySaveStructure',(('playerInventory',12,0),('backupInventory',12,0),('usingBackupInventory',0,0)))
        if len(rows)!=1:return []
        f,b,m=rows[0];flag=self.raw[m['usingBackupInventory']]
        if flag not in (0,1):return []
        field='backupInventory' if flag else 'playerInventory';base=m[field]
        link=member(f,parser_hash('CPedInventorySaveStructure'),field,12)
        if not link:return []
        arr=member(f,link[1],'items',13)
        if not arr:return []
        at=base+arr[0];count,capacity=struct.unpack_from('>HH',self.raw,at+8)
        if not 0<count<=capacity<=4096:return []
        try:
            identity,start,left=self.pointer(f,at,count*8)
            if identity!=12:return []
            result=[]
            for n in range(count):
                identity,record,left=self.pointer(f,start+n*8,48)
                schema=f.structures.get(identity)
                if not schema or left<schema[0]:return []
                word=u32(self.raw,start+n*8);target=f.blocks[(word&0xfff)-1]
                if target[2]%schema[0] or (record-target[1])%schema[0]:return []
                members={name:member(f,identity,name,t,sub) for name,t,sub in (
                    ('Guid',31,0),('ParentGuid',31,0),('ItemId',11,7),('Quantity',31,0))}
                if any(v is None for v in members.values()):return []
                result.append((f,identity,record,{k:record+v[0] for k,v in members.items()}))
            guids=[self.raw[m['Guid']:m['Guid']+8] for f,h,b,m in result]
            if len(set(guids))!=len(guids) or len({b for f,h,b,m in result})!=len(result):return []
            return result
        except (ValueError,struct.error):return []

    def inventory(self):
        items=self.active_items();counts=Counter(u32(self.raw,m['ItemId']) for f,h,b,m in items)
        for f,h,b,m in items:
            identity=u32(self.raw,m['ItemId']);name=labels().get(f'{identity:08x}','');title=item_name(identity)
            guid=self.raw[m['Guid']:m['Guid']+8].hex();key=f'item:{guid}'
            if h==parser_hash('SavegameInventoryItem') and name.startswith(('AMMO_','CONSUMABLE_','PROVISION_')) and not name.startswith(('PROVISION_TRINKET_','PROVISION_TALISMAN_')):
                # No deletion, ID swapping or synthetic GUID creation. Existing
                # satchel capacity and acquisition dependencies stay intact.
                self.add(key+':quantity',title,m['Quantity'],'>q',1,9999 if name.startswith('AMMO_') else 99,'Inventory',
                    'Ammunition' if name.startswith('AMMO_') else 'Supplies',
                    'Quantity of an existing item in the active inventory. The game may apply its own capacity limit. This does not increase satchel capacity or unlock purchases.')
            if h==parser_hash('CPedInventorySaveStructure__WeaponItem'):
                suffix=f' · copy {guid[-4:]}' if counts[identity]>1 else ''
                for field in ('Degradation','PermanentDegradation','Soot','Rust','Dirt'):
                    off=member(f,h,field,7)
                    if off:self.add(key+':'+field.lower(),field,b+off[0],'>f',0,1,'Weapon condition',title+suffix,
                        'Existing weapon only. 0 is clean/undamaged; 1 is maximum deterioration. Equipped slots, weapon identity, components and ownership are preserved.')
            if h==parser_hash('CPedInventorySaveStructure__HorseItem'):
                for field,lo,hi in (('BondingXp',0,10000),('Dirty',0,100),('Hungry',0,100)):
                    off=member(f,h,field,5)
                    if off:self.add(key+':'+field.lower(),{'BondingXp':'Bonding XP','Dirty':'Dirt','Hungry':'Hunger'}[field],b+off[0],'>i',lo,hi,'Horses',title,
                        'Existing active-inventory horse. Higher XP increases bonding; 0 removes dirt/hunger. Horse identity, stable slots, appearance and event multipliers are preserved.')

    def compendium(self):
        specs=(
            ('ItemAnimal','Animals',(('wasObserved','Studied'),('wasDiscovered','Discovered'))),
            ('ItemWeapon','Weapons',(('hasOwned','Owned record'),)),
            ('ItemEquipment','Equipment',(('owned','Owned record'),)),
            ('ItemHerb','Plants',(('wasObserved','Studied'),)),
            ('ItemFish','Fish',(('wasObserved','Studied'),)),
            ('ItemHorse','Horses',(('wasObserved','Studied'),)),
        )
        for type_name,category,flags in specs:
            rows=self.rows('CSaveCompendium__'+type_name,(('name',11,7),)+tuple((key,0,0) for key,label in flags))
            counts=Counter(u32(self.raw,m['name']) for f,b,m in rows)
            for f,b,m in rows:
                identity=u32(self.raw,m['name'])
                if counts[identity]!=1:continue
                for key,title in flags:
                    self.add(f'compendium:{type_name}:{identity:08x}:{key}',item_name(identity)+' · '+title,m[key],'>B',0,1,'Compendium',category,
                        'Compendium record only. Does not grant an item, unlock its shop purchase, complete a challenge or trigger a reward.',boolean=True)

    def world(self):
        rows=self.rows('CSimpleVariablesSaveStructure',(('GameClockHour',6,0),('GameClockMinute',6,0),('GameClockSecond',6,0)))
        if len(rows)==1:
            f,b,m=rows[0]
            for key,maximum in (('GameClockHour',23),('GameClockMinute',59),('GameClockSecond',59)):
                self.add('clock:'+key,key.replace('GameClock',''),m[key],'>I',0,maximum,'World clock',note='Saved clock time only. Calendar dates, story timers, schedules and active missions are preserved.')

    def compendium_records(self):
        note='Recorded compendium history only. Does not perform the action, grant items, change a living horse’s bonding, complete challenges or deliver rewards.'
        for suffix,category,specs in (
            ('ItemHorse','Horses',(('numBroken','Horses broken',4294967295),('highestBondingLevel','Highest recorded bonding level',4))),
            ('ItemGang','Gangs',(('ambushesSurvived','Ambushes survived',4294967295),('uniqueEncounters','Unique encounters',4294967295),
                ('bountiesCaptured','Bounties captured',4294967295),('gangMembersKilled','Gang members killed',4294967295))),
        ):
            rows=self.rows('CSaveCompendium__'+suffix,(('name',11,7),))
            counts=Counter(u32(self.raw,m['name']) for f,b,m in rows)
            for frame,base,m in rows:
                identity=u32(self.raw,m['name'])
                if counts[identity]!=1:continue
                for key,title,maximum in specs:
                    off=member(frame,parser_hash('CSaveCompendium__'+suffix),key,6)
                    if off:self.add(f'compendium:{suffix}:{identity:08x}:{key}',item_name(identity)+' · '+title,base+off[0],'>I',0,maximum,'Compendium',category,note)
        rows=self.rows('CSaveCompendium__ItemFish',(('name',11,7),('lures',13,0)))
        counts=Counter(u32(self.raw,m['name']) for f,b,m in rows);candidates=[]
        for frame,base,m in rows:
            identity=u32(self.raw,m['name']);count,capacity=struct.unpack_from('>HH',self.raw,m['lures']+8)
            if counts[identity]!=1 or not 0<count<=capacity<=64:continue
            h=parser_hash('CSaveCompendium__ItemFishLure');schema=frame.structures.get(h)
            label=member(frame,h,'lureName',11,7);number=member(frame,h,'numCaught',6)
            if not schema or not label or not number:continue
            size=schema[0]
            try:
                target,at,left=self.pointer(frame,m['lures'],count*size)
            except (ValueError,struct.error):continue
            word=u32(self.raw,m['lures']);block=frame.blocks[(word&0xfff)-1]
            if target!=h or not 1<=size<=4096 or block[2]%size or (at-block[1])%size:continue
            entries=[(u32(self.raw,at+i*size+label[0]),at+i*size+number[0]) for i in range(count)]
            if len({k for k,v in entries})!=len(entries):continue
            candidates.extend((identity,lure,off) for lure,off in entries)
        owners=Counter(off for identity,lure,off in candidates)
        for identity,lure,off in candidates:
            if owners[off]==1:
                self.add(f'compendium:ItemFish:{identity:08x}:lure:{lure:08x}',item_name(identity)+' · '+item_name(lure)+' · Caught',off,'>I',0,4294967295,'Compendium','Fish',note)

    def expected(self,key,value):
        fmt=self.formats.get(key)
        return struct.unpack(fmt,struct.pack(fmt,value))[0] if fmt else value

    def patch(self,plain,changes):
        for key,value in changes.items():
            fmt=self.formats.get(key)
            if not fmt:continue
            struct.pack_into(fmt,plain,self.positions[key],value)
            for at in self.related.get(key,()):struct.pack_into(fmt,plain,at,value)
        self.campaign.patch(plain,changes)
        self.unlocks.patch(plain,changes)
        self.components.patch(plain,changes)

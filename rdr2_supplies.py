"""Bounded, experimental acquisition of ordinary RDR2 satchel supplies.

SPDX-License-Identifier: GPL-3.0-or-later
No weapons, story objects, recipes, capacity upgrades or arbitrary item hashes.
"""
import secrets,struct
from rockstar_container import RockstarContainer,u32,name_hash
from rdr2_features import parser_hash,member,labels,item_name
from rdr2_pso import RsavDirectory,pointer

SUPPLIES=(
    ('CONSUMABLE_MEDICINE','Tonics'),('CONSUMABLE_MEDICINE_USED','Tonics'),
    ('CONSUMABLE_SNAKE_OIL','Tonics'),('CONSUMABLE_SNAKE_OIL_USED','Tonics'),
    ('CONSUMABLE_HORSE_REVIVER','Horse supplies'),
    ('CONSUMABLE_HORSE_MEDICINE','Horse supplies'),('CONSUMABLE_HORSE_STIMULANT','Horse supplies'),
    ('CONSUMABLE_HAIR_TONIC','Supplies'),
    ('CONSUMABLE_COFFEE','Food'),('CONSUMABLE_SUGARCUBE','Food'),
    ('CONSUMABLE_BAKED_BEANS_CAN','Food'),('CONSUMABLE_BISCUIT_BOX','Food'),
    ('CONSUMABLE_SWEET_CORN_CAN','Food'),('CONSUMABLE_OAT_CAKES','Food'),
    ('CONSUMABLE_PEACHES_CAN','Food'),('CONSUMABLE_PEAR','Food'),
    ('CONSUMABLE_PINEAPPLES_CAN','Food'),('CONSUMABLE_SALMON_CAN','Food'),
    ('CONSUMABLE_STRAWBERRIES_CAN','Food'),('CONSUMABLE_CHOCOLATE_BAR','Food'),
    ('AMMO_REVOLVER','Ammunition'),('AMMO_PISTOL','Ammunition'),
    ('AMMO_REPEATER','Ammunition'),('AMMO_RIFLE','Ammunition'),
    ('AMMO_SHOTGUN','Ammunition'),('AMMO_ARROW','Ammunition'),
)


class SupplyFields:
    def __init__(self,features):
        self.f=features;self.actions={};self.graph=None
        try:RsavDirectory(features.c)
        except ValueError:return
        if features.c.warnings:return
        rows=features.active_items();raw=features.raw;kind=parser_hash('SavegameInventoryItem')
        roots=features.rows('CPedInventorySaveStructure',(('playerInventory',12,0),('backupInventory',12,0),('usingBackupInventory',0,0)))
        if len(roots)!=1 or not rows:return
        frame,base,m=roots[0]
        if frame is not features.c.frames[0]:return
        cash=[(b,r) for fr,h,b,r in rows if h==kind and u32(raw,r['ItemId'])==name_hash('CURRENCY_CASH')]
        if len(cash)!=1:return
        source,cm=cash[0];slot=member(frame,kind,'SlotId',6);equipped=member(frame,kind,'Equipped',0)
        expected={'Guid':8,'ParentGuid':16,'ItemId':24,'Quantity':40}
        if frame.structures[kind][0]!=48 or any(cm[k]-source!=off for k,off in expected.items()):return
        if not slot or slot[0]!=28 or not equipped or equipped[0]!=32 or u32(raw,source+28)!=name_hash('SLOTID_CURRENCY') or raw[source+8:source+16]==bytes(8):return
        parent=raw[cm['ParentGuid']:cm['ParentGuid']+8]
        if parent==bytes(8) or sum(h==parser_hash('CPedInventorySaveStructure__CharacterItem') and raw[r['Guid']:r['Guid']+8]==parent for fr,h,b,r in rows)!=1:return
        inventory='backupInventory' if raw[m['usingBackupInventory']] else 'playerInventory'
        link=member(frame,parser_hash('CPedInventorySaveStructure'),inventory,12)
        array=member(frame,link[1],'items',13) if link else None
        if not array:return
        array_at=m[inventory]+array[0];count,capacity=struct.unpack_from('>HH',raw,array_at+8)
        if count!=len(rows) or count>=4096:return
        ref_id=u32(raw,array_at)&4095;ref_offset=(u32(raw,array_at)>>20)|(struct.unpack_from('<I',raw,array_at+4)[0]<<12)
        source_blocks=[n for n,(h,at,length) in enumerate(frame.blocks,1) if h==kind and at<=source<=at+length-48 and length%48==0]
        root_blocks=[n for n,(h,at,length) in enumerate(frame.blocks,1) if at<=array_at and array_at+16<=at+length]
        if len(source_blocks)!=1 or len(root_blocks)!=1 or frame.blocks[ref_id-1][2]%8:return
        # Include backup and inactive mapped records when checking GUID collisions.
        used=set()
        for h,at,length in frame.blocks:
            schema=frame.structures.get(h);guid=member(frame,h,'Guid',31);owner=member(frame,h,'ParentGuid',31)
            if not guid or not schema or not 1<=schema[0]<=4096 or length%schema[0]:continue
            for record in range(at,at+length,schema[0]):
                used.add(raw[record+guid[0]:record+guid[0]+8])
                if owner:used.add(raw[record+owner[0]:record+owner[0]+8])
        self.graph=(frame,source,source_blocks[0],root_blocks[0],array_at,ref_id,ref_offset,count,used)
        owned={u32(raw,r['ItemId']) for fr,h,b,r in rows}
        for name,category in SUPPLIES:
            h=name_hash(name)
            if labels().get(f'{h:08x}')!=name:continue
            key=f'supply:{h:08x}:add';done=int(h in owned);self.actions[key]=h
            features.fields.append(features.Field(key,item_name(h),done,0,'',0,1,'Add supplies',
                boolean=True,readonly=bool(done),collection=category,
                note='Add one unit of a missing satchel item. For items you already own, change their amounts under Inventory. Does not increase satchel capacity or unlock story content. Experimental: in-game loading has not been verified.'))

    def finish(self,raw,changes):
        requests=[self.actions[k] for k,v in changes.items() if k in self.actions and v==1]
        if any(v!=1 for k,v in changes.items() if k in self.actions):raise ValueError('Add supply is an apply action, not item removal.')
        if not requests:return raw
        if not self.graph:raise ValueError('RDR2 supply acquisition requires a recognized inventory graph.')
        frame,source,item_id,root_id,array_at,ref_id,ref_offset,count,used=self.graph
        if count+len(requests)>4096:raise ValueError('RDR2 inventory entry limit exceeded.')
        c=RockstarContainer(raw,'rdr2');plain=c.plain;replacements={}
        for n in (item_id,root_id,ref_id):
            h,at,length=frame.blocks[n-1];replacements[n]=bytearray(plain[at:at+length])
        inventory=replacements[item_id];refs=replacements[ref_id]
        new_ref_offset=len(refs);refs.extend(plain[frame.blocks[ref_id-1][1]+ref_offset:frame.blocks[ref_id-1][1]+ref_offset+count*8])
        used=set(used);namespace=plain[source+8:source+12]
        for h in requests:
            for attempt in range(128):
                guid=namespace+secrets.randbits(32).to_bytes(4,'big')
                if guid!=bytes(8) and guid not in used:break
            else:raise ValueError('Could not allocate a unique RDR2 inventory record ID.')
            used.add(guid);record=bytearray(plain[source:source+48]);record[8:16]=guid
            struct.pack_into('>I',record,24,h);struct.pack_into('>I',record,28,name_hash('SLOTID_SATCHEL'))
            record[32]=0;struct.pack_into('>q',record,40,1)
            refs.extend(pointer(item_id,len(inventory)));inventory.extend(record)
        root=replacements[root_id];relative=array_at-frame.blocks[root_id-1][1]
        root[relative:relative+8]=pointer(ref_id,new_ref_offset)
        struct.pack_into('>HH',root,relative+8,count+len(requests),count+len(requests))
        return c.replace_root_blocks(replacements)

"""Curated RE Engine fields; unknown state is retained byte-for-byte.

SPDX-License-Identifier: GPL-3.0-or-later
Format identifiers are documented in docs/RE_ENGINE_FORMAT.md. No upstream
implementation, SDK schema files, or translation databases are bundled.
"""
import math
import struct
from collections import Counter, defaultdict
from re_hashes import murmur32
from re_engine_container import ReEngineEnvelope
from re_engine_stream import StreamReader
from inventory_context import InventoryContext
from village_context import VillageContext
from item_art import item_art
from requiem_context import RequiemContext
from requiem_equipment import RequiemEquipment
from requiem_difficulty import RequiemDifficulty
from remake_context import RemakeContext
from remake_inventory_capacity import RemakeInventoryCapacity
from re_engine_extensions import EXTRA_SPECS,DIFFICULTIES,EngineExtensions

GAMES=('re2','re3','re4_remake','re7','re8','re9')
STEAM_APPS={'883710':'re2','952060':'re3','2050650':'re4_remake','418370':'re7','1196590':'re8','3764200':'re9'}
INVENTORY_OWNERS={'re2':0x41f30892,'re3':0x5f30b0dd,'re4_remake':0xbedd9bf5,'re8':0x3a83076c}
BACKUP_INVENTORY=murmur32(b'_BackupInventoryData')
# owner hash, serialized property, label, group, type, maximum
SPECS={
    're2':(
        (0x6da6a8d3,'HP','Health','Player health','<i',10000),
        (0x2675722d,'Count','Quantity','Inventory quantities','<i',999),
        (0x4e4210f9,'IsOpenedReward','Reward','Rewards','<B',1),
        (0x13e8507e,'GetFileList','File','Library files','<B',1),
    ),
    're3':(
        (0xa39a81a1,'HP','Health','Player health','<i',10000),
        (0xd759bf3d,'Count','Quantity','Inventory quantities','<i',999),
        (0x4ff2c755,'TotalShopPoint','Total shop points earned','Currency','<i',9999999),
        (0x4ff2c755,'IsShopItemPossessionFlag','Shop item','Shop unlocks','<B',1),
        (0x4ff2c755,'IsOpenedReward','Reward','Rewards','<B',1),
    ),
    're4_remake':(
        (0x4d4f1555,'_ExPoint','Extra content points','Currency','<i',9999999),
        (0xf65a5629,'SpinelCount','Spinels','Currency','<i',9999),
        (0x004b7a76,'CurrVirtualStackCount','Quantity','Inventory quantities','<i',999),
    ),
    're7':(
        (0x5e30cd4f,'Health','Health','Player health','<f',10000),
        (0x5e10ebe4,'Num','Quantity','Item box quantities','<i',999),
    ),
    're8':(
        (0x3a83076c,'money','Lei','Currency','<i',99999999),
        (0xe94db9b8,'CP','Challenge points (CP)','Currency','<i',9999999),
        (0x00346547,'SaveHealth','Current health','Player health','<f',10000),
        (0x10b5eaa5,'StackSize','Quantity','Inventory quantities','<i',999),
        (0xf033f1ce,'Has','Owned','Extra content','<B',1),
        (0xf033f1ce,'IsOpened','Opened','Extra content','<B',1),
        (0xf033f1ce,'IsUnlocked','Unlocked','Extra content','<B',1),
    ),
    're9':(
        (0x187cd802,'ClearPoint','Clear points','Currency','<Q',99999999),
        (0x6dc40103,'_Moneys','Money','Currency','<i',99999999),
        (0xc29aee68,'_Moneys','Carry-over money','Currency','<i',99999999),
        (0x239d83eb,'PurchaseUnlocked','Available to purchase','Extra shop','<B',1),
        (0x239d83eb,'AcquisitionUnlocked','Acquisition unlocked','Extra shop','<B',1),
        (0x239d83eb,'Received','Received','Extra shop','<B',1),
        (0x2ba65272,'Unlocked','Unlocked','Bonus content','<B',1),
        (0x474e21b2,'PurchaseUnlocked','Available to purchase','Artwork','<B',1),
        (0x474e21b2,'Purchased','Purchased','Artwork','<B',1),
        (0x0803be3c,'PurchaseUnlocked','Available to purchase','Figures','<B',1),
        (0x0803be3c,'Purchased','Purchased','Figures','<B',1),
        (0xce5ec358,'Unlocked','Unlocked','Special options','<B',1),
    ),
}
for _game,_specs in EXTRA_SPECS.items():SPECS[_game]+= _specs


class ReEngineSave:
    def __init__(self,raw,game,field_type,path=None,account_id=None):
        self.envelope=ReEngineEnvelope(raw,game,path,account_id)
        self.account=self.envelope.account
        self.warnings=self.envelope.warnings
        prefix=bytes(self.envelope.offset)
        self.data=prefix+self.envelope.payload
        nodes=StreamReader(self.data,len(prefix)).parse()
        identities=InventoryContext(nodes,self.data)
        extensions=EngineExtensions(nodes,self.data,game)
        extra_ids={(owner,murmur32(name.encode())) for owner,name,*_ in EXTRA_SPECS[game]}
        village=VillageContext(nodes,self.data) if game=='re8' else None
        self.requiem=RequiemContext(nodes,self.data) if game=='re9' else None
        self.requiem_equipment=RequiemEquipment(self.requiem,field_type) if self.requiem else None
        self.requiem_difficulty=RequiemDifficulty(self.requiem,field_type) if self.requiem else None
        self.remake=RemakeContext(nodes,self.data,field_type) if game=='re4_remake' else None
        self.inventory_capacity=RemakeInventoryCapacity(nodes,self.data,game,field_type) if game in ('re2','re3') else None
        wanted={(owner,murmur32(name.encode())):(label,group,fmt,maximum)
                for owner,name,label,group,fmt,maximum in SPECS[game]}
        selected=[]
        for node in nodes:
            specification=wanted.get((node.owner,node.field))
            if specification is None:continue
            extended=(node.owner,node.field) in extra_ids
            if extended and not extensions.allowed(node):continue
            if game=='re9' and any(owner==0x3a83076c and name==BACKUP_INVENTORY for owner,name,_ in node.path):continue
            label,group,fmt,maximum=specification
            if village:
                if group=='Inventory quantities' and not village.is_inventory_item(node):continue
                if group=='Extra content' and not village.is_extra_content(node):continue
            if 'quantities' in group and game in INVENTORY_OWNERS:
                if not any(owner==INVENTORY_OWNERS[game] for owner,_,_ in node.path):continue
            expected=2 if fmt=='<B' else 11 if fmt=='<f' else 10 if fmt=='<Q' else 8 if fmt=='<I' else 7
            if node.kind!=expected or node.fmt!=fmt:
                raise ValueError('A recognized RE Engine field has an unsupported type.')
            value=struct.unpack_from(fmt,self.data,node.offset)[0]
            if game=='re4_remake' and 'quantities' in group:
                maximum,_,_=identities.quantity_limit(game,node,value,maximum)
                specification=(label,group,fmt,maximum)
            if not math.isfinite(value) or not 0<=value<=maximum:
                # Empty inventory entries can have sentinel counts; never expose them.
                if extended or 'quantities' in group or (game=='re9' and label=='Carry-over money' and value==-1):continue
                raise ValueError('A recognized RE Engine field is outside its supported range.')
            if 'quantities' in group and value==0:continue
            selected.append((node,specification,value))
        extra=self.requiem.fields(field_type) if self.requiem else []
        if self.remake:extra.extend(self.remake.fields)
        if self.inventory_capacity:extra.extend(self.inventory_capacity.fields)
        if self.requiem_equipment:extra.extend(self.requiem_equipment.fields)
        if self.requiem_difficulty:extra.extend(self.requiem_difficulty.fields)
        if not selected and not extra:
            raise ValueError('This file has no supported editable fields. Open a gameplay slot for health or inventory, or the system profile for currency and unlocks.')
        if len(selected)+len(extra)>5000:raise ValueError('Too many editable fields in this RE Engine variant.')
        totals=Counter((node.owner,node.field) for node,_,_ in selected)
        indexes=defaultdict(dict);self.fields=[];self.operations={}
        for node,(label,group,fmt,maximum),value in selected:
            array_value=len(node.path)>1 and node.path[-1][:2]==node.path[-2][:2]
            identity=node.path if array_value else node.path[:-1]
            family=(node.owner,group)
            if identity not in indexes[family]:indexes[family][identity]=len(indexes[family])+1
            index=indexes[family][identity]
            indexed=totals[node.owner,node.field]>1 or fmt=='<B'
            shown=(f'Entry {index} · {label}' if fmt=='<B' else f'{label} · Entry {index}') if indexed else label
            key=f'{node.owner:08x}:{node.field:08x}:{node.offset}'
            note='Changes an existing entry; item identity, equipment and slot layout are preserved.' if 'quantities' in group else ''
            collection=''
            identifier=None
            if 'quantities' in group:
                identifier=identities.item_id(game,node)
                identity=f'ID {identifier}' if identifier is not None else 'identity not mapped'
                shown=f'Unidentified item · {identity} · Entry {index}'
                note='Item-name mapping is pending. Only this existing quantity is changed; identity and equipment are preserved.'
                collection='Unidentified items'
                art=item_art(game,identifier)
                if art:
                    shown=f'{art.name} · Entry {index}'
                    collection=art.category
                    note=f'Item ID {identifier}. Existing quantity only; identity, equipment and layout are preserved.'
                if village:
                    identifier=village.identity(node)
                    shown=f'Item ID {identifier:08X} · Quantity · Entry {index}'
                    collection='Existing stacks' if value>1 else 'Single items · read-only'
                    note=('Existing stack only. Names and in-game stack caps are not mapped; item IDs, loaded ammunition, upgrades and layout are preserved.' if value>1 else
                          'Single-item records are preserved because their stackability is not verified. Weapons, key items and other single objects are not duplicated.')
            if village and group=='Extra content':
                shown=f'Content ID {village.identity(node):08X} · {label} · Entry {index}'
                note='Separate saved content flag. This does not guarantee delivery, grant DLC ownership or update related challenges. Unknown dependencies and other flags are preserved.'
            if game=='re3' and label.startswith('Total shop'):
                note='Total points earned. The game also tracks purchased shop items separately.'
            choices=()
            capacity_readonly=False
            if 'quantities' in group:
                maximum,capacity_readonly,capacity_note=identities.quantity_limit(game,node,value,maximum)
                if capacity_note:note+=' '+capacity_note
            if (node.owner,node.field) in extra_ids:
                shown,note=extensions.describe(node,shown,group)
                if group=='Difficulty':choices=DIFFICULTIES[game]
            self.fields.append(field_type(key,shown,value,node.offset,fmt,1 if 'quantities' in group else 0,maximum,group,
                                          decimal=fmt=='<f',boolean=fmt=='<B',choices=choices,note=note,collection=collection,
                                          readonly=capacity_readonly or bool(village and 'quantities' in group and value==1),item_id=identifier))
            self.operations[key]=(node.offset,fmt)
        self.fields.extend(extra)
        self.operations.update({f.key:(f.offset,f.fmt) for f in extra if not f.readonly and f.fmt})

    def patch(self,changes):
        result=bytearray(self.data)
        for key,value in changes.items():
            if self.requiem_equipment and key in self.requiem_equipment.operations:continue
            if self.requiem_difficulty and key in self.requiem_difficulty.operations:continue
            if self.inventory_capacity and key in self.inventory_capacity.operations:continue
            if key not in self.operations:raise ValueError('Unauthorized RE Engine field.')
            offset,fmt=self.operations[key]
            struct.pack_into(fmt,result,offset,value)
        if self.requiem:self.requiem.apply_health_levels(result,changes)
        if self.requiem_equipment:self.requiem_equipment.patch(result,changes)
        if self.requiem_difficulty:self.requiem_difficulty.patch(result,changes)
        if self.remake:self.remake.patch(result,changes)
        if self.inventory_capacity:self.inventory_capacity.patch(result,changes)
        return self.envelope.patch(bytes(result[self.envelope.offset:]))

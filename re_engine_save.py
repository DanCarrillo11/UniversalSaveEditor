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

GAMES=('re2','re3','re4_remake','re7','re9')
STEAM_APPS={'883710':'re2','952060':'re3','2050650':'re4_remake','418370':'re7','3764200':'re9'}
INVENTORY_OWNERS={'re2':0x41f30892,'re3':0x5f30b0dd,'re4_remake':0xbedd9bf5}
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


class ReEngineSave:
    def __init__(self,raw,game,field_type,path=None,account_id=None):
        self.envelope=ReEngineEnvelope(raw,game,path,account_id)
        self.account=self.envelope.account
        self.warnings=self.envelope.warnings
        prefix=bytes(self.envelope.offset)
        self.data=prefix+self.envelope.payload
        nodes=StreamReader(self.data,len(prefix)).parse()
        wanted={(owner,murmur32(name.encode())):(label,group,fmt,maximum)
                for owner,name,label,group,fmt,maximum in SPECS[game]}
        selected=[]
        for node in nodes:
            specification=wanted.get((node.owner,node.field))
            if specification is None:continue
            if game=='re9' and any(owner==0x3a83076c and name==BACKUP_INVENTORY for owner,name,_ in node.path):continue
            label,group,fmt,maximum=specification
            if 'quantities' in group and game in INVENTORY_OWNERS:
                if not any(owner==INVENTORY_OWNERS[game] for owner,_,_ in node.path):continue
            expected=2 if fmt=='<B' else 11 if fmt=='<f' else 10 if fmt=='<Q' else 7
            if node.kind!=expected or node.fmt!=fmt:
                raise ValueError('A recognized RE Engine field has an unsupported type.')
            value=struct.unpack_from(fmt,self.data,node.offset)[0]
            if not math.isfinite(value) or not 0<=value<=maximum:
                # Empty inventory entries can have sentinel counts; never expose them.
                if 'quantities' in group or (game=='re9' and label=='Carry-over money' and value==-1):continue
                raise ValueError('A recognized RE Engine field is outside its supported range.')
            if 'quantities' in group and value==0:continue
            selected.append((node,specification,value))
        if not selected:
            raise ValueError('This file has no supported editable fields. Open a gameplay slot for health or inventory, or the system profile for currency and unlocks.')
        if len(selected)>5000:raise ValueError('Too many editable fields in this RE Engine variant.')
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
            if game=='re3' and label.startswith('Total shop'):
                note='Total points earned. The game also tracks purchased shop items separately.'
            self.fields.append(field_type(key,shown,value,node.offset,fmt,1 if 'quantities' in group else 0,maximum,group,
                                          decimal=fmt=='<f',boolean=fmt=='<B',note=note))
            self.operations[key]=(node.offset,fmt)

    def patch(self,changes):
        result=bytearray(self.data)
        for key,value in changes.items():
            if key not in self.operations:raise ValueError('Unauthorized RE Engine field.')
            offset,fmt=self.operations[key]
            struct.pack_into(fmt,result,offset,value)
        return self.envelope.patch(bytes(result[self.envelope.offset:]))

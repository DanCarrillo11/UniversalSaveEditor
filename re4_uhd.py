"""Independent Steam RE4 (2005) reader. SPDX-License-Identifier: GPL-3.0-or-later.

UHD offsets and CRC ranges were verified on a local file. Runtime property
names were cross-checked with nipkownix/re4_tweaks; see docs/RE4_UHD_FORMAT.md.
"""
import struct
from re4_items import WEAPONS, QUANTITIES

FILE_SIZE=1047200
FIRST_SLOT=0x1EE8
SLOT_SIZE=0xCAFC
SLOT_COUNT=20
VERSION=0x402
DIFFICULTIES=(1,3,5,6)
DIFFICULTY_NAMES=('Very Easy','Easy','Normal','Professional')
INVENTORY=0x373c
ITEM_COUNT=384


def _crc_table():
    table=[]
    for index in range(256):
        value=index<<24
        for _ in range(8):
            value=((value<<1)^(0x04C11DB7 if value&0x80000000 else 0))&0xffffffff
        table.append(value)
    return tuple(table)


CRC_TABLE=_crc_table()


def checksum(data):
    """MSB-first CRC-32, polynomial 0x04C11DB7, initial/final XOR zero."""
    value=0
    for byte in data:value=((value<<8)&0xffffffff)^CRC_TABLE[(value>>24)^byte]
    return value


class Re4UhdSave:
    def __init__(self,raw,field_type,slot_type):
        if len(raw)!=FILE_SIZE:raise ValueError('Unsupported Resident Evil 4 (2005) Steam save size.')
        self.slots=[];self.records=[];self.warnings=[];self.upgrades={}
        for physical_slot in range(SLOT_COUNT):
            base=FIRST_SLOT+physical_slot*SLOT_SIZE
            record=raw[base:base+SLOT_SIZE]
            if not any(record):continue
            if struct.unpack_from('<I',record,4)[0]!=VERSION:
                raise ValueError(f'Slot {physical_slot+1} has an unsupported RE4 UHD record version.')
            mode=record[0x3520]
            if mode not in DIFFICULTIES or record[0x3D]!=mode:
                raise ValueError(f'Slot {physical_slot+1} has unsupported or inconsistent difficulty data.')
            for offset,length,name in ((0,0x1FC,'header'),(SLOT_SIZE-4,SLOT_SIZE-4,'record')):
                start=4 if offset==0 else 0
                stored=struct.unpack_from('<I',record,offset)[0]
                if stored!=checksum(record[start:start+length]):
                    self.warnings.append(f'Slot {physical_slot+1}: the {name} integrity check does not match. Applying requires explicit integrity repair.')
            fields=[]
            def add(key,label,offset,fmt,low,high,group):
                value=struct.unpack_from(fmt,record,offset)[0]
                if not low<=value<=high:
                    raise ValueError(f'Slot {physical_slot+1} has unsupported {label.lower()} data.')
                fields.append(field_type(key,label,value,base+offset,fmt,low,high,group))
            add('money','Pesetas',0x4C,'<i',0,99999999,'Currency')
            fields.append(field_type('difficulty','Difficulty',DIFFICULTIES.index(mode),base+0x3520,'',0,3,'Difficulty',choices=DIFFICULTY_NAMES,
                note='Updates both saved mode values. Does not recreate a new game or change existing enemies and rewards.'))
            add('player_hp','Current HP',0x58,'<h',0,2400,'Player health')
            add('player_max_hp','Maximum HP',0x5A,'<h',1,2400,'Player health')
            add('ashley_hp','Current HP',0x5C,'<h',0,1200,'Ashley health')
            add('ashley_max_hp','Maximum HP',0x5E,'<h',1,1200,'Ashley health')
            add('save_count','Number of saves',0x40,'<H',0,65535,'Save statistics')
            add('round','Completed rounds',0x42,'<H',0,65535,'Save statistics')
            for key,label,offset,fmt in (
                ('chapter_continues','Current chapter continues',0x3504,'<H'),
                ('total_continues','Total continues',0x3506,'<H'),
                ('chapter_kills','Current chapter kills',0x3508,'<I'),
                ('total_kills','Total kills',0x350C,'<I'),
                ('chapter_hits','Current chapter hits',0x3510,'<I'),
                ('total_hits','Total hits',0x3514,'<I'),
                ('chapter_shots','Current chapter shots',0x3518,'<I'),
                ('total_shots','Total shots',0x351C,'<I'),
            ):add(key,label,offset,fmt,0,65535 if fmt=='<H' else 99999999,'Combat statistics')
            for entry in range(ITEM_COUNT):
                off=INVENTORY+entry*12
                identifier,word,loaded=struct.unpack_from('<3H',record,off)
                if not record[off+11]&1:continue # Only physical case entries, not residual/quest records.
                if identifier in WEAPONS:
                    name,limits=WEAPONS[identifier]
                    for part,(label,maximum) in enumerate(zip(('Firepower','Firing speed','Reload speed','Capacity'),limits)):
                        value=((word>>(part*4))&15)+1
                        key=f'weapon:{entry}:{part}'
                        supported=value<=maximum
                        fields.append(field_type(key,f'{name} · {label}',value,base+off+2,'',value if part==3 else 1,max(value,maximum),'Weapon upgrades',readonly=not supported,
                            note=f'Case entry {entry+1}. Capacity can only increase to preserve loaded ammunition. Item identity, exclusive prerequisites, case position and rotation are preserved. Unknown upgrade tiers remain read-only.'))
                        if supported:self.upgrades[len(self.slots),key]=(base+off+2,part)
                    fields.append(field_type(f'weapon:{entry}:loaded',name+' · Loaded ammunition',loaded>>3,base+off+4,'',0,8191,'Weapon upgrades',readonly=True,
                        note='Loaded rounds and their low flag bits are preserved; reserve ammunition stacks can be edited separately.'))
                elif identifier in QUANTITIES:
                    name,limit,group=QUANTITIES[identifier]
                    if not word:continue
                    fields.append(field_type(f'case:{entry}',name,word,base+off+2,'<H',1,max(word,limit),group,
                        note=f'Existing case entry {entry+1}. Item identity, placement, rotation, flags and record count are preserved; zero/deletion and new case objects are not supported.'))
            self.slots.append(slot_type(f'Slot {physical_slot+1}',fields));self.records.append(base)
        if not self.slots:raise ValueError('No populated RE4 UHD save slots found. Save at a typewriter first.')

    def finish(self,result,changes,repair_crc):
        for key,value in changes.items():
            if key not in self.upgrades:continue
            offset,part=self.upgrades[key]
            original=struct.unpack_from('<H',result,offset)[0]
            mask=15<<(part*4)
            struct.pack_into('<H',result,offset,(original&~mask)|((value-1)<<(part*4)))
        touched={index for index,key in changes}
        for index,slot in enumerate(self.slots):
            values={field.key:changes.get((index,field.key),field.value) for field in slot.fields}
            for prefix in ('player','ashley'):
                if values[prefix+'_hp']>values[prefix+'_max_hp']:
                    raise ValueError('Current HP cannot exceed maximum HP. Adjust both values together.')
            if index not in touched and not repair_crc:continue
            base=self.records[index]
            if (index,'difficulty') in changes:
                mode=DIFFICULTIES[changes[index,'difficulty']]
                result[base+0x3D]=mode;result[base+0x3520]=mode
            struct.pack_into('<I',result,base,checksum(result[base+4:base+0x200]))
            struct.pack_into('<I',result,base+SLOT_SIZE-4,checksum(result[base:base+SLOT_SIZE-4]))
        return result

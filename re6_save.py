"""Independent bounded RE6 PC profile patches. GPL-3.0-or-later.

Format offsets: lightningdotnet/resident-evil-6-save-editor; independently
cross-checked with a public Steam profile. No upstream code is bundled.
"""
import struct
from re6_skills import SKILLS,MODE_SKILLS
from re6_items import SUPPLIES

FILE_SIZE=39416
VERSION=bytes.fromhex('01180712')
CHARACTERS=('Leon','Helena','Chris','Piers','Jake','Sherry','Ada','Agent')
STAGES=('Urban Chaos','Steel Beast','Mining the Depths','Rail Yard','High Seas Fortress',
        'The Catacombs','Requiem for War','Liquid Fire','Rooftop Mission','Creature Workshop')


def checksum(raw):
    return sum(word[0] for word in struct.iter_unpack('<I',raw[0x18:]))&0xffffffff


def looks_like_re6(raw):
    return len(raw)==FILE_SIZE and raw[:4]==VERSION and struct.unpack_from('<I',raw,4)[0]==FILE_SIZE


class Re6Save:
    def __init__(self,raw,field_type):
        if not looks_like_re6(raw):raise ValueError('Unsupported Resident Evil 6 PC profile layout.')
        self.raw=bytes(raw);self.fields=[];self.operations={};self.warnings=[];self.skill_operations={}
        if struct.unpack_from('<I',raw,8)[0]!=checksum(raw):
            self.warnings=['The RE6 profile integrity check does not match. Applying requires explicit integrity repair.']
        points=struct.unpack_from('<I',raw,1804)[0]
        if points>9999999:raise ValueError('Unsupported RE6 skill point balance.')
        self.fields.append(field_type('skill_points','Skill points',points,1804,'',0,9999999,'Currency'))
        self.operations['skill_points']=(1804,'<I',None)
        for group,base,sets in (('Campaign skills',1920,1),('Mercenaries skills',2344,8),
                               ('Siege skills',1752,8),('Onslaught skills',26732,8),
                               ('Survivors skills',26768,8),('Predator skills',26804,8)):
            count=sets if group not in ('Campaign skills','Mercenaries skills') else sets*3
            for index in range(count):
                offset=base+index*4;identifier=struct.unpack_from('<I',raw,offset)[0]
                key=f'skill:{group}:{index}'
                options=dict(SKILLS if group=='Campaign skills' else MODE_SKILLS)
                if identifier not in options:options[identifier]=f'Existing skill ID {identifier} (preserved)'
                values=tuple(options)
                label=f'Skill {index+1}' if group not in ('Campaign skills','Mercenaries skills') else f'Skill {index%3+1}'+(f' · Set {index//3+1}' if sets>1 else '')
                self.fields.append(field_type(key,label,values.index(identifier),offset,'',0,len(values)-1,group,
                    choices=tuple(options[v] for v in values),note='Changes this equipped skill slot only. Purchase/unlock records and game settings are preserved. Extra modes show the known shared skill catalogue; mode restrictions are not verified. No purchase or infinite-ammo unlock is implied.'))
                self.skill_operations[key]=(offset,values)
        def flag(key,label,offset,bit,group,fmt='<B'):
            value=struct.unpack_from(fmt,raw,offset)[0]
            self.fields.append(field_type(key,label,(value>>bit)&1,offset,'',0,1,group,boolean=True))
            self.operations[key]=(offset,fmt,bit)
        for index,character in enumerate(CHARACTERS[:7]):
            for costume in range(4):
                position=index*4+costume
                label=character if costume==0 else character+' · Costume '+str(costume)
                flag(f'character:{position}',label,2448+position//8,position%8,'Characters and costumes')
        for bit,name in ((4,'Carla'),(5,'Agent')):
            flag('extra_character:'+name,name,2451,bit,'Characters and costumes')
        for mode in range(2):
            for index,stage in enumerate(STAGES):
                flag(f'stage:{mode}:{index}',stage,2440,index+mode*10,'No Mercy stages' if mode else 'Mercenaries stages','<I')
        for character,name in enumerate(CHARACTERS):
            base=34028+character*112+16
            for index in range(24):
                offset=base+index*4
                identifier=struct.unpack_from('<H',raw,offset)[0]&0xfff
                count=struct.unpack_from('<h',raw,offset+2)[0]
                if identifier==0 or not 0<=count<=999:continue
                key=f'supply:{character}:{index}'
                mapped=identifier in SUPPLIES
                title=SUPPLIES.get(identifier,f'Unmapped item ID {identifier}')
                self.fields.append(field_type(key,f'Slot {index+1} · {title}',count,offset+2,'',0,999,name+' supplies',readonly=not mapped,
                    note=(f'Existing reserve supply ID {identifier}. Depleted entries can be refilled. Identity, flags, weapon state and layout are preserved; actual game stack caps are not mapped.' if mapped else
                          'Preserved read-only: this may be a weapon record whose count word also stores state, or an unknown item. It is not treated as a simple supply quantity.')))
                if mapped:self.operations[key]=(offset+2,'<h',None)
        for campaign,name in enumerate(('Leon','Chris','Jake','Ada')):
            for index in range(20):
                offset=2016+campaign*20+index;original=raw[offset]
                key=f'emblem:{campaign}:{index}'
                self.fields.append(field_type(key,f'{name} · Emblem {index+1}',int(bool(original)),offset,'',
                    int(bool(original)),1,'Serpent emblems',boolean=True,readonly=bool(original),
                    note=f'Saved state {original}. Adds an uncollected emblem only; existing nonzero states and campaign progress are preserved.'))
                if not original:self.operations[key]=(offset,'<B',None)
        merc_characters=tuple(name+suffix for name in CHARACTERS[:7] for suffix in ('',' (Alt)'))+('Carla','Agent')
        for mode,base in (('Solo',9448),('Duo',13768)):
            for stage_index,stage in enumerate(STAGES):
                for character,name in enumerate(merc_characters):
                    offset=base+stage_index*432+character*12
                    collection=f'{mode} · {stage}'
                    for delta,part,label,fmt,maximum in ((1,'rank','Rank','<B',6),(4,'score','Score','<I',999999999),
                                                       (8,'kills','Enemies defeated','<B',255),(9,'combo','Maximum combo','<B',255)):
                        value=struct.unpack_from(fmt,raw,offset+delta)[0]
                        if value>maximum:continue
                        key=f'merc_record:{mode}:{stage_index}:{character}:{part}'
                        self.fields.append(field_type(key,name+' · '+label,value,offset+delta,'',0,maximum,'Mercenaries records',
                            choices=('SS','S','A','B','C','D','E') if part=='rank' else (),collection=collection,
                            note='Existing stored record only. Does not complete a campaign, purchase skills or change online records.'))
                        self.operations[key]=(offset+delta,fmt,None)

    def patch(self,changes):
        result=bytearray(self.raw)
        for key,value in changes.items():
            if key in self.skill_operations:
                offset,values=self.skill_operations[key]
                struct.pack_into('<I',result,offset,values[value]);continue
            if key not in self.operations:raise ValueError('Unauthorized RE6 field.')
            offset,fmt,bit=self.operations[key]
            if bit is not None:
                original=struct.unpack_from(fmt,result,offset)[0]
                value=(original&~(1<<bit))|(value<<bit)
            struct.pack_into(fmt,result,offset,value)
        struct.pack_into('<I',result,8,checksum(result))
        return bytes(result)

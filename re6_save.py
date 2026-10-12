"""Independent bounded RE6 PC profile patches. GPL-3.0-or-later.

Format offsets: lightningdotnet/resident-evil-6-save-editor; independently
cross-checked with a public Steam profile. No upstream code is bundled.
"""
import struct

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
        self.raw=bytes(raw);self.fields=[];self.operations={};self.warnings=[]
        if struct.unpack_from('<I',raw,8)[0]!=checksum(raw):
            self.warnings=['The RE6 profile integrity check does not match. Applying requires explicit integrity repair.']
        points=struct.unpack_from('<I',raw,1804)[0]
        if points>9999999:raise ValueError('Unsupported RE6 skill point balance.')
        self.fields.append(field_type('skill_points','Skill points',points,1804,'',0,9999999,'Currency'))
        self.operations['skill_points']=(1804,'<I',None)
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
                if identifier==0 or not 0<count<=999:continue
                key=f'supply:{character}:{index}'
                self.fields.append(field_type(key,f'Slot {index+1} quantity',count,offset+2,'',1,999,name+' supplies',
                                              note=f'Existing item ID {identifier}. Item identity and its flags are preserved.'))
                self.operations[key]=(offset+2,'<h',None)

    def patch(self,changes):
        result=bytearray(self.raw)
        for key,value in changes.items():
            if key not in self.operations:raise ValueError('Unauthorized RE6 field.')
            offset,fmt,bit=self.operations[key]
            if bit is not None:
                original=struct.unpack_from(fmt,result,offset)[0]
                value=(original&~(1<<bit))|(value<<bit)
            struct.pack_into(fmt,result,offset,value)
        struct.pack_into('<I',result,8,checksum(result))
        return bytes(result)

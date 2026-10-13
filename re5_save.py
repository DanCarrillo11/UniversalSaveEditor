"""Independent RE5 Steamworks profile adapter. SPDX-License-Identifier: GPL-3.0-or-later.

Format facts cross-checked with shinneider/RE5-Save-Editor and a public Steam
fixture; no accounts are reassigned. See docs/RE5_FORMAT.md.
"""
import struct

FILE_SIZE=23888
CHAIN_SEED=bytes.fromhex('00211108c04b0000')
GUNS=('M92F','H&K P8','SIG P226','M93R','Ithaca M37','Jail Breaker','M3','Hydra',
      'VZ61','AK-74','H&K MP5','SIG 556','S75','Dragunov SVD','H&K PSG-1',
      'S&W M29','L. Hawk','S&W M500','Rocket Launcher')
FILES=('History of Resident Evil','BSAA','Majini','Chris Redfield','Sheva Alomar',
       'Ricardo Irving','Ndipaya Tribe','U-8','Tricell','Jill Valentine','Excella Gionne','Albert Wesker')
FIGURES=('Chris (BSAA)','Sheva (BSAA)','Josh','Jill (Brainwashed)','Wesker','Excella','Irving',
 'Spencer','DeChant','Dave','Kirk','Reynard','Majini (Town A)','Majini (Town B)','Majini (Town C)',
 'Majini (Town D)','Majini (Cephalo)','Majini (Agitator)','Majini (Wetlands A)',
 'Majini (Wetlands B)','Majini (Wetlands C)','Giant Majini','Majini (Base A)','Majini (Base B)',
 'Majini (Duvalia)','Reaper','Big Man Majini','Executioner Majini','Chainsaw Majini',
 'Gatling Gun Majini','Motorcycle Majini','Uroboros','Licker β','Kipepeo','Bui Kichwa','Adjule',
 'Crocodile','Uroboros Aheri','U-8','Popokarimu','Ndesu','Irving (Transformed)',
 'Chris (Rare)','Sheva (Rare)','Jill (Rare)')


def decode(raw):
    if len(raw)!=FILE_SIZE:raise ValueError('Unsupported Resident Evil 5 Steamworks profile size.')
    result=bytearray(FILE_SIZE)
    previous=CHAIN_SEED
    for offset in range(0,FILE_SIZE,8):
        block=raw[offset:offset+8]
        result[offset:offset+8]=bytes(a^b for a,b in zip(block,previous))
        previous=block
    return result


def encode(plain):
    if len(plain)!=FILE_SIZE:raise ValueError('Invalid Resident Evil 5 profile length.')
    result=bytearray(FILE_SIZE)
    previous=CHAIN_SEED
    for offset in range(0,FILE_SIZE,8):
        previous=bytes(a^b for a,b in zip(plain[offset:offset+8],previous))
        result[offset:offset+8]=previous
    return result


def checksum(plain):
    return (sum(struct.unpack_from('<I',plain,offset)[0] for offset in range(0x10,0x3BAC,4))+
            sum(struct.unpack_from('<I',plain,offset)[0] for offset in range(0x3BB0,0x52B0,4)))&0xffffffff


def looks_like_re5(raw):
    if len(raw)!=FILE_SIZE:return False
    plain=decode(raw)
    account=struct.unpack_from('<Q',plain)[0]
    year,month,day,hour,minute,second=struct.unpack_from('<6I',plain,0x10)
    return account>>32==0x01100001 and 2000<=year<=2100 and 1<=month<=12 and 1<=day<=31 and hour<24 and minute<60 and second<60


class Re5Save:
    def __init__(self,raw,field_type):
        if not looks_like_re5(raw):raise ValueError('This is not a supported Resident Evil 5 Steamworks profile.')
        self.plain=decode(raw);self.fields=[];self.operations={};self.warnings=[]
        if struct.unpack_from('<I',self.plain,8)[0]!=checksum(self.plain):
            self.warnings=['The RE5 profile integrity check does not match. Applying requires explicit integrity repair.']
        for key,label,offset,limit in (('money','Money',0x194,99999999),('points','Exchange points',0x198,9999999)):
            value=struct.unpack_from('<I',self.plain,offset)[0]
            if value>limit:raise ValueError('Unsupported '+label.lower()+' value in the RE5 profile.')
            self.fields.append(field_type(key,label,value,offset,'',0,limit,'Currency'))
            self.operations[key]=(offset,None,'<I')
        def flags(prefix,labels,offset,group,fmt='<I'):
            original=struct.unpack_from(fmt,self.plain,offset)[0]
            for bit,label in enumerate(labels):
                key=prefix+':'+str(bit)
                self.fields.append(field_type(key,label,(original>>bit)&1,offset,'',0,1,group,boolean=True))
                self.operations[key]=(offset,bit,fmt)
        flags('chris_costume',('BSAA','Safari','S.T.A.R.S.','Warrior'),0x124,'Chris costumes')
        flags('sheva_costume',('BSAA','Clubbin’','Tribal','Business'),0x128,'Sheva costumes')
        flags('filter',('Default','Classic Horror','Retro','Noise'),0x12C,'Screen filters')
        flags('infinite_ammo',GUNS,0x130,'Infinite ammo')
        flags('file',FILES,0x134,'Library files')
        flags('figure',FIGURES,0x138,'Figures','<Q')

    def patch(self,changes):
        result=bytearray(self.plain)
        for key,value in changes.items():
            if key not in self.operations:raise ValueError('Unauthorized RE5 field.')
            offset,bit,fmt=self.operations[key]
            if bit is None:struct.pack_into(fmt,result,offset,value)
            else:
                original=struct.unpack_from(fmt,result,offset)[0]
                struct.pack_into(fmt,result,offset,(original&~(1<<bit))|(value<<bit))
        struct.pack_into('<I',result,8,checksum(result))
        return encode(result)

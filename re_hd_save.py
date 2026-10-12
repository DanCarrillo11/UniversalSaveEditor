"""RE HD Remaster PC, first mapped save slot. GPL-3.0-or-later.

Independent implementation. PC inventory addresses: SAVE-EDITOR.com;
Blowfish/SHA1 format: bucanero/save-decrypters, cross-checked on a PC fixture.
Supporting field-address comparison: urbanware-org/re-hd-se (PS3).
"""
import hashlib
import struct
from cryptography.hazmat.primitives.ciphers import Cipher,modes
from cryptography.hazmat.decrepit.ciphers.algorithms import Blowfish

FILE_SIZE=457376
KEY=b'SBmdYgEamc=#sA0)Mhs9#>/4iiXbMPxW'
ITEMS={0x01:'Jill knife',0x02:'Chris knife',0x03:'Handgun',0x05:'Samurai Edge',
       0x06:'Shotgun',0x07:'Grenade launcher',0x08:'Acid grenade launcher',
       0x09:'Incendiary grenade launcher',0x0a:'Rocket launcher',0x0b:'Magnum',
       0x0c:'Flamethrower',0x0d:'Assault shotgun',0x0e:'Infinite rocket launcher',
       0x10:'Grenade shells',0x11:'Handgun ammunition',0x12:'Shotgun shells',
       0x13:'Acid shells',0x14:'Incendiary shells',0x19:'Magnum ammunition',
       0x21:'First aid spray',0x22:'Green herb',0x23:'Red herb',0x24:'Blue herb',
       0x37:'Master key',0x44:'Ink ribbons'}


def swap_words(raw):return b''.join(raw[i:i+4][::-1] for i in range(0,len(raw),4))


def crypt(raw,encrypt=False):
    if len(raw)!=FILE_SIZE:raise ValueError('Unsupported Resident Evil HD Remaster PC save size.')
    cipher=Cipher(Blowfish(KEY),modes.ECB())
    operation=cipher.encryptor() if encrypt else cipher.decryptor()
    return swap_words(operation.update(swap_words(raw))+operation.finalize())


def looks_like_hd(raw):
    if len(raw)!=FILE_SIZE:return False
    plain=crypt(raw)
    return struct.unpack_from('<3I',plain)==(1,0,36) and struct.unpack_from('<I',plain,32)[0]==FILE_SIZE-64


class ReHdSave:
    def __init__(self,raw,field_type):
        if not looks_like_hd(raw):raise ValueError('Unsupported Resident Evil HD Remaster PC container.')
        self.plain=crypt(raw);self.fields=[];self.operations={};self.warnings=[]
        if self.plain[12:32]!=swap_words(hashlib.sha1(self.plain[64:]).digest()):
            self.warnings=['The HD Remaster integrity check does not match. Applying requires explicit integrity repair.']
        def number(key,label,offset,group,maximum,choices=()):
            value=struct.unpack_from('<I',self.plain,offset)[0]
            if value>maximum:raise ValueError('Unsupported '+label.lower()+' value in the mapped save slot.')
            self.fields.append(field_type(key,label,value,offset,'',0,maximum,group,choices=choices))
            self.operations[key]=offset
        number('difficulty','Difficulty',0xe05c,'Difficulty',3,('Easy','Normal','Hard','Very Easy'))
        number('save_count','Save count',0xdfb0,'Statistics',9999)
        number('daggers','Daggers',0x1b454,'Defensive supplies',255)
        number('grenades','Flash grenades',0x1b458,'Defensive supplies',255)
        for group,base,count in (('Inventory',0x163ec,8),('Item box',0x1643c,256)):
            for index in range(count):
                offset=base+index*8;identifier,quantity=struct.unpack_from('<2I',self.plain,offset)
                if identifier==0:continue
                if identifier>0xff or quantity>255:raise ValueError('Unsupported item entry in the mapped HD Remaster save slot.')
                key=group.lower().replace(' ','_')+':'+str(index)
                known=identifier in ITEMS
                label=f'Slot {index+1} · {ITEMS.get(identifier,"Unidentified item · ID "+str(identifier))}'
                category='Weapons' if identifier in (1,2,3,5,6,7,8,9,10,11,12,13,14) else 'Ammunition' if identifier in (16,17,18,19,20,25) else 'Consumables' if identifier in (33,34,35,36,68) else 'Other items' if known else 'Unidentified items'
                self.fields.append(field_type(key,label,quantity,offset+4,'',0,255,group,
                                              note=f'Item ID {identifier}. Quantity or loaded ammunition of an existing item. Item identity is preserved.',collection=category))
                self.operations[key]=offset+4

    def patch(self,changes):
        result=bytearray(self.plain)
        for key,value in changes.items():
            if key not in self.operations:raise ValueError('Unauthorized HD Remaster field.')
            struct.pack_into('<I',result,self.operations[key],value)
        result[12:32]=swap_words(hashlib.sha1(result[64:]).digest())
        return crypt(result,True)

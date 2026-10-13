"""RE HD Remaster PC gameplay section directory. GPL-3.0-or-later.

Independent implementation. PC inventory addresses: SAVE-EDITOR.com;
Blowfish/SHA1 format: bucanero/save-decrypters, cross-checked on a PC fixture.
Supporting field-address comparison: urbanware-org/re-hd-se (PS3).
"""
import hashlib
import struct
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher,modes
from cryptography.hazmat.decrepit.ciphers.algorithms import Blowfish
from re_hd_items import ITEMS as DOCUMENTED_ITEMS

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
ITEMS={**DOCUMENTED_ITEMS,**ITEMS}
# The documented one-object entries are never duplicated as arbitrary stacks.
# Weapon rounds, ammo, canteen fuel, old keys and ribbons keep their separate
# existing quantity representation until all game-specific caps are established.
NONSTACKABLE=set(ITEMS)-set((*range(3,21),0x19,0x1b,0x2c,0x44))


def swap_words(raw):return b''.join(raw[i:i+4][::-1] for i in range(0,len(raw),4))


def crypt(raw,encrypt=False):
    if not 64<=len(raw)<=2*1024*1024 or len(raw)%8:raise ValueError('Unsupported Resident Evil HD Remaster PC save size.')
    cipher=Cipher(Blowfish(KEY),modes.ECB())
    operation=cipher.encryptor() if encrypt else cipher.decryptor()
    return swap_words(operation.update(swap_words(raw))+operation.finalize())


def looks_like_hd(raw):
    try:plain=crypt(raw)
    except ValueError:return False
    version,flags,table_size=struct.unpack_from('<3I',plain)
    return (version,flags)==(1,0) and 4<=table_size<=84 and table_size%4==0 and struct.unpack_from('<I',plain,32)[0]==len(raw)-64


class ReHdSave:
    def __init__(self,raw,field_type):
        if not looks_like_hd(raw):raise ValueError('Unsupported Resident Evil HD Remaster PC container.')
        self.plain=crypt(raw);self.fields=[];self.operations={};self.warnings=[]
        if self.plain[12:32]!=swap_words(hashlib.sha1(self.plain[64:]).digest()):
            self.warnings=['The HD Remaster integrity check does not match. Applying requires explicit integrity repair.']
        self.slot_records=[]
        table_size=struct.unpack_from('<I',self.plain,8)[0]
        offsets=struct.unpack_from('<'+str(table_size//4)+'I',self.plain,64)
        if tuple(sorted(set(offsets)))!=offsets or offsets[0]<64+table_size:
            raise ValueError('Invalid HD Remaster section directory.')
        hashes={~zlib.crc32(('GAMEDATA'+str(i)).encode())&0xffffffff:i for i in range(20)}
        seen=set()
        for index,offset in enumerate(offsets):
            end=offsets[index+1] if index+1<len(offsets) else len(self.plain)
            if offset+16>end:raise ValueError('Truncated HD Remaster section header.')
            identifier,version,size,reserved=struct.unpack_from('<4I',self.plain,offset)
            if offset+16+size>end:raise ValueError('HD Remaster section exceeds its allocation.')
            if identifier not in hashes:continue
            slot=hashes[identifier]
            if slot in seen or version!=12 or size!=0xdf20 or reserved!=0:
                raise ValueError('Unsupported HD Remaster gameplay section.')
            seen.add(slot);self.slot_records.append((slot,self.slot_fields(offset,slot,field_type)))
        self.slot_records.sort(key=lambda row:row[0])
        if not self.slot_records:raise ValueError('No supported HD Remaster gameplay records were found.')
        self.fields=self.slot_records[0][1]

    def slot_fields(self,record,slot,field_type):
        fields=[]
        def keyname(key):return key if slot==0 else f'slot:{slot}:{key}'
        def number(key,label,delta,group,maximum,choices=()):
            offset=record+delta;key=keyname(key)
            value=struct.unpack_from('<I',self.plain,offset)[0]
            if value>maximum:raise ValueError('Unsupported '+label.lower()+' value in the mapped save slot.')
            fields.append(field_type(key,label,value,offset,'',0,maximum,group,choices=choices))
            self.operations[key]=(offset,None)
        number('difficulty','Difficulty',0xc8,'Difficulty',3,('Easy','Normal','Hard','Very Easy'))
        number('save_count','Save count',0x1c,'Statistics',9999)
        number('daggers','Daggers',0xd4c0,'Defensive supplies',255)
        number('grenades','Flash grenades',0xd4c4,'Defensive supplies',255)
        for group,base,count in (('Inventory',record+0x8458,8),('Item box',record+0x84a8,256)):
            empty_added=False
            for index in range(count):
                offset=base+index*8;identifier,quantity=struct.unpack_from('<2I',self.plain,offset)
                if identifier==0:
                    if group!='Item box' or quantity or empty_added:continue
                    empty_added=True
                if identifier>0xff or quantity>255:raise ValueError('Unsupported item entry in the mapped HD Remaster save slot.')
                key=keyname(group.lower().replace(' ','_')+':'+str(index))
                known=identifier in ITEMS
                label=f'Slot {index+1} · {ITEMS.get(identifier,"Unidentified item · ID "+str(identifier))}'
                category='Weapons' if identifier in (*range(1,16),0x42) else 'Ammunition' if identifier in (16,17,18,19,20,25) else 'Consumables' if identifier in (*range(33,43),68) else 'Other items' if known else 'Unidentified items'
                fields.append(field_type(key,label,quantity,offset+4,'',0,255,group,
                    readonly=identifier in NONSTACKABLE and quantity>1,
                    note=f'Item ID {identifier}. '+('Single-object quantity is limited to 1. ' if identifier in NONSTACKABLE else 'Quantity or loaded ammunition of an existing entry. ')+
                         'Item identity is preserved; unknown game-specific stack/weapon caps remain unverified.',collection=category,item_id=identifier))
                self.operations[key]=(offset+4,None)
                if known or identifier==0:
                    options={0:'Empty',**ITEMS};values=tuple(options)
                    item_key=key+':identity'
                    fields.append(field_type(item_key,f'Slot {index+1} · Item',values.index(identifier),offset,'',0,len(values)-1,group,
                        choices=tuple(options[i] for i in values),collection=category,
                        note='Replaces this known item or fills the next empty item-box entry. Examinable/composite item state, equipment, story dependencies, capacity and other records are preserved. A new item gets quantity 1 unless a positive quantity is chosen.'))
                    self.operations[item_key]=(offset,values)
        return fields

    def patch(self,changes):
        result=bytearray(self.plain)
        for key,value in changes.items():
            offset,values=self.operations[key]
            if values is not None:continue
            if 'inventory:' not in key and 'item_box:' not in key:continue
            selected=changes.get(key+':identity')
            identifier=(self.operations[key+':identity'][1][selected] if selected is not None else struct.unpack_from('<I',result,offset-4)[0])
            if identifier in NONSTACKABLE and value>1:
                raise ValueError('A single-object item cannot have a quantity above 1. Choose one copy or a stackable item.')
        for key,value in changes.items():
            if key not in self.operations:raise ValueError('Unauthorized HD Remaster field.')
            offset,values=self.operations[key]
            if values is None:
                if ':identity' not in key and 'item_box:' in key:
                    current=struct.unpack_from('<I',result,offset-4)[0]
                    chosen=changes.get(key+':identity')
                    if not current and value and chosen in (None,0):raise ValueError('Choose an item before setting a new item-box quantity.')
                struct.pack_into('<I',result,offset,value)
        for key,value in changes.items():
            offset,values=self.operations[key]
            if values is not None:
                identifier=values[value];struct.pack_into('<I',result,offset,identifier)
                quantity_key=key.removesuffix(':identity')
                quantity=changes.get(quantity_key,struct.unpack_from('<I',result,offset+4)[0])
                if not identifier and changes.get(quantity_key,0):raise ValueError('An empty item cannot have a positive quantity.')
                if identifier in NONSTACKABLE:quantity=min(1,quantity)
                struct.pack_into('<I',result,offset+4,0 if not identifier else max(1,quantity))
        result[12:32]=swap_words(hashlib.sha1(result[64:]).digest())
        return crypt(result,True)

"""Synthetic PSO graphs and rejection cases, with no distributed game saves."""
from collections import Counter
import struct,unittest
from core import Save
from rockstar_container import aes,checksum,name_hash
from rdr2_features import parser_hash
from test_rockstar import fixture as minimal,section


def fixture(encrypted=True,backup=False,duplicate=False,bad_pointer=False,bad_schema=False,honor_disagrees=False,wide_pointer=False):
    blocks=[];schemas={}
    def block(name,size,fields,data):
        h=parser_hash(name) if isinstance(name,str) else name
        schemas[h]=(size,[(parser_hash(k) if isinstance(k,str) else k,t,sub,off,parser_hash(ref) if isinstance(ref,str) else ref) for k,t,sub,off,ref in fields])
        blocks.append((h,bytes(data)));return len(blocks)
    def pointer(block,offset=0):return struct.pack('>I',block|((offset&4095)<<20))+struct.pack('<I',offset>>12)
    base='CPedInventorySaveStructure__CInventorySaveInfoBase'
    schemas[parser_hash(base)]=(48,[(0x100,12,3,0,0),(parser_hash('items'),13,0,8,0)])
    root=bytearray(112);root[108]=int(backup)
    prefix=4096 if wide_pointer else 0
    root[16:32]=pointer(2,prefix)+struct.pack('>HHI',4,4,0)
    root[64:80]=pointer(2,prefix+32)+struct.pack('>HHI',1,1,0)
    block('CPedInventorySaveStructure',112,[('playerInventory',12,0,8,base),('backupInventory',12,0,56,base),('usingBackupInventory',0,0,108,0)],root)
    refs=pointer(3)+pointer(4)+pointer(5)+pointer(6)+pointer(3,48)
    if duplicate:refs=pointer(3)*2+refs[16:]
    if bad_pointer:refs=pointer(4095)+refs[8:]
    blocks.append((12,bytes(prefix)+refs))
    common=[('Guid',31,0,8,0),('ParentGuid',31,0,16,0),('ItemId',11,7,24,0),('SlotId',6,0,28,0),('Quantity',31,0,40,0)]
    def record(size,guid,name,quantity):
        data=bytearray(size);struct.pack_into('>Q',data,8,guid);struct.pack_into('>I',data,24,name_hash(name));struct.pack_into('>q',data,40,quantity);return data
    data=record(48,1,'CONSUMABLE_MEDICINE',3)+record(48,9,'CONSUMABLE_MEDICINE',7)
    block('SavegameInventoryItem',48,common,data)
    gun=record(88,2,'WEAPON_REVOLVER_CATTLEMAN',1)
    for off in (56,60,64,68,72):struct.pack_into('>f',gun,off,0.25)
    block('CPedInventorySaveStructure__WeaponItem',88,common+[(k,7,0,o,0) for k,o in zip(('Degradation','PermanentDegradation','Soot','Rust','Dirt'),(56,60,64,68,72))],gun)
    horse=record(232,3,'A_C_HORSE_ARABIAN_WHITE',1);struct.pack_into('>3i',horse,116,400,20,30)
    block('CPedInventorySaveStructure__HorseItem',232,common+[(k,5,0,o,0) for k,o in (('BondingXp',116),('Dirty',120),('Hungry',124))],horse)
    ammo=record(48,4,'AMMO_REVOLVER',50);block('SavegameInventoryItem',48,common,ammo)
    block('CBaseStatsSaveStructure__CIntStatStruct',12,[('statId',12,0,0,'StatId'),('Data',5,0,8,0)],struct.pack('>2Ii',0x89587b4e,0,11 if honor_disagrees else 10))
    attrs=bytearray(88760+568);attrs[88760]=3;attrs[88760+88]=23
    struct.pack_into('>i',attrs,88760+280,10)
    for n in range(3):struct.pack_into('>f',attrs,88760+8+n*8,50);struct.pack_into('>f',attrs,88760+96+n*8,100)
    schemas[0x41d6f933]=(568,[(0xa53cde40,5,0,280,0),(0xc3364edc,12,0,0,0x41d6f934),(0x18d8e817,12,0,88,0x41d6f938)])
    schemas[0x41d6f934]=(32,[(10+n,12,0,8+n*8,0x41d6f935) for n in range(3)])
    schemas[0x41d6f935]=(8,[(1,7,0,0,0)])
    schemas[0x41d6f938]=(192,[(20+n,7,0,8+n*8,0) for n in range(23)])
    block(0x41d6f894,len(attrs),[(0xb5d75947,12,64,23224,0x41d6f933)],attrs)
    block('CSaveCompendium__ItemWeapon',8,[('name',11,7,0,0),('hasOwned',0,0,4,0)],struct.pack('>IB3x',name_hash('WEAPON_REVOLVER_CATTLEMAN'),0))
    clock=bytearray(64);struct.pack_into('>3I',clock,44,9,25,30)
    block('CSimpleVariablesSaveStructure',64,[('GameClockHour',6,0,44,0),('GameClockMinute',6,0,48,0),('GameClockSecond',6,0,52,0)],clock)
    health=bytearray(64);struct.pack_into('>f',health,48,250)
    block('CPlayerPedSaveStructure',64,[('fHealth',7,0,48,0)],health)
    cash=record(48,8,'CURRENCY_CASH',12345);cash[24:28]=bytes.fromhex('ce548cf5');block('SavegameInventoryItem',48,common,cash)
    if bad_schema:
        h=parser_hash('CPedInventorySaveStructure__WeaponItem');size,fields=schemas[h]
        schemas[h]=(size,[(k,6 if k==parser_hash('Dirt') else t,sub,o,ref) for k,t,sub,o,ref in fields])
    data=b'';mapping=[]
    for h,raw in blocks:
        padding=bytes((-len(data))%16);data+=padding;mapping.append((h,len(data)+8,0,len(raw)));data+=raw
    index=b'';definitions=b'';offset=12+len(schemas)*8
    for h,(size,fields) in schemas.items():
        definition=struct.pack('>3I',len(fields),size,0)+b''.join(struct.pack('>IBBHI',*f) for f in fields)
        index+=struct.pack('>2I',h,offset+len(definitions));definitions+=definition
    frame=section(b'PSIN',data)+section(b'PMAP',struct.pack('>IIHHI',1,0,len(blocks),0,0)+b''.join(struct.pack('>4I',*m) for m in mapping))
    frame+=section(b'PSCH',struct.pack('>I',len(schemas))+index+definitions)+section(b'PSIG',b'')
    check=b'CHKS'+struct.pack('>4I',20,len(frame)+20,0,1)
    check=check[:12]+struct.pack('>I',checksum(frame+check[:8]+bytes(8)+check[16:]))+check[16:]
    header=minimal('rdr2',False)[:0x110];body=b'RSAV'+bytes(188)+frame+check;body+=bytes((-len(body))%16)
    return header+(aes(body,False) if encrypted else body)


class Rdr2FeatureTests(unittest.TestCase):
    def test_all_supported_sections_and_both_active_inventory_modes(self):
        s=Save(fixture(),'rdr2');groups=Counter(f.group for f in s.slots[0].fields)
        self.assertEqual(groups,{'Currency':1,'Honor':1,'Player cores':4,'Player progression':4,'Inventory':2,'Weapon condition':5,'Horses':3,'Compendium':1,'World clock':3})
        inv=[f for f in s.slots[0].fields if f.group=='Inventory'];self.assertEqual([f.value for f in inv],[3,50])
        archive=Save(fixture(backup=True),'rdr2');self.assertEqual([f.value for f in archive.slots[0].fields if f.group=='Inventory'],[7])

    def test_every_feature_roundtrips_exactly_and_only_declared_spans_change(self):
        for encrypted in (True,False):
            raw=fixture(encrypted);s=Save(raw,'rdr2');self.assertFalse(s.warnings);self.assertEqual(s.rockstar.patch({}),raw)
            changes={};allowed=set()
            for f in s.slots[0].fields:
                changes[0,f.key]=0.1234567 if f.decimal and f.maximum==1 else f.value+1
                fmt=s.rockstar.rdr2.formats.get(f.key,'>I')
                allowed.update(range(f.offset,f.offset+struct.calcsize(fmt)))
                for at in s.rockstar.rdr2.related.get(f.key,()):allowed.update(range(at,at+4))
            out=s.patched(changes);after=Save(out,'rdr2');self.assertFalse(after.warnings)
            for begin,at in s.rockstar.container.checks:allowed.update(range(at+12,at+16))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(s.rockstar.container.plain,after.rockstar.container.plain))))
            self.assertEqual(after.patched({(0,f.key):f.value for f in s.slots[0].fields}),raw)
            self.assertEqual(len(out),len(raw));self.assertEqual(out[:0x110],raw[:0x110])

    def test_bad_pointers_duplicate_guids_schema_mismatches_and_honor_disagreement_are_protected(self):
        for args in ({'bad_pointer':True},{'duplicate':True}):
            s=Save(fixture(**args),'rdr2');self.assertFalse(any(f.group in ('Inventory','Weapon condition','Horses') for f in s.slots[0].fields))
        s=Save(fixture(bad_schema=True),'rdr2');self.assertFalse(any(f.key.endswith(':dirt') and f.group=='Weapon condition' for f in s.slots[0].fields))
        s=Save(fixture(honor_disagrees=True),'rdr2');self.assertNotIn('honor',{f.key for f in s.slots[0].fields})
        with self.assertRaises(ValueError):s.patched({(0,'honor'):100})

    def test_inventory_cannot_be_deleted_and_attributes_reject_unsafe_ranges(self):
        s=Save(fixture(),'rdr2');fields=s.slots[0].fields
        for group,value in (('Inventory',0),('Weapon condition',1.01),('Player cores',101),('Honor',321),('Horses',-1),('World clock',99)):
            f=next(f for f in fields if f.group==group)
            with self.subTest(group=group),self.assertRaises(ValueError):s.patched({(0,f.key):value})

    def test_extended_pointer_word_preserves_active_and_backup_membership(self):
        for backup in (False,True):
            a=Save(fixture(backup=backup),'rdr2');b=Save(fixture(backup=backup,wide_pointer=True),'rdr2')
            self.assertEqual([(f.key,f.value) for f in a.slots[0].fields],[(f.key,f.value) for f in b.slots[0].fields])

    def test_navigation_assigns_every_field_once_and_labels_are_bundled(self):
        from editor_layout import organize_fields
        s=Save(fixture(),'rdr2');categories=organize_fields('rdr2',s.slots[0].fields)
        self.assertEqual([c.name for c in categories],['Progress','Character','Collection'])
        flat=[f for c in categories for section in c.sections for f in section.fields]
        self.assertEqual(Counter(f.key for f in flat),Counter(f.key for f in s.slots[0].fields))
        self.assertFalse(any('Unidentified' in f.collection for f in s.slots[0].fields))

import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from core import Save, FormatError, export_copy, replace_current, png_chunks

def variant(value):
    if isinstance(value,dict):
        return struct.pack('<II',18,len(value))+b''.join(variant(k)+variant(v) for k,v in value.items())
    if isinstance(value,list):
        return struct.pack('<II',19,len(value))+b''.join(map(variant,value))
    if isinstance(value,str):
        raw=value.encode()
        return struct.pack('<II',4,len(raw))+raw+bytes((-len(raw))%4)
    if isinstance(value,float):return struct.pack('<If',3,value)
    return struct.pack('<Ii',2,value)

def fishing():
    raw=variant({'inventory':[], 'money':150.0,'loan_left':20,'bait_inv':{'worms':3,'cricket':0},'bait_unlocked':['','worms'],'max_bait':10,'level':1,'unrelated':{'keep':'unchanged'}})
    return struct.pack('<I',len(raw))+raw

def ror2():
    return (b'<?xml version="1.0" encoding="utf-8"?><UserProfile><coins>7</coins>'
        b'<stats><stat name="totalGamesPlayed">2</stat><stat name="totalKills">15</stat>'
        b'<stat name="totalDamageDealt">123.5</stat><stat name="unknownValue">44</stat>'
        b'<unlock>Characters.Huntress</unlock></stats><name>Test</name></UserProfile>')

def chunk(name,data):
    return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data))

def kingdom():
    # Synthetic archive: exact table/record layout, two populated slots.
    pre=chunk(b'IHDR',bytes(13))+chunk(b'tEXt',bytes(43))
    payload=bytearray(16+200*(0x158+0x16c40)+304)
    base=16+200*0x158
    for i in range(2):
        desc=16+i*0x158
        payload[desc:desc+16]=b'BISLPS-25198-01\0'
        struct.pack_into('<I',payload,desc+0x50,0x16c00)
        pos=base+i*0x16c40
        struct.pack_into('<I',payload,pos,5)
        payload[pos+4]=10+i
        struct.pack_into('<I',payload,pos+0x1641c,500+i)
    return b'\x89PNG\r\n\x1a\n'+pre+chunk(b'sqEX',payload)+chunk(b'IEND',b'')

class CoreTests(unittest.TestCase):
    def test_fishing_no_changes_is_byte_identical(self):
        raw=fishing()
        self.assertEqual(Save(raw,'webfishing').patched({}),raw)

    def test_fishing_preserves_unknown_fields_and_numeric_type(self):
        raw=fishing(); save=Save(raw,'webfishing')
        field=next(f for f in save.slots[0].fields if f.key=='money')
        output=save.patched({(0,'money'):999})
        self.assertEqual(struct.unpack_from('<f',output,field.offset)[0],999)
        self.assertEqual(output[:field.offset],raw[:field.offset])
        self.assertEqual(output[field.offset+4:],raw[field.offset+4:])

    def test_bait_capacity_and_negative_money(self):
        save=Save(fishing(),'webfishing')
        for changes in ({(0,'bait:worms'):11},{(0,'money'):-1},{(0,'money'):1.5},{(0,'fake'):3},{(9,'money'):3}):
            with self.assertRaises(ValueError):save.patched(changes)

    def test_bait_quantity_unlocks_unpurchased_bait(self):
        raw=fishing(); save=Save(raw,'webfishing')
        output=save.patched({(0,'bait:cricket'):5})
        parsed=Save(output,'webfishing')
        self.assertEqual(parsed.info['bait_inv']['cricket'],5)
        self.assertIn('cricket',parsed.info['bait_unlocked'])
        self.assertEqual(struct.unpack_from('<I',output)[0],len(output)-4)

    def test_truncated_or_wrong_input(self):
        for raw in (b'',b'garbage',fishing()[:-1],struct.pack('<II',4,17)):
            with self.assertRaises(ValueError):Save(raw,'webfishing')

    def test_ror2_edits_xml_fields_and_preserves_unknown_content(self):
        raw=ror2();save=Save(raw,'ror2')
        self.assertEqual(save.patched({}),raw)
        output=save.patched({(0,'coins'):999,(0,'stat:totalKills'):321,
            (0,'stat:totalDamageDealt'):456.25})
        parsed=Save(output,'ror2')
        values={field.key:field.value for field in parsed.slots[0].fields}
        self.assertEqual(values['coins'],999)
        self.assertEqual(values['stat:totalKills'],321)
        self.assertEqual(values['stat:totalDamageDealt'],456.25)
        self.assertIn(b'<stat name="unknownValue">44</stat>',output)
        self.assertIn(b'<name>Test</name>',output)
        with self.assertRaises(ValueError):save.patched({(0,'coins'):-1})

    def test_ror2_rejects_malformed_or_unrelated_xml(self):
        for raw in (b'<broken',b'<Other><coins>1</coins></Other>'):
            with self.assertRaises(ValueError):Save(raw,'ror2')

    def test_kh_slots_and_crc(self):
        raw=kingdom(); save=Save(raw,'kh1')
        self.assertEqual(len(save.slots),2)
        self.assertEqual(save.patched({}),raw)
        output=save.patched({(1,'munny'):3210})
        after=Save(output,'kh1')
        self.assertEqual(after.slots[0].fields[0].value,500)
        self.assertEqual(after.slots[1].fields[0].value,3210)
        allowed=set(range(save.slots[1].fields[0].offset,save.slots[1].fields[0].offset+4))
        allowed.update(range(save.crc_regions[0][1],save.crc_regions[0][1]+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        png_chunks(output)

    def test_crc_repair_is_explicit(self):
        raw=bytearray(kingdom());save=Save(raw,'kh1')
        raw[save.crc_regions[0][1]]^=1
        save=Save(bytes(raw),'kh1')
        self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,'munny'):999})
        output=save.patched({(0,'munny'):999},repair_crc=True)
        self.assertFalse(Save(output,'kh1').warnings)

    def test_bad_png_rejected(self):
        raw=bytearray(kingdom());raw[20]^=1
        with self.assertRaises(FormatError):Save(bytes(raw),'kh1')

    def test_export_preserves_original_and_backup(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'original.sav';target=Path(root)/'edited.sav'
            original=fishing();source.write_bytes(original)
            edited=Save(original,'webfishing').patched({(0,'money'):999})
            backup=export_copy(source,original,edited,target)
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(backup.read_bytes(),original)
            self.assertEqual(target.read_bytes(),edited)
            with self.assertRaises(ValueError):export_copy(source,original,edited,source)
            with self.assertRaises(ValueError):export_copy(source,original,edited,target)
            source.write_bytes(b'changed')
            with self.assertRaises(ValueError):export_copy(source,original,edited,Path(root)/'other.sav')

    def test_replace_current_creates_backup_and_replaces_active_save(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'webfishing_save_slot_0.sav'
            original=fishing();source.write_bytes(original)
            edited=Save(original,'webfishing').patched({(0,'money'):777})
            backup=replace_current(source,original,edited)
            self.assertEqual(source.read_bytes(),edited)
            self.assertEqual(backup.read_bytes(),original)
            self.assertFalse(list(Path(root).glob('*.tmp')))
            with self.assertRaises(ValueError):replace_current(source,original,edited)

if __name__=='__main__':unittest.main()

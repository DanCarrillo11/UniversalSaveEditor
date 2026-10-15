import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest.mock import patch
from core import Save, FormatError, export_copy, replace_current, png_chunks, identify_game, backup_files, restore_backup

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
        payload[pos+0x492:pos+0x499]=bytes([1])*7
        payload[pos+0x7d0:pos+0x7d6]=bytes([255])*6
        struct.pack_into('<I',payload,pos+0x1641c,500+i)
    return b'\x89PNG\r\n\x1a\n'+pre+chunk(b'sqEX',payload)+chunk(b'IEND',b'')

def kingdom2():
    pre=chunk(b'IHDR',bytes(13))+chunk(b'tEXt',bytes(43))
    count,stride=100,0x10fc0
    payload=bytearray(16+count*0x158+count*stride+0x290)
    table=memoryview(payload)[16:16+count*0x158]
    table[0:16]=b'BISLPM-66675-00\0'
    struct.pack_into('<I',table,0x50,stride)
    key=bytes(range(16,32))
    for index in range(0xf0):table[index]^=key[index%16]
    record=16+count*0x158
    payload[record:record+4]=b'KH2E'
    struct.pack_into('<I',payload,record+0x2440,500)
    payload[record+0x24ff]=12
    payload[record+0x24f4:record+0x24f8]=bytes((20,30,10,20))
    struct.pack_into('<I',payload,record+0x36e0,1234)
    payload[record+0x32f6]=2
    struct.pack_into('<I',payload,record+0x32f8,55)
    struct.pack_into('<I',payload,record+8,Save._kh2_checksum(payload[record:record+stride]))
    return b'\x89PNG\r\n\x1a\n'+pre+chunk(b'sqEX',payload)+chunk(b'IEND',b'')

def alice():
    from alice_profile import fstring
    def ints(values):return struct.pack('<'+str(len(values))+'i',*values)
    def strings(values):return ints([len(values)])+b''.join(fstring(v) for v in values)
    raw=ints([49,0xf223,1])+fstring('Chapter1_W1_VoT_01_S')+ints([2])
    raw+=fstring('MemoryFragment_Family_0')+ints([0,1,0,0,0,-1])
    raw+=fstring('UnrelatedActor_0')+ints([17,23,42,12,64,-1])
    raw+=ints([1])+fstring('Chapter1_W1_P')
    raw+=ints([0]*25)+strings(['','unrelated'])+ints([0]*25)
    raw+=ints([473,64,1,0,0,0,0])+ints([0]*60)
    raw+=strings(['UnknownMovie'])+strings(['VorpalBlade','UnknownAbility'])
    raw+=strings([])+strings([])+strings(['UnknownSecret'])
    raw+=ints([18,16,725,72,0,0,0])+struct.pack('<2f',0.15,3600)
    raw+=bytes([0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0])+ints([0]*70)
    return raw

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

    def test_ror2_adds_and_removes_unlocks_without_duplicates(self):
        raw=ror2();save=Save(raw,'ror2')
        unlock_fields=[field for field in save.slots[0].fields if field.fmt=='xml-unlock']
        self.assertEqual(len(unlock_fields),454)
        self.assertEqual({field.group for field in unlock_fields},{
            'Characters','Skills','Skins and recolors','Artifacts',
            'Items and equipment','Logs','Newt Altars',
        })
        output=save.patched({
            (0,'unlock:Characters.Huntress'):0,
            (0,'unlock:Characters.Acolyte'):1,
            (0,'unlock:Skins.Acolyte.Alt1'):1,
            (0,'unlock:Skills.Acolyte.Backpack'):1,
        })
        parsed=Save(output,'ror2')
        self.assertNotIn('Characters.Huntress',parsed.ror2_unlocked)
        self.assertIn('Characters.Acolyte',parsed.ror2_unlocked)
        self.assertIn('Skins.Acolyte.Alt1',parsed.ror2_unlocked)
        self.assertIn('Skills.Acolyte.Backpack',parsed.ror2_unlocked)
        self.assertEqual(parsed.ror2_unlocked.count('Characters.Acolyte'),1)
        self.assertIn(b'<stat name="unknownValue">44</stat>',output)

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

    def test_kh1_difficulty_modes_preserve_other_slots_and_data(self):
        raw=kingdom();save=Save(raw,'kh1')
        field=next(f for f in save.slots[1].fields if f.key=='difficulty')
        self.assertEqual(field.choices,('Beginner','Final Mix (Standard)','Proud'))
        start,end=save.crc_regions[0]
        for mode in range(3):
            output=save.patched({(1,'difficulty'):mode})
            expected=bytearray(raw);expected[field.offset]=mode
            struct.pack_into('>I',expected,end,zlib.crc32(expected[start-4:end]))
            self.assertEqual(output,bytes(expected))
            parsed=Save(output,'kh1')
            self.assertEqual(next(f.value for f in parsed.slots[1].fields if f.key=='difficulty'),mode)
            self.assertEqual(next(f.value for f in parsed.slots[0].fields if f.key=='difficulty'),0)
            self.assertFalse(parsed.warnings)
        for value in (-1,3,1.5):
            with self.assertRaises(ValueError):save.patched({(1,'difficulty'):value})

    def test_kh2_difficulty_modes_repair_checksums_only_in_changed_slot(self):
        raw=bytearray(kingdom2());first=Save(raw,'kh2')
        start,end=first.crc_regions[0];archive=start+16;stride=0x10fc0
        record=archive+100*0x158
        raw[record+stride:record+2*stride]=raw[record:record+stride]
        struct.pack_into('<I',raw,archive+0x158+0x50,stride)
        struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
        raw=bytes(raw);save=Save(raw,'kh2')
        self.assertEqual(len(save.slots),2)
        field=next(f for f in save.slots[1].fields if f.key=='difficulty')
        self.assertEqual(field.choices,('Beginner','Standard','Proud','Critical'))
        for mode in range(4):
            output=save.patched({(1,'difficulty'):mode})
            expected=bytearray(raw);expected[field.offset]=mode
            second=record+stride
            struct.pack_into('<I',expected,second+8,Save._kh2_checksum(expected[second:second+stride]))
            struct.pack_into('>I',expected,end,zlib.crc32(expected[start-4:end]))
            self.assertEqual(output,bytes(expected))
            parsed=Save(output,'kh2')
            self.assertEqual(next(f.value for f in parsed.slots[1].fields if f.key=='difficulty'),mode)
            self.assertFalse(parsed.warnings)
        for value in (-1,4,1.5):
            with self.assertRaises(ValueError):save.patched({(1,'difficulty'):value})

    def test_unknown_kh_difficulty_is_rejected(self):
        for game,raw in (('kh1',kingdom()),('kh2',kingdom2())):
            save=Save(raw,game);field=next(f for f in save.slots[0].fields if f.key=='difficulty')
            invalid=bytearray(raw);invalid[field.offset]=255
            with self.subTest(game=game),self.assertRaises(FormatError):Save(invalid,game)

    def test_crc_repair_is_explicit(self):
        raw=bytearray(kingdom());save=Save(raw,'kh1')
        raw[save.crc_regions[0][1]]^=1
        save=Save(bytes(raw),'kh1')
        self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,'munny'):999})
        output=save.patched({(0,'munny'):999},repair_crc=True)
        self.assertFalse(Save(output,'kh1').warnings)

    def test_kh2_fields_checksums_and_crc(self):
        raw=kingdom2();save=Save(raw,'kh2')
        self.assertEqual(len(save.slots),1)
        values={field.key:field.value for field in save.slots[0].fields}
        self.assertEqual(values['munny'],500)
        self.assertEqual(values['experience'],1234)
        self.assertEqual(values['character:0:level'],12)
        output=save.patched({(0,'munny'):9999,(0,'experience'):4321,(0,'form:0:level'):7})
        parsed=Save(output,'kh2')
        after={field.key:field.value for field in parsed.slots[0].fields}
        self.assertEqual(after['munny'],9999)
        self.assertEqual(after['experience'],4321)
        self.assertEqual(after['form:0:level'],7)
        record=next(field.offset for field in parsed.slots[0].fields if field.key=='munny')-0x2440
        self.assertEqual(struct.unpack_from('<I',output,record+8)[0],Save._kh2_checksum(output[record:record+0x10fc0]))
        png_chunks(output)

    def test_alice_teeth_are_patched_without_touching_other_data(self):
        raw=alice();save=Save(raw,'alice')
        field=save.slots[0].fields[0]
        self.assertEqual(field.value,473)
        output=save.patched({(0,'teeth'):7250})
        self.assertEqual(Save(output,'alice').slots[0].fields[0].value,7250)
        allowed=set(range(field.offset,field.offset+4))
        self.assertTrue(all(a==b or index in allowed for index,(a,b) in enumerate(zip(raw,output))))

    def test_kh2_internal_checksum_repair_requires_opt_in(self):
        raw=bytearray(kingdom2());save=Save(raw,'kh2')
        record=save.slots[0].fields[0].offset-0x2440
        raw[record+8]^=1
        start,end=save.crc_regions[0]
        struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
        save=Save(bytes(raw),'kh2')
        self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,'munny'):900})
        output=save.patched({(0,'munny'):900},repair_crc=True)
        self.assertFalse(Save(output,'kh2').warnings)

    def test_kh2_no_changes_preserves_every_byte(self):
        raw=kingdom2()
        self.assertEqual(Save(raw,'kh2').patched({}),raw)

    def test_alice_unknown_layout_is_rejected(self):
        raw=bytearray(alice());struct.pack_into('<I',raw,0,50)
        with self.assertRaises(FormatError):Save(bytes(raw),'alice')

    def test_identification_supports_manual_and_renamed_saves(self):
        for name,game in [('KHIIFM_WW.png','kh2'),('PersistentData_PC.PSD','alice'),('KHReCoM_WW.png','recom')]:
            self.assertEqual(identify_game(name),game)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            target=Path(root)/'my-renamed-save.png';target.write_bytes(kingdom2())
            self.assertEqual(identify_game(target),'kh2')
        with self.assertRaises(FormatError):identify_game('notes.txt')

    def test_restore_uses_existing_backup_without_creating_another(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'webfishing_save_slot_0.sav';original=fishing();source.write_bytes(original)
            edited=Save(original,'webfishing').patched({(0,'money'):900})
            backup=Path(root)/'webfishing_save_slot_0.sav.original-abcd.bak'
            backup.write_bytes(original)
            replace_current(source,original,edited)
            (Path(root)/'another-game.original-abcd.bak').write_bytes(original)
            self.assertEqual(backup_files(source),[backup])
            restore_backup(source,backup,'webfishing')
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(backup.read_bytes(),original)
            self.assertEqual(backup_files(source),[backup])

    def test_invalid_backup_does_not_replace_current_file(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'current.sav';source.write_bytes(fishing())
            backup=Path(root)/'invalid.bak';backup.write_bytes(b'invalid save')
            with self.assertRaises(ValueError):restore_backup(source,backup,'webfishing')
            self.assertEqual(source.read_bytes(),fishing())
            self.assertEqual(list(Path(root).glob('*.original-*.bak')),[])

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

    def test_replace_current_updates_active_save_without_extra_files(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'webfishing_save_slot_0.sav'
            original=fishing();source.write_bytes(original)
            edited=Save(original,'webfishing').patched({(0,'money'):777})
            replace_current(source,original,edited)
            self.assertEqual(source.read_bytes(),edited)
            self.assertEqual(list(Path(root).iterdir()),[source])
            with self.assertRaises(ValueError):replace_current(source,original,edited)

    def test_failed_replacement_preserves_source_and_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'current.sav';original=fishing();source.write_bytes(original)
            edited=Save(original,'webfishing').patched({(0,'money'):777})
            with patch('core.os.replace',side_effect=PermissionError('File is locked')):
                with self.assertRaises(PermissionError):replace_current(source,original,edited)
            self.assertEqual(source.read_bytes(),original)
            self.assertEqual(list(Path(root).iterdir()),[source])

    def test_game_save_during_write_is_not_overwritten(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as root:
            source=Path(root)/'current.sav';original=fishing();source.write_bytes(original)
            save=Save(original,'webfishing')
            edited=save.patched({(0,'money'):777})
            game_output=save.patched({(0,'money'):250})
            with patch('core.os.fsync',side_effect=lambda fd:source.write_bytes(game_output)):
                with self.assertRaisesRegex(ValueError,'save changed'):replace_current(source,original,edited)
            self.assertEqual(source.read_bytes(),game_output)
            self.assertEqual(list(Path(root).iterdir()),[source])

if __name__=='__main__':unittest.main()

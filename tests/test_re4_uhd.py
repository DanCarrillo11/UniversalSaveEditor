"""Synthetic RE4 UHD fixtures; no player saves are included."""
import struct
import tempfile
import unittest
from pathlib import Path
from core import Save,FormatError,identify_game
from re4_uhd import FILE_SIZE,FIRST_SLOT,SLOT_SIZE,checksum
from editor_layout import organize_fields


def reference_crc(data):
    value=0
    for byte in data:
        value^=byte<<24
        for _ in range(8):value=((value<<1)^0x04C11DB7 if value&0x80000000 else value<<1)&0xffffffff
    return value


def fixture():
    raw=bytearray(FILE_SIZE)
    raw[0:32]=bytes(range(32));raw[-8:]=b'ACCOUNT!'
    for physical in (0,4):
        base=FIRST_SLOT+physical*SLOT_SIZE
        struct.pack_into('<I',raw,base+4,0x402)
        struct.pack_into('<i',raw,base+0x4c,12345)
        struct.pack_into('<4h',raw,base+0x58,600,1200,600,600)
        raw[base+0x3d]=5;raw[base+0x3520]=5
        raw[base+0x500:base+0x510]=b'KEEP ROOM FLAGS!'
        raw[base+0x4000:base+0x4010]=b'KEEP INVENTORY!!'
        struct.pack_into('<I',raw,base,reference_crc(raw[base+4:base+0x200]))
        struct.pack_into('<I',raw,base+SLOT_SIZE-4,reference_crc(raw[base:base+SLOT_SIZE-4]))
    return bytes(raw)


class Re4UhdTests(unittest.TestCase):
    def setUp(self):self.raw=fixture()

    def test_crc_matches_known_vector_and_independent_bitwise_oracle(self):
        self.assertEqual(checksum(b'123456789'),0x89A1897F)
        self.assertEqual(checksum(bytes(range(256))),reference_crc(bytes(range(256))))

    def test_populated_slots_preserve_physical_numbering_and_noop_bytes(self):
        save=Save(self.raw,'re4_2005')
        self.assertEqual([slot.name for slot in save.slots],['Slot 1','Slot 5'])
        self.assertFalse(save.warnings);self.assertEqual(save.patched({}),self.raw)
        self.assertEqual([c.name for c in organize_fields('re4_2005',save.slots[0].fields)],['Progress','Characters','Records'])

    def test_money_patch_only_changes_requested_slot_field_and_two_crcs(self):
        save=Save(self.raw,'re4_2005');output=save.patched({(1,'money'):45678})
        base=FIRST_SLOT+4*SLOT_SIZE
        allowed=set(range(base,base+4))|set(range(base+0x4c,base+0x50))|set(range(base+SLOT_SIZE-4,base+SLOT_SIZE))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(self.raw,output))))
        self.assertEqual(len(output),FILE_SIZE);self.assertEqual(output[:FIRST_SLOT],self.raw[:FIRST_SLOT]);self.assertEqual(output[-8:],b'ACCOUNT!')
        self.assertFalse(Save(output,'re4_2005').warnings)

    def test_difficulty_updates_both_mirrors_and_valid_crcs(self):
        output=Save(self.raw,'re4_2005').patched({(0,'difficulty'):3})
        self.assertEqual(output[FIRST_SLOT+0x3d],6);self.assertEqual(output[FIRST_SLOT+0x3520],6)
        self.assertFalse(Save(output,'re4_2005').warnings)

    def test_health_relation_is_checked_and_both_values_can_be_changed(self):
        save=Save(self.raw,'re4_2005')
        with self.assertRaisesRegex(ValueError,'exceed'):save.patched({(0,'player_hp'):1500})
        output=save.patched({(0,'player_hp'):1500,(0,'player_max_hp'):1500})
        self.assertEqual(struct.unpack_from('<2h',output,FIRST_SLOT+0x58),(1500,1500))

    def test_statistics_patching_preserves_room_and_inventory(self):
        output=Save(self.raw,'re4_2005').patched({(0,'total_kills'):999,(0,'save_count'):1})
        self.assertEqual(output[FIRST_SLOT+0x500:FIRST_SLOT+0x510],b'KEEP ROOM FLAGS!')
        self.assertEqual(output[FIRST_SLOT+0x4000:FIRST_SLOT+0x4010],b'KEEP INVENTORY!!')
        self.assertFalse(Save(output,'re4_2005').warnings)

    def test_corrupt_crc_requires_explicit_repair(self):
        raw=bytearray(self.raw);raw[FIRST_SLOT]^=1
        save=Save(raw,'re4_2005');self.assertEqual(len(save.warnings),2)
        with self.assertRaisesRegex(ValueError,'repair'):save.patched({(0,'money'):1})
        output=save.patched({},True)
        self.assertEqual(output,self.raw);self.assertFalse(Save(output,'re4_2005').warnings)

    def test_unknown_formats_empty_records_and_invalid_modes_are_rejected(self):
        for raw in (self.raw[:-1],self.raw+b'\0',bytes(FILE_SIZE)):
            with self.assertRaises(FormatError):Save(raw,'re4_2005')
        for offset,value in ((4,3),(0x3d,6),(0x3520,2)):
            raw=bytearray(self.raw);raw[FIRST_SLOT+offset]=value
            with self.assertRaises(FormatError):Save(raw,'re4_2005')

    def test_limits_and_unknown_fields_are_rejected(self):
        save=Save(self.raw,'re4_2005')
        for edits in ({(0,'money'):-1},{(0,'money'):100000000},{(0,'money'):1.5},{(0,'player_max_hp'):0},{(0,'ashley_max_hp'):1201},{(0,'difficulty'):4},{(0,'inventory:0'):1}):
            with self.assertRaises(ValueError):save.patched(edits)

    def test_original_name_is_recognized_before_generic_godot_sav(self):
        self.assertEqual(identify_game(Path('savegame00.sav')),'re4_2005')
        self.assertEqual(identify_game(Path('webfishing_save_slot_0.sav')),'webfishing')


if __name__=='__main__':unittest.main()

"""Spell/shortcut synchronization, known bit masks and related level state."""
import struct
import unittest
from core import Save
from test_kh2_relationships import fixture,option


class Kh2AcquisitionTests(unittest.TestCase):
    def test_six_native_spell_tiers_and_shortcuts_upgrade_and_clear_together(self):
        raw,record,_,end=fixture();raw=bytearray(raw)
        raw[record+0x3594]=1;raw[record+0x3595]=2
        struct.pack_into('<4H',raw,record+0x36f8,49,49,121,23)
        s=Save(raw,'kh2');out=s.patched({(0,'character:0:magic:fire'):3},repair_crc=True)
        self.assertEqual(struct.unpack_from('<4H',out,record+0x36f8),(120,120,121,23))
        allowed={record+0x3594}|set(range(record+0x36f8,record+0x36fc))|set(range(record+8,record+12))|set(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        cleared=Save(out,'kh2').patched({(0,'character:0:magic:fire'):0})
        self.assertEqual(struct.unpack_from('<4H',cleared,record+0x36f8),(0,0,121,23))
        self.assertFalse(Save(cleared,'kh2').warnings)
        values={f.key:f for f in s.slots[0].fields}
        self.assertEqual(values['character:0:magic:reflect'].offset,record+0x35d0)
        self.assertEqual(len([f for f in s.slots[0].fields if f.key.startswith('character:0:magic:')]),6)
        with self.assertRaises(ValueError):s.patched({(0,'character:0:magic:fire'):4},repair_crc=True)

    def test_explicit_shortcuts_require_learned_magic_and_use_the_new_tier(self):
        raw,record,*_=fixture();s=Save(raw,'kh2');key='character:0:magic_shortcut:0'
        with self.assertRaisesRegex(ValueError,'learned'):s.patched({(0,key):1})
        out=s.patched({(0,key):1,(0,'character:0:magic:fire'):2})
        self.assertEqual(struct.unpack_from('<H',out,record+0x36f8)[0],119)
        f=next(f for f in Save(out,'kh2').slots[0].fields if f.key==key)
        self.assertEqual(f.choices[f.value],'Fire')
        with self.assertRaisesRegex(ValueError,'learned'):Save(out,'kh2').patched({(0,key):1,(0,'character:0:magic:fire'):0})

    def test_item_shortcut_follows_equipped_supply_availability(self):
        raw,record,*_=fixture();raw=bytearray(raw);struct.pack_into('<H',raw,record+0x36f8,23)
        raw[record+0x3581]=1;s=Save(raw,'kh2');item='character:0:item:0';shortcut='character:0:magic_shortcut:0'
        out=s.patched({(0,item):option(s,item,2)},repair_crc=True)
        self.assertEqual(struct.unpack_from('<H',out,record+0x36f8)[0],0)
        with self.assertRaisesRegex(ValueError,'equipped in Sora'):s.patched({(0,item):option(s,item,2),(0,shortcut):7},repair_crc=True)
        out=s.patched({(0,item):option(s,item,2),(0,shortcut):8},repair_crc=True)
        self.assertEqual(struct.unpack_from('<H',out,record+0x36f8)[0],20)
        self.assertEqual(out[record+0x3580:record+0x3582],b'\x01\x00')

    def test_acquisition_masks_initialize_only_known_levels_and_reset_only_the_anti_byte(self):
        raw,record,*_=fixture();raw=bytearray(raw)
        raw[record+0x36c0]=0x80;raw[record+0x36c4]=0x0f;raw[record+0x36ca]=0x80
        raw[record+0x32f6]=0;raw[record+0x3526]=0
        struct.pack_into('<I',raw,record+0x3410,0xaabbcc22)
        s=Save(raw,'kh2');out=s.patched({(0,'form:valor'):1,(0,'form:limit'):1,(0,'summon:genie'):1,(0,'report:1'):1,(0,'report:13'):1},repair_crc=True)
        self.assertEqual(out[record+0x36c0],0x82);self.assertEqual(out[record+0x36ca],0x88)
        self.assertEqual(out[record+0x36c4],0x5f);self.assertEqual(out[record+0x36c6]&4,4)
        self.assertEqual(out[record+0x32f6],1);self.assertEqual(out[record+0x3526],1)
        self.assertEqual(struct.unpack_from('<I',out,record+0x3410)[0],0xaabbcc00)
        d={f.key:f for f in Save(out,'kh2').slots[0].fields}
        for key in ('form:valor','form:limit','summon:genie','report:1','report:13'):
            self.assertTrue(d[key].readonly);self.assertEqual(d[key].value,1)
        with self.assertRaises(ValueError):s.patched({(0,'form:valor'):1,(0,'form:0:level'):0},repair_crc=True)
        with self.assertRaises(ValueError):s.patched({(0,'form:valor'):1,(0,'drive_anti_points'):10},repair_crc=True)

    def test_drive_clamps_on_maximum_reduction_and_rejects_explicit_conflict(self):
        raw,record,*_=fixture();raw=bytearray(raw);raw[record+0x3529]=7;raw[record+0x352a]=9
        s=Save(raw,'kh2');out=s.patched({(0,'drive_max'):4},repair_crc=True)
        self.assertEqual(out[record+0x3529:record+0x352b],b'\x04\x04')
        with self.assertRaisesRegex(ValueError,'current Drive'):s.patched({(0,'drive_max'):4,(0,'drive_current'):5},repair_crc=True)

    def test_unknown_commands_and_spell_tiers_are_retained(self):
        raw,record,*_=fixture();raw=bytearray(raw);raw[record+0x3594]=255
        struct.pack_into('<H',raw,record+0x36f8,65534);s=Save(raw,'kh2')
        for key in ('character:0:magic:fire','character:0:magic_shortcut:0'):
            self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key==key))
            with self.assertRaises(ValueError):s.patched({(0,key):0},repair_crc=True)
        out=s.patched({(0,'munny'):1234},repair_crc=True)
        self.assertEqual(out[record+0x3594],255);self.assertEqual(out[record+0x36f8:record+0x36fa],raw[record+0x36f8:record+0x36fa])


if __name__=='__main__':unittest.main()

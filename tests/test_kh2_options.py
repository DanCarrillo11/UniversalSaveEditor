"""Documented option bits, reserved bits and untouched physical records."""
import struct
import unittest
import zlib
from core import Save,png_chunks
from test_kh2_system import mixed_archive


class Kh2OptionTests(unittest.TestCase):
    def test_option_changes_preserve_reserved_bits_system_and_other_state(self):
        raw,system,record,start,end=mixed_archive();raw=bytearray(raw)
        raw[record+0x41a4]=0x06;raw[record+0x41a5]=0x82
        struct.pack_into('<I',raw,record+8,Save._kh2_checksum(raw[record:record+0x10fc0]))
        struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
        s=Save(raw,'kh2');options=[f for f in s.slots[0].fields if f.group=='Game settings']
        self.assertEqual(len(options),7)
        out=s.patched({(0,'setting:vibration'):1,(0,'setting:classic_menu'):1,(0,'setting:invert_vertical'):1})
        self.assertEqual(out[record+0x41a4],0x47);self.assertEqual(out[record+0x41a5],0x83)
        self.assertEqual(out[system:system+0x400],raw[system:system+0x400])
        allowed={record+0x41a4,record+0x41a5}|set(range(record+8,record+12))|set(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        self.assertFalse(Save(out,'kh2').warnings);self.assertEqual(s.patched({}),raw)

    def test_each_setting_is_reversible_and_unknown_or_non_boolean_input_is_rejected(self):
        raw,*_=mixed_archive();s=Save(raw,'kh2')
        for field in s.slots[0].fields:
            if field.group!='Game settings':continue
            out=s.patched({(0,field.key):1-field.value});check=Save(out,'kh2')
            self.assertEqual(next(f.value for f in check.slots[0].fields if f.key==field.key),1-field.value)
            self.assertEqual(check.patched({(0,field.key):field.value}),raw)
        for edits in ({(0,'setting:vibration'):2},{(0,'setting:unknown'):1}):
            with self.assertRaises(ValueError):s.patched(edits)


if __name__=='__main__':unittest.main()

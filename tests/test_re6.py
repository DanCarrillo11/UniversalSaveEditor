import struct
import unittest
from core import Save,FormatError
from re6_save import FILE_SIZE,VERSION,checksum,looks_like_re6


def fixture():
    raw=bytearray(FILE_SIZE);raw[:4]=VERSION
    struct.pack_into('<I',raw,4,FILE_SIZE);raw[16:24]=b'KEEPUSER'
    struct.pack_into('<I',raw,1804,500)
    struct.pack_into('<I',raw,2440,0xc0000000);raw[2451]=0xc0
    struct.pack_into('<Hh',raw,34044,0xb201,4)
    raw[2016:2096]=bytes([3])*80
    raw[-16:]=b'KEEP PROFILE END'
    struct.pack_into('<I',raw,8,checksum(raw))
    return bytes(raw)


class Re6Tests(unittest.TestCase):
    def test_patch_preserves_identity_emblems_item_flags_reserved_bits_and_tail(self):
        raw=fixture();save=Save(raw,'re6')
        self.assertFalse(save.warnings);self.assertEqual(save.patched({}),raw)
        output=save.patched({(0,'skill_points'):1234,(0,'stage:1:9'):1,(0,'extra_character:Agent'):1,(0,'supply:0:0'):7})
        self.assertEqual(raw[16:24],output[16:24]);self.assertEqual(raw[2016:2096],output[2016:2096])
        self.assertEqual(struct.unpack_from('<H',output,34044)[0],0xb201)
        self.assertEqual(struct.unpack_from('<I',output,2440)[0],0xc0080000)
        self.assertEqual(output[2451],0xe0);self.assertEqual(output[-16:],raw[-16:])
        allowed=set(range(8,12))|set(range(1804,1808))|set(range(2440,2444))|{2451,34046,34047}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertFalse(Save(output,'re6').warnings)

    def test_integrity_repair_is_explicit_and_bad_inputs_rejected(self):
        raw=fixture();bad=bytearray(raw);bad[8]^=1
        save=Save(bad,'re6');self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,'skill_points'):10})
        self.assertEqual(save.patched({},True),raw)
        for bad in (raw[:-1],raw+bytes(4),bytes(FILE_SIZE)):
            self.assertFalse(looks_like_re6(bad))
            with self.assertRaises(FormatError):Save(bad,'re6')
        for edits in ({(0,'skill_points'):10000000},{(0,'stage:0:0'):2},{(0,'supply:0:0'):-1},{(0,'unknown'):1}):
            with self.assertRaises(ValueError):Save(raw,'re6').patched(edits)


if __name__=='__main__':unittest.main()

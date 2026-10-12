import struct
import unittest
from core import Save,FormatError
from re5_save import FILE_SIZE,encode,decode,checksum,looks_like_re5
from editor_layout import organize_fields


def fixture():
    plain=bytearray(FILE_SIZE)
    struct.pack_into('<Q',plain,0,0x0110000100000001)
    struct.pack_into('<6I',plain,0x10,2026,1,2,3,4,5)
    struct.pack_into('<I',plain,0x194,1000);struct.pack_into('<I',plain,0x198,500)
    struct.pack_into('<I',plain,0x130,0x80000000)
    plain[-16:]=b'KEEP PROFILE END'
    struct.pack_into('<I',plain,8,checksum(plain))
    return bytes(encode(plain))


class Re5Tests(unittest.TestCase):
    def setUp(self):self.raw=fixture()

    def test_chaining_matches_explicit_xor_oracle_and_round_trip(self):
        decoded=decode(self.raw)
        previous=bytes.fromhex('00211108c04b0000')
        for offset in range(0,FILE_SIZE,8):
            block=self.raw[offset:offset+8]
            self.assertEqual(decoded[offset:offset+8],bytes(a^b for a,b in zip(block,previous)))
            previous=block
        self.assertEqual(bytes(encode(decoded)),self.raw)
        self.assertEqual(Save(self.raw,'re5').patched({}),self.raw)

    def test_profile_fields_and_navigation(self):
        save=Save(self.raw,'re5')
        self.assertFalse(save.warnings);self.assertEqual(len(save.slots),1)
        self.assertEqual([c.name for c in organize_fields('re5',save.slots[0].fields)],['Progress','Unlocks','Collection'])

    def test_money_points_and_unlock_preserve_account_reserved_bits_and_tail(self):
        original=decode(self.raw)
        output=Save(self.raw,'re5').patched({(0,'money'):2345,(0,'points'):678,(0,'infinite_ammo:0'):1,(0,'chris_costume:3'):1})
        plain=decode(output)
        self.assertEqual(plain[:8],original[:8]);self.assertEqual(plain[-16:],b'KEEP PROFILE END')
        self.assertEqual(struct.unpack_from('<I',plain,0x130)[0],0x80000001)
        allowed=set(range(8,12))|set(range(0x124,0x128))|set(range(0x130,0x134))|set(range(0x194,0x19c))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,plain))))
        self.assertFalse(Save(output,'re5').warnings)

    def test_checksum_only_covers_documented_ranges(self):
        original=decode(self.raw);modified=bytearray(original)
        modified[0x3bac]^=1;modified[-1]^=1
        self.assertEqual(checksum(original),checksum(modified))
        modified[0x3bb0]^=1;self.assertNotEqual(checksum(original),checksum(modified))

    def test_corrupt_checksum_requires_repair(self):
        plain=decode(self.raw);plain[8]^=1;raw=encode(plain)
        save=Save(raw,'re5');self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,'money'):10})
        self.assertEqual(save.patched({},True),self.raw)

    def test_unknown_layouts_invalid_limits_and_fields_rejected(self):
        for raw in (bytes(FILE_SIZE),self.raw[:-1],self.raw+b'\0'):
            self.assertFalse(looks_like_re5(raw))
            with self.assertRaises(FormatError):Save(raw,'re5')
        for edits in ({(0,'money'):-1},{(0,'money'):1.5},{(0,'points'):10000000},{(0,'infinite_ammo:19'):1},{(0,'filter:0'):2}):
            with self.assertRaises(ValueError):Save(self.raw,'re5').patched(edits)


if __name__=='__main__':unittest.main()

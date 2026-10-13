import hashlib
import struct
import unittest
from core import Save,FormatError
from re_hd_save import FILE_SIZE,crypt,swap_words,looks_like_hd


def fixture():
    plain=bytearray(FILE_SIZE);struct.pack_into('<3I',plain,0,1,0,4)
    struct.pack_into('<I',plain,64,0xdf94)
    import zlib
    struct.pack_into('<4I',plain,0xdf94,~zlib.crc32(b'GAMEDATA0')&0xffffffff,12,0xdf20,0)
    struct.pack_into('<I',plain,32,FILE_SIZE-64)
    struct.pack_into('<I',plain,0xe05c,1)
    struct.pack_into('<2I',plain,0x163ec,0x11,30)
    struct.pack_into('<2I',plain,0x1643c,0x44,10)
    plain[250000:250016]=b'KEEP OTHER SLOT!'
    plain[12:32]=swap_words(hashlib.sha1(plain[64:]).digest())
    return crypt(plain,True)


class HdTests(unittest.TestCase):
    def test_inventory_supplies_difficulty_patch_preserves_other_slots_and_ids(self):
        raw=fixture();save=Save(raw,'re1_hd')
        self.assertTrue(looks_like_hd(raw));self.assertFalse(save.warnings)
        self.assertEqual(save.patched({}),raw)
        output=save.patched({(0,'difficulty'):3,(0,'inventory:0'):0,(0,'item_box:0'):99,(0,'daggers'):10})
        before=crypt(raw);after=crypt(output)
        allowed=set(range(12,32))|set(range(0xe05c,0xe060))|set(range(0x163f0,0x163f4))|set(range(0x16440,0x16444))|set(range(0x1b454,0x1b458))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
        self.assertEqual(after[250000:250016],b'KEEP OTHER SLOT!')
        self.assertEqual(struct.unpack_from('<I',after,0x163ec)[0],0x11)
        self.assertFalse(Save(output,'re1_hd').warnings)

    def test_integrity_repair_and_unknown_layout_guard(self):
        raw=fixture();plain=bytearray(crypt(raw));plain[12]^=1
        save=Save(crypt(plain,True),'re1_hd');self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,'difficulty'):0})
        self.assertEqual(save.patched({},True),raw)
        for bad in (bytes(FILE_SIZE),raw[:-1],raw+b'\0'):
            with self.assertRaises(FormatError):Save(bad,'re1_hd')
        for edits in ({(0,'difficulty'):4},{(0,'inventory:0'):256},{(0,'other_slot'):1}):
            with self.assertRaises(ValueError):Save(raw,'re1_hd').patched(edits)


if __name__=='__main__':unittest.main()

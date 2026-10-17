"""Synthetic directory/growth tests; no game save is distributed."""
import struct,unittest
from core import Save
from rockstar_container import RockstarContainer,aes,name_hash
from rdr2_pso import RsavDirectory,pointer
from test_rockstar import fixture


def rsav(encrypted=True,source=None):
    native=RockstarContainer(source or fixture('rdr2',False),'rdr2')
    root=native.plain[native.frames[0].start:native.frames[0].end+20]
    root+=bytes((-len(root))%16)
    script=RockstarContainer(fixture('gtav',False),'gtav')
    data=script.plain[script.frames[0].start:script.frames[0].end+20];data+=bytes((-len(data))%16)
    header=bytearray(64);header[:4]=b'RSAV';struct.pack_into('<4I',header,4,3,64,len(root),2)
    body=bytes(header)+b'CODE'+bytes(12)+root+b'ENDC'+bytes(12)
    for n in range(2):
        struct.pack_into('<4I',header,20+n*16,0x100+n,0,len(body),len(data))
        body+=f'S{n:03d}'.encode()+bytes(12)+data+b'ENDS'+bytes(12)
    body=bytes(header)+body[64:]
    return native.raw[:0x110]+(aes(body,False) if encrypted else body)


class Rdr2PsoTests(unittest.TestCase):
    def test_growing_one_block_preserves_scripts_all_checks_and_cipher_mode(self):
        for encrypted in (False,True):
            raw=rsav(encrypted);c=RockstarContainer(raw,'rdr2');directory=RsavDirectory(c)
            h,at,size=c.frames[0].blocks[0];original=c.plain[at:at+size]
            new=bytearray(original);struct.pack_into('>Q',new,8,2);struct.pack_into('>I',new,24,name_hash('CONSUMABLE_MEDICINE'))
            out=c.replace_root_blocks({1:original+new});after=RockstarContainer(out,'rdr2');later=RsavDirectory(after)
            self.assertFalse(after.warnings);self.assertEqual(after.encrypted,encrypted)
            self.assertEqual(len(after.checks),3);self.assertGreater(len(out),len(raw))
            self.assertEqual((len(out)-len(raw))%16,0)
            for before,post in zip(directory.entries[1:],later.entries[1:]):
                self.assertEqual(c.plain[before[1]:before[3]+16],after.plain[post[1]:post[3]+16])
            self.assertEqual(out[:0x110],raw[:0x110]);self.assertEqual(c.replace_root_blocks({}),raw)
            self.assertEqual(c.replace_root_blocks({1:original}),raw)
            # The old cash record remains in orphaned PSIN bytes. Only its
            # mapped replacement is read, so it is not mistaken for a duplicate.
            cash=Save(out,'rdr2');self.assertEqual(cash.slots[0].fields[0].value,123.45)
            changed=Save(cash.patched({(0,'cash'):55.25}),'rdr2')
            self.assertEqual(changed.slots[0].fields[0].value,55.25)

    def test_unknown_chunks_overlaps_versions_and_trailing_data_are_rejected(self):
        c=RockstarContainer(rsav(False),'rdr2');h,at,size=c.frames[0].blocks[0];replacement=c.plain[at:at+size]*2
        for location,fmt,value in ((0x114,'<I',4),(0x110+28,'<I',64),(0x110+12,'<I',32)):
            raw=bytearray(c.plain);struct.pack_into(fmt,raw,location,value)
            bad=RockstarContainer(c.encode(raw),'rdr2')
            with self.assertRaises(ValueError):bad.replace_root_blocks({1:replacement})
        raw=bytearray(c.plain);raw[c.frames[1].start-16:c.frames[1].start-12]=b'NOPE'
        with self.assertRaises(ValueError):RockstarContainer(c.encode(raw),'rdr2').replace_root_blocks({1:replacement})

    def test_block_type_stride_size_and_integrity_are_checked_before_relocation(self):
        c=RockstarContainer(rsav(False),'rdr2');h,at,size=c.frames[0].blocks[0];value=c.plain[at:at+size]
        for changes in ({0:value*2},{2:value*2},{True:value*2},{1:value[:-1]},{1:value+bytes(3)},{1:'not bytes'}):
            with self.assertRaises(ValueError):c.replace_root_blocks(changes)
        raw=bytearray(c.plain);raw[at+44]^=1;bad=RockstarContainer(raw,'rdr2');self.assertTrue(bad.warnings)
        with self.assertRaisesRegex(ValueError,'integrity'):bad.replace_root_blocks({1:value*2})
        with self.assertRaises(ValueError):RockstarContainer(fixture(),'gtav').replace_root_blocks({1:value*2})

    def test_extended_pointer_matches_the_reader_and_rejects_reserved_or_overflow_values(self):
        for offset in (0,4095,4096,1048576,(1<<44)-1):
            raw=pointer(123,offset);word=struct.unpack_from('>I',raw)[0]
            self.assertEqual(word&4095,123);self.assertFalse(word&0xff000)
            self.assertEqual((word>>20)|(struct.unpack_from('<I',raw,4)[0]<<12),offset)
        for args in ((0,0),(4096,0),(True,0),(1,-1),(1,1<<44),(1,False)):
            with self.assertRaises(ValueError):pointer(*args)

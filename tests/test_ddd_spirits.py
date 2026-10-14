"""Native PC spirit coordinates, independent characters and opaque boards."""
import struct
import unittest
import zlib
from core import Save, png_chunks
from test_kh_extra import archive


def fixture(level=20, xp=10000, hp=200, shine=1):
    raw=bytearray(archive('ddd',2));s=Save(raw,'ddd')
    for slot,(record,_) in enumerate(s.extra_kh.records):
        for index in (0,1,101):
            base=record+0x53a0+index*256
            raw[base]=1;raw[base+2]=0x35;raw[base+3]=level
            raw[base+6:base+28]=b'KEEP SPIRIT NAME!!!!!\0'
            raw[base+30]=0x23;raw[base+32:base+35]=bytes((128,37,12))
            struct.pack_into('<i',raw,base+36,xp)
            struct.pack_into('<i',raw,base+40,1500)
            struct.pack_into('<h',raw,base+44,250)
            struct.pack_into('<h',raw,base+48,hp)
            raw[base+61:base+64]=bytes((10,20,30));raw[base+74]=7;raw[base+92]=shine
            struct.pack_into('<h',raw,base+93,7780)
            raw[base+95:base+256]=bytes([0x5a+slot])*161
    for name,start,end in png_chunks(raw,True):
        if name==b'sqEX':struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw)


class DreamEaterDetailsTests(unittest.TestCase):
    def test_populated_spirits_expose_named_values_without_creating_new_species(self):
        s=Save(fixture(),'ddd');fields=s.slots[0].fields
        self.assertEqual(next(f.value for f in fields if f.key=='spirit:0:level'),20)
        self.assertEqual(next(f.value for f in fields if f.key=='spirit:0:link_points'),250)
        self.assertEqual(next(f.value for f in fields if f.key=='spirit:101:max_hp'),200)
        self.assertFalse(any(f.key.startswith('spirit:2:') for f in fields))
        self.assertEqual(s.patched({}),s.raw)

    def test_edits_change_exact_selected_bytes_preserving_board_name_affinity_and_other_slots(self):
        raw=fixture();s=Save(raw,'ddd');record,length=s.extra_kh.records[0]
        edits={'spirit:0:level':40,'spirit:0:experience':25000,'spirit:0:link_points':1000,
               'spirit:0:max_hp':400,'spirit:0:color_red':255,'spirit:0:color_blue':0,'spirit:0:shiny':1,
               'spirit:101:links_used':21}
        out=s.patched({(0,k):v for k,v in edits.items()});check=Save(out,'ddd')
        self.assertFalse(check.warnings)
        for k,v in edits.items():self.assertEqual(next(f.value for f in check.slots[0].fields if f.key==k),v)
        allowed=set()
        for f in s.slots[0].fields:
            if f.key in edits:allowed.update(range(f.offset,f.offset+(struct.calcsize(f.fmt) if f.fmt else 1)))
        for name,start,end in png_chunks(raw,True):
            if name==b'sqEX':allowed.update(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        r,l=s.extra_kh.records[1];self.assertEqual(raw[r:r+l],out[r:r+l])
        base=record+0x53a0
        self.assertEqual(out[base+2],0x35);self.assertEqual(out[base+30],0x23)
        self.assertEqual(struct.unpack_from('<i',out,base+40)[0],1500)
        self.assertEqual(struct.unpack_from('<h',out,base+93)[0],7780)

    def test_shiny_encoding_is_reversible_and_unknown_state_is_preserved(self):
        s=Save(fixture(shine=2),'ddd');out=s.patched({(0,'spirit:0:shiny'):0})
        b=s.extra_kh.records[0][0]+0x53a0
        self.assertEqual(out[b+92],1)
        self.assertFalse(any(f.key.endswith(':shiny') for f in Save(fixture(shine=3),'ddd').slots[0].fields))

    def test_unsupported_or_empty_spirit_layouts_are_not_reinterpreted(self):
        for kw in ({'level':0},{'level':100},{'xp':-1},{'hp':0}):
            s=Save(fixture(**kw),'ddd')
            self.assertFalse(any(f.key=='spirit:0:level' for f in s.slots[0].fields))
            self.assertEqual(s.patched({}),s.raw)
        for key,value in (('spirit:0:link_points',32768),('spirit:0:max_hp',0),('spirit:0:color_red',256)):
            with self.assertRaises(ValueError):Save(fixture(),'ddd').patched({(0,key):value})


if __name__=='__main__':unittest.main()

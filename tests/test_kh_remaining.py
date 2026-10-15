"""Independent native enum values, staged references and nibble preservation."""
import struct,unittest,zlib
from core import Save,png_chunks
from test_kh_extra import kh3_plain,archive
from test_game_completion import checksum3
from test_ddd_spirits import fixture as spirits
from kh_pc import recom_checksum


class KhRemainingTests(unittest.TestCase):
    def test_kh3_links_do_not_overlap_the_native_consumable_commands(self):
        s=Save(kh3_plain(),'kh3');p=s.kh3.progress
        self.assertEqual(p.operations['link:70'][1],(0,70))
        self.assertNotIn('link:65',p.operations)
        choice=p.operations['shortcut:0:0'][1].index(70)
        out=s.patched({(0,'link:70'):1,(0,'shortcut:0:0'):choice})
        self.assertEqual(struct.unpack_from('<i',out,0xbf68)[0],70)
        self.assertEqual(struct.unpack_from('<i',out,0xbf20)[0],70)
        # The previously misidentified command belongs to Megalixir; an
        # unproven word in the Link acquisition block must not be migrated.
        raw=bytearray(kh3_plain());struct.pack_into('<i',raw,0xbf68,65)
        s=Save(checksum3(raw),'kh3');out=s.patched({(0,'munny'):100})
        self.assertEqual(struct.unpack_from('<i',out,0xbf68)[0],65)
    def test_kh3_hi_ether_shortcut_requires_and_resolves_its_distinct_item_enum(self):
        s=Save(kh3_plain(),'kh3');key='shortcut:0:0'
        choice=s.kh3.progress.operations[key][1].index(62)
        with self.assertRaisesRegex(ValueError,'item shortcut'):s.patched({(0,key):choice})
        equipped='character:Sora:equipment:consumable:0'
        item=s.kh3.characters.equipment[equipped][1].index(11)
        out=s.patched({(0,key):choice,(0,equipped):item})
        check=Save(out,'kh3');self.assertFalse(check.warnings)
        self.assertEqual(struct.unpack_from('<i',out,0xbf20)[0],62)
        self.assertEqual(out[0x1880+0x118],11);self.assertGreater(out[0x8f4+11*2],0)
        removed=check.patched({(0,'inventory:11'):0})
        self.assertEqual(struct.unpack_from('<i',removed,0xbf20)[0],0)
        with self.assertRaisesRegex(ValueError,'item shortcut'):
            check.patched({(0,'inventory:11'):0,(0,key):choice})
    def test_kh3_existing_item_shortcuts_and_encrypted_output_remain_verifiable(self):
        from kh3_pc import transform
        import hashlib
        raw=bytearray(kh3_plain());raw[0x8f4+2]=1;raw[0x8f4+3]=1
        at=0x1880+0x118;raw[at]=1;raw[at+4]=1
        struct.pack_into('<i',raw,0xbf20,58);raw=checksum3(raw)
        account='synthetic-item-reference';encrypted=transform(raw,account,True)+b'\x08'+hashlib.md5(raw[:0x94f4e8]).digest()
        s=Save(encrypted,'kh3',account_id=account)
        out=s.patched({(0,'munny'):100});check=Save(out,'kh3',account_id=account)
        self.assertEqual(struct.unpack_from('<i',check.kh3.plain,0xbf20)[0],58)
        self.assertEqual(check.kh3.plain[-8:],raw[-8:]);self.assertFalse(check.warnings)
    def test_ddd_rank_disposition_share_one_byte_without_overwriting_each_other(self):
        raw=spirits();s=Save(raw,'ddd');record,_=s.extra_kh.records[0];at=record+0x53a0+2
        rank=s.patched({(0,'spirit:0:rank'):6});self.assertEqual(rank[at],0x36)
        both=s.patched({(0,'spirit:0:rank'):4,(0,'spirit:0:disposition'):1,(0,'spirit:0:affinity'):2500})
        self.assertEqual(both[at],0x14);self.assertEqual(struct.unpack_from('<i',both,record+0x53a0+40)[0],2500)
        allowed={at}|set(range(record+0x53a0+40,record+0x53a0+44))
        for name,start,end in png_chunks(raw,True):
            if name==b'sqEX':allowed.update(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,both))))
        self.assertFalse(Save(both,'ddd').warnings)
    def test_ddd_unknown_nibbles_and_unpopulated_spirits_remain_protected(self):
        raw=bytearray(spirits());s=Save(raw,'ddd');at=s.extra_kh.records[0][0]+0x53a0+2
        raw[at]=0xf5
        for name,start,end in png_chunks(raw,True):
            if name==b'sqEX':struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
        s=Save(raw,'ddd');self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='spirit:0:disposition'))
        out=s.patched({(0,'spirit:0:rank'):6});self.assertEqual(out[at],0xf6)
        with self.assertRaises(ValueError):s.patched({(0,'spirit:0:disposition'):0})
    def test_recom_stored_level_preserves_xp_growth_decks_other_records_and_integrity(self):
        raw=bytearray(archive('recom'));s=Save(raw,'recom');record,length=s.extra_kh.records[0]
        struct.pack_into('<i',raw,record+0x2d54,7)
        struct.pack_into('<I',raw,record+4,recom_checksum(raw[record+16:record+length]))
        for name,start,end in png_chunks(raw,True):
            if name==b'sqEX':struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
        s=Save(raw,'recom');out=s.patched({(0,'level'):25});check=Save(out,'recom')
        self.assertEqual(next(f.value for f in check.slots[0].fields if f.key=='level'),25)
        self.assertEqual(out[record+0x2d50:record+0x2d54],raw[record+0x2d50:record+0x2d54]);self.assertFalse(check.warnings)
        allowed=set(range(record+4,record+8))|set(range(record+0x2d54,record+0x2d58))
        for name,start,end in png_chunks(raw,True):
            if name==b'sqEX':allowed.update(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))

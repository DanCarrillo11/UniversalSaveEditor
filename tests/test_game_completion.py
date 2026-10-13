"""Dependent magic/shortcut edits and acquisition-state preservation."""
import struct,unittest,zlib
from core import Save,png_chunks
from test_kh_extra import kh3_plain,archive
from kh3_pc import transform

def checksum3(raw):
    struct.pack_into('<I',raw,12,zlib.crc32(raw[16:0x94f4e8]));return bytes(raw)
def recom_ready():
    raw=bytearray(archive('recom'));s=Save(raw,'recom');r,l=s.extra_kh.records[0]
    raw[r+0x32f]=0xfc;raw[r+0x333]=0xff;raw[r+0x337]=0xfe;raw[r+0x4a1]=0xe1
    from kh_pc import recom_checksum
    struct.pack_into('<I',raw,r+4,recom_checksum(raw[r+16:r+l]))
    _,a,b=next(c for c in png_chunks(raw,True) if c[0]==b'sqEX')
    struct.pack_into('>I',raw,b,zlib.crc32(raw[a-4:b]));return bytes(raw),r,l

class CompletionTests(unittest.TestCase):
    def test_hd_complete_documented_item_table_preserves_unmapped_id_and_section_bytes(self):
        from test_re_hd import fixture
        from re_hd_save import crypt,ITEMS
        raw=fixture();save=Save(raw,'re1_hd')
        field=next(f for f in save.slots[0].fields if f.key=='item_box:1:identity')
        self.assertEqual(len(ITEMS),131);self.assertNotIn(0x59,ITEMS)
        choice=save.re_hd.operations[field.key][1].index(0x84)
        output=save.patched({(0,field.key):choice});parsed=Save(output,'re1_hd')
        self.assertFalse(parsed.warnings);a,b=crypt(raw),crypt(output);at=field.offset
        self.assertEqual(struct.unpack_from('<2I',b,at),(0x84,1))
        allowed=set(range(12,32))|set(range(at,at+8))
        self.assertTrue(all(x==y or i in allowed for i,(x,y) in enumerate(zip(a,b))))
        with self.assertRaises(ValueError):save.patched({(0,field.key):choice,(0,'item_box:1'):2})
        original=next(f for f in save.slots[0].fields if f.key=='item_box:0:identity')
        selected=save.re_hd.operations[original.key][1].index(0x37)
        replaced=crypt(save.patched({(0,original.key):selected}))
        self.assertEqual(struct.unpack_from('<2I',replaced,original.offset),(0x37,1))
    def test_kh2_companion_preferences_preserve_party_abilities_and_unknown_bytes(self):
        from test_expansion import kh_fixture
        raw,*_=kh_fixture('kh2');save=Save(raw,'kh2')
        keys={(0,'character:1:ai:combat'):5,(0,'character:2:ai:ability:3'):2}
        output=save.patched(keys);parsed=Save(output,'kh2');self.assertFalse(parsed.warnings)
        for slot,key in keys:self.assertEqual(next(f.value for f in parsed.slots[slot].fields if f.key==key),keys[slot,key])
        allowed={f.offset for f in save.slots[0].fields if (0,f.key) in keys}
        end=save.crc_regions[0][1];allowed.update(range(end,end+4))
        for start,stop in save.crc_regions:
            record=next(f.offset for f in save.slots[0].fields if f.key=='munny')-0x2440;allowed.update(range(record+8,record+12))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
    def test_kh1_shared_abilities_preserve_unknown_entry_and_other_slot(self):
        from test_expansion import kh_fixture
        raw,*_=kh_fixture('kh1');save=Save(raw,'kh1');key='shared_ability:0'
        identifier=save.party.encodings[0,key][2].index(4)
        output=save.patched({(0,key):identifier})
        self.assertEqual(output[next(f.offset for f in save.slots[0].fields if f.key==key)],4)
        self.assertEqual(next(f.value for f in Save(output,'kh1').slots[0].fields if f.key==key),identifier)
    def test_re6_completion_flags_preserve_nonzero_encodings_and_profile_identity(self):
        from test_re6 import fixture
        from re6_save import checksum
        raw=bytearray(fixture());raw[9448]=3;struct.pack_into('<I',raw,8,checksum(raw));raw=bytes(raw);save=Save(raw,'re6')
        with self.assertRaises(ValueError):save.patched({(0,'merc_record:Solo:0:0:completed'):0})
        output=save.patched({(0,'last_difficulty'):4,(0,'merc_record:Solo:0:1:completed'):1})
        self.assertEqual(output[9448],3);self.assertEqual(output[9460],1);self.assertEqual(output[16:24],raw[16:24])
        self.assertFalse(Save(output,'re6').warnings)
    def test_elden_map_unlocks_preserve_other_flags_slots_and_hashes(self):
        from test_expansion import elden_ready
        from hashlib import md5
        raw=elden_ready();save=Save(raw,'eldenring');field=next(f for f in save.slots[1].fields if f.key=='map:62010')
        altered=bytearray(raw);altered[field.offset]|=0x80
        start,length=save.elden_ring.blocks[save.elden_ring.characters[1].physical]
        altered[start:start+16]=md5(altered[start+16:start+length]).digest();raw=bytes(altered);save=Save(raw,'eldenring')
        output=save.patched({(1,'map:62010'):1,(1,'talisman_slots'):3})
        self.assertEqual(output[field.offset],0xa0)
        c=save.elden_ring.characters[1];self.assertEqual(output[c.player+0xbe],3)
        allowed=set(range(start,start+16))|{field.offset,c.player+0xbe}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        parsed=Save(output,'eldenring');self.assertFalse(parsed.warnings)
        with self.assertRaises(ValueError):parsed.patched({(1,'map:62010'):0})
        with self.assertRaises(ValueError):parsed.patched({(1,'talisman_slots'):2})
    def test_ror2_extreme_unknown_counter_is_preserved_without_load_overflow(self):
        from test_core import ror2
        raw=ror2().replace(b'</stats>',b'<stat name="unknownHuge">'+b'9'*1000+b'</stat></stats>')
        save=Save(raw,'ror2');self.assertFalse(any(f.key=='stat:unknownHuge' for f in save.slots[0].fields))
        output=save.patched({(0,'coins'):42});self.assertIn(b'9'*1000,output)
    def test_kh3_acquisition_order_is_not_assumed_and_duplicate_families_are_protected(self):
        raw=bytearray(kh3_plain());struct.pack_into('<6i',raw,0xbf50,41,29,0,0,0,0)
        raw=checksum3(raw);save=Save(raw,'kh3');output=save.patched({(0,'magic:Water'):3,(0,'magic:Blizzard'):2})
        self.assertEqual(struct.unpack_from('<3i',output,0xbf50),(43,29,34))
        duplicated=bytearray(raw);struct.pack_into('<i',duplicated,0xbf58,30);save=Save(checksum3(duplicated),'kh3')
        self.assertFalse(any(f.key=='magic:Fire' for f in save.slots[0].fields))
        with self.assertRaises(ValueError):save.patched({(0,'magic:Fire'):3})
    def test_kh3_magic_tiers_synchronize_known_shortcuts_and_preserve_unknown_commands(self):
        raw=bytearray(kh3_plain());struct.pack_into('<i',raw,0xbf50,29)
        struct.pack_into('<3i',raw,0xbf20,29,999,0);raw=checksum3(raw);s=Save(raw,'kh3')
        output=s.patched({(0,'magic:Fire'):3,(0,'record:0'):123456})
        self.assertEqual(struct.unpack_from('<2i',output,0xbf20),(31,999))
        self.assertEqual(struct.unpack_from('<i',output,0xbf50)[0],31)
        self.assertEqual(struct.unpack_from('<i',output,0x83cd8)[0],123456)
        self.assertFalse(Save(output,'kh3').warnings)
        with self.assertRaises(ValueError):s.patched({(0,'shortcut:0:1'):0})
        allowed=set(range(12,16))|set(range(0xbf20,0xbf24))|set(range(0xbf50,0xbf54))|set(range(0x83cd8,0x83cdc))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
    def test_kh3_shortcuts_require_acquired_commands_and_explicit_shortcuts_win(self):
        raw=checksum3(bytearray(kh3_plain()));s=Save(raw,'kh3');ops=s.kh3.progress.operations
        fire=ops['shortcut:0:0'][1].index(29);fira=ops['shortcut:0:0'][1].index(30)
        with self.assertRaises(ValueError):s.patched({(0,'shortcut:0:0'):fire})
        with self.assertRaises(ValueError):s.patched({(0,'magic:Fire'):1,(0,'shortcut:0:0'):fira})
        output=s.patched({(0,'magic:Fire'):3,(0,'shortcut:0:0'):fire})
        self.assertEqual(struct.unpack_from('<i',output,0xbf20)[0],29)
        link=ops['shortcut:0:1'][1].index(65)
        with self.assertRaises(ValueError):s.patched({(0,'shortcut:0:1'):link})
        output=s.patched({(0,'link:65'):1,(0,'shortcut:0:1'):link})
        empty=Save(output,'kh3').patched({(0,'link:65'):0})
        self.assertEqual(struct.unpack_from('<i',empty,0xbf24)[0],0)
    def test_kh3_new_fields_reencrypt_and_keep_original_account_and_padding(self):
        from hashlib import md5
        account='synthetic-test-account';raw=kh3_plain();encrypted=transform(raw,account,True)+b'\x08'+md5(raw[:0x94f4e8]).digest()
        output=Save(encrypted,'kh3',account_id=account).patched({(0,'magic:Cure'):2,(0,'flan:6:2'):42})
        parsed=Save(output,'kh3',account_id=account)
        self.assertFalse(parsed.warnings);self.assertEqual(parsed.kh3.plain[-8:],raw[-8:])
        self.assertEqual(next(f.value for f in parsed.slots[0].fields if f.key=='flan:6:2'),42)
    def test_recom_acquisition_preserves_reserved_bits_and_other_slot(self):
        raw,r,l=recom_ready();s=Save(raw,'recom');output=s.patched({(0,'card_unlock:25'):1,(0,'extra_card_unlock:12'):1,(0,'friend_unlock:8'):1,(0,'sora_cleared'):1})
        self.assertEqual(output[r+0x32f],0xfe);self.assertEqual(output[r+0x333],0xff)
        self.assertEqual(output[r+0x335],1);self.assertEqual(output[r+0x337],0xfe);self.assertEqual(output[r+0x4a1],0xe3)
        self.assertEqual(output[r+0x3a30:r+2*0x3a30],raw[r+0x3a30:r+2*0x3a30]);self.assertFalse(Save(output,'recom').warnings)
        with self.assertRaises(ValueError):Save(output,'recom').patched({(0,'sora_cleared'):0})
    def test_recom_adding_a_card_grants_only_its_exact_acquisition_and_detects_conflict(self):
        raw,r,l=recom_ready();s=Save(raw,'recom');output=s.patched({(0,'card:60'):5})
        self.assertEqual(output[r+0x32c],raw[r+0x32c]|1)
        with self.assertRaises(ValueError):s.patched({(0,'card:60'):5,(0,'card_unlock:0'):0})
        self.assertEqual(Save(raw,'recom').patched({}),raw)

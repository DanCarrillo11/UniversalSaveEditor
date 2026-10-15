"""Independent tests of typed settings, context guards and cross-slot edits."""
import hashlib
import struct
import unittest
import zlib
from core import Save
from re_engine_stream import StreamReader
from re_engine_container import ReEngineEnvelope
from re_hashes import murmur32
from test_re_engine import wrap,stream,ACCOUNT
from test_village import Writer
from test_expansion import elden_ready,kh_fixture
from re_hd_save import crypt,swap_words

def elden_appearance():
    raw=bytearray(elden_ready());save=Save(raw,'eldenring')
    storage=next(f.offset for f in save.slots[0].fields if f.key=='storage:0')-8
    face=storage-303
    struct.pack_into('<I4s2I',raw,face,0xffffffff,b'FACE',4,0x120)
    raw[face+0x70:face+0xb0]=b'UNKNOWN FACIAL DATA'.ljust(64,b'!')
    raw[face+0xb0:face+0x112]=bytes([128])*98
    for start,length in save.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw),face

def hd_multiple():
    first=0x100;second=first+0xdf30;system=second+0xdf30
    plain=bytearray(system+64);struct.pack_into('<3I',plain,0,1,0,12)
    struct.pack_into('<I',plain,32,len(plain)-64);struct.pack_into('<3I',plain,64,first,second,system)
    for n,base in ((0,first),(7,second)):
        struct.pack_into('<4I',plain,base,~zlib.crc32(f'GAMEDATA{n}'.encode())&0xffffffff,12,0xdf20,0)
        struct.pack_into('<2I',plain,base+0x84a8,0x44,10)
    struct.pack_into('<4I',plain,system,0x11223344,1,16,0);plain[system+16:system+32]=b'KEEP SYSTEM DATA'
    plain[12:32]=swap_words(hashlib.sha1(plain[64:]).digest())
    return crypt(plain,True),first,second,system

class SettingsTests(unittest.TestCase):
    def test_elden_named_appearance_changes_only_selected_bytes_and_block_digest(self):
        raw,face=elden_appearance();save=Save(raw,'eldenring')
        fields=[f for f in save.slots[0].fields if f.group=='Appearance'];self.assertEqual(len(fields),96)
        changes={(0,'appearance:b7'):10,(0,'appearance:10f'):230,(0,'appearance:b3'):77}
        output=save.patched(changes)
        allowed={face+0xb7,face+0x10f,face+0xb3}|set(range(0x300,0x310))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertEqual(output[face+0x70:face+0xb0],raw[face+0x70:face+0xb0]);self.assertFalse(Save(output,'eldenring').warnings)
        with self.assertRaises(ValueError):save.patched({(0,'appearance:b7'):256})

    def test_elden_unknown_face_layout_is_retained_and_not_exposed(self):
        raw,_=elden_appearance();raw=bytearray(raw);save=Save(raw,'eldenring')
        offset=next(f.offset for f in save.slots[0].fields if f.key=='appearance:b7')-0xb7
        raw[offset+8]=5
        for start,length in save.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
        check=Save(raw,'eldenring');self.assertFalse(any(f.group=='Appearance' for f in check.slots[0].fields))
        self.assertEqual(check.patched({}),raw)

    def test_hd_directory_supports_variable_length_and_independent_second_slot(self):
        raw,first,second,system=hd_multiple();save=Save(raw,'re1_hd');self.assertEqual(len(save.slots),2)
        choice=save.re_hd.operations['slot:7:item_box:1:identity'][1].index(17)
        output=save.patched({(1,'slot:7:difficulty'):2,(1,'slot:7:item_box:1:identity'):choice,(1,'slot:7:item_box:1'):25})
        before,after=crypt(raw),crypt(output)
        self.assertEqual(after[first:second],before[first:second]);self.assertEqual(after[system:],before[system:])
        self.assertEqual(struct.unpack_from('<2I',after,second+0x84a8+8),(17,25))
        check=Save(output,'re1_hd');self.assertFalse(check.warnings)
        cleared=check.patched({(1,'slot:7:item_box:1:identity'):0})
        self.assertEqual(struct.unpack_from('<2I',crypt(cleared),second+0x84a8+8),(0,0))
        with self.assertRaises(ValueError):save.patched({(1,'slot:7:item_box:1'):25})

    def test_hd_overlapping_and_unsorted_directory_rejected(self):
        raw,first,second,system=hd_multiple()
        for offsets in ((second,first,system),(first,first,system),(first,first+20,system)):
            plain=bytearray(crypt(raw));struct.pack_into('<3I',plain,64,*offsets)
            with self.assertRaises(ValueError):Save(crypt(plain,True),'re1_hd')

    def test_re4_costume_identity_and_profile_context_are_required(self):
        w=Writer();w.data=bytearray(16);w.data.extend(stream('re4_remake'))
        costume=lambda identifier,duplicate=False:(0xa4ad52ff,[('_ID',7,('<i',identifier)),('_IsUnlock',2,('<B',0))]+([('_ID',7,('<i',101))] if duplicate else []))
        w.root(0x84db4327,[('saveCostumeDatas',-1,[costume(100),costume(200,True)])])
        w.root(*costume(999))
        raw=wrap(bytes(w.data[16:]),'re4_remake');save=Save(raw,'re4_remake',account_id=ACCOUNT)
        fields=[f for f in save.slots[0].fields if f.group=='Costumes']
        self.assertEqual(len(fields),1);self.assertIn('Costume ID 100',fields[0].label)
        output=save.patched({(0,fields[0].key):1});before=save.re_engine.data;after=Save(output,'re4_remake',account_id=ACCOUNT).re_engine.data
        self.assertTrue(all(a==b or i==fields[0].offset for i,(a,b) in enumerate(zip(before,after))))

    def test_saved_difficulty_choices_and_unsigned_records_preserve_unknown_bytes(self):
        raw=wrap(stream('re2'),'re2');save=Save(raw,'re2')
        difficulty=next(f for f in save.slots[0].fields if f.group=='Difficulty')
        count=next(f for f in save.slots[0].fields if f.fmt=='<I')
        self.assertEqual(difficulty.choices,('Assisted','Standard','Hardcore'))
        output=save.patched({(0,difficulty.key):0,(0,count.key):900000001})
        check=Save(output,'re2');self.assertEqual(next(f.value for f in check.slots[0].fields if f.key==count.key),900000001)
        self.assertEqual(check.re_engine.data.count(b'KEEPUNKNOWNSTATE'),save.re_engine.data.count(b'KEEPUNKNOWNSTATE'))

    def test_kh1_magic_bits_and_kh2_auto_reload_keep_other_bytes(self):
        for game,key,value in (('kh1','0:magic:6',1),('kh2','character:0:auto_reload:0',1)):
            raw,record,start,end=kh_fixture(game);save=Save(raw,game)
            f=next(f for f in save.slots[0].fields if f.key==key);output=save.patched({(0,key):value})
            allowed=set(range(f.offset,f.offset+(1 if game=='kh1' else 2)))|set(range(end,end+4))
            if game=='kh1':
                # A first learned Sora spell also grants Donald its availability;
                # the shared native tier is stored separately from both flags.
                allowed.update((record+0x74,record+0xe8))
                self.assertEqual(output[record+0x74]&0x40,0x40)
                self.assertEqual(output[record+0xe8]&0x40,0x40)
                self.assertEqual(output[record+0x498],1)
            if game=='kh2':allowed.update(range(record+8,record+12))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))

if __name__=='__main__':unittest.main()

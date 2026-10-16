"""Synthetic PC story envelopes, typed fields and encrypted preservation."""
from pathlib import Path
import struct,tempfile,unittest
from unittest.mock import patch
from core import Save,FormatError,identify_game,replace_current,discover
from rockstar_container import aes,checksum,RockstarContainer
from rockstar_save import SKILLS,name_hash


def section(tag,data):return tag+struct.pack('>I',len(data)+8)+data


def fixture(game='gtav',encrypted=True,duplicate=False,bad_type=False):
    if game=='gtav':
        pairs=[(name_hash(f'sp{n}_{key}'),1000+n if key=='TOTAL_CASH' else 25+n)
               for n in range(3) for key in ('TOTAL_CASH',)+tuple(k for k,v in SKILLS)]
        if duplicate:pairs.append(pairs[0])
        data=b''.join(struct.pack('>2I',*p) for p in pairs);identity=2199017832
        definition=struct.pack('>3I',2,8,0)+struct.pack('>IBBHI',3742647683,5,0,0,0)+struct.pack('>IBBHI',3021077118,9 if bad_type else 5,0,4,0)
    else:
        data=bytearray(96 if duplicate else 64);data[16:20]=bytes.fromhex('ce548cf5');struct.pack_into('>I',data,32,12345)
        if duplicate:data[64:68]=bytes.fromhex('ce548cf5');struct.pack_into('>I',data,80,12000)
        identity=2363674431;definition=struct.pack('>3I',0,48,0)
    mapping=struct.pack('>IHH',1,1,0x7070) if game=='gtav' else struct.pack('>IIHHI',1,0,1,0,0)
    mapping+=struct.pack('>4I',identity,8,0,len(data))
    schema=struct.pack('>3I',1,identity,20)+definition
    frame=section(b'PSIN',data)+section(b'PMAP',mapping)+section(b'PSCH',schema)+section(b'PSIG',b'')
    check=b'CHKS'+struct.pack('>4I',20,len(frame)+20,0,1)
    check=check[:12]+struct.pack('>I',checksum(frame+check[:8]+bytes(8)+check[16:]))+check[16:]
    start=0x108 if game=='gtav' else 0x110;header=bytearray(start);struct.pack_into('>I',header,0,1 if game=='gtav' else 4)
    title='Synthetic story save'.encode('utf-16-le');header[4:4+len(title)]=title
    h=checksum(header[:4][::-1],0);value=checksum(header[4:0x104],h) if game=='gtav' else checksum(bytes(8),h)
    struct.pack_into('>I',header,0x104 if game=='gtav' else 0x10c,value)
    body=(b'' if game=='gtav' else b'RSAV'+bytes(188))+frame+check
    body+=bytes((-len(body))%16)
    return bytes(header)+(aes(body,False) if encrypted else body)


class RockstarTests(unittest.TestCase):
    def test_known_cash_hashes_and_every_character_skill_use_distinct_fields(self):
        self.assertEqual([name_hash(f'sp{n}_total_cash') for n in range(3)],[0x0324c31d,0x44bd6982,0x8d75047d])
        s=Save(fixture(),'gtav');self.assertEqual(len(s.slots[0].fields),27);self.assertFalse(s.warnings)
        self.assertEqual(len({f.offset for f in s.slots[0].fields}),27)
        self.assertEqual({f.collection for f in s.slots[0].fields},{'Michael','Franklin','Trevor'})

    def test_noop_and_unrelated_bytes_survive_encrypted_and_plaintext_edits(self):
        for game,key,value in (('gtav','character:1:total_cash',8675309),('gtav','character:2:stamina',100),('rdr2','cash',456.78)):
            for encrypted in (False,True):
                with self.subTest(game=game,key=key,encrypted=encrypted):
                    raw=fixture(game,encrypted);s=Save(raw,game);self.assertEqual(s.patched({}),raw)
                    self.assertEqual(s.rockstar.patch({}),raw)
                    out=s.patched({(0,key):value});after=Save(out,game);self.assertFalse(after.warnings)
                    f=next(f for f in s.slots[0].fields if f.key==key);self.assertEqual(next(f.value for f in after.slots[0].fields if f.key==key),value)
                    before=s.rockstar.container.plain;plain=after.rockstar.container.plain
                    allowed=set(range(f.offset,f.offset+4))
                    for begin,at in s.rockstar.container.checks:allowed.update(range(at+12,at+16))
                    self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,plain))))
                    self.assertEqual(len(out),len(raw));self.assertEqual(out[:s.rockstar.container.start],raw[:s.rockstar.container.start])

    def test_cash_precision_limits_and_skill_limits_are_enforced(self):
        s=Save(fixture('rdr2'),'rdr2')
        for value in (-1,21474836.48,float('nan'),True,1.005):
            with self.assertRaises(ValueError):s.patched({(0,'cash'):value})
        for value in (0,0.01,21474836.47):
            out=s.patched({(0,'cash'):value});self.assertFalse(Save(out,'rdr2').warnings)
        s=Save(fixture(),'gtav')
        for value in (-1,101):
            with self.assertRaises(ValueError):s.patched({(0,'character:0:stamina'):value})

    def test_duplicate_cash_entries_are_not_selected_by_first_match(self):
        s=Save(fixture(duplicate=True),'gtav')
        self.assertNotIn('character:0:total_cash',{f.key for f in s.slots[0].fields})
        with self.assertRaises(ValueError):s.patched({(0,'character:0:total_cash'):1})
        with self.assertRaisesRegex(FormatError,'uniquely identified'):Save(fixture('rdr2',duplicate=True),'rdr2')
        with self.assertRaisesRegex(FormatError,'uniquely identified'):Save(fixture(bad_type=True),'gtav')

    def test_corruption_requires_explicit_repair_and_malformed_layouts_are_rejected(self):
        raw=bytearray(fixture(encrypted=False));s=Save(raw,'gtav');raw[s.slots[0].fields[0].offset+3]^=1
        s=Save(raw,'gtav');self.assertTrue(s.warnings)
        with self.assertRaisesRegex(ValueError,'integrity repair'):s.patched({(0,'character:0:total_cash'):42})
        repaired=s.patched({(0,'character:0:total_cash'):42},repair_crc=True);self.assertFalse(Save(repaired,'gtav').warnings)
        for corrupt in (fixture()[:-1],fixture('rdr2'),bytes(len(fixture())),fixture()[:0x108]+bytes(len(fixture())-0x108)):
            with self.assertRaises(ValueError):Save(corrupt,'gtav')
        raw=bytearray(fixture(encrypted=False));at=raw.index(b'PMAP');struct.pack_into('>I',raw,at+20,0xffffffff)
        with self.assertRaisesRegex(ValueError,'outside PSIN'):Save(raw,'gtav')

    def test_names_discovery_and_direct_saving_keep_the_original_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            docs=Path(directory);paths=[]
            for folder,game,name in (('GTA V','gtav','SGTA50000'),('GTAV Enhanced','gtav','SGTA50015'),('Red Dead Redemption 2','rdr2','SRDR30001')):
                p=docs/'Rockstar Games'/folder/'Profiles/example'/name;p.parent.mkdir(parents=True);p.write_bytes(fixture(game));paths.append(p)
                p.with_name(name+'.bak').write_bytes(b'preserve')
                self.assertEqual(identify_game(p),game)
            with patch('core.documents_folder',return_value=docs):found=discover()
            for p in paths:self.assertIn((identify_game(p),p),found)
            self.assertFalse(any(p.suffix=='.bak' and p.parent in [v.parent for v in paths] for game,p in found))
            p=paths[0];raw=p.read_bytes();edited=Save(raw,'gtav').patched({(0,'character:0:total_cash'):500})
            replace_current(p,raw,edited);self.assertEqual(p.read_bytes(),edited)
            self.assertEqual({v.name for v in p.parent.iterdir()},{p.name,p.name+'.bak'})
            self.assertEqual(p.with_name(p.name+'.bak').read_bytes(),b'preserve')

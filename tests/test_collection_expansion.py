"""Synthetic regression checks for coupled collection operations."""
import hashlib
import struct
import unittest
import zlib
from core import Save,png_chunks
from test_core import variant,ror2
from test_kh_extra import archive,kh3_plain
from test_re5 import fixture as re5
from test_re6 import fixture as re6
from re5_save import decode,encode,checksum as checksum5
from re6_save import checksum as checksum6
from kh_pc import bbs_checksum
from kh_feature_tables import KH3_EQUIPMENT,KH3_ABILITY_NAMES,BBS_COMMAND_KINDS
from kh_extra_tables import KH3_ITEMS
from webfishing_features import ITEMS,COSMETICS,LURES


def fishing():
    fish=next(i for i,(n,c) in ITEMS.items() if c=='fish')
    raw=variant({'inventory':[{'id':fish,'quality':1,'ref':42,'size':1.5,'tags':['keep']},
                             {'id':fish,'quality':0,'ref':99,'size':2.0,'tags':[]}],
        'money':100,'loan_left':0,'bait_inv':{'worms':3,'squid':0},'bait_selected':'worms',
        'bait_unlocked':['','worms'],'max_bait':10,'level':1,'cosmetics_unlocked':['unknown_cosmetic'],
        'cosmetics_equipped':{'hat':'','accessory':[]},'lure_unlocked':[], 'lure_selected':'',
        'hotbar':{'1':42,'2':99},'locked_refs':[42,777], 'saved_aqua_fish':{'ref':42,'unknown':5},
        'journal':{'lake':{fish:{'count':3,'record':1.0,'quality':[0,4]}}},
        'quests':{'example':{'title':'Example','progress':2,'goal_amt':10,'reward':777}},
        'unknown':{'bytes':'must survive'}})
    return struct.pack('<I',len(raw))+raw

def field(save,key):return next(f for f in save.slots[0].fields if f.key==key)
def fix_png(raw):
    start,end=next((s,e) for n,s,e in png_chunks(raw,allow_sqex_crc=True) if n==b'sqEX')
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]));return bytes(raw)


class CollectionTests(unittest.TestCase):
    def test_webfishing_hotbar_can_widen_to_a_native_unsigned_32bit_item_ref(self):
        from webfishing_features import variant as encode_variant
        info=Save(fishing(),'webfishing').info;info['inventory'][1]['ref']=3000000000
        info['hotbar']={'1':0};payload=encode_variant(info);raw=struct.pack('<I',len(payload))+payload
        save=Save(raw,'webfishing');choice=save.webfishing.hotbar_choices['hotbar:1'][1].index(3000000000)
        output=save.patched({(0,'hotbar:1'):choice,(0,'remove_item:42'):1})
        check=Save(output,'webfishing');self.assertEqual(check.info['hotbar']['1'],3000000000)
        self.assertEqual(check.webfishing.reader.nodes[('hotbar','1')][1],'<q')

    def test_webfishing_simultaneous_array_growth_and_equipped_ownership(self):
        raw=fishing();save=Save(raw,'webfishing')
        self.assertEqual(save.patched({}),raw)
        hat=next(i for i,(n,c) in COSMETICS.items() if c=='hat')
        hat_key='equipped_cosmetic:hat';hat_choice=save.webfishing.selections[hat_key][1].index(hat)
        lure=next(iter(LURES));lure_choice=save.webfishing.selections['equipped_lure'][1].index(lure)
        identity=next(iter(ITEMS));quantity=save.webfishing.counts[identity]+2
        output=save.patched({(0,hat_key):hat_choice,(0,'equipped_lure'):lure_choice,
                            (0,'item_count:'+identity):quantity,(0,'bait:squid'):5})
        check=Save(output,'webfishing');info=check.info
        self.assertIn(hat,info['cosmetics_unlocked']);self.assertIn('unknown_cosmetic',info['cosmetics_unlocked'])
        self.assertEqual(info['cosmetics_equipped']['hat'],hat);self.assertIn(lure,info['lure_unlocked'])
        self.assertIn('squid',info['bait_unlocked']);self.assertEqual(info['bait_inv']['squid'],5)
        self.assertEqual(check.webfishing.counts[identity],quantity)
        refs=[i['ref'] for i in info['inventory']];self.assertEqual(len(set(refs)),len(refs))
        self.assertEqual(info['inventory'][0],save.info['inventory'][0]);self.assertEqual(info['unknown'],save.info['unknown'])
        self.assertEqual(struct.unpack_from('<I',output)[0],len(output)-4)

    def test_webfishing_deletion_retargets_hotbar_and_cleans_only_matching_refs(self):
        save=Save(fishing(),'webfishing');index=save.webfishing.hotbar_choices['hotbar:1'][1].index(99)
        output=save.patched({(0,'remove_item:42'):1,(0,'hotbar:1'):index,(0,'item_lock:99'):1})
        info=Save(output,'webfishing').info
        self.assertEqual([i['ref'] for i in info['inventory']],[99])
        self.assertEqual(info['hotbar'],{'1':99,'2':99});self.assertEqual(info['saved_aqua_fish']['ref'],0)
        self.assertEqual(info['saved_aqua_fish']['unknown'],5);self.assertEqual(info['locked_refs'],[777,99])
        with self.assertRaises(ValueError):save.patched({(0,'remove_item:99'):1,(0,'hotbar:1'):index})
        with self.assertRaises(ValueError):save.patched({(0,'remove_item:42'):1,(0,'item_ref:42:quality'):2})

    def test_webfishing_quality_membership_bait_requirement_and_quest_reward_preservation(self):
        save=Save(fishing(),'webfishing');fish=save.info['inventory'][0]['id']
        key=f'journal_quality:lake:{fish}:1'
        choice=save.webfishing.selections['equipped_bait'][1].index('squid')
        with self.assertRaises(ValueError):save.patched({(0,'equipped_bait'):choice})
        output=save.patched({(0,key):1,(0,'quest:example'):10,(0,'equipped_bait'):choice,(0,'bait:squid'):5})
        info=Save(output,'webfishing').info
        self.assertEqual(info['journal']['lake'][fish]['quality'],[0,4,1])
        self.assertEqual(info['quests']['example']['reward'],777);self.assertEqual(info['bait_selected'],'squid')

    def test_re5_high_figure_bits_and_reserved_flags_survive(self):
        plain=decode(re5());struct.pack_into('<Q',plain,0x138,1<<63)
        struct.pack_into('<I',plain,8,checksum5(plain));raw=bytes(encode(plain))
        output=Save(raw,'re5').patched({(0,'figure:44'):1,(0,'figure:0'):1})
        updated=decode(output);self.assertEqual(struct.unpack_from('<Q',updated,0x138)[0],(1<<63)|(1<<44)|1)
        allowed=set(range(8,12))|set(range(0x138,0x140))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(plain,updated))))

    def test_re6_emblems_preserve_nonzero_states_and_last_duo_record(self):
        raw=bytearray(re6());raw[2016]=0;struct.pack_into('<I',raw,8,checksum6(raw));save=Save(raw,'re6')
        with self.assertRaises(ValueError):save.patched({(0,'emblem:0:1'):0})
        key='merc_record:Duo:9:15:score';output=save.patched({(0,'emblem:0:0'):1,(0,key):123456})
        self.assertEqual(output[2016:2096],b'\x01'+b'\x03'*79)
        self.assertEqual(struct.unpack_from('<I',output,13768+9*432+15*12+4)[0],123456)
        self.assertFalse(Save(output,'re6').warnings)

    def test_ror2_additional_numeric_stats_keep_unknown_and_duplicate_xml(self):
        raw=ror2().replace(b'</stats>',b'<stat name="damage.CharacterBody">1.25</stat><stat name="opaque">KEEP</stat><stat name="unknownValue">55</stat></stats>')
        save=Save(raw,'ror2');output=save.patched({(0,'stat:unknownValue'):77,(0,'stat:damage.CharacterBody'):8.5})
        self.assertIn(b'<stat name="opaque">KEEP</stat>',output);self.assertIn(b'<stat name="unknownValue">55</stat>',output)
        self.assertEqual(field(Save(output,'ror2'),'stat:unknownValue').value,77)

    def test_kh3_ability_reserved_bits_and_equipment_inventory_acquisition(self):
        plain=bytearray(kh3_plain());identifier=next(iter(KH3_ABILITY_NAMES));offset=0x1880+0x160+identifier*4
        struct.pack_into('<I',plain,offset,0x8000000c)
        plain[0x1880+0x80]=1;plain[0x1880+0x81]=3;plain[0x1880+0x84]=1
        struct.pack_into('<I',plain,12,zlib.crc32(plain[16:0x94f4e8]));save=Save(plain,'kh3')
        armor_key='character:Sora:equipment:armor:0';options=save.kh3.characters.equipment[armor_key][1]
        armor=next(i for i,(n,c) in KH3_EQUIPMENT['Armor'].items() if (n,'Equipment') in save.kh3.characters.inventory_by_name)
        ability_key=f'character:Sora:ability:{identifier}'
        output=save.patched({(0,ability_key):2,(0,armor_key):options.index(armor)})
        self.assertEqual(struct.unpack_from('<I',output,offset)[0],0x8000000f)
        self.assertEqual(output[0x1880+0x99],4);self.assertEqual(output[0x1880+0x9c],1)
        item=save.kh3.characters.inventory_by_name[KH3_EQUIPMENT['Armor'][armor][0],'Equipment']
        self.assertEqual(output[0x8f4+item*2],1);self.assertTrue(output[0x8f5+item*2]&1)
        with self.assertRaises(ValueError):save.patched({(0,'character:Sora:active_weapon'):2})

    def test_bbs_multislot_decks_readonly_and_other_descriptor_words_preserved(self):
        raw=bytearray(archive('bbs',1));save=Save(raw,'bbs');r,length=save.extra_kh.records[0]
        command=next(i for i,(n,k) in BBS_COMMAND_KINDS.items() if k=='Attack')
        struct.pack_into('<H',raw,r+0x3498,command)
        struct.pack_into('<H',raw,r+0x3498+10,command)
        for deck in range(3):
            for i in range(19):struct.pack_into('<3H',raw,r+0x5a2c+deck*0xc4+i*6,0xffff,0x1234,0x5678)
        for i in (0,1):struct.pack_into('<H',raw,r+0x5a2c+i*6,0)
        struct.pack_into('<H',raw,r+0x5a2c+0xc4,1)
        struct.pack_into('<I',raw,r+12,bbs_checksum(raw[r:r+0x11e50]));raw=fix_png(raw);save=Save(raw,'bbs')
        self.assertTrue(field(save,'deck:0:0').readonly)
        with self.assertRaises(ValueError):save.patched({(0,'deck:0:0'):0})
        output=save.patched({(0,'deck:1:0'):0}) # remove single-slot command
        self.assertEqual(output[r+0x5a2c+0xc4+2:r+0x5a2c+0xc4+6],raw[r+0x5a2c+0xc4+2:r+0x5a2c+0xc4+6])
        self.assertEqual(struct.unpack_from('<H',output,r+0x5a2c+0xc4)[0],0xffff)

    def test_ddd_spirit_stats_preserve_identity_and_entire_other_records(self):
        raw=bytearray(archive('ddd',1));r,_=Save(raw,'ddd').extra_kh.records[0]
        raw[r+0x53a0]=1;raw[r+0x53a0+10:r+0x53a0+20]=b'KEEP NAME!'
        raw=fix_png(raw);output=Save(raw,'ddd').patched({(0,'spirit:0:attack'):200})
        allowed={r+0x53a0+61}
        start,end=next((s,e) for n,s,e in png_chunks(raw,allow_sqex_crc=True) if n==b'sqEX');allowed.update(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))


if __name__=='__main__':unittest.main()

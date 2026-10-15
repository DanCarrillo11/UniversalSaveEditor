"""Original artwork provenance, exact identity domains and byte preservation."""
import hashlib,json,struct,unittest,zipfile
from collections import Counter
from pathlib import Path
from core import Save,Field
from item_art import ROOT,catalogue,item_art,field_art_key
from re_engine_container import ReEngineEnvelope

COUNTS={'re2':27,'eldenring':794,'kh1':42,'kh2':135,'kh3':408,'bbs':47,'ddd':56,
        'recom':1123,'ror2':93,'webfishing':169,'re1_hd':25,'re7':141,'re5':19,'re3':76}

class MultiGameArtworkTests(unittest.TestCase):
    def test_packs_exact_hashes_dimensions_and_game_specific_keys(self):
        self.assertEqual(dict(Counter(g for g,i in catalogue())),COUNTS)
        manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
        source=next(s for s in manifest['sources'] if s.get('kind')=='Original multi-game image packs')
        for pack in source['packs']:
            path=ROOT/pack['path'];self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),pack['sha256'])
            with zipfile.ZipFile(path) as z:
                self.assertEqual(len(z.namelist()),pack['members'])
                for game,entries in manifest['games'].items():
                    for key,e in entries.items():
                        if e.get('archive')!=pack['path']:continue
                        raw=z.read(e['atlas']);self.assertTrue(raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'GIF89a'))
                        self.assertEqual(hashlib.sha256(raw).hexdigest(),e['sha256'])
                        dims=struct.unpack('<HH',raw[6:10]) if raw.startswith(b'GIF89a') else struct.unpack('>II',raw[16:24])
                        self.assertEqual(tuple(dims),tuple(e['rect'][2:]))
                        self.assertRegex(e['source_sha256'],r'^[a-f0-9]{64}$')
                        self.assertTrue(e['atlas'].startswith(game+'/'))
        self.assertIsNone(item_art('kh1','card:0'));self.assertIsNone(item_art('re7','bait:worms'))
        self.assertIsNone(item_art('ror2','unlock:Unknown.Mod'));self.assertIsNone(item_art('re7','item:../../../bad'))

    def test_equipment_uses_raw_ids_and_abilities_never_reuse_item_icons(self):
        from test_expansion import kh_fixture
        for game in ('kh1','kh2'):
            raw,*_=kh_fixture(game);save=Save(raw,game)
            equipment=next(f for f in save.slots[0].fields if f.art_choices and any(item_art(game,i) for i in f.art_choices))
            index=next(i for i,identifier in enumerate(equipment.art_choices) if item_art(game,identifier))
            key=field_art_key(equipment,index)
            self.assertEqual(key,equipment.art_choices[index])
            changes={(0,equipment.key):index}
            if game=='kh2':
                from kh2_items import ITEM_TO_STOCK
                changes[0,'inventory:'+str(ITEM_TO_STOCK[key])]=1
            output=save.patched(changes);parsed=Save(output,game)
            updated=next(f for f in parsed.slots[0].fields if f.key==equipment.key)
            self.assertEqual(field_art_key(updated),key);self.assertEqual(save.patched({}),raw)
            self.assertTrue(all(not f.art_choices and f.item_id is None for f in save.slots[0].fields if f.group=='Abilities'))
        self.assertIsNone(field_art_key(Field('test','Test',0,0,'',art_choices=(1,2)),999))

    def test_re7_string_identity_is_read_only_exact_and_same_object_only(self):
        from test_village import Writer
        from test_re_engine import wrap
        for identifiers in [('HandgunBullet',),('HandgunBullet','FirstAidDrink'),('../HandgunBullet',)]:
            w=Writer();fields=[('ItemDataID',15,i) for i in identifiers]
            fields += [('Num',7,('<i',30)),('SlotNo',7,('<i',5))]
            w.root(0x5e10ebe4,fields);raw=wrap(bytes(w.data[32:]),'re7');save=Save(raw,'re7')
            quantity=save.slots[0].fields[0]
            self.assertEqual(quantity.item_id,'item:HandgunBullet' if len(identifiers)==1 and not identifiers[0].startswith('.') else None)
            output=save.patched({(0,quantity.key):45})
            before=ReEngineEnvelope(raw,'re7').payload;after=ReEngineEnvelope(output,'re7').payload
            changed=set(range(quantity.offset-32,quantity.offset-32+4))
            self.assertTrue(all(a==b or i in changed for i,(a,b) in enumerate(zip(before,after))))
            self.assertEqual(Save(output,'re7').slots[0].fields[0].item_id,quantity.item_id)
            self.assertEqual(save.patched({}),raw)

    def test_webfishing_art_uses_saved_id_not_inventory_position(self):
        from test_core import variant
        payload=variant({'inventory':[{'id':'fish_lake_salmon','quality':1,'size':1.0}],
            'money':100,'bait_inv':{'worms':8},'bait_unlocked':['','worms'],'max_bait':10,'level':2})
        raw=struct.pack('<I',len(payload))+payload;save=Save(raw,'webfishing')
        fields={f.key:f for f in save.slots[0].fields}
        self.assertEqual(fields['item:0:size'].item_id,'item:fish_lake_salmon')
        self.assertEqual(item_art('webfishing',field_art_key(fields['bait:worms'])).name,'Worms')
        self.assertIsNotNone(item_art('webfishing',fields['item:0:size'].item_id))
        self.assertEqual(save.patched({}),raw)

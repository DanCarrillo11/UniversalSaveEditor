"""Original atlas mapping, conservative fallback and save-byte preservation."""
from pathlib import Path
import hashlib,json,struct,unittest
from unittest.mock import patch
from core import Save
from item_art import item_art,catalogue,ROOT
from re_engine_container import ReEngineEnvelope
from re_hashes import murmur32

def fixture():
    from test_village import Writer
    from test_re_engine import wrap
    w=Writer();entries=[]
    for ident,count in [(15,20),(2,3),(36,4),(9999,5)]:
        entries.append((0x2675722d,[('ItemId',1,('<i',ident)),('Count',7,('<i',count))]))
    w.root(0x41f30892,[('Items',-1,entries)])
    return wrap(bytes(w.data[32:]),'re2')

class ItemArtTests(unittest.TestCase):
    def test_manifest_provenance_and_item_rectangles(self):
        data=json.loads((ROOT/'manifest.json').read_text());source=data['sources'][0]
        self.assertEqual(sum(game=='re2' for game,identifier in catalogue()),27)
        self.assertEqual(source['revision'],'07db9f610553e6a95cee24aeac99cd1bc6c48e19')
        self.assertEqual(hashlib.sha256((ROOT/'re2/supplies.png').read_bytes()).hexdigest(),source['atlas_sha256'])
        self.assertEqual(item_art('re2',15).rect,(0,112,112,112))
        self.assertEqual(item_art('re2',2).rect,(1232,0,112,112))
        self.assertEqual(item_art('re2',36).rect,(1344,112,112,112))
        for (game,identifier),art in catalogue().items():
            if game!='re2':continue
            x,y,w,h=art.rect;self.assertLessEqual(x+w,2048);self.assertLessEqual(y+h,224)
            self.assertEqual(game,'re2');self.assertGreater(identifier,0)

    def test_unknown_and_other_editions_have_no_guessed_art(self):
        for game,identifier in [('re2',9999),('re2',12),('re2',0),('re2',-1),('re3',15),('re8',15),('re4_remake',15),('re4_2005',15),('re2',None),('re2',True)]:
            self.assertIsNone(item_art(game,identifier))

    def test_named_inventory_and_exact_identity_preservation(self):
        raw=fixture();save=Save(raw,'re2');fields=save.slots[0].fields
        self.assertEqual([f.item_id for f in fields],[15,2,36,9999])
        self.assertEqual([f.collection for f in fields],['Ammunition','Healing','Crafting materials','Unidentified items'])
        self.assertIn('Handgun Ammo',fields[0].label)
        self.assertIn('ID 9999',fields[-1].label)
        out=save.patched({(0,fields[0].key):55})
        before=ReEngineEnvelope(raw,'re2').payload;after=ReEngineEnvelope(out,'re2').payload
        changed=set(range(fields[0].offset-32,fields[0].offset-32+4))
        self.assertTrue(all(a==b for i,(a,b) in enumerate(zip(before,after)) if i not in changed))
        self.assertEqual([f.item_id for f in Save(out,'re2').slots[0].fields],[15,2,36,9999])
        self.assertEqual(Save(out,'re2').slots[0].fields[0].value,55)
        self.assertEqual(save.patched({}),raw)

    def test_missing_catalogue_keeps_safe_text_fallback(self):
        catalogue.cache_clear()
        try:
            with patch.object(Path,'read_text',side_effect=FileNotFoundError()):
                self.assertIsNone(item_art('re2',15))
                field=Save(fixture(),'re2').slots[0].fields[0]
                self.assertIn('Unidentified item',field.label)
                self.assertEqual(field.value,20)
        finally:catalogue.cache_clear()


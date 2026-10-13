"""Original Elden images, namespaced IDs and unchanged editing behavior."""
import hashlib,json,zipfile,unittest
from unittest.mock import patch
from core import Save
from item_art import ROOT,catalogue,item_art
from elden_items import GOODS
from elden_weapons import WEAPONS

class EldenArtworkTests(unittest.TestCase):
    def test_complete_existing_tables_and_original_png_hashes(self):
        manifest=json.loads((ROOT/'manifest.json').read_text());items=manifest['games']['eldenring']
        source=next(s for s in manifest['sources'] if s['game']=='eldenring')
        self.assertEqual(source['revision'],'ee1042d7a5bd933f91e6f8a0162e0e0237a1c4c5')
        self.assertEqual(set(map(int,items)),set(WEAPONS)|{0x40000000|i for i in GOODS})
        total=0
        for pack in source['packs']:
            archive=ROOT/pack['path']
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),pack['sha256'])
            with zipfile.ZipFile(archive) as z:
                total+=len(z.namelist())
                for identifier,entry in items.items():
                    if entry['archive']!=pack['path']:continue
                    raw=z.read(entry['atlas'])
                    self.assertTrue(raw.startswith(b'\x89PNG\r\n\x1a\n') or (raw.startswith(b'RIFF') and raw[8:12]==b'WEBP'))
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),entry['sha256'])
                    art=item_art('eldenring',int(identifier))
                    self.assertIsNotNone(art);self.assertEqual(art.name,entry['name'])
        self.assertEqual(total,794)

    def test_goods_and_weapon_ids_are_separate_and_unknowns_have_no_substitute(self):
        self.assertEqual(item_art('eldenring',0x40000000|190).name,'Rune Arc')
        self.assertEqual(item_art('eldenring',1000000).name,'Dagger')
        self.assertIsNone(item_art('eldenring',190))
        self.assertIsNone(item_art('re2',1000000))
        self.assertIsNone(item_art('eldenring',1000025)) # Adapter normalizes known bases.

    def test_inventory_storage_creation_and_weapons_keep_correct_icons_after_edits(self):
        from test_expansion import elden_ready
        raw=elden_ready(True);save=Save(raw,'eldenring');fields=save.slots[0].fields
        for prefix in ('inventory:','storage:','add_goods:','weapon:'):
            selected=[f for f in fields if f.key.startswith(prefix)]
            self.assertTrue(selected)
            self.assertTrue(all(item_art('eldenring',f.item_id) is not None for f in selected))
        weapon=next(f for f in fields if f.key.startswith('weapon:'))
        self.assertEqual(weapon.item_id,1000000)
        out=save.patched({(0,weapon.key):25});again=Save(out,'eldenring')
        updated=next(f for f in again.slots[0].fields if f.key==weapon.key)
        self.assertEqual(updated.item_id,1000000);self.assertEqual(updated.value,25)
        self.assertFalse(again.warnings);self.assertEqual(save.patched({}),raw)


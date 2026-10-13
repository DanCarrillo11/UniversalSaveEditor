"""Preview scope comes from actual adapters; examples never become writable saves."""
import json,unittest
from pathlib import Path
from editor_preview import EditorPreview
from catalog import BY_ID
from compatibility import EVIDENCE,coverage_label,compatibility_text
from editor_layout import organize_fields

class PreviewTests(unittest.TestCase):
    def test_every_game_has_read_only_offline_examples_and_category_navigation(self):
        self.assertEqual(set(BY_ID),set(EVIDENCE))
        data=json.loads(Path('assets/editor-previews.json').read_text())
        self.assertEqual(set(data['games']),set(BY_ID))
        for game in BY_ID:
            with self.subTest(game=game):
                preview=EditorPreview(game);self.assertTrue(preview.is_preview)
                for slot in preview.slots:
                    self.assertTrue(slot.fields)
                    self.assertEqual(len({f.key for f in slot.fields}),len(slot.fields))
                    self.assertTrue(all(f.readonly and f.offset==-1 for f in slot.fields))
                    self.assertTrue(all(f.minimum<=f.value<=f.maximum for f in slot.fields))
                    categories=organize_fields(game,slot.fields)
                    self.assertGreaterEqual(len(categories),1);self.assertLessEqual(len(categories),3)
                    total=sum(len(s.fields) for c in categories for s in c.sections)
                    self.assertEqual(total,len(slot.fields))
                for changes in ({},{(0,preview.slots[0].fields[0].key):1}):
                    with self.assertRaisesRegex(ValueError,'Preview only'):preview.patched(changes)
                self.assertIn(coverage_label(game),compatibility_text(game))
                self.assertIn('No editor is currently classified as full support',compatibility_text(game))

    def test_generated_examples_match_current_adapters_and_never_package_offsets_or_raw_saves(self):
        from tools.build_editor_previews import generate
        checked=json.loads(Path('assets/editor-previews.json').read_text())
        # JSON normalizes tuple choices to lists.
        self.assertEqual(checked,json.loads(json.dumps(generate())))
        for samples in checked['games'].values():
            for sample in samples:
                for entry in sample['fields']:
                    self.assertNotIn('offset',entry);self.assertNotIn('raw',entry)
        requiem=EditorPreview('re9')
        self.assertEqual(coverage_label('re9'),'Limited coverage')
        self.assertNotIn('Inventory',{c.name for c in organize_fields('re9',requiem.slots[0].fields)})
        self.assertEqual(len(EditorPreview('alice').slots),2)

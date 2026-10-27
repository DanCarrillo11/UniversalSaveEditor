"""Documentation cannot silently drift from the app's current support claims."""
from pathlib import Path
import unittest
from catalog import GAMES
from compatibility import EVIDENCE,coverage_label
from support_matrix import GAPS
from tools.build_support_docs import documents


class SupportMatrixTests(unittest.TestCase):
    def test_every_current_game_has_evidence_and_an_explicit_open_gate(self):
        keys={game.id for game in GAMES}
        self.assertEqual(keys,set(GAPS));self.assertEqual(keys,set(EVIDENCE))
        self.assertTrue(all(len(value)>35 for value in GAPS.values()))
        self.assertTrue(all(coverage_label(key)!='Full support' for key in keys))

    def test_shipped_coverage_and_completion_plan_match_runtime_sources(self):
        root=Path(__file__).resolve().parents[1]
        for path,expected in documents().items():
            with self.subTest(path=path):self.assertEqual((root/path).read_text(encoding='utf-8'),expected)

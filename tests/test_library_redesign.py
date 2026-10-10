"""Regression checks for the dark library and verified local backups."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from app import Window
from library_view import backup_bytes
from test_core import fishing


class LibraryRedesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.source = Path(self.folder.name) / 'webfishing_save_slot_0.sav'
        self.source.write_bytes(fishing())
        self.discovery = patch('app.discover', return_value=[('webfishing', self.source)])
        self.discovery.start()
        self.window = Window()

    def tearDown(self):
        self.window.edits = {}
        self.window.repair.setChecked(False)
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.discovery.stop()
        self.folder.cleanup()

    def test_library_browsing_and_editor_preservation(self):
        w = self.window
        self.assertEqual(w.visible_games[0], 'webfishing')
        self.assertEqual(w.preview_game_id, 'webfishing')
        w.search.setText('Rain')
        self.assertEqual(w.visible_games, ['ror2'])
        w.search.clear()
        w.set_filter('ready')
        self.assertEqual(len(w.visible_games), 3)
        w.show_library(False)  # clicked(bool) must not corrupt the mode.
        self.assertEqual(w.library_mode, 'library')
        w.load('webfishing', self.source)
        w.inputs[(0, 'money')].setText('246')
        w.show_library()
        w.show_editor()
        self.assertEqual(w.edits[(0, 'money')], '246')

    def test_manual_backup_is_exact_and_non_destructive(self):
        original = self.source.read_bytes()
        target = backup_bytes(self.source)
        self.assertNotEqual(target, self.source)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertTrue(target.name.endswith('.bak'))


if __name__ == '__main__':
    unittest.main()

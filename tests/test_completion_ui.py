"""New functional controls work through normal categories and read-only previews."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication,QComboBox
from app import Window
from core import Save
from test_re_engine import ACCOUNT
from test_requiem import fixture as requiem
from test_elden_talismans import fixture as elden


class CompletionUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        with patch('app.discover',return_value=[]):self.w=Window(settings=QSettings(str(self.root/'prefs.ini'),QSettings.Format.IniFormat))
        self.w.reduce_motion.setChecked(True);self.w.show()

    def tearDown(self):
        self.w.edits={};self.w.close();self.w.deleteLater();self.app.processEvents();self.temp.cleanup()

    def test_requiem_difficulty_stages_real_choice_and_preview_is_read_only(self):
        raw=requiem(difficulty=True);path=self.root/'data001Slot.bin';path.write_bytes(raw)
        save=Save(raw,'re9',account_id=ACCOUNT);self.w.display_save(save,path)
        field=next(f for f in save.slots[0].fields if f.group=='Difficulty')
        control=self.w.inputs[0,field.key];self.assertIsInstance(control,QComboBox)
        control.setCurrentIndex(3)
        self.assertEqual(self.w.validated_changes(),{(0,field.key):3});self.assertTrue(self.w.review_button.isEnabled())
        self.assertEqual(path.read_bytes(),raw)
        self.w.edits={};self.w.open_preview('re9')
        field=next(f for f in self.w.save.slots[0].fields if f.group=='Difficulty')
        self.w.inputs[0,field.key].setCurrentIndex(2)
        self.assertEqual(self.w.edits,{});self.assertFalse(self.w.review_button.isEnabled())

    def test_talisman_selection_is_in_equipment_and_survives_category_and_mode_changes(self):
        raw=elden();path=self.root/'ER0000.sl2';path.write_bytes(raw);self.w.load('eldenring',path)
        key=(0,'talisman_slot:0');l=self.w.save.elden_ring.talisman_loadouts[0]
        value=l.options[key[1]].index(0xa0000000|1010)
        self.w.go_to_change(key)
        self.w.inputs[key].setCurrentIndex(value);self.app.processEvents()
        self.assertTrue(self.w.inputs[key].isVisible())
        self.w.editor_search.setText('runes');self.w.go_to_change(key)
        self.w.advanced_options.setChecked(True);self.w.advanced_options.setChecked(False)
        self.assertEqual(self.w.validated_changes(),{key:value})
        self.w.go_to_change(key);self.assertEqual(self.w.inputs[key].currentIndex(),value)
        addition=next(f for f in self.w.save.slots[0].fields if f.key.startswith('add_talisman:'))
        self.w.go_to_change((0,addition.key));acquire=self.w.inputs[0,addition.key]
        self.assertEqual(acquire.text(),'Not acquired');acquire.setChecked(True)
        self.assertEqual(acquire.text(),'Acquire');self.assertIn((0,addition.key),self.w.validated_changes())
        self.assertEqual(path.read_bytes(),raw)

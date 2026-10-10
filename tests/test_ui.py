import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QLabel, QCheckBox
from app import Window
from core import Save
from test_core import fishing, kingdom, ror2

class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root=Path(self.temp.name)
        self.source=self.root/'webfishing_save_slot_0.sav'
        self.source.write_bytes(fishing())
        self.kh=self.root/'KHFM_WW.png';self.kh.write_bytes(kingdom())
        self.ror=self.root/'profile.xml';self.ror.write_bytes(ror2())
        self.discovery=patch('app.discover',return_value=[('webfishing',self.source),('ror2',self.ror),('kh1',self.kh)])
        self.discovery.start()
        self.window=Window()

    def tearDown(self):
        self.window.edits={};self.window.repair.setChecked(False)
        self.window.close();self.window.deleteLater();self.app.processEvents()
        self.discovery.stop();self.temp.cleanup()

    def test_search_and_compatibility(self):
        w=self.window
        descriptions={item.accessibleName():item.text() for item in w.findChildren(QLabel) if item.accessibleName().startswith('Editor features for ')}
        self.assertIn('Level and XP',descriptions['Editor features for WEBFISHING'])
        self.assertIn('Items',descriptions['Editor features for KINGDOM HEARTS'])
        self.assertIn('Editor in development',descriptions['Editor features for MAX PAYNE'])
        w.set_filter('ready');self.assertEqual(w.visible_games,['webfishing','ror2','kh1'])
        w.search.setText('XP');self.assertEqual(w.visible_games,['webfishing'])
        w.search.clear()
        w.set_filter('pending');self.assertEqual(len(w.visible_games),4)
        w.collection('KINGDOM HEARTS');self.assertEqual(len(w.visible_games),4)
        w.search.setText('not a game');self.assertEqual(w.visible_games,[])

    def test_invalid_values_block_export_and_navigation_preserves_edits(self):
        w=self.window;w.load('webfishing',self.source)
        entry=w.inputs[(0,'money')]
        entry.setText('999');self.assertTrue(w.review_button.isEnabled())
        w.show_library();w.show_editor();self.assertEqual(w.edits[(0,'money')],'999')
        for text in ('','-1','1.5','10000000','abc'):
            entry.setText(text);self.assertFalse(w.review_button.isEnabled())
        entry.setText('150');self.assertEqual(w.edits,{})

    def test_cancel_discard_keeps_current_file(self):
        w=self.window;w.load('webfishing',self.source)
        w.inputs[(0,'money')].setText('999')
        with patch('app.QMessageBox.question',return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(w.load('kh1',self.kh))
        self.assertEqual(w.path,self.source)
        self.assertEqual(w.edits[(0,'money')],'999')

    def test_multiple_slots_keep_their_own_changes(self):
        w=self.window;w.load('kh1',self.kh)
        w.inputs[(0,'munny')].setText('111')
        w.change_slot(1);w.inputs[(1,'munny')].setText('222')
        w.change_slot(0)
        self.assertEqual(w.inputs[(0,'munny')].text(),'111')
        self.assertEqual(w.validated_changes(),{(0,'munny'):111,(1,'munny'):222})

    def test_review_applies_webfishing_and_creates_backup(self):
        w=self.window;w.load('webfishing',self.source)
        w.inputs[(0,'money')].setText('987')
        clicked=[]
        def apply_dialog():
            dialog=self.app.activeModalWidget()
            for b in dialog.findChildren(QPushButton):
                if b.text()=='Apply to active save':
                    clicked.append(True);b.click();return
            dialog.reject()
        with patch('app.QMessageBox.information'):
            QTimer.singleShot(0,apply_dialog)
            w.review()
        self.assertTrue(clicked)
        self.assertEqual(Save(self.source.read_bytes(),'webfishing').slots[0].fields[0].value,987)
        self.assertEqual(next(self.root.glob('webfishing_save_slot_0.sav.original-*.bak')).read_bytes(),fishing())
        self.assertFalse(list(self.root.glob('*.edited.sav')))
        self.assertTrue(w.may_discard())

    def test_ror2_unlocks_use_checkboxes_and_batch_actions(self):
        w=self.window;w.load('ror2',self.ror)
        huntress=w.inputs[(0,'unlock:Characters.Huntress')]
        acolyte=w.inputs[(0,'unlock:Characters.Acolyte')]
        self.assertIsInstance(huntress,QCheckBox)
        self.assertTrue(huntress.isChecked());self.assertFalse(acolyte.isChecked())
        acolyte.setChecked(True);huntress.setChecked(False)
        self.assertEqual(w.validated_changes(),{
            (0,'unlock:Characters.Acolyte'):1,
            (0,'unlock:Characters.Huntress'):0,
        })
        characters=[field for field in w.save.slots[0].fields if field.group=='Characters']
        w.set_unlock_fields(characters,1)
        self.assertTrue(all(w.inputs[(0,field.key)].isChecked() for field in characters))

if __name__=='__main__':unittest.main()

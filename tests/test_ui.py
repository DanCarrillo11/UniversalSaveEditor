import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QLabel, QCheckBox, QLineEdit, QFrame, QComboBox
from app import Window
from core import Save
from catalog import BY_ID
from test_core import fishing, kingdom, kingdom2, alice, ror2
from test_alice import configuration

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
        w.set_filter('ready');self.assertEqual(w.visible_games,['alice','kh1','kh2','ror2','webfishing'])
        w.search.setText('XP');self.assertEqual(w.visible_games,['kh2','webfishing'])
        w.search.clear()
        w.set_filter('pending');self.assertEqual(len(w.visible_games),3)
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

    def test_clicking_compatible_cover_opens_detected_save(self):
        w=self.window
        w.activate_game(BY_ID['webfishing'])
        self.assertEqual(w.path,self.source)
        self.assertEqual(w.stack.currentIndex(),1)

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

    def test_manual_open_chooses_kh2_and_alice(self):
        for name,game,raw in [('KHIIFM_WW.png','kh2',kingdom2()),('PersistentData_PC.PSD','alice',alice())]:
            path=self.root/name;path.write_bytes(raw)
            self.window.open_path(path)
            self.assertEqual(self.window.save.game,game)
            self.assertEqual(self.window.stack.currentIndex(),1)

    def test_alice_apply_replaces_active_profile_and_keeps_backup(self):
        path=self.root/'PersistentData_PC.PSD';original=alice();path.write_bytes(original)
        w=self.window;w.open_path(path);w.inputs[(0,'teeth')].setText('1234')
        self.assertIn('apply',w.review_button.text())
        def apply_dialog():
            dialog=self.app.activeModalWidget()
            for item in dialog.findChildren(QPushButton):
                if item.text()=='Apply to active save':item.click();return
            dialog.reject()
        with patch('app.QMessageBox.information'):
            QTimer.singleShot(0,apply_dialog);w.review()
        self.assertEqual(Save(path.read_bytes(),'alice').slots[0].fields[0].value,1234)
        self.assertEqual(next(self.root.glob('*.bak')).read_bytes(),original)

    def test_inventory_search_keeps_pending_changes_and_editor_focus(self):
        w=self.window;w.load('kh1',self.kh)
        inventory=next(i for i in range(w.tabs.count()) if w.tabs.tabText(i)=='Items')
        w.tabs.setCurrentIndex(inventory);tab=w.tabs.currentWidget()
        entry=w.inputs[(0,'inventory:1')];entry.setText('20')
        search=tab.findChild(QLineEdit,'fieldSearch');search.setText('Potion')
        self.assertFalse(entry.parentWidget().isHidden())
        search.setText('no-such-item');self.assertTrue(entry.parentWidget().isHidden())
        search.clear();self.assertEqual(entry.text(),'20')
        w.focus_search();self.assertEqual(w.stack.currentIndex(),1)

    def test_alice_categories_use_selectors_toggles_and_restore(self):
        path=self.root/'PersistentData_PC.PSD';path.write_bytes(alice())
        w=self.window;w.load('alice',path)
        weapon=w.inputs[(0,'weapon:VorpalBlade')]
        memory=w.inputs[(0,'memory:1_M_2_Lizzie')]
        self.assertIsInstance(weapon,QComboBox);self.assertIsInstance(memory,QCheckBox)
        weapon.setCurrentIndex(4);memory.setChecked(True)
        self.assertEqual(w.validated_changes(),{(0,'weapon:VorpalBlade'):4,(0,'memory:1_M_2_Lizzie'):1})
        self.assertFalse(w.repair.isVisible());self.assertTrue(w.review_button.isEnabled())
        fields=[f for f in w.save.slots[0].fields if f.group=='Memories' and f.boolean]
        w.set_unlock_fields(fields,1)
        self.assertTrue(all(w.inputs[(0,f.key)].isChecked() for f in fields))
        w.set_unlock_fields(fields,None)
        self.assertEqual(w.validated_changes(),{(0,'weapon:VorpalBlade'):4})

    def test_alice_configuration_selection_review_and_apply(self):
        profile=self.root/'PersistentData_PC.PSD';profile.write_bytes(alice())
        config=self.root/'GameConfig_PC.CFG';original=configuration();config.write_bytes(original)
        w=self.window;w.files=[('alice',profile),('alice',config)]
        w.load('alice',profile)
        w.file_combo.setCurrentIndex(w.file_combo.findData(config))
        w.file_combo.activated.emit(w.file_combo.currentIndex())
        self.assertEqual(w.path,config)
        self.assertEqual(w.tabs.tabText(0),'Difficulty')
        w.inputs[(0,'current_difficulty')].setCurrentIndex(0)
        def apply_dialog():
            from PySide6.QtWidgets import QTextEdit
            dialog=self.app.activeModalWidget()
            review=dialog.findChild(QTextEdit).toPlainText()
            self.assertIn('Automatic related changes',review)
            self.assertIn('Lowest difficulty used: Normal → Easy',review)
            for item in dialog.findChildren(QPushButton):
                if item.text()=='Apply to active save':item.click();return
            dialog.reject()
        with patch('app.QMessageBox.information'):
            QTimer.singleShot(0,apply_dialog);w.review()
        self.assertEqual(profile.read_bytes(),alice())
        self.assertEqual(config.read_bytes()[16:],original[16:])
        self.assertEqual(next(self.root.glob('*.bak')).read_bytes(),original)

    def test_library_resizes_without_horizontal_scroll_or_clipped_cards(self):
        w=self.window;w.show()
        for width in (1100,1280,1536,1920,1100):
            w.resize(width,800);self.app.processEvents();w.reflow_library();self.app.processEvents()
            self.assertEqual(w.library_scroll.horizontalScrollBar().maximum(),0)
            available=w.library_scroll.viewport().width()
            for card in w.game_cards.values():
                self.assertLessEqual(card.geometry().right(),available)

if __name__=='__main__':unittest.main()

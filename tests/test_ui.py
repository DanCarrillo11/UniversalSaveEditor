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
import test_extended
from editor_layout import organize_fields

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
        w.platform_filter.setCurrentIndex(w.platform_filter.findData('steam'))
        self.assertEqual(set(w.visible_games),set(BY_ID))
        for card in w.game_cards.values():
            self.assertEqual(card.findChild(QLabel,'cardPlatform').text(),'Steam')
            self.assertFalse(card.findChild(QLabel,'platformIcon').pixmap().isNull())
        self.assertIn('Coming soon',w.game_cards['maxpayne'].toolTip())
        w.platform_filter.setCurrentIndex(0)
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

    def test_review_applies_webfishing_without_backup_or_copy(self):
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
        self.assertFalse(list(self.root.glob('*.bak')))
        self.assertFalse(list(self.root.glob('*.tmp')))
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

    def test_alice_apply_replaces_active_profile_without_backup(self):
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
        self.assertFalse(list(self.root.glob('*.bak')))

    def test_inventory_search_keeps_pending_changes_and_editor_focus(self):
        w=self.window;w.load('kh1',self.kh)
        inventory=next(i for i in range(w.tabs.count()) if w.tabs.tabText(i)=='Collection')
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
        self.assertEqual(w.tabs.tabText(0),'Progress')
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
        self.assertFalse(list(self.root.glob('*.bak')))

    def test_kh_apply_repairs_crc_in_original_file_and_keeps_selected_slot(self):
        w=self.window
        for game,path,raw in (
            ('kh1',self.kh,kingdom()),
            ('kh2',self.root/'KHIIFM_WW.png',kingdom2()),
        ):
            damaged=bytearray(raw);end=Save(raw,game).crc_regions[0][1]
            damaged[end]^=1;path.write_bytes(damaged)
            w.load(game,path)
            slot=1 if game=='kh1' else 0
            w.slot_combo.setCurrentIndex(slot);w.change_slot(slot)
            w.inputs[(slot,'munny')].setText('987')
            self.assertFalse(w.review_button.isEnabled())
            w.repair.setChecked(True);self.assertTrue(w.review_button.isEnabled())
            def apply_dialog():
                dialog=self.app.activeModalWidget()
                self.assertEqual(dialog.windowTitle(),'Review and apply')
                for item in dialog.findChildren(QPushButton):
                    if item.text()=='Apply to active save':item.click();return
                dialog.reject()
            with patch('app.QMessageBox.information'),patch('app.QFileDialog.getSaveFileName') as chooser:
                QTimer.singleShot(0,apply_dialog);w.review()
                chooser.assert_not_called()
            saved=Save(path.read_bytes(),game)
            self.assertEqual(saved.slots[slot].fields[0].value,987)
            if game=='kh1':self.assertEqual(saved.slots[0].fields[0].value,500)
            self.assertFalse(saved.warnings)
            self.assertEqual(w.slot_index,slot)
            self.assertEqual(w.inputs[(slot,'munny')].text(),'987')
            self.assertFalse(list(self.root.glob('*.edited.*')))
            self.assertFalse(list(self.root.glob('*.bak')))
            self.assertFalse(list(self.root.glob('*.tmp')))
            self.assertTrue(w.may_discard())

    def test_cancel_kh_review_does_not_write_any_files(self):
        w=self.window;w.load('kh1',self.kh)
        w.inputs[(0,'munny')].setText('987')
        before={path.name:path.read_bytes() for path in self.root.iterdir()}
        QTimer.singleShot(0,lambda:self.app.activeModalWidget().reject())
        w.review()
        self.assertEqual({path.name:path.read_bytes() for path in self.root.iterdir()},before)
        self.assertEqual(w.edits[(0,'munny')],'987')

    def test_kingdom_hearts_difficulty_uses_named_modes_per_slot(self):
        w=self.window
        for game,path,raw,choices in (
            ('kh1',self.kh,kingdom(),['Beginner','Final Mix (Standard)','Proud']),
            ('kh2',self.root/'KHIIFM_WW.png',kingdom2(),['Beginner','Standard','Proud','Critical']),
        ):
            w.edits={};path.write_bytes(raw);w.load(game,path)
            selector=w.inputs[(0,'difficulty')]
            self.assertIsInstance(selector,QComboBox)
            self.assertEqual([selector.itemText(i) for i in range(selector.count())],choices)
            selector.setCurrentIndex(len(choices)-1)
            self.assertEqual(w.validated_changes(),{(0,'difficulty'):len(choices)-1})
            if game=='kh1':
                w.slot_combo.setCurrentIndex(1)
                w.slot_combo.activated.emit(1)
                self.assertEqual(w.inputs[(1,'difficulty')].currentIndex(),0)
                w.slot_combo.setCurrentIndex(0)
                w.slot_combo.activated.emit(0)
                self.assertEqual(w.inputs[(0,'difficulty')].currentIndex(),2)

    def test_library_resizes_without_horizontal_scroll_or_clipped_cards(self):
        w=self.window;w.show()
        for width in (1100,1280,1536,1920,1100):
            w.resize(width,800);self.app.processEvents();w.reflow_library();self.app.processEvents()
            self.assertEqual(w.library_scroll.horizontalScrollBar().maximum(),0)
            available=w.library_scroll.viewport().width()
            for card in w.game_cards.values():
                self.assertLessEqual(card.geometry().right(),available)

    def test_game_categories_preserve_every_existing_control(self):
        fixtures=(
            ('kh1',kingdom(),['Progress','Characters','Collection']),
            ('kh2',kingdom2(),['Progress','Characters','Collection']),
            ('webfishing',test_extended.ExtendedTests().fixture(),['Progress','Equipment','Collection']),
            ('ror2',ror2(),['Progress','Unlocks','Records']),
            ('alice',alice(),['Progress','Character','Collection']),
            ('alice',configuration(),['Progress']),
        )
        for number,(game,raw,expected) in enumerate(fixtures):
            with self.subTest(game=game,number=number):
                path=self.root/f'categories-{number}.save';path.write_bytes(raw)
                w=self.window;w.load(game,path)
                self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],expected)
                original=w.save.slots[0].fields
                mapped=[field.key for category in organize_fields(game,original) for section in category.sections for field in section.fields]
                self.assertCountEqual(mapped,[field.key for field in original])
                self.assertEqual(len(mapped),len(set(mapped)))
                self.assertEqual(set(w.inputs),{(0,field.key) for field in original})

    def test_character_selector_and_slot_changes_keep_edits_and_view(self):
        w=self.window;w.load('kh1',self.kh)
        w.tabs.setCurrentIndex(1)
        selector=w.tabs.currentWidget().findChild(QComboBox,'sectionSelector')
        sora=w.inputs[(0,'0:strength')];donald=w.inputs[(0,'1:strength')]
        sora.setText('120')
        selector.setCurrentIndex(selector.findData('Donald'))
        self.assertTrue(sora.parentWidget().isHidden())
        self.assertFalse(donald.parentWidget().isHidden())
        donald.setText('115')
        w.change_slot(1)
        self.assertEqual(w.tabs.tabText(w.tabs.currentIndex()),'Characters')
        self.assertEqual(w.tabs.currentWidget().findChild(QComboBox,'sectionSelector').currentData(),'Donald')
        w.inputs[(1,'1:strength')].setText('110')
        w.change_slot(0)
        self.assertEqual(w.inputs[(0,'0:strength')].text(),'120')
        self.assertEqual(w.inputs[(0,'1:strength')].text(),'115')
        self.assertEqual(w.validated_changes(),{(0,'0:strength'):120,(0,'1:strength'):115,(1,'1:strength'):110})

    def test_drive_forms_are_inside_sora_and_hidden_for_companions(self):
        path=self.root/'KHIIFM_WW.png';path.write_bytes(kingdom2())
        w=self.window;w.load('kh2',path);w.tabs.setCurrentIndex(1)
        tab=w.tabs.currentWidget();selector=tab.findChild(QComboBox,'sectionSelector')
        form=w.inputs[(0,'form:0:level')]
        header=next(b for b in tab.findChildren(QPushButton,'sectionToggle') if 'Valor form' in b.text())
        self.assertFalse(header.isChecked())
        header.click();self.assertTrue(header.isChecked())
        form.setText('5')
        selector.setCurrentIndex(selector.findData('Donald'))
        self.assertTrue(form.parentWidget().isHidden())
        selector.setCurrentIndex(selector.findData('Sora'))
        self.assertFalse(form.parentWidget().isHidden())
        self.assertEqual(form.text(),'5')
        self.assertEqual(w.validated_changes(),{(0,'form:0:level'):5})

    def test_hidden_invalid_field_still_blocks_apply_and_section_actions_are_scoped(self):
        w=self.window;w.load('ror2',self.ror);w.tabs.setCurrentIndex(1)
        tab=w.tabs.currentWidget();selector=tab.findChild(QComboBox,'sectionSelector')
        selector.setCurrentIndex(selector.findData('Skills'))
        block=next(b for b in tab.findChildren(QFrame,'editorSection') if not b.isHidden())
        next(b for b in block.findChildren(QPushButton) if b.text()=='Unlock section').click()
        self.assertTrue(w.edits)
        self.assertTrue(all(key.startswith('unlock:Skills.') for index,key in w.edits))
        w.inputs[(0,'coins')].setText('-1')
        self.assertFalse(w.review_button.isEnabled())
        selector.setCurrentIndex(selector.findData('Characters'))
        self.assertFalse(w.review_button.isEnabled())

if __name__=='__main__':unittest.main()

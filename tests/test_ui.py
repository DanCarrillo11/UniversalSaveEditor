import os
import struct
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QTimer, QSettings, Qt, QObject, QEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QLabel, QCheckBox, QLineEdit, QFrame, QComboBox
from app import Window, platform_pixmap
from core import Save
from catalog import BY_ID
from test_core import fishing, kingdom, kingdom2, alice, ror2
from test_alice import configuration
import test_extended
from editor_layout import organize_fields
from editor_navigation import category_title

class InterfaceTests(unittest.TestCase):
    def test_visible_navigation_changes_characters_without_losing_edits(self):
        w=self.window;self.assertTrue(w.load('kh1',self.kh));w.show();w.tabs.setCurrentIndex(1);self.app.processEvents()
        page=w.tabs.currentWidget();navigation=page.navigation
        self.assertTrue(navigation.selector.isHidden())
        self.assertFalse(navigation.list.isHidden())
        self.assertTrue(w.workspace_sidebar.isHidden())
        w.inputs[0,'0:strength'].setText('120')
        QTest.mouseClick(navigation.character_buttons['Donald'],Qt.MouseButton.LeftButton)
        self.assertEqual(navigation.selector.currentData(),'Donald')
        self.assertTrue(navigation.character_buttons['Donald'].isChecked())
        QTest.mouseClick(navigation.character_buttons['Donald'],Qt.MouseButton.LeftButton)
        self.assertTrue(navigation.character_buttons['Donald'].isChecked())
        self.assertFalse(navigation.character_buttons['Sora'].isChecked())
        self.assertFalse(w.inputs[0,'1:strength'].parentWidget().isHidden())
        self.assertTrue(w.inputs[0,'0:strength'].parentWidget().isHidden())
        self.assertEqual(w.validated_changes(),{(0,'0:strength'):120})
        w.show_library();self.assertFalse(w.workspace_sidebar.isHidden())

    def test_global_search_reaches_other_categories_and_restores_section_navigation(self):
        w=self.window;w.load('kh1',self.kh);w.tabs.setCurrentIndex(0)
        w.inputs[0,'munny'].setText('1000')
        w.editor_search.setText('Potion');self.app.processEvents()
        self.assertEqual(w.tabs.tabText(w.tabs.currentIndex()),'Inventory')
        navigation=w.tabs.currentWidget().navigation
        self.assertEqual(navigation.heading.text(),'Search results')
        self.assertFalse(navigation.list.isEnabled())
        w.editor_search.clear();self.app.processEvents()
        self.assertTrue(navigation.list.isEnabled())
        self.assertEqual(navigation.heading.text(),navigation.active_section.name)
        w.focus_search();self.assertTrue(w.editor_search.hasFocus() or not w.isVisible())
        self.assertEqual(w.validated_changes(),{(0,'munny'):1000})

    def test_pending_change_dialog_is_read_only_and_footer_stays_visible(self):
        w=self.window;w.load('webfishing',self.source);original=self.source.read_bytes()
        w.show();w.resize(1100,720);self.app.processEvents()
        w.inputs[0,'money'].setText('1000');w.inputs[0,'max_bait'].setText('-1')
        self.assertFalse(w.review_button.isEnabled());self.assertTrue(w.changes_button.isEnabled())
        self.assertLessEqual(w.review_button.geometry().bottom(),w.review_button.parentWidget().height())
        inspected=[]
        def inspect():
            dialog=self.app.activeModalWidget();inspected.append(dialog.windowTitle())
            self.assertTrue(any('1000' in l.text() for l in dialog.findChildren(QLabel)))
            self.assertTrue(any(l.objectName()=='warning' for l in dialog.findChildren(QLabel)))
            dialog.accept()
        QTimer.singleShot(0,inspect);w.show_pending_changes()
        self.assertEqual(inspected,['Pending changes']);self.assertEqual(self.source.read_bytes(),original)
        w.restore_field((0,'max_bait'));self.assertTrue(w.review_button.isEnabled())

    def test_global_search_does_not_remain_hidden_after_reopening_a_save(self):
        w=self.window;w.load('kh1',self.kh);w.editor_search.setText('no-match-in-this-save')
        self.assertTrue(w.inputs[0,'munny'].parentWidget().isHidden())
        w.load('kh1',self.kh)
        self.assertEqual(w.editor_search.text(),'')
        self.assertFalse(w.inputs[0,'munny'].parentWidget().isHidden())

    def test_kh3_review_shows_synchronized_shortcuts_without_writing_on_cancel(self):
        import zlib
        from test_kh_extra import kh3_plain
        raw=bytearray(kh3_plain());struct.pack_into('<i',raw,0xbf50,29);struct.pack_into('<i',raw,0xbf20,29)
        struct.pack_into('<I',raw,12,zlib.crc32(raw[16:0x94f4e8]));raw=bytes(raw)
        path=self.root/'kh3-review.bin';path.write_bytes(raw);w=self.window;w.display_save(Save(raw,'kh3'),path)
        w.inputs[0,'magic:Fire'].setCurrentIndex(3);captured=[]
        def inspect_review():
            from PySide6.QtWidgets import QTextEdit
            dialog=self.app.activeModalWidget();captured.append(dialog.findChild(QTextEdit).toPlainText());dialog.reject()
        QTimer.singleShot(0,inspect_review);w.review()
        self.assertEqual(len(captured),1);self.assertIn('Automatic related changes',captured[0])
        self.assertIn('Set 1 · Circle: Fire → Firaga',captured[0]);self.assertEqual(path.read_bytes(),raw)
        self.assertEqual(w.validated_changes(),{(0,'magic:Fire'):3})
    def test_equipment_search_finds_selected_item_name_and_keeps_unrelated_edits(self):
        from test_expansion import kh_fixture
        raw,*_=kh_fixture('kh2');w=self.window;w.display_save(Save(raw,'kh2'),self.root/'equipment.png')
        w.show();self.app.processEvents()
        page=w.tabs.widget(next(i for i in range(w.tabs.count()) if w.tabs.tabText(i)=='Characters'))
        search=page.findChild(QLineEdit,'fieldSearch');key=(0,'character:0:item:0')
        entry=w.inputs[key];selected=entry.currentText();self.assertTrue(selected)
        w.inputs[0,'munny'].setText('1234');search.setText(selected);self.app.processEvents()
        self.assertFalse(entry.parentWidget().isHidden());self.assertEqual(w.validated_changes(),{(0,'munny'):1234})
        search.setText('not-a-real-equipped-item');self.app.processEvents();self.assertTrue(entry.parentWidget().isHidden())
        search.clear();self.app.processEvents()
        page.navigation.list.setCurrentRow(next(i for i in range(page.navigation.list.count()) if page.navigation.list.item(i).text()=='Equipment'))
        self.assertFalse(entry.parentWidget().isHidden())
        self.assertEqual(w.validated_changes(),{(0,'munny'):1234})

    def test_extreme_numeric_input_is_highlighted_and_review_is_disabled(self):
        w=self.window;w.load('webfishing',self.source);entry=w.inputs[0,'max_bait']
        entry.setText('9'*1000);self.app.processEvents()
        self.assertTrue(entry.property('invalid'));self.assertFalse(w.review_button.isEnabled())
        entry.setText('20');self.assertEqual(w.validated_changes(),{(0,'max_bait'):20})

    def test_large_profile_records_are_paged_and_keep_edits_when_search_changes(self):
        raw=('<UserProfile><coins>7</coins><stats>'+''.join(f'<stat name="killsAs.Example{i}">{i}</stat>' for i in range(2200))+'</stats></UserProfile>').encode()
        save=Save(raw,'ror2');w=self.window;w.display_save(save,self.root/'large.xml');self.app.processEvents()
        records=w.tabs.widget(next(i for i in range(w.tabs.count()) if w.tabs.tabText(i)=='Records'))
        pages=records.findChild(QComboBox,'recordPage');search=records.findChild(QLineEdit,'fieldSearch')
        self.assertEqual(pages.count(),22);self.assertLess(len(w.inputs),600)
        pages.setCurrentIndex(21);self.app.processEvents();self.assertIn((0,'stat:killsAs.Example2199'),w.inputs)
        search.setText('Example2199');self.app.processEvents();entry=w.inputs[0,'stat:killsAs.Example2199']
        entry.setText('9000');self.app.processEvents();self.assertIs(w.inputs[0,'stat:killsAs.Example2199'],entry)
        search.setText('Example1099');self.app.processEvents();w.inputs[0,'stat:killsAs.Example1099'].setText('8000')
        changes=w.validated_changes();self.assertEqual(changes,{(0,'stat:killsAs.Example2199'):9000,(0,'stat:killsAs.Example1099'):8000})
        output=save.patched(changes);self.assertIn(b'<stat name="killsAs.Example2199">9000</stat>',output)
        self.assertIn(b'<stat name="killsAs.Example1099">8000</stat>',output)

    def test_collection_bulk_actions_never_stage_item_removal_or_readonly_flags(self):
        from test_collection_expansion import fishing as collection_fixture
        raw=collection_fixture();save=Save(raw,'webfishing');w=self.window
        w.display_save(save,self.root/'collection.sav');self.app.processEvents()
        fields=[f for f in save.slots[0].fields if f.boolean]
        w.set_unlock_fields(fields,1)
        self.assertFalse(any(key.startswith(('remove_item:','equipped_accessory:')) for slot,key in w.edits))
        for f in fields:
            if f.key.startswith('remove_item:'):self.assertFalse(w.inputs[0,f.key].isChecked())

    def test_kh3_bulk_ability_actions_preserve_equipped_state_and_restore_originals(self):
        from test_kh_extra import kh3_plain
        import zlib
        raw=bytearray(kh3_plain());save=Save(raw,'kh3')
        keys=list(save.kh3.characters.abilities)[:2]
        struct.pack_into('<I',raw,save.kh3.characters.abilities[keys[1]],3)
        struct.pack_into('<I',raw,12,zlib.crc32(raw[16:0x94f4e8]));save=Save(raw,'kh3')
        w=self.window;w.display_save(save,self.root/'kh3.bin');self.app.processEvents()
        fields=[f for f in save.slots[0].fields if f.key in keys]
        w.set_ability_fields(fields,'learn')
        self.assertEqual([w.inputs[0,k].currentIndex() for k in keys],[1,2])
        w.set_ability_fields(fields,'equip');self.assertEqual([w.inputs[0,k].currentIndex() for k in keys],[2,2])
        w.set_ability_fields(fields,'unequip');self.assertEqual([w.inputs[0,k].currentIndex() for k in keys],[1,1])
        w.set_ability_fields(fields,'restore');self.assertEqual(w.edits,{})

    def test_requiem_upgrade_choices_disable_unsupported_tiers_but_preview_stays_browsable(self):
        from test_requiem import fixture
        from test_re_engine import ACCOUNT
        w=self.window;raw=fixture(parts=True);path=self.root/'requiem.bin';path.write_bytes(raw)
        save=Save(raw,'re9',account_id=ACCOUNT)
        w.display_save(save,path);self.app.processEvents()
        self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],['Progress','Characters','Inventory'])
        capacity=next(f for f in save.slots[0].fields if f.label=='Silver Tube Extension' and f.group=='Weapon upgrades')
        entry=w.inputs[0,capacity.key]
        self.assertFalse(entry.model().item(0).isEnabled());self.assertTrue(entry.model().item(2).isEnabled())
        entry.setCurrentIndex(2);self.assertEqual(w.validated_changes()[0,capacity.key],2)
        updated=Save(save.patched({(0,capacity.key):2}),'re9',account_id=ACCOUNT)
        w.edits={};w.display_save(updated,path);self.assertFalse(w.inputs[0,capacity.key].isEnabled())
        self.assertTrue(w.open_preview('re9'))
        upgrades=[f for f in w.save.slots[0].fields if f.group=='Weapon upgrades']
        for f in upgrades:
            control=w.inputs[0,f.key];self.assertTrue(control.isEnabled())
            self.assertTrue(all(control.model().item(i).isEnabled() for i in range(control.count())))
            control.setCurrentIndex(0)
        self.assertEqual(w.edits,{})

    def test_games_without_saves_open_read_only_previews_without_file_dialogs(self):
        w=self.window;w.files=[];history=list(w.recent_files)
        with patch('app.QFileDialog.getOpenFileName',side_effect=AssertionError('Preview must not require a file')):
            for game in BY_ID.values():
                with self.subTest(game=game.id):
                    w.activate_game(game);self.app.processEvents()
                    self.assertTrue(w.preview_mode);self.assertIsNone(w.path)
                    self.assertEqual(w.stack.currentIndex(),1)
                    self.assertIn('No save data found',w.warning.text())
                    self.assertIn('Not full support',w.coverage.text())
                    self.assertFalse(w.review_button.isEnabled());self.assertFalse(w.backup_button.isEnabled())
                    self.assertEqual(len(w.inputs),len(w.save.slots[0].fields))
                    self.assertTrue(all(control.isEnabled()==isinstance(control,QComboBox) for control in w.inputs.values()))
                    self.assertTrue(all(w.tabs.widget(i).navigation.list.count()>0 for i in range(w.tabs.count())))
                    self.assertTrue(all(w.tabs.widget(i).navigation.selector.isHidden() for i in range(w.tabs.count())))
                    for control in w.inputs.values():
                        if isinstance(control,QComboBox) and control.count()>1:control.setCurrentIndex((control.currentIndex()+1)%control.count())
                    self.assertEqual(w.edits,{})
                    w.review();w.open_backups()
                    self.assertEqual(w.recent_files,history);self.assertEqual(w.edits,{})
                    self.assertFalse(w.diagnostic(game.id).find('Save file size: 0')>=0)
                    if len(w.save.slots)>1:w.change_slot(1);self.app.processEvents()
                    self.assertEqual(w.recent_files,history)
                    w.resize(1400,900);self.assertTrue(w.save_steps.isHidden())
                    w.show_library()

    def test_preview_switching_to_real_save_restores_editing_and_preserves_discard_guard(self):
        w=self.window;w.files=[];w.select_game(BY_ID['webfishing'])
        self.assertTrue(w.preview_mode)
        with patch('app.replace_current') as replace:
            w.edits[(0,'money')]='500';w.review_button.setEnabled(True);w.review()
            replace.assert_not_called()
        w.edits={};self.assertTrue(w.load('webfishing',self.source))
        self.assertFalse(w.preview_mode);self.assertEqual(w.path,self.source)
        self.assertTrue(w.inputs[0,'money'].isEnabled());self.assertTrue(w.backup_button.isEnabled())
        self.assertFalse(w.file_combo.isHidden());self.assertNotIn('Preview only',w.warning.text())
        w.inputs[0,'money'].setText('200')
        with patch('app.QMessageBox.question',return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(w.open_preview('re9'))
        self.assertFalse(w.preview_mode);self.assertEqual(w.save.game,'webfishing')
        w.edits={};w.open_preview('webfishing');w.files=[('webfishing',self.source)]
        w.select_game(BY_ID['webfishing']);self.assertFalse(w.preview_mode)

    def test_opening_editors_never_shows_detached_icon_windows(self):
        class WindowShows(QObject):
            def __init__(self):
                super().__init__();self.detached=[]
            def eventFilter(self,widget,event):
                if event.type()==QEvent.Type.Show and isinstance(widget,QLabel) and widget.isWindow():
                    self.detached.append(widget.objectName())
                return False
        w=self.window;w.show();self.app.processEvents()
        watch=WindowShows();self.app.installEventFilter(watch)
        try:
            path=self.root/'KHIIFM_WW.png';path.write_bytes(kingdom2())
            for game,source in (('kh2',path),('ror2',self.ror)):
                self.assertTrue(w.load(game,source));self.app.processEvents()
                w.show_library();self.app.processEvents()
            self.assertEqual(watch.detached,[],'Icon labels must be parented before they become visible')
        finally:self.app.removeEventFilter(watch)

    def test_all_original_art_decodes_and_equipment_preview_tracks_choice_and_reset(self):
        from item_art import catalogue,item_pixmap
        for game,key in catalogue():
            self.assertFalse(item_pixmap(game,key).isNull(),f'{game}: {key}')
        from test_expansion import kh_fixture
        raw,*_=kh_fixture('kh2');path=self.root/'KHIIFM_WW.png';path.write_bytes(raw)
        w=self.window;self.assertTrue(w.load('kh2',path))
        field=next(f for f in w.save.slots[0].fields if f.art_choices and len([i for i in f.art_choices if not item_pixmap('kh2',i).isNull()])>=2)
        entry=w.inputs[0,field.key];sprite=entry._field_row.findChild(QLabel,'itemSprite')
        selected=[i for i,key in enumerate(field.art_choices) if not item_pixmap('kh2',key).isNull()][:2]
        entry.setCurrentIndex(selected[0]);first=sprite.pixmap().cacheKey()
        entry.setCurrentIndex(selected[1]);self.assertNotEqual(sprite.pixmap().cacheKey(),first)
        self.assertEqual(sprite.pixmap().cacheKey(),item_pixmap('kh2',field.art_choices[selected[1]]).cacheKey())
        w.restore_field((0,field.key));self.assertEqual(entry.currentIndex(),field.value)
        self.assertEqual(path.read_bytes(),raw)

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
        self.assertIn('Weapons',descriptions['Editor features for MAX PAYNE'])
        w.platform_filter.setCurrentIndex(w.platform_filter.findData('steam'))
        self.assertEqual(set(w.visible_games),set(BY_ID))
        for card in w.game_cards.values():
            self.assertEqual(card.findChild(QLabel,'cardPlatform').text(),'Steam')
            self.assertFalse(card.findChild(QLabel,'platformIcon').pixmap().isNull())
        self.assertIn('Experimental',w.game_cards['maxpayne'].toolTip())
        w.platform_filter.setCurrentIndex(0)
        w.set_filter('ready');self.assertEqual(set(w.visible_games),set(BY_ID))
        w.search.setText('XP');self.assertEqual(set(w.visible_games),{'bbs','ddd','kh1','kh2','kh3','recom','webfishing'})
        w.search.clear()
        w.set_filter('pending');self.assertEqual(len(w.visible_games),0)
        w.collection('KINGDOM HEARTS');self.assertEqual(len(w.visible_games),6)
        w.search.setText('not a game');self.assertEqual(w.visible_games,[])

    def test_changed_filter_updates_after_edit_and_individual_reset(self):
        w=self.window;w.load('webfishing',self.source)
        tab=w.tabs.widget(0);only=tab.findChild(QCheckBox,'changedOnly')
        money=w.inputs[(0,'money')];debt=w.inputs[(0,'loan_left')]
        only.setChecked(True)
        self.assertTrue(money.parentWidget().isHidden())
        money.setText('2000')
        self.assertFalse(money.parentWidget().isHidden())
        self.assertTrue(debt.parentWidget().isHidden())
        self.assertEqual(tab.findChild(QLabel,'fieldCount').text(),'1 field shown')
        money._reset_button.click()
        self.assertEqual(money.text(),'150');self.assertFalse(w.edits)
        self.assertTrue(money.parentWidget().isHidden())
        self.assertFalse(w.review_button.isEnabled())

    def test_invalid_value_has_inline_error_and_reset_clears_it(self):
        w=self.window;w.load('webfishing',self.source)
        entry=w.inputs[(0,'money')];entry.setText('abc')
        self.assertFalse(entry._error_label.isHidden())
        self.assertIn('whole number',entry._error_label.text())
        self.assertIn('Fix invalid values',w.statusBar().currentMessage())
        self.assertTrue(w.windowTitle().endswith('*'))
        entry._reset_button.click()
        self.assertTrue(entry._error_label.isHidden());self.assertFalse(entry._reset_button.isEnabled())
        self.assertIn('No pending changes',w.statusBar().currentMessage())
        self.assertFalse(w.windowTitle().endswith('*'))
        entry.setText('00150');self.assertFalse(w.edits)

    def test_summary_can_undo_a_change_in_another_slot(self):
        w=self.window;w.load('kh1',self.kh)
        w.inputs[(0,'munny')].setText('111');w.change_slot(1)
        w.inputs[(1,'munny')].setText('222')
        key=(0,'munny');w.restore_field(key)
        self.assertEqual(w.validated_changes(),{(1,'munny'):222})
        w.change_slot(0);self.assertNotEqual(w.inputs[key].text(),'111')

    def test_individual_reset_handles_choices_and_unlocks(self):
        w=self.window;w.load('kh1',self.kh)
        entry=w.inputs[(0,'difficulty')];original=entry.currentIndex()
        entry.setCurrentIndex((original+1)%entry.count());entry._reset_button.click()
        self.assertEqual(entry.currentIndex(),original);self.assertFalse(w.edits)
        w.load('ror2',self.ror)
        entry=next(e for e in w.inputs.values() if isinstance(e,QCheckBox))
        original=entry.isChecked();entry.setChecked(not original);entry._reset_button.click()
        self.assertEqual(entry.isChecked(),original);self.assertFalse(w.edits)

    def test_library_toolbar_and_details_fit_small_windows(self):
        w=self.window;w.show();w.resize(1100,720);self.app.processEvents();w.reflow_library();self.app.processEvents()
        self.assertGreater(w.search.width(),250)
        self.assertEqual(w.library_toolbar.getItemPosition(w.library_toolbar.indexOf(w.library_filter_controls))[0],1)
        self.assertEqual(w.detail_scroll.horizontalScrollBar().maximum(),0)
        w.search.setText('missing game')
        next(b for b in w.findChildren(QPushButton) if b.text()=='Reset filters').click()
        self.assertEqual(set(w.visible_games),set(BY_ID))
        w.resize(1536,960);self.app.processEvents();w.reflow_library()
        self.assertEqual(w.library_toolbar.getItemPosition(w.library_toolbar.indexOf(w.library_filter_controls))[0],0)

    def test_settings_only_store_local_interface_preferences(self):
        settings=QSettings(str(self.root/'preferences.ini'),QSettings.Format.IniFormat)
        w=Window(settings=settings);w.load('webfishing',self.source);w.resize(1280,800)
        w.close();w.deleteLater();self.app.processEvents()
        self.assertEqual(set(settings.allKeys()),{'window/geometry','files/lastDirectory','files/recent','files/rememberRecent','appearance/theme','appearance/reduceMotion','library/favorites'})
        self.assertEqual(settings.value('files/lastDirectory'),str(self.root))
        restored=Window(settings=settings)
        self.assertEqual(restored.last_directory,str(self.root));self.assertIsNone(restored.save)
        with patch('app.QFileDialog.getOpenFileName',return_value=('','')) as choose:
            restored.open_file()
        self.assertEqual(choose.call_args.args[2],str(self.root))
        restored.close();restored.deleteLater();self.app.processEvents()

    def test_compatibility_and_diagnostic_preview_are_available_without_personal_data(self):
        from PySide6.QtWidgets import QTextEdit
        w=self.window;w.load('webfishing',self.source);reports=[]
        def inspect_dialog():
            dialog=self.app.activeModalWidget()
            details=dialog.findChild(QTextEdit,'compatibilityDetails').toPlainText()
            self.assertIn('Money changes confirmed in-game',details)
            self.assertIn('Other editing features still need gameplay checks',details)
            preview=dialog.findChild(QTextEdit,'diagnosticPreview').toPlainText();reports.append(preview)
            self.assertNotIn(str(self.root),preview);self.assertNotIn(self.source.name,preview)
            next(b for b in dialog.findChildren(QPushButton) if b.text()=='Copy diagnostic').click()
            dialog.accept()
        QTimer.singleShot(0,inspect_dialog);w.open_support('webfishing')
        self.assertEqual(self.app.clipboard().text(),reports[0])

    def test_clear_recent_history_removes_shortcuts_and_preserves_save_and_edits(self):
        w=self.window;w.load('webfishing',self.source);original=self.source.read_bytes()
        w.inputs[(0,'money')].setText('1000');self.assertEqual(len(w.recent_files),1)
        def clear_dialog():
            dialog=self.app.activeModalWidget()
            next(b for b in dialog.findChildren(QPushButton) if b.text()=='Clear history').click()
            dialog.accept()
        QTimer.singleShot(0,clear_dialog);w.open_recents()
        self.assertFalse(w.recent_files);self.assertEqual(self.source.read_bytes(),original)
        self.assertEqual(w.validated_changes(),{(0,'money'):1000})

    def test_recent_reopen_restores_character_and_cancel_preserves_pending_changes(self):
        w=self.window;w.load('kh1',self.kh);w.change_slot(1)
        recent=dict(w.recent_files[0]);self.assertEqual(recent['slot'],1)
        w.load('webfishing',self.source);w.inputs[(0,'money')].setText('1000')
        with patch('app.QMessageBox.question',return_value=QMessageBox.StandardButton.Cancel):
            self.assertFalse(w.reopen_recent(recent))
        self.assertEqual(w.save.game,'webfishing');self.assertEqual(w.validated_changes(),{(0,'money'):1000})
        w.edits={};self.assertTrue(w.reopen_recent(recent));self.assertEqual(w.slot_index,1)

    def test_recent_location_is_only_replaced_after_a_successful_open(self):
        w=self.window;w.load('webfishing',self.source);entry=dict(w.recent_files[0])
        target=self.root/'relocated.sav';target.write_bytes(self.source.read_bytes())
        with patch.object(w,'show_problem') as problem:
            self.assertFalse(w.reopen_recent(entry,self.root/'missing.sav'));problem.assert_called_once()
        self.assertEqual(w.recent_files[0],entry)
        self.assertTrue(w.reopen_recent(entry,target));self.assertEqual(w.path,target)
        self.assertEqual(len(w.recent_files),1);self.assertTrue(self.source.is_file())

    def test_cover_reopens_manual_recent_save_when_discovery_has_no_file(self):
        path=self.root/'manual-alice.psd';path.write_bytes(alice())
        w=self.window;w.load('alice',path);w.load('webfishing',self.source)
        with patch('app.QFileDialog.getOpenFileName') as chooser:w.activate_game(BY_ID['alice'])
        chooser.assert_not_called();self.assertEqual(w.path,path);self.assertEqual(w.save.game,'alice')

    def test_disabling_recent_history_persists_and_does_not_remember_more_files(self):
        settings=QSettings(str(self.root/'history.ini'),QSettings.Format.IniFormat);w=Window(settings=settings)
        w.load('webfishing',self.source)
        def disable_dialog():
            dialog=self.app.activeModalWidget()
            next(item for item in dialog.findChildren(QCheckBox) if item.text()=='Remember recent saves').setChecked(False)
            dialog.accept()
        QTimer.singleShot(0,disable_dialog);w.open_recents();w.load('kh1',self.kh)
        self.assertFalse(w.recent_files);w.close();w.deleteLater();self.app.processEvents()
        restored=Window(settings=settings);self.assertFalse(restored.remember_recent);self.assertFalse(restored.recent_files)
        restored.close();restored.deleteLater();self.app.processEvents()

    def test_friendly_failed_load_preserves_open_save_and_copies_safe_diagnostic(self):
        w=self.window;w.load('webfishing',self.source);seen=[]
        def inspect_error():
            dialog=self.app.activeModalWidget();self.assertIsInstance(dialog,QMessageBox)
            seen.append(dialog.text());self.assertIn('moved, renamed or removed',dialog.text())
            next(b for b in dialog.buttons() if b.text()=='Copy diagnostic').click();dialog.close()
        QTimer.singleShot(0,inspect_error)
        self.assertFalse(w.load('webfishing',self.root/'PRIVATE_SAVE.sav'))
        report=self.app.clipboard().text();self.assertIn('file_missing',report)
        self.assertNotIn('PRIVATE_SAVE',report);self.assertNotIn(str(self.root),report)
        self.assertEqual(w.path,self.source);self.assertEqual(len(w.recent_files),1)

    def test_favorite_star_click_does_not_open_or_modify_save(self):
        w=self.window;w.show();self.app.processEvents()
        original=self.source.read_bytes()
        star=w.game_cards['webfishing'].favorite_button
        QTest.mouseClick(star,Qt.MouseButton.LeftButton)
        self.assertEqual(w.favorites,{'webfishing'})
        self.assertIsNone(w.save);self.assertEqual(w.stack.currentIndex(),0)
        self.assertEqual(w.visible_games[0],'webfishing')
        self.assertIn('Remove from favorites',w.game_cards['webfishing'].favorite_button.accessibleName())
        # Clicking the cover still opens the file; only the star is independent.
        card=w.game_cards['webfishing'];self.app.processEvents()
        QTest.mouseClick(card.artwork,Qt.MouseButton.LeftButton,pos=card.artwork.rect().center())
        self.assertEqual(w.path,self.source);self.assertEqual(w.stack.currentIndex(),1)
        self.assertEqual(self.source.read_bytes(),original)

    def test_favorites_are_first_under_sort_and_search_and_have_empty_state(self):
        w=self.window;w.toggle_favorite('webfishing');w.toggle_favorite('kh1')
        w.sort_filter.setCurrentIndex(w.sort_filter.findData('za'))
        self.assertEqual(w.visible_games[:2],['webfishing','kh1'])
        w.search.setText('KINGDOM HEARTS')
        self.assertEqual(w.visible_games[0],'kh1')
        w.favorites_nav.click()
        self.assertEqual(set(w.visible_games),{'kh1','webfishing'})
        self.assertEqual(w.search.text(),'');self.assertTrue(w.favorites_nav.isChecked())
        w.game_cards['kh1'].favorite_button.click();w.game_cards['webfishing'].favorite_button.click()
        self.assertEqual(w.visible_games,[])
        self.assertTrue(any(l.text()=='No favorites yet' for l in w.findChildren(QLabel)))
        next(b for b in w.findChildren(QPushButton) if b.text()=='Browse games').click()
        self.assertEqual(set(w.visible_games),set(BY_ID));self.assertFalse(w.favorites_only)

    def test_favorites_and_motion_preferences_survive_restart(self):
        settings=QSettings(str(self.root/'favorites.ini'),QSettings.Format.IniFormat)
        settings.setValue('library/favorites',['kh2','not-a-game','kh2'])
        w=Window(settings=settings)
        self.assertEqual(w.favorites,{'kh2'})
        w.toggle_favorite('webfishing');w.reduce_motion.setChecked(True)
        w.close();w.deleteLater();self.app.processEvents()
        restored=Window(settings=settings)
        self.assertEqual(restored.favorites,{'kh2','webfishing'})
        self.assertTrue(restored.reduce_motion.isChecked());self.assertFalse(restored.transition.enabled)
        self.assertIsNone(restored.save)
        restored.close();restored.deleteLater();self.app.processEvents()

    def test_keyboard_favorite_toggle_preserves_focus_and_scroll(self):
        w=self.window;w.show();w.resize(1100,720);self.app.processEvents();w.reflow_library();self.app.processEvents()
        w.toggle_favorite('webfishing')
        star=w.game_cards['webfishing'].favorite_button;star.setFocus()
        position=w.library_scroll.verticalScrollBar().value()
        QTest.keyClick(star,Qt.Key.Key_Space);self.app.processEvents()
        self.assertFalse(w.favorites)
        self.assertTrue(w.game_cards['webfishing'].favorite_button.hasFocus())
        self.assertEqual(w.library_scroll.verticalScrollBar().value(),position)
        self.assertIsNone(w.save)

    def test_transitions_are_interruptible_and_keep_inputs_and_edits(self):
        w=self.window;w.show();self.app.processEvents();original=self.source.read_bytes()
        w.load('webfishing',self.source)
        self.assertIsNotNone(w.stack.currentWidget().graphicsEffect())
        entry=w.inputs[(0,'money')];entry.setText('2000')
        for _ in range(3):w.show_library();w.show_editor()
        for _ in range(40):
            if w.transition.animation is None:break
            QTest.qWait(50)
        self.assertIsNone(w.transition.animation)
        self.assertTrue(all(w.stack.widget(i).graphicsEffect() is None for i in range(w.stack.count())))
        self.assertIs(w.inputs[(0,'money')],entry)
        self.assertEqual(w.validated_changes(),{(0,'money'):2000})
        w.show_library();w.reduce_motion.setChecked(True)
        self.assertIsNone(w.transition.animation)
        w.show_editor();self.assertIsNone(w.stack.currentWidget().graphicsEffect())
        self.assertEqual(self.source.read_bytes(),original)

    def test_cover_highlight_keeps_geometry_and_reduced_motion_stops_animation(self):
        w=self.window;w.show();QTest.qWait(150);w.reflow_library();self.app.processEvents()
        art=w.game_cards['kh1'].artwork
        geometry=art.geometry();pixmap=art.pixmap.cacheKey()
        art.set_hovered(True)
        for _ in range(40):
            if art.hover_animation.state()==art.hover_animation.State.Stopped:break
            QTest.qWait(50)
        self.assertAlmostEqual(art.get_highlight(),0.08)
        art.set_hovered(False)
        for _ in range(40):
            if art.hover_animation.state()==art.hover_animation.State.Stopped:break
            QTest.qWait(50)
        self.assertEqual(art.get_highlight(),0)
        self.assertEqual(art.geometry(),geometry);self.assertEqual(art.pixmap.cacheKey(),pixmap)
        art.set_hovered(True);w.reduce_motion.setChecked(True)
        self.assertEqual(art.hover_animation.state(),art.hover_animation.State.Stopped)

    def test_information_notes_do_not_request_integrity_repair(self):
        w=self.window;path=self.root/'alice-profile.save';path.write_bytes(alice())
        w.load('alice',path)
        self.assertTrue(w.warning.isHidden());self.assertFalse(w.editor_notes.isHidden())
        self.assertTrue(w.repair.isHidden());self.assertTrue(w.slot_combo.isHidden())
        w.show();w.resize(1100,720);self.app.processEvents()
        self.assertTrue(w.save_steps.isHidden());self.assertTrue(w.summary_description.isHidden())
        self.assertGreaterEqual(w.review_button.height(),35)
        self.assertGreaterEqual(w.reset_button.height(),35)

    def test_save_row_opens_its_file_directly(self):
        w=self.window;w.preview_game(BY_ID['webfishing'])
        link=next(b for b in w.detail.findChildren(QPushButton,'saveLink') if b.text()==self.source.name)
        link.click();self.assertEqual(w.path,self.source);self.assertEqual(w.stack.currentIndex(),1)

    def test_switching_appearance_preserves_pending_edits_and_navigation(self):
        from appearance import stylesheet, PALETTES
        w=self.window;w.load('webfishing',self.source)
        w.show();self.app.processEvents()
        entry=w.inputs[(0,'money')];entry.setText('2000')
        original=self.source.read_bytes()
        for theme in ('dark','light'):
            w.appearance_button.click()
            self.assertEqual(w.theme,theme)
            self.assertIs(w.inputs[(0,'money')],entry)
            self.assertEqual(w.validated_changes(),{(0,'money'):2000})
            self.assertEqual(w.stack.currentIndex(),1)
            self.assertNotRegex(stylesheet(theme),r'@[A-Za-z]+@')
            self.app.processEvents()
            image=w.review_button.grab().toImage()
            self.assertIn(image.pixelColor(image.width()//2,4).name().upper(),(PALETTES[theme]['accent'],PALETTES[theme]['accentHover']))
            self.assertEqual(self.source.read_bytes(),original)

    def test_appearance_is_restored_and_unknown_preferences_fall_back(self):
        settings=QSettings(str(self.root/'appearance.ini'),QSettings.Format.IniFormat)
        settings.setValue('appearance/theme','dark')
        window=Window(settings=settings)
        self.assertEqual(window.theme,'dark');self.assertEqual(window.appearance_button.text(),'Light mode')
        window.toggle_theme();window.close();window.deleteLater();self.app.processEvents()
        self.assertEqual(settings.value('appearance/theme'),'light')
        settings.setValue('appearance/theme','unknown')
        window=Window(settings=settings)
        self.assertEqual(window.theme,'light')
        window.close();window.deleteLater();self.app.processEvents()

    def test_platform_logo_is_complete_at_fractional_screen_scales(self):
        for scale in (1,1.25,1.5,1.75,2):
            with self.subTest(scale=scale):
                pixmap=platform_pixmap('steam',scale=scale)
                image=pixmap.toImage();edge=image.width()-1;middle=image.width()//2
                # The full round logo has transparent corners and reaches the
                # top, right, and bottom of its own bounds at every screen scale.
                self.assertLess(image.pixelColor(edge,edge).alpha(),10)
                for x,y in ((middle,0),(edge,middle),(middle,edge)):
                    self.assertGreater(image.pixelColor(x,y).alpha(),150)

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

    def test_re4_uhd_without_inventory_opens_relevant_categories_and_updates_mode_mirrors(self):
        from test_re4_uhd import fixture
        path=self.root/'savegame00.sav';original=fixture();path.write_bytes(original)
        w=self.window;w.open_path(path)
        self.assertEqual(w.save.game,'re4_2005')
        self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],['Progress','Characters'])
        w.inputs[(0,'money')].setText('55555');w.inputs[(0,'difficulty')].setCurrentIndex(3)
        output=w.save.patched(w.validated_changes())
        self.assertFalse(Save(output,'re4_2005').warnings)
        self.assertEqual(path.read_bytes(),original)
        w.show_favorites();w.toggle_favorite('re4_2005')
        self.assertEqual(w.validated_changes(),{(0,'money'):55555,(0,'difficulty'):3})
        w.show_editor();self.assertEqual(w.stack.currentIndex(),1)

    def test_party_equipment_and_abilities_are_inside_character_selector(self):
        from test_expansion import kh_fixture
        raw,*_=kh_fixture('kh2');path=self.root/'KHIIFM_WW.png';path.write_bytes(raw)
        w=self.window;w.load('kh2',path)
        selectors=[entry for entry in w.findChildren(QComboBox) if entry.objectName()=='sectionSelector']
        self.assertTrue(any(entry.findText('Riku')>=0 for entry in selectors))
        key=(0,'character:0:ability:0');entry=w.inputs[key]
        entry.setCurrentIndex(entry.findText('Guard · Unequipped'))
        output=w.save.patched(w.validated_changes())
        field=next(f for f in w.save.slots[0].fields if f.key==key[1])
        self.assertEqual(struct.unpack_from('<H',output,field.offset)[0],82)
        self.assertEqual(path.read_bytes(),raw)
        self.assertEqual(w.tabs.count(),3)

    def test_elden_add_item_and_re4_upgrade_controls_reparse_without_writing_source(self):
        from test_expansion import elden_ready,re4_ready
        for game,name,raw,key,value in (('eldenring','ER0000.sl2',elden_ready(),'add_goods:190',5),
                                         ('re4_2005','savegame00.sav',re4_ready(),'weapon:0:0',7)):
            path=self.root/name;path.write_bytes(raw);w=self.window;w.load(game,path)
            w.inputs[(0,key)].setText(str(value))
            output=w.save.patched(w.validated_changes());parsed=Save(output,game)
            self.assertFalse(parsed.warnings);self.assertEqual(path.read_bytes(),raw)
            self.assertEqual(w.tabs.count(),3)
            w.edits.clear()

    def test_re6_skill_dropdown_preserves_numeric_encoding_and_other_sets(self):
        from test_re6 import fixture
        path=self.root/'savedata.bin';raw=fixture();path.write_bytes(raw)
        w=self.window;w.load('re6',path);key=(0,'skill:Campaign skills:0')
        entry=w.inputs[key];entry.setCurrentIndex(entry.findText('Firearm · Level 3'))
        output=w.save.patched(w.validated_changes())
        self.assertEqual(struct.unpack_from('<I',output,1920)[0],3)
        self.assertEqual(output[2344:2440],raw[2344:2440])

    def test_elden_ring_categories_calculated_fields_and_character_edits(self):
        from test_elden_ring import fixture
        path=self.root/'ER0000.sl2';original=fixture(character_versions=(250,261));path.write_bytes(original)
        w=self.window;w.open_path(path)
        self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],['Progress','Character','Inventory'])
        self.assertTrue(w.inputs[(0,'level')].isReadOnly())
        self.assertTrue(w.inputs[(0,'runes_memory')].isReadOnly())
        self.assertTrue(w.inputs[(0,'level')]._reset_button.isHidden())
        w.inputs[(0,'runes')].setText('900');w.inputs[(0,'vigor')].setText('20')
        w.change_slot(1);w.inputs[(1,'storage:0')].setText('77')
        w.change_slot(0)
        self.assertEqual(w.validated_changes(),{(0,'runes'):900,(0,'vigor'):20,(1,'storage:0'):77})
        self.assertEqual(path.read_bytes(),original)

    def test_elden_ring_review_shows_automatic_changes_and_applies_in_place(self):
        from test_elden_ring import fixture
        from PySide6.QtWidgets import QTextEdit
        path=self.root/'ER0000.sl2';path.write_bytes(fixture())
        w=self.window;w.load('eldenring',path)
        w.inputs[(0,'runes')].setText('900');w.inputs[(0,'vigor')].setText('20')
        reviews=[]
        def apply_dialog():
            dialog=self.app.activeModalWidget();reviews.append(dialog.findChild(QTextEdit).toPlainText())
            for control in dialog.findChildren(QPushButton):
                if control.text()=='Apply to active save':control.click();return
            dialog.reject()
        with patch('app.QMessageBox.information'):
            QTimer.singleShot(0,apply_dialog);w.review()
        self.assertIn('Automatic related changes',reviews[0])
        self.assertIn('Level: 9 → 14',reviews[0])
        self.assertIn('Lifetime runes: 1200 → 1600',reviews[0])
        self.assertEqual(w.inputs[(0,'level')].text(),'14')
        self.assertEqual(w.inputs[(0,'runes_memory')].text(),'1600')
        self.assertFalse(w.save.warnings)
        self.assertFalse(list(self.root.glob('*.bak')))
        self.assertFalse(list(self.root.glob('*.edited*')))

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
        self.assertEqual(w.review_button.text(),'Save changes')
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
        inventory=next(i for i in range(w.tabs.count()) if w.tabs.tabText(i)==category_title(w.save.game,'Collection'))
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
                self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],[category_title(game,name) for name in expected])
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
        navigation=tab.navigation.list
        navigation.setCurrentRow(next(i for i in range(navigation.count()) if navigation.item(i).text()=='Valor form'))
        self.assertTrue(header.isChecked())
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

    def test_new_game_editors_render_every_field_in_categories(self):
        from test_kh_extra import archive
        from test_maxpayne import inventory_fixture
        w=self.window
        for game in ('recom','bbs','ddd','maxpayne'):
            with self.subTest(game=game):
                path=self.root/(game+'.mps' if game=='maxpayne' else game+'.png')
                path.write_bytes(inventory_fixture() if game=='maxpayne' else archive(game))
                self.assertTrue(w.load(game,path))
                self.assertLessEqual(w.tabs.count(),3)
                self.assertEqual(len(w.inputs),len(w.save.slots[0].fields))
                key='ammo:3' if game=='maxpayne' else 'moogle_points' if game=='recom' else 'munny'
                w.inputs[0,key].setText('150')
                updated=w.save.patched(w.validated_changes())
                self.assertEqual(next(f.value for f in Save(updated,game).slots[0].fields if f.key==key),150)
                w.edits={}

    def test_elden_original_sprites_cover_inventory_storage_creation_and_weapon_upgrades(self):
        from test_expansion import elden_ready
        from item_art import item_pixmap
        raw=elden_ready(True);path=self.root/'ER0000.sl2';path.write_bytes(raw)
        w=self.window;self.assertTrue(w.load('eldenring',path))
        sprites=w.findChildren(QLabel,'itemSprite');self.assertGreater(len(sprites),250)
        self.assertTrue(all(not s.pixmap().isNull() for s in sprites))
        self.assertEqual(item_pixmap('eldenring',1000000).size().width(),64)
        self.assertTrue(item_pixmap('eldenring',0x40000000|190).width()<=64)
        self.assertTrue(item_pixmap('eldenring',190).isNull())
        from elden_items import GOODS
        from item_art import catalogue
        for game,identifier in catalogue():
            if game=='eldenring':self.assertFalse(item_pixmap(game,identifier).isNull(),str(identifier))
        field=next(f for f in w.save.slots[0].fields if f.key.startswith('weapon:'))
        w.inputs[(0,field.key)].setText('25')
        out=w.save.patched(w.validated_changes())
        self.assertEqual(next(f.value for f in Save(out,'eldenring').slots[0].fields if f.key==field.key),25)
        self.assertEqual(path.read_bytes(),raw)
        for theme in ('light','dark'):
            if w.theme!=theme:w.toggle_theme()
            self.assertTrue(all(not s.pixmap().isNull() for s in sprites))

    def test_original_item_sprites_search_and_editing(self):
        from test_item_art import fixture
        from item_art import item_pixmap
        raw=fixture();path=self.root/'data001Slot.bin';path.write_bytes(raw)
        w=self.window;self.assertTrue(w.load('re2',path))
        sprites=w.findChildren(QLabel,'itemSprite');self.assertEqual(len(sprites),3)
        self.assertTrue(all(not s.pixmap().isNull() for s in sprites))
        search=w.tabs.currentWidget().findChild(QLineEdit,'fieldSearch')
        search.setText('Handgun Ammo')
        self.assertFalse(w.inputs[(0,w.save.slots[0].fields[0].key)]._field_row.isHidden())
        self.assertTrue(w.inputs[(0,w.save.slots[0].fields[1].key)]._field_row.isHidden())
        search.clear()
        self.assertTrue(item_pixmap('re3',15).isNull())
        self.assertTrue(item_pixmap('re2',9999).isNull())
        field=w.save.slots[0].fields[0]
        w.inputs[(0,field.key)].setText('55')
        out=w.save.patched(w.validated_changes())
        self.assertEqual(Save(out,'re2').slots[0].fields[0].value,55)
        self.assertEqual(path.read_bytes(),raw)
        for theme in ('light','dark'):
            if w.theme!=theme:w.toggle_theme()
            self.assertTrue(all(not s.pixmap().isNull() for s in sprites))

    def test_village_editor_cover_context_flags_and_readonly_items(self):
        from test_village import fixture
        raw=fixture();path=self.root/'data001Slot.bin';path.write_bytes(raw)
        w=self.window;self.assertFalse(w.game_cards['re8'].artwork.pixmap.isNull())
        w.open_path(path)
        self.assertEqual(w.save.game,'re8')
        self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],['Progress','Character','Inventory'])
        money=next(f for f in w.save.slots[0].fields if f.label=='Lei')
        cp=next(f for f in w.save.slots[0].fields if f.label=='Challenge points (CP)')
        single=next(f for f in w.save.slots[0].fields if f.readonly)
        self.assertTrue(w.inputs[(0,single.key)].isReadOnly())
        w.inputs[(0,money.key)].setText('100000');w.inputs[(0,cp.key)].setText('2000')
        owned=next(f for f in w.save.slots[0].fields if f.boolean and 'Owned' in f.label)
        w.inputs[(0,owned.key)].setChecked(True)
        output=w.save.patched(w.validated_changes());self.assertFalse(Save(output,'re8').warnings)
        self.assertEqual(path.read_bytes(),raw)
        self.assertNotIn('FEDCBA98',w.diagnostic('re8'))

    def test_resident_evil_editors_render_all_fields_without_changing_source(self):
        from test_re5 import fixture as re5_fixture
        from test_re6 import fixture as re6_fixture
        from test_re_hd import fixture as hd_fixture
        from test_re_engine import stream,wrap,ACCOUNT
        samples={'re5':re5_fixture(),'re6':re6_fixture(),'re1_hd':hd_fixture()}
        samples.update({game:wrap(stream(game),game) for game in ('re2','re3','re4_remake','re7','re8','re9')})
        for game,raw in samples.items():
            with self.subTest(game=game):
                path=self.root/'userdata'/'1'/'remote'/(game+'.bin')
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
                self.assertTrue(self.window.load(game,path))
                self.assertLessEqual(self.window.tabs.count(),3)
                self.assertEqual(len(self.window.inputs),len(self.window.save.slots[0].fields))
                field=next(f for f in self.window.save.slots[0].fields if not f.boolean and not f.choices)
                self.window.inputs[(0,field.key)].setText('120')
                output=self.window.save.patched(self.window.validated_changes())
                check=Save(output,game,path,ACCOUNT)
                self.assertEqual(next(f.value for f in check.slots[0].fields if f.key==field.key),120)
                self.assertEqual(path.read_bytes(),raw)
                self.window.edits={}

    def test_copied_requiem_prompts_for_original_account_only_once(self):
        from test_re_engine import stream,wrap,ACCOUNT
        path=self.root/'data00-1.bin';path.write_bytes(wrap(stream('re9'),'re9'))
        with patch('app.QInputDialog.getText',return_value=(str(ACCOUNT),True)) as prompt:
            self.assertTrue(self.window.load('re9',path))
            self.assertTrue(self.window.load('re9',path))
            self.assertEqual(prompt.call_count,1)
            self.assertIn('original',prompt.call_args.args[2].lower())

    def test_copied_kh3_account_prompt_and_reload(self):
        from test_kh_extra import Kh3Tests
        helper=Kh3Tests();path=self.root/'KHIII_slot0.bin';raw=helper.encrypted();path.write_bytes(raw)
        w=self.window
        with patch('app.QInputDialog.getText',return_value=(helper.ACCOUNT,True)) as prompt:
            self.assertTrue(w.load('kh3',path))
            self.assertEqual(prompt.call_count,1)
            self.assertEqual(w.tabs.count(),3)
            self.assertEqual(len(w.inputs),len(w.save.slots[0].fields))
            self.assertTrue(w.load('kh3',path))
            self.assertEqual(prompt.call_count,1)
        w.inputs[0,'munny'].setText('200')
        output=w.save.patched(w.validated_changes())
        check=Save(output,'kh3',account_id=helper.ACCOUNT)
        self.assertEqual(next(f.value for f in check.slots[0].fields if f.key=='munny'),200)
        self.assertEqual(path.read_bytes(),raw)

if __name__=='__main__':unittest.main()

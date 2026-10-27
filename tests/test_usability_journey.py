"""Navigation and review remain useful without writes or lost staged changes."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QSettings,Qt
from PySide6.QtWidgets import QApplication,QPushButton,QCheckBox
from app import Window
from catalog import BY_ID
from editor_layout import Category,Section
from editor_navigation import SectionNavigation
from test_core import kingdom,ror2


class UsabilityJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        with patch('app.discover',return_value=[]):
            self.w=Window(settings=QSettings(str(self.root/'prefs.ini'),QSettings.Format.IniFormat))
        self.w.reduce_motion.setChecked(True);self.w.show()

    def tearDown(self):
        self.w.edits={};self.w.close();self.w.deleteLater();self.app.processEvents();self.temp.cleanup()

    def test_search_and_undo_can_reach_changes_beyond_first_review_page(self):
        path=self.root/'profile.xml';raw=ror2();path.write_bytes(raw);w=self.w
        self.assertTrue(w.load('ror2',path))
        fields=[f for f in w.save.slots[0].fields if f.fmt=='xml-unlock']
        self.assertGreater(len(fields),160)
        w.set_unlock_fields(fields,1)
        total=len(w.edits);self.assertGreater(total,160)
        w.move_change_page(1)
        self.assertEqual(w.change_page,1);self.assertIn('81–160',w.change_results.text())
        self.assertLessEqual(w.summary_box.count(),81)
        last=fields[-1];key=(0,last.key)
        w.change_search.setText(last.label)
        self.assertEqual(w.change_page,0)
        links=[b for b in w.summary_content.findChildren(QPushButton) if b.accessibleName()=='Go to '+last.label+' in '+w.save.slots[0].name and not b.isHidden()]
        self.assertTrue(links)
        links[-1].click();self.app.processEvents()
        self.assertIn(key,w.inputs);self.assertTrue(w.inputs[key].isVisible())
        w.restore_field(key);self.assertEqual(len(w.edits),total-1)
        self.assertNotIn(key,w.edits);self.assertEqual(path.read_bytes(),raw)

    def test_pending_search_never_conceals_invalid_state_or_changes(self):
        path=self.root/'KHFM_WW.png';raw=kingdom();path.write_bytes(raw);w=self.w;w.load('kh1',path)
        w.inputs[0,'munny'].setText('-1');w.change_search.setText('cannot-match-this')
        self.assertTrue(w.summary_issue.text());self.assertFalse(w.summary_issue.isHidden())
        self.assertFalse(w.review_button.isEnabled());self.assertEqual(w.edits,{(0,'munny'):'-1'})
        clear=next(b for b in w.summary_content.findChildren(QPushButton) if b.text()=='Clear search' and not b.isHidden())
        clear.click();self.assertEqual(w.change_search.text(),'')
        self.assertIn('1–1',w.change_results.text());self.assertEqual(path.read_bytes(),raw)

    def test_clear_filters_recovers_small_and_virtual_categories_without_losing_edits(self):
        path=self.root/'KHFM_WW.png';raw=kingdom();path.write_bytes(raw);w=self.w;w.load('kh1',path)
        w.inputs[0,'munny'].setText('750')
        for page in [w.tabs.widget(i) for i in range(w.tabs.count())]:
            w.tabs.setCurrentWidget(page)
            page.findChild(QCheckBox,'changedOnly').setChecked(True)
            w.editor_search.setText('impossible search value')
            clear=page.findChild(QPushButton,'clearEditorFilters');self.assertFalse(clear.isHidden())
            clear.click()
            self.assertEqual(w.editor_search.text(),'')
            self.assertFalse(page.findChild(QCheckBox,'changedOnly').isChecked())
            self.assertTrue(page.navigation.list.isEnabled())
            self.assertTrue(clear.isHidden())
        self.assertEqual(w.validated_changes(),{(0,'munny'):750});self.assertEqual(path.read_bytes(),raw)

    def test_preview_open_save_preserves_the_chosen_game(self):
        self.w.open_preview('kh2')
        with patch.object(self.w,'open_file') as open_file:
            self.w.open_editor_file.click();open_file.assert_called_once_with('kh2')

    def test_cover_reopens_last_used_detected_file_and_slot(self):
        first=self.root/'first.png';second=self.root/'second.png'
        first.write_bytes(kingdom());second.write_bytes(kingdom());w=self.w
        w.files=[('kh1',first),('kh1',second)];w.remember_file('kh1',second,1)
        w.select_game(BY_ID['kh1']);self.assertEqual(w.path,second);self.assertEqual(w.slot_index,1)
        self.assertIn(' · ',w.file_combo.currentText())
        self.assertEqual(w.file_combo.itemData(w.file_combo.currentIndex(),Qt.ItemDataRole.ToolTipRole),str(second))
        w.inputs[1,'munny'].setText('900');w.show_library();w.select_game(BY_ID['kh1'])
        self.assertEqual(w.edits,{(1,'munny'):'900'});self.assertEqual(w.slot_index,1)
        self.assertEqual(first.read_bytes(),kingdom());self.assertEqual(second.read_bytes(),kingdom())

    def test_section_name_filter_does_not_move_or_edit_the_active_selection(self):
        sections=[Section('A long section name number '+str(i),selection='Sora') for i in range(12)]
        category=Category('Characters','','Character',sections)
        nav=SectionNavigation(category,{},'Characters');nav.show();self.app.processEvents()
        try:
            active=nav.active_section;nav.section_search.setText('number 11')
            visible=[nav.list.item(i) for i in range(nav.list.count()) if not nav.list.item(i).isHidden()]
            self.assertEqual(len(visible),1);self.assertIn('11',visible[0].text())
            self.assertIs(nav.active_section,active)
            nav.list.setCurrentItem(visible[0]);self.assertIs(nav.active_section,sections[-1])
            nav.section_search.setText('no match');self.assertFalse(nav.no_sections.isHidden())
            nav.section_search.clear();self.assertTrue(nav.no_sections.isHidden())
            self.assertIs(nav.active_section,sections[-1]);self.assertTrue(nav.list.wordWrap())
        finally:nav.close();nav.deleteLater()

    def test_library_search_accepts_words_in_any_order(self):
        w=self.w;w.search.setText('hearts kingdom ii')
        self.assertIn('kh2',w.visible_games);self.assertNotIn('webfishing',w.visible_games)

    def test_small_library_scrolls_details_instead_of_compressing_the_cover_header(self):
        w=self.w;w.resize(1100,720);w.preview_game(BY_ID['kh1']);self.app.processEvents()
        hero=w.detail_box.itemAt(0).layout()
        self.assertGreaterEqual(hero.geometry().height(),180)
        divider=w.detail_box.itemAt(1).widget()
        self.assertGreater(divider.geometry().top(),hero.geometry().bottom())
        self.assertGreater(w.detail_scroll.verticalScrollBar().maximum(),0)

    def test_pending_review_last_page_clamps_after_undoing_all_its_entries(self):
        path=self.root/'profile.xml';raw=ror2();path.write_bytes(raw);w=self.w;w.load('ror2',path)
        fields=[f for f in w.save.slots[0].fields if f.fmt=='xml-unlock']
        w.set_unlock_fields(fields,1);w.move_change_page(100)
        last_page=w.change_page;self.assertGreater(last_page,0)
        for key in list(w.edits)[last_page*80:]:w.edits.pop(key)
        w.update_summary()
        self.assertEqual(w.change_page,last_page-1);self.assertFalse(w.change_next.isEnabled())
        self.assertTrue(w.change_previous.isEnabled());self.assertEqual(path.read_bytes(),raw)

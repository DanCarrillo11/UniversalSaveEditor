"""Real navigation and staging stay intact while helping the user find/fix edits."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtCore import QSettings,QTimer,Qt
from PySide6.QtWidgets import QApplication,QPushButton
from app import Window
from core import Save
from choice_picker import ChoiceDialog,SearchableComboBox
from test_core import kingdom
from test_gtav_features import fixture as gta


class EditorGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        with patch('app.discover',return_value=[]):self.w=Window(settings=QSettings(str(self.root/'prefs.ini'),QSettings.Format.IniFormat))
        self.w.reduce_motion.setChecked(True);self.w.show()
        self.discard=patch.object(self.w,'may_discard',return_value=True);self.discard.start()

    def tearDown(self):
        self.w.close();self.w.deleteLater();self.app.processEvents();self.discard.stop();self.temp.cleanup()

    def test_fix_button_reveals_invalid_edit_in_another_slot_without_writing(self):
        path=self.root/'KHFM_WW.png';raw=kingdom();path.write_bytes(raw)
        w=self.w;self.assertTrue(w.load('kh1',path))
        w.change_slot(1);w.inputs[1,'munny'].setText('-1');w.change_slot(0);self.app.processEvents()
        self.assertTrue(w.fix_issue_button.isVisible());self.assertFalse(w.review_button.isEnabled())
        w.fix_issue_button.click();self.app.processEvents()
        self.assertEqual(w.slot_index,1);self.assertEqual(w.inputs[1,'munny'].text(),'-1')
        self.assertTrue(w.inputs[1,'munny'].property('invalid'))
        w.inputs[1,'munny'].setText('700');self.app.processEvents()
        self.assertFalse(w.fix_issue_button.isVisible());self.assertTrue(w.review_button.isEnabled())
        self.assertEqual(w.validated_changes(),{(1,'munny'):700});self.assertEqual(path.read_bytes(),raw)

    def test_pending_review_link_opens_the_actual_advanced_field(self):
        path=self.root/'SGTA50000';raw=gta(weapons=True);path.write_bytes(raw)
        w=self.w;self.assertTrue(w.load('gtav',path))
        key=(0,'weapon_shop:1:1b06d571:purch_0:25');w.inputs[key].setChecked(True)
        self.assertEqual(w.inputs[key].text(),'Purchased')
        w.advanced_options.setChecked(False)
        def navigate():
            dialog=self.app.activeModalWidget()
            next(b for b in dialog.findChildren(QPushButton) if b.text()=='Go to field').click()
        QTimer.singleShot(0,navigate);w.show_pending_changes();self.app.processEvents()
        self.assertTrue(w.advanced_options.isChecked());self.assertEqual(w.tabs.tabText(w.tabs.currentIndex()),'Advanced')
        self.assertTrue(w.inputs[key].isVisible());self.assertEqual(w.validated_changes(),{key:1})
        w.editor_search.setText('no real match');w.editor_search.clear()
        self.assertNotIn('matching advanced options',w.editor_mode_note.text())
        self.assertEqual(path.read_bytes(),raw)

    def test_searchable_paint_selection_stages_native_value_and_preview_never_edits(self):
        path=self.root/'SGTA50000';raw=gta(styles=True);path.write_bytes(raw)
        w=self.w;self.assertTrue(w.load('gtav',path));key=(0,'vehicle:0:0:primary')
        w.reveal_field(key);combo=w.inputs[key];self.assertIsInstance(combo,SearchableComboBox)
        field=w.field_index[key];target=field.maximum
        def choose():
            dialog=self.app.activeModalWidget();self.assertIsInstance(dialog,ChoiceDialog)
            dialog.search.setText(field.choices[target]);
            for i in range(dialog.results.count()):
                if dialog.results.item(i).data(Qt.ItemDataRole.UserRole)==target:
                    dialog.results.setCurrentRow(i);dialog.accept_choice();return
            dialog.reject();self.fail('Native option is missing')
        QTimer.singleShot(0,choose);combo.showPopup()
        self.assertEqual(w.validated_changes(),{key:target});self.assertFalse(Save(w.save.patched(w.validated_changes()),'gtav').warnings)
        self.assertEqual(path.read_bytes(),raw)
        w.open_preview('gtav');w.reveal_field(key);combo=w.inputs[key]
        QTimer.singleShot(0,choose);combo.showPopup()
        self.assertFalse(w.validated_changes());self.assertFalse(w.review_button.isEnabled());self.assertEqual(w.warning.objectName(),'info')

    def test_editor_search_understands_word_order_and_currency_names(self):
        path=self.root/'KHFM_WW.png';path.write_bytes(kingdom());w=self.w;self.assertTrue(w.load('kh1',path))
        w.editor_search.setText('dinero');self.app.processEvents()
        self.assertTrue(w.inputs[0,'munny']._field_row.isVisible())
        w.editor_search.setText('strength sora');self.app.processEvents()
        self.assertEqual(w.tabs.tabText(w.tabs.currentIndex()),'Characters')
        self.assertEqual(w.editor_search.text(),'strength sora')
        control=w.inputs.get((0,'0:strength'));self.assertIsNotNone(control)
        self.assertTrue(control._field_row.isVisible())

"""Search selection keeps original indexes, disabled options and cancel semantics."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import QApplication
from choice_picker import ChoiceDialog,SearchableComboBox
from editor_search import matches_query


class ChoicePickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def combo(self):
        combo=SearchableComboBox();combo.setAccessibleName('Saved weapon')
        combo.addItems([f'Option {i}' for i in range(30)])
        combo.setItemText(5,'Gray Jacket');combo.setItemText(24,'Gray Jacket')
        combo.model().item(29).setEnabled(False)
        combo.setCurrentIndex(5)
        return combo

    def test_multiword_accent_search_and_vocabulary_do_not_match_everything(self):
        self.assertTrue(matches_query('Sora · Maximum HP','hp sora'))
        self.assertTrue(matches_query('Munny · Currency','dinero'))
        self.assertTrue(matches_query('Ammunition · Pistol','munición pistol'))
        self.assertTrue(matches_query('maximum_health','health maximum'))
        self.assertFalse(matches_query('shop options','hp'))
        self.assertFalse(matches_query('Munny · Currency','dinero hp'))
        self.assertFalse(matches_query('Ammo capacity','money'))
        self.assertTrue(matches_query('anything',''))

    def test_duplicate_labels_choose_the_original_native_index(self):
        combo=self.combo();dialog=ChoiceDialog(combo)
        try:
            dialog.search.setText('jacket gray')
            self.assertEqual(dialog.results.count(),2)
            self.assertEqual([dialog.results.item(i).data(Qt.ItemDataRole.UserRole) for i in range(2)],[5,24])
            dialog.results.setCurrentRow(1);dialog.accept_choice()
            self.assertEqual(dialog.choice,24);self.assertEqual(combo.currentIndex(),5)
        finally:dialog.close();dialog.deleteLater();combo.deleteLater();self.app.processEvents()

    def test_disabled_and_no_match_options_cannot_be_accepted(self):
        combo=self.combo();dialog=ChoiceDialog(combo)
        try:
            dialog.search.setText('option 29')
            self.assertEqual(dialog.results.count(),1)
            self.assertFalse(dialog.results.item(0).flags()&Qt.ItemFlag.ItemIsEnabled)
            self.assertFalse(dialog.select.isEnabled());dialog.accept_choice();self.assertIsNone(dialog.choice)
            dialog.search.setText('no matching garment');self.assertEqual(dialog.results.count(),0)
            self.assertFalse(dialog.select.isEnabled());dialog.accept_choice();self.assertIsNone(dialog.choice)
        finally:dialog.close();dialog.deleteLater();combo.deleteLater();self.app.processEvents()

    def test_popup_cancel_preserves_selection_and_choose_emits_once(self):
        combo=self.combo();combo.show();changes=[];combo.currentIndexChanged.connect(changes.append)
        try:
            def cancel():
                dialog=self.app.activeModalWidget();self.assertIsInstance(dialog,ChoiceDialog)
                dialog.search.setText('option 19');dialog.reject()
            QTimer.singleShot(0,cancel);combo.showPopup()
            self.assertEqual(combo.currentIndex(),5);self.assertFalse(changes)
            def choose():
                dialog=self.app.activeModalWidget();dialog.search.setText('option 19')
                dialog.results.setCurrentRow(0);dialog.accept_choice()
            QTimer.singleShot(0,choose);combo.showPopup()
            self.assertEqual(combo.currentIndex(),19);self.assertEqual(changes,[19])
        finally:combo.close();combo.deleteLater();self.app.processEvents()

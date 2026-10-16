import os,tempfile,unittest
os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from app import Window
from core import Save
from editor_navigation import SectionNavigation
from test_rockstar import fixture


class RockstarInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_collection_growth_scrolls_without_clipping_the_sidebar_footer(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=QSettings(str(Path(directory)/'prefs.ini'),QSettings.Format.IniFormat)
            with patch('app.discover',return_value=[]):w=Window(settings=settings)
            w.show()
            try:
                for width,height in ((1440,900),(1100,720)):
                    w.resize(width,height);self.app.processEvents()
                    self.assertGreaterEqual(w.saving_note.height(),w.saving_note.heightForWidth(w.saving_note.width()))
                    self.assertGreaterEqual(w.collection_scroll.height(),80)
                self.assertGreater(w.collection_scroll.verticalScrollBar().maximum(),0)
            finally:w.close();w.deleteLater();self.app.processEvents()

    def test_character_navigation_decimal_cash_and_offline_previews(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat)
            with patch('app.discover',return_value=[]):w=Window(settings=settings)
            discard=patch.object(w,'may_discard',return_value=True);discard.start()
            w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
            try:
                for game in ('gtav','rdr2'):
                    w.open_preview(game);self.app.processEvents();self.assertTrue(w.save.is_preview)
                    self.assertFalse(w.review_button.isEnabled())
                p=root/'SGTA50000';p.write_bytes(fixture());w.load('gtav',p)
                w.inputs[0,'character:2:stamina'].setText('100');self.app.processEvents()
                self.assertEqual(w.validated_changes(),{(0,'character:2:stamina'):100})
                nav=w.tabs.currentWidget().findChild(SectionNavigation)
                self.assertIsNotNone(nav);self.assertEqual(set(nav.character_buttons),{'Michael','Franklin','Trevor'})
                out=w.save.patched(w.validated_changes());self.assertFalse(Save(out,'gtav').warnings)
                self.assertEqual(p.read_bytes(),fixture());w.reset()
                p=root/'SRDR30001';p.write_bytes(fixture('rdr2'));w.load('rdr2',p)
                w.inputs[0,'cash'].setText('1234.56');self.app.processEvents()
                self.assertEqual(w.validated_changes(),{(0,'cash'):1234.56})
                out=w.save.patched(w.validated_changes());self.assertEqual(Save(out,'rdr2').slots[0].fields[0].value,1234.56)
                self.assertEqual(p.read_bytes(),fixture('rdr2'));w.reset()
            finally:w.close();w.deleteLater();self.app.processEvents();discard.stop()

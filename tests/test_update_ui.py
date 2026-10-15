"""Update controls, consent, preferences and portable handoff."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QSettings,QCoreApplication,QEvent
from PySide6.QtWidgets import QApplication
from app import Window
from updates import Release


class UpdateUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.settings=QSettings(str(Path(self.temp.name)/'settings.ini'),QSettings.Format.IniFormat)
        self.discovery=patch('app.discover',return_value=[]);self.discovery.start()
        self.check=patch('updates.UpdateClient.check');self.checker=self.check.start()
        self.window=Window(settings=self.settings)
    def tearDown(self):
        self.window.edits={};self.window.repair.setChecked(False)
        self.window.close();self.window.deleteLater()
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);self.app.processEvents()
        self.check.stop();self.discovery.stop();self.temp.cleanup()
    def test_default_off_and_shared_nonmodal_dialog(self):
        w=self.window;self.assertFalse(w.automatic_updates);self.checker.assert_not_called()
        w.open_updates();dialog=w._updates_dialog
        self.assertFalse(dialog.isModal());self.checker.assert_called_once()
        w.open_updates();self.assertIs(dialog,w._updates_dialog)
        dialog.automatic.setChecked(True)
        self.assertTrue(self.settings.value('updates/checkOnStartup',False,bool))
        dialog.close();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
        self.assertIsNone(w._updates_dialog)
        w.open_updates();self.assertIsNot(dialog,w._updates_dialog)
    def test_states_and_plain_release_notes(self):
        w=self.window;w.open_updates();c=w.updater;d=w._updates_dialog
        c.release=Release('0.34.0-alpha','https://github.com','','',2048,'','<b>Plain notes</b>')
        c.state='available';c.message='Available';c.changed.emit();c.checked.emit(c.release)
        self.assertTrue(d.download.isEnabled());self.assertFalse(d.install.isEnabled())
        self.assertEqual(d.notes.toPlainText(),'<b>Plain notes</b>')
        self.assertEqual(w.updates_button.text(),'Update available')
        c.state='downloading';c.expected=2048;c.received=1024;c.changed.emit()
        self.assertEqual(d.progress.value(),500);self.assertFalse(d.check.isEnabled())
        c.state='ready';c.changed.emit();self.assertEqual(d.progress.value(),1000)
        self.assertTrue(d.folder.isEnabled())
    def test_startup_throttle_and_opt_out(self):
        w=self.window;w.show();w.check_updates_on_startup();self.checker.assert_not_called()
        w.set_automatic_updates(True);w.check_updates_on_startup();self.checker.assert_called_once()
        w.check_updates_on_startup();self.checker.assert_called_once()
        self.settings.setValue('updates/lastStartupCheck','invalid')
        w.check_updates_on_startup();self.assertEqual(self.checker.call_count,2)
    def test_unsaved_cancel_prevents_handoff(self):
        w=self.window;w.updater.state='ready'
        with patch('sys.frozen',True,create=True),patch.object(w,'may_discard',return_value=False),patch('update_install.prepare_install') as prepare:
            w.install_update();prepare.assert_not_called();self.assertFalse(w._installing_update)
    def test_normal_exit_keeps_verified_download_for_manual_replacement(self):
        w=self.window;w.updater.state='ready'
        with patch.object(w.updater,'cancel') as cancel:
            w.close();cancel.assert_not_called()
        w.updater.state='idle'
    def test_handoff_failure_keeps_window_and_verified_download(self):
        w=self.window;w.updater.state='ready';w.updater.downloaded=Path(self.temp.name)/'UniversalSaveEditor.exe'
        with patch('sys.frozen',True,create=True),patch.object(w,'may_discard',return_value=True),patch('update_install.prepare_install',side_effect=PermissionError),patch('app.QMessageBox.warning') as warning:
            w.install_update();warning.assert_called_once();self.assertFalse(w._installing_update)
            self.assertEqual(w.updater.state,'ready')
    def test_successful_handoff_preserves_download_for_helper(self):
        w=self.window;w.updater.state='ready';w.updater.downloaded=Path(self.temp.name)/'UniversalSaveEditor.exe'
        with patch('sys.frozen',True,create=True),patch.object(w,'may_discard',return_value=True),patch('update_install.prepare_install',return_value=Path(self.temp.name)/'update.json'),patch('update_install.launch_helper') as launch,patch.object(w,'close'),patch.object(QApplication,'quit'),patch.object(w.updater,'cancel') as cancel:
            w.install_update();launch.assert_called_once();self.assertTrue(w._installing_update);cancel.assert_not_called()
        w._installing_update=False

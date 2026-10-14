import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from runtime_errors import write_error_report,install_error_reporting


class RuntimeErrorTests(unittest.TestCase):
    def test_report_excludes_exception_text_and_locals_and_keeps_code_location(self):
        with tempfile.TemporaryDirectory() as folder:
            private='C:/Users/private-person/76561198000000000/secret-save.png'
            try:raise ValueError(private)
            except ValueError as error:
                path=write_error_report(type(error),error,error.__traceback__,folder)
            report=path.read_text(encoding='utf8')
            self.assertNotIn(private,report);self.assertNotIn('76561198000000000',report)
            data=json.loads(report);self.assertEqual(data['error_type'],'ValueError')
            self.assertTrue(data['frames']);self.assertGreater(data['frames'][0]['line'],0)
            self.assertTrue(all('/' not in f['module'] and '\\' not in f['module'] for f in data['frames']))

    def test_report_write_failure_does_not_raise_a_second_error(self):
        with patch.object(Path,'mkdir',side_effect=PermissionError('private path')):
            self.assertIsNone(write_error_report(RuntimeError,RuntimeError('secret'),None))

    def test_unhandled_hook_reports_before_showing_notice_and_can_be_restored(self):
        notices=[];old=sys.excepthook
        try:
            with tempfile.TemporaryDirectory() as folder,patch('runtime_errors.report_directory',return_value=Path(folder)):
                self.assertIs(install_error_reporting(notices.append),old)
                sys.excepthook(RuntimeError,RuntimeError('private message'),None)
                self.assertEqual(notices,[Path(folder)/'last-error.json'])
                self.assertTrue(notices[0].exists())
        finally:sys.excepthook=old

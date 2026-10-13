import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from catalog import BY_ID
from compatibility import EVIDENCE,compatibility_text
from core import Field,Slot
from diagnostics import explain_error,support_report
from recent_files import read_history,remember,forget,LIMIT


class SupportTests(unittest.TestCase):
    def test_every_editor_has_scope_and_evidence_without_full_game_claims(self):
        self.assertEqual(set(EVIDENCE),set(BY_ID))
        for game in BY_ID:
            text=compatibility_text(game)
            self.assertIn(BY_ID[game].description,text)
            self.assertIn('In-game checks',text);self.assertIn('Scope and limits',text)
            self.assertIn('do not guarantee',text)
        self.assertIn('native revision-261 checking is pending',compatibility_text('eldenring'))
        self.assertIn('recognized gameplay sections',compatibility_text('re1_hd').lower())
        self.assertIn('native Steam file checking is pending',compatibility_text('re2'))

    def test_error_categories_have_actions_and_do_not_echo_sensitive_messages(self):
        private='C:/Users/PRIVATE_USER/76561198012345678/SECRET_SAVE.sl2'
        cases=(
            (FileNotFoundError(private),'file_missing'),(PermissionError(private),'file_access'),
            (ValueError('The opened save changed. '+private),'file_changed'),
            (ValueError('Invalid CRC '+private),'integrity_check'),
            (ValueError('Wrong account ID 76561198012345678 '+private),'account_or_encryption'),
            (ValueError('No active characters '+private),'no_editable_records'),
            (ValueError('Quantity cannot exceed 99 '+private),'invalid_edit'),
            (ValueError('Unrecognized payload '+private),'unsupported_format'),
        )
        for error,code in cases:
            problem=explain_error(error);self.assertEqual(problem.code,code);self.assertTrue(problem.steps)
            report=support_report('eldenring',problem=problem,operation='open')
            self.assertNotIn('PRIVATE_USER',report+problem.message)
            self.assertNotIn('76561198012345678',report+problem.message)
            self.assertNotIn('SECRET_SAVE',report+problem.message)

    def test_revision_and_character_numbers_are_useful_but_not_arbitrary_text(self):
        problem=explain_error(ValueError('Character 2: unsupported save revision 261. C:/PRIVATE/76561198012345678'))
        self.assertEqual((problem.revision,problem.character),(261,2))
        report=json.loads(support_report('eldenring',problem=problem))
        self.assertEqual((report['save_revision'],report['character_number']),(261,2))
        self.assertNotIn('PRIVATE',json.dumps(report))

    def test_inspection_report_excludes_every_save_value_identity_and_warning_text(self):
        save=SimpleNamespace(game='kh3',raw=b'PRIVATE CONTENT',slots=[Slot('PRIVATE_CHARACTER',[
            Field('private-account:76561198012345678','PRIVATE_LABEL',123456789,0,'<Q'),
            Field('readonly','PRIVATE_METADATA',777,0,'<I',readonly=True)])],warnings=['PRIVATE_WARNING'])
        report=support_report('kh3',save,appearance='dark',suffix='.BIN',size=len(save.raw))
        data=json.loads(report);self.assertEqual(data['editable_fields'],1)
        self.assertEqual(data['active_records'],1);self.assertEqual(data['integrity_warnings'],1)
        self.assertEqual(data['file_extension'],'.bin')
        for token in ('PRIVATE','76561198012345678','123456789','777'):self.assertNotIn(token,report)
        self.assertNotIn('active_records',json.loads(support_report('re2',save)))
        filtered=support_report('bad-game',suffix='/PRIVATE.bin',operation='/PRIVATE',appearance='/PRIVATE',size=-1)
        self.assertNotIn('PRIVATE',filtered);self.assertNotIn('file_bytes',filtered)

    def test_history_is_bounded_deduplicated_and_clear_never_touches_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);history=[]
            for index in range(LIMIT+4):
                path=root/f'{index}.sl2';path.write_bytes(b'KEEP')
                history=remember(history,'eldenring',path,index)
            self.assertEqual(len(history),LIMIT)
            last=root/f'{LIMIT+3}.sl2';history=remember(history,'eldenring',last,2)
            self.assertEqual(history[0]['slot'],2);self.assertEqual(len(history),LIMIT)
            history=forget(history,last);self.assertEqual(len(history),LIMIT-1)
            self.assertEqual(last.read_bytes(),b'KEEP')
            self.assertEqual(len(list(root.iterdir())),LIMIT+4)

    def test_malformed_history_is_ignored_and_extra_properties_never_persist(self):
        for raw in ('bad-json','{}','null','[1,2]','x'*65537):self.assertEqual(read_history(raw),[])
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'sample.sl2')
            encoded=json.dumps([{'game':'eldenring','path':path,'slot':True,'private':'PRIVATE'},
                                {'game':'unknown','path':path},{'game':'kh1','path':'relative.png'}])
            result=read_history(encoded);self.assertEqual(len(result),1)
            self.assertEqual(result[0]['slot'],0);self.assertEqual(set(result[0]),{'game','path','slot'})

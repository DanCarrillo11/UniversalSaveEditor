"""Difficulty identity edits preserve caches, ranks, profiles and unrelated data."""
import struct
import unittest
from core import Save
from re_engine_container import ReEngineEnvelope
from re_hashes import murmur32
from test_re_engine import ACCOUNT,stream,wrap
from test_requiem import Writer,fixture
from requiem_difficulty import OWNER,WRAPPER,HASHES,LABELS


def difficulty_fields(cache=-1,identity=HASHES[0],duplicate=False,kind=8):
    fields=[('DifficultyIDValue',7,('<i',cache)),('DifficultyIDNameHash',kind,('<I',identity))]
    if duplicate:fields.append(('DifficultyIDNameHash',8,('<I',identity)))
    return fields


def sample(cache=-1,identity=HASHES[0],duplicate=False,kind=8,nested=False,wrapped=False,second=False):
    writer=Writer();writer.data.extend(stream('re9'))
    fields=difficulty_fields(cache,identity,duplicate,kind)
    if nested or wrapped:
        writer.root(WRAPPER if wrapped else 0x11112222,[('_Data' if wrapped else '_Backup',17,(OWNER,fields))])
    else:writer.root(OWNER,fields)
    if second:writer.root(OWNER,difficulty_fields())
    writer.root(0x8144dd0b,[('_Difficulty',8,('<I',HASHES[3]))])
    return wrap(bytes(writer.data[16:]),'re9')


class RequiemDifficultyTests(unittest.TestCase):
    def save(self,raw):return Save(raw,'re9',account_id=ACCOUNT)
    def fields(self,save):return [f for f in save.slots[0].fields if f.group=='Difficulty']

    def test_named_modes_change_only_identity_and_keep_lazy_cache_and_other_difficulties(self):
        for wrapped in (False,True):
            raw=sample(wrapped=wrapped);save=self.save(raw);field=self.fields(save)[0]
            self.assertEqual(field.choices,LABELS);self.assertEqual(field.value,0)
            before=ReEngineEnvelope(raw,'re9',account_id=ACCOUNT).payload
            for mode in range(4):
                with self.subTest(wrapped=wrapped,mode=mode):
                    output=save.patched({(0,field.key):mode});parsed=self.save(output)
                    self.assertEqual(self.fields(parsed)[0].value,mode);self.assertFalse(parsed.warnings)
                    after=ReEngineEnvelope(output,'re9',account_id=ACCOUNT).payload
                    offset=field.offset-16
                    self.assertEqual(struct.unpack_from('<I',after,offset)[0],HASHES[mode])
                    self.assertEqual(before[:offset],after[:offset]);self.assertEqual(before[offset+4:],after[offset+4:])
                    self.assertEqual(len(output),len(raw))
                    self.assertEqual(parsed.patched({(0,field.key):0}),raw)
            self.assertEqual(save.patched({}),raw)

    def test_nonlazy_unknown_ambiguous_and_backup_records_do_not_offer_a_writer(self):
        for options in ({'cache':0},{'cache':3},{'identity':0x12345678},{'duplicate':True},
                        {'kind':7},{'nested':True},{'second':True}):
            with self.subTest(options=options):
                raw=sample(**options);save=self.save(raw)
                self.assertEqual(self.fields(save),[]);self.assertEqual(save.patched({}),raw)
                with self.assertRaises(ValueError):save.patched({(0,'re9:difficulty:0'):1})

    def test_invalid_choices_are_rejected_and_health_edits_can_be_combined(self):
        raw=fixture(difficulty=True);save=self.save(raw);field=self.fields(save)[0]
        for value in (-1,4,True,1.5,'2'):
            with self.subTest(value=value),self.assertRaises(ValueError):save.patched({(0,field.key):value})
        health=next(f for f in save.slots[0].fields if f.label=='Health upgrade level')
        output=save.patched({(0,field.key):2,(0,health.key):0});parsed=self.save(output)
        self.assertEqual(self.fields(parsed)[0].value,2)
        self.assertEqual(next(f.value for f in parsed.slots[0].fields if f.label=='Current health'),800)

    def test_hashed_id_constants_match_independently_computed_names(self):
        self.assertEqual(tuple(murmur32(name.encode('utf-16-le')) for name in ('ID0010','ID0020','ID0030','ID0040')),HASHES)

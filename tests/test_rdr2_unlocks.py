"""Catalog actions must not mutate ownership, script progress or other flags."""
import unittest
from core import Save
from test_rdr2_features import fixture


class UnlockTests(unittest.TestCase):
    def save(self,**kwargs):return Save(fixture(unlocks=True,**kwargs),'rdr2')

    def test_apply_changes_only_known_bits_of_active_catalog_entries(self):
        for encrypted in (False,True):
            before=self.save(encrypted=encrypted);features=before.rockstar.rdr2
            fields=[f for f in before.slots[0].fields if f.group=='Unlocks']
            self.assertEqual(len(fields),3)
            self.assertEqual({f.collection for f in fields},{'Weapons','Clothing','Satchels'})
            changes={(0,f.key):1 for f in fields if not f.readonly}
            after=Save(before.patched(changes),'rdr2');raw=after.rockstar.container.plain
            self.assertFalse(after.warnings);self.assertEqual(len(after.raw),len(before.raw))
            allowed=set(features.unlocks.positions.values())
            allowed.update(i for begin,at in features.c.checks for i in range(at+12,at+16))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(features.raw,raw))))
            for key,at in features.unlocks.positions.items():
                self.assertEqual(raw[at],features.raw[at]|7)
                self.assertEqual(raw[at+1:at+4],b'\x12\x34\x56')
            self.assertTrue(all(f.value==1 and f.readonly for f in after.slots[0].fields if f.group=='Unlocks'))
            self.assertEqual([(h,b,m) for f,h,b,m in features.active_items()],
                [(h,b,m) for f,h,b,m in after.rockstar.rdr2.active_items()])

    def test_unknowns_and_story_documents_are_not_exposed_and_duplicate_hashes_are_protected(self):
        before=self.save(unlock_duplicate=True);fields=[f for f in before.slots[0].fields if f.group=='Unlocks']
        self.assertEqual(len(fields),2)
        self.assertFalse(any(f.collection=='Weapons' for f in fields))
        self.assertFalse(any('Newspaper' in f.label or 'Unknown' in f.label for f in fields))

    def test_malformed_graph_schema_and_unknown_versions_do_not_enable_actions(self):
        for args in ({'unlock_bad_pointer':True},{'unlock_bad_schema':True},{'unlock_version':True}):
            self.assertFalse(self.save(**args).rockstar.rdr2.unlocks.positions)
        self.assertEqual(len(self.save(unlock_short_count=True).rockstar.rdr2.unlocks.positions),1)

    def test_already_applied_and_reversal_are_rejected(self):
        before=self.save();fields=[f for f in before.slots[0].fields if f.group=='Unlocks']
        for field in fields:
            if field.readonly:
                with self.assertRaises(ValueError):before.patched({(0,field.key):0})
            else:
                with self.assertRaisesRegex(ValueError,'apply action'):before.patched({(0,field.key):0})
        self.assertEqual(before.patched({}),before.raw)

    def test_unlocks_are_separate_from_owned_items_and_compendium(self):
        before=self.save();field=next(f for f in before.slots[0].fields if f.group=='Unlocks' and f.collection=='Weapons')
        after=Save(before.patched({(0,field.key):1}),'rdr2')
        owned=next(f for f in after.slots[0].fields if f.key.startswith('compendium:ItemWeapon:'))
        self.assertEqual(owned.value,0)
        self.assertEqual(len(after.rockstar.rdr2.active_items()),5)

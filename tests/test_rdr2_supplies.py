"""New satchel records preserve existing ownership, backup references and scripts."""
import struct,unittest
from unittest.mock import patch
from core import Save
from rockstar_container import name_hash,u32
from rdr2_pso import RsavDirectory
from test_rdr2_features import fixture
from test_rdr2_pso import rsav


class SupplyTests(unittest.TestCase):
    def test_acquisition_allowlist_contains_only_resolved_catalog_facts(self):
        from rdr2_supplies import SUPPLIES
        from rdr2_features import labels
        self.assertEqual(len(SUPPLIES),len({n for n,c in SUPPLIES}))
        self.assertTrue(all(labels().get(f'{name_hash(n):08x}')==n for n,c in SUPPLIES))

    def save(self,encrypted=True,**kwargs):
        return Save(rsav(encrypted,fixture(False,supplies=True,**kwargs)),'rdr2')

    def test_add_creates_one_owned_record_without_changing_existing_items_or_scripts(self):
        for encrypted in (False,True):
            before=self.save(encrypted);f=before.rockstar.rdr2
            action=next(x for x in before.slots[0].fields if x.group=='Add supplies' and x.label=='Snake Oil')
            self.assertFalse(action.readonly);self.assertEqual(action.value,0)
            out=before.patched({(0,action.key):1,(0,'cash'):55.25});after=Save(out,'rdr2');g=after.rockstar.rdr2
            self.assertFalse(after.warnings);self.assertEqual(g.c.encrypted,encrypted)
            self.assertGreater(len(out),len(before.raw));self.assertEqual(len(g.c.checks),3)
            rows=g.active_items();self.assertEqual(len(rows),len(f.active_items())+1)
            added=[(h,b,m) for frame,h,b,m in rows if u32(g.raw,m['ItemId'])==name_hash('CONSUMABLE_SNAKE_OIL')]
            self.assertEqual(len(added),1);h,b,m=added[0]
            self.assertEqual(struct.unpack_from('>q',g.raw,m['Quantity'])[0],1)
            self.assertEqual(g.raw[m['ParentGuid']:m['ParentGuid']+8],(42).to_bytes(8,'big'))
            self.assertEqual(u32(g.raw,b+28),name_hash('SLOTID_SATCHEL'));self.assertEqual(g.raw[b+32],0)
            self.assertTrue(next(x for x in after.slots[0].fields if x.key==action.key).readonly)
            self.assertEqual(next(x.value for x in after.slots[0].fields if x.key=='cash'),55.25)
            for old,new in zip(RsavDirectory(f.c).entries[1:],RsavDirectory(g.c).entries[1:]):
                self.assertEqual(f.raw[old[1]:old[3]+16],g.raw[new[1]:new[3]+16])
            # Existing records stay byte-identical except the explicitly edited cash.
            old_guids={f.raw[m['Guid']:m['Guid']+8]:(frame,h,b,m) for frame,h,b,m in f.active_items()}
            for frame,h,b,m in rows:
                guid=g.raw[m['Guid']:m['Guid']+8]
                if guid not in old_guids or u32(g.raw,m['ItemId'])==name_hash('CURRENCY_CASH'):continue
                fr,oh,ob,om=old_guids[guid]
                self.assertEqual(g.raw[b:b+frame.structures[h][0]],f.raw[ob:ob+fr.structures[oh][0]])

    def test_collision_retry_uses_all_mapped_guids_and_multiple_actions_are_unique(self):
        before=self.save();fields=[x for x in before.slots[0].fields if x.group=='Add supplies' and not x.readonly][:2]
        with patch('rdr2_supplies.secrets.randbits',side_effect=[1,9,42,111,111,112]):
            after=Save(before.patched({(0,x.key):1 for x in fields}),'rdr2')
        guids=[after.rockstar.rdr2.raw[m['Guid']:m['Guid']+8] for frame,h,b,m in after.rockstar.rdr2.active_items()]
        self.assertEqual(len(guids),len(set(guids)));self.assertIn((111).to_bytes(8,'big'),guids);self.assertIn((112).to_bytes(8,'big'),guids)
        with patch('rdr2_supplies.secrets.randbits',return_value=9):
            with self.assertRaisesRegex(ValueError,'unique'):before.patched({(0,fields[0].key):1})

    def test_absent_character_broken_graph_unknown_directory_and_backup_mode_are_protected(self):
        for raw in (fixture(False,supplies=True),rsav(True,fixture(False)),
                    rsav(True,fixture(False,supplies=True,bad_pointer=True)),
                    rsav(True,fixture(False,supplies=True,backup=True))):
            s=Save(raw,'rdr2');self.assertFalse(s.rockstar.rdr2.supplies.actions)

    def test_existing_items_and_removal_are_protected_and_empty_apply_is_identical(self):
        before=self.save();fields=[x for x in before.slots[0].fields if x.group=='Add supplies']
        owned=next(x for x in fields if x.label=='Medicine');self.assertTrue(owned.readonly)
        with self.assertRaises(ValueError):before.patched({(0,owned.key):1})
        missing=next(x for x in fields if not x.readonly)
        with self.assertRaisesRegex(ValueError,'apply action'):before.patched({(0,missing.key):0})
        self.assertEqual(before.patched({}),before.raw)
        after=Save(before.patched({(0,missing.key):1}),'rdr2')
        quantity=next(x for x in after.slots[0].fields if x.group=='Inventory' and x.label==missing.label)
        changed=Save(after.patched({(0,quantity.key):3}),'rdr2')
        self.assertEqual(next(x.value for x in changed.slots[0].fields if x.key==quantity.key),3)

"""Serialized virtual stacks, single objects and invalid capacities."""
import unittest
from core import Save
from test_re_engine import wrap, stream, ACCOUNT
from test_requiem import Writer


def fixture(cap=30, duplicate=False, wrong_type=False,count=20):
    fields = [('CurrVirtualStackCount', 7, ('<i', count)),
              ('VirtualStackableCountMax', 8 if wrong_type else 7, ('<I' if wrong_type else '<i', cap))]
    if duplicate: fields.append(('VirtualStackableCountMax', 7, ('<i', cap)))
    w = Writer(); w.data.extend(stream('re4_remake'))
    w.root(0xbedd9bf5, [('InventoryItems', -1, [(0x004b7a76, fields)])])
    return wrap(bytes(w.data[16:]), 're4_remake')


class RemakeCapacityTests(unittest.TestCase):
    def test_saved_capacity_is_enforced_without_rewriting_cap(self):
        save = Save(fixture(), 're4_remake', account_id=ACCOUNT)
        item = next(f for f in save.slots[0].fields if f.group == 'Inventory quantities' and f.maximum == 30)
        output = save.patched({(0, item.key): 30})
        self.assertFalse(Save(output, 're4_remake', account_id=ACCOUNT).warnings)
        with self.assertRaises(ValueError): save.patched({(0, item.key): 31})
        self.assertEqual(save.patched({}), save.raw)

    def test_inconsistent_ambiguous_and_wrong_type_caps_are_readonly(self):
        for kwargs in ({'cap': 1,'count':1}, {'cap': 0}, {'cap': 10}, {'duplicate': True}, {'wrong_type': True}):
            save = Save(fixture(**kwargs), 're4_remake', account_id=ACCOUNT)
            fields = [f for f in save.slots[0].fields if f.group == 'Inventory quantities' and f.readonly]
            self.assertEqual(len(fields), 1)
            with self.assertRaises(ValueError): save.patched({(0, fields[0].key): 99})

    def test_large_valid_native_capacity_is_used_instead_of_an_arbitrary_editor_limit(self):
        save=Save(fixture(cap=1600,count=1200),'re4_remake',account_id=ACCOUNT)
        field=next(f for f in save.slots[0].fields if f.value==1200 and f.group=='Inventory quantities')
        self.assertEqual(field.maximum,1600);self.assertFalse(field.readonly)
        output=save.patched({(0,field.key):1500})
        parsed=Save(output,'re4_remake',account_id=ACCOUNT)
        self.assertEqual(next(f.value for f in parsed.slots[0].fields if f.key==field.key),1500)
        self.assertFalse(parsed.warnings)

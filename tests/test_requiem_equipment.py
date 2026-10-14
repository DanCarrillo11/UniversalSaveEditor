"""Owned-reference edits, ambiguity and unrelated-data preservation."""
import struct
import unittest
from core import Save
from re_hashes import murmur32
from re_engine_container import ReEngineEnvelope
from test_re_engine import stream, wrap, ACCOUNT
from test_requiem import Writer, inventory
from requiem_context import MANAGER, INVENTORY, PANEL
from requiem_equipment import EQUIP, SHORTCUT


def reference(owner, slot='Primary', index=0, code='it10_00_000'):
    return owner, [('_SlotName', 15, slot), ('_ItemIndex', 7, ('<i', index)),
                   ('_ItemIDName', 15, code), ('UnmappedState', 7, ('<i', 123456))]


def fixture(bad=False, duplicate=False, board='Hand', backup=False):
    weapons = [(PANEL, [('_ItemIDHash', 8, ('<I', murmur32(c.encode('utf-16-le')))),
                        ('_Stock', 7, ('<i', 1)), ('_Position', 16, ('<8s', b'GEOMETRY'))])
               for c in ('it10_00_000', 'it10_01_002', 'it10_20_005', 'it10_30_000')]
    equips = [reference(EQUIP, index=9 if bad else 0), reference(EQUIP, 'Secondary', 2, 'it10_20_005')]
    if duplicate: equips.append(reference(EQUIP))
    fields = [('_UserName', 15, 'User01'), ('_BoardTypeName', 15, board),
              ('_PanelItems', -1, weapons), ('_Equips', -1, equips),
              ('_Shortcuts', -1, [reference(SHORTCUT, 'Equip_Up'),
                                reference(SHORTCUT, 'Equip_Down', -1, '')])]
    w = Writer(); w.data.extend(stream('re9'))
    w.root(MANAGER, [('_BackupInventoryData' if backup else '_InventoryData', -1, [(INVENTORY, fields)])])
    w.root(*reference(EQUIP))  # scene lookalike
    return wrap(bytes(w.data[16:]), 're9')


class RequiemEquipmentTests(unittest.TestCase):
    def test_equipment_and_shortcut_update_both_owned_references(self):
        raw = fixture(); save = Save(raw, 're9', account_id=ACCOUNT)
        fields = [f for f in save.slots[0].fields if f.group in ('Equipment', 'Weapon shortcuts')]
        self.assertEqual(len(fields), 3)
        primary = next(f for f in fields if f.label == 'Primary')
        shortcut = next(f for f in fields if f.group == 'Weapon shortcuts')
        self.assertEqual(len(primary.choices), 2)
        self.assertFalse(any('Body Armor' in c or 'Knife' in c for c in primary.choices))
        output = save.patched({(0, primary.key): 1, (0, shortcut.key): 1})
        parsed = Save(output, 're9', account_id=ACCOUNT)
        self.assertFalse(parsed.warnings); self.assertEqual(len(output), len(raw))
        self.assertEqual([f.value for f in parsed.slots[0].fields if f.key in (primary.key, shortcut.key)], [1, 1])
        before = ReEngineEnvelope(raw, 're9', account_id=ACCOUNT).payload
        after = ReEngineEnvelope(output, 're9', account_id=ACCOUNT).payload
        allowed = set()
        for f in (primary, shortcut):
            index, name, _ = save.re_engine.requiem_equipment.operations[f.key]
            allowed.update(range(index.offset - 16, index.offset - 12))
            allowed.update(range(name.offset - 16, name.offset - 16 + name.size))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(before, after))))
        self.assertEqual(save.patched({}), raw)
        with self.assertRaises(ValueError): save.patched({(0, primary.key): 2})

    def test_backups_storage_scene_empty_and_ambiguous_references_are_preserved(self):
        for kwargs in ({'backup': True}, {'board': 'ItemBox'}, {'board': 'ShareItemBox'}):
            s = Save(fixture(**kwargs), 're9', account_id=ACCOUNT)
            self.assertFalse(any(f.group in ('Equipment', 'Weapon shortcuts') for f in s.slots[0].fields))
        for kwargs in ({'bad': True}, {'duplicate': True}):
            s = Save(fixture(**kwargs), 're9', account_id=ACCOUNT)
            self.assertFalse(any(f.label == 'Primary' and f.group == 'Equipment' for f in s.slots[0].fields))

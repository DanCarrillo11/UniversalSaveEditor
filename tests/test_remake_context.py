"""Bounded gameplay sections; encrypted output and dependent health edits."""
import struct
import unittest
from core import Save
from re_engine_container import ReEngineEnvelope
from remake_context import INVENTORY_MANAGER, INVENTORY, CASE, CHARACTERS, GAME_SECTIONS
from test_re_engine import wrap, stream, ACCOUNT
from test_requiem import Writer
from editor_layout import organize_fields


def fixture(duplicate=False, takeover=False, size=1, bad_hp=False):
    w = Writer(); w.data.extend(stream('re4_remake'))
    inventory = [(INVENTORY, [('IsTakeOverData', 2, ('<B', int(takeover))),
        ('InventorySize', 17, (CASE, [('CurrInventorySize', 1, ('<i', size))]))])]
    money = [('PTAS', 7, ('<i', 12345)), ('InventorySaveDatas', -1, inventory)]
    if duplicate: money.append(('PTAS', 7, ('<i', 23456)))
    w.root(INVENTORY_MANAGER, money)
    players = []
    for owner, hp, maximum in ((0x6da9ecfa, 500, 1000), (0x8504d4b1, 100, 300), (0x9e8e1368, 700, 800)):
        fields = [('_HP', 7, ('<i', hp + 1000 if bad_hp else hp)), ('_MaxHP', 7, ('<i', maximum)),
                  ('_IsEliminated', 2, ('<B', 1)), ('UnknownState', 16, ('<16s', b'KEEP ROOM STATE!'))]
        if duplicate: fields.append(('_HP', 7, ('<i', hp)))
        players.append((owner, fields))
    w.root(CHARACTERS, [('_CharacterSaves', -1, players)])
    # Exact class/property hashes placed in the wrong context are not enough.
    w.root(0x6da9ecfa, [('_HP', 7, ('<i', 250)), ('_MaxHP', 7, ('<i', 500))])
    w.root(0x12345678, [('Merchant', 17, (INVENTORY_MANAGER, [('PTAS', 7, ('<i', 999))]))])
    return wrap(bytes(w.data[16:]), 're4_remake')


def save(raw=None):
    return Save(fixture() if raw is None else raw, 're4_remake', account_id=ACCOUNT)


class RemakeContextTests(unittest.TestCase):
    def test_money_player_partner_and_case_have_native_contexts(self):
        s = save(); fields = s.slots[0].fields
        self.assertEqual(sum(f.label == 'Pesetas' for f in fields), 1)
        hp = [f for f in fields if f.group == 'Player health']
        self.assertEqual(len(hp), 4)
        self.assertEqual({f.collection for f in hp}, {'Player record 1', 'Partner record 1'})
        case = next(f for f in fields if f.label == 'Case size')
        self.assertEqual((case.value, case.minimum, case.maximum), (1, 1, 4))
        categories = organize_fields('re4_remake', fields)
        self.assertTrue(any(c.name == 'Characters' for c in categories))
        self.assertEqual(s.patched({}), s.raw)

    def test_health_clamps_only_its_own_record_and_rejects_explicit_conflicts(self):
        s = save(); fields = s.slots[0].fields
        maximum = next(f for f in fields if f.label == 'Maximum health' and f.collection.startswith('Player'))
        current = next(f for f in fields if f.label == 'Current health' and f.collection.startswith('Player'))
        out = s.patched({(0, maximum.key): 200}); parsed = save(out)
        self.assertEqual(next(f.value for f in parsed.slots[0].fields if f.key == current.key), 200)
        self.assertEqual([f.value for f in parsed.slots[0].fields if f.collection.startswith('Partner')], [100, 300])
        self.assertFalse(parsed.warnings)
        with self.assertRaisesRegex(ValueError, 'exceed'): s.patched({(0, maximum.key): 200, (0, current.key): 500})
        out = s.patched({(0, maximum.key): 2000, (0, current.key): 1500})
        self.assertEqual(next(f.value for f in save(out).slots[0].fields if f.key == current.key), 1500)

    def test_only_selected_values_related_hp_and_container_integrity_change(self):
        s = save(); fields = s.slots[0].fields
        money = next(f for f in fields if f.label == 'Pesetas')
        case = next(f for f in fields if f.label == 'Case size')
        out = s.patched({(0, money.key): 9999999, (0, case.key): 4})
        before = ReEngineEnvelope(s.raw, 're4_remake', account_id=ACCOUNT).payload
        after = ReEngineEnvelope(out, 're4_remake', account_id=ACCOUNT).payload
        allowed = {i for f in (money, case) for i in range(f.offset - 16, f.offset - 12)}
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(before, after))))
        self.assertEqual(len(out), len(s.raw)); self.assertFalse(save(out).warnings)
        with self.assertRaises(ValueError): s.patched({(0, case.key): 0})
        with self.assertRaises(ValueError): s.patched({(0, money.key): 10000000})

    def test_ambiguous_invalid_takeover_and_sentinel_records_are_protected(self):
        for kw in ({'duplicate': True}, {'bad_hp': True}):
            self.assertFalse(any(f.group == 'Player health' for f in save(fixture(**kw)).slots[0].fields))
        self.assertFalse(any(f.label == 'Pesetas' for f in save(fixture(duplicate=True)).slots[0].fields))
        for kw in ({'takeover': True}, {'size': -1}, {'size': 5}):
            self.assertFalse(any(f.label == 'Case size' for f in save(fixture(**kw)).slots[0].fields))

    def test_native_game_section_list_is_supported_but_nested_templates_are_not(self):
        player=(0x6da9ecfa,[('_HP',7,('<i',500)),('_MaxHP',7,('<i',1000))])
        inventory=(INVENTORY,[('IsTakeOverData',2,('<B',0)),
            ('InventorySize',17,(CASE,[('CurrInventorySize',1,('<i',2))]))])
        sections=[(INVENTORY_MANAGER,[('PTAS',7,('<i',2500)),('InventorySaveDatas',-1,[inventory])]),
                  (CHARACTERS,[('_CharacterSaves',-1,[player])])]
        w=Writer();w.root(GAME_SECTIONS,[('GameSaveDataList',-1,sections)])
        s=save(wrap(bytes(w.data[16:]),'re4_remake'))
        self.assertEqual({f.label for f in s.slots[0].fields},{'Pesetas','Case size','Current health','Maximum health'})
        money=next(f for f in s.slots[0].fields if f.label=='Pesetas')
        out=s.patched({(0,money.key):9876});self.assertFalse(save(out).warnings)


if __name__ == '__main__': unittest.main()

"""KH1 equipment-aware HP/MP constraints preserve legitimate equipment bonuses."""
import struct, unittest, zlib
from core import Save
from kh1_vitals import Kh1Vitals
from test_expansion import kh_fixture


def fixture():
    raw, record, start, end = kh_fixture('kh1'); raw = bytearray(raw)
    for c in (0, 1, 2, 3, 9):
        base = record + 4 + c * 0x74
        raw[base + 1:base + 6] = bytes((54, 50, 8 if c == 0 else 6, 5, 20))
        raw[base + 0x18] = 1; raw[base + 0x19] = 47
    raw[record + 4 + 0x32] = 92  # Spellbinder, +2 MP.
    struct.pack_into('>I', raw, end, zlib.crc32(raw[start - 4:end]))
    return bytes(raw), record, start, end


def choose(save, key, name):
    return next(f for f in save.slots[0].fields if f.key == key).choices.index(name)


class Kh1VitalsTests(unittest.TestCase):
    def test_equipped_bonuses_allow_current_values_above_the_saved_base(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1')
        fields = {f.key: f for f in save.slots[0].fields}
        self.assertEqual((fields['0:hp_effective_max'].value, fields['0:mp_effective_max'].value), (56, 8))
        self.assertTrue(fields['0:hp_effective_max'].readonly)
        self.assertEqual(save.patched({}), raw)
        save.patched({(0, '0:hp_current'): 56, (0, '0:mp_current'): 8})
        with self.assertRaises(ValueError): save.patched({(0, '0:hp_effective_max'): 200})

    def test_base_reduction_clamps_current_hp_and_preserves_unrelated_bytes(self):
        raw, record, start, end = fixture(); save = Save(raw, 'kh1')
        out = save.patched({(0, '0:hp'): 40}); base = record + 4
        self.assertEqual((out[base + 1], out[base + 2]), (46, 40))
        allowed = {base + 1, base + 2} | set(range(end, end + 4))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, out))))
        self.assertFalse(Save(out, 'kh1').warnings)
        self.assertEqual(save.raw, raw)

    def test_accessory_replacement_and_explicit_current_values_are_one_transaction(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); key = '0:accessory:0'
        edits = {(0, key): choose(save, key, 'Protect Chain')}
        out = save.patched(edits); base = record + 4
        self.assertEqual((out[base + 1], out[base + 3]), (50, 7))
        with self.assertRaisesRegex(ValueError, 'current HP'):
            save.patched({**edits, (0, '0:hp_current'): 51})
        out = save.patched({**edits, (0, '0:hp_current'): 45, (0, '0:mp_current'): 6})
        self.assertEqual((out[base + 1], out[base + 3]), (45, 6))

    def test_signed_weapon_mp_and_increases_do_not_heal(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); key = '0:weapon'
        out = save.patched({(0, key): choose(save, key, 'Metal Chocobo')})
        self.assertEqual(out[record + 7], 5)
        out = save.patched({(0, '0:mp'): 10})
        self.assertEqual((out[record + 7], out[record + 8]), (8, 10))
        with self.assertRaisesRegex(ValueError, 'outside the supported range'):
            save.patched({(0, key): choose(save, key, 'One-Winged Angel'),
                (0, '0:mp'): 2, (0, '0:accessory:0'): choose(save, '0:accessory:0', 'Protect Chain')})

    def test_unknown_equipment_and_existing_excess_are_preserved_without_guessing(self):
        raw, record, *_ = fixture(); base = record + 4
        for offset, value in ((0x19, 57), (0x18, 9)):
            changed = bytearray(raw); changed[base + offset] = value; save = Save(changed, 'kh1')
            self.assertNotIn('0:hp_effective_max', {f.key for f in save.slots[0].fields})
            out = save.patched({(0, 'munny'): 123}, repair_crc=True)
            self.assertEqual(out[base + offset], value)
        changed = bytearray(raw); changed[base + 1] = 100; save = Save(changed, 'kh1')
        out = save.patched({(0, '0:hp'): 51}, repair_crc=True)
        self.assertEqual(out[base + 1], 100)
        with self.assertRaises(ValueError): save.patched({(0, '0:hp_current'): 101}, repair_crc=True)
        with self.assertRaises(ValueError): Save(raw, 'kh1').patched({(0, '0:hp'): 250})

    def test_companions_use_their_own_accessories_and_unknown_mp_is_not_recalculated(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); base = record + 4 + 3 * 0x74
        self.assertEqual(Kh1Vitals.maximum(raw, base, 3, 'hp'), 56)
        self.assertIsNone(Kh1Vitals.maximum(raw, base, 3, 'mp'))
        out = save.patched({(0, '3:hp'): 40})
        self.assertEqual(out[base + 1], 46)
        self.assertEqual(out[record + 4:record + 4 + 0x74], raw[record + 4:record + 4 + 0x74])

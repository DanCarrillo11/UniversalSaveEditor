"""KH1 AP transactions include accessory bonuses and actual equipped flags."""
import struct, unittest, zlib
from core import Save
from kh1_ap import Kh1Ap
from test_expansion import kh_fixture


def fixture():
    raw, record, start, end = kh_fixture('kh1')
    raw = bytearray(raw)
    for c in (0, 1, 2, 3, 9):
        base = record + 4 + c * 0x74
        raw[base + 5] = 1
        raw[base + 0x18] = 2
        raw[base + 0x19:base + 0x1b] = bytes((29, 49))  # +2 and +1 AP.
        raw[base + 0x40:base + 0x70] = bytes(48)
        raw[base + 0x40:base + 0x42] = bytes((0x8a, 0x95))
    struct.pack_into('>I', raw, end, zlib.crc32(raw[start - 4:end]))
    return bytes(raw), record, start, end


def choose(save, key, text):
    return next(f for f in save.slots[0].fields if f.key == key).choices.index(text)


class Kh1ApTests(unittest.TestCase):
    def test_recognized_budget_counts_active_duplicates_and_accessories_only(self):
        raw, record, *_ = fixture(); raw = bytearray(raw); base = record + 4
        raw[base + 0x40:base + 0x44] = bytes((10, 10, 0x99, 0x80))
        save = Save(raw, 'kh1'); fields = {f.key: f for f in save.slots[0].fields}
        self.assertEqual(fields['0:ap_used'].value, 2)
        self.assertEqual(fields['0:ap_capacity'].value, 4)
        self.assertTrue(fields['0:ap_capacity'].readonly)
        self.assertEqual(save.party.kh1_ap.budget(raw, base), (2, 4))
        with self.assertRaises(ValueError): save.patched({(0, '0:ap_capacity'): 20}, repair_crc=True)

    def test_enabling_requires_enough_ap_and_combines_with_base_ap_in_one_write(self):
        raw, record, start, end = fixture(); save = Save(raw, 'kh1'); key = '0:ability:0'
        value = choose(save, key, 'Second Chance · Equipped')
        with self.assertRaisesRegex(ValueError, 'KH1 AP budget'): save.patched({(0, key): value})
        out = save.patched({(0, key): value, (0, '0:ap'): 2})
        self.assertEqual(out[record + 9], 2)
        check = Save(out, 'kh1'); self.assertFalse(check.warnings)
        self.assertEqual(Kh1Ap.budget(out, record + 4), (5, 5))
        allowed = {record + 9, record + 4 + 0x40} | set(range(end, end + 4))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, out))))
        self.assertEqual(save.raw, raw)

    def test_replacing_ap_accessory_or_reducing_ap_checks_final_combined_state(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); key = '0:ability:0'
        out = save.patched({(0, key): choose(save, key, 'Ars Arcanum · Equipped')})
        save = Save(out, 'kh1'); accessory = '0:accessory:0'
        replacement = choose(save, accessory, 'Protect Chain')
        with self.assertRaisesRegex(ValueError, 'KH1 AP budget'):
            save.patched({(0, accessory): replacement})
        with self.assertRaisesRegex(ValueError, 'KH1 AP budget'): save.patched({(0, '0:ap'): 0})
        edits = {(0, accessory): replacement, (0, key): choose(save, key, 'Ars Arcanum · Unequipped')}
        out = save.patched(edits); self.assertEqual(Kh1Ap.budget(out, record + 4), (0, 2))

    def test_unknown_active_costs_accessories_or_capacity_disable_inference(self):
        raw, record, *_ = fixture()
        for offset, value in ((0x40, 65), (0x19, 103), (0x19, 57), (0x18, 9), (5, 255)):
            changed = bytearray(raw); changed[record + 4 + offset] = value
            save = Save(changed, 'kh1')
            self.assertNotIn('0:ap_capacity', {f.key for f in save.slots[0].fields})
            out = save.patched({(0, 'munny'): 123}, repair_crc=True)
            self.assertEqual(out[record + 4 + offset], value)

    def test_existing_excess_is_preserved_but_cannot_increase(self):
        raw, record, *_ = fixture(); raw = bytearray(raw); base = record + 4
        raw[base + 5] = 0; raw[base + 0x19:base + 0x1b] = bytes((17, 18))
        raw[base + 0x40] = 21; save = Save(raw, 'kh1'); key = '0:ability:0'
        with self.assertRaisesRegex(ValueError, 'KH1 AP budget'):
            save.patched({(0, key): choose(save, key, 'Second Chance · Equipped')}, repair_crc=True)
        out = save.patched({(0, key): choose(save, key, 'Scan · Equipped')}, repair_crc=True)
        self.assertEqual(Kh1Ap.budget(out, base), (1, 0))
        self.assertFalse(Save(out, 'kh1').warnings)

    def test_companion_budget_uses_its_own_ap_and_accessories(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); key = '1:ability:0'
        value = choose(save, key, 'Leaf Bracer · Equipped')
        with self.assertRaisesRegex(ValueError, 'Donald'): save.patched({(0, key): value})
        out = save.patched({(0, key): value, (0, '1:ap'): 2})
        self.assertEqual(Kh1Ap.budget(out, record + 4 + 0x74), (5, 5))
        self.assertEqual(out[record + 4:record + 4 + 0x74], raw[record + 4:record + 4 + 0x74])

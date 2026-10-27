"""Ownership includes accessories/weapons; carried consumables use reserve stock."""
import struct, unittest, zlib
from core import Save
from kh1_inventory import Kh1Inventory
from test_expansion import kh_fixture


def fixture():
    raw, record, start, end = kh_fixture('kh1'); raw = bytearray(raw)
    for c in (0, 1, 2, 3, 9):
        base = record + 4 + c * 0x74
        raw[base + 1:base + 6] = bytes((40, 40, 5, 5, 20))
        raw[base + 0x40:base + 0x70] = bytes(48)
    raw[record + 0x499 + 17] = 5
    for w in (81, 103, 119): raw[record + 0x499 + w] = 1
    raw[record + 4 + 0x21] = 2
    raw[record + 4 + 0x22:record + 4 + 0x24] = bytes((1, 2))
    raw[record + 0x499 + 1] = 3; raw[record + 0x499 + 2] = 1
    struct.pack_into('>I', raw, end, zlib.crc32(raw[start - 4:end]))
    return bytes(raw), record, start, end


def choose(save, key, identity):
    return next(f for f in save.slots[0].fields if f.key == key).art_choices.index(identity)


class Kh1InventoryTests(unittest.TestCase):
    def test_normal_weapon_selection_acquires_ownership_without_consuming_other_weapons(self):
        raw, record, _, end = fixture(); save = Save(raw, 'kh1'); key = '0:weapon'
        out = save.patched({(0, key): choose(save, key, 98)})
        self.assertEqual((out[record + 0x499 + 81], out[record + 0x499 + 98]), (1, 1))
        allowed = {record + 4 + 0x32, record + 0x499 + 98} | set(range(end, end + 4))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, out))))
        with self.assertRaisesRegex(ValueError, 'owned copies'):
            save.patched({(0, key): choose(save, key, 98), (0, 'inventory:98'): 0})
        self.assertEqual(save.raw, raw); self.assertFalse(Save(out, 'kh1').warnings)

    def test_accessory_ownership_counts_all_characters_and_duplicate_equipped_copies(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1')
        changes = {(0, '0:accessory:0'): choose(save, '0:accessory:0', 18),
                   (0, '0:accessory:1'): choose(save, '0:accessory:1', 18),
                   (0, '1:accessory:0'): choose(save, '1:accessory:0', 18)}
        out = save.patched(changes)
        self.assertEqual((out[record + 0x499 + 17], out[record + 0x499 + 18]), (5, 3))
        with self.assertRaisesRegex(ValueError, 'at least 3'):
            save.patched({**changes, (0, 'inventory:18'): 2})
        out = save.patched({**changes, (0, 'inventory:18'): 7})
        self.assertEqual(out[record + 0x499 + 18], 7)
        with self.assertRaises(ValueError): save.patched({(0, 'inventory:17'): 4})
        out = save.patched({(0, 'inventory:17'): 4, (0, '0:accessory:0'): choose(save, '0:accessory:0', 0)})
        self.assertEqual(out[record + 0x499 + 17], 4)

    def test_consumables_transfer_reserve_stock_and_restore_exactly(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); key = '0:item:0'
        out = save.patched({(0, key): choose(save, key, 2)})
        self.assertEqual(out[record + 0x49a:record + 0x49c], bytes((4, 0)))
        fresh = Save(out, 'kh1')
        restored = fresh.patched({(0, key): choose(fresh, key, 1)})
        self.assertEqual(restored, raw)
        out = save.patched({(0, key): choose(save, key, 0)})
        self.assertEqual(out[record + 0x49a], 4)

    def test_carried_swaps_need_no_spare_copy_and_ignore_unchanged_hidden_entries(self):
        raw, record, *_ = fixture(); raw = bytearray(raw)
        raw[record + 0x49a:record + 0x49c] = bytes(2)
        raw[record + 4 + 0x24] = 0xf9  # Hidden third entry is never touched.
        save = Save(raw, 'kh1'); a, b = '0:item:0', '0:item:1'
        out = save.patched({(0, a): choose(save, a, 2), (0, b): choose(save, b, 1)}, repair_crc=True)
        self.assertEqual(out[record + 0x49a:record + 0x49c], bytes(2))
        self.assertEqual(out[record + 4 + 0x24], 0xf9)
        with self.assertRaisesRegex(ValueError, 'reserve stock'):
            save.patched({(0, a): choose(save, a, 2)}, repair_crc=True)

    def test_combined_stock_edits_reparse_the_amount_after_transfers(self):
        raw, record, *_ = fixture(); save = Save(raw, 'kh1'); key = '0:item:0'
        out = save.patched({(0, key): choose(save, key, 3), (0, 'inventory:3'): 2, (0, 'inventory:1'): 98})
        self.assertEqual((out[record + 0x49a], out[record + 0x49c]), (99, 1))
        with self.assertRaisesRegex(ValueError, 'reserve stock'):
            save.patched({(0, key): choose(save, key, 3), (0, 'inventory:3'): 2, (0, 'inventory:1'): 99})

    def test_unknown_counts_temporary_weapons_and_existing_deficits_are_protected(self):
        raw, record, *_ = fixture(); raw = bytearray(raw)
        raw[record + 4 + 3 * 0x74 + 0x18] = 9
        save = Save(raw, 'kh1'); key = '0:accessory:0'
        with self.assertRaisesRegex(ValueError, 'unsupported character'):
            save.patched({(0, key): choose(save, key, 18)}, repair_crc=True)
        out = save.patched({(0, 'munny'): 100}, repair_crc=True)
        self.assertEqual(out[record + 4 + 3 * 0x74 + 0x18], 9)
        raw, record, *_ = fixture(); raw = bytearray(raw); raw[record + 0x499 + 17] = 3
        save = Save(raw, 'kh1')
        self.assertEqual(save.patched({}, repair_crc=True)[record + 0x499 + 17], 3)
        save.patched({(0, 'inventory:17'): 4}, repair_crc=True)  # Existing deficit is reduced.
        with self.assertRaises(ValueError): save.patched({(0, 'inventory:17'): 2}, repair_crc=True)
        key = '0:weapon'
        self.assertNotIn(85, next(f.art_choices for f in save.slots[0].fields if f.key == key))
        with self.assertRaises(ValueError): save.patched({(0, 'inventory:85'): 1}, repair_crc=True)
        raw[record + 4 + 0x32] = 85; save = Save(raw, 'kh1')
        self.assertIn(85, next(f.art_choices for f in save.slots[0].fields if f.key == key))
        out = save.patched({(0, 'munny'): 100}, repair_crc=True)
        self.assertEqual(out[record + 4 + 0x32], 85)

    def test_equipment_transactions_keep_ap_and_vitals_constraints(self):
        raw, record, *_ = fixture(); raw = bytearray(raw); base = record + 4
        raw[base + 5] = 0; raw[base + 0x19] = 29; raw[base + 0x40] = 21
        raw[record + 0x499 + 29] = 1
        save = Save(raw, 'kh1'); key = '0:accessory:0'
        with self.assertRaisesRegex(ValueError, 'AP budget'):
            save.patched({(0, key): choose(save, key, 18)}, repair_crc=True)
        out = save.patched({(0, key): choose(save, key, 18), (0, '0:ap'): 5}, repair_crc=True)
        self.assertEqual(out[record + 0x499 + 18], 1)
        self.assertEqual(Kh1Inventory.owned_equipped(out, Kh1Inventory.slots(out, record)[0])[18], 1)

    def test_absent_character_cannot_be_enabled_through_an_equipment_selection(self):
        raw, record, *_ = fixture();raw=bytearray(raw);raw[record+4+0x74]=0
        save=Save(raw,'kh1');key='1:weapon'
        with self.assertRaisesRegex(ValueError,'absent or unsupported'):
            save.patched({(0,key):choose(save,key,104)},repair_crc=True)


if __name__ == '__main__': unittest.main()

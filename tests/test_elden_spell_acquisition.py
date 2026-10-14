"""One-copy native spell goods, registered acquisition and byte preservation."""
import hashlib
import struct
import unittest
from core import Save
from elden_registry import registry_records
from test_elden_spells import ready


def refresh(raw, save):
    for start, length in save.elden_ring.blocks:
        raw[start:start + 16] = hashlib.md5(raw[start + 16:start + length]).digest()
    return bytes(raw)


class SpellAcquisitionTests(unittest.TestCase):
    def test_learning_registers_a_single_good_and_acquisition_counters(self):
        raw, _ = ready(); s = Save(raw, 'eldenring'); c = s.elden_ring.characters[0]
        f = next(f for f in s.slots[0].fields if f.key == 'learn_spell:4010')
        self.assertEqual((f.value, f.minimum, f.maximum, f.readonly), (0, 0, 1, False))
        output = s.patched({(0, f.key): 1}); check = Save(output, 'eldenring')
        learned = next(f for f in check.slots[0].fields if f.key == 'learn_spell:4010')
        self.assertTrue(learned.readonly); self.assertEqual(learned.value, 1)
        rows = [struct.unpack_from('<3I', output, c.held + 4 + i * 12) for i in range(0xa80)]
        copies = [row for row in rows if row[0] == 0xb0000000 | 4010]
        self.assertEqual(len(copies), 1); self.assertEqual(copies[0][1], 1)
        self.assertIn((0x40000000 | 4010, 1), registry_records(output, c.registry))
        self.assertEqual(struct.unpack_from('<I', output, c.held)[0], struct.unpack_from('<I', raw, c.held)[0] + 1)
        counters = c.held + 8 + (0xa80 + 0x180) * 12
        equip, acquired = struct.unpack_from('<2I', output, counters)
        self.assertEqual(equip, struct.unpack_from('<I', raw, counters)[0] + 1)
        self.assertGreater(acquired, copies[0][2]); self.assertEqual(copies[0][2] % 2, 1)
        options = check.elden_ring.spell_loadouts[0].operations['spell_slot:0'][1]
        self.assertIn(4010, options); self.assertFalse(check.warnings)
        with self.assertRaises(ValueError): check.patched({(0, f.key): 0})
        self.assertEqual(s.patched({}), raw)

    def test_multiple_spells_have_unique_indices_and_can_be_memorized_after_apply(self):
        raw, _ = ready(True); s = Save(raw, 'eldenring')
        output = s.patched({(0, 'learn_spell:4010'): 1, (0, 'learn_spell:4020'): 1})
        check = Save(output, 'eldenring'); c = check.elden_ring.characters[0]
        rows = [struct.unpack_from('<3I', output, c.held + 4 + i * 12) for i in range(0xa80)]
        added = [row for row in rows if row[0] in (0xb0000000 | 4010, 0xb0000000 | 4020)]
        self.assertEqual(len({row[2] for row in added}), 2)
        choices = check.elden_ring.spell_loadouts[0].operations['spell_slot:0'][1]
        equipped = check.patched({(0, 'spell_slot:0'): choices.index(4010)})
        self.assertFalse(Save(equipped, 'eldenring').warnings)

    def test_unrelated_blocks_loadout_key_items_and_original_flags_are_unchanged(self):
        raw, off = ready(); s = Save(raw, 'eldenring'); c = s.elden_ring.characters[0]
        output = s.patched({(0, 'learn_spell:4010'): 1})
        key_start = c.held + 4 + 0xa80 * 12
        self.assertEqual(raw[key_start:key_start + 4 + 0x180 * 12], output[key_start:key_start + 4 + 0x180 * 12])
        self.assertEqual(raw[off:off + 116], output[off:off + 116])
        for start, length in s.elden_ring.blocks[1:]: self.assertEqual(raw[start:start + length], output[start:start + length])
        old = registry_records(raw, c.registry); new = registry_records(output, c.registry)
        self.assertTrue(all(record in new for record in old))
        self.assertEqual(len(raw), len(output)); self.assertEqual(raw[:0x300], output[:0x300])

    def test_duplicate_zero_quantity_and_legacy_spell_records_are_not_overwritten(self):
        raw, _ = ready(); s = Save(raw, 'eldenring'); c = s.elden_ring.characters[0]
        for quantity in (0, 2):
            damaged = bytearray(raw)
            struct.pack_into('<3I', damaged, c.held + 4 + 8 * 12, 0xb0000000 | 4010, quantity, 301)
            struct.pack_into('<I', damaged, c.held, struct.unpack_from('<I', raw, c.held)[0] + 1)
            check = Save(refresh(damaged, s), 'eldenring')
            self.assertFalse(any(f.key == 'learn_spell:4010' for f in check.slots[0].fields))
        key_start = c.held + 8 + 0xa80 * 12
        legacy = bytearray(raw); struct.pack_into('<3I', legacy, key_start, 0xb0000000 | 4010, 1, 301)
        struct.pack_into('<I', legacy, key_start - 4, 1)
        check = Save(refresh(legacy, s), 'eldenring')
        self.assertTrue(next(f for f in check.slots[0].fields if f.key == 'learn_spell:4010').readonly)
        duplicate = bytearray(legacy); struct.pack_into('<3I', duplicate, c.held + 4 + 8 * 12, 0xb0000000 | 4010, 1, 303)
        struct.pack_into('<I', duplicate, c.held, struct.unpack_from('<I', raw, c.held)[0] + 1)
        check = Save(refresh(duplicate, s), 'eldenring')
        self.assertFalse(any(f.key == 'learn_spell:4010' for f in check.slots[0].fields))

    def test_invalid_registry_counts_and_unowned_dlc_do_not_offer_learning(self):
        raw, _ = ready(); s = Save(raw, 'eldenring'); c = s.elden_ring.characters[0]
        self.assertFalse(any(f.key.startswith('learn_spell:200') for f in s.slots[0].fields))
        for offset, value in ((c.registry, 7001), (c.held, 0), (c.held + 4 + 0xa80 * 12, 1)):
            bad = bytearray(raw); struct.pack_into('<I', bad, offset, value)
            check = Save(refresh(bad, s), 'eldenring')
            self.assertFalse(any(f.key.startswith('learn_spell:') for f in check.slots[0].fields))
        # A known already-owned DLC spell may be inspected; it cannot be granted.
        dlc = bytearray(raw); struct.pack_into('<3I', dlc, c.held + 4 + 8 * 12, 0xb0000000 | 2004300, 1, 301)
        struct.pack_into('<I', dlc, c.held, struct.unpack_from('<I', raw, c.held)[0] + 1)
        check = Save(refresh(dlc, s), 'eldenring')
        self.assertTrue(next(f for f in check.slots[0].fields if f.key == 'learn_spell:2004300').readonly)


if __name__ == '__main__': unittest.main()

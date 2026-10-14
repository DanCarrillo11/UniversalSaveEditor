"""Critical transitions, explicit overrides and protected ability sources."""
import struct
import unittest
from core import Save
from test_kh_extra import kh3_plain
from test_game_completion import checksum3
from kh3_mode import CRITICAL_ABILITIES


def fixture():
    raw = bytearray(kh3_plain()); raw[0x14] = 1
    for index in range(3):
        base = 0x1880 + index * 0x9c0
        struct.pack_into('<2i', raw, base + 0x984, 101 + index, 100)
    for identifier in CRITICAL_ABILITIES:
        struct.pack_into('<I', raw, 0x1880 + 0x160 + identifier * 4, 0x444)
    struct.pack_into('<i', raw, 0x28, 500)
    struct.pack_into('<2I', raw, 0x840, 800, 300)
    return checksum3(raw)


class Kh3ModeTests(unittest.TestCase):
    def test_entering_critical_synchronizes_known_abilities_and_party_vitals(self):
        raw = fixture(); save = Save(raw, 'kh3')
        output = save.patched({(0, 'difficulty'): 3})
        self.assertEqual(struct.unpack_from('<2i', output, 0x1880 + 0x984), (50, 50))
        self.assertEqual(struct.unpack_from('<2i', output, 0x1880 + 0x9c0 + 0x984), (51, 50))
        for i in CRITICAL_ABILITIES:
            self.assertEqual(struct.unpack_from('<I', output, 0x1880 + 0x160 + i * 4)[0], 0x44b)
        self.assertFalse(Save(output, 'kh3').warnings)
        allowed = set(range(12, 16)) | {0x14}
        for index in range(3): allowed.update(range(0x1880 + index * 0x9c0 + 0x984, 0x1880 + index * 0x9c0 + 0x98c))
        for i in CRITICAL_ABILITIES: allowed.update(range(0x1880 + 0x160 + i * 4, 0x1880 + 0x164 + i * 4))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, output))))

    def test_explicit_vitals_win_and_equipment_sources_and_unknown_words_are_preserved(self):
        raw = bytearray(fixture())
        for i, word in zip(CRITICAL_ABILITIES, (0x444, 0x144b, 0x800)):
            struct.pack_into('<I', raw, 0x1880 + 0x160 + i * 4, word)
        save = Save(checksum3(raw), 'kh3')
        output = save.patched({(0, 'difficulty'): 3, (0, 'character:Sora:hp'): 200})
        self.assertEqual(struct.unpack_from('<i', output, 0x1880 + 0x984)[0], 200)
        for i, word in zip(CRITICAL_ABILITIES, (0x44b, 0x144b, 0x800)):
            self.assertEqual(struct.unpack_from('<I', output, 0x1880 + 0x160 + i * 4)[0], word)
        back = Save(output, 'kh3').patched({(0, 'difficulty'): 1})
        for i, word in zip(CRITICAL_ABILITIES, (0x444, 0x144b, 0x800)):
            self.assertEqual(struct.unpack_from('<I', back, 0x1880 + 0x160 + i * 4)[0], word)
        with self.assertRaises(ValueError): save.patched({(0, 'difficulty'): 3, (0, 'character:Sora:ability:104'): 0})
        self.assertEqual(save.patched({}), checksum3(raw))

    def test_munny_ledger_synchronizes_only_consistent_saved_ledger(self):
        save = Save(fixture(), 'kh3'); output = save.patched({(0, 'munny'): 2000})
        self.assertEqual(struct.unpack_from('<2I', output, 0x840), (2300, 300))
        raw = bytearray(fixture()); struct.pack_into('<I', raw, 0x840, 123)
        save = Save(checksum3(raw), 'kh3'); output = save.patched({(0, 'munny'): 2000})
        self.assertEqual(output[0x840:0x848], raw[0x840:0x848])
        self.assertFalse(Save(output, 'kh3').warnings)

    def test_companion_behavior_is_independent_and_does_not_rewrite_mp_or_skills(self):
        raw = fixture(); save = Save(raw, 'kh3')
        output = save.patched({(0, 'character:Donald:ai:ability'): 2, (0, 'character:Goofy:ai:combat'): 3})
        allowed = set(range(12, 16)) | {0x1880 + 0x9c0 + 0x159, 0x1880 + 2 * 0x9c0 + 0x158}
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, output))))
        self.assertFalse(Save(output, 'kh3').warnings)

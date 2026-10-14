"""Native sentinel pairs, owned spells, cost and fingerprint preservation."""
import hashlib
import struct
import unittest
import zlib
from core import Save
from test_elden_ring import fixture
from elden_spells import EMPTY, spell_hash


def ready(empty=False,source=None):
    raw = bytearray(fixture() if source is None else source); save = Save(raw, 'eldenring'); c = save.elden_ring.characters[0]
    off = c.held + 16 + (0xa80 + 0x180) * 12
    spells = (4000, 4001, 4200)
    for index, identifier in enumerate(spells, 4):
        struct.pack_into('<3I', raw, c.held + 4 + index * 12, 0xb0000000 | identifier, 1, index + 100)
    struct.pack_into('<3I', raw, c.held + 4 + 7 * 12, 0xb000272e, 2, 200)
    count=sum(struct.unpack_from('<I',raw,c.held+4+i*12)[0] not in (0,EMPTY) for i in range(0xa80))
    struct.pack_into('<I',raw,c.held,count)
    ids = [EMPTY] * 14 if empty else [4000, 4001] + [EMPTY] * 12
    for index, identifier in enumerate(ids):
        struct.pack_into('<2I', raw, off + index * 8, identifier, 0 if identifier == EMPTY else EMPTY)
    struct.pack_into('<I', raw, off + 112, EMPTY if empty else 1)
    struct.pack_into('<I', raw, c.fingerprints + 40, spell_hash(ids))
    for start, length in save.elden_ring.blocks:
        raw[start:start + 16] = hashlib.md5(raw[start + 16:start + length]).digest()
    return bytes(raw), off


class SpellLoadoutTests(unittest.TestCase):
    def test_owned_spells_can_be_replaced_and_compacted_with_correct_hash(self):
        raw, off = ready(); s = Save(raw, 'eldenring')
        f = next(f for f in s.slots[0].fields if f.key == 'spell_slot:0')
        self.assertEqual(len(f.choices), 4)
        options = s.elden_ring.spell_loadouts[0].operations[f.key][1]
        out = s.patched({(0, f.key): options.index(4200)})
        self.assertEqual(struct.unpack_from('<2I', out, off), (4200, EMPTY))
        self.assertFalse(Save(out, 'eldenring').warnings)
        compact = Save(out, 'eldenring').patched({(0, 'spell_slot:0'): 0})
        self.assertEqual(struct.unpack_from('<4I', compact, off), (4001, EMPTY, EMPTY, 0))
        self.assertEqual(struct.unpack_from('<I', compact, off + 112)[0], 0)
        allowed = set(range(off, off + 116)) | set(range(s.elden_ring.characters[0].fingerprints + 40, s.elden_ring.characters[0].fingerprints + 44))
        allowed.update(range(0x300, 0x310))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, compact))))
        self.assertEqual(raw, s.patched({}))

    def test_duplicate_over_capacity_and_active_index_are_rejected(self):
        raw, off = ready(); s = Save(raw, 'eldenring')
        options = s.elden_ring.spell_loadouts[0].operations['spell_slot:0'][1]
        # Comet Azur uses 3 slots, so 3+1+1 exceeds the fixture's four slots.
        for changes in ({(0, 'spell_slot:0'): options.index(4001)},
                        {(0, 'spell_slot:2'): options.index(4200)},
                        {(0, 'active_spell'): 13}, {(0, 'active_spell'): 14}):
            with self.assertRaises(ValueError): s.patched(changes)
        cleared = s.patched({(0, 'spell_slot:0'): 0, (0, 'spell_slot:1'): 0})
        self.assertEqual(struct.unpack_from('<I', cleared, off + 112)[0], EMPTY)
        self.assertFalse(Save(cleared, 'eldenring').warnings)

    def test_empty_loadout_can_use_owned_spell_but_unknown_and_invalid_records_are_protected(self):
        raw, off = ready(True); s = Save(raw, 'eldenring')
        options = s.elden_ring.spell_loadouts[0].operations['spell_slot:0'][1]
        out = s.patched({(0, 'spell_slot:0'): options.index(4000)})
        self.assertEqual(struct.unpack_from('<I', out, off + 112)[0], 0)
        self.assertFalse(Save(out, 'eldenring').warnings)
        for location, value in ((off, 999999), (off + 4, EMPTY), (s.elden_ring.characters[0].fingerprints + 40, 123)):
            bad = bytearray(raw); struct.pack_into('<I', bad, location, value)
            start, length = s.elden_ring.blocks[0]; bad[start:start + 16] = hashlib.md5(bad[start + 16:start + length]).digest()
            parsed = Save(bad, 'eldenring')
            self.assertFalse(any(f.group == 'Spells' for f in parsed.slots[0].fields))
            self.assertEqual(parsed.patched({}), bad)

    def test_memory_bonus_needs_an_unlocked_talisman_and_matching_equipment_hash(self):
        raw,off=ready();s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
        raw=bytearray(raw);struct.pack_into('<I',raw,c.held+8+7*12,0)
        struct.pack_into('<I',raw,c.player+0x2f4+17*4,0x474)
        armor=b''.join(raw[c.player+0x2f4+n*4:c.player+0x2f8+n*4] for n in (12,13,14,15,17,18,19,20,21))
        struct.pack_into('<I',raw,c.fingerprints+32,(zlib.adler32(armor)*2)&0xffffffff)
        start,length=s.elden_ring.blocks[0];raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
        s=Save(raw,'eldenring');self.assertEqual(s.elden_ring.spell_loadouts[0].capacity,4)
        choices=s.elden_ring.spell_loadouts[0].operations['spell_slot:0'][1]
        output=s.patched({(0,'spell_slot:0'):choices.index(4200)})
        self.assertFalse(Save(output,'eldenring').warnings)
        bad=bytearray(raw);struct.pack_into('<I',bad,c.fingerprints+32,123)
        bad[start:start+16]=hashlib.md5(bad[start+16:start+length]).digest()
        self.assertFalse(Save(bad,'eldenring').elden_ring.spell_loadouts[0].fields)

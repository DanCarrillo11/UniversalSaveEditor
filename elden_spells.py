"""Owned spell loadouts with native compact records and memory-cost checks.

SPDX-License-Identifier: GPL-3.0-or-later. Independently implemented from
SaveForge's documented slot, sentinel and fingerprint facts; see SOURCES.md.
"""
import struct
import zlib
from collections import Counter
from elden_spells_table import SPELLS

EMPTY = 0xffffffff


def spell_hash(ids):
    return (zlib.adler32(struct.pack('<14I', *ids)) * 2) & 0xffffffff


class SpellLoadout:
    def __init__(self, raw, offset, held, player, fingerprints, Field):
        self.fields = []; self.operations = {}; self.offset = offset
        self.fingerprints = fingerprints
        self.original = [struct.unpack_from('<2I', raw, offset + i * 8) for i in range(14)]
        self.active = struct.unpack_from('<I', raw, offset + 112)[0]
        common = [struct.unpack_from('<3I', raw, held + 4 + i * 12) for i in range(0xa80)]
        keys_at = held + 8 + 0xa80 * 12
        keys = [struct.unpack_from('<3I', raw, keys_at + i * 12) for i in range(0x180)]
        live = [(h, q) for h, q, _ in common + keys if h not in (0, EMPTY) and q]
        identities = Counter(h for h, q in live)
        self.owned = {h & 0x0fffffff for h, q in live
                      if h >> 28 == 11 and h & 0x0fffffff in SPELLS
                      and q == 1 and identities[h] == 1}
        stones = [q & 0x7fffffff for h, q, _ in common if h == 0xb000272e and q]
        if not stones: stones = [q & 0x7fffffff for h, q, _ in keys if h == 0xb000272e and q]
        if len(stones) > 1 or any(q > 8 for q in stones): return
        self.capacity = 2 + (stones[0] if stones else 0)
        talisman_count = raw[player + 0xbe] + 1
        if not 1 <= talisman_count <= 4: return
        for i in range(talisman_count):
            talisman = struct.unpack_from('<I', raw, player + 0x2f4 + (17 + i) * 4)[0]
            if talisman in (0x474, 0x20000474):
                armor = b''.join(raw[player + 0x2f4 + n * 4:player + 0x2f8 + n * 4]
                                 for n in (12,13,14,15,17,18,19,20,21))
                if struct.unpack_from('<I',raw,fingerprints + 32)[0] != (zlib.adler32(armor) * 2) & 0xffffffff:
                    return
                self.capacity += 2; break
        occupied = []; empty_seen = False
        for identifier, follower in self.original:
            if identifier == EMPTY and follower == 0:
                empty_seen = True; continue
            if empty_seen or identifier not in self.owned or follower != EMPTY: return
            occupied.append(identifier)
        if len(set(occupied)) != len(occupied): return
        if sum(SPELLS[i][2] for i in occupied) > self.capacity: return
        if (occupied and self.active >= len(occupied)) or (not occupied and self.active != EMPTY): return
        if struct.unpack_from('<I', raw, fingerprints + 40)[0] != spell_hash([i for i, _ in self.original]): return
        options = (EMPTY,) + tuple(sorted(self.owned, key=lambda i: SPELLS[i][0]))
        for i, (identifier, _) in enumerate(self.original):
            key = f'spell_slot:{i}'; self.operations[key] = (i, options)
            self.fields.append(Field(key, f'Memory {i + 1}', options.index(identifier), offset + i * 8, '',
                                     0, len(options) - 1, 'Spells', collection='Memorized spells',
                                     choices=('Empty',) + tuple(f'{SPELLS[n][0]} · {SPELLS[n][2]} memory slot(s)' for n in options[1:]),
                                     note=f'Owned spells only; {self.capacity} memory slots available. Entries compact on apply, duplicates and excess cost are rejected. Acquisition and quest flags are preserved.'))
        self.fields.append(Field('active_spell', 'Active spell position', 14 if self.active == EMPTY else self.active,
                                 offset + 112, '', 0, 14, 'Spells', collection='Memorized spells',
                                 choices=tuple(f'Memory {i + 1}' for i in range(14)) + ('None',),
                                 note='Position in the final compact spell list. None is valid only when the list is empty.'))

    def patch(self, result, changes):
        if not any(k in self.operations or k == 'active_spell' for k in changes): return
        ids = [i for i, _ in self.original]
        for key, value in changes.items():
            if key in self.operations:
                i, options = self.operations[key]; ids[i] = options[value]
        ids = [i for i in ids if i != EMPTY]
        if len(set(ids)) != len(ids): raise ValueError('A spell cannot appear twice in the memorized loadout.')
        if sum(SPELLS[i][2] for i in ids) > self.capacity:
            raise ValueError('The memorized spells exceed the available memory-slot capacity.')
        active = changes.get('active_spell', self.active)
        if 'active_spell' in changes:
            active = EMPTY if active == 14 else active
            if (ids and active >= len(ids)) or (not ids and active != EMPTY):
                raise ValueError('The active spell position must point to the final memorized loadout.')
        elif not ids: active = EMPTY
        elif active >= len(ids): active = 0
        padded = ids + [EMPTY] * (14 - len(ids))
        for i, identifier in enumerate(padded):
            struct.pack_into('<2I', result, self.offset + i * 8, identifier, 0 if identifier == EMPTY else EMPTY)
        struct.pack_into('<I', result, self.offset + 112, active)
        struct.pack_into('<I', result, self.fingerprints + 40, spell_hash(padded))

    def verifies(self, parsed, changes):
        """Compare the whole compact list, rather than its pre-compaction row."""
        expected = [i for i, _ in self.original]
        for key, value in changes.items():
            if key in self.operations:
                index, options = self.operations[key]; expected[index] = options[value]
        expected = [i for i in expected if i != EMPTY]
        pairs = [(i, EMPTY) for i in expected] + [(EMPTY, 0)] * (14 - len(expected))
        if pairs != parsed.original or not parsed.fields: return False
        if 'active_spell' in changes:
            active = EMPTY if changes['active_spell'] == 14 else changes['active_spell']
        elif not expected: active = EMPTY
        else: active = self.active if self.active < len(expected) else 0
        return parsed.active == active

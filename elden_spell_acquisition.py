"""Monotonic learning of mapped base-game spells in native goods records.

SPDX-License-Identifier: GPL-3.0-or-later. Spell goods, quantities and registry
facts: pinned SaveForge data/core writers. No quest flags or DLC grants.
"""
from collections import defaultdict
import struct
from elden_registry import registry_records
from elden_spells_table import SPELLS


class SpellAcquisition:
    def __init__(self, raw, held, registry, Field):
        self.fields = []
        self.operations = {}
        try:
            registry_records(raw, registry)
        except ValueError:
            return
        common = [struct.unpack_from('<3I', raw, held + 4 + i * 12) for i in range(0xa80)]
        key_start = held + 8 + 0xa80 * 12
        keys = [struct.unpack_from('<3I', raw, key_start + i * 12) for i in range(0x180)]
        active = lambda rows: sum(h not in (0, 0xffffffff) for h, _, _ in rows)
        if struct.unpack_from('<I', raw, held)[0] != active(common): return
        if struct.unpack_from('<I', raw, key_start - 4)[0] != active(keys): return
        clean_empty = any(row == (0, 0, 0) for row in common)
        records = defaultdict(list)
        for container, rows in (('common', common), ('key', keys)):
            for index, (handle, quantity, acquired) in enumerate(rows):
                if handle >> 28 == 11:
                    records[handle & 0x0fffffff].append((container, index, quantity))
        for identifier, (name, category, _) in SPELLS.items():
            found = records.get(identifier, [])
            if len(found) > 1 or (found and found[0][2] != 1):
                continue  # A duplicated or malformed ownership entry is not overwritten.
            owned = bool(found and found[0][2] == 1)
            # DLC content needs a separately verified save-version/entitlement
            # gate. Existing ownership can be inspected, but no DLC spell added.
            if identifier >= 2000000 and not owned: continue
            if not owned and not clean_empty:
                continue
            key = f'learn_spell:{identifier}'
            self.fields.append(Field(key, name, int(owned), held, '', int(owned), 1,
                'Spell collection', boolean=True, readonly=owned, collection=category,
                item_id=0x40000000 | identifier,
                note=('Already learned. Removal is disabled to preserve memorized spells and ownership references.' if owned else
                      'Learns one mapped base-game spell, registers its goods ID and updates acquisition counters. Quest, vendor and achievement flags are preserved. Apply to make it available in the memory selectors; character casting requirements still apply.')))
            if not owned: self.operations[key] = identifier

    def patch(self, result, changes, character, add_goods):
        for key, value in changes.items():
            if key in self.operations and value:
                add_goods(result, character, self.operations[key], 1)

"""Recognized KH1 ownership counts and carried-item stock transactions.

KH1's accessory/weapon counts include equipped copies; consumable stock does
not. Facts: KHSave.Lib1's character/inventory model and native PC references;
see SOURCES.md. No story weapons, hidden slots or unknown IDs are synthesized.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from collections import Counter
from kh_items import ITEMS

ITEMS_BY_ID = {i: (name, kind) for i, name, kind in ITEMS}
ACCESSORIES = {i for i, (_, kind) in ITEMS_BY_ID.items() if kind == 'Accessory'}
CONSUMABLES = {i for i, (_, kind) in ITEMS_BY_ID.items() if kind == 'Consumable'}
WEAPONS = {i for i, (_, kind) in ITEMS_BY_ID.items() if kind in ('Keyblade', 'Staff', 'Shield')}
TEMPORARY_WEAPONS = {82, 83, 84, 85}


class Kh1Inventory:
    def __init__(self, raw):
        self.raw = raw
        self.records = {}

    def record(self, slot, record):
        self.records[slot] = record

    @staticmethod
    def slots(raw, record):
        slots = {}; accessory_counts_known = True
        for c in (0, 1, 2, 3, 5, 6, 7, 8, 9):
            base = record + 4 + c * 0x74
            if not 1 <= raw[base] <= 100:
                # An absent/unsupported character is not a source of stock.
                if raw[base]: accessory_counts_known = False
                continue
            if c < 3:
                slots[f'{c}:weapon'] = (base + 0x32, ({'Keyblade'}, {'Staff'}, {'Shield'})[c])
            for count_at, array_at, maximum, kind, title in (
                    (0x18, 0x19, 8, 'Accessory', 'accessory'),
                    (0x21, 0x22, 12, 'Consumable', 'item')):
                count = raw[base + count_at]
                if count > maximum:
                    if kind == 'Accessory': accessory_counts_known = False
                    continue
                for n in range(count):
                    slots[f'{c}:{title}:{n}'] = (base + array_at + n, {kind})
        return slots, accessory_counts_known

    @staticmethod
    def owned_equipped(raw, slots):
        counts = Counter()
        for offset, kinds in slots.values():
            identity = raw[offset]
            if kinds == {'Accessory'} and identity in ACCESSORIES: counts[identity] += 1
            elif identity in WEAPONS - TEMPORARY_WEAPONS and ITEMS_BY_ID[identity][1] in kinds:
                counts[identity] = max(1, counts[identity])
        return counts

    def finish(self, result, changes):
        for slot, record in self.records.items():
            edits = {key for i, key in changes if i == slot}
            slots, known = self.slots(self.raw, record)
            for key in edits - slots.keys():
                parts = key.split(':')
                if not parts[0].isdigit() or not 0 <= int(parts[0]) < 10: continue
                delta = (0x32 if len(parts) == 2 and parts[1] == 'weapon' else
                         0x19 + int(parts[2]) if len(parts) == 3 and parts[1] == 'accessory' else
                         0x22 + int(parts[2]) if len(parts) == 3 and parts[1] == 'item' else None)
                if delta is None: continue
                offset = record + 4 + int(parts[0]) * 0x74 + delta
                if self.raw[offset] != result[offset]:
                    raise ValueError('KH1 equipment cannot be synchronized for an absent or unsupported character.')
            changed = {key for key in edits & slots.keys()
                       if self.raw[slots[key][0]] != result[slots[key][0]]}
            touched = set(); transfers = Counter()
            for key in changed:
                offset, kinds = slots[key]; old, new = self.raw[offset], result[offset]
                for identity in (old, new):
                    if identity and ITEMS_BY_ID.get(identity, (None, None))[1] not in kinds:
                        raise ValueError('Cannot synchronize an unidentified KH1 equipment entry.')
                if kinds == {'Consumable'}:
                    if old: transfers[old] += 1
                    if new: transfers[new] -= 1
                else:
                    if new in TEMPORARY_WEAPONS:
                        raise ValueError('Temporary KH1 story weapons cannot be acquired by changing equipment.')
                    touched.update(i for i in (old, new) if i and i not in TEMPORARY_WEAPONS)

            for identity, amount in transfers.items():
                if not amount: continue  # Atomic swaps require no spare stock.
                offset = record + 0x499 + identity
                if self.raw[offset] > 99 or not 0 <= result[offset] + amount <= 99:
                    raise ValueError(f'KH1 {ITEMS_BY_ID[identity][0]} needs enough reserve stock and space (0–99). '
                                     'Adjust its inventory quantity in the same edit, or swap carried copies.')
                result[offset] += amount

            before = self.owned_equipped(self.raw, slots)
            after = self.owned_equipped(result, slots)
            for identity in ACCESSORIES | (WEAPONS - TEMPORARY_WEAPONS):
                key = f'inventory:{identity}'; offset = record + 0x499 + identity
                explicit = key in edits
                if identity not in touched and not explicit: continue
                if identity in ACCESSORIES and not known:
                    raise ValueError('KH1 accessory ownership cannot be synchronized with unsupported character slot counts.')
                required = after[identity]; available = result[offset]
                previous_deficit = max(0, before[identity] - self.raw[offset])
                if explicit:
                    if max(0, required - available) > previous_deficit or (
                            required > before[identity] and available < required):
                        raise ValueError(f'KH1 {ITEMS_BY_ID[identity][0]} needs at least {required} owned '
                                         'copies for the selected equipment. Increase its quantity or unequip copies.')
                elif required > before[identity] and available < required:
                    if self.raw[offset] > 99 or required > 99:
                        raise ValueError('KH1 equipment ownership is outside the supported quantity range.')
                    result[offset] = required
        return result

    def expected_stock(self, slot, key, value, changes, encodings):
        """Reparse verification accounts for the requested carried-item transfer."""
        identity = int(key.split(':')[1])
        if identity not in CONSUMABLES: return value
        slots, _ = self.slots(self.raw, self.records[slot]); adjustment = 0
        for equipment_key, (offset, kinds) in slots.items():
            pair = slot, equipment_key
            if kinds != {'Consumable'} or pair not in changes: continue
            before = self.raw[offset]
            after = encodings[pair][2][changes[pair]]
            adjustment += int(before == identity) - int(after == identity)
        return value + adjustment

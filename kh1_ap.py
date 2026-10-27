"""Recognized KH1 Final Mix learned-ability AP and accessory budgets.

SPDX-License-Identifier: GPL-3.0-or-later
Independent calculations from factual PC table bytes. See SOURCES.md.
Unknown active ability costs, accessories and modified tables are not inferred.
"""

# IDs follow the documented original ability order, not translated labels.
ABILITY_AP = {5: 2, 6: 1, 7: 1, 8: 2, 9: 3, 10: 1, 11: 3, 12: 4, 13: 3,
    14: 4, 15: 1, 16: 1, 17: 1, 18: 2, 19: 2, 20: 2, 21: 2, 22: 1, 23: 3,
    24: 3, 25: 5, 26: 1, 27: 2, 28: 2, 29: 1, 30: 1, 31: 2, 32: 3, 33: 2,
    34: 2, 35: 3, 36: 3, 37: 2, 38: 2, 39: 1, 40: 2, 41: 2, 42: 3, 43: 3,
    44: 2, 45: 4, 46: 3, 47: 2, 48: 3, 49: 1, 50: 3, 51: 3, 52: 3, 53: 1,
    54: 1, 55: 2, 56: 3, 57: 2, 58: 2, 59: 2, 60: 2, 61: 1, 62: 5, 63: 3}
ACCESSORY_AP = {i: 0 for i in range(17, 72) if i != 57}  # Unnamed ID 57 stays unknown.
ACCESSORY_AP.update({29: 2, 30: 3, 31: 4, 47: 3, 49: 1, 51: 1, 53: 3,
                     60: 2, 66: 3, 67: 2, 68: 2})


class Kh1Ap:
    def __init__(self, raw, Field, names):
        self.raw, self.Field, self.names = raw, Field, names
        self.characters = {}

    @staticmethod
    def budget(raw, base):
        if not 1 <= raw[base] <= 100:
            return None
        count = raw[base + 0x18]
        if count > 8:
            return None
        accessories = raw[base + 0x19:base + 0x19 + count]
        if any(i and i not in ACCESSORY_AP for i in accessories):
            return None
        used = 0
        for value in raw[base + 0x40:base + 0x70]:
            # KH1 uses bit 7 for UNEQUIPPED; duplicate active entries each cost AP.
            if value & 0x80 or not value:
                continue
            if value not in ABILITY_AP:
                return None
            used += ABILITY_AP[value]
        capacity = raw[base + 5] + sum(ACCESSORY_AP.get(i, 0) for i in accessories)
        return (used, capacity) if capacity <= 255 else None

    def character(self, fields, slot, character, base):
        self.characters[slot, character] = base
        budget = self.budget(self.raw, base)
        if budget is None:
            return
        used, capacity = budget
        for key, label, value in (('ap_used', 'Equipped ability AP', used),
                                  ('ap_capacity', 'Available AP', capacity)):
            fields.append(self.Field(f'{character}:{key}', self.names[character] + ' · ' + label,
                value, 0, '', 0, 255, 'Abilities', readonly=True,
                note='Calculated from recognized standard Final Mix ability costs, saved base AP and equipped accessory bonuses. Duplicate equipped entries each consume AP. Unknown active costs or accessory identities hide this calculation; modified game tables can differ.'))

    def finish(self, result, changes):
        for (slot, character), base in self.characters.items():
            prefix = f'{character}:'
            edits = [key for (index, key) in changes if index == slot]
            if not any(key == prefix + 'ap' or key.startswith(prefix + 'ability:') or
                       key.startswith(prefix + 'accessory:') for key in edits):
                continue
            before, after = self.budget(self.raw, base), self.budget(result, base)
            if before is None or after is None:
                continue
            if max(0, after[0] - after[1]) > max(0, before[0] - before[1]):
                raise ValueError(f'KH1 AP budget: {self.names[character]} equipped abilities need '
                    f'{after[0]} AP but only {after[1]} AP is available. Increase base AP, '
                    'choose an accessory with enough AP, or unequip abilities in the same change.')
        return result

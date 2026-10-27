"""Recognized KH1 PC equipment bonuses and coupled current HP/MP changes.

SPDX-License-Identifier: GPL-3.0-or-later
Independent calculations from original PC table facts. See SOURCES.md.
No inference is made for unknown equipment, runtime effects or modified tables.
"""
ACCESSORIES = {i: (0, 0) for i in range(17, 72) if i != 57}
ACCESSORIES.update({39:(3,0),40:(6,0),41:(9,0),42:(0,1),43:(0,1),44:(0,2),
    45:(3,0),47:(6,1),48:(3,0),52:(3,1),55:(3,0),58:(0,1),65:(0,2),
    67:(6,1),68:(9,2),69:(0,2)})
WEAPON_MP = {i: 0 for i in (*range(81, 118), *range(119, 134))}
WEAPON_MP.update({88:1,90:1,92:2,94:1,95:-1,96:1,97:-1,98:2,100:2,101:3,
    102:-2,106:1,107:1,108:-1,109:-1,110:-1,111:1,112:-1,113:2,114:2,
    115:2,117:3,129:1,130:2,131:1,133:3})


class Kh1Vitals:
    def __init__(self, raw, Field, names):
        self.raw, self.Field, self.names = raw, Field, names
        self.characters = {}

    @staticmethod
    def maximum(raw, base, character, kind):
        if not 1 <= raw[base] <= 100 or not raw[base + (2 if kind == 'hp' else 4)]:
            return None
        count = raw[base + 0x18]
        if count > 8:
            return None
        accessories = raw[base + 0x19:base + 0x19 + count]
        if any(i and i not in ACCESSORIES for i in accessories):
            return None
        part = 0 if kind == 'hp' else 1
        value = raw[base + (2 if kind == 'hp' else 4)] + sum(ACCESSORIES[i][part] for i in accessories if i)
        if kind == 'mp':
            weapon = raw[base + 0x32]
            supported = ((81 <= weapon <= 102) if character == 0 else
                         (103 <= weapon <= 117) if character == 1 else
                         (119 <= weapon <= 133) if character == 2 else False)
            if not supported:
                return None
            value += WEAPON_MP[weapon]
        return value

    def character(self, fields, slot, character, base):
        self.characters[slot, character] = base
        for kind in ('hp', 'mp'):
            maximum = self.maximum(self.raw, base, character, kind)
            if maximum is None or not 1 <= maximum <= 255:
                continue
            prefix = f'{character}:'
            fields.append(self.Field(prefix + kind + '_effective_max',
                self.names[character] + ' · Maximum ' + kind.upper() + ' with equipment',
                maximum, 0, '', 1, 255, 'Attributes', readonly=True,
                note='Saved base plus recognized standard equipped bonuses. MP includes signed weapon bonuses. Current values are not increased automatically; reducing a recognized maximum clamps a previously valid current value unless an explicit conflicting value is requested. Runtime effects, modified game tables and unknown identities are not inferred.'))
            for f in fields:
                if f.key in (prefix + kind, prefix + kind + '_current'):
                    f.note += (' ' if f.note else '') + 'Equipment bonuses contribute to the recognized maximum; base, equipment and current values are checked together.'

    def finish(self, result, changes):
        for (slot, character), base in self.characters.items():
            edits = {key: value for (index, key), value in changes.items() if index == slot}
            prefix = f'{character}:'
            for kind, delta in (('hp', 1), ('mp', 3)):
                current_key = prefix + kind + '_current'
                affected = (current_key in edits or prefix + kind in edits or
                    any(k.startswith(prefix + 'accessory:') for k in edits) or
                    (kind == 'mp' and prefix + 'weapon' in edits))
                if not affected:
                    continue
                before = self.maximum(self.raw, base, character, kind)
                after = self.maximum(result, base, character, kind)
                if before is None or after is None or not 1 <= before <= 255:
                    continue
                if not 1 <= after <= 255:
                    raise ValueError(f'KH1 {self.names[character]}: maximum {kind.upper()} with this equipment is outside the supported range. Adjust the base value or equipment together.')
                original_current = self.raw[base + delta]
                if current_key not in edits and original_current <= before:
                    result[base + delta] = min(result[base + delta], after)
                elif max(0, result[base + delta] - after) > max(0, original_current - before):
                    raise ValueError(f'KH1 {self.names[character]}: current {kind.upper()} exceeds the recognized maximum of {after}. Adjust the current value, base or equipment together.')
        return result

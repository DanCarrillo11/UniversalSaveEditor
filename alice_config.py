"""Alice Steam PC configuration archive (revision 16).

SPDX-License-Identifier: GPL-3.0-or-later
Only mapped gameplay fields are editable; settings and UI records are preserved.
"""
import math
import struct
from alice_profile import Archive


class AliceConfig:
    def __init__(self, raw, Field):
        self.fields = []
        self.scalars = {}
        reader = Archive(raw)
        if (reader.number(), reader.number()) != (16, 0xf223):
            raise ValueError('expected Steam PC configuration revision 16')
        choices = ('Easy', 'Normal', 'Hard', 'Nightmare')
        for key, label, note in (
            ('current_difficulty', 'Current difficulty',
             'Lowering difficulty also lowers the recorded minimum when necessary.'),
            ('lowest_difficulty', 'Lowest difficulty used',
             'Historical value used by the game for completion difficulty. Must not exceed the current difficulty.'),
        ):
            offset = reader.pos
            value = reader.number()
            field = Field(key, label, value, offset, '<i', 0, 3, 'Difficulty',
                          choices=choices, note=note)
            field.validate(value)
            self.fields.append(field)
            self.scalars[key] = (offset, '<i', value)
        # Twenty settings follow the two difficulty values. Float members must
        # be finite; all remain byte-for-byte untouched when editing gameplay.
        for index in range(2, 22):
            fmt = '<f' if index in (2, 4, 5, 6, 10) else '<i'
            if not math.isfinite(reader.number(fmt)):
                raise ValueError('non-finite configuration setting')
        for _ in range(66):
            reader.string()  # Keyboard and controller bindings.
        reader.number()  # Attack type.
        if not math.isfinite(reader.number('<f')):
            raise ValueError('non-finite mouse sensitivity')
        reader.number()  # Lock-on type.
        reader.take((100 + 100 + 100 + 50 + 1) * 4)
        if reader.pos != len(raw):
            raise ValueError('unexpected trailing configuration data')

    def patch(self, result, changes):
        current = changes.get('current_difficulty', self.scalars['current_difficulty'][2])
        lowest = changes.get('lowest_difficulty', self.scalars['lowest_difficulty'][2])
        if 'lowest_difficulty' in changes and lowest > current:
            raise ValueError('Lowest difficulty used must not exceed the current difficulty.')
        if 'current_difficulty' in changes and lowest > current:
            struct.pack_into('<i', result, self.scalars['lowest_difficulty'][0], current)
        return result

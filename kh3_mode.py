"""Known Critical-mode side effects for the supported KH3 PC layout.

SPDX-License-Identifier: GPL-3.0-or-later. Layout and observed word facts
cross-checked with thirteenth-order/kh3-save-editor at 0e09edce; see SOURCES.md.
Unknown ability words, equipment sources and absent party records are retained.
"""
import struct
from kh3_characters import CHARACTERS

CRITICAL_ABILITIES = (0x68, 0x69, 0x6a)
ABSENT = 0x444
INNATE = (0x449, 0x44b)


def synchronize_mode(original, result, changes):
    if 'difficulty' not in changes or changes['difficulty'] == original[0x14]:
        return
    old, target = original[0x14], changes['difficulty']
    if (old == 3) == (target == 3):
        return
    for name_index, name in enumerate(CHARACTERS):
        base = 0x1880 + name_index * 0x9c0
        for stat, delta in (('hp', 0x984), ('mp', 0x988)):
            key = f'character:{name}:{stat}'
            current = struct.unpack_from('<i', original, base + delta)[0]
            if key in changes or current <= 0:
                continue
            value = max(1, current // 2) if target == 3 else current * 2
            if value > 9999:
                raise ValueError('Critical-mode health conversion exceeds the supported range. Set an explicit HP/MP value for this character.')
            struct.pack_into('<i', result, base + delta, value)
    for identifier in CRITICAL_ABILITIES:
        offset = 0x1880 + 0x160 + identifier * 4
        word = struct.unpack_from('<I', original, offset)[0]
        key = f'character:Sora:ability:{identifier}'
        if key in changes:
            if target == 3 and changes[key] == 0:
                raise ValueError('Critical-mode abilities cannot be removed while entering Critical. Keep them learned or change the difficulty selection.')
            if target == 3 and word == ABSENT:
                struct.pack_into('<I', result, offset, 0x449 if changes[key] == 1 else 0x44b)
            continue
        if target == 3 and word == ABSENT:
            struct.pack_into('<I', result, offset, 0x44b)
        elif target != 3 and word in INNATE:
            struct.pack_into('<I', result, offset, ABSENT)


def synchronize_munny(original, result, changes):
    if 'munny' not in changes:
        return
    earned, spent = struct.unpack_from('<2I', original, 0x840)
    balance = struct.unpack_from('<i', original, 0x28)[0]
    if earned >= spent and earned - spent == balance:
        updated = spent + changes['munny']
        if updated > 0xffffffff:
            raise ValueError('Munny exceeds the available saved ledger range.')
        struct.pack_into('<I', result, 0x840, updated)

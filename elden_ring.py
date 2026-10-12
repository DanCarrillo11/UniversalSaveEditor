"""Bounded, byte-preserving Steam SL2 editor.

SPDX-License-Identifier: GPL-3.0-or-later
Independent implementation from format facts; see docs/ELDEN_RING_FORMAT.md.
"""
from dataclasses import dataclass
import hashlib
import struct
import zlib
from elden_items import GOODS
from collection_tables import ELDEN_CATEGORIES

SLOT_SIZE = 0x280000
BLOCK_SIZE = SLOT_SIZE + 16
GLOBAL_START = 0x300 + 10 * BLOCK_SIZE
FILE_SIZE = GLOBAL_START + 0x60010 + 0x240020
STATS = ('Vigor', 'Mind', 'Endurance', 'Strength', 'Dexterity', 'Intelligence', 'Faith', 'Arcane')
CLASS_MINIMUMS = (
    (15,10,11,14,13,9,9,7), (11,12,11,10,16,10,8,9),
    (14,9,12,16,9,7,8,11), (10,11,10,9,13,9,8,14),
    (9,15,9,8,12,16,7,9), (10,14,8,11,10,7,16,10),
    (12,11,13,12,15,9,8,8), (11,12,11,11,14,14,6,9),
    (10,13,10,12,12,9,14,9), (10,10,10,10,10,10,10,10),
    (10,12,11,13,15,8,11,6), (14,8,17,15,11,7,8,9),
)


def number(raw, offset):
    return struct.unpack_from('<I', raw, offset)[0]


def player_hash(data):
    """Short field fingerprints: twice Adler-32, modulo 2**32."""
    return (zlib.adler32(data) * 2) & 0xffffffff


class Cursor:
    def __init__(self, raw, start, end):
        self.raw, self.pos, self.end = raw, start, end

    def skip(self, length):
        if length < 0 or length > self.end - self.pos:
            raise ValueError('An Elden Ring section exceeds its character block.')
        start = self.pos
        self.pos += length
        return start

    def integer(self):
        return number(self.raw, self.skip(4))

    def array(self, size, maximum):
        count = self.integer()
        if count > maximum:
            raise ValueError('Unsupported Elden Ring array length.')
        self.skip(count * size)
        return count

    def blob(self, maximum=0x10000):
        length = self.integer()
        if length > maximum:
            raise ValueError('Unsupported Elden Ring section length.')
        self.skip(length)

    def menu(self):
        self.skip(4)
        self.blob()


@dataclass
class Character:
    physical: int
    start: int
    player: int
    profile: int
    fingerprints: int


class EldenRingSave:
    def __init__(self, raw, field_type, slot_type):
        if len(raw) != FILE_SIZE or raw[:4] != b'BND4' or number(raw, 12) != 12:
            raise ValueError('Unsupported Elden Ring Steam SL2 container. Choose ER0000.sl2 from the original game.')
        self.raw, self.slots, self.characters, self.warnings = raw, [], [], []
        self.blocks = [(0x300 + i * BLOCK_SIZE, BLOCK_SIZE) for i in range(10)]
        self.blocks += [(GLOBAL_START, 0x60010), (GLOBAL_START + 0x60010, 0x240020)]
        for index, (start, length) in enumerate(self.blocks):
            entry = 0x40 + index * 0x20
            if struct.unpack_from('<Q', raw, entry + 8)[0] != length or number(raw, entry + 16) != start:
                raise ValueError('Unsupported Elden Ring block table.')
            if raw[start:start+16] != hashlib.md5(raw[start+16:start+length]).digest():
                self.warnings.append(f'Block {index+1}: integrity check does not match. Applying requires explicit integrity repair.')
        global_data = GLOBAL_START + 16
        menu_size = number(raw, global_data + 0x150)
        if menu_size > 0x10000:
            raise ValueError('Unsupported Elden Ring global menu section.')
        active = global_data + 0x154 + menu_size
        if active + 10 + 10 * 0x24c > GLOBAL_START + 0x60010 or any(v not in (0, 1) for v in raw[active:active+10]):
            raise ValueError('Invalid Elden Ring active-character table.')
        for physical in range(10):
            if not raw[active+physical]:
                continue  # Deleted characters may retain data; never resurrect them.
            start = self.blocks[physical][0] + 16
            cursor = Cursor(raw, start, start+SLOT_SIZE)
            version = cursor.integer()
            if not 65 <= version <= 261:
                raise ValueError(f'Character {physical+1}: save revision {version} is not supported by this editor. Check for an application update; the file has not been changed.')
            cursor.skip(28)
            for _ in range(5118 if version <= 81 else 5120):
                handle = cursor.integer()
                identifier = cursor.integer()
                if handle >> 28 not in (0, 8, 9, 12) or (identifier != 0xffffffff and identifier >> 28 not in (0, 1, 8)):
                    raise ValueError('Unsupported Elden Ring equipment-handle table.')
                if handle >> 28 == 8:
                    cursor.skip(12)
                    if raw[cursor.skip(1)] != 0:
                        raise ValueError('Unsupported Elden Ring weapon record.')
                elif handle >> 28 == 9:
                    cursor.skip(8)
            player = cursor.skip(0x1b0)
            archetype = raw[player+0xb7]
            if archetype >= len(CLASS_MINIMUMS) or number(raw, player+0xb4) & 0xffff:
                raise ValueError('Unsupported Elden Ring character identity.')
            try:
                name = raw[player+0x94:player+0xb4].decode('utf-16-le').split('\0')[0].strip()
            except UnicodeError as error:
                raise ValueError('Invalid Elden Ring character name.') from error
            if not name:
                raise ValueError('An active Elden Ring character has no name.')
            profile = active + 10 + physical * 0x24c
            stats = struct.unpack_from('<8I', raw, player+0x34)
            level, runes, memory = struct.unpack_from('<3I', raw, player+0x60)
            if level != sum(stats)-79 or number(raw, profile+34) != level or number(raw, profile+42) != memory:
                raise ValueError('Character progression and menu summary disagree; this variant cannot be edited.')
            fields = []

            def add(key, label, offset, low, high, group, **options):
                value = number(raw, offset)
                if not low <= value <= high:
                    raise ValueError(f'Character {physical+1}: unsupported {label.lower()} value.')
                fields.append(field_type(key, label, value, offset, '<I', low, high, group, **options))

            add('runes', 'Runes', player+0x64, 0, 999999999, 'Currency',
                note='Adding runes also increases the lifetime rune total. Spending or removing runes keeps that total.')
            add('runes_memory', 'Lifetime runes', player+0x68, 0, 0xffffffff, 'Currency', readonly=True,
                note='Calculated automatically when runes are added.')
            add('level', 'Level', player+0x60, 1, 713, 'Attributes', readonly=True,
                note='Calculated from the eight attributes when changes are applied.')
            for index, label in enumerate(STATS):
                add(label.lower(), label, player+0x34+index*4, min(stats[index],CLASS_MINIMUMS[archetype][index]), 99, 'Attributes',
                    note='Cannot fall below the original starting class. Level and character-menu summary update together.')
            for key, label, offset, max_offset in (('hp','Current HP',8,12), ('fp','Current FP',20,24), ('stamina','Current stamina',36,40)):
                maximum=max(number(raw,player+offset),number(raw,player+max_offset))
                if maximum>65535:raise ValueError('Unsupported Elden Ring vital range.')
                add(key, label, player+offset, 0, maximum, 'Vitals',
                    note='Maximum and base values are preserved; the game recalculates derived values from attributes.')
            cursor.skip(0xd0+0x58+0x1c+0x58+0x58)
            self._inventory(cursor, fields, field_type, 0xa80, 0x180, 'Inventory')
            cursor.skip(116+140+24)
            cursor.array(8, 4096)  # Acquired projectile records.
            cursor.skip(156+12+303)
            self._inventory(cursor, fields, field_type, 0x780, 0x80, 'Storage')
            cursor.skip(256)
            cursor.array(4, 4096)  # Unlocked regions are preserved.
            cursor.skip(117)
            cursor.menu()
            cursor.skip(52+112008)
            cursor.menu()  # Tutorial payload.
            cursor.skip(29+0x1bf9a0)
            for maximum in (0x10000, 0x10000, 0x100000, 0x100000, 0x100000):
                cursor.blob(maximum)
            cursor.skip(61+10+(4 if version >= 65 else 0)+(1 if version >= 66 else 0))
            cursor.skip(0x20004+12+12+16+8+32+50)
            fingerprints = cursor.skip(128)
            for relative, data in self._fingerprint_data(raw, player):
                if number(raw, fingerprints+relative) != player_hash(data):
                    raise ValueError('Unsupported Elden Ring player fingerprint. The file will not be edited.')
            self.characters.append(Character(physical, start, player, profile, fingerprints))
            self.slots.append(slot_type(f'Character {physical+1} · {name}', fields))
        if not self.slots:
            raise ValueError('No active Elden Ring characters were found. Save a character in the game first.')

    @staticmethod
    def _fingerprint_data(raw, player):
        return ((0, raw[player+0x60:player+0x64]),
                (4, raw[player+0x34:player+0x58]),
                (8, struct.pack('<I', raw[player+0xb7])),
                (12, raw[player+0xb8:player+0xb9]),
                (20, raw[player+0x64:player+0x68]),
                (24, raw[player+0x68:player+0x6c]))

    @staticmethod
    def _inventory(cursor, fields, field_type, capacity, key_capacity, group):
        count = cursor.integer()
        if count > capacity:
            raise ValueError('Invalid Elden Ring inventory count.')
        for index in range(capacity):
            offset = cursor.skip(12)
            handle, quantity, acquisition = struct.unpack_from('<3I', cursor.raw, offset)
            if quantity > 999:
                raise ValueError('Invalid Elden Ring inventory quantity.')
            item = GOODS.get(handle & 0x0fffffff) if handle >> 28 == 11 else None
            if not item or not quantity:
                continue
            label, held_limit, storage_limit = item
            limit = held_limit if group == 'Inventory' else storage_limit
            if limit <= 1 or quantity > limit:
                continue
            fields.append(field_type(f'{group.lower()}:{index}', label, quantity, offset+4, '<I', 1, limit, group,
                note=f'Existing stack · item {handle & 0x0fffffff} · record {index+1}. Item identity is preserved.',
                collection=ELDEN_CATEGORIES[handle & 0x0fffffff]))
        key_count = cursor.integer()
        if key_count > key_capacity:
            raise ValueError('Invalid Elden Ring key-item count.')
        cursor.skip(key_capacity*12+8)

    def finish(self, result, changes, repair_crc):
        touched = {index for index, key in changes}
        global_changed = False
        for index in touched:
            character = self.characters[index]
            player = character.player
            for key,offset,max_offset in (('hp',8,12),('fp',20,24),('stamina',36,40)):
                if (index,key) in changes and number(result,player+offset)>number(self.raw,player+max_offset):
                    raise ValueError('Current vitals cannot be changed above the saved maximum.')
            for stat_index, label in enumerate(STATS):
                if (index,label.lower()) in changes and number(result,player+0x34+stat_index*4) < CLASS_MINIMUMS[result[player+0xb7]][stat_index]:
                    raise ValueError(f'{label} cannot be changed below the original starting class minimum.')
            if any((index, label.lower()) in changes for label in STATS):
                level = sum(struct.unpack_from('<8I', result, player+0x34))-79
                if not 1 <= level <= 713:
                    raise ValueError('The selected attributes produce an invalid character level.')
                struct.pack_into('<I', result, player+0x60, level)
                struct.pack_into('<I', result, character.profile+34, level)
                global_changed = True
            if (index, 'runes') in changes:
                gained = max(0, number(result, player+0x64)-number(self.raw, player+0x64))
                total = number(self.raw, player+0x68)+gained
                if total > 0xffffffff:
                    raise ValueError('Adding these runes would overflow the lifetime rune total.')
                struct.pack_into('<I', result, player+0x68, total)
                struct.pack_into('<I', result, character.profile+42, total)
                global_changed = True
            for relative, data in self._fingerprint_data(result, player):
                struct.pack_into('<I', result, character.fingerprints+relative, player_hash(data))
        blocks = set(range(12)) if repair_crc else {self.characters[i].physical for i in touched}
        if global_changed:
            blocks.add(10)
        for index in blocks:
            start, length = self.blocks[index]
            result[start:start+16] = hashlib.md5(result[start+16:start+length]).digest()
        return result

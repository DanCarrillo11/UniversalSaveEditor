"""Preserving editors for the ReCoM and BBS Final Mix PC archives.

Layouts and checksums adapted from Kingdom Save Editor (GPL-3.0-or-later),
Copyright (C) 2020 Luciano Ciccariello; maintained by BFlorry.
See SOURCES.md for the pinned source and modifications.
SPDX-License-Identifier: GPL-3.0-or-later
"""
import struct
import zlib
from kh_extra_tables import RECOM_CARDS, BBS_COMMANDS, BBS_ABILITIES, DDD_ITEMS


def recom_checksum(data):
    checksum = 0xffffffff
    for value in data:
        checksum ^= (value & 1) << 31
        checksum = ((checksum << 1) ^ (0x04c11db7 if checksum & 0x80000000 else 0)) & 0xffffffff
    return checksum ^ 0xffffffff


def bbs_checksum(data):
    return sum(value[0] for value in struct.iter_unpack('<I', data[16:])) & 0xffffffff


class ExtraKhArchive:
    STRIDES = {'recom': 0x3a30, 'bbs': 0x13c00, 'ddd': 0x16600}

    def __init__(self, raw, game, Field, Slot, png_chunks):
        self.raw, self.game, self.records, self.slots, self.warnings = raw, game, [], [], []
        regions = [(s, e) for name, s, e in png_chunks(raw, allow_sqex_crc=True) if name == b'sqEX']
        if len(regions) != 1:
            raise ValueError('A single sqEX save block is required.')
        start, end = regions[0]
        self.crc_regions = regions
        stride = self.STRIDES[game]
        archive = start + 16
        if archive != 0x70 or not 0 <= end - (archive + 100 * (0x158 + stride)) < 0x400:
            raise ValueError('Unrecognized Kingdom Hearts PC archive layout.')
        if zlib.crc32(raw[start-4:end]) != struct.unpack_from('>I', raw, end)[0]:
            self.warnings.append('The save block CRC does not match. Enable integrity repair before applying changes.')
        table = bytearray(raw[archive:archive+100*0x158])
        key = table[0xe0:0xf0]
        for index in range(0xf0):
            table[index] ^= key[index % 16]
        base = archive + 100 * 0x158
        for index in range(100):
            length = struct.unpack_from('<I', table, index*0x158+0x50)[0]
            if not length:
                continue
            if length > stride:
                raise ValueError('Save record exceeds its allocated space.')
            record = base + index * stride
            # System records are retained verbatim, never interpreted as player slots.
            magic = raw[record:record+4]
            if magic != {'recom':b'\x07\0\0\0', 'bbs':b'BBSD', 'ddd':b'SOMD'}[game]:
                continue
            fields = []
            def add(key, label, delta, fmt, maximum, group, minimum=0, **options):
                value = struct.unpack_from(fmt, raw, record+delta)[0]
                fields.append(Field(key, label, value, record+delta, fmt, minimum, maximum, group, **options))
            if game == 'recom':
                if length != 0x3630 or struct.unpack_from('<II', raw, record+8) != (0x3620, 0):
                    raise ValueError('Unsupported Re:Chain of Memories record size or version.')
                actual = recom_checksum(raw[record+16:record+length])
                expected = struct.unpack_from('<I', raw, record+4)[0]
                if expected != actual:
                    self.warnings.append(f'Slot {index+1}: internal checksum mismatch. Enable integrity repair.')
                add('moogle_points', 'Moogle Points', 0x2d58, '<i', 9999999, 'Currency')
                add('experience', 'Experience', 0x2d50, '<i', 99999999, 'Level and experience')
                difficulty = raw[record+0x481]
                if difficulty not in (0, 1, 2):
                    raise ValueError('Unsupported Re:Chain of Memories difficulty.')
                add('difficulty', 'Difficulty', 0x481, '<B', 2, 'Difficulty', choices=('Beginner', 'Standard', 'Proud'))
                for card_index, (name, group) in enumerate(RECOM_CARDS):
                    if name is not None:
                        add(f'card:{card_index}', name, 0x1fc4+card_index, '<B', 99, group)
            elif game == 'bbs':
                if length not in (0x11e50, 0x12000) or struct.unpack_from('<II', raw, record+4) != (0x1d, 0x11e50):
                    raise ValueError('Only Final Mix BBS player records are supported.')
                length = 0x11e50
                if struct.unpack_from('<I', raw, record+12)[0] != bbs_checksum(raw[record:record+length]):
                    self.warnings.append(f'Slot {index+1}: internal checksum mismatch. Enable integrity repair.')
                difficulties = (0x08, 0x48, 0x88, 0xc8)
                if raw[record+0x5cac] not in difficulties:
                    raise ValueError('Unsupported Birth by Sleep difficulty.')
                fields.append(Field('difficulty', 'Difficulty', difficulties.index(raw[record+0x5cac]), record+0x5cac, '', 0, 3, 'Difficulty', choices=('Beginner', 'Standard', 'Proud', 'Critical')))
                for key, label, delta, fmt, maximum, group, minimum in (
                    ('experience', 'Experience', 0, '<I', 99999999, 'Attributes', 0),
                    ('munny', 'Munny', 4, '<I', 9999999, 'Currency', 0),
                    ('medals', 'Arena medals', 8, '<I', 9999999, 'Currency', 0),
                    ('level', 'Level', 0xc, '<H', 99, 'Attributes', 1),
                    ('magic', 'Magic', 0x18, '<H', 999, 'Attributes', 0),
                    ('defense', 'Defense', 0x1a, '<H', 999, 'Attributes', 0),
                    ('arena_level', 'Arena level', 0x1c, '<H', 30, 'Attributes', 0),
                    ('strength', 'Strength', 0x1e, '<H', 999, 'Attributes', 0),
                ):
                    add(key, label, 0x59d0+delta, fmt, maximum, group, minimum)
                # Keep command identities, deck references and unknown flags intact.
                for command in range(512):
                    delta = 0x3498 + command * 10
                    identifier = struct.unpack_from('<H', raw, record+delta)[0]
                    if identifier in BBS_COMMANDS:
                        name = f'{BBS_COMMANDS[identifier]} · Entry {command+1}'
                        add(f'command:{command}:level', name+' · Level', delta+2, '<H', 5, 'Commands', 1,item_id=identifier)
                        add(f'command:{command}:experience', name+' · Experience', delta+4, '<H', 65535, 'Commands',item_id=identifier)
                for ability, name in enumerate(BBS_ABILITIES):
                    delta = 0x4d64 + ability * 4
                    add(f'ability:{ability}:active', name+' · Active stacks', delta, '<B', 5, 'Abilities')
                    add(f'ability:{ability}:slots', name+' · Acquired stacks', delta+1, '<B', 5, 'Abilities')
            else:
                if length != 0x16600 or raw[record+4] != 0x14:
                    raise ValueError('Only Dream Drop Distance HD PC player records are supported.')
                difficulty = raw[record+0x92]
                if difficulty not in range(4):
                    raise ValueError('Unsupported Dream Drop Distance difficulty.')
                add('difficulty', 'Difficulty', 0x92, '<B', 3, 'Difficulty', choices=('Beginner','Standard','Proud','Critical'))
                add('munny', 'Munny', 0xd2ec, '<I', 999999, 'Currency')
                for character, xp, droplets, level in (('Sora',0xd1f0,0xd204,0xd214),('Riku',0xd26c,0xd280,0xd290)):
                    add(f'character:{character}:experience', character+' · Experience', xp, '<I', 99999999, 'Attributes')
                    add(f'character:{character}:droplets', character+' · Drop Points', droplets, '<H', 65535, 'Attributes')
                    add(f'character:{character}:level', character+' · Level', level, '<B', 99, 'Attributes', 1)
                for item in range(511):
                    delta = 0xc004 + item*8
                    identifier = struct.unpack_from('<H', raw, record+delta)[0]
                    if identifier in DDD_ITEMS and identifier:
                        label, group = DDD_ITEMS[identifier]
                        add(f'inventory:{item}', label+f' · Entry {item+1}', delta+5, '<B', 99, group,item_id=identifier)
            name = bytes(table[index*0x158:index*0x158+0x40]).split(b'\0')[0].decode('ascii', errors='replace')
            if game == 'bbs':
                character = {1:'Ventus', 2:'Aqua', 3:'Terra', 5:'Ventus', 6:'Aqua', 7:'Terra'}.get(raw[record+0x17])
                if character is None:
                    raise ValueError('Unsupported BBS playable character record.')
                name = character+' · '+name
            self.records.append((record, length))
            self.slots.append(Slot(name or f'Slot {index+1}', fields))
        if not self.slots:
            raise ValueError('No compatible player slots were found in this archive.')

    def finish(self, result, changes, repair):
        for index, (record, length) in enumerate(self.records):
            if not repair and not any(slot == index for slot, key in changes):
                continue
            if self.game == 'recom':
                result[record+0x14:record+0x18] = result[record+0x2d58:record+0x2d5c]
                struct.pack_into('<I', result, record+4, recom_checksum(result[record+16:record+length]))
            elif self.game == 'bbs':
                if (index, 'difficulty') in changes:
                    result[record+0x5cac] = (0x08, 0x48, 0x88, 0xc8)[changes[index, 'difficulty']]
                fields = {f.key:f for f in self.slots[index].fields}
                for ability in range(30):
                    active = fields[f'ability:{ability}:active']
                    slots = fields[f'ability:{ability}:slots']
                    if any((index, f.key) in changes for f in (active, slots)) and result[active.offset] > result[slots.offset]:
                        raise ValueError('Active ability stacks cannot exceed acquired stacks.')
                struct.pack_into('<I', result, record+12, bbs_checksum(result[record:record+length]))
            elif self.game == 'ddd':
                if (index, 'difficulty') in changes:
                    result[record+0x20] = result[record+0x92]
                if (index, 'character:Sora:experience') in changes:
                    result[record+0x28:record+0x2c] = result[record+0xd1f0:record+0xd1f4]
        return result

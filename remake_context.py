"""RE4 Remake currency, player backups and increasing saved case sizes.

SPDX-License-Identifier: GPL-3.0-or-later. Serialized identities are factual
metadata from the pinned REE Save Editor and RE4R-SaveForge references in
SOURCES.md. No byte-pattern search, scene replacement or account transfer.
"""
from collections import defaultdict
import struct
from re_hashes import murmur32

INVENTORY_MANAGER = 0x52dfdaa8
INVENTORY = 0xbedd9bf5
CASE = 0x740f8831
CHARACTERS = 0xe381234f
GAME_SECTIONS = 0x752fb6e4
PLAYERS = {0x4f581657: 'Player', 0x6da9ecfa: 'Player',
           0x789ff5e9: 'Partner', 0x8504d4b1: 'Partner'}


def h(name):
    return murmur32(name.encode())


def gameplay_section(path):
    """Standalone decoded sections or the documented native section list."""
    if not path or path[0][0] != 0: return False
    if len(path) == 1: return True
    return len(path) == 3 and all(p[:2] == (GAME_SECTIONS, h('GameSaveDataList')) for p in path[1:])


class RemakeContext:
    def __init__(self, nodes, data, Field):
        self.data = data
        self.fields = []
        self.operations = {}
        self.health = {}
        records = defaultdict(list)
        for node in nodes:
            records[node.owner, node.path[:-1]].append(node)

        def one(values, owner, name, fmt='<i', kind=7):
            matches = [n for n in values if (n.owner, n.field) == (owner, h(name))]
            kinds = kind if isinstance(kind, tuple) else (kind,)
            return matches[0] if len(matches) == 1 and matches[0].kind in kinds and (matches[0].fmt, matches[0].size) == (fmt, struct.calcsize(fmt)) else None

        def value(node):
            return struct.unpack_from(node.fmt, data, node.offset)[0]

        def add(node, label, minimum, maximum, group, collection='', note='', choices=()):
            key = f'{node.owner:08x}:{node.field:08x}:{node.offset}'
            self.fields.append(Field(key, label, value(node), node.offset, node.fmt,
                                     minimum, maximum, group, collection=collection,
                                     note=note, choices=choices))
            self.operations[key] = (node.offset, node.fmt)
            return key

        counts = defaultdict(int)
        for (owner, path), values in records.items():
            # Currency belongs to the top-level gameplay inventory section,
            # never a merchant object, nested template or arbitrary PTAS bytes.
            if owner == INVENTORY_MANAGER and gameplay_section(path):
                money = one(values, owner, 'PTAS')
                if money and 0 <= value(money) <= 9999999:
                    add(money, 'Pesetas', 0, 9999999, 'Currency',
                        note='Saved gameplay balance. Shop stock, purchases, treasures and challenge counters are preserved.')

            if owner in PLAYERS and path and path[-1][:2] == (CHARACTERS, h('_CharacterSaves')):
                # The base CharacterBackup also represents enemies. Accept only
                # the four documented player/partner subclasses in this array.
                if len(path)<3 or path[-2][:2] != (CHARACTERS, h('_CharacterSaves')) or not gameplay_section(path[:-2]):
                    continue
                current, maximum = one(values, owner, '_HP'), one(values, owner, '_MaxHP')
                if not current or not maximum:
                    continue
                hp, cap = value(current), value(maximum)
                if not 0 <= hp <= cap <= 100000 or not cap:
                    continue
                kind = PLAYERS[owner]; counts[kind] += 1
                collection = f'{kind} record {counts[kind]}'
                # Increasing the maximum is allowed; lowering it clamps current
                # health. Injury/elimination and yellow-herb history are separate.
                ck = add(current, 'Current health', 0, 100000, 'Player health', collection,
                         'Saved player health. Must fit the final maximum; injury, elimination and story flags are preserved.')
                mk = add(maximum, 'Maximum health', 1, 100000, 'Player health', collection,
                         'Changes the stored maximum, not yellow-herb acquisition or reward history. A reduction clamps current health unless you explicitly choose a conflicting value.')
                self.health[mk] = (current, maximum, ck)

            if owner == CASE and path and path[-1][:2] == (INVENTORY, h('InventorySize')):
                # Require a current inventory in the native gameplay section.
                # Take-over inventories are deliberately excluded.
                if len(path)<4 or not gameplay_section(path[:-3]) or any(p[:2] != (INVENTORY_MANAGER, h('InventorySaveDatas')) for p in path[-3:-1]):
                    continue
                inv = records.get((INVENTORY, path[:-1]), [])
                takeover = one(inv, INVENTORY, 'IsTakeOverData', '<B', 2)
                size = one(values, CASE, 'CurrInventorySize', kind=(1, 7))
                if not takeover or value(takeover) or not size or not 0 <= value(size) <= 4:
                    continue
                counts['Case'] += 1
                add(size, 'Case size', value(size), 4, 'Equipment capacity',
                    f'Inventory {counts["Case"]}',
                    'Increase this existing case only. Item positions, rotations and equipment references stay unchanged. Does not change merchant purchases or create a case inventory.',
                    ('S', 'M', 'L', 'XL', 'XXL'))

    def patch(self, result, changes):
        for key, value in changes.items():
            if key in self.operations:
                offset, fmt = self.operations[key]
                struct.pack_into(fmt, result, offset, value)
        for key, (current, maximum, current_key) in self.health.items():
            hp = changes.get(current_key, struct.unpack_from('<i', self.data, current.offset)[0])
            cap = changes.get(key, struct.unpack_from('<i', self.data, maximum.offset)[0])
            if hp > cap and current_key in changes:
                raise ValueError('Current HP cannot exceed maximum HP. Adjust both values together.')
            if key in changes or current_key in changes:
                struct.pack_into('<i', result, current.offset, min(hp, cap))

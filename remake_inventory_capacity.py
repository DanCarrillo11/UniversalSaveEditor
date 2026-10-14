"""Increasing saved RE2/RE3 main-survivor inventory capacity.

SPDX-License-Identifier: GPL-3.0-or-later. Exact native contexts from the pinned
REE Save Editor metadata; no item/reward synthesis or array resizing.
"""
from collections import defaultdict
import struct
from re_hashes import murmur32

CONFIG = {'re2': (0x7f9decbe, 0x41f30892, 0xf96bfecf),
          're3': (0x0304fb3b, 0x5f30b0dd, 0x55e8fab7)}


def h(name): return murmur32(name.encode())


class RemakeInventoryCapacity:
    def __init__(self, nodes, data, game, Field):
        self.fields = []; self.operations = {}
        wrapper, manager, inventory = CONFIG[game]
        records = defaultdict(list)
        for node in nodes: records[node.owner, node.path[:-1]].append(node)
        def one(values, name, kinds):
            found = [n for n in values if n.field == h(name)]
            return found[0] if len(found) == 1 and found[0].kind in kinds and found[0].fmt == '<i' and found[0].size == 4 else None
        number = 0
        for (owner, path), values in records.items():
            if owner != inventory or len(path) < 3: continue
            if any(p[:2] != (manager, h('DataLists')) for p in path[-2:]): continue
            section = path[:-2]
            if not section or section[0][0] != 0: continue
            if len(section) != 1 and not (len(section) == 3 and all(p[:2] == (wrapper, h('GameSaveDataList')) for p in section[1:])): continue
            survivor = one(values, '_SurvivorType', (1, 7))
            size = one(values, '_CurrentSlotSize', (7,))
            if not survivor or not size: continue
            who = struct.unpack_from('<i', data, survivor.offset)[0]
            count = struct.unpack_from('<i', data, size.offset)[0]
            # The primary two survivors only; child/bonus-mode layouts and
            # unknown capacities remain protected instead of being generalized.
            if who not in (0, 1) or count not in range(8, 21, 2): continue
            number += 1
            key=f'{owner:08x}:{size.field:08x}:{size.offset}'
            choices=tuple(range(8,21,2));self.operations[key]=(size.offset,choices)
            self.fields.append(Field(key,
                'Inventory capacity', choices.index(count), size.offset, '', choices.index(count), len(choices)-1,
                'Equipment capacity', collection=f'Inventory record {number}',
                choices=tuple(f'{i} slots' for i in choices),
                note='Increase this existing main-survivor inventory only. Item slots, equipment and shortcut references stay unchanged. Does not grant hip-pouch pickup events, items or achievements.'))

    def patch(self, result, changes):
        for key, value in changes.items():
            if key in self.operations:
                offset,choices=self.operations[key]
                struct.pack_into('<i',result,offset,choices[value])

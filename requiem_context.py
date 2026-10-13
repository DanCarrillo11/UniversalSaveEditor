"""Requiem player and inventory records, selected by their saved ancestry.

SPDX-License-Identifier: GPL-3.0-or-later
Factual serialized identifiers: kvasszn/ree-save-editor. See docs/RE9_FORMAT.md.
No third-party schema, implementation or translation database is bundled.
"""
from collections import defaultdict
from functools import lru_cache
import struct
from re_hashes import murmur32
from requiem_items import ITEM_CODES, ITEM_NAMES, ATTACHMENT_CODES

CHARACTERS = 0xb3b29efb
CHARACTER = 0x9d98c4ce
PLAYER = 0x64582fd4
HEALTH = 0xe603ebf1
MANAGER = 0x3a83076c
INVENTORY = 0x6dc40103
PANEL = 0xb00026aa
CONTAINED = 0x6b8482e9
ATTACHMENT = 0x1dbdde3d
CAPACITY_PARTS = frozenset(f'it30_00_{i}' for i in (100,101,102,103,104,105,106,108))

@lru_cache(maxsize=64)
def h(name):
    return murmur32(name.encode())


class RequiemContext:
    def __init__(self, nodes, data):
        self.data = data
        self.nodes = nodes
        self.records = defaultdict(list)
        self.characters = defaultdict(list)
        for node in nodes:
            self.records[node.owner, node.path[:-1]].append(node)
            for index, (owner, field, _) in enumerate(node.path):
                if owner == CHARACTER:
                    self.characters[node.path[:index]].append(node)
                    break
        self.health_levels = {}
        self.panels = defaultdict(dict)
        for (owner, path), nodes in self.records.items():
            if owner != PANEL or path[-1][:2] != (INVENTORY, h('_PanelItems')):
                continue
            inv_index = next((i for i, (o, _, _) in enumerate(path) if o == INVENTORY), None)
            if inv_index is None:
                continue
            entries = self.panels[path[:inv_index]]
            index = path[-1][2]
            entries[index] = nodes if index not in entries else []

    def one(self, nodes, owner, name, fmt):
        kind = {'<i':7, '<I':8, '<B':2, 'utf16':15}[fmt]
        matches = [n for n in nodes if (n.owner, n.field) == (owner, h(name))]
        return matches[0] if len(matches) == 1 and (matches[0].fmt, matches[0].kind) == (fmt, kind) else None

    def value(self, node):
        if node.fmt == 'utf16':
            if node.size > 128:
                return None
            try:
                return self.data[node.offset:node.offset + node.size].decode('utf-16-le').rstrip('\0')
            except UnicodeDecodeError:
                return None
        return struct.unpack_from(node.fmt, self.data, node.offset)[0]

    @staticmethod
    def key(node):
        return f'{node.owner:08x}:{node.field:08x}:{node.offset}'

    def fields(self, field_type):
        fields = []
        player_index = 0
        for path, nodes in self.characters.items():
            # The shared health class also appears hundreds of times on enemies.
            # Require a PlayerCommonData structure in this exact character record.
            if not any(n.owner == PLAYER for n in nodes):
                continue
            if not any((o, f) == (CHARACTERS, h('_CharacterSaves')) for o, f, _ in path):
                continue
            current = self.one(nodes, HEALTH, '_CurrentHP', '<i')
            maximum = self.one(nodes, HEALTH, '_CurrentMaxHP', '<i')
            setup = self.one(nodes, HEALTH, '_IsSetuped', '<B')
            if not all((current, maximum, setup)) or self.value(setup) != 1:
                continue
            hp, cap = self.value(current), self.value(maximum)
            if not 0 <= hp <= cap <= 100000 or cap == 0:
                continue
            player_index += 1
            collection = f'Player record {player_index}'
            note = ('Saved player record, identified by its player-specific structure. '
                    'Character names and which variant is active are not mapped. '
                    'Health changes do not reset death, injury or story flags.')
            fields.append(field_type(self.key(current), 'Current health', hp, current.offset,
                                     '<i', 0, cap, 'Player health', note=note, collection=collection))
            fields.append(field_type(self.key(maximum), 'Maximum health', cap, maximum.offset,
                                     '<i', 1, 100000, 'Player health', readonly=True,
                                     note='Derived from the saved health upgrade table; preserved unless the health upgrade level changes.',
                                     collection=collection))
            level = self.one(nodes, HEALTH, '_CurrentHPLevel', '<i')
            table = [n for n in nodes if (n.owner, n.field, n.fmt) == (HEALTH, h('_MaximumHPTable'), '<i')]
            if not level or not 1 < len(table) <= 32:
                continue
            # Match the same health object and require a complete ordered array.
            if any(n.path[:-2] != level.path[:-1] for n in table):
                continue
            if [n.path[-1][2] for n in table] != list(range(len(table))):
                continue
            caps = tuple(self.value(n) for n in table)
            value = self.value(level)
            if not all(0 < v <= 100000 for v in caps) or tuple(sorted(set(caps))) != caps:
                continue
            if not 0 <= value < len(caps) or caps[value] != cap:
                continue
            key = self.key(level)
            self.health_levels[key] = (level, current, maximum, caps)
            fields.append(field_type(key, 'Health upgrade level', value, level.offset, '<i',
                                     0, len(caps) - 1, 'Player health',
                                     choices=tuple(f'Level {i} · {v} HP' for i, v in enumerate(caps)),
                                     note='Uses this record’s own health table. Updates maximum health and clamps current health when reducing the level.',
                                     collection=collection))

        item_index = 0
        for (owner, path), nodes in self.records.items():
            if owner not in (PANEL, CONTAINED):
                continue
            inv_index = next((i for i, (o, _, _) in enumerate(path) if o == INVENTORY), None)
            if inv_index is None or not any((o, f) == (MANAGER, h('_InventoryData')) for o, f, _ in path[:inv_index]):
                continue
            if any((o,f)==(MANAGER,h('_BackupInventoryData')) for o,f,_ in path):
                continue
            inventory_nodes = self.records.get((INVENTORY, path[:inv_index]), [])
            user = self.one(inventory_nodes, INVENTORY, '_UserName', 'utf16')
            board = self.one(inventory_nodes, INVENTORY, '_BoardTypeName', 'utf16')
            if not user or not board:
                continue
            username, boardname = self.value(user), self.value(board)
            if username not in ('None', 'User00', 'User01', 'User02', 'User03'):
                continue
            if boardname not in ('Hand', 'ItemBox', 'ShareItemBox'):
                continue
            # Loaded rounds/chamber state and archive/key-item records are excluded.
            allowed = ('_PanelItems', '_PreferentialPanelItems', '_InternalPanelItems')
            if not any(o == INVENTORY and f in tuple(h(n) for n in allowed) for o, f, _ in path):
                continue
            if owner == CONTAINED and path[-1][:2] != (PANEL, h('_StorageItems')):
                continue
            if owner == CONTAINED:
                parent_index = next(i for i, (o, _, _) in enumerate(path) if o == PANEL)
                parent = self.records.get((PANEL, path[:parent_index]), [])
                parent_id = self.one(parent, PANEL, '_ItemIDHash', '<I')
                parent_count = self.one(parent, PANEL, '_Stock', '<i')
                if not parent_id or not parent_count or self.value(parent_id) in (0,0xffffffff,1857826560) or self.value(parent_count) < 1:
                    continue
            count = self.one(nodes, owner, '_Stock', '<i')
            identifier = self.one(nodes, owner, '_ItemIDHash', '<I')
            if not count or not identifier:
                continue
            value, item_id = self.value(count), self.value(identifier)
            if not 1 <= value <= 999 or item_id in (0, 0xffffffff, 1857826560):
                continue
            boardlabel = {'Hand': 'Carried inventory', 'ItemBox': 'Item box', 'ShareItemBox': 'Shared item box'}[boardname]
            section = f'{boardlabel} · {username}'
            code = ITEM_CODES.get(item_id)
            # The game's durability pseudo-item is not a pile of consumables.
            if code == 'it40_20_001':
                continue
            known_ammo = bool(code and code.startswith('it40_'))
            single = value == 1 and not known_ammo
            item_index += 1
            label = ITEM_NAMES.get(code, f'Item {item_id:08X}')
            fields.append(field_type(self.key(count), f'{label} · Quantity · Entry {item_index}', value,
                                     count.offset, '<i', 1, 999, 'Inventory quantities',
                                     readonly=single, collection=section,
                                     item_id=item_id,
                                     note=('Single-item records are read-only until stackability is verified.' if single else
                                           f'Existing stack only. Item ID {item_id:08X}. Game stack limits are not mapped. Loaded rounds, equipment, upgrades and case geometry are preserved.')))
        fields.extend(self.attachment_fields(field_type))
        return fields

    def attachment_fields(self, field_type):
        fields = []
        for (owner, path), nodes in self.records.items():
            if owner != ATTACHMENT or path[-1][:2] != (INVENTORY, h('_PanelAttachments')):
                continue
            inv_index = next((i for i, (o, _, _) in enumerate(path) if o == INVENTORY), None)
            if inv_index is None or not any((o,f)==(MANAGER,h('_InventoryData')) for o,f,_ in path[:inv_index]):
                continue
            if any((o,f)==(MANAGER,h('_BackupInventoryData')) for o,f,_ in path):
                continue
            inv_path = path[:inv_index]
            name = self.one(nodes, ATTACHMENT, '_ItemIDName', 'utf16')
            level = self.one(nodes, ATTACHMENT, '_Level', '<i')
            item_index = self.one(nodes, ATTACHMENT, '_ItemIndex', '<i')
            target_index = self.one(nodes, ATTACHMENT, '_AttachTargetItemIndex', '<i')
            if not all((name, level, item_index, target_index)):
                continue
            code, value = self.value(name), self.value(level)
            if code not in ATTACHMENT_CODES or not 0 <= value <= 2:
                continue
            panels = self.panels.get(inv_path, {})
            part = self.one(panels.get(self.value(item_index), []), PANEL, '_ItemIDHash', '<I')
            weapon = self.one(panels.get(self.value(target_index), []), PANEL, '_ItemIDHash', '<I')
            if not part or not weapon or self.value(part) != murmur32(code.encode('utf-16-le')):
                continue
            part_count = self.one(panels.get(self.value(item_index), []), PANEL, '_Stock', '<i')
            weapon_count = self.one(panels.get(self.value(target_index), []), PANEL, '_Stock', '<i')
            if not part_count or not weapon_count or self.value(part_count) != 1 or self.value(weapon_count) != 1:
                continue
            weapon_code = ITEM_CODES.get(self.value(weapon), '')
            if not weapon_code.startswith('it10_'):
                continue
            capacity = code in CAPACITY_PARTS
            fields.append(field_type(self.key(level), ITEM_NAMES[code], value, level.offset,
                                     '<i', value if capacity else 0, 2, 'Weapon upgrades',
                                     choices=('Base', 'Improved (+)', 'Maximum (★)'),
                                     collection=f'{ITEM_NAMES[weapon_code]} · Item {self.value(target_index) + 1}',
                                     item_id=self.value(part),
                                     readonly=capacity and value == 2,
                                     note=('Existing attached part only; references, socket, item identity and loaded ammunition are preserved. '
                                           + ('Capacity tiers can only increase to avoid shrinking an occupied magazine.' if capacity else
                                              'Only the three mapped saved tiers are offered. This does not add or attach parts.'))))
        return fields

    def apply_health_levels(self, result, changes):
        for key, (level, current, maximum, caps) in self.health_levels.items():
            if key not in changes:
                continue
            cap = caps[changes[key]]
            hp = changes.get(self.key(current), self.value(current))
            if self.key(current) in changes and hp > cap:
                raise ValueError('Current health exceeds the selected health upgrade level.')
            struct.pack_into('<i', result, maximum.offset, cap)
            struct.pack_into('<i', result, current.offset, min(hp, cap))

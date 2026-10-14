"""Owned Requiem weapon references, without resizing serialized strings/arrays.

SPDX-License-Identifier: GPL-3.0-or-later. Factual class/property identities:
kvasszn/ree-save-editor, pinned in SOURCES.md. No SDK assets bundled.
"""
from collections import Counter, defaultdict
import struct
from requiem_items import ITEM_CODES, ITEM_NAMES
from requiem_context import INVENTORY, PANEL, MANAGER, h

EQUIP = 0xdf233e4a
SHORTCUT = 0x1be9729e
FIREARMS = frozenset(code for code in ITEM_NAMES
                     if code[:8] in ('it10_00_', 'it10_01_', 'it10_02_',
                                     'it10_03_', 'it10_04_', 'it10_05_'))
MELEE = frozenset(code for code in ITEM_NAMES if code.startswith('it10_20_'))
SHORTCUTS = frozenset('Equip_' + direction + suffix
                     for direction in ('Up', 'Down', 'Left', 'Right')
                     for suffix in ('', '2'))


class RequiemEquipment:
    def __init__(self, context, Field):
        self.context = context
        self.fields = []
        self.operations = {}
        slot_names = defaultdict(Counter)
        for (owner, path), nodes in context.records.items():
            if owner not in (EQUIP, SHORTCUT) or not path: continue
            slot = context.one(nodes, owner, '_SlotName', 'utf16')
            if slot: slot_names[owner, path[:-1]][context.value(slot)] += 1
        for (owner, path), nodes in context.records.items():
            if owner not in (EQUIP, SHORTCUT) or not path:
                continue
            array = '_Equips' if owner == EQUIP else '_Shortcuts'
            if path[-1][:2] != (INVENTORY, h(array)):
                continue
            inv_index = next((i for i, (o, _, _) in enumerate(path) if o == INVENTORY), None)
            if inv_index is None or not any((o, f) == (MANAGER, h('_InventoryData'))
                                          for o, f, _ in path[:inv_index]):
                continue
            if any((o, f) == (MANAGER, h('_BackupInventoryData')) for o, f, _ in path):
                continue
            inv_path = path[:inv_index]
            inventory = context.records.get((INVENTORY, inv_path), [])
            user = context.one(inventory, INVENTORY, '_UserName', 'utf16')
            board = context.one(inventory, INVENTORY, '_BoardTypeName', 'utf16')
            if not user or not board or context.value(board) != 'Hand':
                continue
            username = context.value(user)
            if username not in ('User00', 'User01', 'User02', 'User03'):
                continue
            slot = context.one(nodes, owner, '_SlotName', 'utf16')
            index = context.one(nodes, owner, '_ItemIndex', '<i')
            name = context.one(nodes, owner, '_ItemIDName', 'utf16')
            if not all((slot, index, name)):
                continue
            slotname, current, code = context.value(slot), context.value(index), context.value(name)
            allowed_slots = ('Primary', 'Secondary') if owner == EQUIP else SHORTCUTS
            if slotname not in allowed_slots or current < 0 or code not in ITEM_NAMES:
                continue
            # Duplicate slot names cannot be assigned an unambiguous meaning.
            if slot_names[owner, path[:-1]][slotname] != 1:
                continue
            family = MELEE if owner == EQUIP and slotname == 'Secondary' else FIREARMS
            if code not in family or name.size != len(code.encode('utf-16-le')):
                continue
            choices = []
            for item_index, panel in sorted(context.panels.get(inv_path, {}).items()):
                identity = context.one(panel, PANEL, '_ItemIDHash', '<I')
                stock = context.one(panel, PANEL, '_Stock', '<i')
                if not identity or not stock or context.value(stock) != 1:
                    continue
                item_code = ITEM_CODES.get(context.value(identity))
                if item_code in family and len(item_code.encode('utf-16-le')) == name.size:
                    choices.append((item_index, item_code))
            if (current, code) not in choices:
                continue
            key = context.key(index)
            self.operations[key] = (index, name, tuple(choices))
            group = 'Equipment' if owner == EQUIP else 'Weapon shortcuts'
            label = slotname if owner == EQUIP else slotname.removeprefix('Equip_')
            self.fields.append(Field(key, label, choices.index((current, code)), index.offset,
                                     '', 0, len(choices) - 1, group,
                                     choices=tuple(f'{ITEM_NAMES[c]} · Item {i + 1}' for i, c in choices),
                                     collection=f'Carried inventory · {username}',
                                     note='Selects an owned weapon in this carried inventory. Updates its item reference and name together; ammunition, upgrades and geometry are preserved. Empty or unresolved slots are preserved.'))

    def patch(self, result, changes):
        for key, value in changes.items():
            if key not in self.operations:
                continue
            index, name, choices = self.operations[key]
            target, code = choices[value]
            struct.pack_into('<i', result, index.offset, target)
            result[name.offset:name.offset + name.size] = code.encode('utf-16-le')

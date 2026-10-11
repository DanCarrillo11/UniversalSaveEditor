"""Max Payne 1 PC tagged save reader and preserving inventory editor.

The game uses tagged values and size-delimited chunks, not fixed offsets.
Weapon IDs are checked against the original game's inventory definitions.
See docs/MAX_PAYNE_FORMAT.md for evidence and outstanding checks.
"""
from dataclasses import dataclass
import math
import struct


class MaxPayneFormatError(ValueError):
    pass


@dataclass(frozen=True)
class Value:
    offset: int
    end: int
    tag: int
    value: object = None
    identifier: int | None = None
    revision: int | None = None
    children: tuple = ()


INTEGER_WIDTHS = {
    0x00: 4, 0x01: 4, 0x02: 4, 0x03: 4, 0x04: 2, 0x05: 2,
    0x06: 1, 0x07: 1, 0x08: 1, 0x0f: 3, 0x10: 2, 0x11: 1,
    0x12: 3, 0x13: 2, 0x14: 1,
}
SIGNED = {0x00, 0x02, 0x04, 0x07, 0x12, 0x13, 0x14}
FIXED_WIDTHS = {
    **INTEGER_WIDTHS, 0x09: 4, 0x0a: 8, 0x0e: 1,
    0x15: 8, 0x16: 12, 0x17: 16, 0x18: 16,
    0x19: 36, 0x1a: 48, 0x1b: 64, 0x1c: 0,
}


class Reader:
    def __init__(self, raw):
        if not raw or len(raw) > 64 * 1024 * 1024:
            raise MaxPayneFormatError('Empty or oversized Max Payne save.')
        self.raw = bytes(raw)
        self.remaining = 500000

    def require(self, offset, size, limit):
        if offset < 0 or size < 0 or offset + size > limit or limit > len(self.raw):
            raise MaxPayneFormatError('Truncated Max Payne value or chunk.')

    def chunk_header(self, offset, limit):
        self.require(offset, 13, limit)
        if self.raw[offset] != 0x0c:
            raise MaxPayneFormatError('Expected a Max Payne chunk.')
        identifier, revision, size = struct.unpack_from('<III', self.raw, offset + 1)
        if size < 13:
            raise MaxPayneFormatError('Invalid Max Payne chunk size.')
        self.require(offset, size, limit)
        return identifier, revision, offset + size

    def read(self, offset, limit, depth=0):
        self.require(offset, 1, limit)
        self.remaining -= 1
        if depth > 64 or self.remaining < 0:
            raise MaxPayneFormatError('Max Payne save nesting or value limit exceeded.')
        tag = self.raw[offset]
        start = offset + 1
        if tag == 0x0c:
            identifier, revision, end = self.chunk_header(offset, limit)
            children = self.sequence(offset + 13, end, depth + 1)
            return Value(offset, end, tag, identifier=identifier,
                         revision=revision, children=children)
        if tag == 0x0d:
            length = self.read(start, limit, depth + 1)
            if length.tag not in INTEGER_WIDTHS or not 0 <= length.value <= 65536:
                raise MaxPayneFormatError('Invalid Max Payne string length.')
            self.require(length.end, length.value, limit)
            end = length.end + length.value
            text = self.raw[length.end:end].decode('latin-1')
            return Value(offset, end, tag, text)
        width = FIXED_WIDTHS.get(tag)
        if width is None:
            raise MaxPayneFormatError(f'Unsupported Max Payne value tag: 0x{tag:02x}.')
        self.require(start, width, limit)
        end = start + width
        if tag in INTEGER_WIDTHS:
            value = int.from_bytes(self.raw[start:end], 'little', signed=tag in SIGNED)
        elif tag == 0x0e:
            value = self.raw[start]
            if value not in (0, 1):
                raise MaxPayneFormatError('Invalid Max Payne boolean.')
        elif tag in (0x09, 0x0a):
            value = struct.unpack_from('<f' if tag == 0x09 else '<d', self.raw, start)[0]
            if not math.isfinite(value):
                raise MaxPayneFormatError('Non-finite Max Payne scalar.')
        else:
            value = self.raw[start:end]
        return Value(offset, end, tag, value)

    def sequence(self, offset, end, depth=0):
        values = []
        while offset < end:
            value = self.read(offset, end, depth)
            values.append(value)
            offset = value.end
        return tuple(values)


class MaxPayneArchive:
    """Validate revision 48 saves and locate the named player structurally."""
    def __init__(self, raw):
        self.raw = bytes(raw)
        reader = Reader(self.raw)
        identifier, revision, header_end = reader.chunk_header(0, len(self.raw))
        if (identifier, revision) != (1, 1):
            raise MaxPayneFormatError('Unsupported Max Payne save header.')
        version = reader.read(13, header_end)
        if version.tag not in INTEGER_WIDTHS or version.value != 48:
            raise MaxPayneFormatError('Unsupported Max Payne save revision.')
        caption = reader.read(version.end, header_end)
        if caption.tag != 0x0d:
            raise MaxPayneFormatError('Missing Max Payne save description.')
        preview_size = reader.read(caption.end, header_end)
        if (preview_size.tag not in INTEGER_WIDTHS or preview_size.value < 0 or
                preview_size.end + preview_size.value != header_end):
            raise MaxPayneFormatError('Invalid Max Payne preview bounds.')
        self.description = caption.value
        self.preview = self.raw[preview_size.end:header_end]
        self.roots = reader.sequence(header_end, len(self.raw))
        if [(v.tag, v.identifier, v.revision) for v in self.roots] != [
                (0x0c, 16, 13), (0x0c, 0, 1), (0x0c, 0, 4)]:
            raise MaxPayneFormatError('Unsupported Max Payne top-level layout.')
        world = self.roots[0]
        if not world.children or world.children[0].tag != 0x0d:
            raise MaxPayneFormatError('Missing Max Payne level identifier.')
        self.level = world.children[0].value
        entities = [v for v in world.children if v.identifier == 17 and v.revision == 1]
        if len(entities) != 1:
            raise MaxPayneFormatError('Expected one Max Payne entity section.')
        matches = []
        for index, node in enumerate(entities[0].children):
            if (node.identifier == 18 and node.revision == 1 and
                    len(node.children) == 1 and node.children[0].tag == 0x0d and
                    node.children[0].value == 'player'):
                following = entities[0].children[index + 1:index + 2]
                if not following or (following[0].identifier, following[0].revision) != (0, 13):
                    raise MaxPayneFormatError('Invalid Max Payne player record.')
                matches.append(following[0])
        if len(matches) != 1:
            raise MaxPayneFormatError('Expected exactly one named Max Payne player.')
        self.player = matches[0]


WEAPON_NAMES = ('Empty', 'Lead pipe', 'Baseball bat', 'Beretta', 'Dual Berettas',
                'Desert Eagle', 'Sawed-off shotgun', 'Pump-action shotgun', 'Ingram',
                'Dual Ingrams', 'MP5', 'Jackhammer', 'Molotov cocktails', 'Grenades',
                'M79', 'Sniper rifle', 'Painkillers')
INVENTORY_WEAPONS = ((0,), (1,), (2,), (3,4), (5,), (6,7), (8,9), (15,),
                     (10,), (11,), (13,), (12,), (14,), (16,))
AMMO_CAPACITIES = {3:162, 4:48, 5:80, 6:300, 7:20, 8:150, 9:168,
                   10:10, 11:10, 12:10, 13:8}


class MaxPayneEditor(MaxPayneArchive):
    def __init__(self, raw, Field):
        super().__init__(raw)
        candidates = []
        def visit(node):
            if node.tag != 0x0c:
                return
            values = node.children
            if ((node.identifier, node.revision) == (0,1) and len(values) == 18 and
                    values[0].tag in INTEGER_WIDTHS and
                    values[1].tag in INTEGER_WIDTHS and values[1].value == 14):
                candidates.append(node)
            for child in values:
                visit(child)
        visit(self.player)
        if len(candidates) != 1:
            raise MaxPayneFormatError('Unsupported Max Payne player inventory layout.')
        self.inventory = candidates[0]
        self.fields, self.nodes = [], {}
        for index, (entry, identifiers) in enumerate(zip(self.inventory.children[2:], INVENTORY_WEAPONS)):
            v = entry.children
            if ((entry.identifier, entry.revision) != (0,1) or len(v) != 4+len(identifiers)*2 or
                    any(v[i].tag not in SIGNED for i in (0,1,3)) or
                    v[2].tag != 0x0e or v[3].value != len(identifiers)):
                raise MaxPayneFormatError('Unsupported Max Payne inventory entry.')
            for variant, identifier in enumerate(identifiers):
                id_node, owned = v[4+variant*2:6+variant*2]
                if id_node.tag not in SIGNED or id_node.value != identifier or owned.tag != 0x0e:
                    raise MaxPayneFormatError('Weapon IDs do not match the original Max Payne inventory.')
                if identifier not in (0,16):
                    key = f'weapon:{identifier}'
                    self.nodes[key] = owned
                    self.fields.append(Field(key, WEAPON_NAMES[identifier], owned.value, -1, '', 0, 1, 'Weapons', boolean=True))
            if index >= 3:
                key = f'ammo:{index}'
                self.nodes[key] = v[0]
                label = 'Painkillers' if index == 13 else WEAPON_NAMES[identifiers[0]]+' · Reserve ammunition'
                self.fields.append(Field(key, label, v[0].value, -1, '', 0, AMMO_CAPACITIES[index],
                                         'Health supplies' if index == 13 else 'Ammunition'))
        # Do not alter equipped-weapon pointers, loaded rounds, world entities,
        # screenshots or unknown player attributes.

    def patch(self, changes):
        replacements = {}
        for key, value in changes.items():
            node = self.nodes[key]
            if node.tag == 0x0e:
                replacements[node.offset] = bytes((0x0e, value))
            else:
                width = INTEGER_WIDTHS[node.tag]
                if value < (1 << (width*8-1)):
                    replacements[node.offset] = bytes((node.tag,)) + value.to_bytes(width, 'little', signed=True)
                else:
                    replacements[node.offset] = b'\x02' + struct.pack('<i', value)
        def render(node):
            if node.offset in replacements:
                return replacements[node.offset]
            if node.tag != 0x0c or not any(node.offset <= offset < node.end for offset in replacements):
                return self.raw[node.offset:node.end]
            payload = b''.join(render(child) for child in node.children)
            return b'\x0c' + struct.pack('<III', node.identifier, node.revision, 13+len(payload)) + payload
        header_end = self.roots[0].offset
        return bytearray(self.raw[:header_end] + b''.join(render(root) for root in self.roots))

"""Existing occupied GTA V garage records; no model/slot creation.

SPDX-License-Identifier: GPL-3.0-or-later
PSO pointer layout: CodeWalker; typed members: rage-parser-dumps.
"""
import struct
from rockstar_container import u32

VEHICLE = 2541711729
HOUSE = 1095704148
GARAGES = 1109755184
FLAGS = (
    ('bullets', 'Bullet protection', 2386424170, 79),
    ('fire', 'Fire protection', 779245171, 80),
    ('explosions', 'Explosion protection', 1983399964, 81),
    ('collisions', 'Collision protection', 1473572232, 82),
    ('melee', 'Melee protection', 2407176912, 83),
    ('tires', 'Bulletproof tires', 601072703, 84),
)


def exact(entries, item):
    return [x for x in entries if x[0] == item[0]] == [item]


def array(raw, frame, at, expected, size, limit):
    count, capacity = struct.unpack_from('>HH', raw, at + 8)
    if not 0 <= count <= capacity <= limit:
        raise ValueError('Unrecognized GTA V garage array count.')
    if count == 0:
        return []
    word = u32(raw, at)
    block, offset = word & 4095, word >> 12
    if not 1 <= block <= len(frame.blocks):
        raise ValueError('Invalid GTA V garage block pointer.')
    identity, start, length = frame.blocks[block - 1]
    if identity != expected or length % size or offset % size or offset + count * size > length:
        raise ValueError('GTA V garage pointer does not match its typed records.')
    return list(range(start + offset, start + offset + count * size, size))


class VehicleFields:
    def __init__(self, feature, Field):
        self.feature = feature
        self.plates = {}
        owner = feature.owner
        raw = owner.container.plain
        roots = [(f, at, length) for f in owner.container.frames for h, at, length in f.blocks if h == GARAGES]
        if len(roots) != 1:
            return
        f, at, length = roots[0]
        root = f.structures.get(GARAGES)
        houses = f.structures.get(HOUSE)
        vehicle = f.structures.get(VEHICLE)
        if not root or root[0] != 40 or length != 40 or not houses or houses[0] != 24 or not vehicle or vehicle[0] not in (96, 112):
            return
        if not exact(root[1], (1490745283, 13, 0, 8, 2)) or not exact(houses[1], (642989194, 13, 0, 8, 1)):
            return
        if (256, 12, 0, 0, HOUSE) not in root[1] or (256, 12, 0, 0, VEHICLE) not in houses[1]:
            return
        size = vehicle[0]
        # Two known native layouts; PSCH still has to confirm every offset.
        shift = 0 if size == 96 else 12
        modeloff = 56 if size == 96 else 64
        required = ((1442269562, 6, 0, modeloff, 0), (1697766853, 0, 0, 77 + shift, 0))
        if not all(exact(vehicle[1], item) for item in required):
            return
        try:
            house_rows = array(raw, f, at + 8, HOUSE, 24, 64)
            rows, seen = [], set()
            for house, base in enumerate(house_rows):
                for slot, b in enumerate(array(raw, f, base + 8, VEHICLE, size, 64)):
                    if b in seen:
                        raise ValueError('Duplicate GTA V garage vehicle reference.')
                    seen.add(b)
                    rows.append((house, slot, b))
        except (ValueError, struct.error):
            return
        for house, slot, b in rows:
            if raw[b + 77 + shift] != 1 or u32(raw, b + modeloff) in (0, 0xffffffff):
                continue
            prefix = f'vehicle:{house}:{slot}'
            collection = f'Garage {house + 1} · Vehicle {slot + 1}'
            note = ('Existing occupied garage record only. Vehicle identity, ownership, upgrades and '
                    'slot membership are preserved. Scripts may override saved protections. '
                    'Edited-save loading has not been verified in-game.')
            for key, title, h, off in FLAGS:
                off += shift
                if not exact(vehicle[1], (h, 0, 0, off, 0)) or raw[b + off] not in (0, 1):
                    continue
                key = prefix + ':' + key
                feature.formats[key] = ('>B', b + off)
                owner.fields.append(Field(key, title, raw[b + off], b + off, '', 0, 1,
                    'Saved vehicle', boolean=True, collection=collection, note=note))
            off = 86 + shift
            ref = 524311 if size == 96 else 524312
            if not exact(vehicle[1], (3810156612, 13, 4, off, ref)):
                continue
            data = raw[b + off:b + off + 8]
            value = data.split(b'\0', 1)[0]
            if data[len(value):].strip(b'\0') or any(c < 32 or c > 126 for c in value):
                continue
            key = prefix + ':plate'
            self.plates[key] = b + off
            owner.fields.append(Field(key, 'License plate (up to 8 ASCII characters)', value.decode('ascii'),
                b + off, '', 0, 8, 'Saved vehicle', collection=collection, text=True, note=note))

    def patch(self, plain, changes):
        for key, at in self.plates.items():
            if key not in changes:
                continue
            value = changes[key]
            if not isinstance(value, str) or len(value) > 8 or any(ord(c) < 32 or ord(c) > 126 for c in value):
                raise ValueError('A GTA V license plate accepts up to 8 printable ASCII characters.')
            plain[at:at + 8] = value.encode('ascii').ljust(8, b'\0')

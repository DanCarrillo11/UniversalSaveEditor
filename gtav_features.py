"""Schema-gated GTA V story player and world fields.

SPDX-License-Identifier: GPL-3.0-or-later
Scalar schema facts: alexguirre/rage-parser-dumps; see SOURCES.md.
No script globals, account identifiers or online state are exposed.
"""
import math
import struct


PLAYER = 2383497134
WORLD = 1712306115
GARAGES = 1109755184
# field hash, scalar type, byte offset, encoding, lower/upper editor bounds.
PLAYER_FIELDS = (
    ('stamina_flag', 'Does not get tired', 1834379285, 0, 20, '>B', 0, 1),
    ('reload_flag', 'Fast reload', 1770698022, 0, 21, '>B', 0, 1),
    ('fire_flag', 'Fire protection', 1402367612, 0, 22, '>B', 0, 1),
    ('max_health', 'Maximum health', 495965803, 4, 24, '>H', 1, 1000),
    ('max_armour', 'Maximum armor', 436447855, 4, 26, '>H', 0, 1000),
    ('drive_by', 'Drive-by shooting allowed', 2978589556, 0, 28, '>B', 0, 1),
    ('gangs', 'Can be hassled by gangs', 2123147925, 0, 29, '>B', 0, 1),
    ('health', 'Health', 137683408, 7, 64, '>f', 1, 1000),
    ('armour', 'Armor', 3562964998, 7, 68, '>f', 0, 1000),
)
WORLD_FIELDS = (
    ('hour', 'Hour', 3364437253, 6, 44, '>I', 0, 23),
    ('minute', 'Minute', 4220276760, 6, 48, '>I', 0, 59),
    ('second', 'Second', 2925909707, 6, 52, '>I', 0, 59),
)
GARAGE_FIELDS = (
    ('free_resprays', 'Free resprays', 3725757729, 0, 0, '>B', 0, 1),
    ('no_resprays', 'Disable resprays', 1377080091, 0, 1, '>B', 0, 1),
)
NOTE = ('Existing saved state only; scripts may reset it after loading or switching '
        'characters. File-level validation does not establish in-game persistence.')


class GtavFeatures:
    def __init__(self, owner, Field):
        self.owner = owner
        self.formats = {}
        for identity, size, prefix, group, collection, specs in (
            (PLAYER, 208, 'player', 'Attributes', 'Saved player', PLAYER_FIELDS),
            (WORLD, 160, 'world', 'Clock', 'World', WORLD_FIELDS),
            (GARAGES, 40, 'garages', 'Garage services', 'Vehicles', GARAGE_FIELDS),
        ):
            candidates = [(frame, at, length) for frame in owner.container.frames
                          for h, at, length in frame.blocks if h == identity]
            # Root singleton only. Duplicates, alternate layouts and partial
            # records cannot accidentally turn into writable scalar fields.
            if len(candidates) != 1:
                continue
            frame, at, length = candidates[0]
            schema = frame.structures.get(identity)
            if length != size or not schema or schema[0] != size:
                continue
            entries = schema[1]
            if any([entry for entry in entries if entry[0] == h] != [(h, t, 0, off, 0)]
                   for _, _, h, t, off, _, _, _ in specs):
                continue
            if identity == PLAYER:
                model = (1442269562, 6, 0, 32, 0)
                if [entry for entry in entries if entry[0] == model[0]] != [model]:
                    continue
                model_value = struct.unpack_from('>I', owner.container.plain, at + 32)[0]
                # Scope is the one serialized active player, never all three.
                from rockstar_container import name_hash
                names = {name_hash('player_zero'): 'Michael', name_hash('player_one'): 'Franklin',
                         name_hash('player_two'): 'Trevor'}
                if model_value not in names:
                    continue
                collection = names[model_value]
                group = 'Saved player attributes'
            for key, title, _, typ, off, fmt, low, high in specs:
                value = struct.unpack_from(fmt, owner.container.plain, at + off)[0]
                if not math.isfinite(value):
                    continue
                key = f'{prefix}:{key}'
                self.formats[key] = (fmt, at + off)
                if typ == 0 and value not in (0, 1):
                    continue
                owner.fields.append(Field(key, title, value, at + off, '', min(low, value), max(high, value),
                    group, decimal=typ == 7, boolean=typ == 0,
                    readonly=not low <= value <= high, collection=collection, note=NOTE))
        from gtav_vehicles import VehicleFields
        self.vehicles = VehicleFields(self, Field)

    def patch(self, plain, changes):
        changes = dict(changes)
        for current, maximum in (('player:health', 'player:max_health'), ('player:armour', 'player:max_armour')):
            if not any(key in changes for key in (current, maximum)):
                continue
            if current not in self.formats or maximum not in self.formats:
                raise ValueError('The saved player health/armor pair is not fully recognized.')
            values = {field.key: field.value for field in self.owner.fields}
            limit = changes.get(maximum, values[maximum])
            value = changes.get(current, values[current])
            if value > limit:
                if current in changes:
                    raise ValueError('Health and armor cannot exceed their saved maximum.')
                # A lower maximum also lowers the current value in the copy.
                changes[current] = limit
        for key, value in changes.items():
            if key in self.formats:
                fmt, at = self.formats[key]
                struct.pack_into(fmt, plain, at, value)
        self.vehicles.patch(plain, changes)

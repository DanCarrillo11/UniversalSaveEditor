"""Typed story inventories and masked Ammu-Nation acquisition statistics.

SPDX-License-Identifier: GPL-3.0-or-later
Format/name facts and verification limits are documented in SOURCES.md.
"""
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import json
import struct
import sys
from rockstar_container import name_hash, u32

CHARACTERS = ('Michael', 'Franklin', 'Trevor')
SCRIPT = 0x77714D97
SIGNED_STATS = 0x83125968
STAT_SCHEMA = (8, ((3742647683, 5, 0, 0, 0), (3021077118, 5, 0, 4, 0)))


@lru_cache(maxsize=1)
def catalog():
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return json.loads((root/'assets/gtav-weapons.json').read_text(encoding='utf8'))


def embedded(frame, identity, base, key, child):
    """Resolve exactly one embedded member, including both PSCH offset bits."""
    schema = frame.structures.get(identity)
    target = frame.structures.get(child)
    if not schema or not target:
        raise ValueError('Missing GTA V script schema.')
    members = [e for e in schema[1] if e[0] == key]
    if len(members) != 1:
        raise ValueError('Ambiguous GTA V script member.')
    _, kind, subtype, offset, ref = members[0]
    offset += (subtype & 0xc0) << 10
    if kind != 12 or subtype & 63 or ref != child or offset + target[0] > schema[0]:
        raise ValueError('Unrecognized GTA V embedded inventory.')
    return base + offset


class WeaponFields:
    def __init__(self, feature, Field):
        self.owner = feature.owner
        self.bits = {}
        self.dependencies = {}
        self.ammo = {}
        self.ammo_groups = defaultdict(list)
        self.records = {}
        self.strides = {}
        self.inventory_fields = {}
        self._inventories(Field)
        self._shops(Field)

    def _shops(self, Field):
        raw = self.owner.container.plain
        found = defaultdict(list)
        for frame in self.owner.container.frames:
            if frame.structures.get(SIGNED_STATS) != STAT_SCHEMA:
                continue
            for identity, base, length in frame.blocks:
                if identity == SIGNED_STATS and length % 8 == 0:
                    for at in range(base, base + length, 8):
                        found[u32(raw, at)].append(at + 4)
        def position(character, bank):
            matches = found[name_hash(f'sp{character}_weap_{bank}')]
            return matches[0] if len(matches) == 1 else None
        for character, name in enumerate(CHARACTERS):
            for weapon in catalog()['shop']:
                unlock = next(r for r in weapon['shop'] if r['bank'].startswith('unlock_'))
                unlock_at = position(character, unlock['bank'])
                purchase = next(r for r in weapon['shop'] if r['bank'].startswith('purch_'))
                purchase_at = position(character, purchase['bank'])
                if unlock_at is None or purchase_at is None:
                    continue
                for row in weapon['shop']:
                    bank, bit = row['bank'], row['bit']
                    at = position(character, bank)
                    if at is None:
                        continue
                    dependencies = []
                    if bank.startswith('purch_'):
                        dependencies.append((unlock_at, unlock['bit']))
                    elif bank.startswith('addon_purch_'):
                        other = position(character, bank.replace('addon_purch_', 'addon_unlock_'))
                        if other is None:
                            continue
                        dependencies.extend(((other, bit), (unlock_at, unlock['bit'])))
                    elif bank.startswith('tint_purch_'):
                        dependencies.append((unlock_at, unlock['bit']))
                    key = f'weapon_shop:{character}:{weapon["hash"]:08x}:{bank}:{bit}'
                    self.bits[key] = (at, bit)
                    self.dependencies[key] = dependencies
                    title = {'Unlocked': 'Available in Ammu-Nation', 'Purchased': 'Purchased from Ammu-Nation'}.get(
                        row['label'], row['label'] + ' purchased')
                    self.owner.fields.append(Field(key, title, (u32(raw, at) >> bit) & 1, at, '', 0, 1,
                        'Weapon shop · ' + weapon['label'], boolean=True, collection=name,
                        note=('Shop availability does not add the weapon to your inventory. Edition restrictions may still apply.'
                              if row['label'] == 'Unlocked' else '')))

    def _inventories(self, Field):
        raw = self.owner.container.plain
        roots = [(f, at, length) for f in self.owner.container.frames
                 for h, at, length in f.blocks if h == SCRIPT]
        if len(roots) != 1:
            return
        frame, base, length = roots[0]
        if not frame.structures.get(SCRIPT) or length != frame.structures[SCRIPT][0]:
            return
        try:
            base = embedded(frame, SCRIPT, base, 0x622852C8, 0x77714E0A)
            base = embedded(frame, 0x77714E0A, base, 0x96A2A7B0, 0x77714E13)
            array_size = frame.structures[0x77714E13][0]
            shapes = {6824: (2272,24,50), 11456: (3816,40,51)}
            if array_size not in shapes or raw[base] != 3:
                return
            player_size, stride, extra_count = shapes[array_size]
            rows = []
            for character, key in enumerate((0x6437837C, 0xD83D1027, 0xB3EF3343)):
                player = embedded(frame, 0x77714E13, base, key, 0x77714E14)
                if frame.structures[0x77714E14][0] != player_size:
                    return
                for member, child, count in ((3184939672, 0x77714E15, 44), (2572158464, 0x77714E16, extra_count)):
                    at = embedded(frame, 0x77714E14, player, member, child)
                    size, entries = frame.structures[child]
                    # Every cell has a signed 32-bit value and opaque padding;
                    # the fixed array count occupies the first byte, not a u32.
                    if size != 8 + count * stride or raw[at] != count or len(entries) != count * (stride//8):
                        return
                    expected = set(range(8, size, 8))
                    if (len({e[0] for e in entries}) != len(entries) or
                        {e[3] for e in entries} != expected or
                        any(e[1:3] != (5, 0) or e[4] for e in entries) or
                        not all(item in entries for item in ((1841282083, 5, 0, 8, 0),
                            (3658223146, 5, 0, 16, 0), (1773797100, 5, 0, 24, 0)))):
                        return
                    if stride == 40 and not all(item in entries for item in (
                            (3352058537,5,0,32,0),(2867619800,5,0,40,0))):
                        return
                    rows.extend((character, at + 8 + slot * stride, member == 3184939672, slot) for slot in range(count))
            if len({at for _, at, _, _ in rows}) != len(rows):
                return
        except (KeyError, ValueError, struct.error, IndexError):
            return
        names = {w['hash']: w for w in catalog()['inventory']}
        seen = defaultdict(list)
        for character, at, _, _ in rows:
            seen[character, u32(raw, at)].append(at)
        ambiguous_characters = {c for (c,h),positions in seen.items() if h and len(positions) > 1}
        slots = {w['slot']: w for w in names.values() if 'slot' in w}
        for character, at, standard, slot in rows:
            if character in ambiguous_characters:
                continue
            identity = u32(raw, at)
            weapon = slots.get(slot) if standard else names.get(identity)
            if not weapon or identity not in (0, weapon['hash']):
                continue
            if (identity and len(seen[character, identity]) != 1) or (not identity and any(u32(raw, at+d) for d in range(8,stride,8))):
                continue
            if not identity and seen[character, weapon['hash']]:
                continue
            prefix = f'weapon_inventory:{character}:{weapon["hash"]:08x}'
            weapon = dict(weapon)
            if stride == 40:
                weapon['components'] = weapon['modern_components']
            self.records[prefix] = (character, at, weapon, bool(identity), standard)
            self.strides[prefix] = stride
            def add(suffix, label, value, maximum=1, boolean=False, choices=(), readonly=False):
                key = prefix + ':' + suffix
                self.inventory_fields[key] = (prefix, suffix)
                offset = at if suffix == 'present' else at+24 if suffix == 'tint' and stride == 40 else at+16
                self.owner.fields.append(Field(key, label, value, offset, '',
                    0, maximum, 'Inventory · ' + weapon['label'], collection=CHARACTERS[character],
                    boolean=boolean, choices=choices, readonly=readonly,
                    note=('Adding or equipping also grants recognized shop ownership. Game loading remains unverified.'
                          if suffix == 'present' else '')))
            if standard:
                add('present', 'Carried in inventory', int(bool(identity)), boolean=True)
            flags = u32(raw, at + 16)
            tint = (flags >> 20) & 255 if stride == 24 else u32(raw,at+24)
            if weapon['tints'] and (identity or standard):
                valid = not identity or (tint != 0 and tint & (tint - 1) == 0 if stride == 24 else tint < len(weapon['tints']))
                index = (tint.bit_length()-1 if stride == 24 else tint) if identity and valid else 0
                add('tint', 'Equipped color', index, len(weapon['tints'])-1,
                    choices=tuple(weapon['tints']), readonly=not valid)
            for component in weapon['components']:
                add(f'component_{component["bit"]}', component['label'],
                    int(bool(flags & (1 << component['bit']))), boolean=True)
            if weapon['ammo'] in (None, 'NULL') or not weapon['max_ammo']:
                continue
            identity = weapon['hash']
            at += 8
            key = f'weapon_ammo:{character}:{identity:08x}'
            group = (character, weapon['ammo'])
            self.ammo[key] = (at, group, weapon['max_ammo'])
            if self.records[prefix][3]:
                self.ammo_groups[group].append(key)
        for key, (at, group, maximum) in self.ammo.items():
            character = group[0]
            identity = int(key.rsplit(':', 1)[1], 16)
            value = u32(raw, at)
            cap = min([maximum]+[self.ammo[k][2] for k in self.ammo_groups[group]])
            coherent = len({u32(raw, self.ammo[k][0]) for k in self.ammo_groups[group]}) <= 1
            self.owner.fields.append(Field(key, 'Ammunition', value, at, '',
                0, max(cap, value), 'Inventory · ' + names[identity]['label'], collection=CHARACTERS[character],
                readonly=not coherent or value > cap,
                note='Automatically shared with this character’s weapons using the same ammunition. '
                     'Entering ammunition for an empty base slot also adds the weapon. Skill may limit ammo in-game.'))

    def patch(self, plain, changes):
        changes = dict(changes)
        self._patch_inventory(plain, changes)
        requests = {}
        def request(at, bit, value):
            address = (at, bit)
            if address in requests and requests[address] != value:
                raise ValueError('Conflicting GTA V weapon purchase/unlock settings.')
            requests[address] = value
        for key, value in changes.items():
            if key in self.bits:
                request(*self.bits[key], value)
        for key, value in changes.items():
            if key in self.bits and value:
                for at, bit in self.dependencies[key]:
                    request(at, bit, 1)
        # Turning off availability also turns off its purchase flag. Other
        # acquisition and inventory state stays unchanged.
        for key, value in changes.items():
            if key in self.bits and not value and ':unlock_' in key:
                purchased = key.replace(':unlock_', ':purch_')
                if purchased in self.bits:
                    request(*self.bits[purchased], 0)
        for (at, bit), value in requests.items():
            mask = 1 << bit
            current = u32(plain, at)
            struct.pack_into('>I', plain, at, current | mask if value else current & ~mask)
        ammo_requests = {}
        for key, value in changes.items():
            if key not in self.ammo:
                continue
            _, group, _ = self.ammo[key]
            if group in ammo_requests and ammo_requests[group] != value:
                raise ValueError('Weapons sharing ammunition must use the same total.')
            cap = min([self.ammo[key][2]]+[self.ammo[k][2] for k in self.ammo_groups[group]])
            if not 0 <= value <= cap:
                raise ValueError('GTA V ammunition exceeds the recognized story capacity.')
            ammo_requests[group] = value
        for group, value in ammo_requests.items():
            targets = {key for key,(at,g,_) in self.ammo.items() if g == group and
                       u32(plain,at-8) == int(key.rsplit(':',1)[1],16)}
            for key in targets:
                struct.pack_into('>I', plain, self.ammo[key][0], value)

    def _patch_inventory(self, plain, changes):
        def acquire(character, weapon, labels):
            wanted = {label.casefold() for label in labels}
            for row in catalog()['shop']:
                if row['hash'] != weapon['hash']:
                    continue
                for field in row['shop']:
                    if field['label'].casefold() not in wanted:
                        continue
                    key = f'weapon_shop:{character}:{weapon["hash"]:08x}:{field["bank"]}:{field["bit"]}'
                    if key in self.bits:
                        if key in changes and changes[key] != 1:
                            raise ValueError('Weapon acquisition conflicts with its shop unlock/purchase settings.')
                        changes[key] = 1
        requested = defaultdict(dict)
        for key, value in changes.items():
            if key in self.inventory_fields:
                prefix, suffix = self.inventory_fields[key]
                requested[prefix][suffix] = value
            elif key in self.ammo:
                prefix = key.replace('weapon_ammo:', 'weapon_inventory:')
                requested[prefix]['ammo'] = value
        for prefix, edits in requested.items():
            character, at, weapon, owned, standard = self.records[prefix]
            stride = self.strides[prefix]
            present = edits.get('present', int(owned))
            if not present and any(v for k,v in edits.items() if k != 'present'):
                if 'present' in edits:
                    raise ValueError('A removed weapon cannot receive ammunition or customization.')
                present = 1
            if present and not owned:
                if not standard:
                    raise ValueError('Unrecognized GTA V weapon acquisition slot.')
                flags = (1 << 20 if stride == 24 else 0) | sum(1 << c['bit'] for c in weapon['components'] if c['default'])
                struct.pack_into('>I', plain, at, weapon['hash'])
                struct.pack_into('>I', plain, at+16, flags)
                if weapon['id'] == 'GADGET_PARACHUTE':
                    struct.pack_into('>I',plain,at+8,1)
                # Preserve a shared existing ammo pool; the user may supply a
                # different total in this same operation.
                ammo_key = prefix.replace('weapon_inventory:', 'weapon_ammo:')
                if ammo_key in self.ammo:
                    _, group, _ = self.ammo[ammo_key]
                    others = self.ammo_groups[group]
                    struct.pack_into('>I',plain,at+8,u32(plain,self.ammo[others[0]][0]) if others else 0)
                acquire(character, weapon, ['Unlocked', 'Purchased'] +
                        [c['label'] for c in weapon['components'] if c['default']])
            if not present:
                if 'present' in edits:
                    for delta in range(0,stride,8):
                        struct.pack_into('>I',plain,at+delta,0)
                continue
            flags = u32(plain,at+16)
            if 'tint' in edits:
                if stride == 24:
                    flags = flags & ~(255 << 20) | (1 << (20 + edits['tint']))
                else:
                    struct.pack_into('>I',plain,at+24,edits['tint'])
                acquire(character, weapon, [weapon['tints'][edits['tint']]])
            enabled = [c for c in weapon['components'] if edits.get(f'component_{c["bit"]}') == 1]
            for c in enabled:
                acquire(character, weapon, [c['label']])
                peers = [p for p in weapon['components'] if p['slot'] == c['slot'] and p['bit'] != c['bit']]
                if c['slot'] and any(edits.get(f'component_{p["bit"]}') == 1 for p in peers):
                    raise ValueError('Select only one GTA V component for each attachment point.')
                if c['slot']:
                    for p in peers:
                        flags &= ~(1 << p['bit'])
            for c in weapon['components']:
                value = edits.get(f'component_{c["bit"]}')
                if value is not None:
                    flags = flags | (1 << c['bit']) if value else flags & ~(1 << c['bit'])
            clips = [c for c in weapon['components'] if c['slot'] == 'WAPClip']
            if clips and any(f'component_{c["bit"]}' in edits for c in clips) and not any(flags & (1 << c['bit']) for c in clips):
                raise ValueError('Choose a magazine before removing the weapon’s current magazine.')
            struct.pack_into('>I',plain,at+16,flags)

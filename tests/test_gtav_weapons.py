"""Independent native shapes, masked bits and shared ammunition invariants."""
import struct
import unittest
from core import Save
from rockstar_container import RockstarContainer, name_hash, u32
from test_gtav_features import fixture


def shop_stats():
    banks = [(prefix, count) for prefix, count in (('unlock',3),('purch',3),
             ('addon_unlock',7),('addon_purch',7),('tint_purch',13))]
    return b''.join(struct.pack('>II', name_hash(f'sp{c}_weap_{prefix}_{n}'), 0)
                    for c in range(3) for prefix, count in banks for n in range(count))


def script_blocks(stride=24):
    # Extended offset bit 7 must contribute 131072 bytes, not wrap at 65536.
    offset = 131080
    modern = stride == 40
    main_size = 34592 if modern else 28416
    player_size = 3816 if modern else 2272
    extra_count = 51 if modern else 50
    standard_size = 8+44*stride
    root = bytearray(offset + main_size)
    players = offset + 2384
    root[players:players+8] = b'\x03opaque!'
    for c in range(3):
        player = players + 8 + c * player_size
        for pool, count in ((0,44),(standard_size,extra_count)):
            root[player+pool:player+pool+8] = bytes([count])+b'header!'
        for slot, weapon, ammo, flags in ((8,'weapon_pistol',42,0x00100009),
                (9,'weapon_combatpistol',42,0x00100001), (26,'weapon_grenade',3,0x00100000)):
            at = player + 8 + slot * stride
            if modern:
                flags=2 if weapon=='weapon_pistol' else 1
            for delta, value in ((0,name_hash(weapon)),(8,ammo),(16,flags)):
                struct.pack_into('>I',root,at+delta,value)
                root[at+delta+4:at+delta+8] = b'keep'
            if modern:
                struct.pack_into('>I',root,at+32,0xffffffff)
    yield 0x77714D97, root, len(root), [(0x622852C8,12,128,8,0x77714E0A)]
    yield 0x77714E0A, b'', main_size, [(0x96A2A7B0,12,0,2384,0x77714E13)]
    yield 0x77714E13, b'', 8+3*player_size, [(h,12,0,8+n*player_size,0x77714E14)
        for n,h in enumerate((0x6437837C,0xD83D1027,0xB3EF3343))]
    yield 0x77714E14, b'', player_size, [(3184939672,12,0,0,0x77714E15),(2572158464,12,0,standard_size,0x77714E16)]
    for identity, count in ((0x77714E15,44),(0x77714E16,extra_count)):
        fields = [(1841282083,5,0,8,0),(3658223146,5,0,16,0),(1773797100,5,0,24,0)]
        if modern:fields += [(3352058537,5,0,32,0),(2867619800,5,0,40,0)]
        cells=stride//8
        fields += [(0xE0000000 + n,5,0,8+n*8,0) for n in range(cells,count*cells)]
        yield identity, b'', 8+count*stride, fields


def fields(save):
    return {f.key:f for f in save.slots[0].fields}


def mutate(save, change):
    plain=bytearray(save.rockstar.container.plain)
    change(plain)
    return Save(save.rockstar.container.encode(plain),'gtav')


class WeaponTests(unittest.TestCase):
    def test_shop_and_inventory_are_separate_for_three_characters(self):
        save=Save(fixture(weapons=True),'gtav')
        self.assertEqual(len(save.rockstar.gtav.weapons.bits),1191)
        self.assertEqual(len(save.rockstar.gtav.weapons.ammo),84)
        self.assertEqual(save.patched({}),fixture(weapons=True))
        from editor_layout import organize_fields
        categories=organize_fields('gtav',save.slots[0].fields)
        equipment=next(c for c in categories if c.name=='Equipment')
        self.assertEqual({s.selection for s in equipment.sections if any(f.key.startswith('weapon_shop:') for f in s.fields)},
                         {'Michael','Franklin','Trevor'})
        self.assertEqual(equipment.selector_label,'Character')
        self.assertEqual(sum(s.name=='Pistol' for s in equipment.sections),3)
        self.assertTrue(all(not s.name.startswith(('Inventory ·','Weapon shop ·')) for s in equipment.sections))

    def test_purchase_unlock_dependency_and_bit31_preserve_neighbor_bits(self):
        for encrypted in (False,True):
            save=Save(fixture(encrypted,weapons=True),'gtav')
            key='weapon_shop:1:13532244:purch_0:31'  # Micro SMG, not pistol.
            self.assertIn(key,fields(save))
            at=fields(save)[key].offset
            save=mutate(save,lambda raw:struct.pack_into('>I',raw,at,0x12345678))
            before=save.rockstar.container.plain
            after=Save(save.patched({(0,key):1}),'gtav')
            self.assertEqual(u32(after.rockstar.container.plain,at),0x92345678)
            unlock=key.replace('purch_0','unlock_0')
            self.assertEqual(fields(after)[unlock].value,1)
            self.assertEqual(fields(after)[key].value,1)
            # Other characters and all inventory cells are unchanged.
            for k,f in fields(save).items():
                if k not in (key,unlock) and f.key.startswith('weapon_'):
                    self.assertEqual(fields(after)[k].value,f.value,k)
            with self.assertRaisesRegex(ValueError,'Conflicting'):
                save.patched({(0,key):1,(0,unlock):0})
            off=Save(after.patched({(0,unlock):0}),'gtav')
            self.assertEqual(fields(off)[key].value,0)

    def test_attachment_purchase_sets_only_corresponding_unlock_bits(self):
        save=Save(fixture(weapons=True),'gtav')
        key='weapon_shop:0:1b06d571:addon_purch_0:27'  # Pistol suppressor.
        self.assertIn(key,fields(save))
        weapons=save.rockstar.gtav.weapons
        after=Save(save.patched({(0,key):1}),'gtav')
        self.assertEqual(fields(after)[key].value,1)
        for at,bit in weapons.dependencies[key]:
            self.assertTrue(u32(after.rockstar.container.plain,at)&(1<<bit))
        self.assertFalse(fields(after)['weapon_shop:0:1b06d571:purch_0:25'].value)

    def test_shared_ammo_sync_conflicts_capacity_and_exact_span(self):
        for encrypted in (False,True):
            save=Save(fixture(encrypted,weapons=True),'gtav')
            pistol='weapon_ammo:2:1b06d571'
            combat='weapon_ammo:2:5ef9fec4'
            out=save.patched({(0,pistol):9999})
            after=Save(out,'gtav')
            self.assertEqual(fields(after)[combat].value,9999)
            self.assertEqual(fields(after)['weapon_ammo:0:1b06d571'].value,42)
            before=save.rockstar.container.plain
            allowed=set()
            for k in (pistol,combat):
                allowed.update(range(fields(save)[k].offset,fields(save)[k].offset+4))
            for _,at in save.rockstar.container.checks:allowed.update(range(at+12,at+16))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after.rockstar.container.plain))))
            self.assertEqual(after.patched({(0,pistol):42}),fixture(encrypted,weapons=True))
            with self.assertRaisesRegex(ValueError,'same total'):
                save.patched({(0,pistol):12,(0,combat):13})
            grenade='weapon_ammo:0:93e220bd'
            self.assertEqual(fields(save)[grenade].maximum,25)
            with self.assertRaises(ValueError):save.patched({(0,grenade):26})

    def test_inconsistent_ammo_or_bad_counts_protect_inventory(self):
        save=Save(fixture(weapons=True),'gtav')
        key='weapon_ammo:0:1b06d571'
        damaged=mutate(save,lambda raw:struct.pack_into('>I',raw,fields(save)[key].offset,100))
        self.assertTrue(fields(damaged)[key].readonly)
        with self.assertRaises(ValueError):damaged.patched({(0,key):101})
        root=next(at for h,at,length in save.rockstar.container.frames[0].blocks if h==0x77714D97)
        damaged=mutate(save,lambda raw:raw.__setitem__(root+131080+2384+8,43))
        self.assertFalse(damaged.rockstar.gtav.weapons.ammo)
        self.assertEqual(len(damaged.rockstar.gtav.weapons.bits),1191)

    def test_duplicate_stat_keys_never_write_first_match(self):
        save=Save(fixture(weapons=True),'gtav')
        plain=bytearray(save.rockstar.container.plain)
        key='weapon_shop:0:1b06d571:unlock_0:25'
        at=fields(save)[key].offset
        other=fields(save)['weapon_shop:0:13532244:unlock_0:31'].offset
        # Same bank already shares this offset: duplicate a different bank row.
        other=fields(save)['weapon_shop:0:99b507ea:unlock_1:26'].offset
        struct.pack_into('>I',plain,other-4,u32(plain,at-4))
        damaged=Save(save.rockstar.container.encode(plain),'gtav')
        self.assertNotIn(key,fields(damaged))

    def test_base_weapon_creation_ammo_and_automatic_shop_acquisition(self):
        save=Save(fixture(weapons=True),'gtav')
        prefix='weapon_inventory:1:22d8fe39'  # AP pistol, canonical slot 10.
        present=prefix+':present'
        ammo='weapon_ammo:1:22d8fe39'
        self.assertEqual(fields(save)[present].value,0)
        after=Save(save.patched({(0,present):1,(0,ammo):75,(0,prefix+':tint'):7}),'gtav')
        for key,value in ((present,1),(ammo,75),(prefix+':tint',7)):
            self.assertEqual(fields(after)[key].value,value)
        self.assertEqual(fields(after)['weapon_ammo:1:1b06d571'].value,75)
        self.assertEqual(fields(after)['weapon_shop:1:22d8fe39:unlock_0:27'].value,1)
        self.assertEqual(fields(after)['weapon_shop:1:22d8fe39:purch_0:27'].value,1)
        with self.assertRaisesRegex(ValueError,'removed weapon'):
            save.patched({(0,present):0,(0,ammo):5})
        removed=Save(after.patched({(0,present):0,(0,'weapon_ammo:1:1b06d571'):60}),'gtav')
        self.assertEqual(fields(removed)[present].value,0)
        self.assertEqual(fields(removed)[ammo].value,0)

    def test_tint_one_hot_mask_and_exclusive_components_preserve_unknown_bits(self):
        save=Save(fixture(weapons=True),'gtav')
        prefix='weapon_inventory:0:1b06d571'
        _,at,_,_,_=save.rockstar.gtav.weapons.records[prefix]
        save=mutate(save,lambda raw:struct.pack_into('>I',raw,at+16,0x80140009))
        out=Save(save.patched({(0,prefix+':tint'):3,(0,prefix+':component_1'):1}),'gtav')
        self.assertEqual(u32(out.rockstar.container.plain,at+16),0x8084000a)
        self.assertEqual(fields(out)[prefix+':component_0'].value,0)
        self.assertEqual(fields(out)[prefix+':tint'].value,3)
        with self.assertRaisesRegex(ValueError,'attachment point'):
            save.patched({(0,prefix+':component_0'):1,(0,prefix+':component_1'):1})
        ambiguous=mutate(save,lambda raw:struct.pack_into('>I',raw,at+16,0x00300009))
        self.assertTrue(fields(ambiguous)[prefix+':tint'].readonly)
        with self.assertRaisesRegex(ValueError,'Choose a magazine'):
            save.patched({(0,prefix+':component_0'):0})

    def test_five_cell_revision_has_separate_tint_and_different_component_bits(self):
        for encrypted in (False,True):
            save=Save(fixture(encrypted,weapons=True,weapon_stride=40),'gtav')
            prefix='weapon_inventory:0:1b06d571'
            _,at,weapon,_,_=save.rockstar.gtav.weapons.records[prefix]
            self.assertEqual(save.rockstar.gtav.weapons.strides[prefix],40)
            self.assertEqual(fields(save)[prefix+':component_1'].label,'Default Clip')
            self.assertEqual(fields(save)[prefix+':component_1'].value,1)
            out=Save(save.patched({(0,prefix+':tint'):7,(0,prefix+':component_2'):1}),'gtav')
            self.assertEqual(u32(out.rockstar.container.plain,at+16),4)
            self.assertEqual(u32(out.rockstar.container.plain,at+24),7)
            self.assertEqual(u32(out.rockstar.container.plain,at+32),0xffffffff)
            for delta in range(0,40,8):
                self.assertEqual(out.rockstar.container.plain[at+delta+4:at+delta+8],
                                 save.rockstar.container.plain[at+delta+4:at+delta+8])
            added='weapon_inventory:2:22d8fe39:present'
            added_save=Save(save.patched({(0,added):1}),'gtav')
            self.assertEqual(fields(added_save)[added].value,1)
            self.assertEqual(fields(added_save)['weapon_inventory:2:22d8fe39:component_0'].value,1)

    def test_catalog_labels_identifiers_and_slot_facts_are_well_formed(self):
        from gtav_weapons import catalog
        inventory=catalog()['inventory']
        self.assertEqual(len({w['hash'] for w in inventory}),len(inventory))
        self.assertEqual(len([w for w in inventory if 'slot' in w]),35)
        for w in inventory:
            self.assertIsInstance(w['label'],str)
            for c in w['components']+w['modern_components']:
                self.assertIsInstance(c['label'],str)
                self.assertTrue(c['label'])

    def test_parachute_creation_and_duplicate_inventories_are_not_guessed(self):
        save=Save(fixture(weapons=True),'gtav')
        prefix='weapon_inventory:0:fbab5776'
        self.assertIn(prefix+':present',fields(save))
        out=Save(save.patched({(0,prefix+':present'):1}),'gtav')
        at=out.rockstar.gtav.weapons.records[prefix][1]
        self.assertEqual(u32(out.rockstar.container.plain,at+8),1)
        pistol=save.rockstar.gtav.weapons.records['weapon_inventory:0:1b06d571'][1]
        # A second physical pistol occupies the combat-pistol cell. The entire
        # character pool is ambiguous; other protagonists are still independent.
        damaged=mutate(save,lambda raw:struct.pack_into('>I',raw,pistol+24,name_hash('weapon_pistol')))
        self.assertFalse(any(k.startswith('weapon_inventory:0:') for k in fields(damaged)))
        self.assertTrue(any(k.startswith('weapon_inventory:1:') for k in fields(damaged)))

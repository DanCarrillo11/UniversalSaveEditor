"""Independent synthetic PSO graphs; no personal saves or account identifiers."""
import struct
import unittest
from core import Save
from rockstar_container import checksum, aes, RockstarContainer, name_hash
from test_rockstar import section


def fixture(encrypted=False, vehicle_size=112, duplicate=False, malformed=False, weapons=False, weapon_stride=24):
    blocks = []
    definitions = []
    def add(identity, data, size, fields):
        blocks.append((identity, data))
        definitions.append((identity, struct.pack('>3I', len(fields), size, 0) +
                            b''.join(struct.pack('>IBBHI', *x) for x in fields)))
    keys=('TOTAL_CASH','STAMINA','SHOOTING_ABILITY','STRENGTH','STEALTH_ABILITY','FLYING_ABILITY','WHEELIE_ABILITY','LUNG_CAPACITY','SPECIAL_ABILITY')
    stats=b''.join(struct.pack('>Ii',name_hash(f'sp{n}_{k}'),1000 if k=='TOTAL_CASH' else 25) for n in range(3) for k in keys)
    if weapons:
        from test_gtav_weapons import shop_stats
        stats += shop_stats()
    add(2199017832, stats, 8,
        [(3742647683, 5, 0, 0, 0), (3021077118, 5, 0, 4, 0)])
    player = bytearray(208)
    struct.pack_into('>HH', player, 24, 200, 100)
    struct.pack_into('>Iff', player, 32, name_hash('player_one'), 0, 0)
    struct.pack_into('>ff', player, 64, 190, 50)
    fields = [(h, 0, 0, off, 0) for h, off in ((1834379285,20),(1770698022,21),(1402367612,22),(2978589556,28),(2123147925,29))]
    fields += [(495965803,4,0,24,0),(436447855,4,0,26,0),(1442269562,6,0,32,0),(137683408,7,0,64,0),(3562964998,7,0,68,0)]
    add(2383497134, player, 208, fields)
    if duplicate:
        blocks.append((2383497134, player))
    world = bytearray(160)
    struct.pack_into('>6I', world, 44, 12, 30, 15, 20, 5, 2013)
    add(1712306115, world, 160, [(3364437253,6,0,44,0),(4220276760,6,0,48,0),(2925909707,6,0,52,0)])
    garage = bytearray(40)
    house = bytearray(24)
    # Big-endian block pointer followed by opaque runtime/padding word,
    # then native uint16 count/capacity. Values are synthetic, not addresses.
    house_index = len(blocks) + 2
    vehicle_index = len(blocks) + 3
    struct.pack_into('>IIHH', garage, 8, house_index, 0x12345678, 1, 1)
    struct.pack_into('>IIHH', house, 8, vehicle_index if not malformed else 4095, 0x87654321, 1, 1)
    add(1109755184, garage, 40, [(3725757729,0,0,0,0),(1377080091,0,0,1,0),
        (256,12,0,0,1095704148),(1490745283,13,0,8,2)])
    add(1095704148, house, 24, [(256,12,0,0,2541711729),(642989194,13,0,8,1)])
    vehicle = bytearray(vehicle_size)
    shift = 12 if vehicle_size == 112 else 0
    modeloff = 64 if vehicle_size == 112 else 56
    struct.pack_into('>I', vehicle, modeloff, name_hash('adder'))
    vehicle[77 + shift] = 1
    vehicle[86 + shift:94 + shift] = b'TEST1234'
    fields = [(1442269562,6,0,modeloff,0),(1697766853,0,0,77+shift,0)]
    fields += [(h,0,0,off+shift,0) for h,off in ((2386424170,79),(779245171,80),(1983399964,81),(1473572232,82),(2407176912,83),(601072703,84))]
    fields += [(3810156612,13,4,86+shift,524312 if vehicle_size == 112 else 524311)]
    add(2541711729, vehicle, vehicle_size, fields)
    if weapons:
        from test_gtav_weapons import script_blocks
        for identity, payload, size, fields in script_blocks(weapon_stride):
            add(identity, payload, size, fields)
    data = bytearray()
    mapping = struct.pack('>IHH',1,len(blocks),0x7070)
    for identity, payload in blocks:
        mapping += struct.pack('>4I',identity,8+len(data),0,len(payload))
        data += payload
    schema = struct.pack('>I',len(definitions))
    offset = 12 + len(definitions)*8
    for identity, definition in definitions:
        schema += struct.pack('>II',identity,offset)
        offset += len(definition)
    schema += b''.join(d for _,d in definitions)
    frame = section(b'PSIN',data)+section(b'PMAP',mapping)+section(b'PSCH',schema)+section(b'PSIG',b'')
    check = b'CHKS'+struct.pack('>4I',20,len(frame)+20,0,1)
    check = check[:12]+struct.pack('>I',checksum(frame+check[:8]+bytes(8)+check[16:]))+check[16:]
    header = bytearray(0x108)
    struct.pack_into('>I',header,0,1)
    struct.pack_into('>I',header,0x104,checksum(header[4:0x104],checksum(header[:4][::-1],0)))
    body = frame+check
    body += bytes(-len(body)%16)
    return bytes(header)+(aes(body,False) if encrypted else body)


class GtaExpandedTests(unittest.TestCase):
    def test_both_native_vehicle_layouts_and_encryption_preserve_every_unedited_byte(self):
        for size in (96,112):
            for encrypted in (False,True):
                original=fixture(encrypted,size)
                before=Save(original,'gtav')
                self.assertEqual(before.patched({}),original)
                self.assertFalse(before.warnings)
                fields=before.slots[0].fields
                self.assertEqual(len(fields),48)
                changes={(0,f.key): ('NEWPLATE' if f.text else 1-f.value if f.boolean else 10 if f.group=='Clock' else 150 if f.key=='player:health' else 200 if f.key=='player:max_health' else 80 if f.key=='player:max_armour' else 60 if f.key=='player:armour' else 50 if f.group=='Skills' else 4321) for f in fields}
                out=before.patched(changes)
                after=Save(out,'gtav')
                self.assertFalse(after.warnings)
                self.assertEqual(after.patched({(0,f.key):f.value for f in fields}),original)
                allowed=set()
                for f in fields:
                    fmt=before.rockstar.gtav.formats.get(f.key)
                    width=8 if f.text else struct.calcsize(fmt[0]) if fmt else 4
                    allowed.update(range(f.offset,f.offset+width))
                for _,at in before.rockstar.container.checks:allowed.update(range(at+12,at+16))
                self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before.rockstar.container.plain,after.rockstar.container.plain))))
                self.assertEqual(len(out),len(original))

    def test_health_and_armor_maximums_are_consistent(self):
        save=Save(fixture(),'gtav')
        out=Save(save.patched({(0,'player:max_health'):150,(0,'player:max_armour'):20}),'gtav')
        values={f.key:f.value for f in out.slots[0].fields}
        self.assertEqual((values['player:health'],values['player:armour']),(150,20))
        for changes in ({(0,'player:health'):201},{(0,'player:armour'):101},{(0,'player:max_health'):100,(0,'player:health'):101}):
            with self.assertRaisesRegex(ValueError,'cannot exceed'):save.patched(changes)

    def test_duplicate_roots_and_broken_pointers_do_not_expose_guessed_fields(self):
        duplicate=Save(fixture(duplicate=True),'gtav')
        self.assertFalse(any(f.key.startswith('player:') for f in duplicate.slots[0].fields))
        broken=Save(fixture(malformed=True),'gtav')
        self.assertFalse(any(f.key.startswith('vehicle:') for f in broken.slots[0].fields))
        self.assertTrue(any(f.key.startswith('world:') for f in broken.slots[0].fields))

    def test_plate_printable_ascii_and_capacity(self):
        save=Save(fixture(),'gtav');key=(0,'vehicle:0:0:plate')
        for value in ('123456789','éclair','line\nend'):
            with self.assertRaises(ValueError):save.patched({key:value})
        for value in ('','12345678','  A  '):
            after=Save(save.patched({key:value}),'gtav')
            self.assertEqual(next(f.value for f in after.slots[0].fields if f.key==key[1]),value)

    def test_unknown_player_model_and_malformed_schema_protect_player(self):
        container=RockstarContainer(fixture(),'gtav');raw=bytearray(container.plain)
        at=next(at for h,at,length in container.frames[0].blocks if h==2383497134)
        struct.pack_into('>I',raw,at+32,name_hash('unknown_ped'))
        save=Save(container.encode(raw),'gtav')
        self.assertFalse(any(f.key.startswith('player:') for f in save.slots[0].fields))
        # Mutate one schema member type while keeping all container checks valid.
        raw=bytearray(container.plain)
        signature=struct.pack('>IBBHI',495965803,4,0,24,0)
        at=raw.index(signature);raw[at+4]=5
        save=Save(container.encode(raw),'gtav')
        self.assertFalse(any(f.key.startswith('player:') for f in save.slots[0].fields))

    def test_navigation_separates_characters_clock_and_vehicles(self):
        from editor_layout import organize_fields
        fields=Save(fixture(),'gtav').slots[0].fields
        categories=organize_fields('gtav',fields)
        self.assertEqual({c.name for c in categories},{'Characters','Progress','Equipment'})
        self.assertEqual(sum(len(s.fields) for c in categories for s in c.sections),len(fields))

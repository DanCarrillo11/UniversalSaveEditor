"""Native talisman assignment, exclusive groups, swaps and preserved ownership."""
import hashlib,struct,unittest
from core import Save
from elden_loadouts import fingerprint,u32
from elden_talismans import SLOTS,HASH_INDICES,INVALID
from elden_talisman_tables import TALISMANS
from test_elden_loadouts import fixture as equipment

IDS=(1000,1001,1010,3000,3001,7000)


def fixture(capacity=3,source=None):
    raw=bytearray(equipment() if source is None else source);save=Save(raw,'eldenring');c=save.elden_ring.characters[0]
    armaments=save.elden_ring.equipment_loadouts[0].armaments
    held=[struct.unpack_from('<3I',raw,c.held+4+n*12) for n in range(2688)]
    available=[n for n,(h,q,a) in enumerate(held) if h==q==a==0]
    rows={}
    for n,identifier in zip(available,IDS):
        rows[identifier]=n;struct.pack_into('<3I',raw,c.held+4+n*12,0xa0000000|identifier,1,5000+n)
    struct.pack_into('<I',raw,c.held,u32(raw,c.held)+len(rows));raw[c.player+0xbe]=capacity
    for slot,identifier in zip(SLOTS,(1000,3000,0,0)):
        handle=0xa0000000|identifier if identifier else 0
        for at,value in ((c.player+0x280+slot*4,rows[identifier]+0x180 if identifier else INVALID),
                (c.player+0x2f4+slot*4,identifier if identifier else INVALID),(c.player+0x34c+slot*4,handle),
                (armaments+slot*4,0x20000000|identifier if identifier else INVALID)):
            struct.pack_into('<I',raw,at,value)
    struct.pack_into('<I',raw,c.fingerprints+32,fingerprint(raw,c.player+0x2f4,HASH_INDICES))
    for start,length in save.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw)


class TalismanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=fixture()

    def choice(self,loadout,slot,identifier):
        return loadout.options[f'talisman_slot:{slot}'].index(0xa0000000|identifier if identifier else 0)

    def test_owned_assignments_update_exact_references_and_only_their_fingerprint(self):
        raw=self.raw;save=Save(raw,'eldenring');l=save.elden_ring.talisman_loadouts[0];c=l.c
        self.assertTrue(all(not reason for reason in l.reasons.values()))
        changes={(0,'talisman_slot:0'):self.choice(l,0,1010),(0,'talisman_slot:2'):self.choice(l,2,3001)}
        output=save.patched(changes);check=Save(output,'eldenring');after=check.elden_ring.talisman_loadouts[0]
        self.assertFalse(check.warnings)
        for (_,key),value in changes.items():self.assertTrue(l.verifies(after,key,value))
        allowed=set(range(c.start-16,c.start))|set(range(c.fingerprints+32,c.fingerprints+36))
        for slot in (17,19):
            for at in (c.player+0x280+slot*4,c.player+0x2f4+slot*4,c.player+0x34c+slot*4,l.armaments+slot*4):allowed.update(range(at,at+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertEqual(output[c.held:c.held+16+3072*12],raw[c.held:c.held+16+3072*12])
        self.assertEqual(save.patched({}),raw)

    def test_exclusive_tiers_and_dlc_family_are_rejected_but_compatible_boosts_stack(self):
        save=Save(self.raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        for identifier in (1000,1001,7000):
            with self.subTest(identifier=identifier),self.assertRaisesRegex(ValueError,'exclusive accessory group'):
                save.patched({(0,'talisman_slot:2'):self.choice(l,2,identifier)})
        self.assertNotEqual(TALISMANS[0x20000000|3000][1],TALISMANS[0x20000000|3001][1])
        output=save.patched({(0,'talisman_slot:2'):self.choice(l,2,3001)})
        self.assertFalse(Save(output,'eldenring').warnings)

    def test_clear_and_atomic_swap_work_without_creating_or_moving_inventory_items(self):
        save=Save(self.raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        changes={(0,'talisman_slot:0'):self.choice(l,0,3000),(0,'talisman_slot:1'):self.choice(l,1,1000)}
        output=save.patched(changes);other=Save(output,'eldenring').elden_ring.talisman_loadouts[0]
        for (_,key),value in changes.items():self.assertTrue(l.verifies(other,key,value))
        output=save.patched({(0,'talisman_slot:0'):0,(0,'talisman_slot:2'):self.choice(l,2,1001)})
        other=Save(output,'eldenring').elden_ring.talisman_loadouts[0]
        self.assertEqual(other.current[17],0);self.assertFalse(other.reasons[17])

    def test_locked_slots_and_unrecognized_or_duplicate_ownership_stay_protected(self):
        raw=fixture(capacity=1);save=Save(raw,'eldenring')
        field=next(f for f in save.slots[0].fields if f.key=='talisman_slot:2')
        self.assertTrue(field.readonly);self.assertIn('locked',field.note)
        with self.assertRaises(ValueError):save.patched({(0,field.key):1})
        raw=bytearray(self.raw);save=Save(raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        row,identity=l.owned[0xa0000000|1000]
        struct.pack_into('<I',raw,l.c.held+4+row*12,0xa0000000|99999)
        struct.pack_into('<I',raw,l.c.player+0x34c+17*4,0xa0000000|99999)
        other=Save(raw,'eldenring')
        self.assertTrue(all(f.readonly for f in other.slots[0].fields if f.key.startswith('talisman_slot:')))

    def test_native_mirror_disagreement_and_fingerprint_are_not_overwritten(self):
        save=Save(self.raw,'eldenring');l=save.elden_ring.talisman_loadouts[0];c=l.c
        for at in (c.player+0x280+17*4,c.player+0x2f4+17*4,l.armaments+17*4,c.fingerprints+32):
            raw=bytearray(self.raw);raw[at]^=1;parsed=Save(raw,'eldenring')
            field=next(f for f in parsed.slots[0].fields if f.key=='talisman_slot:0')
            self.assertTrue(field.readonly)
            with self.assertRaises(ValueError):parsed.patched({(0,field.key):0},repair_crc=True)

    def test_armor_and_structural_weapon_creation_can_be_combined_with_talisman_assignment(self):
        from test_elden_equipment_creation import ARMOR_ID
        save=Save(self.raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        changes={(0,'talisman_slot:0'):self.choice(l,0,1010),(0,'create_weapon:1000000'):1}
        armor=save.elden_ring.equipment_loadouts[0]
        changes[0,'equipment_slot:12']=next(i for i,h in enumerate(armor.options['equipment_slot:12']) if h!=armor.current[12])
        output=save.patched(changes);parsed=Save(output,'eldenring')
        self.assertFalse(parsed.warnings)
        self.assertTrue(l.verifies(parsed.elden_ring.talisman_loadouts[0],'talisman_slot:0',changes[0,'talisman_slot:0']))

    def test_missing_base_talisman_acquisition_registers_one_copy_and_preserves_existing_equipment(self):
        raw=self.raw;save=Save(raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        identity=0x2000041a;key=f'add_talisman:{identity}'
        self.assertIn(key,l.additions)
        self.assertFalse(any((value&0x0fffffff)>=7000 for value in l.additions.values()))
        self.assertNotIn(f'add_talisman:{0x200003e8}',l.additions)
        output=save.patched({(0,key):1});check=Save(output,'eldenring');other=check.elden_ring.talisman_loadouts[0]
        self.assertTrue(l.verifies_addition(other,key,1));self.assertFalse(check.warnings)
        self.assertNotIn(key,other.additions);self.assertEqual(other.current,l.current)
        self.assertEqual(len(output),len(raw));self.assertEqual(u32(output,l.c.held),u32(raw,l.c.held)+1)
        for n in range(2688):
            at=l.c.held+4+n*12
            if raw[at:at+12]!=bytes(12):self.assertEqual(output[at:at+12],raw[at:at+12])
        self.assertEqual(output[l.c.player:l.c.held],raw[l.c.player:l.c.held])
        self.assertEqual(save.patched({(0,key):0}),raw)

    def test_multiple_acquisitions_combine_with_goods_and_physical_creation(self):
        save=Save(self.raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        keys=list(l.additions)[:4]
        changes={(0,key):1 for key in keys};changes[0,'create_weapon:1000000']=1
        goods=next(f for f in save.slots[0].fields if f.key.startswith('add_goods:'))
        changes[0,goods.key]=1
        output=save.patched(changes);check=Save(output,'eldenring');other=check.elden_ring.talisman_loadouts[0]
        self.assertFalse(check.warnings)
        self.assertTrue(all(l.verifies_addition(other,key,1) for key in keys))
        self.assertEqual(u32(output,other.c.held),u32(self.raw,l.c.held)+6)

    def test_storage_owned_and_dlc_acquisition_are_not_exposed_and_bad_amounts_are_rejected(self):
        raw=bytearray(self.raw);save=Save(raw,'eldenring');l=save.elden_ring.talisman_loadouts[0]
        identity=0x2000041a;key=f'add_talisman:{identity}'
        for value in (-1,2,True,1.2):
            with self.subTest(value=value),self.assertRaises(ValueError):save.patched({(0,key):value})
        storage=l.armaments+156+12+303
        entries=[struct.unpack_from('<3I',raw,storage+4+n*12) for n in range(1920)]
        empty=next(n for n,value in enumerate(entries) if value==(0,0,0))
        struct.pack_into('<3I',raw,storage+4+empty*12,0xa000041a,1,6000)
        struct.pack_into('<I',raw,storage,u32(raw,storage)+1)
        check=Save(raw,'eldenring')
        self.assertNotIn(key,check.elden_ring.talisman_loadouts[0].additions)
        self.assertNotIn(f'add_talisman:{0x20001b62}',check.elden_ring.talisman_loadouts[0].additions)

    def test_legitimate_duplicate_held_and_storage_copies_keep_the_referenced_held_row(self):
        raw=bytearray(self.raw);save=Save(raw,'eldenring');l=save.elden_ring.talisman_loadouts[0];c=l.c
        empty=next(n for n in range(2688) if raw[c.held+4+n*12:c.held+16+n*12]==bytes(12))
        struct.pack_into('<3I',raw,c.held+4+empty*12,0xa00003e8,1,7001)
        struct.pack_into('<I',raw,c.held,u32(raw,c.held)+1)
        struct.pack_into('<I',raw,c.player+0x280+17*4,empty+0x180)
        storage=l.armaments+156+12+303
        stored_empty=next(n for n in range(1920) if raw[storage+4+n*12:storage+16+n*12]==bytes(12))
        struct.pack_into('<3I',raw,storage+4+stored_empty*12,0xa00003e8,1,7003)
        struct.pack_into('<I',raw,storage,u32(raw,storage)+1)
        parsed=Save(raw,'eldenring');other=parsed.elden_ring.talisman_loadouts[0]
        self.assertEqual(other.owned[0xa00003e8][0],empty);self.assertFalse(other.reasons[17])
        output=parsed.patched({(0,'talisman_slot:0'):self.choice(other,0,1010)},repair_crc=True)
        self.assertFalse(Save(output,'eldenring').warnings)
        self.assertEqual(output[storage:storage+16+2048*12],raw[storage:storage+16+2048*12])

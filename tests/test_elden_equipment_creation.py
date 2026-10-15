"""Independent native projection, resize, acquisition and preservation fixtures."""
import hashlib
import struct
import unittest
from collections import Counter
from core import Save
from elden_equipment_tables import ARMOR,WEAPON_CREATION
from elden_ring import BLOCK_SIZE,SLOT_SIZE,GLOBAL_START
from test_expansion import elden_ready


ARMOR_ID=next(iter(ARMOR))

def ready(source=None):
    raw=bytearray(elden_ready(True) if source is None else source);s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
    ash=struct.pack('<2I',0xc0800000,0x80000064)
    weapon=struct.pack('<5IB',0x80800001,1000000,17,23,0xc0800000,0)
    armor=struct.pack('<4I',0x90800002,ARMOR_ID,31,47)
    raw[c.start+32:c.start+77]=ash+weapon+armor
    struct.pack_into('<I',raw,c.held+40,0x80800001)
    for at in (c.player+0x34c,c.profile+382):
        if struct.unpack_from('<I',raw,at)[0]==0x80000001:struct.pack_into('<I',raw,at,0x80800001)
    raw[c.start+SLOT_SIZE-178:c.start+SLOT_SIZE]=bytes(range(178))
    for start,length in s.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw)


class EquipmentCreationTests(unittest.TestCase):
    def test_weapon_and_armor_have_distinct_handles_and_native_records_with_anchored_tail(self):
        raw=ready();s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
        self.assertFalse(s.elden_ring.physical_equipment[0].reason)
        changes={(0,'create_weapon:1000000'):2,(0,'create_armor:'+str(ARMOR_ID)):1}
        out=s.patched(changes);check=Save(out,'eldenring');d=check.elden_ring.characters[0]
        self.assertEqual(d.player-c.player,34)
        created={h:i for h,i in check.elden_ring.physical_equipment[0].handles.items() if h not in s.elden_ring.physical_equipment[0].handles}
        self.assertEqual(Counter(created.values()),Counter({1000000:2,ARMOR_ID:1}))
        self.assertEqual(len(created),3)
        self.assertTrue(all(h&0x800000 for h in created))
        self.assertEqual(set(h&65535 for h in created),{3,4,5})
        self.assertEqual(out[c.start+SLOT_SIZE-178:c.start+SLOT_SIZE],raw[c.start+SLOT_SIZE-178:c.start+SLOT_SIZE])
        self.assertEqual(out[c.start+32:c.start+77],raw[c.start+32:c.start+77])
        # Existing custom Ash, armor parameters and the opaque tail move intact.
        self.assertEqual(out[d.fingerprints+128:d.fingerprints+142],b'KEEP TAIL DATA')
        self.assertEqual(out[0x300+BLOCK_SIZE:],raw[0x300+BLOCK_SIZE:])
        for i,(h,item) in enumerate(created.items()):
            at,size,_,_=next(r for r in check.elden_ring.physical_equipment[0].records if r[2]==h)
            self.assertEqual(out[at+8:at+size],bytes(size-8))
        counters=d.held+8+(2688+384)*12
        self.assertEqual(struct.unpack_from('<2I',out,counters),(436,974))
        self.assertEqual(struct.unpack_from('<I',out,d.held)[0],7)
        self.assertFalse(check.warnings)
        self.assertEqual(s.patched({}),raw)

    def test_bulk_additions_preserve_all_other_sections_and_do_not_truncate_tail(self):
        raw=ready();s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
        keys=[f.key for f in s.slots[0].fields if f.key.startswith('create_weapon:') and not f.readonly][:40]
        changes={(0,k):1 for k in keys};out=s.patched(changes);check=Save(out,'eldenring');d=check.elden_ring.characters[0]
        self.assertEqual(d.player-c.player,520)
        # Compare every relocated byte except the explicit inventory/registry edits.
        before=bytearray(raw[c.player:c.fingerprints+142]);after=bytearray(out[d.player:d.fingerprints+142])
        allowed=set(range(c.held-c.player,c.held-c.player+4))
        allowed.update(range(c.held-c.player+52,c.held-c.player+52+len(keys)*12))
        allowed.update(range(c.held-c.player+8+(2688+384)*12,c.held-c.player+16+(2688+384)*12))
        allowed.update(range(c.registry-c.player,c.registry-c.player+8+(len(keys))*8))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
        self.assertEqual(out[c.start+SLOT_SIZE-178:c.start+SLOT_SIZE],raw[c.start+SLOT_SIZE-178:c.start+SLOT_SIZE])
        self.assertEqual(len(out),len(raw));self.assertFalse(check.warnings)

    def test_creation_combines_with_stats_existing_upgrade_goods_and_other_character(self):
        raw=ready();s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
        out=s.patched({(0,'create_weapon:1000000'):1,(0,'create_armor:'+str(ARMOR_ID)):1,
            (0,'weapon:80800001'):3,(0,'runes'):900,(0,'vigor'):20,(0,'add_goods:190'):5,(1,'runes'):777})
        check=Save(out,'eldenring');d=check.elden_ring.characters[0];v={f.key:f.value for f in check.slots[0].fields}
        self.assertEqual((v['runes'],v['runes_memory'],v['vigor'],v['weapon:80800001']),(900,1600,20,3))
        self.assertEqual(check.elden_ring.added_amount(0,'add_goods:190'),5)
        self.assertEqual(struct.unpack_from('<I',out,d.player+0x2f4)[0],1000003)
        self.assertEqual(struct.unpack_from('<I',out,d.profile+466)[0],1000003)
        self.assertEqual(next(f.value for f in check.slots[1].fields if f.key=='runes'),777)
        self.assertFalse(check.warnings)
        self.assertEqual(bytes(s.raw),raw)

    def test_combined_growth_limit_and_unknown_layout_refuse_without_mutating_source(self):
        raw=bytearray(ready());s=Save(raw,'eldenring');c=s.elden_ring.characters[0];anchor=c.start+SLOT_SIZE-178
        raw[anchor-97]=1;s=Save(raw,'eldenring')
        with self.assertRaisesRegex(ValueError,'combined equipment'):
            s.patched({(0,'create_weapon:1000000'):7,(0,'create_armor:'+str(ARMOR_ID)):1},repair_crc=True)
        self.assertEqual(bytes(s.raw),bytes(raw))
        # Nonzero terminal padding must never be discarded.
        raw[anchor-1]=9;s=Save(raw,'eldenring')
        self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='create_weapon:1000000'))
        with self.assertRaises(ValueError):s.patched({(0,'create_weapon:1000000'):1},repair_crc=True)
        out=s.patched({(0,'runes'):800},repair_crc=True)
        self.assertEqual(out[anchor-97:anchor],raw[anchor-97:anchor])

    def test_duplicate_indices_missing_references_and_foreign_projection_are_protected(self):
        for part in ('generation','duplicate','projection','missing_ash','missing_inventory','missing_equipment'):
            raw=bytearray(ready());s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
            if part=='generation':struct.pack_into('<I',raw,c.start+40,0x80000001)
            if part=='duplicate':struct.pack_into('<I',raw,c.start+61,0x90800001)
            if part=='projection':
                a=bytes(raw[c.start+32:c.start+40]);b=bytes(raw[c.start+40:c.start+61])
                raw[c.start+32:c.start+61]=b+a
            if part=='missing_ash':struct.pack_into('<I',raw,c.start+56,0xc0801111)
            if part=='missing_inventory':struct.pack_into('<I',raw,c.held+40,0x80801234)
            if part=='missing_equipment':struct.pack_into('<I',raw,c.player+0x34c,0x80801234)
            s=Save(raw,'eldenring')
            with self.subTest(part=part):
                self.assertTrue(s.elden_ring.physical_equipment[0].reason)
                self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='create_weapon:1000000'))
                self.assertEqual(s.patched({(0,'runes'):999},repair_crc=True)[c.start+32:c.player],raw[c.start+32:c.player])

    def test_empty_counts_bounds_and_unlisted_equipment_cannot_be_written(self):
        raw=ready();s=Save(raw,'eldenring')
        self.assertEqual(s.patched({(0,'create_weapon:1000000'):0}),raw)
        for key,value in (('create_weapon:1000000',11),('create_armor:12345',1)):
            with self.assertRaises(ValueError):s.patched({(0,key):value})
        self.assertEqual(len(WEAPON_CREATION),377);self.assertEqual(len(ARMOR),559)

    def test_meteorite_staff_cannot_receive_an_invalid_reinforcement(self):
        raw=bytearray(elden_ready());s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
        struct.pack_into('<I',raw,c.start+36,33250000)
        s=Save(raw,'eldenring');field=next(f for f in s.slots[0].fields if f.key=='weapon:80000001')
        self.assertTrue(field.readonly);self.assertEqual(field.maximum,0)
        with self.assertRaises(ValueError):s.patched({(0,field.key):1},repair_crc=True)

    def test_registry_and_acquisition_counter_failures_are_atomic(self):
        for part in ('counter','registry','inventory','menu_collision'):
            raw=bytearray(ready());s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
            if part=='counter':struct.pack_into('<I',raw,c.held+8+(2688+384)*12,0xffffffff)
            if part=='registry':struct.pack_into('<I',raw,c.registry,7000)
            if part=='inventory':
                # Supported physical table but no spare common-inventory rows.
                for n in range(4,2688):struct.pack_into('<3I',raw,c.held+4+n*12,0xb00000be,1,1000+n*2)
                struct.pack_into('<I',raw,c.held,2688)
            if part=='menu_collision':
                struct.pack_into('<I',raw,c.profile+382,0x80800003)
                struct.pack_into('<I',raw,c.profile+382+20*4,0x90800004)
                s=Save(raw,'eldenring');out=s.patched({(0,'create_weapon:1000000'):1},repair_crc=True)
                new=set(Save(out,'eldenring').elden_ring.physical_equipment[0].handles)-set(s.elden_ring.physical_equipment[0].handles)
                self.assertNotIn(0x80800003,new);self.assertTrue(all(h&65535!=4 for h in new))
                self.assertEqual(out[c.profile+382:c.profile+466],raw[c.profile+382:c.profile+466])
                continue
            s=Save(raw,'eldenring');before=bytes(s.raw)
            with self.subTest(part=part),self.assertRaises(ValueError):s.patched({(0,'create_weapon:1000000'):1},repair_crc=True)
            self.assertEqual(bytes(s.raw),before)


if __name__=='__main__':unittest.main()

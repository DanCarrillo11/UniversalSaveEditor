"""Native stock indexes, inventory conservation and standard AP constraints."""
import struct
import unittest
import zlib
from core import Save
from editor_layout import organize_fields
from test_expansion import kh_fixture


def fixture():
    raw,record,start,end=kh_fixture('kh2');raw=bytearray(raw)
    for character,weapon in enumerate((41,75,49)):
        base=record+0x24f0+character*0x114
        struct.pack_into('<H',raw,base,weapon)
        struct.pack_into('<H',raw,base+20,67) # Actual armor category.
        struct.pack_into('<3H',raw,base+84,0x52,0,0) # Guard unequipped; no unknown active entry.
    base=record+0x24f0
    raw[base+15]=1;raw[base+8]=0 # Level AP 0, Ability Ring AP 1.
    struct.pack_into('<I',raw,record+8,Save._kh2_checksum(raw[record:record+0x10fc0]))
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw),record,start,end


def option(save,key,identifier):
    f=next(f for f in save.slots[0].fields if f.key==key)
    return f.art_choices.index(identifier)


class Kh2RelationshipsTests(unittest.TestCase):
    def test_stock_positions_and_artwork_use_distinct_native_identities(self):
        raw,record,*_=fixture();s=Save(raw,'kh2');d={f.key:f for f in s.slots[0].fields}
        for position,name,item in ((0,'Potion',1),(1,'Hi-Potion',2),(33,'Kingdom Key',41),
                                   (34,'Oathkeeper',42),(280,'Two Become One',543),(309,"Executive's Ring",599)):
            f=d[f'inventory:{position}'];self.assertEqual((f.label,f.item_id,f.offset),(name,item,record+0x3580+position))
            out=s.patched({(0,f.key):1})
            self.assertEqual(out[f.offset],1);self.assertFalse(Save(out,'kh2').warnings)
        self.assertNotIn('inventory:20',d)
        for position in (312,319):
            f=d[f'inventory:{position}'];self.assertTrue(f.readonly);self.assertIsNone(f.item_id)
            with self.assertRaises(ValueError):s.patched({(0,f.key):1})
        categories=organize_fields('kh2',s.slots[0].fields)
        for section in next(c.sections for c in categories if c.name=='Collection'):
            if section.name=='Weapons':self.assertIn(d['inventory:280'],section.fields)
        self.assertEqual(s.patched({}),raw)

    def test_consumable_replacement_transfers_exactly_one_copy_and_preserves_other_bytes(self):
        raw,record,start,end=fixture();raw=bytearray(raw);raw[record+0x3581]=1
        s=Save(raw,'kh2');key='character:0:item:0';old=bytes(raw)
        out=s.patched({(0,key):option(s,key,2)},repair_crc=True)
        self.assertEqual(out[record+0x3580:record+0x3582],b'\x01\x00')
        self.assertEqual(struct.unpack_from('<H',out,record+0x24f0+52)[0],2)
        allowed={record+0x3580,record+0x3581}|set(range(record+0x24f0+52,record+0x24f0+54))
        allowed.update(range(record+8,record+12));allowed.update(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        self.assertEqual(bytes(s.raw),old);self.assertFalse(Save(out,'kh2').warnings)

    def test_missing_stock_overflow_and_unknown_equipment_are_rejected(self):
        raw,record,*_=fixture();s=Save(raw,'kh2');key='character:0:item:0'
        with self.assertRaisesRegex(ValueError,'bag transfer'):s.patched({(0,key):option(s,key,2)})
        out=s.patched({(0,'inventory:1'):1,(0,key):option(s,key,2)})
        self.assertEqual(out[record+0x3581],0)
        raw=bytearray(raw);raw[record+0x3580]=99;raw[record+0x3581]=1;s=Save(raw,'kh2')
        with self.assertRaisesRegex(ValueError,'bag transfer'):s.patched({(0,key):option(s,key,2)},repair_crc=True)
        raw[record+0x3580]=255;s=Save(raw,'kh2')
        self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='inventory:0'))

    def test_equipment_swap_is_atomic_and_does_not_require_spare_copies(self):
        raw,record,*_=fixture();raw=bytearray(raw)
        other=record+0x24f0+0x114+36;struct.pack_into('<H',raw,other,9)
        s=Save(raw,'kh2');a,b='character:0:accessory:0','character:1:accessory:0'
        out=s.patched({(0,a):option(s,a,9),(0,b):option(s,b,8)},repair_crc=True)
        self.assertEqual(out[record+0x3580:record+0x36c0],raw[record+0x3580:record+0x36c0])
        self.assertEqual(struct.unpack_from('<H',out,other)[0],8)
        self.assertFalse(Save(out,'kh2').warnings)

    def test_sora_and_dual_wield_form_keyblades_transfer_and_reject_new_duplicates(self):
        raw,record,*_=fixture();raw=bytearray(raw);form=record+0x32f4;struct.pack_into('<H',raw,form,42)
        s=Save(raw,'kh2');a,b='character:0:weapon','form:0:weapon'
        out=s.patched({(0,a):option(s,a,42),(0,b):option(s,b,41)},repair_crc=True)
        self.assertEqual((struct.unpack_from('<H',out,record+0x24f0)[0],struct.unpack_from('<H',out,form)[0]),(42,41))
        self.assertEqual(out[record+0x3580:record+0x36c0],raw[record+0x3580:record+0x36c0])
        with self.assertRaises(ValueError):s.patched({(0,a):option(s,a,42)},repair_crc=True)
        keys={f.key for f in s.slots[0].fields}
        self.assertNotIn('form:1:weapon',keys);self.assertNotIn('form:2:weapon',keys)

    def test_ap_cost_budget_and_explicit_boost_are_checked_together(self):
        raw,record,*_=fixture();s=Save(raw,'kh2');d={f.key:f for f in s.slots[0].fields}
        self.assertEqual(d['character:0:ap_used'].value,0)
        self.assertEqual(d['character:0:ap_capacity'].value,1)
        f=d['character:0:ability:0'];guard=f.choices.index('Guard · Equipped')
        with self.assertRaisesRegex(ValueError,'need 2 AP'):s.patched({(0,f.key):guard})
        out=s.patched({(0,f.key):guard,(0,'character:0:ap_boost'):1})
        values={f.key:f.value for f in Save(out,'kh2').slots[0].fields}
        self.assertEqual((values['character:0:ap_used'],values['character:0:ap_capacity']),(2,2))
        self.assertEqual(struct.unpack_from('<H',out,f.offset)[0],0x8052)
        with self.assertRaises(ValueError):Save(out,'kh2').patched({(0,'character:0:ap_boost'):0})
        with self.assertRaises(ValueError):s.patched({(0,'character:0:ap_capacity'):255})

    def test_unknown_active_abilities_and_unsupported_equipment_are_not_given_an_invented_budget(self):
        raw,record,*_=fixture();raw=bytearray(raw);base=record+0x24f0
        struct.pack_into('<H',raw,base+84,0xfffe);s=Save(raw,'kh2')
        self.assertNotIn('character:0:ap_capacity',{f.key for f in s.slots[0].fields})
        self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='character:0:ability:0'))
        out=s.patched({(0,'munny'):1234},repair_crc=True)
        self.assertEqual(out[base+84:base+86],raw[base+84:base+86])

    def test_existing_ap_excess_is_preserved_but_cannot_be_increased(self):
        raw,record,*_=fixture();raw=bytearray(raw);base=record+0x24f0;struct.pack_into('<H',raw,base+84,0x8052)
        s=Save(raw,'kh2');self.assertEqual(s.party.kh2.budget(raw,record,0),(2,1))
        self.assertEqual(bytes(s.raw),raw)
        s.patched({(0,'character:0:ap_boost'):1},repair_crc=True)
        key='character:0:ability:1';f=next(f for f in s.slots[0].fields if f.key==key)
        with self.assertRaisesRegex(ValueError,'AP'):s.patched({(0,key):f.choices.index('Scan · Equipped')},repair_crc=True)


if __name__=='__main__':unittest.main()

"""Independent field, identity, mirror, registry and byte-preservation checks."""
import hashlib
import struct
import unittest
import zlib
from core import Save, png_chunks
from editor_layout import organize_fields
from elden_registry import register_item
from elden_ring import BLOCK_SIZE, GLOBAL_START, player_hash
from test_core import kingdom, kingdom2
from test_elden_ring import fixture as elden_fixture
from test_re4_uhd import fixture as re4_fixture, reference_crc
from test_re6 import fixture as re6_fixture

def kh_fixture(game):
    raw=bytearray(kingdom() if game=='kh1' else kingdom2())
    start,end=next((s,e) for n,s,e in png_chunks(raw) if n==b'sqEX')
    record=start+16+(200 if game=='kh1' else 100)*0x158
    if game=='kh1':
        for c in (0,1,2,3,9):
            base=record+4+c*0x74;raw[base]=20
            raw[base+0x18]=2;raw[base+0x19]=17
            raw[base+0x32]=(81,103,119,0,0,0,0,0,0,0)[c]
            raw[base+0x40:base+0x43]=bytes((0x8a,0x19,0x7e))
    else:
        for c in (0,1,2,3,12):
            base=record+0x24f0+c*0x114;raw[base+15]=20
            raw[base+16]=1;raw[base+17]=1;raw[base+18]=1
            struct.pack_into('<3H',raw,base+20,53,0,0)
            struct.pack_into('<H',raw,base+36,8)
            struct.pack_into('<H',raw,base+52,1)
            struct.pack_into('<3H',raw,base+84,0x8052,0x52,0x7ffe)
        struct.pack_into('<I',raw,record+8,Save._kh2_checksum(raw[record:record+0x10fc0]))
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw),record,start,end

def elden_ready(equipped=False):
    raw=bytearray(elden_fixture());save=Save(raw,'eldenring');c=save.elden_ring.characters[0]
    struct.pack_into('<I',raw,c.start+36,1000000) # Native Dagger base ID; first GaItem's identity field.
    struct.pack_into('<I',raw,c.held,4)
    counters=c.held+8+(2688+384)*12
    struct.pack_into('<2I',raw,counters,433,968)
    other=next(f.offset for f in save.slots[0].fields if f.key=='storage:0')-4
    raw[other+36:other+48]=bytes(12) # Handle 0x80000001 must have exactly one owner.
    if equipped:
        ids=c.player+0x2f4;handles=ids+0x58
        struct.pack_into('<I',raw,ids,1000000);struct.pack_into('<I',raw,handles,0x80000001)
        # Held list+key list+counters, spells/items/gestures, projectile list.
        arm=c.held+16+(2688+384)*12+116+140+24+4+3*8
        struct.pack_into('<I',raw,arm,1000000)
        struct.pack_into('<I',raw,c.profile+382,0x80000001)
        struct.pack_into('<I',raw,c.profile+466,1000000)
        ordered=b''.join(raw[ids+n*4:ids+n*4+4] for n in (0,2,4,1,3,5,6,8,7,9))
        struct.pack_into('<I',raw,c.fingerprints+28,player_hash(ordered))
    for start,length in save.elden_ring.blocks:
        raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw)

def re4_ready():
    raw=bytearray(re4_fixture());base=0x1ee8
    # UHD case record: itemID(2), quantity or tune-up word(2), weapon rounds(2),
    # opaque word(2), x/y/orientation/case flag(4).
    struct.pack_into('<4H4B',raw,base+0x373c,35,0x2010,80|3,0x55aa,2,3,1,1)
    struct.pack_into('<4H4B',raw,base+0x3748,4,20,0,0x1122,7,4,0,1)
    struct.pack_into('<4H4B',raw,base+0x3754,999,9,7,0x7788,1,2,1,1)
    struct.pack_into('<I',raw,base,reference_crc(raw[base+4:base+0x200]))
    struct.pack_into('<I',raw,base+0xcaf8,reference_crc(raw[base:base+0xcaf8]))
    return bytes(raw)

class KhPartyTests(unittest.TestCase):
    def test_known_ability_flags_use_opposite_encodings(self):
        for game,fmt,value,choice in (('kh1','<B',0x8a,'Scan · Equipped'),('kh2','<H',0x8052,'Guard · Unequipped')):
            raw,record,start,end=kh_fixture(game);save=Save(raw,game)
            key='0:ability:0' if game=='kh1' else 'character:0:ability:0'
            f=next(f for f in save.slots[0].fields if f.key==key)
            output=save.patched({(0,key):f.choices.index(choice)})
            self.assertEqual(struct.unpack_from(fmt,output,f.offset)[0],0x0a if game=='kh1' else 0x52)
            self.assertFalse(Save(output,game).warnings)
            allowed=set(range(f.offset,f.offset+struct.calcsize(fmt)))|set(range(end,end+4))
            if game=='kh2':allowed.update(range(record+8,record+12))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))

    def test_unknown_abilities_are_readonly_and_preserved(self):
        for game in ('kh1','kh2'):
            raw,*_=kh_fixture(game);save=Save(raw,game)
            key='0:ability:2' if game=='kh1' else 'character:0:ability:2'
            f=next(f for f in save.slots[0].fields if f.key==key);self.assertTrue(f.readonly)
            with self.assertRaises(ValueError):save.patched({(0,key):0})
            self.assertEqual(save.patched({}),raw)

    def test_one_empty_ability_entry_and_existing_duplicates_are_kept(self):
        for game in ('kh1','kh2'):
            raw,*_=kh_fixture(game);save=Save(raw,game)
            prefix='0:ability:' if game=='kh1' else 'character:0:ability:'
            fields=[f for f in save.slots[0].fields if f.key.startswith(prefix)]
            self.assertEqual(len(fields),4)
            empty=next(f for f in fields if f.key.endswith(':3'))
            choice=next(i for i,n in enumerate(empty.choices) if n=='Scan · Unequipped')
            output=save.patched({(0,empty.key):choice})
            new=Save(output,game)
            self.assertEqual(len([f for f in new.slots[0].fields if f.key.startswith(prefix)]),5)

    def test_companions_are_selected_inside_categories_without_unlocking_absent_characters(self):
        for game,present,absent in (('kh1','Tarzan','Ariel'),('kh2','Riku','Mulan')):
            raw,*_=kh_fixture(game);save=Save(raw,game)
            categories=organize_fields(game,save.slots[0].fields)
            chars=next(c for c in categories if c.name=='Characters')
            self.assertIn(present,{s.selection for s in chars.sections})
            self.assertNotIn(absent,{s.selection for s in chars.sections})
            self.assertLessEqual(len(categories),3)
            self.assertEqual(sum(len(s.fields) for c in categories for s in c.sections),len(save.slots[0].fields))

    def test_weapon_types_and_equipment_array_bounds_are_preserved(self):
        for game in ('kh1','kh2'):
            raw,record,*_=kh_fixture(game);save=Save(raw,game)
            key='1:weapon' if game=='kh1' else 'character:1:weapon'
            f=next(f for f in save.slots[0].fields if f.key==key)
            self.assertFalse(any('Kingdom Key' in s for s in f.choices))
            equip=[f for f in save.slots[0].fields if f.key.startswith('0:accessory:' if game=='kh1' else 'character:0:armor:')]
            self.assertEqual(len(equip),2 if game=='kh1' else 1)
            self.assertEqual(save.patched({}),raw)

class EldenExpansionTests(unittest.TestCase):
    def test_ng_cycle_changes_only_its_word_and_selected_character_checksum(self):
        raw=elden_ready();save=Save(raw,'eldenring');field=next(f for f in save.slots[0].fields if f.key=='ng_cycle')
        output=save.patched({(0,'ng_cycle'):7});c=save.elden_ring.characters[0]
        allowed=set(range(field.offset,field.offset+4))|set(range(c.start-16,c.start))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertEqual(output[GLOBAL_START:],raw[GLOBAL_START:])
        for value in (-1,8):
            with self.assertRaises(ValueError):save.patched({(0,'ng_cycle'):value})

    def test_equipped_upgrade_updates_all_mirrors_registry_hash_and_highest_level(self):
        raw=elden_ready(True);save=Save(raw,'eldenring');c=save.elden_ring.characters[0]
        key='weapon:80000001';output=save.patched({(0,key):25})
        ids=c.player+0x2f4;arm=c.held+16+(2688+384)*12+116+140+24+4+3*8
        for offset in (c.start+36,ids,arm,c.profile+466):self.assertEqual(struct.unpack_from('<I',output,offset)[0],1000025)
        self.assertEqual(output[c.player+0xda],25)
        self.assertEqual(struct.unpack_from('<2I',output,c.registry+8),(1000025,1))
        self.assertEqual(output[c.start+48:c.start+53],raw[c.start+48:c.start+53]) # Ash handle + trailer.
        self.assertFalse(Save(output,'eldenring').warnings)
        changed=[i for i,(a,b) in enumerate(zip(raw,output)) if a!=b]
        allowed=set(range(c.start-16,c.start))|set(range(GLOBAL_START,GLOBAL_START+16))
        for off,length in ((c.start+36,4),(ids,4),(arm,4),(c.profile+466,4),(c.fingerprints+28,4),(c.player+0xda,1),(c.registry,16)):
            allowed.update(range(off,off+length))
        self.assertTrue(set(changed)<=allowed)
        downgraded=Save(output,'eldenring').patched({(0,key):1})
        self.assertEqual(downgraded[c.player+0xda],25)

    def test_unverified_equipped_mirror_is_readonly(self):
        raw=bytearray(elden_ready(True));c=Save(raw,'eldenring').elden_ring.characters[0]
        struct.pack_into('<I',raw,c.profile+466,0)
        save=Save(raw,'eldenring');f=next(f for f in save.slots[0].fields if f.key=='weapon:80000001')
        self.assertTrue(f.readonly)
        with self.assertRaises(ValueError):save.patched({(0,f.key):1},repair_crc=True)

    def test_goods_creation_updates_native_counters_and_registry_without_touching_other_slots(self):
        raw=elden_ready();save=Save(raw,'eldenring');c=save.elden_ring.characters[0]
        f=next(f for f in save.slots[0].fields if f.key=='add_goods:190') # Rune Arc, held limit 99.
        amount=min(5,f.maximum);output=save.patched({(0,f.key):amount})
        self.assertEqual(struct.unpack_from('<3I',output,c.held+52),(0xb00000be,amount,969))
        counters=c.held+8+(2688+384)*12
        self.assertEqual(struct.unpack_from('<2I',output,counters),(434,970))
        self.assertEqual(struct.unpack_from('<I',output,c.held)[0],5)
        self.assertEqual(Save(output,'eldenring').elden_ring.added_amount(0,f.key),amount)
        self.assertEqual(output[0x300+BLOCK_SIZE:],raw[0x300+BLOCK_SIZE:])
        self.assertEqual(output[c.registry+8:c.registry+16],struct.pack('<2I',0x400000be,1))
        self.assertFalse(Save(output,'eldenring').warnings)
        self.assertEqual(save.patched({(0,f.key):0}),raw)
        with self.assertRaises(ValueError):save.patched({(0,f.key):f.maximum+1})

    def test_registry_insertion_preserves_legacy_prefix_aow_flags_and_inactive_tail(self):
        raw=bytearray(160);struct.pack_into('<Q',raw,0,5)
        entries=((9,17),(2,21),(4,1),(0x80000003,7),(0x80000005,8))
        for i,entry in enumerate(entries):struct.pack_into('<2I',raw,8+i*8,*entry)
        raw[56:]=b'X'*104;before=bytes(raw)
        register_item(raw,0,3)
        actual=tuple(struct.unpack_from('<2I',raw,8+i*8) for i in range(6))
        self.assertEqual(actual,(entries[0],entries[1],(3,1),*entries[2:]))
        self.assertEqual(raw[56:],before[56:])
        original=bytes(raw);register_item(raw,0,3);self.assertEqual(bytes(raw),original)
        struct.pack_into('<I',raw,0,7000)
        with self.assertRaises(ValueError):register_item(raw,0,10)

    def test_empty_existing_stack_is_reused_without_advancing_inventory_counters(self):
        raw=elden_ready();save=Save(raw,'eldenring');c=save.elden_ring.characters[0]
        key='add_goods:10100' # Depleted Neutralizing Boluses record in the base fixture.
        f=next(f for f in save.slots[0].fields if f.key==key)
        output=save.patched({(0,key):1})
        self.assertEqual(struct.unpack_from('<3I',output,c.held+16),(0xb0002774,1,78))
        counters=c.held+8+(2688+384)*12
        self.assertEqual(output[counters:counters+8],raw[counters:counters+8])
        self.assertEqual(output[c.held:c.held+4],raw[c.held:c.held+4])

class Re4ExpansionTests(unittest.TestCase):
    def test_quantity_and_three_upgrade_nibbles_preserve_case_geometry_flags_and_all_other_slots(self):
        raw=re4_ready();save=Save(raw,'re4_2005');base=0x1ee8
        output=save.patched({(0,'weapon:0:0'):7,(0,'weapon:0:1'):3,(0,'weapon:0:2'):3,(0,'case:1'):50})
        self.assertEqual(struct.unpack_from('<H',output,base+0x373e)[0],0x2226)
        self.assertEqual(output[base+0x3740:base+0x3748],raw[base+0x3740:base+0x3748])
        self.assertEqual(output[base+0x3754:base+0x3760],raw[base+0x3754:base+0x3760])
        allowed=set(range(base,base+4))|set(range(base+0xcaf8,base+0xcafc))|set(range(base+0x373e,base+0x3740))|set(range(base+0x374a,base+0x374c))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertFalse(Save(output,'re4_2005').warnings)

    def test_capacity_cannot_reduce_and_loaded_ammo_is_not_overwritten(self):
        raw=re4_ready();save=Save(raw,'re4_2005')
        with self.assertRaises(ValueError):save.patched({(0,'weapon:0:3'):2})
        with self.assertRaises(ValueError):save.patched({(0,'weapon:0:loaded'):10})
        output=save.patched({(0,'weapon:0:3'):6})
        self.assertEqual(output[0x1ee8+0x3740:0x1ee8+0x3748],raw[0x1ee8+0x3740:0x1ee8+0x3748])
        self.assertEqual([c.name for c in organize_fields('re4_2005',save.slots[0].fields)],['Progress','Characters','Collection'])

    def test_unknown_id_or_tuneup_and_zero_quantity_are_never_given_a_writable_identity(self):
        raw=bytearray(re4_ready());struct.pack_into('<H',raw,0x1ee8+0x373e,0xffff)
        save=Save(raw,'re4_2005')
        self.assertTrue(all(f.readonly for f in save.slots[0].fields if f.key.startswith('weapon:0:')))
        with self.assertRaises(ValueError):save.patched({(0,'case:1'):0},repair_crc=True)
        with self.assertRaises(ValueError):save.patched({(0,'case:2'):1},repair_crc=True)

class Re6SkillTests(unittest.TestCase):
    def test_equipped_skill_reparses_and_preserves_unlocks_identity_and_other_sets(self):
        raw=re6_fixture();save=Save(raw,'re6')
        key='skill:Campaign skills:1'
        f=next(f for f in save.slots[0].fields if f.key==key)
        selected=f.choices.index('Firearm · Level 3')
        output=save.patched({(0,key):selected})
        self.assertEqual(struct.unpack_from('<I',output,1924)[0],3)
        allowed=set(range(8,12))|set(range(1924,1928))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertFalse(Save(output,'re6').warnings)

    def test_unknown_mode_skill_is_preserved_without_exposing_a_free_numeric_identity(self):
        from re6_save import checksum
        raw=bytearray(re6_fixture());struct.pack_into('<I',raw,2344,999999)
        struct.pack_into('<I',raw,8,checksum(raw));save=Save(raw,'re6')
        f=next(f for f in save.slots[0].fields if f.key=='skill:Mercenaries skills:0')
        self.assertIn('999999',f.choices[f.value]);self.assertEqual(save.patched({}),bytes(raw))
        with self.assertRaises(ValueError):save.patched({(0,f.key):999999})

if __name__=='__main__':unittest.main()

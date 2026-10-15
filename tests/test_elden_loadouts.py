"""Native equipment copies, references, fingerprints and preservation."""
import hashlib,struct,unittest
from core import Save
from elden_ring import player_hash,number,GLOBAL_START
from elden_loadouts import fingerprint
from test_elden_equipment_creation import ready,ARMOR_ID


def fixture(source=None):
    raw=bytearray(ready() if source is None else source);s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
    arm=s.elden_ring.equipment_loadouts[0].armaments
    entries=[struct.unpack_from('<3I',raw,c.held+4+n*12) for n in range(2688)]
    armor_row=next(i for i,v in enumerate(entries) if v==(0,0,0))
    struct.pack_into('<I',raw,c.held,1+sum(h not in (0,0xffffffff) for h,q,a in entries))
    struct.pack_into('<3I',raw,c.held+4+armor_row*12,0x90800002,1,971)
    for n,row,h,item in ((0,3,0x80800001,1000000),(12,armor_row,0x90800002,ARMOR_ID)):
        for at,value in ((c.player+0x280+n*4,0x180+row),(c.player+0x2f4+n*4,item&0x0fffffff),
                         (c.player+0x34c+n*4,h),(arm+n*4,item)):
            struct.pack_into('<I',raw,at,value)
    for indices,offset in (((0,2,4,1,3,5,6,8,7,9),28),((12,13,14,15,17,18,19,20,21),32)):
        struct.pack_into('<I',raw,c.fingerprints+offset,fingerprint(raw,c.player+0x2f4,indices))
    for start,length in s.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return Save(raw,'eldenring').patched({(0,'create_weapon:2000000'):1,(0,'create_armor:'+str(ARMOR_ID)):1})


class LoadoutTests(unittest.TestCase):
    def test_weapon_and_armor_switch_four_native_representations_without_changing_ownership(self):
        raw=fixture();s=Save(raw,'eldenring');c=s.elden_ring.characters[0];l=s.elden_ring.equipment_loadouts[0]
        changes={}
        for key in ('equipment_slot:0','equipment_slot:12'):
            changes[0,key]=next(i for i,h in enumerate(l.options[key]) if h!=l.current[int(key.split(':')[1])])
        out=s.patched(changes);check=Save(out,'eldenring');d=check.elden_ring.equipment_loadouts[0]
        for (_,key),choice in changes.items():
            slot=int(key.split(':')[1]);h=l.options[key][choice];row,item,*_=l.owned[h]
            self.assertFalse(d.reasons[slot]);self.assertEqual(d.current[slot],h)
            self.assertEqual(number(out,c.player+0x280+slot*4),row+0x180)
            self.assertEqual(number(out,c.player+0x2f4+slot*4),item&0x0fffffff)
            self.assertEqual(number(out,l.armaments+slot*4),item)
        self.assertEqual(out[c.held:c.held+16+(2688+384)*12],raw[c.held:c.held+16+(2688+384)*12])
        self.assertEqual(out[c.start+32:c.player],raw[c.start+32:c.player])
        self.assertEqual(out[GLOBAL_START:],raw[GLOBAL_START:]);self.assertFalse(check.warnings)
        allowed=set(range(c.start-16,c.start))
        for slot in (0,12):
            for at in (c.player+0x280+slot*4,c.player+0x2f4+slot*4,c.player+0x34c+slot*4,l.armaments+slot*4):allowed.update(range(at,at+4))
        allowed.update(range(c.fingerprints+28,c.fingerprints+36))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))

    def test_duplicate_assignment_is_rejected_but_an_atomic_swap_is_allowed(self):
        raw=fixture();s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0]
        alternative=next(h for h,v in l.owned.items() if v[2]=='Weapons' and h!=l.current[0])
        c=l.c;raw=bytearray(raw);row,item,*_=l.owned[alternative]
        for at,v in ((c.player+0x284,row+0x180),(c.player+0x2f8,item),(c.player+0x350,alternative),(l.armaments+4,item)):
            struct.pack_into('<I',raw,at,v)
        struct.pack_into('<I',raw,c.fingerprints+28,fingerprint(raw,c.player+0x2f4,(0,2,4,1,3,5,6,8,7,9)))
        s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0]
        first=l.options['equipment_slot:0'].index(alternative)
        with self.assertRaisesRegex(ValueError,'same physical'):s.patched({(0,'equipment_slot:0'):first},repair_crc=True)
        second=l.options['equipment_slot:1'].index(l.current[0])
        out=s.patched({(0,'equipment_slot:0'):first,(0,'equipment_slot:1'):second},repair_crc=True)
        after=Save(out,'eldenring').elden_ring.equipment_loadouts[0]
        self.assertEqual((after.current[0],after.current[1]),(alternative,l.current[0]))

    def test_native_upgrades_and_assignment_can_be_combined_with_structural_creation(self):
        raw=fixture();s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0]
        upgrade=next(f for f in s.slots[0].fields if f.key=='weapon:80800001')
        self.assertFalse(upgrade.readonly)
        other=next(h for h,v in l.owned.items() if v[2]=='Weapons' and h!=l.current[0])
        choice=l.options['equipment_slot:0'].index(other)
        out=s.patched({(0,upgrade.key):3,(0,'equipment_slot:0'):choice,(0,'create_weapon:1000000'):1,(1,'runes'):800})
        check=Save(out,'eldenring');d=check.elden_ring.equipment_loadouts[0]
        self.assertEqual(d.current[0],other);self.assertFalse(d.reasons[0]);self.assertFalse(check.warnings)
        self.assertEqual(next(f.value for f in check.slots[0].fields if f.key==upgrade.key),3)

    def test_mismatched_references_and_fingerprints_cannot_be_overwritten(self):
        for kind in ('index','identity','dynamic','fingerprint'):
            raw=bytearray(fixture());s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0];c=l.c
            at={'index':c.player+0x280,'identity':c.player+0x2f4,'dynamic':l.armaments,'fingerprint':c.fingerprints+28}[kind]
            raw[at]^=1;s=Save(raw,'eldenring');field=next(f for f in s.slots[0].fields if f.key=='equipment_slot:0')
            self.assertTrue(field.readonly)
            with self.assertRaises(ValueError):s.patched({(0,field.key):0},repair_crc=True)
            self.assertEqual(bytes(s.raw),bytes(raw))

    def test_reparse_verifies_handles_when_upgrade_reorders_choice_labels(self):
        raw=fixture();s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0]
        choice=l.options['equipment_slot:0'].index(l.current[0])
        out=s.patched({(0,'equipment_slot:0'):choice,(0,'weapon:80800001'):25})
        after=Save(out,'eldenring').elden_ring.equipment_loadouts[0]
        self.assertTrue(l.verifies(after,'equipment_slot:0',choice))

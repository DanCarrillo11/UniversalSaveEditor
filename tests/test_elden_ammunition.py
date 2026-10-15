"""Ammunition ownership, native empty slots and equipment fingerprints."""
import hashlib,struct,unittest
from core import Save
from elden_loadouts import fingerprint
from elden_tool_tables import AMMUNITION
from test_elden_loadouts import fixture as equipment_fixture


def fixture():
    raw=bytearray(equipment_fixture());s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0];c=l.c
    h=next(h for h,v in l.owned.items() if v[2]=='Weapons' and h!=l.current[0])
    row=l.owned[h][0];item=next(i for i,v in AMMUNITION.items() if v[1]=='Arrows')
    p=c.start+32
    for _ in range(5120):
        handle=struct.unpack_from('<I',raw,p)[0]
        if handle==h:struct.pack_into('<I',raw,p+4,item);break
        p+=21 if handle>>28==8 else 16 if handle>>28==9 else 8
    struct.pack_into('<I',raw,c.held+8+row*12,35)
    for slot in (6,7,8,9):
        for at,value in ((c.player+0x280+slot*4,0xffffffff),(c.player+0x2f4+slot*4,0xffffffff),
                         (c.player+0x34c+slot*4,0),(l.armaments+slot*4,0xffffffff)):
            struct.pack_into('<I',raw,at,value)
    struct.pack_into('<I',raw,c.fingerprints+28,fingerprint(raw,c.player+0x2f4,(0,2,4,1,3,5,6,8,7,9)))
    for start,length in s.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw),h


class AmmunitionTests(unittest.TestCase):
    def test_owned_stack_can_be_equipped_and_cleared_without_modifying_inventory(self):
        raw,h=fixture();s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0]
        key='equipment_slot:6';choice=l.options[key].index(h)
        self.assertNotIn(h,l.options['equipment_slot:7']);self.assertNotIn(h,l.options['equipment_slot:0'])
        out=s.patched({(0,key):choice,(0,'weapon:80800001'):3});check=Save(out,'eldenring');after=check.elden_ring.equipment_loadouts[0]
        self.assertEqual(after.current[6],h);self.assertFalse(after.reasons[6]);self.assertFalse(check.warnings)
        c=l.c;self.assertEqual(out[c.held:c.held+32260],raw[c.held:c.held+32260])
        cleared=check.patched({(0,key):after.options[key].index(0)})
        d=Save(cleared,'eldenring').elden_ring.equipment_loadouts[0]
        self.assertEqual(d.current[6],0);self.assertFalse(d.reasons[6])
        for at in (c.player+0x280+24,c.player+0x2f4+24,l.armaments+24):
            self.assertEqual(struct.unpack_from('<I',cleared,at)[0],0xffffffff)

    def test_duplicate_stack_and_inconsistent_empty_representations_are_rejected(self):
        raw,h=fixture();s=Save(raw,'eldenring');l=s.elden_ring.equipment_loadouts[0]
        with self.assertRaisesRegex(ValueError,'same physical'):
            s.patched({(0,'equipment_slot:'+str(n)):l.options['equipment_slot:'+str(n)].index(h) for n in (6,8)})
        raw=bytearray(raw);raw[l.armaments+24]^=1;s=Save(raw,'eldenring')
        field=next(f for f in s.slots[0].fields if f.key=='equipment_slot:6')
        self.assertTrue(field.readonly)
        with self.assertRaises(ValueError):s.patched({(0,field.key):0},repair_crc=True)

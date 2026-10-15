"""Owned tools, two serialized quick-item references and native fingerprints."""
import hashlib,struct,unittest
from core import Save
from elden_ring import number,GLOBAL_START
from elden_tools import quick_hash
from test_elden_loadouts import fixture as equipment


def fixture(source=None):
    raw=bytearray(equipment() if source is None else source);s=Save(raw,'eldenring');c=s.elden_ring.characters[0]
    t=s.elden_ring.tool_loadouts[0];pair=t.spells+116
    rows=[struct.unpack_from('<3I',raw,c.held+4+n*12) for n in range(2688)]
    additions=(0xb00000fa,0xb00000be,0xb00003e9,0xb000041b)
    for h in additions:
        if any(a==h and q for a,q,m in rows):continue
        row=next(i for i,v in enumerate(rows) if v==(0,0,0));rows[row]=(h,1,1500+row)
        struct.pack_into('<3I',raw,c.held+4+row*12,*rows[row])
    struct.pack_into('<I',raw,c.held,sum(h not in (0,0xffffffff) for h,q,a in rows))
    for n in range(16):
        at=pair+(n*8 if n<10 else 84+(n-10)*8)
        struct.pack_into('<2I',raw,at,0,0xffffffff);struct.pack_into('<I',raw,t.armaments+88+n*4,0xffffffff)
    key_base=c.held+8+2688*12
    keys=[struct.unpack_from('<3I',raw,key_base+n*12) for n in range(384)]
    for h in (0xb0002afa,0xb0002af9):
        if any(a==h and q for a,q,m in keys):continue
        row=next(i for i,v in enumerate(keys) if v==(0,0,0));keys[row]=(h,1,1700+row)
        struct.pack_into('<3I',raw,key_base+row*12,*keys[row])
    struct.pack_into('<I',raw,c.held+4+2688*12,sum(h not in (0,0xffffffff) for h,q,a in keys))
    struct.pack_into('<2I',raw,t.armaments+156,0xffffffff,0xffffffff)
    struct.pack_into('<I',raw,c.fingerprints+36,quick_hash(raw,t.armaments))
    for start,length in s.elden_ring.blocks:raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw)


class ToolTests(unittest.TestCase):
    def test_quick_and_pouch_synchronize_pairs_ids_and_checked_hash_only(self):
        raw=fixture();s=Save(raw,'eldenring');t=s.elden_ring.tool_loadouts[0];c=t.c;changes={}
        for key in ('quick_slot:0','quick_slot:10'):changes[0,key]=t.options[key].index(0xb00000be)
        out=s.patched(changes);check=Save(out,'eldenring');other=check.elden_ring.tool_loadouts[0]
        for (_,key),value in changes.items():self.assertTrue(t.verifies(other,key,value))
        self.assertEqual(number(out,c.fingerprints+36),quick_hash(out,t.armaments))
        self.assertEqual(out[GLOBAL_START:],raw[GLOBAL_START:]);self.assertFalse(check.warnings)
        allowed=set(range(c.start-16,c.start))|set(range(c.fingerprints+36,c.fingerprints+40))
        for key in ('quick_slot:0','quick_slot:10'):
            pair,dynamic=t.positions[key];allowed.update(range(pair,pair+8));allowed.update(range(dynamic,dynamic+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
    def test_duplicate_group_rejected_and_single_item_can_be_in_quick_and_pouch(self):
        s=Save(fixture(),'eldenring');t=s.elden_ring.tool_loadouts[0]
        choice=t.options['quick_slot:0'].index(0xb00000be)
        with self.assertRaisesRegex(ValueError,'same quick-item'):s.patched({(0,'quick_slot:0'):choice,(0,'quick_slot:1'):choice})
        s.patched({(0,'quick_slot:0'):choice,(0,'quick_slot:10'):choice})
    def test_physick_requires_owned_tears_and_preserves_other_position_and_tail(self):
        raw=fixture();s=Save(raw,'eldenring');t=s.elden_ring.tool_loadouts[0]
        selected=t.options['physick_slot:0'].index(0x40002afa)
        out=s.patched({(0,'physick_slot:0'):selected});other=Save(out,'eldenring').elden_ring.tool_loadouts[0]
        self.assertTrue(t.verifies(other,'physick_slot:0',selected))
        self.assertEqual(out[t.armaments+160:t.armaments+168],raw[t.armaments+160:t.armaments+168])
        with self.assertRaisesRegex(ValueError,'same Crystal Tear'):
            s.patched({(0,'physick_slot:0'):selected,(0,'physick_slot:1'):selected})
    def test_hash_mismatch_and_unowned_or_mismatched_current_references_are_protected(self):
        for problem in ('hash','pair','flask'):
            raw=bytearray(fixture());s=Save(raw,'eldenring');t=s.elden_ring.tool_loadouts[0]
            if problem=='hash':raw[t.c.fingerprints+36]^=1
            elif problem=='pair':struct.pack_into('<I',raw,t.positions['quick_slot:0'][0]+4,0)
            else:
                row=t.tools[0xb00000fa][0];struct.pack_into('<I',raw,t.c.held+8+row*12,0)
            s=Save(raw,'eldenring');key='physick_slot:0' if problem=='flask' else 'quick_slot:0'
            self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key==key))
            with self.assertRaises(ValueError):s.patched({(0,key):0},repair_crc=True)
    def test_tool_changes_survive_equipment_growth_and_independent_character_changes(self):
        s=Save(fixture(),'eldenring');t=s.elden_ring.tool_loadouts[0];choice=t.options['quick_slot:0'].index(0xb00000be)
        out=s.patched({(0,'quick_slot:0'):choice,(0,'create_weapon:1000000'):1,(1,'runes'):1234})
        c=Save(out,'eldenring');self.assertTrue(t.verifies(c.elden_ring.tool_loadouts[0],'quick_slot:0',choice));self.assertFalse(c.warnings)

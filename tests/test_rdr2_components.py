"""Existing component identity, one-active-slot rules and related catalog flags."""
import unittest,struct
from core import Save
from rockstar_container import name_hash,u32
from test_rdr2_features import fixture
from test_rdr2_pso import rsav


class ComponentTests(unittest.TestCase):
    def save(self,**kwargs):return Save(fixture(components=True,unlocks=True,**kwargs),'rdr2')

    def test_owned_parts_change_only_equipped_bytes_and_restore_identically(self):
        for encrypted in (False,True):
            s=self.save(encrypted=encrypted);f=s.rockstar.rdr2
            key='component:0000000000000002:3d0d02db';field=next(x for x in s.slots[0].fields if x.key==key)
            self.assertEqual(field.choices,('Long','Short'));self.assertEqual(field.value,0)
            out=Save(s.patched({(0,key):1}),'rdr2');self.assertFalse(out.warnings)
            rows,current,options,extend=f.components.groups[key]
            self.assertEqual([out.rockstar.rdr2.raw[flag] for h,flag,at,guid in rows],[1,0])
            allowed={flag for h,flag,at,guid in rows}
            allowed.update(i for b,at in f.c.checks for i in range(at+12,at+16))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(f.raw,out.rockstar.rdr2.raw))))
            self.assertEqual(out.patched({(0,key):0}),s.raw)

    def test_new_finish_replaces_only_leaf_identity_and_synchronizes_catalog(self):
        s=self.save();f=s.rockstar.rdr2;key='component:0000000000000002:0f43dcc6'
        rows,current,options,extend=f.components.groups[key];self.assertTrue(extend)
        out=Save(s.patched({(0,key):1}),'rdr2');g=out.rockstar.rdr2
        self.assertEqual(u32(g.raw,current[2]),name_hash('COMPONENT_SHORTARM_FRAME_MATERIAL_2'))
        unlock=f'unlock:{options[1]:08x}:apply';at=f.unlocks.positions[unlock]
        self.assertEqual(g.raw[at],f.raw[at]|7)
        allowed=set(range(current[2],current[2]+4))|{at}
        allowed.update(i for b,at in f.c.checks for i in range(at+12,at+16))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(f.raw,g.raw))))
        self.assertEqual(len(g.active_items()),len(f.active_items()))
        self.assertEqual(next(x.value for x in out.slots[0].fields if x.key==key),1)

    def test_nested_finishes_survive_selecting_another_owned_grip(self):
        s=self.save();grip='component:0000000000000002:ebe563e3';tint='component:0000000000000035:7fe38573'
        out=Save(s.patched({(0,grip):1,(0,tint):1}),'rdr2')
        fields={f.key:f for f in out.slots[0].fields}
        self.assertEqual(fields[grip].value,1);self.assertEqual(fields[tint].value,1)
        self.assertFalse(out.warnings)

    def test_ambiguous_unknown_and_invalid_records_are_protected(self):
        barrel='component:0000000000000002:3d0d02db';material='component:0000000000000002:0f43dcc6'
        for kw in ({'component_duplicate':True},{'component_flags':True}):
            self.assertNotIn(barrel,self.save(**kw).rockstar.rdr2.components.groups)
        self.assertNotIn(material,self.save(component_quantity=True).rockstar.rdr2.components.groups)
        groups=self.save(component_cycle=True).rockstar.rdr2.components.groups
        self.assertNotIn('component:0000000000000035:7fe38573',groups)
        # No catalog mapping means no new-variant replacement; owned slots still work.
        s=Save(fixture(components=True),'rdr2')
        self.assertNotIn(material,s.rockstar.rdr2.components.groups)
        self.assertIn(barrel,s.rockstar.rdr2.components.groups)

    def test_component_edits_and_supply_acquisition_share_one_checked_output(self):
        s=Save(rsav(True,fixture(False,components=True,unlocks=True,supplies=True)),'rdr2')
        key='component:0000000000000002:0f43dcc6'
        addition=next(f for f in s.slots[0].fields if f.group=='Add supplies' and not f.readonly)
        after=Save(s.patched({(0,key):1,(0,addition.key):1}),'rdr2')
        self.assertFalse(after.warnings);self.assertEqual(len(after.rockstar.rdr2.active_items()),len(s.rockstar.rdr2.active_items())+1)
        values={f.key:f.value for f in after.slots[0].fields};self.assertEqual(values[key],1);self.assertEqual(values[addition.key],1)

    def test_noop_and_invalid_indices_preserve_inputs(self):
        s=self.save();key='component:0000000000000002:0f43dcc6';before=s.raw
        self.assertEqual(s.patched({(0,key):0}),before)
        for value in (-1,2,1.0,True):
            with self.assertRaises(ValueError):s.patched({(0,key):value})
        self.assertEqual(s.raw,before)

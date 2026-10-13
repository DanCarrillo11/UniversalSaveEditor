import struct
import unittest
from core import Save
from test_core import variant, kingdom

class ExtendedTests(unittest.TestCase):
    def fixture(self):
        payload=variant({'inventory':[{'id':'fish_salmon','quality':1,'size':1.0,'ref':73}],
            'money':100.0,'bait_inv':{'worms':8},'bait_unlocked':['','worms'],'max_bait':10,'level':2,'xp':3.0,
            'rod_power':0,'journal':{'lake':{'salmon':{'count':1,'record':1.0}}}})
        return struct.pack('<I',len(payload))+payload

    def test_extended_fields_preserve_every_other_byte(self):
        raw=self.fixture();save=Save(raw,'webfishing')
        changes={(0,'xp'):123.1,(0,'level'):30,(0,'rod_power'):5,
            (0,'item_ref:73:size'):42.3,(0,'item_ref:73:quality'):5,(0,'journal:lake:salmon:count'):88}
        output=save.patched(changes)
        allowed=set()
        for field in save.slots[0].fields:
            if (0,field.key) in changes:allowed.update(range(field.offset,field.offset+struct.calcsize(field.fmt)))
        self.assertEqual(len(raw),len(output))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertEqual(Save(output,'webfishing').info['inventory'][0]['ref'],73)

    def test_invalid_decimals_and_capacity(self):
        save=Save(self.fixture(),'webfishing')
        for changes in ({(0,'xp'):float('nan')},{(0,'xp'):float('inf')},
                        {(0,'item_ref:73:quality'):6},{(0,'max_bait'):7},{(0,'level'):51}):
            with self.assertRaises(ValueError):save.patched(changes)

    def test_named_inventory_across_slots(self):
        raw=kingdom();save=Save(raw,'kh1')
        potion=next(f for f in save.slots[1].fields if f.key=='inventory:1')
        self.assertEqual(potion.label,'Potion')
        output=save.patched({(1,'inventory:1'):99})
        self.assertEqual(output[potion.offset],99)
        self.assertEqual(next(f.value for f in Save(output,'kh1').slots[0].fields if f.key=='inventory:1'),0)
        allowed={potion.offset}|set(range(save.crc_regions[0][1],save.crc_regions[0][1]+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        with self.assertRaises(ValueError):save.patched({(1,'inventory:1'):100})

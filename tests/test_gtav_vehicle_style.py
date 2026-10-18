import struct
import unittest
from core import Save
from rockstar_container import u32,name_hash
from test_gtav_features import fixture


def add_style(add,blocks,vehicle,size,default_kit,shared=False):
    modern=size==112
    shift=2 if modern else 0
    pair_index=len(blocks)+2
    vehicle[:8]=b'\x01'+bytes(7)
    struct.pack_into('>IIHH',vehicle,8,pair_index,0x24681357,5,5)
    vehicle[26]=255 if default_kit else 38
    vehicle[27:31]=bytes([4,4,111,156])
    fields=[(2393392848,2,0,26,0),(339378721,2,0,27,0),(2286316087,2,0,28,0),
            (2129614729,2,0,29,0),(1809854827,2,0,30,0)]
    for h,off in ((3809562301,31),(4163041496,32),(2428283409,33),
                  (1346029982,34),(2890957252,35),(117552945,36),
                  (1097807168,37),(3806865411,38),(2733182056,39)):
        fields.append((h,2,0,off+shift,0))
    fields.append((3207858859,16,1,0,917519 if modern else 786445))
    add(2181085963,b'',48 if modern else 40,fields)
    names=sorted(('VMT_ENGINE','VMT_BRAKES','VMT_GEARBOX','VMT_SUSPENSION','VMT_ARMOUR'),key=name_hash)
    nodes=b''.join(struct.pack('>IB3s',name_hash(name),255,b'xyz') for name in names)
    add(0x102,nodes,8,[(1620616462,11,7,0,0),(104834034,2,0,4,0)])
    if shared:
        index=next(i for i,(h,payload) in enumerate(blocks) if h==2541711729)
        blocks[index]=(2541711729,vehicle+vehicle)


def fields(save):return {f.key:f for f in save.slots[0].fields}


class VehicleStyleTests(unittest.TestCase):
    def test_known_layouts_colors_performance_exact_spans_and_restoration(self):
        for size in (96,112):
            for encrypted in (False,True):
                raw=fixture(encrypted,vehicle_size=size,styles=True)
                save=Save(raw,'gtav');fs=fields(save)
                self.assertEqual(fs['vehicle:0:0:model_name'].value,'Voltic')
                self.assertTrue(fs['vehicle:0:0:model_name'].readonly)
                self.assertNotIn('vehicle:0:0:mod_13',fs) # Electric Voltic has no gearbox stages.
                self.assertEqual(len(fs['vehicle:0:0:primary'].choices),161)
                editable=[f for f in fs.values() if f.group in ('Vehicle appearance','Vehicle performance')]
                changes={(0,f.key):(f.value+1)%(f.maximum+1) for f in editable}
                out=Save(save.patched(changes),'gtav')
                self.assertFalse(out.warnings)
                self.assertEqual(out.patched({(0,f.key):f.value for f in editable}),raw)
                allowed=set()
                for f in editable:allowed.add(f.offset)
                for _,at in save.rockstar.container.checks:allowed.update(range(at+12,at+16))
                before=save.rockstar.container.plain;after=out.rockstar.container.plain
                self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))

    def test_default_kit_initializes_only_when_applying_a_real_upgrade(self):
        raw=fixture(styles=True,default_kit=True);save=Save(raw,'gtav');fs=fields(save)
        key='vehicle:0:0:mod_11';at=fs[key].offset
        kit_at=save.rockstar.gtav.vehicles.styles.modifications[key][1]
        self.assertEqual(save.rockstar.container.plain[kit_at],255)
        self.assertEqual(save.patched({(0,key):0}),raw)
        out=Save(save.patched({(0,key):4}),'gtav')
        self.assertEqual(out.rockstar.container.plain[at],3)
        self.assertEqual(out.rockstar.container.plain[kit_at],0)
        self.assertEqual(out.rockstar.container.plain[at+1:at+4],b'xyz')

    def test_broken_map_duplicate_keys_and_unknown_kits_do_not_guess_upgrades(self):
        original=Save(fixture(styles=True),'gtav')
        frame=original.rockstar.container.frames[0]
        vehicle_at=next(b for h,b,n in frame.blocks if h==2541711729)
        pair_at=next(b for h,b,n in frame.blocks if h==0x102)
        for address,fmt,value in ((vehicle_at+8,'>I',4095),(vehicle_at+26,'>B',254),(pair_at,'>I',0xffffffff),(vehicle_at,'>B',2),
                                  (pair_at+8,'>I',u32(original.rockstar.container.plain,pair_at))):
            raw=bytearray(original.rockstar.container.plain);struct.pack_into(fmt,raw,address,value)
            damaged=Save(original.rockstar.container.encode(raw),'gtav')
            self.assertFalse(any(f.group=='Vehicle performance' for f in damaged.slots[0].fields))
            self.assertIn('vehicle:0:0:primary',fields(damaged))
        shared=Save(fixture(styles=True,shared_modmap=True),'gtav')
        self.assertFalse(any(f.group=='Vehicle performance' for f in shared.slots[0].fields))
        self.assertIn('vehicle:0:0:primary',fields(shared))

    def test_paint_and_tint_bounds_and_unknown_palette_values_are_preserved(self):
        save=Save(fixture(styles=True),'gtav')
        for key,value in (('primary',161),('window_tint',7),('smoke_r',256),('mod_11',5)):
            with self.assertRaises(ValueError):save.patched({(0,'vehicle:0:0:'+key):value})
        fs=fields(save);raw=bytearray(save.rockstar.container.plain)
        raw[fs['vehicle:0:0:window_tint'].offset]=255
        damaged=Save(save.rockstar.container.encode(raw),'gtav')
        self.assertNotIn('vehicle:0:0:window_tint',fields(damaged))

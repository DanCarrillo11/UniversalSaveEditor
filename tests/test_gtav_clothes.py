"""Wardrobe dependencies, independent actor snapshots and active map invariants."""
import struct
import unittest
from core import Save
from rockstar_container import name_hash,u32
from gtav_clothes import catalog,COMPONENTS,DRAW_PAIR,TEX_PAIR,DRAW_VALUE
from test_gtav_features import fixture
from test_gtav_weapons import script_blocks as weapon_script,fields,mutate


def script_blocks(stride=24):
    rows=list(weapon_script(stride))
    root=rows[0][1]
    main=131080
    bank=8
    root[bank]=3
    for c in range(3):
        for b in range(41):
            at=bank+8+c*1312+b*32
            root[at:at+8]=b'\x03header!'
            for state in range(3):root[at+12+state*8:at+16+state*8]=b'keep'
        at=main+8+c*520
        for delta,count in ((0,12),(104,12),(208,12),(312,9),(392,9)):
            root[at+delta:at+delta+8]=bytes([count])+b'opaque!'
            for n in range(count):root[at+delta+12+n*8:at+delta+16+n*8]=b'keep'
    root[main:main+8]=b'\x03header!'
    rows[0]=(rows[0][0],root,rows[0][2],rows[0][3]+[(101016013,12,0,bank,0x77714DDF)])
    rows[1]=(rows[1][0],rows[1][1],rows[1][2],rows[1][3]+[(274315432,12,0,0,0x77714E0B)])
    for h,(size,schema) in catalog()['schemas'].items():
        rows.append((h,b'',size,list(schema)))
    return rows


def active_maps(add,blocks,player):
    names=sorted(name_hash('PV_COMP_'+n) for n in COMPONENTS)
    for off,identity,stride,schema in ((144,0x100,12,DRAW_PAIR),(168,0x101,8,TEX_PAIR)):
        data=bytearray()
        for key in names:
            data+=struct.pack('>I',key)+(bytes(8) if stride==12 else b'\x00pad')
        struct.pack_into('>IIHH',player,off+8,len(blocks)+1,0x88776655,12,16)
        add(identity,data,stride,list(schema[1]))
    add(4029920929,b'',8,list(DRAW_VALUE[1]))


class ClothingTests(unittest.TestCase):
    def test_catalogue_versions_and_purchases_preserve_every_other_bit_and_cell(self):
        for stride,total in ((24,5733),(40,5664)):
            for encrypted in (False,True):
                original=fixture(encrypted,clothes=True,weapon_stride=stride)
                save=Save(original,'gtav');clothes=save.rockstar.gtav.clothes
                self.assertEqual(len(clothes.bits),total)
                self.assertEqual(save.patched({}),original)
                key=next(k for k,(at,bit) in clothes.bits.items() if bit==31 and k.endswith(':1'))
                at,bit=clothes.bits[key]
                save=mutate(save,lambda raw:struct.pack_into('>I',raw,at,0x12345678))
                before=save.rockstar.container.plain
                after=Save(save.patched({(0,key):1}),'gtav')
                self.assertEqual(u32(after.rockstar.container.plain,at),0x92345678)
                available=key[:-1]+'0';self.assertEqual(fields(after)[available].value,1)
                allowed=set(range(at,at+4))|set(range(fields(save)[available].offset,fields(save)[available].offset+4))
                for _,check in save.rockstar.container.checks:allowed.update(range(check+12,check+16))
                self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after.rockstar.container.plain))))
                self.assertEqual(len(after.raw),len(save.raw))
                with self.assertRaisesRegex(ValueError,'Conflicting'):save.patched({(0,key):1,(0,available):0})
                off=Save(after.patched({(0,available):0}),'gtav')
                self.assertEqual(fields(off)[key].value,0)
                seen=key[:-1]+'2'
                self.assertEqual(fields(Save(off.patched({(0,seen):1}),'gtav'))[seen].value,1)

    def test_equipped_clothes_sync_current_actor_and_acquire_without_changing_other_actors(self):
        for encrypted in (False,True):
            save=Save(fixture(encrypted,clothes=True),'gtav')
            clothes=save.rockstar.gtav.clothes
            self.assertTrue(clothes.outfits)
            key='clothes_worn:1:3';self.assertIn(key,clothes.outfits)
            field=fields(save)[key];choice=(field.value+1)%len(field.choices)
            draw_at,tex_at,active,options=clothes.outfits[key];self.assertIsNotNone(active)
            out=Save(save.patched({(0,key):choice}),'gtav')
            self.assertEqual(fields(out)[key].value,choice)
            raw=out.rockstar.container.plain
            self.assertEqual((u32(raw,draw_at),u32(raw,tex_at)),options[choice])
            self.assertEqual((u32(raw,active[0]),raw[active[1]]),options[choice])
            acquired=clothes.acquisition[key][choice]
            self.assertTrue(fields(out)[acquired+':0'].value)
            self.assertTrue(fields(out)[acquired+':1'].value)
            with self.assertRaisesRegex(ValueError,'Conflicting'):save.patched({(0,key):choice,(0,acquired+':1'):0})
            for other in clothes.outfits:
                if other!=key:self.assertEqual(fields(out)[other].value,fields(save)[other].value)
            original=save.rockstar.container.plain
            allowed=set(range(draw_at,draw_at+4))|set(range(tex_at,tex_at+4))|set(range(active[0],active[0]+4))|{active[1]}
            for suffix in (':0',':1'):
                at=fields(save)[acquired+suffix].offset;allowed.update(range(at,at+4))
            for _,check in save.rockstar.container.checks:allowed.update(range(check+12,check+16))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(original,raw))))
            self.assertEqual(save.patched({(0,key):field.value}),save.raw)

    def test_bad_bank_header_protects_wardrobe_but_leaves_unrelated_editors(self):
        save=Save(fixture(clothes=True,weapons=True),'gtav')
        at=fields(save)['clothes:0:3:0:0'].offset
        bad=mutate(save,lambda raw:raw.__setitem__(at-8,4))
        self.assertFalse(bad.rockstar.gtav.clothes.bits)
        self.assertFalse(bad.rockstar.gtav.clothes.outfits)
        self.assertTrue(any(k.startswith('weapon_') for k in fields(bad)))
        self.assertIn('world:hour',fields(bad))

    def test_active_map_mismatch_pointer_keys_and_resource_override_protect_only_affected_outfit(self):
        save=Save(fixture(clothes=True),'gtav')
        key='clothes_worn:1:3';other='clothes_worn:0:3'
        active=save.rockstar.gtav.clothes.outfits[key][2]
        player=next(at for h,at,n in save.rockstar.container.frames[0].blocks if h==2383497134)
        for change in (lambda raw:struct.pack_into('>I',raw,active[0],999),
                       lambda raw:struct.pack_into('>I',raw,active[0]-4,123),
                       lambda raw:struct.pack_into('>I',raw,player+152,4095),
                       lambda raw:struct.pack_into('>I',raw,active[0]-8,0)):
            bad=mutate(save,change)
            self.assertNotIn(key,fields(bad));self.assertIn(other,fields(bad))
            self.assertTrue(bad.rockstar.gtav.clothes.bits)
        unknown=mutate(save,lambda raw:struct.pack_into('>I',raw,player+32,name_hash('unknown')))
        self.assertFalse(unknown.rockstar.gtav.clothes.outfits)

    def test_navigation_keeps_clothing_with_its_character(self):
        from editor_layout import organize_fields
        save=Save(fixture(clothes=True),'gtav')
        equipment=next(c for c in organize_fields('gtav',save.slots[0].fields) if c.name=='Equipment')
        sections=[s for s in equipment.sections if any(f.key.startswith('clothes') for f in s.fields)]
        self.assertEqual({s.selection for s in sections},{'Michael','Franklin','Trevor'})
        self.assertTrue(all(s.name=='Current clothes' or s.name.startswith('Wardrobe · ') for s in sections))

    def test_overlapping_script_members_and_unknown_schema_do_not_become_writable(self):
        save=Save(fixture(clothes=True),'gtav')
        for old,new in ((struct.pack('>IBBHI',0x622852C8,12,128,8,0x77714E0A),
                         struct.pack('>IBBHI',0x622852C8,12,0,8,0x77714E0A)),
                        (struct.pack('>IBBHI',3740333462,5,0,8,0),
                         struct.pack('>IBBHI',3740333462,6,0,8,0))):
            raw=bytearray(save.rockstar.container.plain)
            at=raw.find(old);self.assertGreater(at,0)
            raw[at:at+len(old)]=new
            bad=Save(save.rockstar.container.encode(raw),'gtav')
            self.assertFalse(bad.rockstar.gtav.clothes.bits)
            self.assertFalse(bad.rockstar.gtav.clothes.outfits)
            self.assertIn('world:hour',fields(bad))

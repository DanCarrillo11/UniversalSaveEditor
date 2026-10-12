import struct
import unittest
from core import Field,Slot,Save
from editor_layout import organize_fields
from collection_tables import ELDEN_CATEGORIES,KH3_MATERIALS
from elden_items import GOODS
from inventory_context import InventoryContext
from re_engine_stream import Node
from re_hashes import murmur32
from test_elden_ring import fixture


class CollectionTests(unittest.TestCase):
    def test_verified_tables_cover_existing_goods_and_material_order(self):
        self.assertEqual(set(ELDEN_CATEGORIES),set(GOODS))
        self.assertEqual(len(KH3_MATERIALS),60)
        self.assertEqual(KH3_MATERIALS[:4],('Blazing Shard','Blazing Stone','Blazing Gem','Blazing Crystal'))
        self.assertEqual(KH3_MATERIALS[-1],'Illusory Crystal')

    def test_collection_groups_keep_location_and_every_field_without_new_writable_data(self):
        save=Save(fixture(),'eldenring');fields=save.slots[0].fields
        categories=organize_fields('eldenring',fields);collection=next(c for c in categories if c.name=='Collection')
        self.assertEqual([(s.name,s.selection) for s in collection.sections],[('Crafting materials','Inventory'),('Crafting materials','Storage')])
        self.assertCountEqual([f.key for c in categories for s in c.sections for f in s.fields],[f.key for f in fields])
        out=save.patched({(0,'inventory:0'):20})
        self.assertEqual(next(f.value for f in Save(out,'eldenring').slots[0].fields if f.key=='inventory:0'),20)

    def test_item_identity_requires_the_same_object_and_unambiguous_sibling(self):
        raw=struct.pack('<3i',10,20,30);owner=0x2675722d;parent=((0,123,0),(0x41f30892,1,0))
        quantity=Node(owner,murmur32(b'Count'),7,8,4,parent+((owner,2,4),),'<i')
        valid=Node(owner,murmur32(b'ItemId'),1,0,4,parent+((owner,3,0),),'<i')
        other=Node(owner,murmur32(b'ItemId'),1,4,4,((0,123,1),)+parent[1:]+((owner,3,0),),'<i')
        self.assertEqual(InventoryContext([valid,other],raw).item_id('re2',quantity),10)
        duplicate=Node(owner,murmur32(b'ItemId'),1,4,4,valid.path,'<i')
        self.assertIsNone(InventoryContext([valid,duplicate],raw).item_id('re2',quantity))
        self.assertIsNone(InventoryContext([other],raw).item_id('re2',quantity))

    def test_remake_identity_requires_the_verified_nested_item_property(self):
        parent=((0,123,0),(0xbedd9bf5,1,0));owner=0x004b7a76
        quantity=Node(owner,murmur32(b'CurrVirtualStackCount'),7,4,4,parent+((owner,2,1),),'<i')
        item=Node(0xa84686d9,murmur32(b'_ItemId'),1,0,4,parent+((owner,murmur32(b'Item'),0),(0xa84686d9,3,1)),'<i')
        self.assertEqual(InventoryContext([item],struct.pack('<2i',555,2)).item_id('re4_remake',quantity),555)
        self.assertIsNone(InventoryContext([item],struct.pack('<2i',-1,2)).item_id('re4_remake',quantity))

    def test_kh3_verified_material_names_keep_offsets_and_edited_values(self):
        from test_kh_extra import kh3_plain
        save=Save(kh3_plain(),'kh3');fields={f.key:f for f in save.slots[0].fields}
        self.assertEqual(fields['material:0'].label,'Blazing Shard')
        self.assertEqual(fields['material:59'].label,'Illusory Crystal')
        self.assertIn('Unidentified',fields['material:60'].label)
        self.assertEqual(fields['material:0'].offset,0x165e)
        out=save.patched({(0,'material:0'):321})
        self.assertEqual(next(f.value for f in Save(out,'kh3').slots[0].fields if f.key=='material:0'),321)

    def test_engine_display_names_never_make_identity_writable(self):
        from test_re_engine import wrap
        owner=0x2675722d;data=bytearray(32)
        # Exact player-inventory object, containing a read-only identity and quantity.
        data.extend(struct.pack('<3I',123,1,0x41f30892))
        data.extend(struct.pack('<Ii',murmur32(b'Items'),17))
        data.extend(struct.pack('<2I',2,owner))
        data.extend(struct.pack('<IiIi',murmur32(b'ItemId'),1,4,42))
        data.extend(struct.pack('<IiIi',murmur32(b'Count'),7,4,5))
        save=Save(wrap(bytes(data[32:]),'re2'),'re2')
        field=save.slots[0].fields[0]
        self.assertIn('ID 42',field.label);self.assertEqual(field.collection,'Unidentified items')
        out=save.patched({(0,field.key):99})
        updated=Save(out,'re2');self.assertEqual(updated.slots[0].fields[0].value,99)
        self.assertIn('ID 42',updated.slots[0].fields[0].label)
        self.assertEqual(len(updated.slots[0].fields),1)

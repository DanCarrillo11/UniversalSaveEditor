"""Native inventory capacity; no item layout or reward rewrites."""
import unittest
from core import Save
from remake_inventory_capacity import CONFIG
from re_engine_container import ReEngineEnvelope
from test_requiem import Writer
from test_re_engine import wrap, stream, ACCOUNT


def fixture(game,size=8,survivor=0,duplicate=False,nested=False):
    wrapper,manager,inventory=CONFIG[game]
    fields=[('_SurvivorType',1,('<i',survivor)),('_CurrentSlotSize',7,('<i',size)),
            ('UnknownLayout',16,('<16s',b'KEEP INVENTORY!!'))]
    if duplicate:fields.append(('_CurrentSlotSize',7,('<i',size)))
    section=(manager,[('DataLists',-1,[(inventory,fields)])])
    w=Writer();w.data=bytearray(32);w.data.extend(stream(game))
    if nested:section=(0x12345678,[('Template',17,section)])
    w.root(wrapper,[('GameSaveDataList',-1,[section])])
    return wrap(bytes(w.data[32:]),game)


class RemakeInventoryCapacityTests(unittest.TestCase):
    def test_increasing_native_capacity_preserves_all_item_and_unknown_data(self):
        for game in CONFIG:
            with self.subTest(game=game):
                s=Save(fixture(game),game,account_id=ACCOUNT)
                f=next(f for f in s.slots[0].fields if f.label=='Inventory capacity')
                self.assertEqual((f.value,f.minimum,f.maximum),(0,0,6))
                self.assertEqual(f.choices,tuple(f'{i} slots' for i in range(8,21,2)))
                out=s.patched({(0,f.key):6});check=Save(out,game,account_id=ACCOUNT)
                changed=next(value for value in check.slots[0].fields if value.key==f.key)
                self.assertEqual((changed.value,changed.minimum),(6,6));self.assertFalse(check.warnings)
                before=ReEngineEnvelope(s.raw,game,account_id=ACCOUNT).payload
                after=ReEngineEnvelope(out,game,account_id=ACCOUNT).payload
                offset=f.offset-32
                self.assertEqual(before[:offset],after[:offset]);self.assertEqual(before[offset+4:],after[offset+4:])
                self.assertEqual(after[offset:offset+4],b'\x14\0\0\0')
                with self.assertRaises(ValueError):check.patched({(0,f.key):5})
                self.assertEqual(s.patched({}),s.raw)

    def test_unsupported_survivors_capacities_duplicates_and_templates_are_protected(self):
        for game in CONFIG:
            for kw in ({'survivor':2},{'survivor':-1},{'size':7},{'size':9},{'size':22},{'duplicate':True},{'nested':True}):
                s=Save(fixture(game,**kw),game,account_id=ACCOUNT)
                self.assertFalse(any(f.label=='Inventory capacity' for f in s.slots[0].fields))
                self.assertEqual(s.patched({}),s.raw)


if __name__=='__main__':unittest.main()

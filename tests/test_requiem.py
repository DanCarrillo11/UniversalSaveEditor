"""Independent synthetic Requiem records; no private saves or SDK assets."""
import struct
import unittest
from core import Save
from re_engine_container import ReEngineEnvelope
from re_hashes import murmur32
from editor_layout import organize_fields
from test_re_engine import wrap, stream, ACCOUNT
from test_village import Writer as VillageWriter
from requiem_context import CHARACTERS, CHARACTER, PLAYER, HEALTH, MANAGER, INVENTORY, PANEL, CONTAINED


class Writer(VillageWriter):
    def __init__(self):self.data=bytearray(16)
    def clazz(self,owner,fields):
        self.pack('<2I',len(fields),owner)
        for name,kind,value in fields:
            self.pack('<Ii',murmur32(name.encode()),-1 if kind==-2 else kind)
            if kind==17:self.clazz(*value)
            elif kind==-1:
                self.align(4);self.pack('<iIIi',17,4,len(value),1)
                for child in value:self.clazz(*child)
            elif kind==-2:
                self.align(4);self.pack('<iIIi',7,4,len(value),0)
                for item in value:self.align(4);self.pack('<i',item)
            elif kind==15:
                self.align(4);encoded=value.encode('utf-16-le')
                self.pack('<I',len(encoded)//2);self.data.extend(encoded)
            else:
                fmt,item=value;size=struct.calcsize(fmt)
                self.align(4);self.pack('<I',size);self.align(size);self.pack(fmt,item)
            self.align(4)


def character(player=True, mismatch=False):
    structures=[(HEALTH,[('_IsSetuped',2,('<B',1)),('_CurrentHP',7,('<i',850)),
        ('_CurrentMaxHP',7,('<i',900)),('_CurrentHPLevel',7,('<i',0 if mismatch else 1)),
        ('_MaximumHPTable',-2,[800,900,1000]),('UnknownState',16,('<16s',b'KEEPPLAYERSTATE!'))])]
    if player:structures.append((PLAYER,[('_FearLevelRate',11,('<f',1.0))]))
    return CHARACTER,[('_StructureDatas',-1,structures)]


def panel(identifier=0x12345678, count=20, ambiguous=False):
    fields=[('_ItemIDHash',8,('<I',identifier)),('_Stock',7,('<i',count)),
        ('_Position',16,('<8s',b'GEOMETRY')),
        ('_LoadingItems',-1,[(CONTAINED,[('_ItemIDHash',8,('<I',0x22334455)),('_Stock',7,('<i',12)),('_ChamberStock',7,('<i',1))])]),
        ('_StorageItems',-1,[(CONTAINED,[('_ItemIDHash',8,('<I',0x33445566)),('_Stock',7,('<i',25)),('_ChamberStock',7,('<i',0))])])]
    if ambiguous:fields.append(('_ItemIDHash',8,('<I',0x99887766)))
    return PANEL,fields


def inventory(ambiguous=False,parts=False,bad_reference=False,equipment=False):
    fields=[('_UserName',15,'User01'),('_BoardTypeName',15,'Hand'),
        ('_PanelItems',-1,[panel(ambiguous=ambiguous),panel(0x11223344,1),panel(0,0)]),
        ('_ArchiveItems',-1,[(0x3b572458,[('_ItemIDHash',8,('<I',0x44556677)),('_Stock',7,('<i',50))])])]
    if parts:
        for code in ('it10_01_002','it30_00_101','it30_00_501'):
            fields[2][2].append((PANEL,[('_ItemIDHash',8,('<I',murmur32(code.encode('utf-16-le')))),('_Stock',7,('<i',1))]))
        attachments=[]
        for index,code in ((4,'it30_00_101'),(5,'it30_00_501')):
            attachments.append((0x1dbdde3d,[('_ItemIndex',7,('<i',index)),
                ('_AttachTargetItemIndex',7,('<i',99 if bad_reference else 3)),
                ('_ItemIDName',15,code),('_Level',7,('<i',1)),('_AttachTargetSocketName',15,'SocketG')]))
        fields.append(('_PanelAttachments',-1,attachments))
        if equipment:
            fields[2][2].append((PANEL,[('_ItemIDHash',8,('<I',murmur32('it10_00_000'.encode('utf-16-le')))),('_Stock',7,('<i',1))]))
            from test_requiem_equipment import reference
            from requiem_equipment import EQUIP, SHORTCUT
            fields.append(('_Equips',-1,[reference(EQUIP,'Primary',3,'it10_01_002')]))
            fields.append(('_Shortcuts',-1,[reference(SHORTCUT,'Equip_Up',6,'it10_00_000')]))
    return INVENTORY,fields


def fixture(ambiguous=False,mismatch=False,parts=False,bad_reference=False,equipment=False,difficulty=False):
    w=Writer();w.data.extend(stream('re9'))
    w.root(CHARACTERS,[('_CharacterSaves',-1,[character(False),character(mismatch=mismatch)])])
    w.root(MANAGER,[('_InventoryData',-1,[inventory(ambiguous,parts,bad_reference,equipment)]),('_BackupInventoryData',-1,[inventory(parts=True)])])
    w.root(*panel(0x77889900,99)) # misleading scene stock is not player inventory
    if difficulty:
        w.root(0xda736ae5,[('DifficultyIDValue',7,('<i',-1)),('DifficultyIDNameHash',8,('<I',3326958550))])
    return wrap(bytes(w.data[16:]),'re9')


class RequiemTests(unittest.TestCase):
    def save(self,raw=None):return Save(fixture() if raw is None else raw,'re9',account_id=ACCOUNT)

    def test_player_health_and_inventory_are_selected_by_exact_context(self):
        save=self.save();health=[f for f in save.slots[0].fields if f.group=='Player health']
        self.assertEqual([f.label for f in health],['Current health','Maximum health','Health upgrade level'])
        self.assertEqual({f.collection for f in health},{'Player record 1'})
        items=[f for f in save.slots[0].fields if f.group=='Inventory quantities']
        self.assertEqual(len(items),4) # valid panel/storage records only
        self.assertEqual(sum(not f.readonly for f in items),3)
        self.assertEqual({f.collection for f in items},{'Carried inventory · User01'})
        self.assertFalse(any(x in ' '.join(f.label for f in items) for x in ('22334455','44556677','77889900')))
        self.assertEqual([c.name for c in organize_fields('re9',save.slots[0].fields)],['Progress','Characters','Collection'])

    def test_upgrade_uses_own_table_and_clamps_health_without_changing_enemies(self):
        raw=fixture();save=self.save(raw);fields=save.slots[0].fields
        level=next(f for f in fields if f.label=='Health upgrade level')
        output=save.patched({(0,level.key):0});check=self.save(output)
        health={f.label:f.value for f in check.slots[0].fields if f.group=='Player health'}
        self.assertEqual(health,{'Current health':800,'Maximum health':800,'Health upgrade level':0})
        before=ReEngineEnvelope(raw,'re9',account_id=ACCOUNT).payload
        after=ReEngineEnvelope(output,'re9',account_id=ACCOUNT).payload
        allowed={i for f in fields if f.group=='Player health' for i in range(f.offset-16,f.offset-12)}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
        self.assertEqual(len(output),len(raw));self.assertFalse(check.warnings)
        self.assertEqual(save.patched({}),raw)

    def test_invalid_health_readonly_identity_and_ambiguous_records_are_preserved(self):
        save=self.save();fields=save.slots[0].fields
        hp=next(f for f in fields if f.label=='Current health')
        level=next(f for f in fields if f.label=='Health upgrade level')
        maximum=next(f for f in fields if f.label=='Maximum health')
        single=next(f for f in fields if f.group=='Inventory quantities' and f.readonly)
        for edits in ({(0,hp.key):901},{(0,level.key):3},{(0,level.key):0,(0,hp.key):850},
                      {(0,maximum.key):5000},{(0,single.key):5}):
            with self.assertRaises(ValueError):save.patched(edits)
        unmatched=self.save(fixture(mismatch=True))
        self.assertFalse(any(f.label=='Health upgrade level' for f in unmatched.slots[0].fields))
        ambiguous=self.save(fixture(ambiguous=True))
        self.assertFalse(any('12345678' in f.label for f in ambiguous.slots[0].fields))

    def test_stack_patch_changes_only_existing_stock_and_authenticates_output(self):
        raw=fixture();save=self.save(raw)
        item=next(f for f in save.slots[0].fields if f.group=='Inventory quantities' and not f.readonly)
        output=save.patched({(0,item.key):99});check=self.save(output)
        self.assertEqual(next(f.value for f in check.slots[0].fields if f.key==item.key),99)
        before=ReEngineEnvelope(raw,'re9',account_id=ACCOUNT).payload
        after=ReEngineEnvelope(output,'re9',account_id=ACCOUNT).payload
        self.assertEqual(before[:item.offset-16],after[:item.offset-16])
        self.assertEqual(before[item.offset-12:],after[item.offset-12:])
        self.assertFalse(check.warnings)

    def test_attached_upgrade_tiers_match_owned_part_and_weapon_references(self):
        raw=fixture(parts=True);save=self.save(raw)
        fields=[f for f in save.slots[0].fields if f.group=='Weapon upgrades']
        self.assertEqual([f.label for f in fields],['Silver Tube Extension','Chrome Barrel'])
        self.assertEqual({f.collection for f in fields},{'W870 Police · Item 4'})
        capacity,barrel=fields
        self.assertEqual(capacity.minimum,1);self.assertEqual(barrel.minimum,0)
        with self.assertRaises(ValueError):save.patched({(0,capacity.key):0})
        output=save.patched({(0,capacity.key):2,(0,barrel.key):0});check=self.save(output)
        tiers=[f.value for f in check.slots[0].fields if f.group=='Weapon upgrades']
        self.assertEqual(tiers,[2,0]);self.assertFalse(check.warnings)
        self.assertTrue(next(f for f in check.slots[0].fields if f.key==capacity.key).readonly)
        before=ReEngineEnvelope(raw,'re9',account_id=ACCOUNT).payload
        after=ReEngineEnvelope(output,'re9',account_id=ACCOUNT).payload
        allowed={i for f in fields for i in range(f.offset-16,f.offset-12)}
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
        invalid=self.save(fixture(parts=True,bad_reference=True))
        self.assertFalse(any(f.group=='Weapon upgrades' for f in invalid.slots[0].fields))

    def test_named_ammunition_can_increase_from_one_but_durability_is_not_quantity(self):
        w=Writer();items=[]
        for code,value in (('it40_00_000',1),('it40_20_001',20)):
            items.append((PANEL,[('_ItemIDHash',8,('<I',murmur32(code.encode('utf-16-le')))),('_Stock',7,('<i',value))]))
        w.root(MANAGER,[('_InventoryData',-1,[(INVENTORY,[('_UserName',15,'User00'),
            ('_BoardTypeName',15,'ItemBox'),('_PanelItems',-1,items)])])])
        raw=wrap(bytes(w.data[16:]),'re9');save=self.save(raw)
        self.assertEqual(len(save.slots[0].fields),1)
        ammo=save.slots[0].fields[0];self.assertIn('Handgun Ammo',ammo.label);self.assertFalse(ammo.readonly)
        output=save.patched({(0,ammo.key):50})
        self.assertEqual(self.save(output).slots[0].fields[0].value,50)

if __name__=='__main__':unittest.main()

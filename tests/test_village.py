"""Independent synthetic Village streams; no downloaded or personal saves."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from core import Save, FormatError, identify_game, discover, replace_current
from re_engine_container import ReEngineEnvelope, KEYS
from re_engine_stream import StreamReader
from re_hashes import murmur32
from editor_layout import organize_fields
from diagnostics import support_report
from test_re_engine import wrap

class Writer:
    def __init__(self):self.data=bytearray(32)
    def align(self,size):self.data.extend(bytes((-len(self.data))%size))
    def pack(self,fmt,*values):self.data.extend(struct.pack(fmt,*values))
    def clazz(self,owner,fields):
        self.pack('<2I',len(fields),owner)
        for name,kind,value in fields:
            self.pack('<Ii',murmur32(name.encode()),kind)
            if kind==17:self.clazz(*value)
            elif kind==-1:
                self.align(4);self.pack('<iIIi',17,4,len(value),1)
                for child in value:self.clazz(*child)
            elif kind==15:
                self.align(4);encoded=value.encode('utf-16-le')
                self.pack('<I',len(encoded)//2);self.data.extend(encoded)
            else:
                fmt,item=value;size=struct.calcsize(fmt)
                self.align(4);self.pack('<I',size);self.align(size);self.pack(fmt,item)
            self.align(4)
    def root(self,owner,fields):self.pack('<I',0x12345678);self.clazz(owner,fields)

def item(identifier=0xfedcba98,amount=20,duplicate=False,identity_kind=8):
    fields=[('ItemID',identity_kind,('<I' if identity_kind==8 else '<i',identifier)),
            ('StackSize',7,('<i',amount)),('SlotNo',7,('<i',7)),
            ('IncludeItemID',8,('<I',0x12345678)),('IncludeStackSize',7,('<i',10)),
            ('IsHorizontal',2,('<B',1)),('UnidentifiedData',16,('<16s',b'KEEPUNKNOWNSTATE'))]
    if duplicate:fields.append(('ItemID',8,('<I',0x76543210)))
    return 0x0431bf51,[('inventoryID',8,('<I',999)),('objectID',8,('<I',444)),
                        ('work',17,(0x10b5eaa5,fields))]

def content(identity=0xabcddcba):
    return 0xf033f1ce,[('Hash',8,('<I',identity)),('Has',2,('<B',0)),
        ('IsOpened',2,('<B',1)),('IsUnlocked',2,('<B',0)),
        ('IsNoDependDLC',2,('<B',0)),('IsNewByShop',2,('<B',1))]

def fixture(profile_only=False,gameplay_only=False,scene=True,ambiguous=False):
    w=Writer()
    if not profile_only:
        w.root(0x3a83076c,[('money',7,('<i',500)),('datas',-1,[item(duplicate=ambiguous),item(0x11223344,1),item(0x22334455,0)]),
            ('UnrelatedInventory',16,('<16s',b'KEEP INVENTORY!!'))])
        w.root(0x00346547,[('SaveHealth',11,('<f',850.5)),('SaveHealthPl2000',11,('<f',555)),
            ('SaveHealth1Custom',2,('<B',1)),('SaveRArmCut',2,('<B',0)),('SaveGuid',16,('<16s',b'KEEP PLAYER GUID'))])
        if scene:
            # Same item type in a shop/scene context must never become inventory.
            _,fields=item(0x99887766,50)
            w.root(0x21fc5004,fields)
    if not gameplay_only:
        w.root(0xe94db9b8,[('CP',7,('<i',1000)),('Units',-1,[content(),content(0xfedcba98)]),
            ('PrivateInfo',15,'PRIVATE_VILLAGE_ACCOUNT')])
        # A content-looking object outside CP.Units must remain untouched.
        w.root(*content(0x55667788))
    return wrap(bytes(w.data[32:]),'re8')

class VillageTests(unittest.TestCase):
    def test_envelope_key_autodetection_noop_and_cross_game_refusal(self):
        raw=fixture();save=Save(raw,'re8')
        self.assertEqual(save.patched({}),raw);self.assertFalse(save.warnings)
        self.assertEqual(KEYS['re8'],b'j1lL1AOR31sd4HKJS90fs')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'data001Slot.bin';path.write_bytes(raw)
            self.assertEqual(identify_game(path),'re8')
        for game in ('re2','re3','re7'):
            with self.assertRaises(FormatError):Save(raw,game)

    def test_profile_and_gameplay_show_only_present_options(self):
        profile=Save(fixture(profile_only=True),'re8')
        self.assertEqual({f.group for f in profile.slots[0].fields},{'Currency','Extra content'})
        game=Save(fixture(gameplay_only=True),'re8')
        self.assertEqual({f.group for f in game.slots[0].fields},{'Currency','Player health','Inventory quantities'})
        self.assertEqual([c.name for c in organize_fields('re8',Save(fixture(),'re8').slots[0].fields)],['Progress','Character','Collection'])

    def test_currency_health_stacks_and_content_patch_only_authorized_plaintext_bytes(self):
        raw=fixture();save=Save(raw,'re8');fields=save.slots[0].fields
        edits={(0,f.key):(1-f.value if f.boolean else 123.25 if f.decimal else 123) for f in fields if not f.readonly}
        output=save.patched(edits);parsed=Save(output,'re8');self.assertFalse(parsed.warnings)
        before=ReEngineEnvelope(raw,'re8').payload;after=ReEngineEnvelope(output,'re8').payload
        allowed=set()
        for f in fields:
            if (0,f.key) in edits:allowed.update(range(f.offset-32,f.offset-32+struct.calcsize(f.fmt)))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
        self.assertEqual(output[:32],raw[:32]);self.assertEqual(len(output),len(raw))
        self.assertIn(b'KEEPUNKNOWNSTATE',after)
        self.assertTrue(any('FEDCBA98' in f.label for f in fields))

    def test_context_excludes_scene_stock_ambiguous_ids_and_zero_stacks(self):
        save=Save(fixture(),'re8');quantities=[f for f in save.slots[0].fields if f.group=='Inventory quantities']
        self.assertEqual(len(quantities),2)
        self.assertEqual(sum(f.readonly for f in quantities),1)
        self.assertNotIn('99887766',' '.join(f.label for f in quantities))
        ambiguous=Save(fixture(ambiguous=True),'re8')
        self.assertEqual(len([f for f in ambiguous.slots[0].fields if f.group=='Inventory quantities']),1)
        self.assertEqual(len([f for f in save.slots[0].fields if f.group=='Extra content']),6)
        self.assertNotIn('55667788',' '.join(f.label for f in save.slots[0].fields))

    def test_single_objects_are_readonly_loaded_rounds_and_dlc_flags_preserved(self):
        raw=fixture();save=Save(raw,'re8')
        single=next(f for f in save.slots[0].fields if f.readonly)
        with self.assertRaises(ValueError):save.patched({(0,single.key):2})
        labels=' '.join(f.label for f in save.slots[0].fields)
        for hidden in ('IncludeStackSize','NoDependDLC','NewByShop','SaveHealthPl2000','RArmCut'):self.assertNotIn(hidden,labels)
        before=StreamReader(bytes(32)+ReEngineEnvelope(raw,'re8').payload,32).parse()
        edits={(0,f.key):1 for f in save.slots[0].fields if f.group=='Extra content'}
        result=save.patched(edits);clear=bytes(32)+ReEngineEnvelope(result,'re8').payload
        original=bytes(32)+ReEngineEnvelope(raw,'re8').payload
        keep={murmur32(p.encode()) for p in ('IncludeStackSize','IsNoDependDLC','IsNewByShop','ItemID','SaveGuid')}
        for node in before:
            if node.field in keep:self.assertEqual(clear[node.offset:node.offset+node.size],original[node.offset:node.offset+node.size])

    def test_invalid_types_values_integrity_and_direct_saving_without_backup(self):
        raw=fixture();save=Save(raw,'re8')
        money=next(f for f in save.slots[0].fields if f.label=='Lei')
        for value in (-1,100000000,1.5):
            with self.assertRaises(ValueError):save.patched({(0,money.key):value})
        damaged=bytearray(raw);damaged[-1]^=1
        with self.assertRaises(ValueError):Save(damaged,'re8').patched({(0,money.key):1})
        self.assertEqual(Save(damaged,'re8').patched({},True),raw)
        for data in (raw[:30],raw[:-5],bytes(len(raw))):
            with self.assertRaises(ValueError):Save(data,'re8')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'data001Slot.bin';path.write_bytes(raw)
            output=save.patched({(0,money.key):999});replace_current(path,raw,output)
            self.assertEqual(list(path.parent.iterdir()),[path]);self.assertEqual(path.read_bytes(),output)

    def test_discovery_and_diagnostics_preserve_privacy(self):
        raw=fixture()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'Steam/userdata/123/1196590/remote/win64_save/data001Slot.bin'
            path.parent.mkdir(parents=True);path.write_bytes(raw)
            with patch.dict('os.environ',{'PROGRAMFILES(X86)':str(root),'PROGRAMFILES':str(root),'APPDATA':str(root)}),patch('core.documents_folder',return_value=root/'Documents'):
                self.assertIn(('re8',path),discover())
            report=support_report('re8',Save(raw,'re8'),suffix='.bin',size=len(raw))
            self.assertNotIn(str(path),report);self.assertNotIn('PRIVATE_VILLAGE_ACCOUNT',report)
            self.assertNotIn('FEDCBA98',report)

if __name__=='__main__':unittest.main()

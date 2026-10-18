"""Synthetic PSO graphs and rejection cases, with no distributed game saves."""
from collections import Counter
import struct,unittest
from core import Save
from rockstar_container import aes,checksum,name_hash
from rdr2_features import parser_hash
from test_rockstar import fixture as minimal,section


def fixture(encrypted=True,backup=False,duplicate=False,bad_pointer=False,bad_schema=False,honor_disagrees=False,wide_pointer=False,
            camp_disagrees=False,horse_disagrees=False,unknown_horse_slot=False,missing_horse_model=False,
            records=False,fish_alias=False,fish_bad_pointer=False,stat_duplicate=False,stat_namespace=False,bad_horse_counts=False,
            bounties=False,bounty_zero=False,bounty_temporary=False,bounty_mismatch=False,bounty_bad_count=False,
            unlocks=False,unlock_duplicate=False,unlock_bad_pointer=False,unlock_bad_schema=False,unlock_version=False,unlock_short_count=False,
            supplies=False,components=False,component_duplicate=False,component_flags=False,component_cycle=False,component_quantity=False):
    blocks=[];schemas={}
    def block(name,size,fields,data):
        h=parser_hash(name) if isinstance(name,str) else name
        schemas[h]=(size,[(parser_hash(k) if isinstance(k,str) else k,t,sub,off,parser_hash(ref) if isinstance(ref,str) else ref) for k,t,sub,off,ref in fields])
        blocks.append((h,bytes(data)));return len(blocks)
    def pointer(block,offset=0):return struct.pack('>I',block|((offset&4095)<<20))+struct.pack('<I',offset>>12)
    base='CPedInventorySaveStructure__CInventorySaveInfoBase'
    schemas[parser_hash(base)]=(48,[(0x100,12,3,0,0),(parser_hash('items'),13,0,8,0)])
    root=bytearray(112);root[108]=int(backup)
    prefix=4096 if wide_pointer else 0
    root[16:32]=pointer(2,prefix)+struct.pack('>HHI',5,5,0)
    root[64:80]=pointer(2,prefix+40)+struct.pack('>HHI',1,1,0)
    block('CPedInventorySaveStructure',112,[('playerInventory',12,0,8,base),('backupInventory',12,0,56,base),('usingBackupInventory',0,0,108,0)],root)
    refs=pointer(3)+pointer(4)+pointer(5)+pointer(6)+bytes(8)+pointer(3,48)
    if duplicate:refs=pointer(3)*2+refs[16:]
    if bad_pointer:refs=pointer(4095)+refs[8:]
    blocks.append((12,bytes(prefix)+refs))
    common=[('Guid',31,0,8,0),('ParentGuid',31,0,16,0),('ItemId',11,7,24,0),('SlotId',6,0,28,0),('Quantity',31,0,40,0),('Equipped',0,0,32,0)]
    def record(size,guid,name,quantity):
        data=bytearray(size);struct.pack_into('>Q',data,8,guid);struct.pack_into('>Q',data,16,42 if supplies else 0);struct.pack_into('>I',data,24,name_hash(name));struct.pack_into('>q',data,40,quantity);return data
    data=record(48,1,'CONSUMABLE_MEDICINE',3)+record(48,9,'CONSUMABLE_MEDICINE',7)
    block('SavegameInventoryItem',48,common,data)
    gun=record(88,2,'WEAPON_REVOLVER_CATTLEMAN',1)
    for off in (56,60,64,68,72):struct.pack_into('>f',gun,off,0.25)
    block('CPedInventorySaveStructure__WeaponItem',88,common+[(k,7,0,o,0) for k,o in zip(('Degradation','PermanentDegradation','Soot','Rust','Dirt'),(56,60,64,68,72))],gun)
    horse=record(232,3,'A_C_HORSE_ARABIAN_WHITE',1);struct.pack_into('>3i',horse,116,400,20,30)
    struct.pack_into('>I',horse,28,123 if unknown_horse_slot else name_hash('SLOTID_ACTIVE_HORSE'))
    block('CPedInventorySaveStructure__HorseItem',232,common+[(k,5,0,o,0) for k,o in (('BondingXp',116),('Dirty',120),('Hungry',124))],horse)
    ammo=record(48,4,'AMMO_REVOLVER',50);block('SavegameInventoryItem',48,common,ammo)
    schemas[parser_hash('StatId')]=(8,[])
    stats=struct.pack('>2Ii',0x89587b4e,0,11 if honor_disagrees else 10)
    stats+=struct.pack('>2Ii',name_hash('GANG_SAVINGS_CASH'),0,999 if camp_disagrees else 12345)
    if records:
        stats+=struct.pack('>2Ii',name_hash('HEADSHOTS'),1 if stat_namespace else 0,37)+struct.pack('>2Ii',name_hash('DEATHS'),0,2)
        if stat_duplicate:stats+=struct.pack('>2Ii',name_hash('HEADSHOTS'),0,37)
    block('CBaseStatsSaveStructure__CIntStatStruct',12,[('statId',12,0,0,'StatId'),('Data',5,0,8,0)],stats)
    attrs=bytearray(96528 if bounties else 88760+568);attrs[88760]=3;attrs[88760+88]=23
    struct.pack_into('>i',attrs,88760+280,10)
    for n in range(3):struct.pack_into('>f',attrs,88760+8+n*8,50);struct.pack_into('>f',attrs,88760+96+n*8,100)
    schemas[0x41d6f933]=(568,[(0xa53cde40,5,0,280,0),(0xc3364edc,12,0,0,0x41d6f934),(0x18d8e817,12,0,88,0x41d6f938)])
    schemas[0x41d6f934]=(32,[(10+n,12,0,8+n*8,0x41d6f935) for n in range(3)])
    schemas[0x41d6f935]=(8,[(1,7,0,0,0)])
    schemas[0x41d6f938]=(192,[(20+n,7,0,8+n*8,0) for n in range(23)])
    struct.pack_into('>i',attrs,(4283+325)*8,12345)
    schemas[0x41d6f8bf]=(2616,[(0xe1ff2c39,5,0,2600,0)])
    struct.pack_into('>I',attrs,(1097+9)*8,0 if missing_horse_model else name_hash('A_C_HORSE_ARABIAN_WHITE'))
    attrs[1096*8]=7;attrs[(1097+398)*8]=1 if bad_horse_counts else 2
    struct.pack_into('>f',attrs,(1097+373)*8,399 if horse_disagrees else 400)
    struct.pack_into('>i',attrs,(1097+399)*8,45);struct.pack_into('>i',attrs,(1097+403)*8,55)
    schemas[0x41d6f8a2]=(3504,[(1,12,0,8,0x41d6f8a3)])
    schemas[0x41d6f8a3]=(3496,[(2,12,0,8,0x41d6f8a4)])
    schemas[0x41d6f8a4]=(3488,[(3,5,0,72,0),(4,7,0,373*8,0),(5,12,0,398*8,0x41d6f8af)])
    schemas[0x41d6f8af]=(72,[(6,12,0,8,0x41d6f8b0),(7,12,0,40,0x41d6f8b0)])
    schemas[0x41d6f8b0]=(32,[(8,5,0,0,0)])
    root_fields=[(0xb5d75947,12,64,23224,0x41d6f933),(0xa08031a2,12,0,34264,0x41d6f8bf),(0x454e4c92,12,0,8760,0x41d6f8a2)]
    if bounties:
        attrs[358*8]=5 if bounty_bad_count else 6
        struct.pack_into('>i',attrs,(359+2*12)*8,0 if bounty_zero else 2000)
        struct.pack_into('>I',attrs,(359+2*12+5)*8,0x82 if bounty_zero else 0x86)
        struct.pack_into('>i',attrs,11957*8,500 if bounty_temporary else 0)
        schemas[0x41d6f8e8]=(584,[(10+n,12,0,8+n*96,0x41d6f8e9) for n in range(6)])
        schemas[0x41d6f8e9]=(96,[(0xee983f03,5,0,0,0),(11,5,0,40,0)])
        root_fields.extend(((0x6d563153,12,0,2864,0x41d6f8e8),(0x9cafc185,5,64,30120,0)))
        bounty=bytearray(48);struct.pack_into('>I',bounty,8,777 if bounty_mismatch else 0 if bounty_zero else 2000)
        block('CBountySaveStructure',48,[('CurrentBounty',6,0,8,0)],bounty)
    block(0x41d6f894,len(attrs),root_fields,attrs)
    block('CSaveCompendium__ItemWeapon',8,[('name',11,7,0,0),('hasOwned',0,0,4,0)],struct.pack('>IB3x',name_hash('WEAPON_REVOLVER_CATTLEMAN'),0))
    clock=bytearray(64);struct.pack_into('>3I',clock,44,9,25,30)
    block('CSimpleVariablesSaveStructure',64,[('GameClockHour',6,0,44,0),('GameClockMinute',6,0,48,0),('GameClockSecond',6,0,52,0)],clock)
    health=bytearray(64);struct.pack_into('>f',health,48,250)
    block('CPlayerPedSaveStructure',64,[('fHealth',7,0,48,0)],health)
    cash=record(48,8,'CURRENCY_CASH',12345);struct.pack_into('>I',cash,28,name_hash('SLOTID_CURRENCY'))
    cash_id=block('SavegameInventoryItem',48,common,cash)
    refs=refs[:32]+pointer(cash_id)+refs[40:];blocks[1]=(12,bytes(prefix)+refs)
    if supplies:
        character=record(112,42,'CHARACTER_PLAYER',1);struct.pack_into('>Q',character,16,0)
        character_id=block('CPedInventorySaveStructure__CharacterItem',112,common,character)
        refs=refs[:40]+pointer(character_id)+refs[40:];blocks[1]=(12,bytes(prefix)+refs)
        root[16:32]=pointer(2,prefix)+struct.pack('>HHI',6,6,0)
        root[64:80]=pointer(2,prefix+48)+struct.pack('>HHI',1,1,0)
        blocks[0]=(blocks[0][0],bytes(root))
    if unlocks:
        catalog=[('WEAPON_REVOLVER_CATTLEMAN',0x89),('CLOTHING_SP_OUTFIT_LGD_GATOR_PANTHER',9),
            ('CLOTHING_HL_PLAYER_SATCHEL_004_1',7),('DOCUMENT_NEWSPAPER_ED_10',0),('NOT_A_KNOWN_ITEM',0)]
        if components:catalog.extend((n,9) for n in ('COMPONENT_SHORTARM_FRAME_MATERIAL_1','COMPONENT_SHORTARM_FRAME_MATERIAL_2',
            'COMPONENT_REVOLVER_CATTLEMAN_BARREL_SHORT','COMPONENT_REVOLVER_CATTLEMAN_BARREL_LONG',
            'COMPONENT_SHORTARM_GRIPSTOCK_TINT_A_5','COMPONENT_SHORTARM_GRIPSTOCK_TINT_A_6'))
        if unlock_duplicate:catalog.append(catalog[0])
        data=b''.join(struct.pack('>IB3s',name_hash(n),v,b'\x12\x34\x56') for n,v in catalog)
        items=block('SUnlockInfo',8,[('Hash',11,7 if unlock_bad_schema else 11,0,6),('PackedData',2,0,4,0)],data)
        unlock=bytearray(32);struct.pack_into('>I',unlock,8,int(unlock_version))
        unlock[16:32]=pointer(4095 if unlock_bad_pointer else items)+struct.pack('>HHI',1 if unlock_short_count else len(catalog),len(catalog),0)
        block('CUnlockSaveStructureSP',32,[('UnlockSaveDataVersion',6,0,8,0),('UnlockXmlVersion',6,0,12,0),('UnlockItemList',13,0,16,0)],unlock)
    if components:
        entries=[]
        for n,parent,name,slot,enabled in (
            (50,2,'COMPONENT_REVOLVER_CATTLEMAN_BARREL_SHORT',0x3d0d02db,0),
            (51,2,'COMPONENT_REVOLVER_CATTLEMAN_BARREL_SHORT' if component_duplicate else 'COMPONENT_REVOLVER_CATTLEMAN_BARREL_LONG',0x3d0d02db,2 if component_flags else 1),
            (52,2,'COMPONENT_SHORTARM_FRAME_MATERIAL_1',0x0f43dcc6,1),
            (53,53 if component_cycle else 2,'COMPONENT_REVOLVER_CATTLEMAN_GRIP',0xebe563e3,1),
            (54,2,'COMPONENT_REVOLVER_CATTLEMAN_GRIP_PEARL',0xebe563e3,0),
            (55,53,'COMPONENT_SHORTARM_GRIPSTOCK_TINT_A_5',0x7fe38573,1),
        ):
            data=record(48,n,name,2 if component_quantity and n==52 else 1)
            struct.pack_into('>Q',data,16,parent);struct.pack_into('>I',data,28,slot);data[32]=enabled
            entries.append(data)
        id=block('SavegameInventoryItem',48,common,b''.join(entries))
        count=struct.unpack_from('>H',root,24)[0]
        refs=refs[:count*8]+b''.join(pointer(id,n*48) for n in range(len(entries)))+refs[count*8:]
        blocks[1]=(12,bytes(prefix)+refs);count+=len(entries)
        root[16:32]=pointer(2,prefix)+struct.pack('>HHI',count,count,0)
        root[64:80]=pointer(2,prefix+count*8)+struct.pack('>HHI',1,1,0);blocks[0]=(blocks[0][0],bytes(root))
    if records:
        history=bytearray(56);struct.pack_into('>I',history,0,name_hash('A_C_HORSE_ARABIAN_WHITE'));struct.pack_into('>II',history,44,3,2)
        block('CSaveCompendium__ItemHorse',56,[('name',11,7,0,0),('numBroken',6,0,44,0),('highestBondingLevel',6,0,48,0)],history)
        history=bytearray(56);struct.pack_into('>I',history,0,name_hash('GANG_ODRISCOLL'));struct.pack_into('>4I',history,40,1,2,3,4)
        block('CSaveCompendium__ItemGang',56,[('name',11,7,0,0)]+[(n,6,0,o,0) for n,o in zip(('ambushesSurvived','uniqueEncounters','bountiesCaptured','gangMembersKilled'),(40,44,48,52))],history)
        fish=bytearray(64);lure_block=len(blocks)+2
        for i,name in enumerate(('PROVISION_FISH_BLUEGILL','PROVISION_FISH_PERCH')):
            struct.pack_into('>I',fish,i*32,name_hash(name))
            fish[i*32+8:i*32+24]=pointer(4095 if fish_bad_pointer else lure_block,0 if i==0 or fish_alias else 16)+struct.pack('>HHI',2 if i==0 else 1,2,0)
        block('CSaveCompendium__ItemFish',32,[('name',11,7,0,0),('lures',13,0,8,0),('wasObserved',0,0,24,0)],fish)
        lure=struct.pack('>6I',name_hash('UPGRADE_FSH_BAIT_CRICKET'),3,name_hash('UPGRADE_FSH_BAIT_WORM'),5,name_hash('UPGRADE_FSH_BAIT_CRICKET'),2)
        block('CSaveCompendium__ItemFishLure',8,[('lureName',11,7,0,0),('numCaught',6,0,4,0)],lure)
    if bad_schema:
        h=parser_hash('CPedInventorySaveStructure__WeaponItem');size,fields=schemas[h]
        schemas[h]=(size,[(k,6 if k==parser_hash('Dirt') else t,sub,o,ref) for k,t,sub,o,ref in fields])
    data=b'';mapping=[]
    for h,raw in blocks:
        padding=bytes((-len(data))%16);data+=padding;mapping.append((h,len(data)+8,0,len(raw)));data+=raw
    index=b'';definitions=b'';offset=12+len(schemas)*8
    for h,(size,fields) in schemas.items():
        definition=struct.pack('>3I',len(fields),size,0)+b''.join(struct.pack('>IBBHI',*f) for f in fields)
        index+=struct.pack('>2I',h,offset+len(definitions));definitions+=definition
    frame=section(b'PSIN',data)+section(b'PMAP',struct.pack('>IIHHI',1,0,len(blocks),0,0)+b''.join(struct.pack('>4I',*m) for m in mapping))
    frame+=section(b'PSCH',struct.pack('>I',len(schemas))+index+definitions)+section(b'PSIG',b'')
    check=b'CHKS'+struct.pack('>4I',20,len(frame)+20,0,1)
    check=check[:12]+struct.pack('>I',checksum(frame+check[:8]+bytes(8)+check[16:]))+check[16:]
    header=minimal('rdr2',False)[:0x110];body=b'RSAV'+bytes(188)+frame+check;body+=bytes((-len(body))%16)
    return header+(aes(body,False) if encrypted else body)


class Rdr2FeatureTests(unittest.TestCase):
    def test_all_supported_sections_and_both_active_inventory_modes(self):
        s=Save(fixture(),'rdr2');groups=Counter(f.group for f in s.slots[0].fields)
        self.assertEqual(groups,{'Currency':1,'Honor':1,'Player cores':4,'Player progression':4,'Inventory':2,'Weapon condition':5,'Horses':5,'Camp':1,'Compendium':1,'World clock':3})
        inv=[f for f in s.slots[0].fields if f.group=='Inventory'];self.assertEqual([f.value for f in inv],[3,50])
        archive=Save(fixture(backup=True),'rdr2');self.assertEqual([f.value for f in archive.slots[0].fields if f.group=='Inventory'],[7])

    def test_every_feature_roundtrips_exactly_and_only_declared_spans_change(self):
        for encrypted in (True,False):
            raw=fixture(encrypted,records=True);s=Save(raw,'rdr2');self.assertFalse(s.warnings);self.assertEqual(s.rockstar.patch({}),raw)
            changes={};allowed=set()
            for f in s.slots[0].fields:
                changes[0,f.key]=0.1234567 if f.decimal and f.maximum==1 else f.value+1
                fmt=s.rockstar.rdr2.formats.get(f.key,'>I')
                allowed.update(range(f.offset,f.offset+struct.calcsize(fmt)))
                for at in s.rockstar.rdr2.related.get(f.key,()):allowed.update(range(at,at+4))
                for at in s.rockstar.rdr2.campaign.money.get(f.key,()):allowed.update(range(at,at+4))
                for at,fmt in s.rockstar.rdr2.campaign.mirrors.get(f.key,()):allowed.update(range(at,at+struct.calcsize(fmt)))
            out=s.patched(changes);after=Save(out,'rdr2');self.assertFalse(after.warnings)
            for begin,at in s.rockstar.container.checks:allowed.update(range(at+12,at+16))
            self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(s.rockstar.container.plain,after.rockstar.container.plain))))
            self.assertEqual(after.patched({(0,f.key):f.value for f in s.slots[0].fields}),raw)
            self.assertEqual(len(out),len(raw));self.assertEqual(out[:0x110],raw[:0x110])

    def test_bad_pointers_duplicate_guids_schema_mismatches_and_honor_disagreement_are_protected(self):
        for args in ({'bad_pointer':True},{'duplicate':True}):
            s=Save(fixture(**args),'rdr2');self.assertFalse(any(f.group in ('Inventory','Weapon condition','Horses') for f in s.slots[0].fields))
        s=Save(fixture(bad_schema=True),'rdr2');self.assertFalse(any(f.key.endswith(':dirt') and f.group=='Weapon condition' for f in s.slots[0].fields))
        s=Save(fixture(honor_disagrees=True),'rdr2');self.assertNotIn('honor',{f.key for f in s.slots[0].fields})
        with self.assertRaises(ValueError):s.patched({(0,'honor'):100})

    def test_inventory_cannot_be_deleted_and_attributes_reject_unsafe_ranges(self):
        s=Save(fixture(),'rdr2');fields=s.slots[0].fields
        for group,value in (('Inventory',0),('Weapon condition',1.01),('Player cores',101),('Honor',321),('Horses',-1),('World clock',99)):
            f=next(f for f in fields if f.group==group)
            with self.subTest(group=group),self.assertRaises(ValueError):s.patched({(0,f.key):value})

    def test_extended_pointer_word_preserves_active_and_backup_membership(self):
        for backup in (False,True):
            a=Save(fixture(backup=backup),'rdr2');b=Save(fixture(backup=backup,wide_pointer=True),'rdr2')
            self.assertEqual([(f.key,f.value) for f in a.slots[0].fields],[(f.key,f.value) for f in b.slots[0].fields])

    def test_navigation_assigns_every_field_once_and_labels_are_bundled(self):
        from editor_layout import organize_fields
        s=Save(fixture(),'rdr2');categories=organize_fields('rdr2',s.slots[0].fields)
        self.assertEqual([c.name for c in categories],['Progress','Character','Collection'])
        flat=[f for c in categories for section in c.sections for f in section.fields]
        self.assertEqual(Counter(f.key for f in flat),Counter(f.key for f in s.slots[0].fields))
        self.assertFalse(any('Unidentified' in f.collection for f in s.slots[0].fields))

    def test_campaign_copies_stay_synchronized_and_cents_are_exact(self):
        s=Save(fixture(),'rdr2');xp='item:0000000000000003:bondingxp'
        out=s.patched({(0,'camp:cash'):765.43,(0,xp):1234});after=Save(out,'rdr2')
        campaign=after.rockstar.rdr2.campaign;plain=after.rockstar.container.plain
        self.assertEqual([struct.unpack_from('>i',plain,at)[0] for at in campaign.money['camp:cash']],[76543,76543])
        self.assertEqual(struct.unpack_from('>f',plain,campaign.mirrors[xp][0][0])[0],1234)
        self.assertEqual(next(f.value for f in after.slots[0].fields if f.key==xp),1234)
        with self.assertRaises(ValueError):s.patched({(0,'camp:cash'):1.001})

    def test_disagreement_and_unmapped_horse_slots_are_protected(self):
        s=Save(fixture(camp_disagrees=True),'rdr2');self.assertNotIn('camp:cash',{f.key for f in s.slots[0].fields})
        for args in ({'horse_disagrees':True},{'unknown_horse_slot':True},{'missing_horse_model':True}):
            s=Save(fixture(**args),'rdr2');f=next(f for f in s.slots[0].fields if f.key.endswith(':bondingxp'))
            self.assertTrue(f.readonly)
            with self.assertRaises(ValueError):s.patched({(0,f.key):500})
            if not args.get('horse_disagrees'):
                self.assertFalse(any(f.group=='Horses' and f.key.endswith(':health_core') for f in s.slots[0].fields))

    def test_compendium_histories_are_distinct_from_inventory_and_statistics_are_unique(self):
        s=Save(fixture(records=True),'rdr2');fields={f.key:f for f in s.slots[0].fields}
        fish=[f for f in fields.values() if ':lure:' in f.key];self.assertEqual([f.value for f in fish],[3,5,2])
        self.assertEqual(fields['stat:HEADSHOTS'].value,37);self.assertEqual(fields['stat:DEATHS'].value,2)
        changes={(0,f.key):9 for f in fish};changes[0,'stat:HEADSHOTS']=40
        out=Save(s.patched(changes),'rdr2');self.assertEqual(len(out.rockstar.rdr2.active_items()),5)
        self.assertTrue(all(f.value==9 for f in out.slots[0].fields if ':lure:' in f.key))
        for args in ({'stat_duplicate':True},{'stat_namespace':True}):
            protected=Save(fixture(records=True,**args),'rdr2');self.assertNotIn('stat:HEADSHOTS',{f.key for f in protected.slots[0].fields})

    def test_shared_or_invalid_fishing_arrays_do_not_offer_overlapping_fields(self):
        s=Save(fixture(records=True,fish_alias=True),'rdr2')
        self.assertEqual([f.value for f in s.slots[0].fields if ':lure:' in f.key],[5])
        s=Save(fixture(records=True,fish_bad_pointer=True),'rdr2');self.assertFalse(any(':lure:' in f.key for f in s.slots[0].fields))

    def test_invalid_horse_core_count_and_scalar_schema_aliases_are_protected(self):
        from types import SimpleNamespace
        from rdr2_campaign import scalar_paths,ROOT
        s=Save(fixture(bad_horse_counts=True),'rdr2')
        self.assertFalse(any(f.group=='Horses' and f.key.endswith(':health_core') for f in s.slots[0].fields))
        frame=SimpleNamespace(structures={ROOT:(32,[(1,5,0,8,0),(2,7,0,16,0),(3,5,128,24,0)])})
        self.assertEqual(len(scalar_paths(frame,ROOT,8,5)),1)
        self.assertFalse(scalar_paths(frame,ROOT,16,5));self.assertFalse(scalar_paths(frame,ROOT,24,5))
        frame.structures[ROOT][1].append((4,5,0,8,0))
        self.assertEqual(len(scalar_paths(frame,ROOT,8,5)),2)

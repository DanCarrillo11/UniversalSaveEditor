"""Synthetic SL2 fixtures: no personal profiles or downloaded saves bundled."""
import hashlib
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib
from core import Save, FormatError, discover, identify_game, replace_current
from elden_ring import FILE_SIZE, SLOT_SIZE, BLOCK_SIZE, GLOBAL_START, EldenRingSave


def fixture(version=211, menu_size=0x1800, projectile_count=3, regions=2, worlds=(4,32,40,32,4), character_versions=None, archetype=0):
    raw=bytearray(FILE_SIZE)
    raw[:4]=b'BND4';struct.pack_into('<I',raw,12,12)
    blocks=[(0x300+i*BLOCK_SIZE,BLOCK_SIZE) for i in range(10)]
    blocks += [(GLOBAL_START,0x60010),(GLOBAL_START+0x60010,0x240020)]
    for i,(start,length) in enumerate(blocks):
        struct.pack_into('<QI',raw,0x40+i*32+8,length,start)
    global_data=GLOBAL_START+16
    struct.pack_into('<IQ',raw,global_data,version,76561197960265728)
    struct.pack_into('<I',raw,global_data+0x150,menu_size)
    active=global_data+0x154+menu_size
    for slot in (0,3):
        slot_version=version if character_versions is None else character_versions[0 if slot==0 else 1]
        raw[active+slot]=1
        start=blocks[slot][0]+16
        struct.pack_into('<I',raw,start,slot_version)
        p=start+32
        for i in range(5118 if slot_version<=81 else 5120):
            h=(0x80000001,0x90000001,0xc0000001)[i] if i<3 else 0
            struct.pack_into('<II',raw,p,h,10000 if h else 0xffffffff)
            p+=21 if h>>28==8 else 16 if h>>28==9 else 8
        player=p
        for off,value in ((8,300),(12,414),(16,414),(20,50),(24,78),(28,78),(36,90),(40,105),(44,105)):
            struct.pack_into('<I',raw,p+off,value)
        stats=(10,12,11,13,15,8,11,6) if archetype==10 else (14,8,17,15,11,7,8,9) if archetype==11 else (15,10,11,14,13,9,9,7)
        struct.pack_into('<8I',raw,p+52,*stats)
        raw[p+183]=archetype
        struct.pack_into('<3I',raw,p+96,sum(stats)-79,500,1200)
        name=f'Test {slot+1}'.encode('utf-16-le');raw[p+148:p+148+len(name)]=name
        profile=active+10+slot*588;raw[profile:profile+len(name)]=name
        struct.pack_into('<3I',raw,profile+34,sum(stats)-79,100,1200)
        p+=932
        for group,capacity,keys in (('held',2688,384),('storage',1920,128)):
            struct.pack_into('<I',raw,p,3)
            # Rowa Fruit: goods handles contain a B prefix; preserve acquisition ID.
            struct.pack_into('<3I',raw,p+4,0xb00050f0,10,77)
            # Empty stack, unknown good and equipment quantity stay unchanged.
            struct.pack_into('<3I',raw,p+16,0xb0002774,0,78)
            struct.pack_into('<3I',raw,p+28,0xbffffffe,7,79)
            struct.pack_into('<3I',raw,p+40,0x80000001,1,80)
            p+=16+(capacity+keys)*12
            if group=='held':
                p+=116+140+24
                struct.pack_into('<I',raw,p,projectile_count);p+=4+projectile_count*8+156+12+303
        p+=256;struct.pack_into('<I',raw,p,regions);p+=4+regions*4+117
        struct.pack_into('<I',raw,p+4,17);p+=8+17+52+112008
        struct.pack_into('<II',raw,p+4,4,1);p+=12+29+0x1bf9a0
        for size in worlds:
            struct.pack_into('<I',raw,p,size);p+=4+size
        p+=61+10+4+(1 if slot_version>=66 else 0)+0x20004+12+12+16+8+32+50
        for offset,data in EldenRingSave._fingerprint_data(raw,player):
            struct.pack_into('<I',raw,p+offset,(zlib.adler32(data)*2)&0xffffffff)
        raw[p+16:p+20]=b'\xfe\xff\xff\xff'  # Preserve opaque hash padding.
        raw[p+128:p+142]=b'KEEP TAIL DATA'
    for start,length in blocks:
        raw[start:start+16]=hashlib.md5(raw[start+16:start+length]).digest()
    return bytes(raw)


class EldenRingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.raw=fixture()

    def values(self,save,index=0):return {f.key:f.value for f in save.slots[index].fields}

    def test_gaps_and_identity_roundtrip(self):
        save=Save(self.raw,'eldenring')
        self.assertEqual([s.name for s in save.slots],['Character 1 · Test 1','Character 4 · Test 4'])
        self.assertEqual(save.patched({}),self.raw)
        self.assertEqual(self.values(save)['inventory:0'],10)
        self.assertNotIn('inventory:1',self.values(save))
        self.assertNotIn('inventory:2',self.values(save))
        self.assertNotIn('inventory:3',self.values(save))

    def test_stats_level_and_global_mirror_with_only_authorized_bytes_changed(self):
        save=Save(self.raw,'eldenring');char=save.elden_ring.characters[0]
        out=save.patched({(0,'vigor'):20,(0,'runes'):900,(0,'inventory:0'):99})
        parsed=Save(out,'eldenring');values=self.values(parsed)
        self.assertEqual((values['level'],values['runes_memory']),(14,1600))
        self.assertEqual(struct.unpack_from('<I',out,char.profile+34)[0],14)
        self.assertEqual(struct.unpack_from('<I',out,char.profile+42)[0],1600)
        allowed=set(range(char.start-16,char.start))|set(range(GLOBAL_START,GLOBAL_START+16))
        for f in save.slots[0].fields:
            if f.key in ('vigor','runes','inventory:0','level','runes_memory'):allowed.update(range(f.offset,f.offset+4))
        for offset in (34,42):allowed.update(range(char.profile+offset,char.profile+offset+4))
        for offset in (0,4,8,12,20,24):allowed.update(range(char.fingerprints+offset,char.fingerprints+offset+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(self.raw,out))))
        self.assertFalse(parsed.warnings)

    def test_decreasing_runes_preserves_lifetime_and_other_character_edits(self):
        parsed=Save(Save(self.raw,'eldenring').patched({(0,'runes'):0,(1,'storage:0'):999}),'eldenring')
        self.assertEqual(self.values(parsed)['runes_memory'],1200)
        self.assertEqual(self.values(parsed,1)['storage:0'],999)

    def test_calculated_fields_limits_and_original_class_are_enforced(self):
        save=Save(self.raw,'eldenring')
        for changes in ({(0,'level'):50},{(0,'runes_memory'):1},{(0,'vigor'):14},{(0,'vigor'):100},
                        {(0,'inventory:0'):0},{(0,'storage:0'):1000},{(0,'hp'):415},{(0,'unknown'):1}):
            with self.assertRaises(ValueError):save.patched(changes)

    def test_level_cap(self):
        save=Save(self.raw,'eldenring')
        fields={ (0,f.key):99 for f in save.slots[0].fields if f.group=='Attributes' and not f.readonly }
        self.assertEqual(self.values(Save(save.patched(fields),'eldenring'))['level'],713)

    def test_revision_and_variable_sections_change_offsets_without_search(self):
        for version in (65,81,82,131,250,260,261):
            raw=fixture(version=version,menu_size=64,projectile_count=7,regions=5,worlds=(0,0,0,0,0))
            save=Save(raw,'eldenring');out=save.patched({(1,'runes'):501})
            self.assertEqual(self.values(Save(out,'eldenring'),1)['runes_memory'],1201)
            self.assertEqual(save.patched({}),raw)

    def test_mixed_revision_file_does_not_block_the_newer_character(self):
        raw=fixture(character_versions=(250,261));save=Save(raw,'eldenring')
        out=save.patched({(1,'runes'):900,(1,'vigor'):20})
        updated=Save(out,'eldenring')
        self.assertEqual(self.values(updated,1)['level'],14)
        self.assertEqual(out[0x300:0x300+BLOCK_SIZE],raw[0x300:0x300+BLOCK_SIZE])
        self.assertEqual(struct.unpack_from('<I',out,save.elden_ring.characters[1].start)[0],261)

    def test_new_starting_classes_keep_their_own_minimum_attributes(self):
        for archetype,key,minimum in ((10,'arcane',6),(11,'endurance',17)):
            save=Save(fixture(version=261,archetype=archetype),'eldenring')
            self.assertEqual(self.values(save)[key],minimum)
            with self.assertRaises(ValueError):save.patched({(0,key):minimum-1})
            out=save.patched({(0,key):minimum+1})
            self.assertEqual(self.values(Save(out,'eldenring'))['level'],self.values(save)['level']+1)

    def test_new_revision_does_not_bypass_unknown_layout_or_fingerprint_checks(self):
        raw=fixture(version=261);save=Save(raw,'eldenring');char=save.elden_ring.characters[1]
        for offset,value in ((char.start,262),(char.fingerprints,0),(char.player+96,99),(char.start+32,0xffffffff)):
            broken=bytearray(raw);struct.pack_into('<I',broken,offset,value)
            with self.assertRaises(FormatError):Save(bytes(broken),'eldenring')
        broken=bytearray(raw);broken[char.player+183]=12
        with self.assertRaises(FormatError):Save(bytes(broken),'eldenring')

    def test_corrupted_checksum_requires_explicit_repair(self):
        raw=bytearray(self.raw);raw[0x300]^=1;raw[GLOBAL_START+0x60010]^=1
        save=Save(bytes(raw),'eldenring');self.assertEqual(len(save.warnings),2)
        with self.assertRaises(ValueError):save.patched({(0,'runes'):501})
        repaired=save.patched({},repair_crc=True)
        self.assertEqual(repaired,self.raw)

    def test_invalid_tables_lengths_fingerprints_and_progression_are_rejected(self):
        save=Save(self.raw,'eldenring');char=save.elden_ring.characters[0]
        for offset,value in ((0x50,0),(char.start,999),(char.player+96,42),
                             (char.fingerprints,0),(GLOBAL_START+16+0x150,0xffffffff)):
            raw=bytearray(self.raw);struct.pack_into('<I',raw,offset,value)
            with self.assertRaises(FormatError):Save(bytes(raw),'eldenring')
        for raw in (self.raw[:-1],self.raw+b'x',b'BND4'+self.raw[4:100]):
            with self.assertRaises(FormatError):Save(raw,'eldenring')

    def test_lifetime_overflow_is_rejected(self):
        raw=bytearray(self.raw);save=Save(self.raw,'eldenring');char=save.elden_ring.characters[0]
        for offset in (char.player+104,char.profile+42):struct.pack_into('<I',raw,offset,0xffffffff)
        struct.pack_into('<I',raw,char.fingerprints+24,(zlib.adler32(raw[char.player+104:char.player+108])*2)&0xffffffff)
        save=Save(bytes(raw),'eldenring')
        with self.assertRaisesRegex(ValueError,'overflow'):save.patched({(0,'runes'):501},repair_crc=True)

    def test_variable_section_counts_cannot_escape_character_bounds(self):
        save=Save(self.raw,'eldenring');char=save.elden_ring.characters[0]
        held=next(f.offset-8 for f in save.slots[0].fields if f.key=='inventory:0')
        projectiles=held+36880+116+140+24
        storage=projectiles+4+3*8+156+12+303
        regions=storage+24592+256
        for offset in (char.start+32,held,held+4+2688*12,projectiles,storage,regions):
            raw=bytearray(self.raw);struct.pack_into('<I',raw,offset,0xffffffff)
            with self.assertRaises(FormatError):Save(bytes(raw),'eldenring')

    def test_preexisting_nonstandard_vitals_are_preserved_until_explicitly_changed(self):
        raw=bytearray(self.raw);char=Save(self.raw,'eldenring').elden_ring.characters[0]
        struct.pack_into('<I',raw,char.player+20,100)
        save=Save(bytes(raw),'eldenring')
        out=save.patched({(0,'runes'):501},repair_crc=True)
        self.assertEqual(self.values(Save(out,'eldenring'))['fp'],100)
        with self.assertRaisesRegex(ValueError,'saved maximum'):save.patched({(0,'fp'):90},repair_crc=True)
        out=save.patched({(0,'fp'):78},repair_crc=True)
        self.assertEqual(self.values(Save(out,'eldenring'))['fp'],78)

    def test_discovery_identification_and_direct_apply_without_backups(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'EldenRing/76561197960265728/ER0000.sl2'
            path.parent.mkdir(parents=True);path.write_bytes(self.raw)
            with patch.dict(os.environ,{'APPDATA':str(root)}),patch('core.documents_folder',return_value=root/'Documents'):
                self.assertIn(('eldenring',path),discover())
            self.assertEqual(identify_game(path),'eldenring')
            save=Save(self.raw,'eldenring');out=save.patched({(0,'runes'):777})
            replace_current(path,self.raw,out)
            self.assertEqual(path.read_bytes(),out)
            self.assertEqual(list(path.parent.iterdir()),[path])


if __name__=='__main__':unittest.main()

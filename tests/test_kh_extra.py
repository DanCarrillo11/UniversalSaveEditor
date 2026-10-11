"""Synthetic fixtures: no downloaded or personal saves are distributed."""
import struct
import unittest
import zlib
from pathlib import Path
import tempfile
from core import Save, FormatError, identify_game
from kh_pc import recom_checksum, bbs_checksum
from kh3_pc import transform, derive_key, AccountIdRequired
from editor_layout import organize_fields
from test_core import chunk


def archive(game, records=2):
    stride = {'recom':0x3a30,'bbs':0x13c00,'ddd':0x16600}[game]
    length = {'recom':0x3630,'bbs':0x12000,'ddd':0x16600}[game]
    pre = chunk(b'IHDR',bytes(13))+chunk(b'tEXt',bytes(43))
    payload = bytearray(16+100*(344+stride)+128)
    base = 16+34400
    for index in range(records):
        descriptor = 16+index*344
        name = f'Test {index}'.encode()+b'\0'
        payload[descriptor:descriptor+len(name)] = name
        struct.pack_into('<I',payload,descriptor+80,length)
        r = base+index*stride
        if game == 'recom':
            struct.pack_into('<4I',payload,r,7,0,length-16,0)
            struct.pack_into('<i',payload,r+0x2d58,1162+index)
            struct.pack_into('<i',payload,r+0x14,1162+index)
            struct.pack_into('<I',payload,r+4,recom_checksum(payload[r+16:r+length]))
        elif game == 'bbs':
            struct.pack_into('<4I',payload,r,0x44534242,0x1d,0x11e50,0)
            payload[r+0x17] = index+1
            payload[r+0x5cac] = 0x48
            struct.pack_into('<I',payload,r+0x59d4,500+index)
            # Preserve PC entry padding beyond the declared FM record length.
            payload[r+0x11e50:r+length] = bytes([0x5a])*(length-0x11e50)
            struct.pack_into('<I',payload,r+12,bbs_checksum(payload[r:r+0x11e50]))
        else:
            payload[r:r+4] = b'SOMD'
            payload[r+4] = 0x14
            payload[r+0x92] = payload[r+0x20] = 1
            struct.pack_into('<I',payload,r+0xd2ec,500+index)
    return b'\x89PNG\r\n\x1a\n'+pre+chunk(b'sqEX',payload)+chunk(b'IEND',b'')


def kh3_plain():
    raw = bytearray(0x94f4f0)
    raw[:4] = b'S@vE'
    struct.pack_into('<I',raw,4,0x94f4d8)
    raw[0x2c] = 1
    raw[-8:] = b'PADDING!'
    struct.pack_into('<I',raw,12,zlib.crc32(raw[16:0x94f4e8]))
    return bytes(raw)


class ExtraKhTests(unittest.TestCase):
    def test_recom_checksum_known_zero_payload(self):
        # Independent, hand-derived vectors from the published recurrence.
        self.assertEqual(recom_checksum(b''),0)
        self.assertEqual(recom_checksum(b'\x00'),0x04c11db6)
        self.assertEqual(recom_checksum(b'\x01'),1)

    def test_no_changes_preserve_entire_archives(self):
        for game in ('recom','bbs','ddd'):
            raw = archive(game)
            self.assertEqual(Save(raw,game).patched({}),raw)

    def test_recom_mirrors_checksum_and_untouched_slot(self):
        raw = archive('recom');save = Save(raw,'recom')
        result = save.patched({(0,'moogle_points'):9876,(0,'difficulty'):2,(0,'card:0'):8})
        r,length = save.extra_kh.records[0]
        self.assertEqual(struct.unpack_from('<i',result,r+0x14)[0],9876)
        self.assertEqual(struct.unpack_from('<I',result,r+4)[0],recom_checksum(result[r+16:r+length]))
        self.assertEqual(result[r+0x3a30:r+2*0x3a30],raw[r+0x3a30:r+2*0x3a30])
        self.assertFalse(Save(result,'recom').warnings)

    def test_bbs_difficulty_mapping_abilities_and_padding(self):
        raw = archive('bbs');save = Save(raw,'bbs')
        result = save.patched({(1,'difficulty'):3,(1,'munny'):999,(1,'ability:0:slots'):2,(1,'ability:0:active'):2})
        r,length = save.extra_kh.records[1]
        self.assertEqual(result[r+0x5cac],0xc8)
        self.assertEqual(result[r+length:r+0x12000],raw[r+length:r+0x12000])
        self.assertFalse(Save(result,'bbs').warnings)
        with self.assertRaises(ValueError):save.patched({(0,'ability:0:active'):1})

    def test_ddd_loading_mirrors_and_character_categories(self):
        save = Save(archive('ddd'),'ddd')
        result = save.patched({(0,'difficulty'):3,(0,'character:Sora:experience'):9000,(0,'character:Riku:experience'):8000})
        r,length = save.extra_kh.records[0]
        self.assertEqual(result[r+0x20],3)
        self.assertEqual(struct.unpack_from('<I',result,r+0x28)[0],9000)
        categories = organize_fields('ddd',save.slots[0].fields)
        character = next(c for c in categories if c.name=='Characters')
        self.assertEqual({s.selection for s in character.sections},{'Sora','Riku'})

    def test_checksum_requires_explicit_repair(self):
        raw = bytearray(archive('recom'));raw[34400+112+4] ^= 1
        # Repair PNG CRC separately so the test exercises the internal checksum.
        from core import png_chunks
        start,end = next((s,e) for n,s,e in png_chunks(raw,allow_sqex_crc=True) if n==b'sqEX')
        struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
        save = Save(bytes(raw),'recom')
        with self.assertRaises(ValueError):save.patched({(0,'moogle_points'):3})
        self.assertFalse(Save(save.patched({},repair_crc=True),'recom').warnings)

    def test_bounds_wrong_game_and_renamed_archives(self):
        for game in ('recom','bbs','ddd'):
            raw = archive(game)
            with self.assertRaises(ValueError):Save(raw[:-1],game)
            with self.assertRaises(ValueError):Save(raw,'bbs' if game!='bbs' else 'recom')
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'renamed.png';path.write_bytes(raw)
                self.assertEqual(identify_game(path),game)
            with self.assertRaises(ValueError):Save(raw,game).patched({(0,'invented'):3})


class Kh3Tests(unittest.TestCase):
    ACCOUNT = '12345678901234567'

    def encrypted(self):
        import hashlib
        plain = kh3_plain()
        return transform(plain,self.ACCOUNT,True)+b'\x08'+hashlib.md5(plain[:0x94f4e8]).digest()

    def test_published_key_derivation_vector(self):
        self.assertEqual(derive_key('76561197999624471'),b'Ew0$iIKA!rPM$HqI2ot%!AAj(4PEv4L2')

    def test_encrypted_roundtrip_and_inventory_acquisition(self):
        raw = self.encrypted()
        save=Save(raw,'kh3',account_id=self.ACCOUNT)
        self.assertEqual(save.patched({}),raw)
        item = next(f for f in save.slots[0].fields if f.key.startswith('inventory:'))
        output=save.patched({(0,'munny'):4321,(0,'difficulty'):3,(0,item.key):2})
        check=Save(output,'kh3',account_id=self.ACCOUNT)
        self.assertEqual(check.kh3.plain[-8:],b'PADDING!')
        self.assertTrue(check.kh3.plain[item.offset+1]&1)
        self.assertFalse(check.warnings)
        self.assertEqual(len(output),len(raw))

    def test_account_is_detected_from_original_path(self):
        path=f'C:/Test/{self.ACCOUNT}/SaveGames/kh3sv2/data/KHIII_slot0.bin'
        self.assertEqual(Save(self.encrypted(),'kh3',path=path).account_id,self.ACCOUNT)

    def test_missing_wrong_account_and_corrupt_digest_are_rejected(self):
        raw=self.encrypted()
        with self.assertRaises(AccountIdRequired):Save(raw,'kh3')
        with self.assertRaises(ValueError):Save(raw,'kh3',account_id='wrong')
        damaged=raw[:-1]+bytes([raw[-1]^1])
        with self.assertRaises(ValueError):Save(damaged,'kh3',account_id=self.ACCOUNT)

    def test_plain_record_edit_preserves_every_unrelated_byte(self):
        raw=kh3_plain();save=Save(raw,'kh3');output=save.patched({(0,'munny'):55})
        changed={i for i,(a,b) in enumerate(zip(raw,output)) if a!=b}
        self.assertTrue(changed <= set(range(12,16))|set(range(0x28,0x2c)))
        self.assertFalse(Save(output,'kh3').warnings)

    def test_console_layout_and_truncated_container_are_rejected(self):
        raw=bytearray(kh3_plain());struct.pack_into('<I',raw,4,0x94e8e0)
        with self.assertRaises(ValueError):Save(raw,'kh3')
        with self.assertRaises(ValueError):Save(self.encrypted()[:-1],'kh3',account_id=self.ACCOUNT)

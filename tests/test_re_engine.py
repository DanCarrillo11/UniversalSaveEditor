"""Synthetic fixtures only: no private accounts, downloaded saves or SDK assets."""
import hashlib
import math
import struct
import unittest
from pathlib import Path
from core import Save,FormatError,identify_game
from editor_layout import organize_fields
from re_engine_container import ReEngineEnvelope,KEYS,PRIME,blowfish_cbc,_aes,splitmix
from re_engine_save import SPECS,INVENTORY_OWNERS
from re_engine_stream import StreamReader
from re_hashes import murmur32,city64,MASK64
from kh3_pc import AccountIdRequired

ACCOUNT=0x0110000100000001


def signed_file(raw):
    return bytes(raw)+struct.pack('<I',murmur32(raw))


def pairs(key_iv,account):
    result=bytearray()
    for index in range(4):
        first=index+2
        divisor=pow(first,(~account)&MASK64,PRIME)
        second=divisor*int.from_bytes(key_iv[index*8:index*8+8],'little')
        result.extend(first.to_bytes(64,'little')+second.to_bytes(64,'little'))
    return bytes(result)


def wrap(payload,game,account=ACCOUNT):
    if game in KEYS:
        head=b'DSSS'+struct.pack('<3I',2,3,3)
        head+=blowfish_cbc(b'DSSSDSSS',KEYS[game],True)
        head+=blowfish_cbc(struct.pack('<Q',account),KEYS[game],True)
        return signed_file(head+blowfish_cbc(payload,KEYS[game],True))
    encoded=bytearray()
    if game=='re4_remake':
        key_iv=bytes(range(32))
        for offset in range(0,len(payload),4096):
            clear=payload[offset:offset+4096].ljust(4096,b'\x5a')
            encoded.extend(pairs(key_iv,account&0xffffffff))
            encoded.extend(_aes(clear,key_iv[:16],key_iv[16:]))
            encoded.extend(hashlib.sha3_256(clear).digest())
    else:
        state=0x61f6868699c14dfa
        capacities=[]
        for _ in range(math.ceil(len(payload)/16384)):
            capacities.append(((state&7)+1)*16384);state=splitmix(state)
        state=(state+(~account))&MASK64;pos=0
        for capacity in capacities:
            if pos>=len(payload):break
            key=bytearray();iv=bytearray()
            for _ in range(16):state=splitmix(state);key.append(state&255);iv.append((state>>8)&255)
            mask=bytearray()
            for _ in range(528):state=splitmix(state);mask.append(state&255)
            used=payload[pos:pos+capacity];clear=used.ljust(capacity,b'\x5a')
            metadata=pairs(bytes(key+iv),account)+struct.pack('<Q',city64(used))+b'KEEPINFO'
            encoded.extend(bytes(a^b for a,b in zip(metadata,mask)))
            encoded.extend(_aes(clear,bytes(key),bytes(iv)));pos+=len(used)
    encoded.extend(b'KEEP RSA TRAILER'.ljust(128,b'\xa5'))
    return signed_file(b'DSSS'+struct.pack('<3I',2,16,0)+encoded+struct.pack('<Q',len(payload)))


def stream(game):
    offset=32 if game in KEYS else 16
    data=bytearray(offset)
    def align(size):data.extend(bytes((-len(data))%size))
    def number(fmt,value):data.extend(struct.pack(fmt,value))
    for owner,name,label,group,fmt,maximum in SPECS[game]:
        number('<I',123) # root identifier
        if 'quantities' in group and game in INVENTORY_OWNERS:
            number('<I',1);number('<I',INVENTORY_OWNERS[game])
            number('<I',murmur32(b'Items'));number('<i',17)
        number('<I',2);number('<I',owner)
        number('<I',murmur32(name.encode()))
        kind=2 if fmt=='<B' else 11 if fmt=='<f' else 10 if fmt=='<Q' else 8 if fmt=='<I' else 7
        if fmt=='<B':
            number('<i',-1);align(4)
            data.extend(struct.pack('<iIIi',kind,1,3,0));data.extend(b'\x00\x01\x00');align(4)
        else:
            number('<i',kind);number('<I',struct.calcsize(fmt));align(struct.calcsize(fmt));number(fmt,min(25,maximum));align(4)
        # Unknown property is deliberately retained, never offered by the editor.
        number('<I',murmur32(b'UnknownProperty'));number('<i',16);number('<I',16);align(16)
        data.extend(b'KEEPUNKNOWNSTATE');align(4)
    return bytes(data[offset:])


class ContainerTests(unittest.TestCase):
    def test_aes_ofb_matches_nist_sp800_38a_vector(self):
        key=bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')
        iv=bytes.fromhex('000102030405060708090a0b0c0d0e0f')
        plain=bytes.fromhex('6bc1bee22e409f96e93d7e117393172a')
        self.assertEqual(_aes(plain,key,iv).hex(),'3b3fd92eb72dad20333449f8e83cfb4a')

    def test_all_profiles_preserve_headers_padding_trailers_and_no_op_identity(self):
        payload=bytes(range(256))*600+bytes(range(13))
        for game in SPECS:
            with self.subTest(game=game):
                raw=wrap(payload,game);env=ReEngineEnvelope(raw,game,account_id=ACCOUNT)
                self.assertEqual(env.payload,payload);self.assertFalse(env.warnings)
                self.assertEqual(env.patch(payload),raw)
                edited=bytearray(payload);edited[0]^=1;edited[-1]^=2
                output=env.patch(bytes(edited))
                self.assertEqual(output[:env.offset],raw[:env.offset])
                check=ReEngineEnvelope(output,game,account_id=ACCOUNT)
                self.assertEqual(check.payload,edited);self.assertFalse(check.warnings)
                if game not in KEYS:self.assertEqual(output[-140:-12],raw[-140:-12])

    def test_account_required_and_wrong_account_or_corrupted_block_rejected(self):
        for game in ('re4_remake','re9'):
            raw=wrap(b'TEST DATA'*80,game)
            with self.assertRaises(AccountIdRequired):ReEngineEnvelope(raw,game)
            with self.assertRaises(ValueError):ReEngineEnvelope(raw,game,account_id=ACCOUNT+1)
            damaged=bytearray(raw);damaged[16+0x220]^=1
            damaged[-4:]=struct.pack('<I',murmur32(damaged[:-4]))
            with self.assertRaises(ValueError):ReEngineEnvelope(damaged,game,account_id=ACCOUNT)

    def test_wrong_game_unknown_flags_lengths_and_resizing_rejected(self):
        raw=wrap(stream('re2'),'re2')
        with self.assertRaises(ValueError):ReEngineEnvelope(raw,'re3')
        for bad in (b'DSSS',raw[:20],raw[:-10],raw+b'x'):
            with self.assertRaises(ValueError):Save(bad,'re2')
        damaged=bytearray(raw);struct.pack_into('<I',damaged,8,11)
        with self.assertRaises(ValueError):ReEngineEnvelope(damaged,'re2')
        with self.assertRaises(ValueError):ReEngineEnvelope(raw,'re2').patch(b'short')


class EngineSaveTests(unittest.TestCase):
    def test_every_game_can_edit_recognized_fields_and_keep_unknown_bytes(self):
        for game in SPECS:
            with self.subTest(game=game):
                raw=wrap(stream(game),game);save=Save(raw,game,account_id=ACCOUNT)
                self.assertFalse(save.warnings);self.assertEqual(save.patched({}),raw)
                fields=save.slots[0].fields
                self.assertTrue(fields);self.assertEqual(len({f.key for f in fields}),len(fields))
                edits={(0,f.key):(1-f.value if f.boolean else min(123.1,f.maximum) if f.decimal else min(123,f.maximum)) for f in fields}
                output=save.patched(edits);check=Save(output,game,account_id=ACCOUNT)
                before=ReEngineEnvelope(raw,game,account_id=ACCOUNT).payload
                after=ReEngineEnvelope(output,game,account_id=ACCOUNT).payload
                allowed=set()
                for f in fields:allowed.update(range(f.offset-save.re_engine.envelope.offset,f.offset-save.re_engine.envelope.offset+struct.calcsize(f.fmt)))
                self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(before,after))))
                self.assertEqual(after.count(b'KEEPUNKNOWNSTATE'),before.count(b'KEEPUNKNOWNSTATE'))
                categories=organize_fields(game,check.slots[0].fields)
                self.assertLessEqual(len(categories),3)
                self.assertEqual(sum(len(s.fields) for c in categories for s in c.sections),len(fields))
                bools=[f.label for f in fields if f.boolean]
                if bools:self.assertTrue(any('Entry 3' in label for label in bools))

    def test_integrity_repair_is_explicit_and_limits_are_validated(self):
        raw=wrap(stream('re3'),'re3');damaged=bytearray(raw);damaged[-1]^=1
        save=Save(damaged,'re3');self.assertTrue(save.warnings)
        with self.assertRaises(ValueError):save.patched({(0,save.slots[0].fields[0].key):1})
        self.assertEqual(save.patched({},True),raw)
        for edits in ({(0,'unknown'):1},{(0,save.slots[0].fields[0].key):-1}):
            with self.assertRaises(ValueError):Save(raw,'re3').patched(edits)

    def test_scene_item_counts_are_not_exposed_as_player_inventory(self):
        body=stream('re3')
        original=Save(wrap(body,'re3'),'re3')
        scene=struct.pack('<IIIIiIi',123,1,0xd759bf3d,murmur32(b'Count'),7,4,99)
        check=Save(wrap(body+scene,'re3'),'re3')
        self.assertEqual([f.key for f in original.slots[0].fields],[f.key for f in check.slots[0].fields])

    def test_parser_bounds_unknown_types_and_empty_streams(self):
        payload=stream('re9');full=bytes(16)+payload
        for length in (16,20,24,28,40,len(full)-10):
            with self.assertRaises(ValueError):StreamReader(full[:length],16).parse() if length>16 else Save(wrap(b'\0'*4,'re9'),'re9',account_id=ACCOUNT)
        damaged=bytearray(full);struct.pack_into('<i',damaged,32,999)
        with self.assertRaises(ValueError):StreamReader(damaged,16).parse()
        damaged=bytearray(full);struct.pack_into('<I',damaged,20,100001)
        with self.assertRaises(ValueError):StreamReader(damaged,16).parse()


if __name__=='__main__':unittest.main()

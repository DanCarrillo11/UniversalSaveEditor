"""Independent bounded RE Engine envelopes. SPDX-License-Identifier: GPL-3.0-or-later.

Format facts: kvasszn/ree-save-editor, mi5hmash tools and local/public fixtures.
No upstream implementation or schema assets are bundled.
"""
import hashlib
import struct
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from cryptography.hazmat.decrepit.ciphers.algorithms import Blowfish
from cryptography.hazmat.decrepit.ciphers.modes import OFB
from re_hashes import murmur32,city64,MASK64

MAX_DATA=64*1024*1024
KEYS={
    're2':b'K<>$cl%isqA|~nV4W5~3z_Q)j]5DHdB9sb{cI9Hn&Gqc-zO8O6zf',
    're3':b'mAz{]jeQ+uxyNH*d<Dt2kC5r=3M9RV6c$TaG[b|}^%&)En4F(Wvp',
    're7':b'hHGb4nS653aRT29jy',
}
PRIME=int.from_bytes(bytes.fromhex('f33b6fb972a0b72515e45c391829e182ad8a9bdc0a64d3444d79c810ab863717'),'little')


def splitmix(state):
    value=(state+0x9e3779b97f4a7c15)&MASK64
    value=((value^(value>>30))*0xbf58476d1ce4e5b9)&MASK64
    value=((value^(value>>27))*0x94d049bb133111eb)&MASK64
    return value^(value>>31)


def _account(path,explicit):
    if explicit is not None:
        try:value=int(explicit)
        except (ValueError,TypeError):raise ValueError('Enter a valid original SteamID64.')
        if 0x0110000100000000<=value<=0x01100001ffffffff:return value
        raise ValueError('Enter a valid original SteamID64.')
    if path is not None:
        parts=Path(path).parts
        for i,part in enumerate(parts):
            if part.casefold()=='userdata' and i+1<len(parts) and parts[i+1].isdigit():
                value=int(parts[i+1])
                if 0<value<1<<32:return 0x0110000100000000+value
    from kh3_pc import AccountIdRequired
    raise AccountIdRequired('The original SteamID64 is required for this copied RE Engine save.')


def _swap_words(data):
    return b''.join(data[offset:offset+4][::-1] for offset in range(0,len(data),4))


def blowfish_cbc(data,key,encrypt=False):
    end=len(data)&~7
    context=Cipher(Blowfish(key),modes.ECB()).encryptor() if encrypt else Cipher(Blowfish(key),modes.ECB()).decryptor()
    result=bytearray();previous=bytes(8)
    for offset in range(0,end,8):
        block=bytes(data[offset:offset+8])
        if encrypt:
            mixed=bytes(a^b for a,b in zip(block,previous))
            output=_swap_words(context.update(_swap_words(mixed)));previous=output
        else:
            clear=_swap_words(context.update(_swap_words(block)))
            output=bytes(a^b for a,b in zip(clear,previous));previous=block
        result.extend(output)
    context.finalize();result.extend(data[end:])
    return bytes(result)


def _aes(data,key,iv):
    context=Cipher(algorithms.AES(key),OFB(iv)).encryptor()
    return context.update(data)+context.finalize()


def _key_pair(metadata,account):
    result=bytearray()
    for offset in range(0,0x200,0x80):
        multiplier=int.from_bytes(metadata[offset:offset+64],'little')
        ciphertext=int.from_bytes(metadata[offset+64:offset+128],'little')
        if not 0<multiplier<PRIME:raise ValueError('Invalid encrypted RE Engine key metadata.')
        divisor=pow(multiplier,(~account)&MASK64,PRIME)
        value,remainder=divmod(ciphertext,divisor)
        if remainder or value>=1<<64:raise ValueError('The original account does not match this encrypted save.')
        result.extend(value.to_bytes(8,'little'))
    return bytes(result)


class ReEngineEnvelope:
    def __init__(self,raw,game,path=None,account_id=None):
        if len(raw)<20 or len(raw)>MAX_DATA or raw[:4]!=b'DSSS':raise ValueError('Unsupported RE Engine save container.')
        version,self.flags=struct.unpack_from('<2I',raw,4)
        if version!=2:raise ValueError('Unsupported RE Engine container version.')
        allowed=(3,) if game in KEYS else (16,)
        if self.flags not in allowed:raise ValueError('This RE Engine encryption/compression variant is not supported yet.')
        self.raw=bytes(raw);self.game=game;self.account=None;self.warnings=[];self.blocks=[]
        if struct.unpack_from('<I',raw,len(raw)-4)[0]!=murmur32(raw[:-4]):
            self.warnings.append('The RE Engine file integrity check does not match. Applying requires explicit integrity repair.')
        if game in KEYS:
            option=struct.unpack_from('<I',raw,12)[0]
            if option!=3 or len(raw)<40:raise ValueError('Unsupported RE Engine Blowfish header.')
            if blowfish_cbc(raw[16:24],KEYS[game])!=b'DSSSDSSS':raise ValueError('The selected Resident Evil game does not match this save.')
            # Header and account ciphertext stay byte-identical on export.
            self.offset=32;self.payload=blowfish_cbc(raw[32:-4],KEYS[game])
        elif game in ('re4_remake','re9'):
            self.offset=16;self.account=_account(path,account_id)
            length=struct.unpack_from('<Q',raw,len(raw)-12)[0]
            if not 0<length<=MAX_DATA:raise ValueError('Invalid RE Engine decrypted size.')
            encoded=raw[self.offset:-12]
            if game=='re4_remake':self.payload=self._read_lime(encoded,length)
            else:self.payload=self._read_mandarin(encoded,length)
        else:raise ValueError('Unsupported RE Engine game profile.')

    def _read_lime(self,encoded,length):
        count=(length+0xfff)//0x1000
        if count*0x1220+0x80!=len(encoded):raise ValueError('The encrypted RE4 Remake save has an unexpected size.')
        result=bytearray()
        for index in range(count):
            base=index*0x1220;metadata=encoded[base:base+0x200]
            key_iv=_key_pair(metadata,self.account&0xffffffff)
            clear=_aes(encoded[base+0x200:base+0x1200],key_iv[:16],key_iv[16:])
            digest=encoded[base+0x1200:base+0x1220]
            if hashlib.sha3_256(clear).digest()!=digest:raise ValueError('The RE4 Remake block integrity check does not match.')
            self.blocks.append((base,key_iv,None,clear))
            result.extend(clear)
        self.encoded=bytes(encoded);return bytes(result[:length])

    def _read_mandarin(self,encoded,length):
        count=(length+0x3fff)//0x4000;state=0x61f6868699c14dfa;sizes=[]
        for _ in range(count):sizes.append(((state&7)+1)*0x4000);state=splitmix(state)
        state=(state+((~self.account)&MASK64))&MASK64
        result=bytearray();base=0
        for capacity in sizes:
            if len(result)>=length:break
            if base+0x210+capacity>len(encoded):raise ValueError('The encrypted Requiem save is truncated.')
            key=bytearray();iv=bytearray()
            for _ in range(16):state=splitmix(state);key.append(state&255);iv.append((state>>8)&255)
            mask=bytearray()
            for _ in range(0x210):state=splitmix(state);mask.append(state&255)
            metadata=bytes(a^b for a,b in zip(encoded[base:base+0x210],mask))
            auth=_key_pair(metadata,self.account)
            if auth!=bytes(key+iv):raise ValueError('The Requiem encryption key does not match the original account.')
            clear=_aes(encoded[base+0x210:base+0x210+capacity],bytes(key),bytes(iv))
            used=min(capacity,length-len(result))
            if struct.unpack_from('<Q',metadata,0x200)[0]!=city64(clear[:used]):raise ValueError('The Requiem block integrity check does not match.')
            self.blocks.append((base,bytes(key+iv),bytes(mask),clear))
            result.extend(clear[:used]);base+=0x210+capacity
        if base+0x80!=len(encoded):raise ValueError('The encrypted Requiem save has an unexpected size.')
        self.encoded=bytes(encoded);return bytes(result)

    def patch(self,payload):
        if len(payload)!=len(self.payload):raise ValueError('RE Engine edits must preserve the serialized payload size.')
        result=bytearray(self.raw)
        if self.game in KEYS:result[self.offset:-4]=blowfish_cbc(payload,KEYS[self.game],True)
        else:
            encoded=bytearray(self.encoded);pos=0
            for base,key_iv,mask,original in self.blocks:
                used=min(len(original),len(payload)-pos)
                clear=payload[pos:pos+used]+original[used:]
                if self.game=='re4_remake':
                    encoded[base+0x200:base+0x1200]=_aes(clear,key_iv[:16],key_iv[16:])
                    encoded[base+0x1200:base+0x1220]=hashlib.sha3_256(clear).digest()
                else:
                    metadata=bytearray(a^b for a,b in zip(encoded[base:base+0x210],mask))
                    struct.pack_into('<Q',metadata,0x200,city64(clear[:used]))
                    encoded[base:base+0x210]=bytes(a^b for a,b in zip(metadata,mask))
                    encoded[base+0x210:base+0x210+len(clear)]=_aes(clear,key_iv[:16],key_iv[16:])
                pos+=used
            result[self.offset:-12]=encoded
        struct.pack_into('<I',result,len(result)-4,murmur32(result[:-4]))
        return bytes(result)

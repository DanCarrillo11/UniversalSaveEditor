"""Bounded PC story-save AES/CHKS and read-only PSO tables.

Independent implementation from attributed primary format facts: SOURCES.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
import struct
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes

PC_KEY=bytes.fromhex('46ed8d3f9435e4ec122cb2e2af97c57e4c5a8c3092c7844e11c686ff41df410f')
LAYOUTS={'gtav':(0x108,1,b'PSIN'),'rdr2':(0x110,4,b'RSAV')}


def checksum(data,seed=0x3fac7125):
    """Rockstar checksum uses signed bytes; this is not a normal name hash."""
    h=seed
    for b in data:
        h=(h+(b if b<128 else b-256))&0xffffffff
        h=(h+(h<<10))&0xffffffff;h^=h>>6
    h=(h+(h<<3))&0xffffffff;h^=h>>11
    return (h+(h<<15))&0xffffffff


def name_hash(name):
    # Statistic names are lowercase ASCII and use the ordinary unsigned hash.
    return checksum(name.lower().encode('ascii'),0)


def aes(body,decrypt):
    cipher=Cipher(algorithms.AES(PC_KEY),modes.ECB())
    ctx=cipher.decryptor() if decrypt else cipher.encryptor()
    return ctx.update(body)+ctx.finalize()


def u32(raw,at):return struct.unpack_from('>I',raw,at)[0]


class PsoFrame:
    """Index an exact framed PSO inside one authenticated checksum region."""
    def __init__(self,raw,start,end):
        self.start,self.end=start,end;self.blocks=[];self.structures={};parts={};at=start
        for tag in (b'PSIN',b'PMAP',b'PSCH',b'PSIG'):
            if at+8>end or raw[at:at+4]!=tag:raise ValueError('Unsupported Rockstar PSO section order.')
            size=u32(raw,at+4)
            if size<8 or size>end-at:raise ValueError('Rockstar PSO section exceeds its checksum region.')
            parts[tag]=(at,size);at+=size
        if at!=end:raise ValueError('Unsupported bytes between the Rockstar PSO frame and checksum.')
        self.data_start=start+8;self.data_end=start+parts[b'PSIN'][1]
        m,length=parts[b'PMAP']
        if length<16:raise ValueError('Truncated Rockstar mapping header.')
        count=struct.unpack_from('>H',raw,m+12)[0];header=16
        if count==0:
            if length<24:raise ValueError('Truncated Rockstar extended mapping header.')
            count=struct.unpack_from('>H',raw,m+16)[0];header=24
        if not 1<=count<=8192 or header+count*16!=length or not 1<=u32(raw,m+8)<=count:
            raise ValueError('Unsupported Rockstar mapping count/root.')
        for i in range(count):
            identity,offset,unknown,size=struct.unpack_from('>4I',raw,m+header+i*16)
            # GTA V offsets include the PSIN header, matching CodeWalker.
            # RDR2 mappings are not used to infer writable field semantics.
            if offset<8 or offset>parts[b'PSIN'][1] or size>parts[b'PSIN'][1]-offset:
                raise ValueError('Rockstar mapping points outside PSIN.')
            self.blocks.append((identity,start+offset,size))
        s,length=parts[b'PSCH']
        if length<12:raise ValueError('Truncated Rockstar schema header.')
        count=u32(raw,s+8)
        if count>4096 or 12+count*8>length:raise ValueError('Unsupported Rockstar schema index.')
        for i in range(count):
            identity,offset=struct.unpack_from('>2I',raw,s+12+i*8)
            if offset<12+count*8 or offset>length-12:raise ValueError('Rockstar schema definition is out of bounds.')
            at=s+offset;descriptor,size=struct.unpack_from('>2I',raw,at)
            if descriptor>>24:continue
            fields=descriptor&0xffff
            if fields>2048 or 12+fields*12>length-offset:raise ValueError('Rockstar schema fields are out of bounds.')
            if identity in self.structures:raise ValueError('Duplicate Rockstar structure definition.')
            self.structures[identity]=(size,tuple(struct.unpack_from('>IBBHI',raw,at+12+j*12) for j in range(fields)))


class RockstarContainer:
    def __init__(self,raw,game):
        self.raw,self.game=bytes(raw),game;self.start,version,magic=LAYOUTS[game]
        if len(raw)<=self.start+32 or len(raw)>64*1024*1024 or (len(raw)-self.start)%16 or u32(raw,0)!=version:
            raise ValueError('Not a supported Rockstar PC Story Mode save envelope.')
        self.encrypted=raw[self.start:self.start+4]!=magic
        self.plain=bytes(raw[:self.start])+(aes(raw[self.start:],True) if self.encrypted else bytes(raw[self.start:]))
        if self.plain[self.start:self.start+4]!=magic:raise ValueError('The file does not decode to the selected Rockstar PC story format.')
        self.checks=[];self.frames=[];self.warnings=[];at=self.start;last=self.start
        while (at:=self.plain.find(b'CHKS\0\0\0\x14',at))>=0:
            if at+20>len(raw):raise ValueError('Truncated Rockstar checksum record.')
            length,stored=struct.unpack_from('>2I',self.plain,at+8);begin=at+20-length
            if length<20 or begin<last or begin<self.start or begin>at or len(self.checks)>=64:
                raise ValueError('Invalid or overlapping Rockstar checksum region.')
            sample=bytearray(self.plain[begin:at+20]);sample[-12:-4]=bytes(8)
            if checksum(sample)!=stored:self.warnings.append('A Rockstar payload checksum does not match. Integrity repair does not prove the saved data is intact.')
            self.checks.append((begin,at));self.frames.append(PsoFrame(self.plain,begin,at))
            at+=20;last=at
        if not self.checks or game=='gtav' and (len(self.checks)!=1 or self.checks[0][0]!=self.start):
            raise ValueError('Unsupported Rockstar checksum/frame layout.')
        if game=='rdr2' and self.checks[0][0]<=self.start+4:raise ValueError('Unsupported RSAV frame directory.')
        if u32(raw,self.header_checksum_offset)!=self.header_checksum():
            self.warnings.append('The Rockstar header checksum does not match. Review the original save before enabling integrity repair.')

    @property
    def header_checksum_offset(self):return 0x104 if self.game=='gtav' else 0x10c

    def header_checksum(self):
        seed=checksum(self.raw[:4][::-1],0)
        data=self.raw[4:0x104] if self.game=='gtav' else self.raw[0x104:0x108][::-1]+self.raw[0x108:0x10c][::-1]
        return checksum(data,seed)

    def encode(self,plain):
        if len(plain)!=len(self.plain):raise ValueError('Rockstar save length cannot change.')
        result=bytearray(plain)
        struct.pack_into('>I',result,self.header_checksum_offset,self.header_checksum())
        for begin,at in self.checks:
            sample=bytearray(result[begin:at+20]);sample[-12:-4]=bytes(8)
            struct.pack_into('>I',result,at+12,checksum(sample))
        if self.encrypted:result[self.start:]=aes(result[self.start:],False)
        return bytes(result)

    def replace_root_blocks(self,replacements):
        """Internal structural growth; callers must verify acquisition semantics."""
        from rdr2_pso import replace_root_blocks
        return replace_root_blocks(self,replacements)

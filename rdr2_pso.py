"""Bounded RDR2 RSAV/PSO block growth for future inventory acquisition.

SPDX-License-Identifier: GPL-3.0-or-later
Structural support only: this module does not invent item GUIDs or unlocks.
"""
import struct
from rockstar_container import RockstarContainer,aes,checksum,u32

MAX_FILE=64*1024*1024


def pointer(block,offset=0):
    if type(block) is not int or type(offset) is not int or not 1<=block<=4095 or not 0<=offset<1<<44:
        raise ValueError('Unsupported RDR2 block pointer.')
    return struct.pack('>I',block|((offset&4095)<<20))+struct.pack('<I',offset>>12)


class RsavDirectory:
    def __init__(self,container):
        raw=container.plain;start=container.start;self.entries=[]
        if container.game!='rdr2' or raw[start:start+4]!=b'RSAV' or len(raw)-start<32:
            raise ValueError('RDR2 block growth requires a recognized RSAV directory.')
        version,offset,length,count=struct.unpack_from('<4I',raw,start+4)
        if version!=3 or not 0<=count<=64 or 20+count*16>offset or offset%16 or offset>len(raw)-start-16:
            raise ValueError('Unsupported RDR2 RSAV directory version/count.')
        if len(container.frames)!=count+1:raise ValueError('RDR2 directory/frame counts disagree.')
        requests=[(None,offset,length)]
        for n in range(count):
            slot=start+20+n*16
            identity,reserved,offset,length=struct.unpack_from('<4I',raw,slot)
            if reserved:raise ValueError('Unsupported RDR2 directory entry flags.')
            requests.append((slot+8,offset,length))
        previous=None
        for n,((slot,offset,length),frame) in enumerate(zip(requests,container.frames)):
            begin=start+offset;payload=begin+16;end=payload+length
            if offset%16 or length%16 or length<16 or end+16>len(raw) or previous is not None and begin!=previous:
                raise ValueError('RDR2 directory chunks overlap or exceed the file.')
            tag=b'CODE' if n==0 else f'S{n-1:03d}'.encode('ascii')
            ending=b'ENDC' if n==0 else b'ENDS'
            if raw[begin:payload]!=tag+bytes(12) or raw[end:end+16]!=ending+bytes(12):
                raise ValueError('Unsupported RDR2 chunk boundary markers.')
            if frame.start!=payload or not 0<=end-frame.end-20<16:
                raise ValueError('RDR2 directory length does not match its PSO frame.')
            self.entries.append((slot,begin,payload,end));previous=end+16
        if previous!=len(raw):raise ValueError('Unrecognized trailing RDR2 directory data.')


def replace_root_blocks(container,replacements):
    """Relocate mapped CODE blocks, retaining block IDs, old bytes and scripts.

    Callers must separately prove game semantics and update typed references.
    This API is not an item-grant action and refuses shrinking mapped blocks.
    """
    if not replacements:return container.raw
    if container.warnings:raise ValueError('Repair and verify original integrity before growing RDR2 data.')
    directory=RsavDirectory(container);raw=container.plain;frame=container.frames[0]
    normalized={}
    for block,value in replacements.items():
        if type(block) is not int or not 1<=block<=len(frame.blocks) or not isinstance(value,(bytes,bytearray)):
            raise ValueError('Unknown RDR2 block replacement.')
        identity,at,length=frame.blocks[block-1];value=bytes(value)
        stride=frame.structures.get(identity,(0,()))[0] or {0:1,2:1,4:2,5:4,6:4,7:4,11:4,12:8,31:8}.get(identity)
        if not stride or not length<=len(value)<=16*1024*1024 or len(value)%stride:
            raise ValueError('RDR2 block growth has an unsupported type, size or stride.')
        if value!=raw[at:at+length]:normalized[block]=value
    if not normalized:return container.raw
    old_size=u32(raw,frame.start+4);map_at=frame.start+old_size;map_size=u32(raw,map_at+4)
    mapping=bytearray(raw[map_at:map_at+map_size]);header=16 if struct.unpack_from('>H',mapping,12)[0] else 24
    data=bytearray(raw[frame.start:map_at])
    for block,value in sorted(normalized.items()):
        data.extend(bytes((-len(data))%16));offset=len(data);data.extend(value)
        struct.pack_into('>I',mapping,header+(block-1)*16+4,offset)
        struct.pack_into('>I',mapping,header+(block-1)*16+12,len(value))
    # Keep the original PSIN size modulo 16 so later AES chunks and original
    # checksum padding remain aligned without normalizing any old padding.
    data.extend(bytes((old_size-len(data))%16));delta=len(data)-old_size
    if delta<=0 or len(raw)+delta>MAX_FILE:raise ValueError('RDR2 block growth exceeds the file limit.')
    struct.pack_into('>I',data,4,len(data))
    body=bytes(data)+bytes(mapping)+raw[map_at+map_size:frame.end]
    check=bytearray(raw[frame.end:frame.end+20])
    struct.pack_into('>I',check,8,len(body)+20)
    sample=body+check[:8]+bytes(8)+check[16:]
    struct.pack_into('>I',check,12,checksum(sample))
    _,begin,payload,end=directory.entries[0]
    code=body+bytes(check)+raw[frame.end+20:end]
    result=bytearray(raw[:payload]+code+raw[end:])
    struct.pack_into('<I',result,container.start+12,end-payload+delta)
    for slot,begin,payload,end in directory.entries[1:]:
        struct.pack_into('<I',result,slot,begin-container.start+delta)
    if container.encrypted:result[container.start:]=aes(result[container.start:],False)
    result=bytes(result);after=RockstarContainer(result,'rdr2');new_directory=RsavDirectory(after)
    if after.warnings:raise ValueError('RDR2 growth failed integrity verification.')
    for n,((slot,begin,payload,end),(ns,nb,np,ne)) in enumerate(zip(directory.entries,new_directory.entries)):
        if n and raw[begin:end+16]!=after.plain[nb:ne+16]:raise ValueError('RDR2 growth changed an unrelated script.')
    for n,((h,at,length),(nh,nat,nlength)) in enumerate(zip(frame.blocks,after.frames[0].blocks),1):
        expected=normalized.get(n,raw[at:at+length])
        if nh!=h or after.plain[nat:nat+nlength]!=expected:raise ValueError('RDR2 growth failed mapped-block verification.')
    return result

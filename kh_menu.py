"""Identified KH1 PC menu snapshots, bounded by the archive directory.

GPL-3.0-or-later. Layout cross-checked with KatRewrites/kh1-save-editor
and original public/local PC bytes. Unknown summary members are preserved.
"""
import re
import struct

def menu_snapshot(raw,table,index,record,end):
    if index>=199:return None
    current=bytes(table[index*0x158:index*0x158+64]).split(b'\0')[0]
    match=re.fullmatch(rb'BISLPS-25198-(\d{2})',current)
    following=bytes(table[(index+1)*0x158:(index+1)*0x158+64]).split(b'\0')[0]
    size=struct.unpack_from('<I',table,(index+1)*0x158+0x50)[0]
    start=record+0x16c40
    if not match or following!=b'-'+match[1]+b'/system.bin' or size!=0x400:return None
    if start+size>end or raw[start:start+4]!=b'KHSQ':return None
    return start

def synchronize(result,snapshots,changes):
    for (slot,key),value in changes.items():
        start=snapshots.get(slot)
        if start is None:continue
        if key=='0:level':result[start+8]=value
        elif key=='difficulty':result[start+0x38]=value

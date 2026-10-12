"""Bounded native item registry updates; no opaque tail reconstruction.

Independent implementation of native facts cross-checked with SaveForge.
SPDX-License-Identifier: GPL-3.0-or-later
"""
import struct

def registry_records(raw,offset):
    if offset<0 or offset+8>len(raw):raise ValueError('The Elden Ring item registry header is out of bounds.')
    count,unknown=struct.unpack_from('<2I',raw,offset)
    if count>7000 or unknown or offset+8+count*8>len(raw):
        raise ValueError('Unsupported Elden Ring item registry header. Item additions and weapon upgrades cannot be applied to this variant.')
    return [struct.unpack_from('<2I',raw,offset+8+i*8) for i in range(count)]

def register_item(result,offset,identifier):
    records=registry_records(result,offset)
    if any(key==identifier for key,flag in records):return
    if len(records)>=7000:raise ValueError('The Elden Ring item registry is full.')
    # Preserve the legacy prefix and high-bit Ashes of War. Insert only in the
    # final ascending ordinary segment, as native acquisition does.
    end=next((i for i,(key,_) in enumerate(records) if key>>28==8),len(records))
    start=0
    for i in range(1,end):
        if records[i-1][0]>records[i][0]:start=i
    index=next((i for i in range(start,end) if records[i][0]>=identifier),end)
    records.insert(index,(identifier,1))
    result[offset+8:offset+8+len(records)*8]=b''.join(struct.pack('<2I',*entry) for entry in records)
    struct.pack_into('<I',result,offset,len(records))

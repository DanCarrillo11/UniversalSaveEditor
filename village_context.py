"""Exact Village inventory/profile contexts, independent of SDK assets.

SPDX-License-Identifier: GPL-3.0-or-later
Factual owners/properties: kvasszn/ree-save-editor. See docs/RE8_FORMAT.md.
"""
from collections import defaultdict
import struct
from re_hashes import murmur32

ITEM=0x10b5eaa5
INVENTORY=0x3a83076c
INVENTORY_UNIT=0x0431bf51
CP=0xe94db9b8
CP_UNIT=0xf033f1ce
HASH=murmur32(b'Hash')
WORK=murmur32(b'work')
UNITS=murmur32(b'Units')

class VillageContext:
    def __init__(self,nodes,data):
        self.data=data;self.identities=defaultdict(list)
        for node in nodes:
            if node.kind!=8 or node.fmt!='<I' or node.size!=4:continue
            if (node.owner,node.field) in ((ITEM,murmur32(b'ItemID')),(CP_UNIT,HASH)):
                self.identities[node.owner,node.path[:-1]].append(node)

    def identity(self,node):
        candidates=self.identities.get((node.owner,node.path[:-1]),[])
        if len(candidates)!=1:return None
        value=struct.unpack_from('<I',self.data,candidates[0].offset)[0]
        return value if value else None

    def is_inventory_item(self,node):
        return (node.owner==ITEM and len(node.path)>=2 and
                node.path[-2][:2]==(INVENTORY_UNIT,WORK) and
                any(owner==INVENTORY for owner,field,index in node.path[:-2]) and
                self.identity(node) is not None)

    def is_extra_content(self,node):
        return (node.owner==CP_UNIT and any((owner,field)==(CP,UNITS) for owner,field,index in node.path[:-1]) and
                self.identity(node) is not None)

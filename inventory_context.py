"""Read-only RE Engine item identities from exact serialized object contexts.

SPDX-License-Identifier: GPL-3.0-or-later
Factual property/owner IDs: kvasszn/ree-save-editor. No SDK assets bundled.
"""
from collections import defaultdict
import struct
import re
from re_hashes import murmur32


class InventoryContext:
    def __init__(self,nodes,data):
        self.data=data;self.direct=defaultdict(list);self.remake=defaultdict(list);self.named=defaultdict(list)
        self.capacities=defaultdict(list)
        for node in nodes:
            if node.owner==0x004b7a76 and node.field==murmur32(b'VirtualStackableCountMax'):
                self.capacities[node.path[:-1]].append(node)
            if node.owner==0x5e10ebe4 and node.field==murmur32(b'ItemDataID') and node.kind==15:
                self.named[node.path[:-1]].append(node)
            if node.fmt not in ('<i','<I') or node.size!=4:continue
            if node.owner in (0x2675722d,0xd759bf3d) and node.field==murmur32(b'ItemId'):
                self.direct[node.owner,node.path[:-1]].append(node)
            if node.owner==0xa84686d9 and node.field==murmur32(b'_ItemId') and len(node.path)>1:
                parent=node.path[-2]
                if parent[:2]==(0x004b7a76,murmur32(b'Item')):
                    self.remake[node.path[:-2]].append(node)

    def item_id(self,game,node):
        if game=='re7':
            candidates=self.named.get(node.path[:-1],[])
            if len(candidates)!=1 or not 0<candidates[0].size<=320:return None
            candidate=candidates[0]
            try:value=self.data[candidate.offset:candidate.offset+candidate.size].decode('utf-16-le').rstrip('\0')
            except UnicodeDecodeError:return None
            return 'item:'+value if re.fullmatch(r'[A-Za-z0-9_-]{1,150}',value) else None
        candidates=self.remake.get(node.path[:-1],[]) if game=='re4_remake' else self.direct.get((node.owner,node.path[:-1]),[]) if game in ('re2','re3') else []
        if len(candidates)!=1:return None
        candidate=candidates[0];value=struct.unpack_from(candidate.fmt,self.data,candidate.offset)[0]
        return value if 0<value<=0x7fffffff else None

    def quantity_limit(self,game,node,value,maximum):
        """A serialized virtual-stack cap belongs to this exact armoury item."""
        if game!='re4_remake':return maximum,False,''
        caps=self.capacities.get(node.path[:-1],[])
        if not caps:return maximum,False,''
        if len(caps)!=1 or (caps[0].kind,caps[0].fmt,caps[0].size)!=(7,'<i',4):
            return maximum,True,'Ambiguous or unsupported saved stack capacity; quantity is preserved.'
        cap=struct.unpack_from('<i',self.data,caps[0].offset)[0]
        if not 1<=value<=cap<=2147483647:
            return maximum,True,'Inconsistent saved stack capacity; quantity is preserved.'
        return cap,cap==1,f'This record’s saved virtual-stack capacity is {cap}. Capacity, item state and equipment are preserved.'

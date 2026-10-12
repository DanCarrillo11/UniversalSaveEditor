"""Read-only RE Engine item identities from exact serialized object contexts.

SPDX-License-Identifier: GPL-3.0-or-later
Factual property/owner IDs: kvasszn/ree-save-editor. No SDK assets bundled.
"""
from collections import defaultdict
import struct
from re_hashes import murmur32


class InventoryContext:
    def __init__(self,nodes,data):
        self.data=data;self.direct=defaultdict(list);self.remake=defaultdict(list)
        for node in nodes:
            if node.fmt not in ('<i','<I') or node.size!=4:continue
            if node.owner in (0x2675722d,0xd759bf3d) and node.field==murmur32(b'ItemId'):
                self.direct[node.owner,node.path[:-1]].append(node)
            if node.owner==0xa84686d9 and node.field==murmur32(b'_ItemId') and len(node.path)>1:
                parent=node.path[-2]
                if parent[:2]==(0x004b7a76,murmur32(b'Item')):
                    self.remake[node.path[:-2]].append(node)

    def item_id(self,game,node):
        candidates=self.remake.get(node.path[:-1],[]) if game=='re4_remake' else self.direct.get((node.owner,node.path[:-1]),[]) if game in ('re2','re3') else []
        if len(candidates)!=1:return None
        candidate=candidates[0];value=struct.unpack_from(candidate.fmt,self.data,candidate.offset)[0]
        return value if 0<value<=0x7fffffff else None

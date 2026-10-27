"""Named Requiem difficulty in a recognized lazy-ID gameplay record.

SPDX-License-Identifier: GPL-3.0-or-later
Schema/hash facts: kvasszn/ree-save-editor. Difficulty-name facts:
Namsku/re-engine-trainer, pinned in SOURCES.md. No upstream code is bundled.
"""
import struct
from requiem_context import h

OWNER=0xda736ae5
WRAPPER=0xe137773c
HASHES=(3326958550,1449966879,203173698,1155280123)
LABELS=('Casual','Standard (Modern)','Standard (Classic)','Insanity')


class RequiemDifficulty:
    def __init__(self,context,Field):
        self.fields=[];self.operations={}
        records=[(path,nodes) for (owner,path),nodes in context.records.items() if owner==OWNER]
        # A second gameplay-difficulty object can be a backup/scenario variant.
        # Only the single current root object has a verified interpretation.
        if len(records)!=1:return
        path,nodes=records[0]
        root=(len(path)==1 and path[0][0]==0)
        wrapped=(len(path)==2 and path[0][0]==0 and path[1][:2]==(WRAPPER,h('_Data')))
        if not (root or wrapped):return
        cache=context.one(nodes,OWNER,'DifficultyIDValue','<i')
        identity=context.one(nodes,OWNER,'DifficultyIDNameHash','<I')
        if not cache or not identity or cache.size!=4 or identity.size!=4:return
        # Native references use -1: the engine resolves the identity by its hash.
        # Other cache representations are deliberately left untouched.
        if context.value(cache)!=-1 or context.value(identity) not in HASHES:return
        key=f're9:difficulty:{identity.offset}'
        self.operations[key]=identity.offset
        self.fields.append(Field(key,'Difficulty',HASHES.index(context.value(identity)),
            identity.offset,'',0,3,'Difficulty',choices=LABELS,
            note='Changes the saved difficulty identity. Adaptive rank, clear records, rewards and difficulty unlocks are preserved. In-game verification is pending.'))

    def patch(self,result,changes):
        for key,offset in self.operations.items():
            if key in changes:struct.pack_into('<I',result,offset,HASHES[changes[key]])

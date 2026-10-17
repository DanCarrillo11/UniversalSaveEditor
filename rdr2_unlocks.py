"""Existing RDR2 Story Mode catalog unlock actions, independent of inventory.

SPDX-License-Identifier: GPL-3.0-or-later
Only the visibility/custom-unlock bits demonstrated by the reference editor
are set. No entry, item, ownership GUID or campaign progress is fabricated.
"""
from collections import Counter
import struct
from rockstar_container import u32
from rdr2_features import parser_hash,member,labels,item_name


def category(name):
    if name.startswith('CLOTHING_') and '_SATCHEL_' in name:return 'Satchels'
    for prefix,title in (
        ('WEAPON_','Weapons'),('CLOTHING_','Clothing'),
        ('COMPONENT_','Weapon components'),('HORSE_EQUIPMENT_','Horse equipment'),
        ('HORSE_BREED_','Horse breeds'),('AMMO_','Ammunition'),
    ):
        if name.startswith(prefix):return title
    return None


class UnlockFields:
    def __init__(self,features):
        self.f=features;self.positions={};raw=features.raw
        roots=features.rows('CUnlockSaveStructureSP',(('UnlockItemList',13,0),
            ('UnlockSaveDataVersion',6,0),('UnlockXmlVersion',6,0)))
        if len(roots)!=1:return
        frame,base,m=roots[0]
        # These are the Story Mode versions observed in all native samples.
        if frame is not features.c.frames[0] or any(u32(raw,m[n])!=0 for n in ('UnlockSaveDataVersion','UnlockXmlVersion')):return
        identity=parser_hash('SUnlockInfo');schema=frame.structures.get(identity)
        name=member(frame,identity,'Hash',11,11);packed=member(frame,identity,'PackedData',2)
        if not schema or schema[0]!=8 or not name or not packed or name[0]!=0 or packed[0]!=4:return
        count,capacity=struct.unpack_from('>HH',raw,m['UnlockItemList']+8)
        if not 0<count<=capacity<=8192:return
        try:target,at,left=features.pointer(frame,m['UnlockItemList'],count*8)
        except (ValueError,struct.error):return
        block=frame.blocks[(u32(raw,m['UnlockItemList'])&4095)-1]
        if target!=identity or block[2]%8 or (at-block[1])%8:return
        rows=[(u32(raw,at+n*8),at+n*8+4) for n in range(count)]
        counts=Counter(h for h,off in rows)
        for h,off in rows:
            title=labels().get(f'{h:08x}','');collection=category(title)
            if counts[h]!=1 or not collection:continue
            key=f'unlock:{h:08x}:apply';done=int(raw[off]&7==7)
            self.positions[key]=off;features.positions[key]=off
            features.fields.append(features.Field(key,item_name(h),done,off,'',0,1,'Unlocks',
                boolean=True,readonly=bool(done),collection=collection,
                note='Apply this catalog unlock. This does not add, buy or equip the item, or create a horse. Story and recipe requirements can still apply. Already-applied actions are read-only. In-game loading has not been verified.'))

    def patch(self,plain,changes):
        for key,value in changes.items():
            if key not in self.positions:continue
            if value!=1:raise ValueError('Catalog unlock is an apply action; it cannot restore a previous unlock state.')
            plain[self.positions[key]]|=7

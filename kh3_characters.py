"""Preserving KH3 party equipment/ability operations.

GPL-3.0-or-later. Layout/flag facts adapted from Kingdom Save Editor;
Copyright (C) 2020 Luciano Ciccariello. See SOURCES.md.
"""
import struct
from collections import Counter
from kh_feature_tables import KH3_EQUIPMENT,KH3_ABILITY_NAMES
from kh_extra_tables import KH3_ITEMS

CHARACTERS=('Sora','Donald','Goofy','Hercules','Woody','Buzz','Rapunzel','Flynn','Sulley','Mike','Marshmallow','Baymax','Jack','Riku','Mickey')

class Kh3CharacterFeatures:
    def __init__(self,plain,Field):
        self.plain=plain;self.fields=[];self.equipment={};self.abilities={};self.active_weapons={}
        counts=Counter(KH3_ITEMS.values())
        self.inventory_by_name={(name,group):i for i,(name,group) in KH3_ITEMS.items() if counts[name,group]==1}
        # Inventory enum blocks begin at Weapon=25, Armor=125, Accessory=225.
        # Require the corresponding known name too; do not choose a medal's
        # arbitrary duplicate label as its acquisition record.
        self.equipment_inventory={}
        for kind,shift in (('Weapon',24),('Armor',124),('Accessory',224),('Consumable',0)):
            for identifier,(title,category) in KH3_EQUIPMENT[kind].items():
                candidate=identifier+shift;entry=KH3_ITEMS.get(candidate)
                if entry and entry[0].replace(' ','').casefold()==title.replace(' ','').casefold():
                    self.equipment_inventory[kind,identifier]=candidate
        for character,name in enumerate(CHARACTERS):
            base=0x1880+character*0x9c0
            # World companions are edited only when their saved record is populated.
            if character>=3 and struct.unpack_from('<i',plain,base+0x984)[0]<=0:continue
            if character<3 and plain[base+6]<=2:
                key=f'character:{name}:active_weapon'
                self.fields.append(Field(key,'Active weapon slot',plain[base+6],base+6,'<B',0,2,'Equipment',choices=('Weapon 1','Weapon 2','Weapon 3')))
                self.active_weapons[key]=base
            for kind,delta,count,item_type,inventory_group in (('Weapon',0x80,3,3,'Weapons'),
                ('Armor',0x98,8,4,'Equipment'),('Accessory',0xd8,8,5,'Equipment'),('Consumable',0x118,8,0,'Items')):
                options={0:'Empty'}
                for identifier,(title,category) in KH3_EQUIPMENT[kind].items():
                    if kind=='Weapon':
                        if character<3 and category!=('Keyblade','Staff','Shield')[character]:continue
                        if character>=3:continue # retain world-specific weapons
                    options[identifier]=title
                for index in range(count):
                    offset=base+delta+index*8;identifier,type_id=plain[offset:offset+2];enabled=plain[offset+4]
                    if enabled not in (0,1):continue
                    if identifier and type_id not in ((0,1) if kind=='Consumable' else (item_type,)):continue
                    current_options=dict(options)
                    if identifier not in current_options:
                        current_options[identifier]=KH3_EQUIPMENT[kind].get(identifier,(f'Saved ID {identifier}',))[0]
                    values=tuple(current_options);key=f'character:{name}:equipment:{kind.lower()}:{index}'
                    readonly=bool(identifier not in options)
                    self.fields.append(Field(key,f'{kind} {index+1}',values.index(identifier),offset,'',0,len(values)-1,'Equipment',
                        choices=tuple(current_options[v] for v in values),readonly=readonly,
                        note='Saved equipment entry. Selecting a mapped item enables the entry and grants its inventory acquisition flag/count when mapped. AP, derived stats and world/story availability are not recalculated.'))
                    if not readonly:self.equipment[key]=(offset,values,current_options,item_type,inventory_group,base,kind,index)
            for identifier,(title,category) in KH3_ABILITY_NAMES.items():
                if not 0<identifier<512:continue
                offset=base+0x160+identifier*4;word=struct.unpack_from('<I',plain,offset)[0]
                bits=word&3
                key=f'character:{name}:ability:{identifier}'
                choices=('Not learned','Learned · Unequipped','Learned · Equipped')
                if bits==2:
                    self.fields.append(Field(key,title,0,offset,'',0,0,'Abilities',choices=('Existing inconsistent flags (preserved)',),readonly=True,
                        note='Equipped without the acquisition flag. No automatic correction of an unverified existing representation.'))
                    continue
                value=(0,1,3).index(bits)
                self.fields.append(Field(key,title,value,offset,'',0,2,'Abilities',choices=choices,
                    note='Synchronizes learned/equipped bits and preserves unseen/reserved flags. AP costs, character-specific actions and story dependencies are not recalculated.'))
                self.abilities[key]=offset

    def patch(self,result,changes):
        changed_weapons=set()
        for key,value in changes.items():
            if key in self.active_weapons:changed_weapons.add(self.active_weapons[key])
            if key in self.abilities:
                offset=self.abilities[key];word=struct.unpack_from('<I',result,offset)[0]
                struct.pack_into('<I',result,offset,(word&~3)|(0,1,3)[value])
            elif key in self.equipment:
                offset,values,options,type_id,group,base,kind,index=self.equipment[key]
                identifier=values[value];result[offset]=identifier
                if identifier:
                    result[offset+1]=type_id;result[offset+4]=1
                    item=self.equipment_inventory.get((kind,identifier))
                    if item is not None:
                        if changes.get(f'inventory:{item}',1)<1:
                            raise ValueError('An equipped item must have a positive inventory quantity. Remove the conflicting inventory edit or choose another item.')
                        amount=0x8f4+item*2
                        result[amount]=max(1,result[amount]);result[amount+1]|=1
                if kind=='Weapon':changed_weapons.add(base)
        for base in changed_weapons:
            active=result[base+6]
            if active>2 or result[base+0x80+active*8]==0 or result[base+0x84+active*8]!=1:
                raise ValueError('The active weapon slot must contain an enabled weapon. Select a weapon for that slot before applying.')

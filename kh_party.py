"""Bounded party equipment and ability lists for the supported PC archives.

Format facts/names adapted from KingdomSaveEditor; see SOURCES.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
import struct
from kh_items import ITEMS
from kh_party_tables import KH1_ABILITIES, KH2_ABILITIES, KH2_EQUIPMENT
from kh2_relationships import Kh2Relationships

KH1_CHARACTERS=('Sora','Donald','Goofy','Tarzan','Pooh','Aladdin','Ariel','Jack Skellington','Peter Pan','Beast')
KH2_CHARACTERS=('Sora','Donald','Goofy','Mickey','Auron','Mulan','Aladdin','Jack Sparrow','Beast','Jack Skellington','Simba','Tron','Riku')


class PartyEditor:
    def __init__(self,raw,game,field_type):
        self.raw,self.game,self.field_type=raw,game,field_type
        self.encodings={}
        self.bits={}
        self.shortcuts={}
        self.kh2=Kh2Relationships(raw,field_type,KH2_CHARACTERS) if game=='kh2' else None

    def shared(self,fields,slot,record):
        if self.game!='kh1':return
        options={0:'Empty',0x80:'Empty (saved flag)'}
        for identifier,label in ((1,'High Jump'),(2,'Mermaid Kick'),(3,'Glide'),(4,'Superglide')):
            options[identifier]=label+' · Equipped';options[identifier|0x80]=label+' · Unequipped'
        for index in range(4):
            self.choice(fields,slot,f'shared_ability:{index}',f'Shared entry {index+1}',record+0x599+index,'<B',options,'Shared abilities',
                'Changes a known shared movement ability and its enabled state. Unknown identities, character-specific abilities and story flags are preserved.')
        spells=('Fire','Blizzard','Thunder','Cure','Gravity','Stop','Aero')
        options={i:n for i,n in enumerate(spells)};options[255]='Empty'
        for index,button in enumerate(('Circle','Triangle','Square')):
            key='magic_shortcut:'+str(index)
            self.choice(fields,slot,key,button,record+0x844+index,'<B',options,'Magic shortcuts',
                        'Choose a magic family available to Sora. Disabling its availability clears matching shortcuts. Spell tiers, inventory and story rewards are preserved.')
            if (slot,key) in self.encodings:self.shortcuts[slot,key]=(record+0x74,record+0x844+index)

    def game_settings(self,fields,slot,record):
        if self.game!='kh2':return
        for delta,bit,key,label in ((0x41a4,0,'vibration','Controller vibration'),
                (0x41a4,3,'navigation_map','Navigation map'),
                (0x41a4,4,'manual_camera','Manual field camera'),
                (0x41a4,5,'stick_commands','Right stick controls command menu'),
                (0x41a4,6,'classic_menu','Classic command menu'),
                (0x41a4,7,'invert_horizontal','Reverse horizontal camera'),
                (0x41a5,0,'invert_vertical','Reverse vertical camera')):
            key='setting:'+key;offset=record+delta
            fields.append(self.field_type(key,label,(self.raw[offset]>>bit)&1,offset,'',0,1,
                'Game settings',boolean=True,
                note='Changes this slot’s documented saved option only. Other option bits, controls configured outside this save, progression and equipment are preserved.'))
            self.bits[slot,key]=(offset,bit)

    def companion_ai(self,fields,slot,record,character):
        if self.game!='kh2' or character not in (1,2):return
        base=record+0x24f0+character*0x114;name=KH2_CHARACTERS[character]
        self.choice(fields,slot,f'character:{character}:ai:combat',name+' · Combat style',base+244,'<B',
            dict(enumerate(('Technic Attack','Target Attack','Huddle Attack','Party Attack','Sora Attack','Relentless Attack'))),
            'Companion AI','Saved companion combat behavior only. Equipment, abilities, stats, story and world variants are preserved.')
        for index in range(4):
            self.choice(fields,slot,f'character:{character}:ai:ability:{index}',f'{name} · Ability-use setting {index+1}',base+245+index,'<B',
                {0:'Free',1:'Well-balanced',2:'Rare'},'Companion AI',
                'Changes an existing ability-use preference. The underlying ability identity/order and its acquisition are preserved.')

    def choice(self,fields,slot,key,label,offset,fmt,options,group,note=''):
        original=struct.unpack_from(fmt,self.raw,offset)[0]
        # Unknown identities are displayed but cannot be overwritten by a guess.
        if original not in options:
            fields.append(self.field_type(key,label,original,offset,fmt,0,65535,group,readonly=True,
                note=f'Unidentified saved ID {original}. This entry is preserved.'))
            return
        values=tuple(options)
        self.encodings[slot,key]=(offset,fmt,values)
        fields.append(self.field_type(key,label,values.index(original),offset,'',0,len(values)-1,group,
            choices=tuple(options[v] for v in values),note=note,
            art_choices=values if group=='Equipment' else ()))

    def abilities(self,fields,slot,prefix,label,base,count,fmt,names,inactive_bit):
        size=struct.calcsize(fmt)
        # Show existing entries plus a single empty entry for adding a new ability.
        # Hidden unused bytes and their order are never rewritten.
        empty_added=False
        options={0:'Empty'}
        for identifier,name in names.items():
            enabled=identifier if self.game=='kh1' else identifier|inactive_bit
            disabled=identifier|inactive_bit if self.game=='kh1' else identifier
            options[disabled]=name+' · Unequipped'
            options[enabled]=name+' · Equipped'
        for index in range(count):
            offset=base+index*size;original=struct.unpack_from(fmt,self.raw,offset)[0]
            if original & ~inactive_bit==0:
                if empty_added:continue
                empty_added=True
                # 0x80 (KH1) / 0x8000 (KH2) empty flags are retained as a choice.
                if original:options[original]='Empty (saved flag)'
            self.choice(fields,slot,f'{prefix}:ability:{index}',f'{label} · Ability entry {index+1}',offset,fmt,options,'Abilities',
                ('Choose a known ability and its equipped state. Standard AP budgets are checked for recognized character data; duplicate entries and unknown data are preserved. Apply to expose the next empty entry.'
                 if self.game=='kh2' else 'Choose a known ability and its equipped state. Duplicate entries are retained; AP costs and character-specific behavior are not recalculated. Apply to expose the next empty entry.'))

    def character(self,fields,slot,record,character):
        kh1=self.game=='kh1';names=KH1_CHARACTERS if kh1 else KH2_CHARACTERS
        name=names[character];prefix=f'{character}' if kh1 else f'character:{character}'
        base=record+4+character*0x74 if kh1 else record+0x24f0+character*0x114
        if kh1:
            if character==4:return # Pooh is not a combat character.
            if character>=3 and not self.raw[base]:return # Do not enable absent companions.
            fields.append(self.field_type(prefix+':level',name+' · Level',self.raw[base],base,'<B',min(1,self.raw[base]),100,'Attributes',
                note='Level and experience are independent saved values; starting bonuses and story unlocks are not recalculated.'))
            xp=struct.unpack_from('<i',self.raw,base+0x3c)[0]
            if 0<=xp<=99999999:fields.append(self.field_type(prefix+':experience',name+' · Experience',xp,base+0x3c,'<i',0,99999999,'Attributes'))
            if character>=3:
                for delta,key,title,low in ((1,'hp_current','Current HP',0),(2,'hp','Base HP',1),(3,'mp_current','Current MP',0),(4,'mp','Base MP',1),(5,'ap','Base AP',0),(6,'strength','Strength',0),(7,'defense','Defense',0)):
                    fields.append(self.field_type(prefix+':'+key,name+' · '+title,self.raw[base+delta],base+delta,'<B',low,255,'Attributes'))
            equipment={identifier:(title,kind) for identifier,title,kind in ITEMS}
            weapon_kind=('Keyblade','Staff','Shield')[character] if character<3 else None
            weapon=struct.unpack_from('<B',self.raw,base+0x32)[0]
            weapons={identifier:title for identifier,(title,kind) in equipment.items() if kind==weapon_kind}
            if weapon==0:weapons[0]='Empty'
            self.choice(fields,slot,prefix+':weapon',name+' · Weapon',base+0x32,'<B',weapons,'Equipment',
                'Changes the equipped weapon only. Bag quantities, world variants and derived attributes are preserved.')
            for count_offset,array_offset,capacity,kind,title in ((0x18,0x19,8,'Accessory','Accessory'),(0x21,0x22,12,'Consumable','Item')):
                count=self.raw[base+count_offset]
                if count>capacity:continue # Preserve unsupported counts rather than making new slots.
                options={0:'Empty',**{i:t for i,(t,k) in equipment.items() if k==kind}}
                for index in range(count):self.choice(fields,slot,f'{prefix}:{title.lower()}:{index}',f'{name} · {title} {index+1}',base+array_offset+index,'<B',options,'Equipment',
                    'Edits an already unlocked equipment slot. Inventory quantities and slot counts are preserved.')
            self.abilities(fields,slot,prefix,name,base+0x40,48,'<B',KH1_ABILITIES,0x80)
            for bit,spell in enumerate(('Fire','Blizzard','Thunder','Cure','Gravity','Stop','Aero')):
                key=prefix+':magic:'+str(bit);offset=base+0x70
                fields.append(self.field_type(key,spell+' available',(self.raw[offset]>>bit)&1,offset,'',0,1,'Magic',boolean=True,
                    note='Character-specific availability flag. Spell tiers, shortcuts, world events and related acquisition records are preserved.'))
                self.bits[slot,key]=(offset,bit)
        else:
            if character>=3 and not self.raw[base+15]:return
            equipment=KH2_EQUIPMENT
            weapon_kind=('Keyblade','Staff','Shield')[character] if character<3 else 'Weapon'
            weapon=struct.unpack_from('<H',self.raw,base)[0]
            weapons={i:t for i,(t,k) in equipment.items() if k==weapon_kind and 'Unused' not in t}
            if character>=3:weapons={weapon:equipment[weapon][0]} if weapon in equipment else {}
            if not weapon:weapons[0]='Empty'
            self.choice(fields,slot,prefix+':weapon',name+' · Weapon',base,'<H',weapons,'Equipment',
                'Transfers one copy between this weapon slot and the bag. World-specific weapon variants and story records are preserved.')
            for count_offset,array_offset,kind,title in ((16,20,'Armor','Armor'),(17,36,'Accessory','Accessory'),(18,52,'Consumable','Item')):
                count=self.raw[base+count_offset]
                if count>8:continue
                options={0:'Empty',**{i:t for i,(t,k) in equipment.items() if k==kind}}
                for index in range(count):self.choice(fields,slot,f'{prefix}:{title.lower()}:{index}',f'{name} · {title} {index+1}',base+array_offset+index*2,'<H',options,'Equipment',
                    'Transfers one copy between this unlocked slot and the bag. Item auto-reload, slot counts and story records are preserved.')
                if kind=='Consumable':
                    for index in range(count):self.choice(fields,slot,f'{prefix}:auto_reload:{index}',f'{name} · Item {index+1} auto-reload',base+68+index*2,'<H',options,'Equipment',
                        'Changes the saved item auto-reload identity for an existing slot. Does not create stock; only available inventory can be reloaded in the game.')
            self.abilities(fields,slot,prefix,name,base+84,80,'<H',{i:t for i,(t,k) in KH2_ABILITIES.items()},0x8000)
            self.companion_ai(fields,slot,record,character)

    def finish(self,result,changes):
        for key,value in changes.items():
            if key in self.bits:
                offset,bit=self.bits[key];result[offset]=(result[offset]&~(1<<bit))|(value<<bit)
                continue
            if key not in self.encodings:continue
            offset,fmt,values=self.encodings[key]
            struct.pack_into(fmt,result,offset,values[value])
        for (slot,key),(availability,offset) in self.shortcuts.items():
            command=result[offset]
            if command==255:continue
            available=bool(result[availability]&(1<<command))
            if (slot,key) in changes and not available:
                raise ValueError('A KH1 magic shortcut must reference a spell available to Sora.')
            if (slot,f'0:magic:{command}') in changes and not available:
                result[offset]=255
        if self.kh2:result=self.kh2.finish(result,changes)
        return result

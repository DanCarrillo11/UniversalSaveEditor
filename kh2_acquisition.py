"""Known KH2 spell tiers, command shortcuts and acquisition bits.

Format facts cross-check OpenKH item data, KingdomSaveEditor shortcut offsets,
and Archipelago's KH2 item/receiver maps. See SOURCES.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
import struct

MAGIC=(('fire',0x3594,21,('Fire','Fira','Firaga'),(49,119,120)),
       ('blizzard',0x3595,22,('Blizzard','Blizzara','Blizzaga'),(51,121,122)),
       ('thunder',0x3596,23,('Thunder','Thundara','Thundaga'),(50,123,124)),
       ('cure',0x3597,24,('Cure','Cura','Curaga'),(52,125,126)),
       ('magnet',0x35cf,87,('Magnet','Magnera','Magnega'),(174,175,176)),
       ('reflect',0x35d0,88,('Reflect','Reflera','Reflega'),(177,178,179)))
MAGIC_STOCK={offset-0x3580: names[0] for _,offset,_,names,_ in MAGIC}
SUPPLIES=((23,1,'Potion'),(20,2,'Hi-Potion'),(21,3,'Ether'),(22,4,'Elixir'),
          (242,5,'Mega-Potion'),(243,6,'Mega-Ether'),(244,7,'Megalixir'))
FORMS=(('valor','Valor',0x36c0,1,0),('wisdom','Wisdom',0x36c0,2,1),
       ('limit','Limit',0x36ca,3,2),('master','Master',0x36c0,6,3),
       ('final','Final',0x36c0,4,4),('anti','Anti',0x36c0,5,None))
SUMMONS=(('stitch','Stitch',0x36c0,0),('chicken_little','Chicken Little',0x36c0,3),
         ('genie','Genie',0x36c4,4),('peter_pan','Peter Pan',0x36c4,5))


class Kh2Acquisition:
    def __init__(self,raw,field_type):
        self.raw,self.field_type=raw,field_type
        self.records={};self.unlocks={};self.shortcuts={}
        self.commands={command:('magic',n) for n,entry in enumerate(MAGIC) for command in entry[4]}
        self.commands.update({command:('item',item) for command,item,_ in SUPPLIES})
        self.commands[0]=('empty',0)
        self.options=(('empty',0),)+tuple(('magic',n) for n in range(6))+tuple(('item',i) for _,i,_ in SUPPLIES)
        self.labels=('Empty',)+tuple(entry[3][0] for entry in MAGIC)+tuple(n for _,_,n in SUPPLIES)

    def record(self,fields,slot,record):
        self.records[slot]=record
        for key,delta,item,names,_ in MAGIC:
            offset=record+delta;value=self.raw[offset]
            fields.append(self.field_type('character:0:magic:'+key,'Sora · '+names[0],value,offset,'<B',0,
                3 if value<=3 else 255,'Magic',choices=('Not learned',)+names if value<=3 else (),readonly=value>3,
                item_id=item,note='Stored spell tier. Known shortcuts follow tier changes and clear when this family is removed. Story rewards and event flags are preserved.'))
        for index,button in enumerate(('Circle','Triangle','Square','Cross')):
            offset=record+0x36f8+index*2;word=struct.unpack_from('<H',self.raw,offset)[0]
            key='character:0:magic_shortcut:'+str(index)
            if word not in self.commands:
                fields.append(self.field_type(key,'Sora · '+button+' shortcut',word,offset,'<H',0,65535,'Magic',readonly=True,
                    note='Unidentified saved command is preserved.'))
                continue
            self.shortcuts[slot,key]=(offset,self.options.index(self.commands[word]))
            fields.append(self.field_type(key,'Sora · '+button+' shortcut',self.options.index(self.commands[word]),offset,'',0,len(self.options)-1,
                'Magic',choices=self.labels,note='Spell families use their learned tier. Item shortcuts require a copy equipped in Sora’s item slots.'))
        for key,label,delta,bit,form in FORMS:
            self.unlock(fields,slot,record,'form:'+key,label+' Form',delta,bit,'Forms',form)
        for key,label,delta,bit in SUMMONS:
            self.unlock(fields,slot,record,'summon:'+key,label,delta,bit,'Summons')
        for number in range(1,14):
            delta,bit=(0x36c4,number+5) if number<3 else (0x36c5+(number-3)//8,(number-3)%8)
            self.unlock(fields,slot,record,'report:'+str(number),'Secret Ansem Report '+str(number),delta,bit,'Reports')

    def unlock(self,fields,slot,record,key,label,delta,bit,group,form=None):
        offset=record+delta;value=(self.raw[offset]>>bit)&1
        supported=True
        if form is not None:
            base=record+0x32f4+form*56
            supported=self.raw[base+2]<=7
        self.unlocks[slot,key]=(offset,bit,group,form)
        fields.append(self.field_type(key,label+' acquired',value,offset,'',0,1,group,boolean=True,
            readonly=bool(value) or not supported,
            note='Adds this recognized acquisition bit; existing acquisitions cannot be removed. Story, journal completion, rewards and achievements are preserved.'))

    def finish(self,result,changes):
        for slot,record in self.records.items():
            edits={key:value for (i,key),value in changes.items() if i==slot}
            form_added=False;summon_added=False
            for (index,key),(offset,bit,group,form) in self.unlocks.items():
                if index!=slot or key not in edits:continue
                if edits[key]==0:continue
                was_set=bool(self.raw[offset]&(1<<bit))
                result[offset]|=1<<bit
                if was_set:continue
                if group=='Forms' and form is not None:
                    form_added=True;base=record+0x32f4+form*56
                    if result[base+2]==0:
                        if f'form:{form}:level' in edits:raise ValueError('KH2 acquired forms require a positive saved form level.')
                        result[base+2]=1
                if group=='Summons':summon_added=True
            if form_added:
                # The receiver resets this documented one-byte Anti-point counter.
                if edits.get('drive_anti_points',0)!=0:raise ValueError('KH2 new form acquisition resets Anti points to zero. Reset the conflicting Anti-point edit.')
                result[record+0x3410]=0
            if summon_added and result[record+0x3526]==0:
                if 'summon_level' in edits:raise ValueError('KH2 acquired summons require a positive saved summon level.')
                result[record+0x3526]=1
            if 'drive_max' in edits or 'drive_current' in edits:
                current,maximum=record+0x3529,record+0x352a
                if result[current]>result[maximum]:
                    if 'drive_current' in edits:raise ValueError('KH2 current Drive cannot exceed maximum Drive.')
                    result[current]=result[maximum]
            item_slots_changed=any(k.startswith('character:0:item:') for k in edits)
            for (index,key),(offset,_) in self.shortcuts.items():
                if index!=slot:continue
                original=struct.unpack_from('<H',self.raw,offset)[0]
                explicit=key in edits
                kind,which=self.options[edits[key]] if explicit else self.commands[original]
                if kind=='magic':
                    family,delta,_,_,commands=MAGIC[which];level=result[record+delta]
                    if explicit and not 1<=level<=3:raise ValueError('KH2 magic shortcuts require a learned spell family.')
                    if explicit or 'character:0:magic:'+family in edits:
                        command=commands[level-1] if 1<=level<=3 else 0
                        struct.pack_into('<H',result,offset,command)
                elif kind=='item':
                    count=result[record+0x24f0+18]
                    available=count<=8 and any(struct.unpack_from('<H',result,record+0x24f0+52+n*2)[0]==which for n in range(count))
                    if explicit and not available:raise ValueError('KH2 item shortcuts require a copy equipped in Sora’s item slots.')
                    if explicit or item_slots_changed:
                        command=next(c for c,item,_ in SUPPLIES if item==which) if available else 0
                        struct.pack_into('<H',result,offset,command)
                elif explicit:struct.pack_into('<H',result,offset,0)
        return result

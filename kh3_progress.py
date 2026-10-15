"""Known KH3 PC magic, links, shortcut references and minigame records.

GPL-3.0-or-later. PC positions and command IDs adapted from Kingdom Save
Editor, Copyright (C) 2020 Luciano Ciccariello and 2026 Mikko Mäntylä.
Unknown commands, story flags, photographs and reserved data are retained.
"""
import struct

MAGICS=(('Fire',29),('Blizzard',33),('Thunder',37),('Water',41),('Aero',45),('Cure',49))
NAMES={29:'Fire',30:'Fira',31:'Firaga',33:'Blizzard',34:'Blizzara',35:'Blizzaga',
       37:'Thunder',38:'Thundara',39:'Thundaga',41:'Water',42:'Watera',43:'Waterga',
       45:'Aero',46:'Aerora',47:'Aeroga',49:'Cure',50:'Cura',51:'Curaga'}
LINKS={70:'Meow Wow Balloon',71:'8-Bit Blast',72:"King's Flare",73:'Plasma Encounter',74:'Sea Spectacle'}
# CommandType and ConsumableType are distinct native enumerations. Hi-Ether
# appears earlier in the command enum but last in the consumable inventory.
CONSUMABLES={58:('Potion',1),59:('Hi-Potion',2),60:('Mega-Potion',3),61:('Ether',4),
             62:('Hi-Ether',11),63:('Mega-Ether',5),64:('Elixir',6),65:('Megalixir',7),
             66:('Refocuser',8),67:('Hi-Refocuser',9),68:('Panacea',10)}
RECORDS=('Verum Rex high score','Verum Rex timer','Flash Tracer 1 high score','Flash Tracer 2 high score',
         'Flash Tracer 1 timer','Flash Tracer 2 timer','Frozen Slider high score','Frozen Slider timer',
         'Frozen Slider medals','Festival Dance high score','Festival Dance longest chain')

class Kh3Progress:
    def __init__(self,raw,Field):
        self.fields=[];self.operations={};self.magic={};self.links={};self.shortcuts={};self.raw=raw
        def choice(key,label,offset,options,group,note):
            current=struct.unpack_from('<i',raw,offset)[0];known=current in options
            if not known:options={current:f'Existing command ID {current} (preserved)'}
            values=tuple(options)
            self.fields.append(Field(key,label,values.index(current),offset,'',0,len(values)-1,group,
                choices=tuple(options[v] for v in values),readonly=not known,note=note))
            if known:self.operations[key]=(offset,values)
            return current
        def resolve(base,count,families,group):
            saved=[struct.unpack_from('<i',raw,base+i*4)[0] for i in range(count)]
            empty=[i for i,value in enumerate(saved) if value==0];resolved={};known=set()
            for name,allowed in families:
                matches=[i for i,value in enumerate(saved) if value in allowed];known.update(matches)
                if len(matches)==1:resolved[name]=base+matches[0]*4
                elif not matches and empty:resolved[name]=base+empty.pop(0)*4
                else:
                    resolved[name]=None
                    self.fields.append(Field('unavailable:'+group+':'+str(name),str(name),0,-1,'',0,0,group,readonly=True,
                        note='No uniquely identified entry or clean empty slot is available. Duplicate and unknown saved commands are preserved.'))
            for index,value in enumerate(saved):
                if value and index not in known:
                    self.fields.append(Field('unknown:'+group+':'+str(index),f'Entry {index+1} · Command ID {value}',0,-1,'',0,0,group,readonly=True,
                        note='Unknown command identity; preserved without rewriting this entry.'))
            return resolved
        magic_offsets=resolve(0xbf50,6,[(name,set(range(base,base+3))) for name,base in MAGICS],'Magic')
        for name,base in MAGICS:
            key='magic:'+name;offset=magic_offsets[name]
            if offset is None:continue
            choice(key,name,offset,{0:'Not acquired',**{v:NAMES[v] for v in range(base,base+3)}},'Magic',
                'Changes the saved spell tier. Matching known shortcuts synchronize when this tier changes; story rewards and character stats remain unchanged.')
            self.magic[name]=(offset,base)
        link_offsets=resolve(0xbf68,5,[(identifier,{identifier}) for identifier in LINKS],'Links')
        for identifier,name in LINKS.items():
            offset=link_offsets[identifier];key='link:'+str(identifier)
            if offset is None:continue
            choice(key,name,offset,{0:'Not acquired',identifier:'Acquired'},'Links',
                'Changes this saved Link entry. Removing a Link clears its matching known shortcuts; story and installed content remain unchanged.')
            self.links[identifier]=offset
        # Form attacks, sea magic and unknown commands remain protected.
        options={0:'Empty',**NAMES,**LINKS,**{i:name for i,(name,item) in CONSUMABLES.items()}}
        for group in range(3):
            for index,button in enumerate(('Circle','Triangle','Square','Cross')):
                key=f'shortcut:{group}:{index}';offset=0xbf20+(group*4+index)*4
                current=choice(key,f'Set {group+1} · {button}',offset,options,'Shortcuts',
                    'Choose a learned spell, acquired Link or available consumable equipped by Sora. Items are not granted automatically. Known item shortcuts clear if their last available Sora item is explicitly removed; unknown commands remain protected.')
                if key in self.operations:self.shortcuts[key]=(offset,current)
        for index,label in enumerate(RECORDS):
            offset=0x83cd8+index*4;value=struct.unpack_from('<i',raw,offset)[0]
            if not 0<=value<=2147483647:continue
            self.fields.append(Field('record:'+str(index),label,value,offset,'<i',0,2147483647,'Minigame records',
                note='Existing saved record only. Timer units, reward thresholds, mission completion and online rankings are not recalculated.'))
        for index,name in enumerate(('Cherry','Strawberry','Banana','Honeydew','Grape','Watermelon','Orange')):
            for part,label in enumerate(('High score','Secondary high score','Attempts')):
                offset=0x83cd8+44+index*12+part*4;value=struct.unpack_from('<i',raw,offset)[0]
                if not 0<=value<=2147483647:continue
                self.fields.append(Field(f'flan:{index}:{part}',f'{name} Flan · {label}',value,offset,'<i',0,2147483647,'Minigame records',
                    note='Saved Flantastic Seven record only. Does not deliver ingredients, abilities or online achievements.'))
        for key,label,offset,fmt in (('enemies_defeated','Enemies defeated',0x70,'<i'),('save_count','Save count',0x5b8,'<h'),
                                     ('crabs','Crabs collected',0x17ec,'<i')):
            value=struct.unpack_from(fmt,raw,offset)[0];maximum=32767 if fmt=='<h' else 2147483647
            if not 0<=value<=maximum:continue
            self.fields.append(Field(key,label,value,offset,fmt,0,maximum,'Statistics',note='Saved counter only; reward and story dependencies are preserved.'))

    def patch(self,result,changes):
        for key,value in changes.items():
            if key in self.operations:
                offset,values=self.operations[key];struct.pack_into('<i',result,offset,values[value])
        # Tier changes synchronize only recognized original shortcuts. Explicit
        # shortcut edits win, but must pass the learned-command check below.
        for key,(offset,current) in self.shortcuts.items():
            if key in changes:continue
            family=next((name for name,base in MAGICS if base<=current<base+3),None)
            if family in self.magic and 'magic:'+family in changes:
                struct.pack_into('<i',result,offset,struct.unpack_from('<i',result,self.magic[family][0])[0])
            if current in self.links and 'link:'+str(current) in changes and not struct.unpack_from('<i',result,self.links[current])[0]:
                struct.pack_into('<i',result,offset,0)
            if current in CONSUMABLES:
                item=CONSUMABLES[current][1]
                relevant=(f'inventory:{item}' in changes or any(k.startswith('character:Sora:equipment:consumable:') for k in changes))
                if relevant and not self.item_available(result,item):struct.pack_into('<i',result,offset,0)
        for key in changes:
            if key not in self.shortcuts:continue
            offset,_=self.shortcuts[key];value=struct.unpack_from('<i',result,offset)[0]
            if not value:continue
            if value in CONSUMABLES:
                if not self.item_available(result,CONSUMABLES[value][1]):
                    raise ValueError('An item shortcut requires a positive acquired inventory quantity and an enabled matching Sora consumable slot. Equip the item first or include that equipment change.')
            elif value in LINKS:
                if value not in self.links or struct.unpack_from('<i',result,self.links[value])[0]!=value:
                    raise ValueError('A shortcut must reference an acquired spell or Link. Acquire it first or choose another command.')
            else:
                name,base=next((name,base) for name,base in MAGICS if base<=value<base+3)
                learned=struct.unpack_from('<i',result,self.magic[name][0])[0] if name in self.magic else 0
                if not base<=value<=learned<base+3:
                    raise ValueError('A shortcut must reference an acquired spell or Link. Acquire it first or choose another command.')

    @staticmethod
    def item_available(raw,item):
        at=0x8f4+item*2
        if not raw[at] or not raw[at+1]&1:return False
        for i in range(8):
            offset=0x1880+0x118+i*8
            if raw[offset]==item and raw[offset+1] in (0,1) and raw[offset+4]==1:return True
        return False

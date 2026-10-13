"""Additional BBS/DDD operations using verified PC record positions.

GPL-3.0-or-later. Adapted format/label facts from Kingdom Save Editor;
Copyright (C) 2020 Luciano Ciccariello. See SOURCES.md.
"""
from collections import Counter
import struct
from kh_feature_tables import BBS_KEYBLADES,BBS_COMMAND_KINDS,DDD_SPIRITS
from kh_extra_tables import DDD_ITEMS

class ExtraKhFeatures:
    def __init__(self,raw,game,record,slot,Field):
        self.fields=[];self.operations={};self.raw,self.record,self.game=raw,record,game
        def choice(key,label,delta,options,group,note='',collection=''):
            value=struct.unpack_from('<H',raw,record+delta)[0]
            readonly=value not in options
            if readonly:options={value:f'Existing ID {value} (preserved)'}
            values=tuple(options)
            self.fields.append(Field(key,label,values.index(value),record+delta,'',0,len(values)-1,group,
                choices=tuple(options[i] for i in values),readonly=readonly,note=note,collection=collection))
            if not readonly:self.operations[key]=(record+delta,values)
        if game=='bbs':
            character={1:'Ventus',2:'Aqua',3:'Terra',5:'Ventus',6:'Aqua',7:'Terra'}[raw[record+0x17]]
            defaults={'Ventus':(1,0x21,0x22),'Aqua':(2,0x23,0x24,0x25,0x32),'Terra':(3,0x26,0x27,0x28)}
            options={i:n for i,(n,c) in BBS_KEYBLADES.items() if '('+character+')' in n or i in defaults[character]}
            choice('keyblade','Equipped Keyblade',0x59fa,options,'Equipment','Character-specific known weapons only. Changes the equipped ID; story and weapon-acquisition records are preserved.')
            for index in range(15):
                delta=0x5644+index*8;identifier=struct.unpack_from('<H',raw,record+delta)[0]
                spec=BBS_COMMAND_KINDS.get(identifier)
                if not spec or spec[1]!='Finisher':continue
                value=struct.unpack_from('<I',raw,record+delta+4)[0]
                if value>99999999:continue
                key=f'finisher:{index}:xp'
                self.fields.append(Field(key,spec[0]+' · Experience',value,record+delta+4,'<I',0,99999999,'Finishers',note='Saved finisher experience only. Unlock/status flags and character availability are preserved.'))
            pool={}
            for index in range(512):
                identifier=struct.unpack_from('<H',raw,record+0x3498+index*10)[0]
                if identifier in BBS_COMMAND_KINDS:pool[index]=BBS_COMMAND_KINDS[identifier]
            # Battle commands with an unknown or multi-slot footprint stay read-only.
            single_battle=set()
            multi_battle=set()
            for deck in range(3):
                values=[struct.unpack_from('<H',raw,record+0x5a2c+deck*0xc4+i*6)[0] for i in range(8)]
                single_battle.update(i for i,n in Counter(values).items() if n==1 and i in pool)
                multi_battle.update(i for i,n in Counter(values).items() if n>1 and i!=0xffff)
            single_battle-=multi_battle
            for deck in range(3):
                base=0x5a2c+deck*0xc4
                battle=[struct.unpack_from('<H',raw,record+base+i*6)[0] for i in range(8)]
                duplicates=multi_battle
                for index in range(19):
                    role='Battle' if index<8 else 'Action' if index<18 else 'Shotlock'
                    kinds={'Battle':('Attack','Magic','Consumable'),'Action':('Movement','Defense','Reprisal'),'Shotlock':('Shotlock',)}[role]
                    original=struct.unpack_from('<H',raw,record+base+index*6)[0]
                    options={0xffff:'Empty'}
                    options.update({i:f'{title} · Inventory entry {i+1}' for i,(title,kind) in pool.items()
                                    if kind in kinds and (role!='Battle' or i in single_battle)})
                    if role=='Battle' and original in duplicates:options={original:f'{pool.get(original,("Saved command",))[0]} · Multi-slot (preserved)'}
                    choice(f'deck:{deck}:{index}',f'{role} entry {index+1 if index<8 else index-7 if index<18 else 1}',base+index*6,
                        options,'Decks','Uses existing owned command references. Modifier words and pool order are preserved; multi-slot layouts and unknown references are not rewritten.',f'Deck {deck+1}')
                    if role=='Battle' and original in duplicates:
                        self.fields[-1].readonly=True;self.operations.pop(self.fields[-1].key,None)
        elif game=='ddd':
            for character,delta,low,high in (('Sora',0xd2e8,512,528),('Riku',0xd2ea,528,544)):
                options={i:n for i,(n,g) in DDD_ITEMS.items() if g=='Keyblades' and low<=i<high}
                choice(f'character:{character}:keyblade',character+' · Keyblade',delta,options,'Equipment',
                       'Changes the equipped character-specific Keyblade only. Story and other acquisition records are preserved.')
            for index in range(102):
                delta=0x53a0+index*256;identifier=raw[record+delta]
                if identifier not in DDD_SPIRITS:continue
                name=DDD_SPIRITS[identifier][0]
                for offset,part in ((61,'Attack'),(62,'Magic'),(63,'Defense')):
                    self.fields.append(Field(f'spirit:{index}:{part.lower()}',part,raw[record+delta+offset],record+delta+offset,'<B',0,255,'Dream Eaters',
                        collection=f'{index+1} · {name}',note='Existing spirit only. Species, name, board, affinity, level/experience and party references are preserved.'))

    def patch(self,result,changes):
        for key,value in changes.items():
            if key in self.operations:
                offset,values=self.operations[key];struct.pack_into('<H',result,offset,values[value])

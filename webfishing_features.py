"""Independent WEBFISHING collection and item operations.

GPL-3.0-or-later. Format facts checked against the MIT NotNite save editor and
native Steam data. Original variant entries and unknown fields are preserved.
"""
from collections import Counter
import struct
from webfishing_tables import THINGS,LURES

ITEMS={i:(name,category) for i,(name,category) in THINGS.items()
       if category in ('fish','none','tool','furniture') and i and not i.startswith('_')
       and i!='none' and 'test' not in (i+' '+name).lower()}
COSMETICS={i:(name,category) for i,(name,category) in THINGS.items() if category not in ('fish','none','tool','furniture')}
QUALITIES=('Normal','Shining','Glistening','Opulent','Radiant','Alpha')

def variant(value):
    if isinstance(value,str):
        raw=value.encode('utf8');return struct.pack('<2I',4,len(raw))+raw+bytes((-len(raw))%4)
    if isinstance(value,int):
        return struct.pack('<Ii',2,value) if -2**31<=value<2**31 else struct.pack('<Iq',0x10002,value)
    if isinstance(value,float):return struct.pack('<If',3,value)
    if isinstance(value,list):return struct.pack('<2I',19,len(value))+b''.join(variant(v) for v in value)
    if isinstance(value,dict):return struct.pack('<2I',18,len(value))+b''.join(variant(k)+variant(v) for k,v in value.items())
    raise ValueError('Unsupported new WEBFISHING value.')

class WebfishingFeatures:
    def __init__(self,raw,info,reader,Field):
        self.raw,self.info,self.reader=raw,info,reader
        self.fields=[];self.memberships={};self.selections={};self.item_choices={};self.removals={};self.hotbar_choices={}
        self.counts=Counter(i.get('id') for i in info['inventory'] if isinstance(i,dict) and isinstance(i.get('id'),str))
        self.refs=Counter(i.get('ref') for i in info['inventory'] if isinstance(i,dict) and type(i.get('ref')) is int)
        self.inventory_span=reader.spans.get(('inventory',))
        def membership(path,options,prefix,group,category=''):
            values=self.at(path)
            if not isinstance(values,list) or path not in reader.spans:return
            expected=str if all(isinstance(x,str) for x in options) else int
            if any(type(x) is not expected for x in values):return
            for identifier,label in options.items():
                key=prefix+str(identifier)
                self.fields.append(Field(key,label,int(identifier in values),reader.spans[path][0],'',0,1,group,boolean=True,collection=category,
                    note='Changes this saved membership only; unknown identities and other entries are retained.'))
                self.memberships[key]=(path,identifier)
        membership(('cosmetics_unlocked',),{i:n for i,(n,c) in COSMETICS.items()},'cosmetic_unlock:','Cosmetics')
        for f in self.fields:
            if f.key.startswith('cosmetic_unlock:'):f.collection=COSMETICS[f.key.split(':',1)[1]][1].replace('_',' ').title()
        membership(('lure_unlocked',),LURES,'lure_unlock:','Lures')
        membership(('cosmetics_equipped','accessory'),{i:n for i,(n,c) in COSMETICS.items() if c=='accessory'},'equipped_accessory:','Appearance','Accessories')
        if isinstance(info.get('bait_selected'),str) and ('bait_selected',) in reader.spans:
            options={'':'None',**{i:i.title() for i in info['bait_inv'] if i}}
            current=info['bait_selected']
            if current not in options:options[current]=f'Existing bait ({current})'
            values=tuple(options)
            self.fields.append(Field('equipped_bait','Equipped bait',values.index(current),reader.spans[('bait_selected',)][0],'',0,len(values)-1,'Bait',choices=tuple(options[i] for i in values),
                note='Requires a positive saved bait quantity. Bait acquisition is synchronized automatically.'))
            self.selections['equipped_bait']=(('bait_selected',),values,'')
        equipped=info.get('cosmetics_equipped',{})
        if isinstance(equipped,dict):
            for category,current in equipped.items():
                if not isinstance(current,str):continue
                options={i:n for i,(n,c) in COSMETICS.items() if c==category}
                if not options:continue
                if category not in ('species','primary_color','secondary_color','eye','mouth','nose','pattern'):options={'':'None',**options}
                if current not in options:options[current]=f'Existing selection ({current})'
                path=('cosmetics_equipped',category)
                if path not in reader.spans:continue
                values=tuple(options);key='equipped_cosmetic:'+category
                self.fields.append(Field(key,category.replace('_',' ').title(),values.index(current),reader.spans[path][0],'',0,len(values)-1,'Appearance',
                    choices=tuple(options[v] for v in values),note='Selecting an original cosmetic also adds its ownership entry automatically. Existing unknown selections are retained until changed.'))
                self.selections[key]=(path,values,'cosmetics_unlocked')
        if isinstance(info.get('lure_selected'),str) and ('lure_selected',) in reader.spans:
            options={'':'Default',**LURES};current=info['lure_selected']
            if current not in options:options[current]=f'Existing lure ({current})'
            values=tuple(options);key='equipped_lure'
            self.fields.append(Field(key,'Equipped lure',values.index(current),reader.spans[('lure_selected',)][0],'',0,len(values)-1,'Lures',choices=tuple(options[v] for v in values)))
            self.selections[key]=( ('lure_selected',),values,'lure_unlocked')
        quests=info.get('quests',{})
        if isinstance(quests,dict):
            for identity,quest in quests.items():
                if not isinstance(quest,dict):continue
                node=reader.nodes.get(('quests',identity,'progress'));goal=quest.get('goal_amt')
                if node and node[1] in ('<i','<q') and type(goal) is int and goal>0 and node[2]>=0:
                    self.fields.append(Field('quest:'+str(identity),str(quest.get('title') or identity)+' · Progress',node[2],node[0],node[1],0,max(goal,node[2]),'Quests',
                        note='Saved progress only. Claim rewards in the game; reward amounts, tiers and completion lists are preserved.'))
        journal=info.get('journal',{})
        if isinstance(journal,dict):
            for category,entries in journal.items():
                if not isinstance(entries,dict):continue
                for fish,entry in entries.items():
                    if isinstance(entry,dict):membership(('journal',category,fish,'quality'),dict(enumerate(QUALITIES)),f'journal_quality:{category}:{fish}:','Journal qualities',str(fish))
        for index,item in enumerate(info['inventory']):
            if not isinstance(item,dict) or not isinstance(item.get('id'),str):continue
            ref=item.get('ref');stable=type(ref) is int and ref>0 and self.refs[ref]==1
            prefix=f'item_ref:{ref}' if stable else f'item:{index}'
            options={i:n for i,(n,c) in ITEMS.items()};current=item['id']
            if current not in options:options[current]=f'Existing item ({current})'
            values=tuple(options);path=('inventory',index,'id')
            if path in reader.spans:
                key=prefix+':identity';self.item_choices[key]=(index,values)
                self.fields.append(Field(key,f'Entry {index+1} · Item',values.index(current),reader.spans[path][0],'',0,len(values)-1,'Inventory',choices=tuple(options[v] for v in values),
                    note='Changes the item ID and preserves its unique reference, quality, size, tags and other saved fields.'))
            if stable and ('inventory',index) in reader.spans:
                key=f'remove_item:{ref}';self.removals[key]=(index,ref)
                self.fields.append(Field(key,f'Remove entry {index+1} · {THINGS.get(current,(current,))[0]}',0,reader.spans[('inventory',index)][0],'',0,1,'Inventory',boolean=True,
                    note='Deletes this exact item on apply and clears matching hotbar, aquarium and locked references.'))
        reference_names={i['ref']:THINGS.get(i.get('id'),(str(i.get('id')),))[0]+f' · Ref {i["ref"]}'
                         for i in info['inventory'] if isinstance(i,dict) and type(i.get('ref')) is int and i['ref']>0 and self.refs[i['ref']]==1}
        membership(('locked_refs',),reference_names,'item_lock:','Inventory','Item locks')
        hotbar=info.get('hotbar',{})
        if isinstance(hotbar,dict):
            for slot,current in hotbar.items():
                node=reader.nodes.get(('hotbar',slot))
                if not node or node[1] not in ('<i','<q') or type(current) is not int:continue
                options={0:'Empty',**reference_names}
                if current not in options:options[current]=f'Existing reference {current} (unmapped)'
                values=tuple(options);key='hotbar:'+str(slot)
                self.fields.append(Field(key,f'Hotbar slot {slot}',values.index(current),node[0],'',0,len(values)-1,'Hotbar',choices=tuple(options[i] for i in values),
                    note='References an existing inventory item; item identity, quantity and tags are preserved.'))
                self.hotbar_choices[key]=(node,values,('hotbar',slot))
        if self.inventory_span:
            for identity,(name,category) in ITEMS.items():
                amount=self.counts[identity]
                self.fields.append(Field('item_count:'+identity,name,amount,self.inventory_span[0],'',amount,amount+99,'Add items',collection=category.title(),
                    note='Total inventory copies. Increase to create normal-quality, size-1 items with unique references. Decreases are not offered here; remove individual entries instead.'))

    def at(self,path):
        value=self.info
        try:
            for component in path:value=value[component]
        except (KeyError,IndexError,TypeError):return None
        return value

    def array(self,path,values,encode=variant):
        start,end=self.reader.spans[path];original=self.at(path)
        entries={}
        for index,value in enumerate(original):
            a,b=self.reader.spans[path+(index,)];entries.setdefault(value,[]).append(self.raw[a:b])
        contents=[]
        for value in values:
            saved=entries.get(value,[]);contents.append(saved.pop(0) if saved else encode(value))
        flags=struct.unpack_from('<I',self.raw,start+4)[0]&0x80000000
        return self.raw[start:start+4]+struct.pack('<I',flags|len(values))+b''.join(contents)

    def replacements(self,result,changes):
        updates=[];lists={}
        for key,value in changes.items():
            if key not in self.memberships:continue
            path,identity=self.memberships[key];values=lists.setdefault(path,list(self.at(path)))
            if value and identity not in values:values.append(identity)
            elif not value:values[:]=[v for v in values if v!=identity]
            if key.startswith('equipped_accessory:') and value and ('cosmetics_unlocked',) in self.reader.spans:
                if changes.get('cosmetic_unlock:'+identity)==0:raise ValueError('An equipped accessory must remain owned.')
                owned=lists.setdefault(('cosmetics_unlocked',),list(self.info['cosmetics_unlocked']))
                if identity not in owned:owned.append(identity)
        for key,value in changes.items():
            if key not in self.selections:continue
            path,values,owned=self.selections[key];identity=values[value]
            if key=='equipped_bait' and identity and changes.get('bait:'+identity,self.info['bait_inv'].get(identity,0))<=0:
                raise ValueError('Add a positive quantity before selecting this bait.')
            start,end=self.reader.spans[path];updates.append((start,end,variant(identity)))
            owned_path=(owned,)
            if identity and identity in (COSMETICS if owned=='cosmetics_unlocked' else LURES) and owned_path in self.reader.spans:
                values=lists.setdefault(owned_path,list(self.at(owned_path)))
                unlock_key=('cosmetic_unlock:' if owned=='cosmetics_unlocked' else 'lure_unlock:')+identity
                if changes.get(unlock_key)==0:raise ValueError('An equipped selection cannot be removed from its ownership list in the same edit.')
                if identity not in values:values.append(identity)
        removed={index:ref for key,(index,ref) in self.removals.items() if changes.get(key)}
        if removed and any(k.startswith('item:') for k in changes):raise ValueError('Apply edits to items without unique references separately from removals.')
        for index,ref in removed.items():
            if any(k.startswith(f'item_ref:{ref}:') for k in changes):raise ValueError('Restore other edits to an item before removing it.')
            if changes.get(f'item_lock:{ref}'):raise ValueError('A removed item cannot remain locked.')
        staged_hotbar={}
        for key,(node,values,path) in self.hotbar_choices.items():
            if key in changes:
                ref=values[changes[key]]
                if ref and ref in removed.values():raise ValueError('The hotbar cannot reference an item being removed.')
                staged_hotbar[path[-1]]=ref
                if node[1]=='<i' and not -2**31<=ref<2**31:
                    start,end=self.reader.spans[path];updates.append((start,end,variant(ref)))
                else:struct.pack_into(node[1],result,node[0],ref)
        if removed or any(k in self.item_choices or k.startswith('item_count:') for k in changes):
            start,end=self.inventory_span;entries=[];counts=Counter();ids_changed={}
            for key,(index,values) in self.item_choices.items():
                if key in changes:ids_changed[index]=values[changes[key]]
            for index,item in enumerate(self.info['inventory']):
                if index in removed:continue
                a,b=self.reader.spans[('inventory',index)];encoded=bytearray(result[a:b])
                identity=ids_changed.get(index,item.get('id') if isinstance(item,dict) else None)
                if index in ids_changed:
                    x,y=self.reader.spans[('inventory',index,'id')];encoded[x-a:y-a]=variant(identity)
                entries.append(bytes(encoded));counts[identity]+=1
            refs=set(self.refs)|{v for v in self.info.get('hotbar',{}).values() if type(v) is int}
            aquarium=self.info.get('saved_aqua_fish',{})
            if isinstance(aquarium,dict) and type(aquarium.get('ref')) is int:refs.add(aquarium['ref'])
            if isinstance(self.info.get('locked_refs'),list):refs.update(v for v in self.info['locked_refs'] if type(v) is int)
            added=0;ref=1
            for key,target in changes.items():
                if not key.startswith('item_count:'):continue
                identity=key.split(':',1)[1]
                if target<counts[identity]:raise ValueError('The requested total is below the copies remaining after other item edits.')
                for _ in range(target-counts[identity]):
                    added+=1
                    if added>500 or len(entries)>=10000:raise ValueError('Add at most 500 items per apply, within 10,000 total items.')
                    while ref in refs:ref+=1
                    if ref>=2**31:raise ValueError('No supported unused item reference is available.')
                    refs.add(ref);entries.append(variant({'id':identity,'quality':0,'ref':ref,'size':1.0,'tags':[]}))
            flags=struct.unpack_from('<I',self.raw,start+4)[0]&0x80000000
            updates.append((start,end,self.raw[start:start+4]+struct.pack('<I',flags|len(entries))+b''.join(entries)))
        if removed:
            removed_refs=set(removed.values())
            hotbar=self.info.get('hotbar',{})
            if isinstance(hotbar,dict):
                for slot,ref in hotbar.items():
                    node=self.reader.nodes.get(('hotbar',slot))
                    if node and staged_hotbar.get(slot,node[2]) in removed_refs:struct.pack_into(node[1],result,node[0],0)
            node=self.reader.nodes.get(('saved_aqua_fish','ref'))
            if node and node[2] in removed_refs:struct.pack_into(node[1],result,node[0],0)
            path=('locked_refs',)
            if isinstance(self.at(path),list) and all(type(v) is int for v in self.at(path)):
                lists[path]=[v for v in lists.get(path,self.at(path)) if v not in removed_refs]
        for path,values in lists.items():
            start,end=self.reader.spans[path];updates.append((start,end,self.array(path,values)))
        return updates

    def removed(self,key):
        ref=int(key.split(':')[1]);return int(ref not in self.refs)

    def verify_hotbar(self,key,value,other):
        node,values,path=self.hotbar_choices[key]
        fresh=other.reader.nodes.get(path)
        return bool(fresh and fresh[2]==values[value])

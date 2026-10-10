"""Independent reader for Alice's Steam PC persistent archive, revision 49.

SPDX-License-Identifier: GPL-3.0-or-later
See docs/ALICE_FORMAT.md for the mapped serialization order and limits.
"""
import math
import struct
from alice_catalog import COLLECTIBLES, ACTORS, CHAPTERS, CINEMATICS, HEALTH_ACTORS

WEAPONS = ('VorpalBlade', 'HobbyHorse', 'TeapotCannon', 'PepperGrinder')
ABILITIES = ('Float','DoubleJump','Shrink','Sonar','Combat','Lockon','VorpalBlade',
             'Dodge','PepperGrinder','Aiming','ClockBomb','Hysteria','Umbrella',
             'Deflect','HobbyHorse','TeapotCannon')
CAPABILITIES = ('DoubleJump','Float','Sprint','Combat','Shrink','Lockon','Aiming',
                'ShowPath','ShowCat','Sonar','ClockBomb','Hysteria','Umbrella','Deflect','Dodge')
ENEMIES = ('Insidious Ruin','Bolterfly','Madcap','Slithering Ruin','Eyepot',
           'Menacing Ruin','Ice Snark','Cannon Crab','Lost Soul','Colossal Ruin',
           'Samurai Wasp','Ink Wasp','Daimyo Wasp','Whirligig','Card Guard',
           'Armored Card Guard','Executioner','Dollgirl','Bitch Baby','Archer Wasp')
DRESSES = ('Silk Maiden','Siren','Steamdress','Classic','Royal Suit','Misstitched',
           'Fleshmaiden','Hattress','Checkmate','Late but Lucky','Cheshire','Caterpillar')
LABELS = {'VorpalBlade':'Vorpal Blade','HobbyHorse':'Hobby Horse',
          'TeapotCannon':'Teapot Cannon','PepperGrinder':'Pepper Grinder',
          'DoubleJump':'Double jump','ClockBomb':'Clockwork Bomb','Lockon':'Lock-on',
          'ShowPath':'Golden path','ShowCat':'Cheshire guidance','Sonar':'Shrink sense',
          'Umbrella':'Umbrella / block','Aiming':'Aim','Deflect':'Deflect','Float':'Float',
          'Shrink':'Shrink','Combat':'Combat','Dodge':'Dodge','Hysteria':'Hysteria'}

def fstring(value):
    if not value:return struct.pack('<i',0)
    try:raw=value.encode('latin-1')+b'\0';return struct.pack('<i',len(raw))+raw
    except UnicodeEncodeError:
        raw=value.encode('utf-16le')+b'\0\0'
        return struct.pack('<i',-len(raw)//2)+raw

class Archive:
    def __init__(self, raw):self.raw=raw;self.pos=0
    def take(self, size):
        if size<0 or self.pos+size>len(self.raw):raise ValueError('truncated archive')
        start=self.pos;self.pos+=size;return self.raw[start:self.pos]
    def number(self,fmt='<i'):return struct.unpack(fmt,self.take(struct.calcsize(fmt)))[0]
    def count(self):
        n=self.number()
        if not 0<=n<=100000 or n>(len(self.raw)-self.pos)//4:raise ValueError('invalid array count')
        return n
    def string(self):
        n=self.number()
        if not n:return ''
        if abs(n)>65536:raise ValueError('invalid string length')
        raw=self.take(n if n>0 else -n*2);terminator=b'\0' if n>0 else b'\0\0'
        if not raw.endswith(terminator):raise ValueError('unterminated string')
        value=raw[:-len(terminator)].decode('latin-1' if n>0 else 'utf-16le')
        if '\0' in value:raise ValueError('embedded string terminator')
        return value
    def strings(self):return [self.string() for _ in range(self.count())]

class AliceProfile:
    def __init__(self,raw,Field):
        self.raw=raw;self.fields=[];self.scalars={};self.lists={};self.list_entries={};self.actors={};self.maps=[];self.Field=Field
        r=Archive(raw)
        if (r.number(),r.number())!=(49,0xf223):raise ValueError('expected Steam PC archive revision 49')
        seen=set();self.map_start=8
        for _ in range(r.count()):
            map_start=r.pos
            map_name=r.string()
            if not map_name or map_name.casefold() in seen:raise ValueError('duplicate or empty map name')
            seen.add(map_name.casefold())
            count_start=r.pos;count=r.count();items_start=r.pos
            actor_names=set()
            for _ in range(count):
                actor=r.string();identity=(map_name,actor)
                if not actor or actor.casefold() in actor_names:raise ValueError('duplicate or empty actor name')
                actor_names.add(actor.casefold())
                start=r.pos;values=[r.number() for _ in range(6)]
                self.actors[identity]=(start,values)
            self.maps.append((map_name,map_start,count_start,items_start,r.pos,count))
        self.map_end=r.pos
        self.actor_lookup={tuple(v.casefold() for v in identity):record for identity,record in self.actors.items()}
        r.number();self.current_map=r.string()
        def scalar(key,label,group,maximum=999999,minimum=0,fmt='<i',boolean=False,choices=(),note='',expose=True):
            offset=r.pos;value=r.number(fmt)
            if not math.isfinite(value):raise ValueError('non-finite value in '+key)
            self.scalars[key]=(offset,fmt,value)
            if expose:
                field=Field(key,label,value,offset,fmt,minimum,maximum,group,fmt=='<f',boolean,choices,note)
                field.validate(value);self.fields.append(field)
            return value
        def flag(key,label,group,note='',expose=True):
            return scalar(key,label,group,1,boolean=True,note=note,expose=expose)
        def strings(key):
            start=r.pos;values=[];entries=[]
            for _ in range(r.count()):
                entry_start=r.pos;values.append(r.string());entries.append(raw[entry_start:r.pos])
            self.lists[key]=(start,r.pos,values)
            self.list_entries[key]=entries
            return values
        scalar('paint','Rose paint pots','Health',16,note='Every four pots add health. Changing the count also updates the individual pot pickups.')
        scalar('challenge_count','Challenge room statistic','Statistics')
        scalar('interactive_count','Interactive object statistic','Statistics')
        scalar('golden_path_count','Golden path uses','Statistics')
        for chapter in range(1,7):
            flag(f'gi_chapter:{chapter}',f'Chapter {chapter} statistic','Story and chapters',expose=False)
            scalar(f'snout_count:{chapter}',f'Chapter {chapter} snout count','Snouts',expose=False)
            scalar(f'memory_count:{chapter}',f'Chapter {chapter} memory count','Memories',expose=False)
        scalar('overall','Completion statistic','Statistics',100,expose=False)
        scalar('snout_total','Snouts statistic','Snouts',expose=False)
        scalar('family_total','Family memory statistic','Statistics',expose=False)
        strings('gi_memories')
        flag('achievement41','Achievement 41 profile flag','Statistics',expose=False)
        for weapon in ('VorpalBlade','TeapotCannon','HobbyHorse','PepperGrinder'):
            flag('dlc_unlock:'+weapon,LABELS[weapon]+' DLC unlocked','DLC')
            flag('dlc_enable:'+weapon,LABELS[weapon]+' DLC enabled','DLC',
                 'Requires the DLC content to be available in the game installation.')
        flag('game_complete','Game completed','Story and chapters')
        scalar('skipped','Skipped cinematics','Statistics')
        scalar('hysteria_uses','Hysteria uses','Statistics')
        flag('ngplus','New Game Plus','Story and chapters')
        for index,dress in enumerate(DRESSES):
            flag('dress:'+str(index),dress+' ability active','Dresses',
                 'Controls the dress ability flag; select outfits in the game. DLC outfits need installed content.')
        scalar('teeth','Teeth','Economy',999999999)
        # Keep economy first for quick access and existing integrations.
        self.fields.insert(0,self.fields.pop())
        scalar('health','Current health','Health',144,note='Base health: 64. Each story upgrade and each set of four pots adds 8. A loaded checkpoint can override current health.')
        for weapon in WEAPONS:
            scalar('weapon:'+weapon,LABELS[weapon]+' level','Weapons',4,
                   choices=('Not acquired','Level 1','Level 2','Level 3','Level 4'),
                   note='Choosing level 1–4 also adds the weapon to acquired abilities.')
        flag('deflect_spin','Spinning deflect','Skills')
        for index in range(16):
            flag('cave:'+str(index),f'Chapter {2+index//4} · Radula room {1+index%4}','Radula rooms')
        for chapter in range(1,6):flag('big_memory:'+str(chapter),f'Chapter {chapter} major memory completed','Memories')
        for chapter in range(1,7):flag('chapter:'+str(chapter),f'Chapter {chapter} completed','Story and chapters')
        for chapter in range(1,7):
            scalar('difficulty:'+str(chapter),f'Chapter {chapter} highest completed difficulty','Story and chapters',3,
                   choices=('Easy','Normal','Hard','Nightmare'))
        for index,enemy in enumerate(ENEMIES):flag('enemy:'+str(index),enemy,'Enemy journal')
        for chapter in range(1,7):
            flag('health_upgrade:'+str(chapter),f'Chapter {chapter} health upgrade','Health')
        flag('last_checkpoint','Final checkpoint reached','Story and chapters')
        strings('bink');strings('ability');strings('memory');strings('snout');strings('secret')
        for key,label in [('barriers','Doom barriers destroyed'),('frozen','Enemies frozen'),('ruin_kills','Ruin enemies defeated'),
                          ('card_kills','Card guards defeated'),('achievement43','Achievement 43 counter'),
                          ('achievement38','Achievement 38 counter')]:scalar(key,label,'Statistics')
        flag('first_upgrade','First weapon upgrade completed','Weapons')
        scalar('completion','Completion fraction','Statistics',1,fmt='<f')
        scalar('seconds','Play time in seconds','Statistics',1000000000,fmt='<f')
        r.take(1) # Native global flag: preserve, meaning not established.
        for ability in CAPABILITIES:
            flag_offset=r.pos;value=r.number('<B')
            if value not in (0,1):raise ValueError('invalid capability flag')
            self.scalars['cap:'+ability]=(flag_offset,'<B',value)
        r.take(1) # Native global flag: preserve.
        for index in range(70):
            scalar('section:'+str(index),CHAPTERS.get(index,f'Section {index}'),'Chapter select',1,
                   boolean=True,expose=index in CHAPTERS,
                   note='Unlocks the chapter-select entry; does not relocate the current checkpoint.')
        if r.pos!=len(raw):raise ValueError('unexpected trailing data')
        for index,identity in enumerate(HEALTH_ACTORS):
            record=self.actor_lookup.get(tuple(v.casefold() for v in identity))
            value=int(bool(record and record[1][2]))
            kind={'CC_Riddles_S':'Riddle','CC_Combats_S':'Combat','CC_LSA_Health_S':'Challenge'}[identity[0]]
            self.fields.append(Field('pot:'+str(index),kind+' paint pot · '+identity[1].split('_')[-1],value,-1,'',0,1,'Health',boolean=True))
        for ability in ABILITIES:
            acquired=ability in self.lists['ability'][2]
            self.fields.append(Field('ability:'+ability,LABELS[ability],int(acquired),-1,'',0,1,'Skills',boolean=True))
        for kind,group in [('memory','Memories'),('snout','Snouts'),('secret','Bottles'),('bink','Cinematics')]:
            originals=self.lists[kind][2]
            identifiers=sorted(set(originals)|(set(CINEMATICS) if kind=='bink' else set(COLLECTIBLES[kind])))
            for identifier in identifiers:
                if not identifier:continue
                if kind=='memory' and len(identifier.split('_'))>=4:
                    parts=identifier.split('_');label='Chapter '+parts[0]+' · Memory '+parts[2]+' · '+' '.join(parts[3:])
                elif kind=='bink' or kind=='memory':label=identifier+(' played' if kind=='bink' else '')
                else:label='Chapter '+identifier[2:3]+' · '+('Snout ' if kind=='snout' else 'Bottle ')+' '.join(identifier.split('_')[1:])
                self.fields.append(Field(kind+':'+identifier,label,int(identifier in originals),-1,'',0,1,group,boolean=True))

    def patch(self,result,changes):
        replacements=[];additions={}
        def put(key,value):
            offset,fmt,_=self.scalars[key];struct.pack_into(fmt,result,offset,value)
        def actor_state(identity,value,health=False):
            identity=tuple(identity);normalized=tuple(v.casefold() for v in identity)
            record=self.actor_lookup.get(normalized)
            if record:
                offset,_=record;struct.pack_into('<i',result,offset+8,value)
            elif value:
                additions[identity]=struct.pack('<6i',0,1,value,-1 if health else 0,0,-1)
        for chapter in range(1,7):
            if 'chapter:'+str(chapter) in changes:put('gi_chapter:'+str(chapter),changes['chapter:'+str(chapter)])
        list_changes={kind:{} for kind in self.lists}
        for key,value in changes.items():
            kind,_,identifier=key.partition(':')
            if kind in list_changes:list_changes[kind][identifier]=value
        for weapon in WEAPONS:
            key='weapon:'+weapon;ability_key='ability:'+weapon
            if key in changes:
                acquired=int(changes[key]>0)
                if ability_key in changes and changes[ability_key]!=acquired:
                    raise ValueError('The weapon level conflicts with its acquired ability.')
                list_changes['ability'][weapon]=acquired
            elif ability_key in changes:
                level=self.scalars[key][2]
                put(key,max(1,level) if changes[ability_key] else 0)
        if any('weapon:'+w in changes or 'ability:'+w in changes for w in WEAPONS) and 'first_upgrade' not in changes:
            levels=[struct.unpack_from('<i',result,self.scalars['weapon:'+w][0])[0] for w in WEAPONS]
            put('first_upgrade',int(any(level>1 for level in levels)))
        pot_fields=[field for field in self.fields if field.key.startswith('pot:')]
        pots=[changes.get(field.key,field.value) for field in pot_fields]
        if 'paint' in changes:
            requested=changes['paint']
            pinned={int(key[4:]) for key in changes if key.startswith('pot:')}
            if sum(pots[index] for index in pinned)>requested or sum(1-pots[index] for index in pinned)>len(pots)-requested:
                raise ValueError('Paint-pot count conflicts with the selected individual pickups.')
            for target in (0,1):
                for index in range(len(pots)):
                    if sum(pots)==requested:break
                    if index not in pinned and pots[index]!=target and ((target==0 and sum(pots)>requested) or (target==1 and sum(pots)<requested)):
                        pots[index]=target
        if 'paint' in changes or any(key.startswith('pot:') for key in changes):
            put('paint',sum(pots))
            for index,(field,value) in enumerate(zip(pot_fields,pots)):
                if value!=field.value:actor_state(HEALTH_ACTORS[index],value,True)
        for ability,value in list_changes['ability'].items():
            if 'cap:'+ability in self.scalars:put('cap:'+ability,value)
        for kind,edits in list_changes.items():
            if not edits:continue
            start,end,original=self.lists[kind]
            values=[s for s in original if s not in edits or edits[s]]
            values.extend(s for s,v in edits.items() if v and s not in values)
            if values!=original:
                retained=b''.join(data for value,data in zip(original,self.list_entries[kind]) if value not in edits or edits[value])
                appended=b''.join(fstring(value) for value in values if value not in original)
                replacements.append((start,end,struct.pack('<i',len(values))+retained+appended))
            for identifier,value in edits.items():
                for identity in ACTORS.get(identifier,()):
                    # Snouts use their own native state machine; their global
                    # list is authoritative. Pickup records use scalar 3.
                    if kind in ('memory','secret'):actor_state(identity,value)
            if kind=='snout':
                put('snout_total',len(values))
                for ch in range(1,7):put('snout_count:'+str(ch),sum(s.startswith('CH'+str(ch)+'_') for s in values))
        if additions:
            map_additions={}
            for (map_name,actor),data in additions.items():
                map_additions.setdefault(map_name.casefold(),[]).append(fstring(actor)+data)
            chunks=[];new_maps=[]
            for name,start,count_start,items_start,end,count in self.maps:
                extra=map_additions.pop(name.casefold(),[])
                if extra:chunks.append(bytes(result[start:count_start])+struct.pack('<i',count+len(extra))+bytes(result[items_start:end])+b''.join(extra))
                else:chunks.append(bytes(result[start:end]))
            for normalized,items in map_additions.items():
                name=next(identity[0] for identity in additions if identity[0].casefold()==normalized)
                new_maps.append(fstring(name)+struct.pack('<i',len(items))+b''.join(items))
            replacements.append((self.map_start,self.map_end,struct.pack('<i',len(chunks)+len(new_maps))+b''.join(chunks+new_maps)))
        progress_changed=any(key.startswith(('chapter:','big_memory:','cave:','memory:','snout:','secret:')) for key in changes)
        if progress_changed and 'completion' not in changes:
            def final(key):return changes.get(key,self.scalars[key][2])
            score=sum(final('chapter:'+str(c))*weight for c,weight in enumerate((.15,.1,.1,.1,.1,.05),1))
            def list_count(kind):
                edits=list_changes[kind];original=self.lists[kind][2]
                return len([v for v in original if v not in edits or edits[v]])+sum(1 for v,enabled in edits.items() if enabled and v not in original)
            score+=(list_count('memory')+sum(final('big_memory:'+str(c)) for c in range(1,6)))/94*.1
            score+=list_count('snout')/59*.1+sum(final('cave:'+str(i)) for i in range(16))/16*.1+list_count('secret')/83*.1
            put('completion',max(0,min(1,score)))
        for start,end,data in sorted(replacements,reverse=True):result[start:end]=data
        return result

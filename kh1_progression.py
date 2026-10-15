"""Known KH1 spell tiers and acquisition records, with unrelated state retained.

Independent save-relative reader/writer from documented format facts.
See SOURCES.md for the primary randomizer maps and native-file evidence.
SPDX-License-Identifier: GPL-3.0-or-later
"""
MAGIC=(('Fire','Fira','Firaga'),('Blizzard','Blizzara','Blizzaga'),
       ('Thunder','Thundara','Thundaga'),('Cure','Cura','Curaga'),
       ('Gravity','Gravira','Graviga'),('Stop','Stopra','Stopga'),('Aero','Aerora','Aeroga'))
SUMMONS=('Dumbo','Bambi','Genie','Tinker Bell','Mushu','Simba')
TRINITIES=('Blue','Red','Green','Yellow','White')


class Kh1Progression:
    def __init__(self,raw,field_type):
        self.raw,self.field_type=raw,field_type
        self.records={};self.summons={}

    def magic(self,fields,slot,record):
        for bit,names in enumerate(MAGIC):
            tier=self.raw[record+0x492+bit];available=bool(self.raw[record+0x74]&(1<<bit))
            supported=1<=tier<=3
            fields.append(self.field_type(f'0:magic:{bit}','Sora · '+names[0],tier if available and supported else 0,
                record+0x492+bit,'',0,3,'Magic',choices=('Not learned',)+names,readonly=not supported,
                note=('Changes Sora’s availability and the shared spell tier. New acquisitions also make the spell available to Donald unless explicitly overridden. Removing Sora’s spell preserves Donald’s availability and the shared tier.'
                      if supported else 'Unrecognized shared spell tier. Availability and tier bytes are preserved.')))

    def record(self,fields,slot,record):
        self.records[slot]=record
        values=tuple(self.raw[record+0x7d0:record+0x7d6]);known=tuple(v for v in values if v!=255)
        valid=all(v<6 for v in known) and len(set(known))==len(known) and values==known+(255,)*(6-len(known))
        self.summons[slot]=values if valid else None
        for identifier,name in enumerate(SUMMONS):
            owned=identifier in known if valid else False
            fields.append(self.field_type(f'0:summon:{identifier}','Sora · '+name+' acquired',int(owned),record+0x7d0,'',0,1,'Summons',
                boolean=True,readonly=owned or not valid,
                note='Adds the summon to a recognized compact acquisition list without changing existing order. Story, gems, reward claims and journal entries are preserved.' if valid else 'Unrecognized summon list; its bytes and identities are preserved.'))
        for bit,color in enumerate(TRINITIES):
            owned=(self.raw[record+0x1c1b]>>bit)&1
            fields.append(self.field_type('trinity:'+str(bit),color+' Trinity acquired',owned,record+0x1c1b,'',0,1,'Trinities',
                boolean=True,readonly=bool(owned),note='Adds this learned Trinity color. Individual activated marks, world events and reward claims are preserved.'))
        rescued=0
        for number in range(1,100):
            offset=record+0x1703+(number-1)//8;bit=7-(number-1)%8;owned=(self.raw[offset]>>bit)&1;rescued+=owned
            fields.append(self.field_type('puppy:'+str(number),'Puppy '+str(number)+' rescued',owned,offset,'',0,1,'Dalmatians',
                boolean=True,readonly=bool(owned),note='Adds this rescued-puppy bit. Reward-claim flags, journal completion and world chest state are preserved.'))
        fields.append(self.field_type('puppies_rescued','Rescued puppies',rescued,record+0x1703,'',0,99,'Dalmatians',readonly=True,
            note='Count of the 99 mapped rescue bits. The final five reserved bits are excluded and preserved.'))
        value=self.raw[record+0x1400]
        fields.append(self.field_type('torn_pages','Available Torn Pages',value,record+0x1400,'<B',0,5 if value<=5 else 255,'Story items',readonly=value>5,
            note='Unspent pages available to use. Already completed book chapters, consumed-page history and reward flags are preserved.'))

    def finish(self,result,changes):
        for slot,record in self.records.items():
            edits={key:value for (index,key),value in changes.items() if index==slot}
            for bit in range(7):
                key=f'0:magic:{bit}'
                if key not in edits:continue
                value=edits[key];mask=1<<bit;available=record+0x74;donald=record+0xe8
                if value:
                    newly_acquired=not self.raw[available]&mask
                    result[record+0x492+bit]=value;result[available]|=mask
                    if newly_acquired and f'1:magic:{bit}' not in edits:result[donald]|=mask
                else:result[available]&=~mask
            values=self.summons[slot]
            if values is not None:
                acquired=[v for v in values if v!=255]
                for identifier in range(6):
                    if edits.get(f'0:summon:{identifier}')==1 and identifier not in acquired:acquired.append(identifier)
                result[record+0x7d0:record+0x7d6]=bytes(acquired+[255]*(6-len(acquired)))
            for bit in range(5):
                if edits.get('trinity:'+str(bit))==1:result[record+0x1c1b]|=1<<bit
            for number in range(1,100):
                if edits.get('puppy:'+str(number))==1:result[record+0x1703+(number-1)//8]|=1<<(7-(number-1)%8)
        return result

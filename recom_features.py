"""ReCoM PC acquisition flags, preserving unknown bits and deck data.

GPL-3.0-or-later. Layout/labels adapted from Kingdom Save Editor's
DataRecomTable0/Table2 and flag models. Copyright (C) 2020 Luciano Ciccariello.
"""
from kh_extra_tables import RECOM_CARDS

CARD_UNLOCKS=('Spellbinder','Metal Chocobo','Lionheart','Oathkeeper','Oblivion','Ultima Weapon',
 'Diamond Dust','One-Winged Angel','Fire','Thunder','Gravity','Stop','Aero','Simba','Genie','Bambi',
 'Dumbo','Tinker Bell','Mushu','Cloud','Hi-Potion','Mega-Potion','Ether','Mega-Ether','Elixir','Megalixir')
EXTRA_CARDS=('Xemnas','Xigbar','Xaldin','Saïx','Demyx','Luxord','Roxas','Star Seeker','Monochrome',
 'Follow the Wind','Hidden Dragon','Photon Debugger','Bond of Flame')
FRIENDS=('Donald','Goofy','Aladdin','Ariel','Jack Skellington','Peter Pan','Beast','King Mickey','Pluto')

def normalized(name):return ''.join(c for c in name.casefold() if c.isalnum()).replace('ï','i')

class RecomFeatures:
    def __init__(self,raw,record,Field):
        self.fields=[];self.bits={};self.card_flags={};self.record=record
        for prefix,offset,names,group in (('card_unlock:',0x32c,CARD_UNLOCKS,'Card acquisition'),
                ('extra_card_unlock:',0x330,EXTRA_CARDS,'Extra card acquisition'),('friend_unlock:',0x334,FRIENDS,'Friend acquisition')):
            for index,name in enumerate(names):
                at=record+offset+index//8;bit=index%8;key=prefix+str(index);value=(raw[at]>>bit)&1
                self.fields.append(Field(key,name,value,at,'',0,1,group,boolean=True,
                    note='Saved acquisition flag only. Does not build decks, synthesize story events or grant card quantities. Adding a mapped card quantity enables its matching acquisition flag.'))
                self.bits[key]=(at,bit)
                self.card_flags[normalized(name)]=(key,at,bit)
        for key,label,delta,bit in (('sora_cleared','Sora campaign completed',0x4a1,1),
                ('riku_cleared','Riku campaign completed',0x4a1,4),('kh2_cleared','KH II bonus-card requirement cleared',0x4a1,3),
                ('game_cleared','Completion flag',0x4b0,3)):
            at=record+delta;value=(raw[at]>>bit)&1
            self.fields.append(Field(key,label,value,at,'',value,1,'Completion flags',boolean=True,readonly=bool(value),
                note='Adds the saved completion flag only. Existing completed state is protected. Locations, scenarios, enemies, decks and reward delivery are not rebuilt.'))
            if not value:self.bits[key]=(at,bit)
        # Resolve factual names only; card value/premium variants share acquisition.
        for index,(label,group) in enumerate(RECOM_CARDS):
            if not label:continue
            name=label.split(' · ')[0].replace(' (Premium)','')
            found=self.card_flags.get(normalized(name))
            if found:self.card_flags[index]=found

    def patch(self,result,changes):
        for key,value in changes.items():
            if key in self.bits:
                at,bit=self.bits[key];result[at]=(result[at]&~(1<<bit))|(value<<bit)
        for key,value in changes.items():
            if not key.startswith('card:') or not value:continue
            found=self.card_flags.get(int(key.split(':')[1]))
            if not found:continue
            flag,at,bit=found
            if changes.get(flag)==0:raise ValueError('A card with a positive quantity cannot have its acquisition disabled.')
            result[at]|=1<<bit

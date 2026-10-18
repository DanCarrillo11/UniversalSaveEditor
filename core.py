"""UniversalSaveEditor: byte-preserving save inspection and explicit field patches.

SPDX-License-Identifier: GPL-3.0-or-later
Format references and attribution: SOURCES.md.
"""
from dataclasses import dataclass
from collections import Counter
from pathlib import Path
import ctypes
import hashlib
import math
import os
import re
import struct
import uuid
import unicodedata
import xml.etree.ElementTree as ET
import zlib
from kh_items import ITEMS
from kh2_items import ITEM_NAMES as KH2_ITEM_NAMES
from ror2_unlocks import UNLOCK_IDS, unlock_group, unlock_label
from alice_profile import AliceProfile
from alice_config import AliceConfig
from kh_party import PartyEditor, KH1_CHARACTERS, KH2_CHARACTERS
from kh_party_tables import KH2_ABILITIES, KH2_EQUIPMENT

MAX_SIZE = 64 * 1024 * 1024

class FormatError(ValueError):
    pass

@dataclass
class Field:
    key: str
    label: str
    value: int | float | str
    offset: int
    fmt: str
    minimum: int = 0
    maximum: int = 999999
    group: str = ''
    decimal: bool = False
    boolean: bool = False
    choices: tuple = ()
    note: str = ''
    readonly: bool = False
    collection: str = ''
    item_id: int | str | None = None
    art_choices: tuple = ()
    text: bool = False

    def parse(self, text):
        if self.text:
            self.validate(text)
            return text
        try:
            value = float(text) if self.decimal else int(text)
        except (ValueError, TypeError):
            raise ValueError('enter a valid number' if self.decimal else 'enter a whole number')
        self.validate(value)
        return value

    def validate(self, value):
        if self.text:
            if type(value) is not str or any(unicodedata.category(c).startswith('C') for c in value):
                raise ValueError(f'{self.label}: enter text without control or invisible characters.')
            if not self.minimum <= len(value.encode('utf-8')) <= self.maximum:
                raise ValueError(f'{self.label}: use at most {self.maximum} UTF-8 bytes.')
            return
        if type(value) not in ((int, float) if self.decimal else (int,)) or (type(value) is float and not math.isfinite(value)) or not self.minimum <= value <= self.maximum:
            raise ValueError(f'{self.label}: use a value between {self.minimum} and {self.maximum}.')

@dataclass
class Slot:
    name: str
    fields: list

class GodotReader:
    def __init__(self, data):
        self.data, self.pos, self.nodes, self.spans = data, 4, {}, {}
        if len(data) < 8 or struct.unpack_from('<I', data)[0] != len(data)-4:
            raise FormatError('Invalid Godot save length.')

    def take(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise FormatError('The save file is truncated.')
        result = self.data[self.pos:self.pos+count]
        self.pos += count
        return result

    def number(self, fmt):
        return struct.unpack('<'+fmt, self.take(struct.calcsize('<'+fmt)))[0]

    def string(self):
        count = self.number('I')
        value = self.take(count).decode('utf-8').rstrip('\0')
        self.take((-count) % 4)
        return value

    def read(self, path=(), depth=0):
        start = self.pos
        value = self._read(path, depth)
        self.spans[path] = (start, self.pos)
        return value

    def _read(self, path=(), depth=0):
        if depth > 64:
            raise FormatError('The save structure is too deeply nested.')
        header = self.number('I')
        kind, flags = header & 65535, header >> 16
        if flags and (kind not in (2, 3) or flags != 1):
            raise FormatError('Unsupported Godot flags.')
        start = self.pos
        if kind == 0:
            return None
        if kind in (1, 2, 3):
            fmt = {1:'I', 2: 'q' if flags else 'i', 3: 'd' if flags else 'f'}[kind]
            value = self.number(fmt)
            self.nodes[path] = (start, '<'+fmt, value)
            return value
        if kind == 4:
            return self.string()
        if kind in (18, 19):
            count = self.number('I') & 0x7fffffff
            if count > (len(self.data)-self.pos)//4:
                raise FormatError('Invalid element count.')
            result = {} if kind == 18 else []
            for index in range(count):
                if kind == 18:
                    key = self.read((), depth+1)
                    if not isinstance(key, (str, int)) or key in result:
                        raise FormatError('Unsupported or duplicate Godot key.')
                    result[key] = self.read(path+(key,), depth+1)
                else:
                    result.append(self.read(path+(index,), depth+1))
            return result
        sizes = {5:8, 6:16, 7:12, 8:24, 9:16, 10:16, 11:24, 12:36, 13:48, 14:16}
        if kind in sizes:
            return self.take(sizes[kind])
        if kind in (20,21,22,24,25,26):
            count = self.number('I')
            size = count * {20:1,21:4,22:4,24:8,25:12,26:16}[kind]
            result = self.take(size)
            self.take((-size)%4)
            return result
        if kind == 23:
            count = self.number('I')
            if count > (len(self.data)-self.pos)//4:
                raise FormatError('Invalid array.')
            return [self.string() for _ in range(count)]
        raise FormatError(f'Godot type {kind} is unsupported. The file will not be edited.')

def godot_string_array(values):
    result = bytearray(struct.pack('<II', 19, len(values)))
    for value in values:
        raw = value.encode('utf-8')
        result.extend(struct.pack('<II', 4, len(raw)))
        result.extend(raw)
        result.extend(bytes((-len(raw)) % 4))
    return bytes(result)

def png_chunks(raw, allow_sqex_crc=False):
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise FormatError('This is not a Kingdom Hearts PNG container.')
    pos, chunks = 8, []
    while pos + 12 <= len(raw):
        size = struct.unpack_from('>I', raw, pos)[0]
        name, start, end = raw[pos+4:pos+8], pos+8, pos+8+size
        if end+4 > len(raw):
            raise FormatError('The container is truncated.')
        if zlib.crc32(raw[pos+4:end]) != struct.unpack_from('>I', raw, end)[0] and not (allow_sqex_crc and name == b'sqEX'):
            raise FormatError(f'Invalid CRC in {name!r}.')
        chunks.append((name,start,end))
        pos = end+4
        if name == b'IEND':
            if pos != len(raw):
                raise FormatError('Unexpected data after IEND.')
            return chunks
    raise FormatError('The IEND chunk is missing.')

class Save:
    def __init__(self, raw, game, path=None, account_id=None):
        if not raw or len(raw) > MAX_SIZE:
            raise FormatError('Unsupported file size (64 MB maximum).')
        self.raw, self.game, self.slots, self.crc_regions = raw, game, [], []
        self.warnings = []
        self.path, self.account_id = path, account_id
        if game == 'webfishing':
            self._webfishing()
        elif game == 'ror2':
            self._ror2()
        elif game == 'kh1':
            self._kh1()
        elif game == 'kh2':
            self._kh2()
        elif game in ('recom', 'bbs', 'ddd'):
            from kh_pc import ExtraKhArchive
            try:
                self.extra_kh = ExtraKhArchive(raw, game, Field, Slot, png_chunks)
            except (ValueError, struct.error) as error:
                raise FormatError(str(error)) from error
            self.slots = self.extra_kh.slots
            self.warnings = self.extra_kh.warnings
            self.crc_regions = self.extra_kh.crc_regions
            self.notes = ['Close the game before applying changes. Difficulty edits do not recalculate starting bonuses. Only explicitly exposed deck references are editable; unknown and multi-slot layouts are preserved.']
            if game=='recom':self.notes.append('Mapped acquisition and completion flags are experimental. Adding mapped card quantities enables acquisition; decks, HP/CP, scenario events and reward delivery are not rebuilt. Native edits were reparsed, but their in-game effect is not yet confirmed.')
        elif game == 'alice':
            self._alice()
        elif game == 'maxpayne':
            from maxpayne_save import MaxPayneEditor
            try:
                self.maxpayne = MaxPayneEditor(raw, Field)
            except ValueError as error:
                raise FormatError(str(error)) from error
            self.slots = [Slot(self.maxpayne.description, self.maxpayne.fields)]
            self.notes = ['Original PC revision 48 inventory. Weapons, reserve ammunition and painkillers can be edited. Loaded rounds, health, Bullet Time and checkpoint state are preserved. Close Max Payne before applying changes. Experimental: game-load verification is still pending.']
        elif game in ('gtav','rdr2'):
            from rockstar_save import RockstarSave
            try:self.rockstar=RockstarSave(raw,game,Field)
            except (ValueError,struct.error) as error:raise FormatError(str(error)) from error
            self.slots=[Slot('Story Mode',self.rockstar.fields)];self.warnings=self.rockstar.warnings
            self.notes=['PC Story Mode only. '+('Character cash/eight skills, recognized saved-player health/armor and flags, clock, respray services and existing occupied garage vehicle protections/plates. Lower maximums also lower the corresponding current value when needed. Saved player means the one serialized active protagonist; scripts may reset flags. Weapons, vehicle creation/models, properties, clothes and story unlocks remain unsupported. Legacy files were checked; Enhanced-native validation is pending.' if game=='gtav' else 'Recognized currency, character/horse attributes and matched horse names, supplies, compendium, bounties, catalog unlocks and weapon customization. Available controls depend on the file. Catalog unlocks do not grant ownership. Experimental acquisition adds ordinary satchel supplies only. Full weapon/clothing acquisition, stable management and story/reward dependencies remain unsupported.')+' Unknown formats are protected. File-level checks do not prove successful in-game loading. Close the game before applying changes.']
        elif game == 'eldenring':
            from elden_ring import EldenRingSave
            try:self.elden_ring=EldenRingSave(raw,Field,Slot)
            except (ValueError,struct.error) as error:raise FormatError(str(error)) from error
            self.slots=self.elden_ring.slots;self.warnings=self.elden_ring.warnings
            self.notes=['Original Elden Ring Steam SL2 files. Select a character to edit progression, supported stacks, held-goods additions, verified weapon upgrades and NG+ scaling. Related item registry, counters, menu data and integrity checks synchronize when needed. NG+ scaling does not restart the story. Close the game before applying. Experimental: edited saves still need in-game verification. Use edited saves offline; online compatibility is not guaranteed.']
        elif game == 're4_2005':
            from re4_uhd import Re4UhdSave
            try:self.re4_uhd=Re4UhdSave(raw,Field,Slot)
            except ValueError as error:raise FormatError(str(error)) from error
            self.slots=self.re4_uhd.slots;self.warnings=self.re4_uhd.warnings
            self.notes=['Steam Ultimate HD Edition. Pesetas, difficulty, player/Ashley health, statistics, existing case quantities and mapped weapon tiers. New case objects, geometry, costumes, unlock dependencies and room state are preserved. Experimental: edited saves still need in-game verification. Close the game before applying changes.']
        elif game == 're5':
            from re5_save import Re5Save
            try:self.re5=Re5Save(raw,Field)
            except ValueError as error:raise FormatError(str(error)) from error
            self.slots=[Slot('Steamworks profile',self.re5.fields)];self.warnings=self.re5.warnings
            self.notes=['Money, exchange points, costume flags, screen filters, infinite-ammo, library-file and figure unlocks. Weapon ownership, upgrades, inventory, chapter progress and account data are preserved. Infinite-ammo flags do not grant weapons. Experimental: in-game verification is pending. Close the game before applying changes.']
        elif game=='re1_hd':
            from re_hd_save import ReHdSave
            try:self.re_hd=ReHdSave(raw,Field)
            except ValueError as error:raise FormatError(str(error)) from error
            self.slots=[Slot(f'Save record {index+1}',fields) for index,fields in self.re_hd.slot_records];self.warnings=self.re_hd.warnings
            self.notes=['Experimental HD Remaster PC gameplay records: difficulty, save count, defensive supplies, known inventory/item-box replacement and next empty box entry. Other sections, capacities, player identity and story are preserved. Edited saves still need in-game verification. Close the game before applying changes.']
        elif game=='re6':
            from re6_save import Re6Save
            try:self.re6=Re6Save(raw,Field)
            except ValueError as error:raise FormatError(str(error)) from error
            self.slots=[Slot('PC profile',self.re6.fields)];self.warnings=self.re6.warnings
            self.notes=['Skill points, Mercenaries flags/results, uncollected emblems, existing supplies and equipped campaign/extra-mode skills. Existing nonzero emblems, profile identity, purchase flags, weapon IDs, story and difficulty are preserved. Extra-mode skill restrictions need further verification. DLC still requires ownership. Experimental: edited saves need in-game verification. Close the game before applying changes.']
        elif game in ('re2','re3','re4_remake','re7','re8','re9'):
            from re_engine_save import ReEngineSave
            from kh3_pc import AccountIdRequired
            try:self.re_engine=ReEngineSave(raw,game,Field,path,account_id)
            except AccountIdRequired:raise
            except (ValueError,struct.error) as error:raise FormatError(str(error)) from error
            self.account_id=self.re_engine.account
            self.slots=[Slot('Opened file',self.re_engine.fields)];self.warnings=self.re_engine.warnings
            validation='Native Steam files were checked; edited saves still need in-game verification.' if game=='re9' else 'Experimental: compatibility with real Steam saves is still being verified.'
            self.notes=[validation+' Gameplay slots and system profiles contain different options. Numbered collection entries follow their order in the save. Unknown data, item identities, story state and original account encryption are preserved. Close the game before applying changes.']
        elif game == 'kh3':
            from kh3_pc import Kh3PcSave, AccountIdRequired
            try:
                self.kh3 = Kh3PcSave(raw, Field, path, account_id)
            except AccountIdRequired:
                raise
            except ValueError as error:
                raise FormatError(str(error)) from error
            self.account_id = self.kh3.account
            self.slots = [Slot('PC save slot', self.kh3.fields)]
            self.warnings = self.kh3.warnings
            self.notes = ['Account encryption is preserved. Difficulty edits do not recalculate starting bonuses. Close Kingdom Hearts III before applying changes.']
        else:
            raise FormatError('Editing is not implemented for this game yet.')

    def _webfishing(self):
        reader = GodotReader(self.raw)
        self.info = reader.read()
        if reader.pos != len(self.raw) or not isinstance(self.info,dict):
            raise FormatError('Unsupported WEBFISHING save structure.')
        if not {'inventory','money','bait_inv','level'} <= self.info.keys():
            raise FormatError('This does not appear to be a WEBFISHING player save.')
        if not isinstance(self.info['inventory'],list) or not isinstance(self.info['bait_inv'],dict):
            raise FormatError('The inventory or bait structure is unsupported.')
        unlocked = self.info.get('bait_unlocked', [])
        if not isinstance(unlocked, list) or any(not isinstance(value, str) for value in unlocked):
            raise FormatError('The unlocked bait list is unsupported.')
        self.bait_unlocked_span = reader.spans.get(('bait_unlocked',))
        fields = []
        specs = [('money','Money',9999999), ('loan_left','Outstanding debt',9999999)]
        for key,label,limit in specs:
            node = reader.nodes.get((key,))
            if node and node[1] in ('<i','<q','<f','<d'):
                if not math.isfinite(node[2]):
                    raise FormatError('Invalid numeric value in '+key)
                fields.append(Field(key,label,node[2],node[0],node[1],0,limit))
        for bait, amount in self.info['bait_inv'].items():
            if not bait:
                continue
            node = reader.nodes.get(('bait_inv',bait))
            if node and node[1] in ('<i','<q'):
                limit = self.info.get('max_bait',100)
                if not isinstance(limit,int) or limit < 0:
                    raise FormatError('Invalid bait capacity.')
                fields.append(Field('bait:'+bait,'Bait · '+bait,amount,node[0],node[1],0,limit))
        def add(path, key, label, low, high, group, decimal=False,**options):
            node=reader.nodes.get(path)
            if node and node[1] in ('<i','<q','<f','<d'):
                if not math.isfinite(node[2]):
                    raise FormatError('Invalid value: '+label)
                fields.append(Field(key,label,node[2],node[0],node[1],low,high,group,decimal and node[1] in ('<f','<d'),**options))
        for key,label,low,high,group,decimal in [
            ('level','Level',1,50,'Progress',False),
            ('xp','Experience (XP)',0,9999999,'Progress',True),
            ('fish_caught','Fish caught',0,9999999,'Progress',False),
            ('cash_total','Total money earned',0,9999999,'Economy',False),
            ('max_bait','Bait capacity',1,9999,'Bait',False),
            ('rod_power','Rod power',0,5,'Upgrades',False),
            ('rod_speed','Rod speed',0,5,'Upgrades',False),
            ('rod_chance','Rod chance',0,5,'Upgrades',False),
            ('rod_luck','Rod luck',0,5,'Upgrades',False),
            ('buddy_level','Buddy level',0,5,'Upgrades',False),
            ('buddy_speed','Buddy speed',0,5,'Upgrades',False),
        ]: add((key,),key,label,low,high,group,decimal)
        reference_counts=Counter(i.get('ref') for i in self.info['inventory'] if isinstance(i,dict) and type(i.get('ref')) is int)
        for index,item in enumerate(self.info['inventory']):
            if not isinstance(item,dict):continue
            name=f'{index+1} · {item.get("id","Item")}'
            identity='item:'+item['id'] if isinstance(item.get('id'),str) else None
            ref=item.get('ref')
            unique=type(ref) is int and ref>0 and reference_counts[ref]==1
            prefix=f'item_ref:{ref}' if unique else f'item:{index}'
            add(('inventory',index,'quality'),prefix+':quality',name+' · quality (0–5)',0,5,'Inventory',item_id=identity)
            add(('inventory',index,'size'),prefix+':size',name+' · size',0.001,999999,'Inventory',True,item_id=identity)
        journal=self.info.get('journal',{})
        if isinstance(journal,dict):
            for category,entries in journal.items():
                if not isinstance(entries,dict):continue
                for fish,entry in entries.items():
                    if not isinstance(entry,dict):continue
                    name=f'{category} / {fish}'
                    identity='item:'+fish if isinstance(fish,str) else None
                    add(('journal',category,fish,'count'),f'journal:{category}:{fish}:count',name+' · catches',0,9999999,'Journal',item_id=identity)
                    add(('journal',category,fish,'record'),f'journal:{category}:{fish}:record',name+' · record',0,999999,'Journal',True,item_id=identity)
        from webfishing_features import WebfishingFeatures
        self.webfishing=WebfishingFeatures(self.raw,self.info,reader,Field)
        fields.extend(self.webfishing.fields)
        self.slots = [Slot(f'Level {self.info["level"]} · {len(self.info["inventory"])} items',fields)]

    def _ror2(self):
        try:
            text = self.raw.decode('utf-8')
            root = ET.fromstring(text)
        except (UnicodeDecodeError, ET.ParseError) as error:
            raise FormatError('Unsupported Risk of Rain 2 XML profile.') from error
        if root.tag != 'UserProfile':
            raise FormatError('This does not appear to be a Risk of Rain 2 profile.')
        self.xml_text = text
        fields = []
        def add_value(key, label, raw_value, start, low, high, group, decimal=False):
            if raw_value is None:
                return
            raw_value = raw_value.strip()
            try:
                value = float(raw_value) if decimal else int(raw_value)
            except ValueError as error:
                raise FormatError('Invalid value in '+key) from error
            fields.append(Field(key,label,value,start,
                'xml-float' if decimal else 'xml-int',low,high,group,decimal))
        coins = re.search(r'<coins>([^<]*)</coins>',text)
        if coins:
            add_value('coins','Lunar Coins',coins.group(1),coins.start(1),0,2147483647,'Economy')
        stat_specs = {
            'totalGamesPlayed':('Games played',0,999999999,'Progress',False),
            'totalTimeAlive':('Total time alive (seconds)',0,1e15,'Progress',True),
            'highestLevel':('Highest level',0,999999,'Progress',False),
            'totalItemsCollected':('Items collected',0,999999999999,'Progress',False),
            'highestItemsCollected':('Most items in one run',0,999999999,'Progress',False),
            'totalStagesCompleted':('Stages completed',0,999999999,'Progress',False),
            'highestStagesCompleted':('Most stages in one run',0,999999,'Progress',False),
            'highestInfiniteTowerWaveReached':('Highest Simulacrum wave',0,999999,'Progress',False),
            'totalKills':('Enemies killed',0,999999999999,'Combat',False),
            'totalMinionKills':('Ally kills',0,999999999999,'Combat',False),
            'totalDeaths':('Deaths',0,999999999,'Combat',False),
            'totalDamageDealt':('Total damage dealt',0,1e15,'Combat',True),
            'highestDamageDealt':('Highest single hit',0,1e15,'Combat',True),
            'totalDamageTaken':('Total damage taken',0,1e15,'Combat',True),
            'totalHealthHealed':('Total health healed',0,1e15,'Combat',True),
            'totalEliteKills':('Elite kills',0,999999999999,'Combat',False),
            'totalGoldCollected':('Total gold collected',0,1e15,'Economy',True),
            'maxGoldCollected':('Most gold in one run',0,1e15,'Economy',True),
            'totalPurchases':('Purchases made',0,999999999999,'Economy',False),
        }
        seen = set()
        for match in re.finditer(r'<stat\s+name="([^"]+)"\s*>([^<]*)</stat>',text):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            if name in stat_specs:label,low,high,group,decimal = stat_specs[name]
            else:
                saved=match.group(2).strip()
                # Unknown nonnumeric statistics are retained, not coerced. Keep
                # integer representation for integer counters and reject infinities.
                if re.fullmatch(r'\d+',saved):decimal=False;value=int(saved);high=2**64-1
                elif re.fullmatch(r'\d+(?:\.\d+)?(?:[eE][+-]?\d+)?',saved):
                    decimal=True;value=float(saved);high=1e15
                else:continue
                if value>high or (type(value) is float and not math.isfinite(value)):continue
                label=re.sub(r'(?<=[a-z0-9])(?=[A-Z])',' ',name).replace('.',' · ').replace('_',' ').strip()
                low=0;group='Additional saved statistics'
            add_value('stat:'+name,label,match.group(2),match.start(2),low,high,group,decimal)
            if name not in stat_specs:
                fields[-1].note='Existing saved statistic. The internal identifier is '+name+'. Its gameplay dependencies and units are not mapped; nonnumeric entries and other XML are preserved.'
                family=name.split('.')[0] if '.' in name else 'Additional saved statistics'
                fields[-1].collection=re.sub(r'(?<=[a-z0-9])(?=[A-Z])',' ',family).replace('_',' ').strip().capitalize()
        if not fields or not any(field.key == 'coins' for field in fields):
            raise FormatError('The profile does not contain the expected Risk of Rain 2 fields.')
        stats_node = root.find('stats')
        if stats_node is None:
            raise FormatError('The profile does not contain the Risk of Rain 2 unlock section.')
        unlocked = [child.text or '' for child in stats_node if child.tag == 'unlock']
        self.ror2_unlocked = unlocked
        for identifier in UNLOCK_IDS:
            fields.append(Field('unlock:'+identifier,unlock_label(identifier),
                int(identifier in unlocked),-1,'xml-unlock',0,1,unlock_group(identifier)))
        self.slots = [Slot(f'Steam profile · {len(unlocked)} unlocks',fields)]

    def _kh1(self):
        from kh_menu import menu_snapshot
        self.kh_menu={}
        self.party=PartyEditor(self.raw,'kh1',Field)
        chunks = png_chunks(self.raw, allow_sqex_crc=True)
        regions = [(start,end) for name,start,end in chunks if name == b'sqEX']
        if len(regions) != 1:
            raise FormatError('A single sqEX block is required.')
        start,end = regions[0]
        self.crc_regions = regions
        if zlib.crc32(self.raw[start-4:end]) != struct.unpack_from('>I',self.raw,end)[0]:
            self.warnings.append('The save block CRC does not match. Enable integrity repair before applying changes. A CRC mismatch alone does not prove that the save data is damaged.')
        # PC archive: 200 entries, 0x158-byte descriptors, 0x16c40-byte records.
        archive = start+16
        if archive != 0x70 or not 0 <= end-(archive+200*0x158+200*0x16c40) < 0x400:
            raise FormatError('Unrecognized Kingdom Hearts Final Mix Steam layout.')
        table = bytearray(self.raw[archive:archive+200*0x158])
        key = bytes(table[0xe0:0xf0])
        for i in range(0xf0):
            table[i] ^= key[i%16]
        base = archive+200*0x158
        for index in range(200):
            desc = index*0x158
            length = struct.unpack_from('<I',table,desc+0x50)[0]
            if length == 0:
                continue
            if length > 0x16c40:
                raise FormatError('The KHFM record is out of bounds.')
            record = base+index*0x16c40
            if length < 0x16c00 or self.raw[record:record+4] != b'\x05\0\0\0':
                continue
            name = bytes(table[desc:desc+0x40]).split(b'\0')[0].decode('ascii',errors='replace')
            fields = [Field('munny','Munny',struct.unpack_from('<I',self.raw,record+0x1641c)[0],record+0x1641c,'<I',0,999999)]
            difficulty=self.raw[record+0x1642c]
            if difficulty not in (0,1,2):
                raise FormatError(f'Slot {index+1}: unsupported KH Final Mix difficulty value.')
            fields.append(Field('difficulty','Difficulty',difficulty,record+0x1642c,'<B',0,2,'Difficulty',
                                choices=('Beginner','Final Mix (Standard)','Proud'),
                                note='Changes this slot\'s saved difficulty. Existing attributes, equipment and starting bonuses are not recalculated.'))
            for char,namechar in enumerate(('Sora','Donald','Goofy')):
                stat = record+4+char*0x74
                for delta,keyname,label,low,high in [(1,'hp_current','Current HP',0,255),(2,'hp','Base HP',1,255),(3,'mp_current','Current MP',0,255),(4,'mp','Base MP',1,255),(5,'ap','Base AP',0,255),(6,'strength','Strength',0,255),(7,'defense','Defense',0,255)]:
                    fields.append(Field(f'{char}:{keyname}',f'{namechar} · {label}',self.raw[stat+delta],stat+delta,'<B',low,high))
            for item_id,item_name,category in ITEMS:
                offset=record+0x499+item_id
                group={'Synthesis':'Materials','Accessory':'Accessories','Keyblade':'Weapons','Staff':'Weapons','Shield':'Weapons'}.get(category,'Items')
                fields.append(Field(f'inventory:{item_id}',item_name,self.raw[offset],offset,'<B',0,99,group,item_id=item_id))
            for character in range(len(KH1_CHARACTERS)):
                self.party.character(fields,len(self.slots),record,character)
            self.party.shared(fields,len(self.slots),record)
            snapshot=menu_snapshot(self.raw,table,index,record,end)
            if snapshot is not None:
                self.kh_menu[len(self.slots)]=snapshot
                for field in fields:
                    if field.key in ('0:level','difficulty'):
                        field.note+=' The identified save-menu snapshot is updated together.'
            level = self.raw[record+4]
            self.slots.append(Slot(f'{name or str(index+1)} · Sora level {level}',fields))
        if not self.slots:
            raise FormatError('No compatible Kingdom Hearts Final Mix saves were found.')

    @staticmethod
    def _kh2_checksum(data):
        """Checksum used by an individual Kingdom Hearts II save record."""
        polynomial = 0x04c11db7
        table = []
        for value in range(256):
            current = value << 24
            for _ in range(255):
                current = ((current << 1) ^ (polynomial if current & 0x80000000 else 0)) & 0xffffffff
            table.append(current)
        checksum = 0xffffffff
        for value in data[:8]:
            checksum = table[((checksum >> 24) ^ value) & 0xff] ^ ((checksum << 8) & 0xffffffff)
        checksum ^= 0xffffffff
        checksum ^= 0xffffffff
        for value in data[12:0x10fc0]:
            checksum = table[((checksum >> 24) ^ value) & 0xff] ^ ((checksum << 8) & 0xffffffff)
        return checksum ^ 0xffffffff

    def _kh2(self):
        self.party=PartyEditor(self.raw,'kh2',Field)
        chunks = png_chunks(self.raw, allow_sqex_crc=True)
        regions = [(start,end) for name,start,end in chunks if name == b'sqEX']
        if len(regions) != 1:
            raise FormatError('A single sqEX block is required.')
        start,end = regions[0]
        self.crc_regions = regions
        if zlib.crc32(self.raw[start-4:end]) != struct.unpack_from('>I',self.raw,end)[0]:
            self.warnings.append('The save block CRC does not match. Enable CRC repair when applying changes.')
        entry_count, stride = 100, 0x10fc0
        archive = start + 16
        table_size = entry_count * 0x158
        if archive != 0x70 or not 0 <= end-(archive+table_size+entry_count*stride) < 0x400:
            raise FormatError('Unrecognized Kingdom Hearts II Final Mix Steam layout.')
        table = bytearray(self.raw[archive:archive+table_size])
        key = bytes(table[0xe0:0xf0])
        for index in range(0xf0):
            table[index] ^= key[index % 16]
        base = archive + table_size
        character_names = KH2_CHARACTERS
        form_names = ('Valor','Wisdom','Limit','Master','Final')
        for index in range(entry_count):
            descriptor = index * 0x158
            length = struct.unpack_from('<I',table,descriptor+0x50)[0]
            if not length:
                continue
            if length > stride:
                raise FormatError('The KH2 record exceeds its allocated space.')
            record = base + index * stride
            magic = self.raw[record:record+4]
            # PC archives also contain a 1 KB KH2S system record. Its metadata
            # is not a player slot; preserve the entire allocated region.
            if magic == b'KH2S' and length == 0x400:
                continue
            if length != stride:
                raise FormatError('The KH2 record has an unexpected size.')
            if magic not in (b'KH2J',b'KH2U',b'KH2E'):
                raise FormatError('The KH2 record header is invalid.')
            expected_checksum=struct.unpack_from('<I',self.raw,record+8)[0]
            if expected_checksum!=self._kh2_checksum(self.raw[record:record+stride]):
                self.warnings.append(f'Slot {index+1}: internal checksum does not match. Enable integrity repair before applying changes.')
            difficulty=self.raw[record+0x2498]
            if difficulty not in (0,1,2,3):
                raise FormatError(f'Slot {index+1}: unsupported KH II Final Mix difficulty value.')
            fields = [
                Field('munny','Munny',struct.unpack_from('<I',self.raw,record+0x2440)[0],record+0x2440,'<I',0,9999999,'Economy'),
                Field('difficulty','Difficulty',difficulty,record+0x2498,'<B',0,3,'Difficulty',
                      choices=('Beginner','Standard','Proud','Critical'),
                      note='Changes this slot\'s saved difficulty. Existing attributes, equipment and starting bonuses are not recalculated.'),
                Field('experience','Experience',struct.unpack_from('<I',self.raw,record+0x36e0)[0],record+0x36e0,'<I',0,99999999,'Progress'),
                Field('bonus_level','Bonus level',struct.unpack_from('<I',self.raw,record+0x3700)[0],record+0x3700,'<I',0,99,'Progress'),
                Field('summon_level','Summon level',self.raw[record+0x3526],record+0x3526,'<B',0,7,'Progress'),
                Field('drive_current','Current Drive',self.raw[record+0x3529],record+0x3529,'<B',0,9,'Drive'),
                Field('drive_max','Maximum Drive',self.raw[record+0x352a],record+0x352a,'<B',0,9,'Drive'),
                Field('drive_anti_points','Anti points',self.raw[record+0x3410],record+0x3410,'<B',0,255,'Drive',
                      note='Saved Anti-point counter. Acquiring a new playable Drive Form resets this counter; other Antiform record bytes are preserved.'),
            ]
            for character,name in enumerate(character_names):
                offset = record + 0x24f0 + character * 0x114
                if character>=3 and not self.raw[offset+15]:continue
                for delta,key_name,label,low,high in (
                    (4,'hp_current','Current HP',0,255),(5,'hp_max','Maximum HP',1,255),
                    (6,'mp_current','Current MP',0,255),(7,'mp_max','Maximum MP',0,255),
                    (8,'ap_boost','AP boosts',0,255),(9,'strength_boost','Strength boosts',0,255),
                    (10,'magic_boost','Magic boosts',0,255),(11,'defense_boost','Defense boosts',0,255),
                    (15,'level','Level',1,99),
                ):
                    fields.append(Field(f'character:{character}:{key_name}',f'{name} · {label}',self.raw[offset+delta],offset+delta,'<B',low,high,'Characters'))
                self.party.character(fields,len(self.slots),record,character)
            self.party.game_settings(fields,len(self.slots),record)
            for form,name in enumerate(form_names):
                offset = record + 0x32f4 + form * 0x38
                fields.extend((
                    Field(f'form:{form}:level',f'{name} · Level',self.raw[offset+2],offset+2,'<B',0,7,'Drive Forms'),
                    Field(f'form:{form}:experience',f'{name} · Experience',struct.unpack_from('<I',self.raw,offset+4)[0],offset+4,'<I',0,99999999,'Drive Forms'),
                ))
                if form in (0,3,4):
                    weapons={i:title for i,(title,kind) in KH2_EQUIPMENT.items() if kind=='Keyblade'}
                    if not struct.unpack_from('<H',self.raw,offset)[0]:weapons[0]='Empty'
                    self.party.choice(fields,len(self.slots),f'form:{form}:weapon',name+' · Weapon',offset,'<H',weapons,'Equipment',
                                      'Transfers one Keyblade between this dual-wield form and the bag. Form-unlock records are preserved; Sora and his dual-wield forms need distinct Keyblades.')
                    self.party.abilities(fields,len(self.slots),f'form:{form}',name,offset+8,24,'<H',
                                         {i:title for i,(title,kind) in KH2_ABILITIES.items()},0x8000)
            self.party.kh2.record(fields,len(self.slots),record)
            name = bytes(table[descriptor:descriptor+0x40]).split(b'\0')[0].decode('ascii',errors='replace')
            level = self.raw[record+0x24ff]
            self.slots.append(Slot(f'{name or str(index+1)} · Sora level {level}',fields))
        if not self.slots:
            raise FormatError('No saved Kingdom Hearts II slots were found in this container.')

    def _alice(self):
        config = self.raw[:8] == struct.pack('<2i',16,0xf223)
        try:self.alice = (AliceConfig if config else AliceProfile)(self.raw, Field)
        except (ValueError,struct.error,UnicodeError) as error:
            raise FormatError('Unsupported Alice profile or configuration: '+str(error)) from error
        self.slots = [Slot('Game configuration' if config else 'Persistent profile',self.alice.fields)]
        self.notes = [
            'GameConfig_PC.CFG: difficulty only. Graphics, controls and extras-menu records are preserved. Close Alice before applying edits.'
            if config else
            'Persistent profile. Select GameConfig_PC.CFG in the file selector to edit current difficulty. Checkpoint position and active outfit are stored separately. Close Alice before applying edits.'
        ]

    def patched(self, changes, repair_crc=False):
        if self.warnings and not repair_crc:
            raise ValueError('Enable integrity repair before applying changes.')
        if not changes and not repair_crc:
            return bytes(self.raw)
        result = bytearray(self.raw)
        known = {(i,f.key):f for i,s in enumerate(self.slots) for f in s.fields}
        for key,value in changes.items():
            if key not in known:
                raise ValueError('Unauthorized field.')
            field = known[key]
            if field.readonly:
                raise ValueError('This field is read-only and cannot be edited directly.')
            field.validate(value)
            if self.game not in ('kh3','re2','re3','re4_remake','re7','re8','re9') and field.fmt and not field.fmt.startswith('xml-'):
                struct.pack_into(field.fmt,result,field.offset,value)
        if self.game == 'kh3':
            result = self.kh3.patch({key:value for (index,key),value in changes.items()})
        elif self.game == 'maxpayne':
            result = self.maxpayne.patch({key:value for (index,key),value in changes.items()})
        elif self.game in ('gtav','rdr2'):
            result=self.rockstar.patch({key:value for (index,key),value in changes.items()})
        elif self.game == 'eldenring':
            result = self.elden_ring.finish(result,changes,repair_crc)
        elif self.game == 're4_2005':
            result = self.re4_uhd.finish(result,changes,repair_crc)
        elif self.game == 're5':
            result = self.re5.patch({key:value for (index,key),value in changes.items()})
        elif self.game=='re6':
            result=self.re6.patch({key:value for (index,key),value in changes.items()})
        elif self.game=='re1_hd':
            result=self.re_hd.patch({key:value for (index,key),value in changes.items()})
        elif self.game in ('re2','re3','re4_remake','re7','re8','re9'):
            result = self.re_engine.patch({key:value for (index,key),value in changes.items()})
        elif self.game in ('recom', 'bbs', 'ddd'):
            result = self.extra_kh.finish(result, changes, repair_crc)
        elif self.game == 'alice':
            try:result = self.alice.patch(result,{key:value for (index,key),value in changes.items()})
            except ValueError as error:raise FormatError(str(error)) from error
        elif self.game == 'webfishing':
            variable_updates=[]
            capacity=changes.get((0,'max_bait'),self.info.get('max_bait',100))
            for field in self.slots[0].fields:
                if field.key.startswith('bait:') and changes.get((0,field.key),field.value)>capacity:
                    raise ValueError('The bait amount exceeds the selected capacity.')
            unlocked = list(self.info.get('bait_unlocked', []))
            for bait, original_amount in self.info['bait_inv'].items():
                if not bait:
                    continue
                amount_key = (0, 'bait:'+bait)
                final_amount = changes.get(amount_key, original_amount)
                if final_amount > 0 and bait not in unlocked:
                    unlocked.append(bait)
            if unlocked != self.info.get('bait_unlocked', []):
                if not self.bait_unlocked_span:
                    raise FormatError('The unlocked bait list was not found.')
                start, end = self.bait_unlocked_span
                encoded=bytearray(godot_string_array(unlocked))
                flags=struct.unpack_from('<I',self.raw,start+4)[0]&0x80000000
                struct.pack_into('<I',encoded,4,flags|len(unlocked))
                variable_updates.append((start,end,bytes(encoded)))
            variable_updates.extend(self.webfishing.replacements(result,{key:value for (index,key),value in changes.items()}))
            for start,end,encoded in sorted(variable_updates,reverse=True):result[start:end]=encoded
            struct.pack_into('<I',result,0,len(result)-4)
        elif self.game == 'ror2':
            text = self.xml_text
            replacements = []
            for key,value in changes.items():
                field = known[key]
                if field.fmt == 'xml-unlock':
                    continue
                rendered = str(value)
                current_end = field.offset
                while current_end < len(text) and text[current_end] not in '<':
                    current_end += 1
                replacements.append((field.offset,current_end,rendered))
            for start,end,rendered in sorted(replacements,reverse=True):
                text = text[:start]+rendered+text[end:]
            unlock_changes = {
                field.key.removeprefix('unlock:'): value
                for key,value in changes.items()
                for field in (known[key],)
                if field.fmt == 'xml-unlock'
            }
            if unlock_changes:
                changed_ids = set(unlock_changes)
                text = re.sub(
                    r'<unlock>\s*([^<]+?)\s*</unlock>',
                    lambda match: '' if match.group(1).strip() in changed_ids else match.group(0),
                    text,
                )
                closing = text.find('</stats>')
                if closing < 0:
                    raise FormatError('The end of the unlock section was not found.')
                additions = ''.join(
                    '<unlock>'+identifier+'</unlock>'
                    for identifier,value in unlock_changes.items() if value
                )
                text = text[:closing]+additions+text[closing:]
            result = bytearray(text.encode('utf-8'))
        if self.game in ('kh1','kh2'):
            result=self.party.finish(result,changes)
        if self.game=='kh1':
            from kh_menu import synchronize
            synchronize(result,self.kh_menu,changes)
        for start,end in self.crc_regions:
            if self.game == 'kh2':
                changed_slots={index for index,key in changes}
                for slot_index,slot in enumerate(self.slots):
                    if slot_index not in changed_slots and not repair_crc:continue
                    record = next(field.offset for field in slot.fields if field.key == 'munny') - 0x2440
                    struct.pack_into('<I',result,record+8,self._kh2_checksum(result[record:record+0x10fc0]))
            struct.pack_into('>I',result,end,zlib.crc32(result[start-4:end]))
        output = bytes(result)
        # Reparse and assert every requested field before returning data to the UI.
        check = Save(output,self.game,self.path,self.account_id)
        for (index,key),value in changes.items():
            field=known[(index,key)]
            if field.fmt.startswith('xml-'):
                expected=value
            else:
                expected=struct.unpack(field.fmt,struct.pack(field.fmt,value))[0] if field.fmt else value
            actual=next((f.value for f in check.slots[index].fields if f.key == key),None)
            if self.game=='rdr2':expected=self.rockstar.rdr2.expected(key,value)
            if self.game=='kh2' and key.startswith('inventory:'):
                expected=self.party.kh2.expected_stock(index,key,value,changes,self.party.encodings)
            if self.game=='eldenring' and (key.startswith('spell_slot:') or key=='active_spell'):
                requested={k:v for (slot,k),v in changes.items() if slot==index}
                valid=self.elden_ring.spell_loadouts[index].verifies(check.elden_ring.spell_loadouts[index],requested)
                actual=expected if valid else None
            if actual is None and self.game=='eldenring' and key.startswith('add_goods:'):
                actual=check.elden_ring.added_amount(index,key)
            if self.game=='eldenring' and key.startswith(('create_weapon:','create_armor:')):
                actual=expected if self.elden_ring.physical_equipment[index].verifies(check.elden_ring.physical_equipment[index],key,value) else None
            if self.game=='eldenring' and key.startswith('equipment_slot:'):
                actual=expected if self.elden_ring.equipment_loadouts[index].verifies(check.elden_ring.equipment_loadouts[index],key,value) else None
            if self.game=='eldenring' and key.startswith(('quick_slot:','physick_slot:')):
                actual=expected if self.elden_ring.tool_loadouts[index].verifies(check.elden_ring.tool_loadouts[index],key,value) else None
            if actual is None and self.game=='re1_hd' and key.endswith(':identity') and value==0:
                identifier,quantity=struct.unpack_from('<2I',check.re_hd.plain,field.offset)
                if (identifier,quantity)==(0,0):actual=0
            if actual is None and self.game=='re1_hd' and field.group in ('Inventory','Item box') and not key.endswith(':identity') and value==0:
                identifier,quantity=struct.unpack_from('<2I',check.re_hd.plain,field.offset-4)
                if (identifier,quantity)==(0,0):actual=0
            if actual is None and self.game=='webfishing' and key.startswith('remove_item:'):
                actual=check.webfishing.removed(key)
            if self.game=='webfishing' and key in self.webfishing.hotbar_choices:
                actual=expected if self.webfishing.verify_hotbar(key,value,check.webfishing) else -1
            if actual is None and self.game=='webfishing' and key.startswith('item_lock:'):
                actual=int(int(key.split(':')[1]) in check.info.get('locked_refs',[]))
            if actual is None and self.game=='alice' and not field.fmt:
                kind,_,identifier=key.partition(':')
                if kind in getattr(check.alice,'lists',{}):
                    actual=int(identifier in check.alice.lists[kind][2])
            if actual != expected:
                raise FormatError('Export verification failed.')
        return output

def documents_folder():
    if os.name == 'nt':
        buf = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None,5,None,0,buf) == 0:
            return Path(buf.value)
    return Path.home()/'Documents'

def discover():
    found = []
    appdata = Path(os.environ.get('APPDATA',str(Path.home())))
    for p in (appdata/'EldenRing').glob('*/ER0000.sl2'):
        if p.is_file():found.append(('eldenring',p))
    for p in (appdata/'Godot/app_userdata/webfishing_2_newver').glob('webfishing_save_slot_*.sav'):
        found.append(('webfishing',p))
    steam_roots = {
        Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)'))/'Steam/userdata',
        Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Steam/userdata',
    }
    for steam in steam_roots:
        for p in steam.glob('*/632360/remote/UserProfiles/*.xml'):
            found.append(('ror2',p))
        for p in steam.glob('*/254700/remote/savegame00.sav'):
            found.append(('re4_2005',p))
        for p in steam.glob('*/21690/remote/savedata.bin'):
            found.append(('re5',p))
        for p in steam.glob('*/221040/remote/savedata.bin'):
            found.append(('re6',p))
        for p in steam.glob('*/304240/remote/biodata.bin'):
            found.append(('re1_hd',p))
        from re_engine_save import STEAM_APPS
        for app_id,game in STEAM_APPS.items():
            for p in steam.glob('*/'+app_id+'/remote/win64_save/*.bin'):
                if p.name.casefold().startswith('data'):found.append((game,p))
    docs = documents_folder()
    for folder,game,pattern in (('GTA V','gtav','SGTA5[0-9][0-9][0-9][0-9]'),
            ('GTAV Enhanced','gtav','SGTA5[0-9][0-9][0-9][0-9]'),
            ('Red Dead Redemption 2','rdr2','SRDR[0-9][0-9][0-9][0-9][0-9]')):
        for p in (docs/'Rockstar Games'/folder/'Profiles').glob('*/'+pattern):
            if p.is_file():found.append((game,p))
    base = docs/'My Games/KINGDOM HEARTS HD 1.5+2.5 ReMIX/Steam'
    for name,game in [('KHFM_WW.png','kh1'),('KHReCoM_WW.png','recom'),('KHIIFM_WW.png','kh2'),('KHBbS_WW.png','bbs')]:
        for p in base.glob('*/'+name):
            found.append((game,p))
    for p in (docs/'My Games/Alice Madness Returns/AliceGame/CheckPoint').glob('*/PersistentData_PC.PSD'):
        found.append(('alice',p))
        config = p.with_name('GameConfig_PC.CFG')
        if config.is_file():found.append(('alice',config))
    for p in (docs/'Max Payne Savegames').glob('*.mps'):
        found.append(('maxpayne',p))
    for p in (docs/'My Games/KINGDOM HEARTS HD 2.8 Final Chapter Prologue/Steam').glob('*/KH3DHD*.png'):
        found.append(('ddd',p))
    for p in (docs/'My Games/KINGDOM HEARTS III/Steam').glob('*/SaveGames/kh3sv2/data/KHIII_slot*.bin'):
        found.append(('kh3',p))
    return found

def identify_game(path):
    """Identify supported file names before choosing an extension fallback."""
    path = Path(path)
    name = path.name.casefold()
    if re.fullmatch(r'sgta5\d{4}',name):return 'gtav'
    if re.fullmatch(r'srdr\d{5}',name):return 'rdr2'
    known = {'khfm_ww.png':'kh1', 'khiifm_ww.png':'kh2',
             'kh2fm_ww.png':'kh2', 'khrecom_ww.png':'recom',
             'khbbs_ww.png':'bbs', 'khbbsfm.png':'bbs', 'kh3dhd.png':'ddd',
             'kh3dhd_ww.png':'ddd', 'persistentdata_pc.psd':'alice', 'gameconfig_pc.cfg':'alice',
             'savegame00.sav':'re4_2005', 'er0000.sl2':'eldenring'}
    if name in known:
        return known[name]
    if re.fullmatch(r'khiii_slot\d+\.bin',name):
        return 'kh3'
    extensions = {'.sav':'webfishing', '.xml':'ror2', '.psd':'alice', '.mps':'maxpayne', '.sl2':'eldenring'}
    if path.suffix.casefold() == '.png':
        # Recognize renamed archives by their bounded sqEX layout.
        raw=read_limited(path)
        for name,start,end in png_chunks(raw,allow_sqex_crc=True):
            if name==b'sqEX':
                for game,count,stride in (('kh1',200,0x16c40),('kh2',100,0x10fc0),('recom',100,0x3a30),('bbs',100,0x13c00),('ddd',100,0x16600)):
                    if start == 0x60 and 0 <= end-start-16-count*(0x158+stride) < 0x400:
                        return game
        raise FormatError('This PNG does not contain a supported Kingdom Hearts archive.')
    if path.suffix.casefold() in extensions:
        return extensions[path.suffix.casefold()]
    if path.suffix.casefold() == '.bin':
        raw = read_limited(path)
        if raw.startswith(b'DSSS'):
            from re_engine_save import STEAM_APPS
            for part in path.parts:
                if part in STEAM_APPS:return STEAM_APPS[part]
            from re_engine_container import KEYS,blowfish_cbc
            if len(raw)>=24:
                for game,key in KEYS.items():
                    if blowfish_cbc(raw[16:24],key)==b'DSSSDSSS':return game
            raise FormatError('Open this encrypted Resident Evil file from its game cover so the correct edition can be selected.')
        if raw.startswith(b'S@vE') or (len(raw) == 0x94f4f0+17 and raw[-17] == 8):
            return 'kh3'
        from re5_save import looks_like_re5
        if looks_like_re5(raw):return 're5'
        from re6_save import looks_like_re6
        if looks_like_re6(raw):return 're6'
        from re_hd_save import looks_like_hd
        if looks_like_hd(raw):return 're1_hd'
    raise FormatError('Choose a supported .sav, .sl2, .png, .mps, .bin, .xml, .PSD, or GameConfig_PC.CFG file.')

def backup_files(source):
    """Only list backups associated with this active file or its default export."""
    source = Path(source)
    patterns = (source.name+'.original-*.bak',
                source.stem+'.edited'+source.suffix+'.original-*.bak')
    backups = {path for pattern in patterns for path in source.parent.glob(pattern) if path.is_file()}
    return sorted(backups, key=lambda path:path.stat().st_mtime_ns, reverse=True)

def restore_backup(source, backup, game, account_id=None):
    """Validate an existing backup and restore it without creating another."""
    source, backup = Path(source).resolve(), Path(backup).resolve()
    if source == backup or os.path.samefile(source,backup):
        raise ValueError('Choose a backup other than the active save.')
    original = read_limited(source)
    restored = read_limited(backup)
    Save(restored, game, path=source, account_id=account_id)
    return replace_current(source, original, restored)

def read_limited(path):
    with Path(path).open('rb') as file:
        data = file.read(MAX_SIZE+1)
    if len(data)>MAX_SIZE:
        raise FormatError('The file exceeds 64 MB.')
    return data

def export_copy(source, original, edited, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if source == target or (target.exists() and os.path.samefile(source,target)):
        raise ValueError('Choose a file other than the original.')
    if source.read_bytes() != original:
        raise ValueError('The original save changed. Reopen it before exporting.')
    if target.exists():
        raise ValueError('That file already exists. Choose another name to preserve it.')
    backup = target.parent / (target.name+'.original-'+uuid.uuid4().hex[:8]+'.bak')
    with backup.open('xb') as file:
        file.write(original)
        file.flush()
        os.fsync(file.fileno())
    try:
        with target.open('xb') as file:
            file.write(edited)
            file.flush()
            os.fsync(file.fileno())
    except Exception:
        # Keep the original backup even if exporting fails.
        raise
    if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(edited).digest():
        raise OSError('Exported file verification failed.')
    return backup

def replace_current(source, original, edited):
    """Verify and atomically update the opened save without creating a backup."""
    source = Path(source).resolve()
    if source.read_bytes() != original:
        raise ValueError('The original save changed. Reopen it before applying changes.')
    token = uuid.uuid4().hex[:8]
    temporary = source.with_name(source.name+'.update-'+token+'.tmp')
    try:
        with temporary.open('xb') as file:
            file.write(edited)
            file.flush()
            os.fsync(file.fileno())
        if hashlib.sha256(temporary.read_bytes()).digest() != hashlib.sha256(edited).digest():
            raise OSError('Temporary file verification failed.')
        # Recheck immediately before replacement so an in-game save is never lost.
        if source.read_bytes() != original:
            raise ValueError('The save changed while you were editing. The file was not replaced.')
        os.replace(temporary,source)
        if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(edited).digest():
            with temporary.open('xb') as file:
                file.write(original)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary,source)
            raise OSError('Verification failed and the original save was restored.')
    finally:
        if temporary.exists():
            temporary.unlink()
    return source

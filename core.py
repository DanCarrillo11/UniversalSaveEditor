"""UniversalSaveEditor: byte-preserving save inspection and explicit field patches.

SPDX-License-Identifier: GPL-3.0-or-later
Format references and attribution: SOURCES.md.
"""
from dataclasses import dataclass
from pathlib import Path
import ctypes
import hashlib
import math
import os
import re
import struct
import uuid
import xml.etree.ElementTree as ET
import zlib
from kh_items import ITEMS
from ror2_unlocks import UNLOCK_IDS, unlock_group, unlock_label

MAX_SIZE = 64 * 1024 * 1024

class FormatError(ValueError):
    pass

@dataclass
class Field:
    key: str
    label: str
    value: int
    offset: int
    fmt: str
    minimum: int = 0
    maximum: int = 999999
    group: str = ''
    decimal: bool = False

    def parse(self, text):
        try:
            value = float(text) if self.decimal else int(text)
        except (ValueError, TypeError):
            raise ValueError('enter a valid number' if self.decimal else 'enter a whole number')
        self.validate(value)
        return value

    def validate(self, value):
        if type(value) not in ((int, float) if self.decimal else (int,)) or not math.isfinite(value) or not self.minimum <= value <= self.maximum:
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
    def __init__(self, raw, game):
        if not raw or len(raw) > MAX_SIZE:
            raise FormatError('Unsupported file size (64 MB maximum).')
        self.raw, self.game, self.slots, self.crc_regions = raw, game, [], []
        self.warnings = []
        if game == 'webfishing':
            self._webfishing()
        elif game == 'ror2':
            self._ror2()
        elif game == 'kh1':
            self._kh1()
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
        def add(path, key, label, low, high, group, decimal=False):
            node=reader.nodes.get(path)
            if node and node[1] in ('<i','<q','<f','<d'):
                if not math.isfinite(node[2]):
                    raise FormatError('Invalid value: '+label)
                fields.append(Field(key,label,node[2],node[0],node[1],low,high,group,decimal and node[1] in ('<f','<d')))
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
        for index,item in enumerate(self.info['inventory']):
            if not isinstance(item,dict):continue
            name=f'{index+1} · {item.get("id","Item")}'
            add(('inventory',index,'quality'),f'item:{index}:quality',name+' · quality (0–5)',0,5,'Inventory')
            add(('inventory',index,'size'),f'item:{index}:size',name+' · size',0.001,999999,'Inventory',True)
        journal=self.info.get('journal',{})
        if isinstance(journal,dict):
            for category,entries in journal.items():
                if not isinstance(entries,dict):continue
                for fish,entry in entries.items():
                    if not isinstance(entry,dict):continue
                    name=f'{category} / {fish}'
                    add(('journal',category,fish,'count'),f'journal:{category}:{fish}:count',name+' · catches',0,9999999,'Journal')
                    add(('journal',category,fish,'record'),f'journal:{category}:{fish}:record',name+' · record',0,999999,'Journal',True)
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
            if name not in stat_specs or name in seen:
                continue
            seen.add(name); label,low,high,group,decimal = stat_specs[name]
            add_value('stat:'+name,label,match.group(2),match.start(2),low,high,group,decimal)
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
        chunks = png_chunks(self.raw, allow_sqex_crc=True)
        regions = [(start,end) for name,start,end in chunks if name == b'sqEX']
        if len(regions) != 1:
            raise FormatError('A single sqEX block is required.')
        start,end = regions[0]
        self.crc_regions = regions
        if zlib.crc32(self.raw[start-4:end]) != struct.unpack_from('>I',self.raw,end)[0]:
            self.warnings.append('The save block CRC does not match. You may inspect the save, but exporting requires repairing the CRC in the copy. This does not prove that the internal data is intact.')
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
            for char,namechar in enumerate(('Sora','Donald','Goofy')):
                stat = record+4+char*0x74
                for delta,keyname,label,low,high in [(1,'hp_current','Current HP',0,255),(2,'hp','Base HP',1,255),(3,'mp_current','Current MP',0,255),(4,'mp','Base MP',1,255),(5,'ap','Base AP',0,255),(6,'strength','Strength',0,255),(7,'defense','Defense',0,255)]:
                    fields.append(Field(f'{char}:{keyname}',f'{namechar} · {label}',self.raw[stat+delta],stat+delta,'<B',low,high))
            for item_id,item_name,category in ITEMS:
                offset=record+0x499+item_id
                group={'Synthesis':'Materials','Accessory':'Accessories','Keyblade':'Weapons','Staff':'Weapons','Shield':'Weapons'}.get(category,'Items')
                fields.append(Field(f'inventory:{item_id}',item_name,self.raw[offset],offset,'<B',0,99,group))
            level = self.raw[record+4]
            self.slots.append(Slot(f'{name or str(index+1)} · Sora level {level}',fields))
        if not self.slots:
            raise FormatError('No compatible Kingdom Hearts Final Mix saves were found.')

    def patched(self, changes, repair_crc=False):
        if self.warnings and not repair_crc:
            raise ValueError('Enable CRC repair before exporting this copy.')
        result = bytearray(self.raw)
        known = {(i,f.key):f for i,s in enumerate(self.slots) for f in s.fields}
        for key,value in changes.items():
            if key not in known:
                raise ValueError('Unauthorized field.')
            field = known[key]
            field.validate(value)
            if field.fmt and not field.fmt.startswith('xml-'):
                struct.pack_into(field.fmt,result,field.offset,value)
        if self.game == 'webfishing':
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
                result[start:end] = godot_string_array(unlocked)
                struct.pack_into('<I', result, 0, len(result)-4)
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
        for start,end in self.crc_regions:
            struct.pack_into('>I',result,end,zlib.crc32(result[start-4:end]))
        output = bytes(result)
        # Reparse and assert every requested field before returning data to the UI.
        check = Save(output,self.game)
        for (index,key),value in changes.items():
            field=known[(index,key)]
            if field.fmt.startswith('xml-'):
                expected=value
            else:
                expected=struct.unpack(field.fmt,struct.pack(field.fmt,value))[0] if field.fmt else value
            if next(f.value for f in check.slots[index].fields if f.key == key) != expected:
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
    for p in (appdata/'Godot/app_userdata/webfishing_2_newver').glob('webfishing_save_slot_*.sav'):
        found.append(('webfishing',p))
    steam_roots = {
        Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)'))/'Steam/userdata',
        Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Steam/userdata',
    }
    for steam in steam_roots:
        for p in steam.glob('*/632360/remote/UserProfiles/*.xml'):
            found.append(('ror2',p))
    docs = documents_folder()
    base = docs/'My Games/KINGDOM HEARTS HD 1.5+2.5 ReMIX/Steam'
    for name,game in [('KHFM_WW.png','kh1'),('KHReCoM_WW.png','recom'),('KH2FM_WW.png','kh2'),('KHBbS_WW.png','bbs')]:
        for p in base.glob('*/'+name):
            found.append((game,p))
    for p in (docs/'Max Payne Savegames').glob('*.mps'):
        found.append(('maxpayne',p))
    return found

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
    """Atomically replace the active save after creating an exact backup."""
    source = Path(source).resolve()
    if source.read_bytes() != original:
        raise ValueError('The original save changed. Reopen it before applying changes.')
    token = uuid.uuid4().hex[:8]
    backup = source.with_name(source.name+'.original-'+token+'.bak')
    temporary = source.with_name(source.name+'.update-'+token+'.tmp')
    with backup.open('xb') as file:
        file.write(original)
        file.flush()
        os.fsync(file.fileno())
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
            restore = source.with_name(source.name+'.restore-'+token+'.tmp')
            restore.write_bytes(original)
            os.replace(restore,source)
            raise OSError('Verification failed and the original save was restored.')
    finally:
        if temporary.exists():
            temporary.unlink()
    return backup

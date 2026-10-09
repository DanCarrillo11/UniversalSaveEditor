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
import struct
import uuid
import zlib
from kh_items import ITEMS

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
            raise ValueError('introduce un número válido' if self.decimal else 'introduce un número entero')
        self.validate(value)
        return value

    def validate(self, value):
        if type(value) not in ((int, float) if self.decimal else (int,)) or not math.isfinite(value) or not self.minimum <= value <= self.maximum:
            raise ValueError(f'{self.label}: usa un valor entre {self.minimum} y {self.maximum}.')

@dataclass
class Slot:
    name: str
    fields: list

class GodotReader:
    def __init__(self, data):
        self.data, self.pos, self.nodes = data, 4, {}
        if len(data) < 8 or struct.unpack_from('<I', data)[0] != len(data)-4:
            raise FormatError('Longitud de partida Godot incorrecta.')

    def take(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise FormatError('Partida truncada.')
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
        if depth > 64:
            raise FormatError('Estructura demasiado profunda.')
        header = self.number('I')
        kind, flags = header & 65535, header >> 16
        if flags and (kind not in (2, 3) or flags != 1):
            raise FormatError('Flags Godot no compatibles.')
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
                raise FormatError('Cantidad de elementos inválida.')
            result = {} if kind == 18 else []
            for index in range(count):
                if kind == 18:
                    key = self.read((), depth+1)
                    if not isinstance(key, (str, int)) or key in result:
                        raise FormatError('Clave Godot no compatible o duplicada.')
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
                raise FormatError('Array inválido.')
            return [self.string() for _ in range(count)]
        raise FormatError(f'Tipo Godot {kind} no compatible. No se editará el archivo.')

def png_chunks(raw, allow_sqex_crc=False):
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise FormatError('No es un contenedor PNG de Kingdom Hearts.')
    pos, chunks = 8, []
    while pos + 12 <= len(raw):
        size = struct.unpack_from('>I', raw, pos)[0]
        name, start, end = raw[pos+4:pos+8], pos+8, pos+8+size
        if end+4 > len(raw):
            raise FormatError('Contenedor truncado.')
        if zlib.crc32(raw[pos+4:end]) != struct.unpack_from('>I', raw, end)[0] and not (allow_sqex_crc and name == b'sqEX'):
            raise FormatError(f'CRC inválido en {name!r}.')
        chunks.append((name,start,end))
        pos = end+4
        if name == b'IEND':
            if pos != len(raw):
                raise FormatError('Datos inesperados tras IEND.')
            return chunks
    raise FormatError('Falta IEND.')

class Save:
    def __init__(self, raw, game):
        if not raw or len(raw) > MAX_SIZE:
            raise FormatError('Tamaño de archivo no compatible (máximo 64 MB).')
        self.raw, self.game, self.slots, self.crc_regions = raw, game, [], []
        self.warnings = []
        if game == 'webfishing':
            self._webfishing()
        elif game == 'kh1':
            self._kh1()
        else:
            raise FormatError('La edición de este juego todavía no está implementada.')

    def _webfishing(self):
        reader = GodotReader(self.raw)
        self.info = reader.read()
        if reader.pos != len(self.raw) or not isinstance(self.info,dict):
            raise FormatError('Estructura WEBFISHING no compatible.')
        if not {'inventory','money','bait_inv','level'} <= self.info.keys():
            raise FormatError('No parece una partida de jugador de WEBFISHING.')
        if not isinstance(self.info['inventory'],list) or not isinstance(self.info['bait_inv'],dict):
            raise FormatError('Inventario o cebos con estructura no compatible.')
        fields = []
        specs = [('money','Dinero',9999999), ('loan_left','Deuda pendiente',9999999)]
        for key,label,limit in specs:
            node = reader.nodes.get((key,))
            if node and node[1] in ('<i','<q','<f','<d'):
                if not math.isfinite(node[2]):
                    raise FormatError('Valor numérico no válido en '+key)
                fields.append(Field(key,label,node[2],node[0],node[1],0,limit))
        for bait, amount in self.info['bait_inv'].items():
            if not bait:
                continue
            node = reader.nodes.get(('bait_inv',bait))
            if node and node[1] in ('<i','<q'):
                limit = self.info.get('max_bait',100)
                if not isinstance(limit,int) or limit < 0:
                    raise FormatError('Capacidad de cebo inválida.')
                fields.append(Field('bait:'+bait,'Cebo · '+bait,amount,node[0],node[1],0,limit))
        def add(path, key, label, low, high, group, decimal=False):
            node=reader.nodes.get(path)
            if node and node[1] in ('<i','<q','<f','<d'):
                if not math.isfinite(node[2]):
                    raise FormatError('Valor no válido: '+label)
                fields.append(Field(key,label,node[2],node[0],node[1],low,high,group,decimal and node[1] in ('<f','<d')))
        for key,label,low,high,group,decimal in [
            ('level','Nivel',1,50,'Progreso',False),
            ('xp','Experiencia (XP)',0,9999999,'Progreso',True),
            ('fish_caught','Peces capturados',0,9999999,'Progreso',False),
            ('cash_total','Dinero ganado en total',0,9999999,'Economía',False),
            ('max_bait','Capacidad de cebos',1,9999,'Cebos',False),
            ('rod_power','Potencia de caña',0,5,'Mejoras',False),
            ('rod_speed','Velocidad de caña',0,5,'Mejoras',False),
            ('rod_chance','Probabilidad de caña',0,5,'Mejoras',False),
            ('rod_luck','Suerte de caña',0,5,'Mejoras',False),
            ('buddy_level','Nivel del compañero',0,5,'Mejoras',False),
            ('buddy_speed','Velocidad del compañero',0,5,'Mejoras',False),
        ]: add((key,),key,label,low,high,group,decimal)
        for index,item in enumerate(self.info['inventory']):
            if not isinstance(item,dict):continue
            name=f'{index+1} · {item.get("id","Objeto")}'
            add(('inventory',index,'quality'),f'item:{index}:quality',name+' · calidad (0–5)',0,5,'Inventario')
            add(('inventory',index,'size'),f'item:{index}:size',name+' · tamaño',0.001,999999,'Inventario',True)
        journal=self.info.get('journal',{})
        if isinstance(journal,dict):
            for category,entries in journal.items():
                if not isinstance(entries,dict):continue
                for fish,entry in entries.items():
                    if not isinstance(entry,dict):continue
                    name=f'{category} / {fish}'
                    add(('journal',category,fish,'count'),f'journal:{category}:{fish}:count',name+' · capturas',0,9999999,'Diario')
                    add(('journal',category,fish,'record'),f'journal:{category}:{fish}:record',name+' · récord',0,999999,'Diario',True)
        self.slots = [Slot(f'Nivel {self.info["level"]} · {len(self.info["inventory"])} objetos',fields)]

    def _kh1(self):
        chunks = png_chunks(self.raw, allow_sqex_crc=True)
        regions = [(start,end) for name,start,end in chunks if name == b'sqEX']
        if len(regions) != 1:
            raise FormatError('Falta un bloque sqEX único.')
        start,end = regions[0]
        self.crc_regions = regions
        if zlib.crc32(self.raw[start-4:end]) != struct.unpack_from('>I',self.raw,end)[0]:
            self.warnings.append('El CRC del bloque de guardado no coincide. Puedes inspeccionar la partida; exportarla requiere reparar el CRC de la copia. Esto no demuestra que los datos internos estén íntegros.')
        # PC archive: 200 entries, 0x158-byte descriptors, 0x16c40-byte records.
        archive = start+16
        if archive != 0x70 or not 0 <= end-(archive+200*0x158+200*0x16c40) < 0x400:
            raise FormatError('Distribución KH Final Mix de Steam no reconocida.')
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
                raise FormatError('Registro KHFM fuera de límites.')
            record = base+index*0x16c40
            if length < 0x16c00 or self.raw[record:record+4] != b'\x05\0\0\0':
                continue
            name = bytes(table[desc:desc+0x40]).split(b'\0')[0].decode('ascii',errors='replace')
            fields = [Field('munny','Platines (munny)',struct.unpack_from('<I',self.raw,record+0x1641c)[0],record+0x1641c,'<I',0,999999)]
            for char,namechar in enumerate(('Sora','Donald','Goofy')):
                stat = record+4+char*0x74
                for delta,keyname,label,low,high in [(1,'hp_current','VT actuales',0,255),(2,'hp','VT base',1,255),(3,'mp_current','PM actuales',0,255),(4,'mp','PM base',1,255),(5,'ap','PH base',0,255),(6,'strength','Fuerza',0,255),(7,'defense','Defensa',0,255)]:
                    fields.append(Field(f'{char}:{keyname}',f'{namechar} · {label}',self.raw[stat+delta],stat+delta,'<B',low,high))
            for item_id,item_name,category in ITEMS:
                offset=record+0x499+item_id
                group={'Synthesis':'Materiales','Accessory':'Accesorios','Keyblade':'Armas','Staff':'Armas','Shield':'Armas'}.get(category,'Objetos')
                fields.append(Field(f'inventory:{item_id}',item_name,self.raw[offset],offset,'<B',0,99,group))
            level = self.raw[record+4]
            self.slots.append(Slot(f'{name or str(index+1)} · Sora nivel {level}',fields))
        if not self.slots:
            raise FormatError('No se encontraron partidas KH Final Mix compatibles.')

    def patched(self, changes, repair_crc=False):
        if self.warnings and not repair_crc:
            raise ValueError('Marca la reparación del CRC para exportar esta copia.')
        result = bytearray(self.raw)
        known = {(i,f.key):f for i,s in enumerate(self.slots) for f in s.fields}
        for key,value in changes.items():
            if key not in known:
                raise ValueError('Campo no autorizado.')
            field = known[key]
            field.validate(value)
            struct.pack_into(field.fmt,result,field.offset,value)
        if self.game == 'webfishing':
            capacity=changes.get((0,'max_bait'),self.info.get('max_bait',100))
            for field in self.slots[0].fields:
                if field.key.startswith('bait:') and changes.get((0,field.key),field.value)>capacity:
                    raise ValueError('La cantidad de cebo supera la capacidad seleccionada.')
        for start,end in self.crc_regions:
            struct.pack_into('>I',result,end,zlib.crc32(result[start-4:end]))
        output = bytes(result)
        # Reparse and assert every requested field before returning data to the UI.
        check = Save(output,self.game)
        for (index,key),value in changes.items():
            field=known[(index,key)]
            expected=struct.unpack(field.fmt,struct.pack(field.fmt,value))[0]
            if next(f.value for f in check.slots[index].fields if f.key == key) != expected:
                raise FormatError('La verificación de la exportación falló.')
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
        raise FormatError('El archivo supera 64 MB.')
    return data

def export_copy(source, original, edited, target):
    source, target = Path(source).resolve(), Path(target).resolve()
    if source == target or (target.exists() and os.path.samefile(source,target)):
        raise ValueError('Elige un archivo distinto del original.')
    if source.read_bytes() != original:
        raise ValueError('La partida original cambió. Vuelve a abrirla antes de exportar.')
    if target.exists():
        raise ValueError('Ese archivo ya existe. Elige otro nombre para conservarlo.')
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
        raise OSError('La verificación del archivo exportado falló.')
    return backup

def replace_current(source, original, edited):
    """Atomically replace the active save after creating an exact backup."""
    source = Path(source).resolve()
    if source.read_bytes() != original:
        raise ValueError('La partida original cambió. Vuelve a abrirla antes de aplicar los cambios.')
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
            raise OSError('La verificación del archivo temporal falló.')
        # Recheck immediately before replacement so an in-game save is never lost.
        if source.read_bytes() != original:
            raise ValueError('La partida cambió mientras editabas. No se reemplazó el archivo.')
        os.replace(temporary,source)
        if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(edited).digest():
            restore = source.with_name(source.name+'.restore-'+token+'.tmp')
            restore.write_bytes(original)
            os.replace(restore,source)
            raise OSError('La verificación falló y se restauró la partida original.')
    finally:
        if temporary.exists():
            temporary.unlink()
    return backup

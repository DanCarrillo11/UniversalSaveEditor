"""Kingdom Hearts III PC save container and field editor.

Adapted from Kingdom Save Editor, GPL-3.0-or-later.
Copyright (C) 2020 Luciano Ciccariello
Copyright (C) 2026 Mikko Mäntylä (BFlorry)
PC layout contributions: fungualtissue1230; key derivation: dedede123.
Preserves padding, unknown flags, equipment, photographs and world state.
"""
import hashlib
import re
import struct
import zlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from kh_extra_tables import KH3_ITEMS
from collection_tables import KH3_MATERIALS
from kh3_characters import Kh3CharacterFeatures


class AccountIdRequired(ValueError):
    pass


def account_from_path(path):
    parts = re.split(r'[/\\]', str(path or ''))
    for i in range(1, len(parts)):
        if parts[i].lower() == 'savegames' and re.fullmatch(r'[0-9A-Za-z_-]{1,64}', parts[i-1]):
            return parts[i-1]
    return None


def derive_key(account):
    if not isinstance(account, str) or not re.fullmatch(r'[0-9A-Za-z_-]{1,64}', account):
        raise ValueError('Enter the platform account ID that originally created this save.')
    mask = b'hN96q4X9f%BCURBV&pMT4kcvqTMhHYD&'
    table = b'ABCDE!#$%&FGHIJ012345KLMNOPqrstuvwxyzQRSTUVWXYZ6789abcdefgh},.<>ijklmnop()=~|-^+*;:[]{/?_@'
    data = account.encode('ascii')
    return bytes(table[(mask[i] ^ data[(i+1) % len(data)]) % len(table)] for i in range(32))


def transform(data, account, encrypt=False):
    cipher = Cipher(algorithms.AES(derive_key(account)), modes.ECB())
    context = cipher.encryptor() if encrypt else cipher.decryptor()
    return context.update(data) + context.finalize()


class Kh3PcSave:
    def __init__(self, raw, Field, path=None, account_id=None):
        self.raw, self.warnings = bytes(raw), []
        self.account = account_id or account_from_path(path)
        self.encrypted = not raw.startswith(b'S@vE')
        if self.encrypted:
            if len(raw) < 33 or (len(raw)-17) % 16 or raw[-17] != 8:
                raise ValueError('Unrecognized Kingdom Hearts III PC container.')
            if not self.account:
                raise AccountIdRequired('This PC save is encrypted. Open it in its original account folder or enter the account ID that created it.')
            plain = transform(raw[:-17], self.account)
        else:
            plain = bytes(raw)
        if len(plain) != 0x94f4f0 or plain[:4] != b'S@vE' or struct.unpack_from('<I', plain, 4)[0] != 0x94f4d8:
            raise ValueError('Wrong account ID or unsupported Kingdom Hearts III PC save layout.')
        self.plain = plain
        self.hash_end = 0x94f4e8
        if self.encrypted and hashlib.md5(plain[:self.hash_end]).digest() != raw[-16:]:
            raise ValueError('The encrypted save digest does not match. The file may be damaged.')
        if zlib.crc32(plain[16:self.hash_end]) != struct.unpack_from('<I', plain, 12)[0]:
            self.warnings.append('The internal save CRC does not match. Enable integrity repair before applying changes.')
        if plain[0x14] not in range(4):
            raise ValueError('Unsupported Kingdom Hearts III difficulty.')
        self.fields = []
        def add(key, label, offset, fmt, maximum, group, minimum=0, **options):
            self.fields.append(Field(key, label, struct.unpack_from(fmt, plain, offset)[0], offset, fmt, minimum, maximum, group, **options))
        add('difficulty', 'Difficulty', 0x14, '<B', 3, 'Difficulty', choices=('Beginner','Standard','Proud','Critical'))
        add('munny', 'Munny', 0x28, '<i', 9999999, 'Currency')
        add('experience', 'Experience', 0x24, '<i', 99999999, 'Level and experience')
        add('level', 'Sora level', 0x2c, '<B', 99, 'Level and experience', 1)
        for name, offset in (('HP',0xb49c),('MP',0xb4a0),('Strength',0xb4a4),('Magic',0xb4a8),('Defense',0xb4ac)):
            add('bonus:'+name, 'Sora · Bonus '+name, offset, '<i', 999, 'Attributes')
        characters = ('Sora','Donald','Goofy','Hercules','Woody','Buzz','Rapunzel','Flynn','Sulley','Mike','Marshmallow','Baymax','Jack','Riku','Mickey')
        for index, name in enumerate(characters):
            base = 0x1880 + index*0x9c0
            for delta, key, label, fmt, maximum in (
                (0x980,'strength','Strength boosts','<B',255), (0x981,'magic','Magic boosts','<B',255),
                (0x982,'defense','Defense boosts','<B',255), (0x983,'ap','AP boosts','<B',255),
                (0x984,'hp','HP','<i',9999), (0x988,'mp','MP','<i',9999), (0x98c,'focus','Focus','<i',9999)):
                add(f'character:{name}:{key}', name+' · '+label, base+delta, fmt, maximum, 'Attributes')
        for identifier, (name, group) in KH3_ITEMS.items():
            if 0 <= identifier < 1024:
                add(f'inventory:{identifier}', name, 0x8f4 + identifier*2, '<B', 99, group,item_id=identifier)
        for material in range(100):
            known=material<len(KH3_MATERIALS)
            name=KH3_MATERIALS[material] if known else f'Unidentified material · Entry {material+1:03d}'
            add(f'material:{material}', name, 0x165e+material*2, '<h', 999, 'Materials',
                collection='Materials' if known else 'Unidentified materials',
                note=f'Saved material index {material}. '+('Verified material order.' if known else 'Name mapping is pending; this entry keeps its saved index.'))
        self.characters=Kh3CharacterFeatures(plain,Field)
        self.fields.extend(self.characters.fields)

    def patch(self, changes):
        result = bytearray(self.plain)
        fields = {f.key:f for f in self.fields}
        for key, value in changes.items():
            field = fields[key]
            if not field.fmt:continue
            struct.pack_into(field.fmt, result, field.offset, value)
            if key.startswith('inventory:') and value > 0:
                result[field.offset+1] |= 1  # Obtained; preserve all other flags.
        self.characters.patch(result,changes)
        struct.pack_into('<I', result, 12, zlib.crc32(result[16:self.hash_end]))
        plain = bytes(result)
        if self.encrypted:
            return bytearray(transform(plain, self.account, True) + b'\x08' + hashlib.md5(plain[:self.hash_end]).digest())
        return result

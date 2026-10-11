"""KH2 Steam containers can mix system metadata and player records."""
import struct
import unittest
import zlib
from core import Save, FormatError, png_chunks
from test_core import kingdom2


def mixed_archive(system_index=0, player_index=1):
    raw = bytearray(kingdom2())
    start, end = next((s, e) for n, s, e in png_chunks(raw) if n == b'sqEX')
    archive = start + 16
    table = bytearray(raw[archive:archive+100*0x158])
    key = bytes(table[0xe0:0xf0])
    for index in range(0xf0): table[index] ^= key[index % 16]
    descriptor = bytes(table[:0x158])
    table[:0x158] = bytes(0x158)
    table[player_index*0x158:(player_index+1)*0x158] = descriptor
    name = b'BISLPM-66675FM-SYS\0'
    pos = system_index*0x158
    table[pos:pos+len(name)] = name
    struct.pack_into('<I', table, pos+0x50, 0x400)
    # Retain a real obfuscation key even when descriptor zero is unused.
    table[0xe0:0xf0] = bytes(16)
    for index in range(0xf0): table[index] ^= key[index % 16]
    raw[archive:archive+len(table)] = table
    stride = 0x10fc0
    base = archive + len(table)
    player = bytes(raw[base:base+stride])
    raw[base:base+stride] = bytes(stride)
    raw[base+player_index*stride:base+(player_index+1)*stride] = player
    system = base + system_index*stride
    raw[system:system+stride] = bytes((i*17+7) % 256 for i in range(stride))
    raw[system:system+4] = b'KH2S'
    struct.pack_into('<I', raw, system+4, 0x1504a)
    struct.pack_into('>I', raw, end, zlib.crc32(raw[start-4:end]))
    return bytes(raw), system, base+player_index*stride, start, end


class Kh2SystemTests(unittest.TestCase):
    def test_system_record_before_player_opens_without_becoming_editable(self):
        raw, system, player, start, end = mixed_archive()
        save = Save(raw, 'kh2')
        self.assertEqual(len(save.slots), 1)
        self.assertEqual(next(f.offset for f in save.slots[0].fields if f.key == 'munny'), player+0x2440)
        self.assertFalse(save.warnings)
        self.assertEqual(save.patched({}), raw)

    def test_edits_and_integrity_repair_preserve_all_system_bytes(self):
        raw, system, player, start, end = mixed_archive()
        save = Save(raw, 'kh2')
        output = save.patched({(0, 'munny'): 1234, (0, 'difficulty'): 3})
        self.assertEqual(output[system:system+0x10fc0], raw[system:system+0x10fc0])
        self.assertFalse(Save(output, 'kh2').warnings)
        broken = bytearray(raw); broken[player+8] ^= 1
        struct.pack_into('>I', broken, end, zlib.crc32(broken[start-4:end]))
        repaired = Save(bytes(broken), 'kh2').patched({}, repair_crc=True)
        self.assertEqual(repaired[system:system+0x10fc0], raw[system:system+0x10fc0])
        self.assertFalse(Save(repaired, 'kh2').warnings)

    def test_system_can_follow_player_or_use_another_archive_position(self):
        for system_index, player_index in ((1, 0), (6, 7)):
            with self.subTest(system_index=system_index):
                raw, system, player, start, end = mixed_archive(system_index, player_index)
                self.assertEqual(len(Save(raw, 'kh2').slots), 1)

    def test_short_unknown_player_and_oversized_system_remain_rejected(self):
        raw, system, player, start, end = mixed_archive()
        invalid = bytearray(raw); invalid[system:system+4] = b'KH2J'
        with self.assertRaises(FormatError): Save(bytes(invalid), 'kh2')
        for length in (0x401, 0x10fc1):
            invalid = bytearray(raw)
            archive = start+16
            table = bytearray(invalid[archive:archive+100*0x158]); key = table[0xe0:0xf0]
            for i in range(0xf0): table[i] ^= key[i % 16]
            struct.pack_into('<I', table, 0x50, length)
            for i in range(0xf0): table[i] ^= key[i % 16]
            invalid[archive:archive+len(table)] = table
            with self.subTest(length=length), self.assertRaises(FormatError): Save(bytes(invalid), 'kh2')

    def test_system_only_archive_has_no_editable_parties(self):
        raw, system, player, start, end = mixed_archive()
        invalid = bytearray(raw)
        # Descriptor one is outside the obfuscated prefix.
        struct.pack_into('<I', invalid, start+16+0x158+0x50, 0)
        struct.pack_into('>I', invalid, end, zlib.crc32(invalid[start-4:end]))
        with self.assertRaisesRegex(FormatError, 'No saved Kingdom Hearts II slots'):
            Save(bytes(invalid), 'kh2')


if __name__ == '__main__':
    unittest.main()

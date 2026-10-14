import struct
import unittest
import zlib
from core import Save, png_chunks
from test_expansion import kh_fixture


def fixture():
    raw, record, *_ = kh_fixture('kh1'); raw = bytearray(raw)
    raw[record + 0x74] = 0x89  # Fire, Cure and an unrelated reserved bit.
    raw[record + 0x844:record + 0x847] = bytes((0, 3, 255))
    start, end = next((s, e) for n, s, e in png_chunks(raw, True) if n == b'sqEX')
    struct.pack_into('>I', raw, end, zlib.crc32(raw[start - 4:end]))
    return bytes(raw), record


class Kh1ShortcutTests(unittest.TestCase):
    def test_known_shortcuts_require_sora_availability_and_clear_on_removal(self):
        raw, record = fixture(); s = Save(raw, 'kh1')
        with self.assertRaises(ValueError): s.patched({(0, 'magic_shortcut:2'): 1})
        out = s.patched({(0, 'magic_shortcut:2'): 1, (0, '0:magic:1'): 1})
        self.assertEqual(out[record + 0x846], 1); self.assertEqual(out[record + 0x74], 0x8b)
        cleared = Save(out, 'kh1').patched({(0, '0:magic:0'): 0})
        self.assertEqual(cleared[record + 0x844], 255)
        self.assertEqual(cleared[record + 0x845:record + 0x847], bytes((3, 1)))
        self.assertFalse(Save(cleared, 'kh1').warnings)
        self.assertEqual(s.patched({}), raw)

    def test_unknown_command_is_preserved_and_other_slot_is_unchanged(self):
        raw, record = fixture(); raw = bytearray(raw); raw[record + 0x844] = 250
        start, end = next((s, e) for n, s, e in png_chunks(raw, True) if n == b'sqEX')
        struct.pack_into('>I', raw, end, zlib.crc32(raw[start - 4:end]))
        s = Save(raw, 'kh1'); f = next(f for f in s.slots[0].fields if f.key == 'magic_shortcut:0')
        self.assertTrue(f.readonly)
        out = s.patched({(0, 'magic_shortcut:1'): 0})
        self.assertEqual(out[record + 0x844], 250)
        allowed = {record + 0x845} | set(range(end, end + 4))
        self.assertTrue(all(a == b or i in allowed for i, (a, b) in enumerate(zip(raw, out))))

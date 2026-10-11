import struct
import unittest

from maxpayne_save import MaxPayneArchive, MaxPayneFormatError, Reader
from maxpayne_save import INVENTORY_WEAPONS, MaxPayneEditor
from core import Save


def chunk(identifier, revision, contents):
    return b'\x0c' + struct.pack('<III', identifier, revision, 13 + len(contents)) + contents


def text(value):
    raw = value.encode('latin-1')
    return b'\x0d\x10' + struct.pack('<H', len(raw)) + raw


def fixture(players=1, description='Test save', version=48, payload=None):
    # Synthetic data only; no personal save or extracted game bytes.
    preview = bytes(range(32))
    header = chunk(1, 1, b'\x14' + bytes([version]) + text(description) +
                   b'\x03' + struct.pack('<I', len(preview)) + preview)
    player = chunk(0, 13, payload if payload is not None else
                   b'\x09' + struct.pack('<f', 1.0))
    entities = chunk(17, 1, (chunk(18, 1, text('player')) + player) * players)
    world = chunk(16, 13, text('synthetic_level') + b'\x0e\x00' + entities)
    return header + world + chunk(0, 1, b'') + chunk(0, 4, b'')


def inventory_fixture():
    def integer(value):return b'\x14'+value.to_bytes(1,'little',signed=True)
    entries=[]
    for index,identifiers in enumerate(INVENTORY_WEAPONS):
        body=integer(10 if index==3 else 0)+integer(18 if index==3 else 1)+b'\x0e\0'+integer(len(identifiers))
        body+=b''.join(integer(identifier)+b'\x0e\0' for identifier in identifiers)
        entries.append(chunk(0,1,body))
    inventory=chunk(0,1,integer(3)+integer(14)+b''.join(entries)+chunk(0,3,b'\x09'+struct.pack('<f',0.5))*2)
    return fixture(payload=chunk(0,2,b'\x0e\1')+inventory+text('Preserve unrelated state'))


class MaxPayneEditingTests(unittest.TestCase):
    def test_variable_width_growth_repairs_all_parent_lengths(self):
        raw=inventory_fixture();save=Save(raw,'maxpayne')
        self.assertEqual(save.patched({}),raw)
        out=save.patched({(0,'ammo:3'):150,(0,'weapon:5'):1,(0,'ammo:13'):8})
        self.assertEqual(len(out)-len(raw),3)
        check=Save(out,'maxpayne')
        values={f.key:f.value for f in check.slots[0].fields}
        self.assertEqual(values['ammo:3'],150)
        self.assertEqual(values['weapon:5'],1)
        self.assertEqual(values['ammo:13'],8)
        self.assertEqual(check.maxpayne.preview,save.maxpayne.preview)
        self.assertEqual(check.maxpayne.description,save.maxpayne.description)
        self.assertEqual(check.maxpayne.level,save.maxpayne.level)
        self.assertEqual(out[:save.maxpayne.roots[0].offset],raw[:save.maxpayne.roots[0].offset])
        self.assertTrue(out.endswith(text('Preserve unrelated state')+chunk(0,1,b'')+chunk(0,4,b'')))

    def test_wrong_weapon_id_rejects_modded_inventory(self):
        raw=bytearray(inventory_fixture());save=Save(raw,'maxpayne')
        entry=save.maxpayne.inventory.children[5]
        node=entry.children[4]
        raw[node.offset+1]=99
        with self.assertRaises(ValueError):Save(raw,'maxpayne')

    def test_invalid_changes_and_unrecognized_player_are_rejected(self):
        save=Save(inventory_fixture(),'maxpayne')
        for changes in ({(0,'ammo:13'):9},{(0,'ammo:3'):-1},{(0,'weapon:5'):2},{(1,'ammo:3'):1}):
            with self.assertRaises(ValueError):save.patched(changes)
        with self.assertRaises(ValueError):Save(fixture(),'maxpayne')

    def test_fixed_width_weapon_edit_preserves_other_payload_bytes(self):
        raw=inventory_fixture();save=Save(raw,'maxpayne');out=save.patched({(0,'weapon:5'):1})
        self.assertEqual([i for i,(a,b) in enumerate(zip(raw,out)) if a!=b],[save.maxpayne.nodes['weapon:5'].offset+1])


class MaxPayneReaderTests(unittest.TestCase):
    def test_structural_player_and_preview_preservation(self):
        raw = fixture(description='A considerably longer description')
        save = MaxPayneArchive(raw)
        self.assertEqual(save.description, 'A considerably longer description')
        self.assertEqual(save.level, 'synthetic_level')
        self.assertEqual(save.preview, bytes(range(32)))
        self.assertEqual(save.player.children[0].value, 1.0)
        self.assertEqual(save.raw, raw)

    def test_integer_widths_and_signs(self):
        for tag, width, signed, expected in [
            (0x14, 1, True, -12), (0x13, 2, True, -250),
            (0x12, 3, True, -70000), (0x02, 4, True, -9000000),
            (0x11, 1, False, 200), (0x10, 2, False, 50000),
            (0x0f, 3, False, 9000000), (0x03, 4, False, 4000000000),
        ]:
            with self.subTest(tag=tag):
                raw = bytes([tag]) + expected.to_bytes(width, 'little', signed=signed)
                self.assertEqual(Reader(raw).read(0, len(raw)).value, expected)

    def test_truncation_at_every_byte_is_rejected(self):
        raw = fixture()
        for length in range(len(raw)):
            with self.subTest(length=length), self.assertRaises(MaxPayneFormatError):
                MaxPayneArchive(raw[:length])

    def test_missing_or_duplicate_player_is_rejected(self):
        for count in (0, 2):
            with self.subTest(count=count), self.assertRaises(MaxPayneFormatError):
                MaxPayneArchive(fixture(players=count))

    def test_unsupported_revision_and_unknown_tags_are_rejected(self):
        for raw in (fixture(version=49), fixture(payload=b'\x0b')):
            with self.assertRaises(MaxPayneFormatError):
                MaxPayneArchive(raw)

    def test_invalid_boolean_and_nonfinite_scalar_are_rejected(self):
        for payload in (b'\x0e\x02', b'\x09' + struct.pack('<f', float('nan'))):
            with self.assertRaises(MaxPayneFormatError):
                MaxPayneArchive(fixture(payload=payload))

    def test_child_cannot_escape_parent_bounds(self):
        bad = b'\x0c' + struct.pack('<III', 0, 1, 100)
        with self.assertRaises(MaxPayneFormatError):
            MaxPayneArchive(fixture(payload=bad))

    def test_nesting_limit(self):
        payload = b'\x14\x00'
        for _ in range(70):
            payload = chunk(0, 1, payload)
        with self.assertRaises(MaxPayneFormatError):
            MaxPayneArchive(fixture(payload=payload))

    def test_negative_string_length_and_trailing_bytes(self):
        for raw in (fixture(payload=b'\x0d\x14\xff'), fixture() + b'\x14\x00'):
            with self.assertRaises(MaxPayneFormatError):
                MaxPayneArchive(raw)


if __name__ == '__main__':
    unittest.main()

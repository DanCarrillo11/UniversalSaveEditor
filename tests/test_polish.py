"""Cross-editor input safety and KH1 identified menu snapshot regression checks."""
import struct
import unittest
import zlib
from core import Save,Field,png_chunks
from diagnostics import explain_error,support_report,EDIT_CONFLICTS
from test_core import kingdom

def menu_fixture(foreign=False):
    raw=bytearray(kingdom());start,end=next((a,b) for n,a,b in png_chunks(raw) if n==b'sqEX')
    archive=start+16;table_size=200*0x158;record=archive+table_size;stride=0x16c40
    # Move the second gameplay record to make room for the first record's menu.
    raw[record+2*stride:record+3*stride]=raw[record+stride:record+2*stride]
    raw[archive+2*0x158:archive+3*0x158]=raw[archive+0x158:archive+2*0x158]
    raw[archive+0x158:archive+2*0x158]=bytes(0x158)
    name=b'-01/foreign.bin' if foreign else b'-01/system.bin'
    raw[archive+0x158:archive+0x158+len(name)]=name
    struct.pack_into('<I',raw,archive+0x158+0x50,0x400)
    summary=record+stride;raw[summary:summary+stride]=bytes(stride)
    raw[summary:summary+4]=b'KHSQ';raw[summary+8]=raw[record+4]
    raw[summary+12:summary+38]=b'KEEP CASH XP AND METADATA!!'[:26]
    raw[summary+0x38]=raw[record+0x1642c]
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw),record,summary,end

class PolishTests(unittest.TestCase):
    def test_re6_depleted_reserves_refill_without_editing_weapon_count_words(self):
        from test_re6 import fixture
        from re6_save import checksum
        raw=bytearray(fixture());struct.pack_into('<h',raw,34046,0)
        struct.pack_into('<Hh',raw,34048,272,286) # A weapon's count word is not an ammo stack.
        struct.pack_into('<I',raw,8,checksum(raw));save=Save(raw,'re6')
        ammo=next(f for f in save.slots[0].fields if f.key=='supply:0:0')
        weapon=next(f for f in save.slots[0].fields if f.key=='supply:0:1')
        self.assertIn('9mm',ammo.label);self.assertFalse(ammo.readonly);self.assertTrue(weapon.readonly)
        with self.assertRaises(ValueError):save.patched({(0,weapon.key):10})
        output=save.patched({(0,ammo.key):30})
        self.assertEqual(struct.unpack_from('<Hh',output,34044),(0xb201,30))
        self.assertEqual(output[34048:34052],raw[34048:34052]);self.assertFalse(Save(output,'re6').warnings)
        empty=Save(output,'re6').patched({(0,ammo.key):0})
        self.assertEqual(next(f.value for f in Save(empty,'re6').slots[0].fields if f.key==ammo.key),0)

    def test_extreme_integer_input_has_a_normal_validation_error(self):
        for field in (Field('count','Count',1,0,'<I',0,2**64-1),Field('amount','Amount',1,0,'<f',0,100,decimal=True)):
            for value in (10**999,-10**999,True,float('inf'),float('nan')):
                with self.assertRaises(ValueError):field.validate(value)
            with self.assertRaises(ValueError):field.parse('9'*1000)

    def test_kh1_level_and_difficulty_update_only_the_identified_menu_bytes(self):
        raw,record,summary,end=menu_fixture();save=Save(raw,'kh1');self.assertEqual(len(save.slots),2)
        self.assertEqual(save.kh_menu,{0:summary})
        output=save.patched({(0,'0:level'):90,(0,'difficulty'):2})
        self.assertEqual(output[record+4],90);self.assertEqual(output[summary+8],90)
        self.assertEqual(output[record+0x1642c],2);self.assertEqual(output[summary+0x38],2)
        allowed={record+4,record+0x1642c,summary+8,summary+0x38}|set(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,output))))
        self.assertEqual(output[summary+12:summary+38],raw[summary+12:summary+38]);self.assertFalse(Save(output,'kh1').warnings)

    def test_kh1_menu_like_bytes_with_foreign_directory_identity_are_preserved(self):
        raw,record,summary,end=menu_fixture(True);save=Save(raw,'kh1');self.assertEqual(save.kh_menu,{})
        output=save.patched({(0,'0:level'):90,(0,'difficulty'):2})
        self.assertEqual(output[summary:summary+0x400],raw[summary:summary+0x400])

    def test_known_edit_conflicts_give_specific_fixed_guidance_without_private_data(self):
        private=' C:/Users/PRIVATE_USER/76561198012345678/SECRET.sl2'
        for prefix,message,steps in EDIT_CONFLICTS:
            error=ValueError(prefix+private);problem=explain_error(error,'review')
            self.assertEqual(problem.code,'invalid_edit');self.assertEqual(problem.message,message)
            self.assertEqual(problem.steps,steps)
            text=problem.message+' '.join(problem.steps)+support_report('kh3',problem=problem,operation='review')
            self.assertNotIn('PRIVATE_USER',text);self.assertNotIn('76561198012345678',text)
        self.assertEqual(explain_error(ValueError('unsupported encrypted format'), 'review').code,'account_or_encryption')
        self.assertEqual(explain_error(ValueError('unsupported payload'), 'review').code,'unsupported_format')

if __name__=='__main__':unittest.main()

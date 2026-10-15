"""KH1 shared spell tiers, compact summons, rescue-bit order and preservation."""
import struct
import unittest
from core import Save
from test_expansion import kh_fixture


class Kh1ProgressionTests(unittest.TestCase):
    def test_spell_acquisition_updates_shared_tier_and_availability_without_clearing_reserved_bits(self):
        raw,record,*_=kh_fixture('kh1');raw=bytearray(raw)
        raw[record+0x74]=0x80;raw[record+0xe8]=0x80
        raw[record+0x844]=0
        s=Save(raw,'kh1');out=s.patched({(0,'0:magic:0'):3},repair_crc=True)
        self.assertEqual(out[record+0x492],3)
        self.assertEqual((out[record+0x74],out[record+0xe8]),(0x81,0x81))
        self.assertEqual(next(f.value for f in Save(out,'kh1').slots[0].fields if f.key=='0:magic:0'),3)
        cleared=Save(out,'kh1').patched({(0,'0:magic:0'):0})
        self.assertEqual(cleared[record+0x492],3)
        self.assertEqual((cleared[record+0x74],cleared[record+0xe8],cleared[record+0x844]),(0x80,0x81,255))
        self.assertFalse(Save(cleared,'kh1').warnings)

    def test_explicit_donald_availability_is_respected_and_other_family_bits_are_unchanged(self):
        raw,record,*_=kh_fixture('kh1');raw=bytearray(raw)
        raw[record+0x74]=0x40;raw[record+0xe8]=0x20;s=Save(raw,'kh1')
        out=s.patched({(0,'0:magic:1'):2,(0,'1:magic:1'):0},repair_crc=True)
        self.assertEqual(out[record+0x493],2)
        self.assertEqual((out[record+0x74],out[record+0xe8]),(0x42,0x20))
        self.assertEqual(out[record+0x494:record+0x499],raw[record+0x494:record+0x499])

    def test_compact_summon_acquisition_preserves_original_order_and_checks_unknown_layouts(self):
        raw,record,*_=kh_fixture('kh1');raw=bytearray(raw)
        raw[record+0x7d0:record+0x7d6]=bytes((5,2,255,255,255,255));s=Save(raw,'kh1')
        out=s.patched({(0,'0:summon:0'):1,(0,'0:summon:1'):1},repair_crc=True)
        self.assertEqual(out[record+0x7d0:record+0x7d6],bytes((5,2,0,1,255,255)))
        self.assertEqual(next(f.label for f in s.slots[0].fields if f.key=='0:summon:5'),'Sora · Simba acquired')
        self.assertTrue(next(f.readonly for f in Save(out,'kh1').slots[0].fields if f.key=='0:summon:0'))
        for values in ((5,5,255,255,255,255),(5,255,2,255,255,255),(99,255,255,255,255,255)):
            raw[record+0x7d0:record+0x7d6]=bytes(values);s=Save(raw,'kh1')
            self.assertTrue(all(f.readonly for f in s.slots[0].fields if f.group=='Summons'))
            out=s.patched({(0,'munny'):4321},repair_crc=True)
            self.assertEqual(out[record+0x7d0:record+0x7d6],bytes(values))

    def test_trinity_acquisition_changes_only_its_mask_and_existing_acquisitions_are_protected(self):
        raw,record,start,end=kh_fixture('kh1');raw=bytearray(raw);raw[record+0x1c1b]=0xa0;s=Save(raw,'kh1')
        out=s.patched({(0,'trinity:0'):1,(0,'trinity:4'):1},repair_crc=True)
        self.assertEqual(out[record+0x1c1b],0xb1)
        allowed={record+0x1c1b}|set(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        with self.assertRaises(ValueError):Save(out,'kh1').patched({(0,'trinity:0'):0})

    def test_99_puppy_bits_use_msb_order_and_preserve_last_five_reserved_bits_and_rewards(self):
        raw,record,start,end=kh_fixture('kh1');raw=bytearray(raw);raw[record+0x170f]=31;s=Save(raw,'kh1')
        out=s.patched({(0,'puppy:1'):1,(0,'puppy:8'):1,(0,'puppy:9'):1,(0,'puppy:99'):1},repair_crc=True)
        self.assertEqual((out[record+0x1703],out[record+0x1704],out[record+0x170f]),(0x81,0x80,0x3f))
        self.assertEqual(next(f.value for f in Save(out,'kh1').slots[0].fields if f.key=='puppies_rescued'),4)
        allowed={record+0x1703,record+0x1704,record+0x170f}|set(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        with self.assertRaises(ValueError):Save(out,'kh1').patched({(0,'puppy:99'):0})
        with self.assertRaises(ValueError):s.patched({(0,'puppies_rescued'):99},repair_crc=True)

    def test_remaining_torn_pages_are_bounded_and_do_not_change_story_or_other_slots(self):
        raw,record,start,end=kh_fixture('kh1');s=Save(raw,'kh1')
        out=s.patched({(0,'torn_pages'):5});allowed={record+0x1400}|set(range(end,end+4))
        self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,out))))
        self.assertEqual(out[record+0x1400],5);self.assertFalse(Save(out,'kh1').warnings)
        with self.assertRaises(ValueError):s.patched({(0,'torn_pages'):6})
        raw=bytearray(raw);raw[record+0x1400]=200;s=Save(raw,'kh1')
        self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='torn_pages'))
        self.assertEqual(s.patched({(0,'munny'):999},repair_crc=True)[record+0x1400],200)

    def test_unknown_shared_spell_tiers_are_not_invented_and_patches_do_not_mutate_inputs(self):
        raw,record,*_=kh_fixture('kh1');raw=bytearray(raw)
        for value in (0,4,255):
            raw[record+0x492]=value;s=Save(raw,'kh1');before=bytes(s.raw)
            self.assertTrue(next(f.readonly for f in s.slots[0].fields if f.key=='0:magic:0'))
            with self.assertRaises(ValueError):s.patched({(0,'0:magic:0'):3},repair_crc=True)
            out=s.patched({(0,'munny'):999},repair_crc=True)
            self.assertEqual(out[record+0x492],value);self.assertEqual(bytes(s.raw),before)


if __name__=='__main__':unittest.main()

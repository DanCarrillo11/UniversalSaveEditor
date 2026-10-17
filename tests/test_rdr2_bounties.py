import struct,unittest
from core import Save
from rockstar_container import u32
from test_rdr2_features import fixture


class BountyTests(unittest.TestCase):
    def save(self,**kwargs):return Save(fixture(bounties=True,**kwargs),'rdr2')

    def test_clear_synchronizes_regions_and_native_amount_and_preserves_story_bits(self):
        for encrypted in (False,True):
            s=self.save(encrypted=encrypted);b=s.rockstar.rdr2.campaign.bounties
            out=s.patched({(0,'bounty:clear'):1});after=Save(out,'rdr2');plain=after.rockstar.container.plain
            self.assertFalse(after.warnings);self.assertEqual(len(out),len(s.raw))
            self.assertTrue(all(u32(plain,at)==0 for at in b.amounts.values()))
            self.assertEqual(u32(plain,b.current),0)
            for key,at in b.flags.items():self.assertEqual(u32(plain,at),u32(s.rockstar.container.plain,at)&~4)
            self.assertEqual(u32(plain,b.flags['bounty:region:2']),0x82)
            self.assertEqual(next(f.value for f in after.slots[0].fields if f.key=='bounty:clear'),1)
            allowed={i for at in b.spans for i in range(at,at+4)}
            allowed.update(i for begin,at in s.rockstar.container.checks for i in range(at+12,at+16))
            self.assertTrue(all(x==y or i in allowed for i,(x,y) in enumerate(zip(s.rockstar.container.plain,plain))))

    def test_known_current_amount_syncs_when_unique_and_unrelated_regions_stay_separate(self):
        s=self.save();out=s.patched({(0,'bounty:region:2'):10.25,(0,'bounty:region:0'):5})
        after=Save(out,'rdr2');b=after.rockstar.rdr2.campaign.bounties;plain=after.rockstar.container.plain
        self.assertEqual(u32(plain,b.current),1025)
        self.assertEqual(u32(plain,b.amounts['bounty:region:0']),500)
        self.assertEqual(u32(plain,b.flags['bounty:region:2']),0x86)
        out=s.patched({(0,'bounty:region:2'):0});after=Save(out,'rdr2')
        self.assertEqual(u32(after.rockstar.container.plain,b.flags['bounty:region:2']),0x82)

    def test_ambiguous_current_region_requires_consistent_matching_final_amounts(self):
        s=self.save(bounty_zero=True)
        with self.assertRaisesRegex(ValueError,'ambiguous'):s.patched({(0,'bounty:region:0'):10})
        out=s.patched({(0,f'bounty:region:{n}'):10 for n in range(6)});after=Save(out,'rdr2')
        self.assertEqual(u32(after.rockstar.container.plain,after.rockstar.rdr2.campaign.bounties.current),1000)

    def test_mission_temporary_bounty_and_mismatched_current_are_protected(self):
        s=self.save(bounty_temporary=True)
        for key in ('bounty:clear','bounty:region:2'):
            with self.assertRaises(ValueError):s.patched({(0,key):1})
        s=self.save(bounty_mismatch=True)
        with self.assertRaises(ValueError):s.patched({(0,'bounty:region:2'):1})
        after=Save(s.patched({(0,'bounty:clear'):1}),'rdr2')
        self.assertEqual(u32(after.rockstar.container.plain,after.rockstar.rdr2.campaign.bounties.current),0)
        s=self.save(bounty_bad_count=True);self.assertFalse(any(f.group=='Bounties' for f in s.slots[0].fields))

    def test_clear_is_an_action_not_a_toggle_and_conflicting_edits_and_invalid_cents_fail(self):
        s=self.save()
        with self.assertRaisesRegex(ValueError,'combined'):s.patched({(0,'bounty:clear'):1,(0,'bounty:region:2'):1})
        for value in (-1,1500.01,1.001):
            with self.assertRaises(ValueError):s.patched({(0,'bounty:region:2'):value})
        after=Save(s.patched({(0,'bounty:clear'):1}),'rdr2')
        with self.assertRaises(ValueError):after.patched({(0,'bounty:clear'):0})

"""Synthetic PC archives exercise variable-size and coupled Alice edits."""
import struct
import unittest
from core import Save, FormatError, identify_game
from alice_catalog import ACTORS, HEALTH_ACTORS, COLLECTIBLES
from alice_profile import Archive, fstring
from test_core import alice

class AliceTests(unittest.TestCase):
    def open(self,raw=None):return Save(alice() if raw is None else raw,'alice')
    def fields(self,save):return {f.key:f.value for f in save.slots[0].fields}

    def test_noop_and_teeth_do_not_touch_combat_counter(self):
        save=self.open();self.assertEqual(save.patched({}),save.raw)
        self.assertEqual(save.alice.scalars['ruin_kills'][2],725)
        output=save.patched({(0,'teeth'):100000})
        check=self.open(output)
        self.assertEqual(self.fields(check)['teeth'],100000)
        self.assertEqual(check.alice.scalars['ruin_kills'][2],725)
        offset=save.alice.scalars['teeth'][0]
        self.assertEqual(output[:offset],save.raw[:offset])
        self.assertEqual(output[offset+4:],save.raw[offset+4:])

    def test_every_exposed_field_can_round_trip_at_its_boundaries(self):
        save=self.open()
        for field in save.slots[0].fields:
            for boundary in (field.minimum,field.maximum):
                with self.subTest(key=field.key,value=boundary):
                    save.patched({(0,field.key):boundary})

    def test_collectibles_resize_lists_and_sync_existing_and_missing_actors(self):
        save=self.open()
        changes={(0,'memory:1_M_2_Lizzie'):1,(0,'memory:1_M_18_Nanny'):1,
                 (0,'secret:CH1_MIN_04'):1,(0,'snout:CH1_SNT_14'):1}
        check=self.open(save.patched(changes));self.assertGreater(len(check.raw),len(save.raw))
        for (_,key),value in changes.items():self.assertEqual(self.fields(check)[key],value)
        self.assertEqual(check.alice.actors[('Chapter1_W1_VoT_01_S','MemoryFragment_Family_0')][1][2],1)
        for tag in ('1_M_18_Nanny','CH1_MIN_04'):
            for identity in ACTORS[tag]:
                self.assertEqual(check.alice.actor_lookup[tuple(v.casefold() for v in identity)][1][2],1)
        self.assertEqual(check.alice.actors[('Chapter1_W1_VoT_01_S','UnrelatedActor_0')][1],[17,23,42,12,64,-1])
        self.assertIn('UnknownSecret',check.alice.lists['secret'][2])
        self.assertEqual(check.alice.scalars['snout_total'][2],1)
        self.assertEqual(check.alice.scalars['snout_count:1'][2],1)
        removed=self.open(check.patched({key:0 for key in changes}))
        self.assertFalse(removed.alice.lists['memory'][2])
        self.assertFalse(removed.alice.lists['snout'][2])
        self.assertEqual(removed.alice.lists['secret'][2],['UnknownSecret'])
        self.assertEqual(removed.alice.actors[('Chapter1_W1_VoT_01_S','MemoryFragment_Family_0')][1][2],0)

    def test_weapon_levels_and_acquired_flags_stay_consistent(self):
        save=self.open()
        check=self.open(save.patched({(0,'weapon:HobbyHorse'):4,(0,'ability:Float'):1}))
        self.assertIn('HobbyHorse',check.alice.lists['ability'][2])
        self.assertIn('UnknownAbility',check.alice.lists['ability'][2])
        self.assertEqual(check.alice.scalars['cap:Float'][2],1)
        self.assertEqual(self.fields(check)['first_upgrade'],1)
        check=self.open(check.patched({(0,'ability:HobbyHorse'):0,(0,'ability:Float'):0}))
        self.assertEqual(self.fields(check)['weapon:HobbyHorse'],0)
        self.assertEqual(check.alice.scalars['cap:Float'][2],0)
        with self.assertRaises(ValueError):save.patched({(0,'weapon:VorpalBlade'):3,(0,'ability:VorpalBlade'):0})

    def test_paint_pots_are_real_pickups_with_a_synchronized_total(self):
        save=self.open();check=self.open(save.patched({(0,'paint'):16}))
        self.assertEqual(sum(f.value for f in check.slots[0].fields if f.key.startswith('pot:')),16)
        self.assertEqual(check.alice.scalars['paint'][2],16)
        for identity in HEALTH_ACTORS:
            self.assertEqual(check.alice.actors[identity][1],[0,1,1,-1,0,-1])
        check=self.open(check.patched({(0,'pot:0'):0}))
        self.assertEqual(check.alice.scalars['paint'][2],15)
        with self.assertRaises(ValueError):save.patched({(0,'paint'):0,(0,'pot:0'):1})

    def test_progress_uses_the_game_weights_and_leaves_checkpoint_map(self):
        save=self.open()
        changes={(0,'chapter:'+str(i)):1 for i in range(1,7)}
        changes.update({(0,'big_memory:'+str(i)):1 for i in range(1,6)})
        changes.update({(0,'cave:'+str(i)):1 for i in range(16)})
        changes.update({(0,kind+':'+tag):1 for kind in ('memory','snout','secret') for tag in COLLECTIBLES[kind]})
        check=self.open(save.patched(changes))
        self.assertEqual(check.alice.scalars['completion'][2],1)
        self.assertEqual(check.alice.current_map,save.alice.current_map)
        self.assertEqual(check.alice.scalars['gi_chapter:6'][2],1)
        self.assertEqual(check.alice.lists['gi_memories'][2],['','unrelated'])

    def test_rejects_truncation_bad_counts_flags_and_unknown_revision(self):
        raw=alice()
        for size in (1,7,12,len(raw)-1):
            with self.subTest(size=size),self.assertRaises(FormatError):self.open(raw[:size])
        for offset,value in ((0,50),(4,0),(8,-1),(8,100001)):
            data=bytearray(raw);struct.pack_into('<i',data,offset,value)
            with self.subTest(offset=offset,value=value),self.assertRaises(FormatError):self.open(bytes(data))
        for key,value in [('weapon:VorpalBlade',5),('chapter:1',2),('health',-1),('seconds',float('nan'))]:
            with self.subTest(key=key),self.assertRaises(ValueError):self.open().patched({(0,key):value})
        with self.assertRaises(ValueError):self.open().patched({(0,'unknown'):1})

    def test_archive_strings_support_utf16_and_reject_bad_terminators(self):
        for value in ('', 'Ascii', 'Alicia á', '記憶'):
            reader=Archive(fstring(value));self.assertEqual(reader.string(),value)
        with self.assertRaises(ValueError):Archive(struct.pack('<i',4)+b'abcd').string()
        with self.assertRaises(ValueError):Archive(struct.pack('<i',100000)).string()

    def test_utf16_unknown_list_entries_survive_resize(self):
        save=self.open()
        start,end,_=save.alice.lists['secret']
        original=struct.pack('<i',1)+fstring('記憶')
        raw=bytes(save.raw[:start])+original+bytes(save.raw[end:])
        parsed=self.open(raw)
        check=self.open(parsed.patched({(0,'secret:CH1_MIN_04'):1}))
        self.assertIn(original[4:],check.alice.list_entries['secret'])
        self.assertIn('記憶',check.alice.lists['secret'][2])

    def test_rejects_ambiguous_actor_names(self):
        raw=alice().replace(fstring('UnrelatedActor_0'),fstring('memoryfragment_family_0'))
        with self.assertRaises(FormatError):self.open(raw)


def configuration():
    settings=bytearray(struct.pack('<22i',1,1,*([0]*20)))
    for index,value in ((2,1),(4,.6),(5,.7),(6,.8),(10,2.2)):
        struct.pack_into('<f',settings,index*4,value)
    keys=b''.join(fstring('鍵' if index==1 else 'Key'+str(index)) for index in range(66))
    return (struct.pack('<2i',16,0xf223)+settings+keys+struct.pack('<ifi',1,1.5,0)
            +struct.pack('<351i',*range(351)))


class AliceConfigTests(unittest.TestCase):
    def test_configuration_preserves_bindings_settings_and_ui_records(self):
        raw=configuration();save=Save(raw,'alice')
        self.assertEqual(identify_game('GameConfig_PC.CFG'),'alice')
        self.assertEqual(save.slots[0].name,'Game configuration')
        self.assertEqual(save.patched({}),raw)
        output=save.patched({(0,'current_difficulty'):3})
        self.assertEqual(output[:8],raw[:8])
        self.assertEqual(output[12:],raw[12:])
        self.assertEqual(struct.unpack_from('<2i',output,8),(3,1))

    def test_lowering_difficulty_updates_historical_minimum(self):
        save=Save(configuration(),'alice')
        output=save.patched({(0,'current_difficulty'):0})
        self.assertEqual(struct.unpack_from('<2i',output,8),(0,0))
        self.assertEqual(output[16:],save.raw[16:])
        with self.assertRaises(ValueError):save.patched({(0,'lowest_difficulty'):2})

    def test_configuration_rejects_truncation_and_unknown_revisions(self):
        raw=configuration()
        for invalid in (raw[:-1],raw[:50],raw+b'\0',struct.pack('<i',17)+raw[4:]):
            with self.subTest(length=len(invalid)),self.assertRaises(FormatError):Save(invalid,'alice')
        for value in (-1,4):
            with self.assertRaises(ValueError):Save(raw,'alice').patched({(0,'current_difficulty'):value})

if __name__=='__main__':unittest.main()

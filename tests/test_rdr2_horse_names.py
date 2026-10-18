"""Text boundaries, synchronized horse names and protected ambiguous originals."""
import unittest
from core import Field,Save
from test_rdr2_features import fixture
from test_rdr2_pso import rsav


class HorseNameTests(unittest.TestCase):
    def save(self,encrypted=True,**kwargs):
        return Save(rsav(encrypted,fixture(False,horse_names=True,**kwargs)),'rdr2')

    def test_utf8_names_update_both_copies_with_exact_restoration(self):
        for encrypted in (False,True):
            before=self.save(encrypted);f=before.rockstar.rdr2
            field=next(x for x in before.slots[0].fields if x.text)
            positions=f.campaign.horse_names.positions[field.key]
            allowed={i for at in positions for i in range(at,at+64)}
            allowed.update(i for b,at in f.c.checks for i in range(at+12,at+16))
            for value in ('Epona','007','Éclair 🐴','', 'a'*63,'é'*31+'a'):
                with self.subTest(encrypted=encrypted,bytes=len(value.encode('utf-8'))):
                    after=Save(before.patched({(0,field.key):value}),'rdr2');g=after.rockstar.rdr2
                    self.assertEqual(next(x.value for x in after.slots[0].fields if x.key==field.key),value)
                    self.assertFalse(after.warnings);self.assertEqual(g.c.encrypted,encrypted)
                    self.assertEqual(len(after.raw),len(before.raw));self.assertEqual(after.raw[:0x110],before.raw[:0x110])
                    for at in positions:self.assertEqual(g.raw[at:at+64],value.encode().ljust(64,b'\0'))
                    self.assertTrue(all(a==b or i in allowed for i,(a,b) in enumerate(zip(f.raw,g.raw))))
                    self.assertEqual(after.patched({(0,field.key):field.value}),before.raw)

    def test_invalid_text_is_rejected_without_numeric_coercion_or_truncation(self):
        before=self.save();field=next(x for x in before.slots[0].fields if x.text)
        self.assertEqual(field.parse('007'),'007')
        for value in (3,None,b'Name','a'*64,'é'*32,'Name\0x','a\nb','a\tb','a\u202eb','a\ud800b'):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):field.parse(value)
                with self.assertRaises(ValueError):before.patched({(0,field.key):value})
        numeric=Field('n','Number',1,0,'',0,100)
        for value in ('1',True,None):
            with self.assertRaises(ValueError):numeric.validate(value)
        self.assertEqual(before.patched({}),before.raw)

    def test_disagreement_noncanonical_strings_wrong_schemas_and_unknown_slots_are_protected(self):
        before=self.save();f=before.rockstar.rdr2;field=next(x for x in before.slots[0].fields if x.text)
        inventory,script=f.campaign.horse_names.positions[field.key]
        plain=bytearray(f.raw);plain[script:script+64]=b'Other'.ljust(64,b'\0')
        after=Save(f.c.encode(plain),'rdr2');read=next(x for x in after.slots[0].fields if x.key==field.key)
        self.assertTrue(read.readonly)
        with self.assertRaises(ValueError):after.patched({(0,field.key):'New'})
        for at,data in ((inventory,b'x'*64),(inventory,b'\xff'+bytes(63)),(script,b'x\0nonzero'+bytes(55))):
            plain=bytearray(f.raw);plain[at:at+64]=data
            protected=Save(f.c.encode(plain),'rdr2');self.assertFalse(any(x.text for x in protected.slots[0].fields))
        for kwargs in ({'unknown_horse_slot':True},{'missing_horse_model':True},{'bad_pointer':True}):
            self.assertFalse(any(x.text for x in self.save(**kwargs).slots[0].fields))
        # A schema with a different fixed-string capacity cannot expose a writer.
        self.assertFalse(any(x.text for x in self.save(horse_name_capacity=32).slots[0].fields))
        # No declared Name member is sufficient to protect an otherwise valid horse.
        without=Save(rsav(True,fixture(False)),'rdr2');self.assertFalse(any(x.text for x in without.slots[0].fields))

    def test_rename_and_inventory_growth_share_a_checked_output(self):
        before=self.save(supplies=True,unlocks=True,components=True)
        fields=before.slots[0].fields;name=next(x for x in fields if x.text)
        supply=next(x for x in fields if x.group=='Add supplies' and not x.readonly)
        changes={(0,name.key):'Epona',(0,supply.key):12,(0,'cash'):123.45}
        after=Save(before.patched(changes),'rdr2');self.assertFalse(after.warnings)
        for (n,key),value in changes.items():self.assertEqual(next(x.value for x in after.slots[n].fields if x.key==key),value)


if __name__=='__main__':unittest.main()

"""Everyday navigation hides records without discarding or changing native fields."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication,QPushButton,QLineEdit,QComboBox,QLabel
from catalog import BY_ID
from editor_preview import EditorPreview
from editor_presentation import present_categories,is_advanced,bulk_actions,quick_actions
from core import Save
from app import Window


class PresentationTests(unittest.TestCase):
    def test_all_catalogue_fields_remain_accessible_once_with_original_identity(self):
        for game in BY_ID:
            for slot in EditorPreview(game).slots:
                with self.subTest(game=game,slot=slot.name):
                    before=[(id(f),f.key,f.label,f.group,f.value,f.readonly) for f in slot.fields]
                    basic=present_categories(game,slot.fields)
                    full=present_categories(game,slot.fields,True)
                    shown=[f for c in basic for s in c.sections for f in s.fields]
                    all_fields=[f for c in full for s in c.sections for f in s.fields]
                    self.assertCountEqual([id(f) for f in all_fields],[id(f) for f in slot.fields])
                    self.assertEqual(len({id(f) for f in all_fields}),len(slot.fields))
                    self.assertTrue(all(not is_advanced(game,f) for f in shown))
                    self.assertEqual(sum(len(s.fields) for c in full if c.name=='Advanced' for s in c.sections),
                                     sum(is_advanced(game,f) for f in slot.fields))
                    self.assertEqual(before,[(id(f),f.key,f.label,f.group,f.value,f.readonly) for f in slot.fields])

    def test_rdr2_everyday_tabs_and_records_have_distinct_meanings(self):
        fs=EditorPreview('rdr2').slots[0].fields
        basic=present_categories('rdr2',fs)
        self.assertEqual([c.name for c in basic],['Character','Inventory','Weapons','Horse'])
        self.assertFalse(any(f.group in ('Statistics','Compendium','Unlocks') for c in basic for s in c.sections for f in s.fields))
        inventory=next(c for c in basic if c.name=='Inventory')
        self.assertEqual({s.selection for s in inventory.sections},{'Owned items','Add items'})
        self.assertTrue(any(f.key=='cash' for c in basic if c.name=='Character' for s in c.sections for f in s.fields))
        advanced=present_categories('rdr2',fs,True)[-1]
        self.assertEqual(advanced.name,'Advanced')
        self.assertTrue(any(f.key.startswith('unlock:') for s in advanced.sections for f in s.fields))

    def test_gta_has_purchase_and_worn_clothes_without_raw_shop_or_seen_flags(self):
        fs=EditorPreview('gtav').slots[0].fields
        basic=[f for c in present_categories('gtav',fs) for s in c.sections for f in s.fields]
        self.assertTrue(any(f.key.startswith('clothes_worn:') for f in basic))
        self.assertTrue(any(f.key.startswith('weapon_inventory:') for f in basic))
        self.assertTrue(all(f.key.endswith(':1') for f in basic if f.key.startswith('clothes:')))
        self.assertFalse(any(f.key.startswith('weapon_shop:') for f in basic))
        elden=EditorPreview('eldenring').slots[0].fields
        self.assertTrue(is_advanced('eldenring',next(f for f in elden if f.key=='runes_memory')))

    def test_mixed_flags_do_not_get_enable_everything_buttons(self):
        from test_gtav_features import fixture
        from test_rdr2_features import fixture as rdr
        for game,raw in (('gtav',fixture(weapons=True)),('rdr2',rdr(records=True,unlocks=True))):
            for c in present_categories(game,Save(raw,game).slots[0].fields,True):
                for s in c.sections:self.assertFalse(bulk_actions(game,s.fields))

    def test_same_model_weapons_are_separate_and_do_not_share_a_repair_action(self):
        from dataclasses import replace
        from test_rdr2_features import fixture
        fs=Save(fixture(),'rdr2').slots[0].fields
        original=[f for f in fs if f.group=='Weapon condition']
        other=[replace(f,key=f.key.replace(':0000000000000002:',':0000000000000099:')) for f in original]
        sections=next(c for c in present_categories('rdr2',fs+other) if c.name=='Weapons').sections
        self.assertEqual(len(sections),2)
        self.assertTrue(all(len(quick_actions('rdr2',s.fields)[0][1])==5 for s in sections))
        self.assertFalse(quick_actions('rdr2',original+other))


class PresentationInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_advanced_toggle_preserves_invalid_and_hidden_edits_and_reveal_can_materialize_them(self):
        from test_rdr2_features import fixture
        raw=fixture(records=True,unlocks=True,supplies=True,components=True,horse_names=True)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'SRDR30001';path.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                try:
                    w.show();self.assertTrue(w.load('rdr2',path))
                    self.assertFalse(w.advanced_options.isChecked())
                    self.assertEqual([w.tabs.tabText(i) for i in range(w.tabs.count())],['Character','Inventory','Weapons','Horse'])
                    cash=w.inputs[0,'cash'];cash.setText('250');self.assertEqual(w.validated_changes(),{(0,'cash'):250})
                    f=next(f for f in w.save.slots[0].fields if f.group=='Statistics' and not f.readonly)
                    control=w.inputs[0,f.key];self.assertIsInstance(control,QLineEdit)
                    self.assertTrue(w.advanced_options.isChecked());control.setText(str(f.maximum+1))
                    self.assertFalse(w.review_button.isEnabled())
                    w.advanced_options.setChecked(False);self.app.processEvents()
                    self.assertFalse(w.review_button.isEnabled())
                    self.assertIn('hidden pending changes',w.editor_mode_note.text())
                    with self.assertRaises(ValueError):w.validated_changes()
                    restored=w.inputs[0,f.key];self.assertEqual(restored.text(),str(f.maximum+1))
                    restored.setText(str(f.value));w.advanced_options.setChecked(False)
                    self.assertEqual(w.validated_changes(),{(0,'cash'):250})
                    self.assertEqual(path.read_bytes(),raw)
                    w.open_preview('rdr2');self.assertFalse(w.advanced_options.isChecked())
                    w.advanced_options.setChecked(True);self.app.processEvents()
                    self.assertFalse(w.review_button.isEnabled());self.assertFalse(w.validated_changes())
                    weapon=next(f for f in w.save.slots[0].fields if f.group=='Weapon condition')
                    w.reveal_field((0,weapon.key));self.app.processEvents()
                    self.assertTrue(any(b.isVisible() and b.text()=='Repair weapon' and not b.isEnabled()
                                        for b in w.findChildren(QPushButton)))
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_search_explains_hidden_matches_and_details_are_opt_in(self):
        from test_rdr2_features import fixture
        raw=fixture(records=True,unlocks=True)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'SRDR30001';path.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(Path(d)/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                try:
                    w.show();self.assertTrue(w.load('rdr2',path));w.resize(1024,800)
                    w.editor_search.setText('Headshots');self.app.processEvents()
                    self.assertIn('matching advanced options',w.editor_mode_note.text())
                    self.assertFalse(w.advanced_options.isChecked());w.advanced_options.setChecked(True)
                    self.app.processEvents();self.assertEqual(w.tabs.tabText(w.tabs.currentIndex()),'Advanced')
                    w.editor_search.clear();w.advanced_options.setChecked(False)
                    w.reveal_field((0,'player:health_core'));self.app.processEvents()
                    details=next(b for b in w.findChildren(QPushButton,'fieldHelp') if b.isVisible())
                    self.assertTrue(details.toolTip());details.click();self.app.processEvents()
                    self.assertTrue(any(l.isVisible() and l.text()==details.toolTip()
                                        for l in details.parentWidget().findChildren(QLabel)))
                    self.assertTrue(w.review_button.isVisible());self.assertLessEqual(w.review_button.mapTo(w,w.review_button.rect().bottomRight()).y(),w.height())
                    self.assertFalse(w.validated_changes());self.assertEqual(path.read_bytes(),raw)
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_rdr2_repair_and_core_buttons_only_stage_the_named_weapon_or_actor(self):
        from test_rdr2_features import fixture
        raw=fixture()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'SRDR30001';path.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(Path(d)/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                try:
                    w.show();self.assertTrue(w.load('rdr2',path))
                    field=next(f for f in w.save.slots[0].fields if f.group=='Weapon condition')
                    w.reveal_field((0,field.key));self.app.processEvents()
                    next(b for b in w.findChildren(QPushButton) if b.text()=='Repair weapon' and b.isVisible()).click()
                    changes=w.validated_changes();self.assertEqual(len(changes),5)
                    self.assertTrue(all(k.startswith(field.key.rsplit(':',1)[0]+':') and v==0 for (slot,k),v in changes.items()))
                    after=Save(w.save.patched(changes),'rdr2')
                    self.assertTrue(all(f.value==0 for f in after.slots[0].fields if f.group=='Weapon condition'))
                    w.reset();w.reveal_field((0,'player:health_core'));self.app.processEvents()
                    next(b for b in w.findChildren(QPushButton) if b.text()=='Refill player cores' and b.isVisible()).click()
                    self.assertEqual(w.validated_changes(),{(0,'player:health_core'):100,(0,'player:stamina_core'):100,(0,'player:dead_eye_core'):100})
                    self.assertEqual(path.read_bytes(),raw)
                finally:w.close();w.deleteLater();self.app.processEvents()

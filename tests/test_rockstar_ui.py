import os,tempfile,unittest
os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from app import Window
from core import Save
from editor_navigation import SectionNavigation
from test_rockstar import fixture


class RockstarInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_vehicle_paint_and_model_specific_performance_choices_stage_and_reset(self):
        from test_gtav_features import fixture as expanded
        from PySide6.QtWidgets import QComboBox,QLineEdit
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SGTA50000';raw=expanded(True,weapons=True,styles=True);p.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    self.assertTrue(w.load('gtav',p))
                    expected={(0,'vehicle:0:0:primary'):160,(0,'vehicle:0:0:mod_11'):4,
                              (0,'vehicle:0:0:window_tint'):3}
                    for key,value in expected.items():
                        w.reveal_field(key);self.app.processEvents();control=w.inputs[key]
                        self.assertIsInstance(control,QComboBox);control.setCurrentIndex(value)
                    self.assertEqual(w.validated_changes(),expected)
                    self.assertFalse(Save(w.save.patched(expected),'gtav').warnings)
                    w.reveal_field((0,'vehicle:0:0:model_name'));self.app.processEvents()
                    self.assertIsInstance(w.inputs[0,'vehicle:0:0:model_name'],QLineEdit)
                    self.assertTrue(w.inputs[0,'vehicle:0:0:model_name'].isReadOnly())
                    self.assertEqual(p.read_bytes(),raw);w.reset();self.assertFalse(w.validated_changes())
                    w.open_preview('gtav');self.app.processEvents()
                    w.reveal_field((0,'vehicle:0:0:primary'));self.app.processEvents()
                    self.assertEqual(w.inputs[0,'vehicle:0:0:primary'].count(),161)
                    self.assertFalse(w.review_button.isEnabled())
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_gta_weapon_inventory_shop_and_color_choices_stage_across_sections(self):
        from test_gtav_features import fixture as expanded
        from PySide6.QtWidgets import QCheckBox,QComboBox,QLineEdit
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SGTA50000';raw=expanded(True,weapons=True);p.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    self.assertTrue(w.load('gtav',p))
                    changes={(0,'weapon_inventory:1:22d8fe39:present'):1,
                             (0,'weapon_inventory:1:22d8fe39:tint'):7,
                             (0,'weapon_ammo:1:22d8fe39'):75,
                             (0,'weapon_shop:2:13532244:purch_0:31'):1}
                    for key,value in changes.items():
                        w.reveal_field(key);self.app.processEvents();control=w.inputs[key]
                        if isinstance(control,QComboBox):control.setCurrentIndex(value)
                        elif isinstance(control,QCheckBox):control.setChecked(bool(value))
                        else:self.assertIsInstance(control,QLineEdit);control.setText(str(value))
                    self.assertEqual(w.validated_changes(),changes)
                    after=Save(w.save.patched(changes),'gtav');self.assertFalse(after.warnings)
                    self.assertEqual(p.read_bytes(),raw);w.reset();self.assertFalse(w.validated_changes())
                    w.reveal_field((0,'weapon_shop:1:1b06d571:purch_0:25'));self.app.processEvents()
                    from PySide6.QtWidgets import QPushButton
                    action=next(b for b in w.findChildren(QPushButton) if b.text()=='Unlock shop options' and b.isVisible())
                    action.click();self.app.processEvents()
                    self.assertTrue(w.validated_changes())
                    self.assertTrue(all(key.startswith('weapon_shop:') for slot,key in w.validated_changes()))
                    w.reset()
                    w.open_preview('gtav');self.app.processEvents()
                    for key in changes:
                        w.reveal_field(key);self.app.processEvents()
                        if isinstance(w.inputs[key],QComboBox):
                            w.inputs[key].setCurrentIndex(3)
                        else:self.assertFalse(w.inputs[key].isEnabled())
                    self.assertFalse(w.validated_changes())
                    self.assertFalse(w.review_button.isEnabled())
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_gta_player_clock_and_vehicle_fields_stage_and_preview(self):
        from test_gtav_features import fixture as expanded
        from PySide6.QtWidgets import QLineEdit, QCheckBox
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SGTA50000';raw=expanded(True);p.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    self.assertTrue(w.load('gtav',p))
                    changes={(0,'player:health'):150,(0,'world:hour'):18,(0,'vehicle:0:0:tires'):1,(0,'vehicle:0:0:plate'):'MY CAR'}
                    for key,value in changes.items():
                        w.reveal_field(key);self.app.processEvents();control=w.inputs[key]
                        if isinstance(control,QCheckBox):control.setChecked(bool(value))
                        else:self.assertIsInstance(control,QLineEdit);control.setText(str(value))
                    self.assertEqual(w.validated_changes(),changes)
                    self.assertFalse(Save(w.save.patched(changes),'gtav').warnings)
                    self.assertEqual(p.read_bytes(),raw)
                    w.reset();self.assertFalse(w.validated_changes())
                    w.open_preview('gtav');self.app.processEvents()
                    w.reveal_field((0,'vehicle:0:0:plate'));self.app.processEvents()
                    self.assertFalse(w.inputs[0,'vehicle:0:0:plate'].isEnabled())
                    self.assertFalse(w.review_button.isEnabled())
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_rdr2_catalog_and_acquisition_actions_stage_in_distinct_sections(self):
        from test_rdr2_features import fixture as expanded
        from test_rdr2_pso import rsav
        from PySide6.QtWidgets import QCheckBox,QLineEdit
        from editor_layout import organize_fields
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SRDR30001'
            raw=rsav(True,expanded(False,records=True,bounties=True,unlocks=True,supplies=True));p.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    self.assertTrue(w.load('rdr2',p));expected={}
                    for group in ('Unlocks','Add supplies','Bounties'):
                        f=next(f for f in w.save.slots[0].fields if f.group==group and not f.readonly and (group=='Add supplies' or f.boolean))
                        w.reveal_field((0,f.key));self.app.processEvents();control=w.inputs[0,f.key]
                        if group=='Add supplies':
                            self.assertIsInstance(control,QLineEdit);control.setText('12');expected[0,f.key]=12
                        else:
                            self.assertIsInstance(control,QCheckBox);control.setChecked(True);expected[0,f.key]=1
                    self.assertEqual(w.validated_changes(),expected)
                    after=Save(w.save.patched(expected),'rdr2');self.assertFalse(after.warnings)
                    sections=[s.name for c in organize_fields('rdr2',after.slots[0].fields) for s in c.sections]
                    self.assertIn('Unlocks: Weapons',sections);self.assertIn('Add supplies: Tonics',sections)
                    self.assertEqual(p.read_bytes(),raw);w.reset();self.assertFalse(w.validated_changes())
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_horse_name_text_validation_navigation_reset_and_preview_are_safe(self):
        from test_rdr2_features import fixture as expanded
        from PySide6.QtWidgets import QLineEdit
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SRDR30001';raw=expanded(horse_names=True);p.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    self.assertTrue(w.load('rdr2',p));field=next(x for x in w.save.slots[0].fields if x.text)
                    key=(0,field.key);w.reveal_field(key);self.app.processEvents();entry=w.inputs[key]
                    self.assertIsInstance(entry,QLineEdit);entry.setText('007')
                    self.assertEqual(w.validated_changes(),{key:'007'})
                    entry.setText('é'*32);self.assertTrue(entry.property('invalid'))
                    with self.assertRaises(ValueError):w.validated_changes()
                    entry.setText('Éclair');self.assertFalse(entry.property('invalid'))
                    self.assertEqual(w.validated_changes(),{key:'Éclair'})
                    w.restore_field(key);self.assertEqual(w.inputs[key].text(),field.value)
                    self.assertFalse(w.validated_changes());self.assertEqual(p.read_bytes(),raw)
                    w.open_preview('rdr2');self.app.processEvents()
                    preview=next(x for x in w.save.slots[0].fields if x.text);w.reveal_field((0,preview.key));self.app.processEvents()
                    self.assertFalse(w.inputs[0,preview.key].isEnabled());self.assertFalse(w.review_button.isEnabled())
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_rdr2_weapon_parts_use_named_choices_and_preserve_pending_edits(self):
        from test_rdr2_features import fixture as expanded
        from PySide6.QtWidgets import QComboBox
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SRDR30001';raw=expanded(components=True,unlocks=True);p.write_bytes(raw)
            with patch('app.discover',return_value=[]):w=Window(settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat))
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    self.assertTrue(w.load('rdr2',p));keys=('component:0000000000000002:0f43dcc6','component:0000000000000002:ebe563e3','component:0000000000000035:7fe38573')
                    for key in keys:
                        w.reveal_field((0,key));self.app.processEvents();control=w.inputs[0,key]
                        self.assertIsInstance(control,QComboBox);control.setCurrentIndex(1)
                    changes=w.validated_changes();self.assertEqual(changes,{(0,k):1 for k in keys})
                    after=Save(w.save.patched(changes),'rdr2');self.assertFalse(after.warnings)
                    self.assertEqual(p.read_bytes(),raw);w.reset();self.assertFalse(w.validated_changes())
                finally:w.close();w.deleteLater();self.app.processEvents()

    def test_collection_growth_scrolls_without_clipping_the_sidebar_footer(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=QSettings(str(Path(directory)/'prefs.ini'),QSettings.Format.IniFormat)
            with patch('app.discover',return_value=[]):w=Window(settings=settings)
            w.show()
            try:
                for width,height in ((1440,900),(1100,720)):
                    w.resize(width,height);self.app.processEvents()
                    self.assertGreaterEqual(w.saving_note.height(),w.saving_note.heightForWidth(w.saving_note.width()))
                    self.assertGreaterEqual(w.collection_scroll.height(),80)
                self.assertGreater(w.collection_scroll.verticalScrollBar().maximum(),0)
            finally:w.close();w.deleteLater();self.app.processEvents()

    def test_character_navigation_decimal_cash_and_offline_previews(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat)
            with patch('app.discover',return_value=[]):w=Window(settings=settings)
            discard=patch.object(w,'may_discard',return_value=True);discard.start()
            w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
            try:
                for game in ('gtav','rdr2'):
                    w.open_preview(game);self.app.processEvents();self.assertTrue(w.save.is_preview)
                    self.assertFalse(w.review_button.isEnabled())
                p=root/'SGTA50000';p.write_bytes(fixture());w.load('gtav',p)
                w.inputs[0,'character:2:stamina'].setText('100');self.app.processEvents()
                self.assertEqual(w.validated_changes(),{(0,'character:2:stamina'):100})
                nav=w.tabs.currentWidget().findChild(SectionNavigation)
                self.assertIsNotNone(nav);self.assertEqual(set(nav.character_buttons),{'Michael','Franklin','Trevor'})
                out=w.save.patched(w.validated_changes());self.assertFalse(Save(out,'gtav').warnings)
                self.assertEqual(p.read_bytes(),fixture());w.reset()
                p=root/'SRDR30001';p.write_bytes(fixture('rdr2'));w.load('rdr2',p)
                w.inputs[0,'cash'].setText('1234.56');self.app.processEvents()
                self.assertEqual(w.validated_changes(),{(0,'cash'):1234.56})
                out=w.save.patched(w.validated_changes());self.assertEqual(Save(out,'rdr2').slots[0].fields[0].value,1234.56)
                self.assertEqual(p.read_bytes(),fixture('rdr2'));w.reset()
            finally:w.close();w.deleteLater();self.app.processEvents();discard.stop()

    def test_expanded_rdr2_navigation_and_staged_edits(self):
        from test_rdr2_features import fixture as expanded
        from PySide6.QtWidgets import QCheckBox
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'SRDR30001';raw=expanded(records=True);p.write_bytes(raw)
            settings=QSettings(str(root/'prefs.ini'),QSettings.Format.IniFormat)
            with patch('app.discover',return_value=[]):w=Window(settings=settings)
            with patch.object(w,'may_discard',return_value=True):
                w.reduce_motion.setChecked(True);w.show();w.resize(1280,800)
                try:
                    w.load('rdr2',p);fields=w.save.slots[0].fields;expected={}
                    for group in ('Honor','Player cores','Player progression','Inventory','Weapon condition','Horses','Camp','Statistics','Compendium','World clock'):
                        f=next(f for f in fields if f.group==group);w.reveal_field((0,f.key));entry=w.inputs[0,f.key]
                        if isinstance(entry,QCheckBox):entry.setChecked(True);value=1
                        else:value=0.5 if group=='Weapon condition' else f.value+1;entry.setText(str(value))
                        expected[0,f.key]=value;self.app.processEvents()
                        self.assertTrue(entry.isVisible())
                    self.assertEqual(w.validated_changes(),expected);out=w.save.patched(expected)
                    self.assertFalse(Save(out,'rdr2').warnings);self.assertEqual(p.read_bytes(),raw)
                    self.assertLess(len(w.inputs),len(fields)+1)
                    w.reset()
                finally:w.close();w.deleteLater();self.app.processEvents()

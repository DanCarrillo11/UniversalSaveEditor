"""Game-specific editor navigation, independent of save-format parsing.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from dataclasses import dataclass, field
from kh_party import KH1_CHARACTERS, KH2_CHARACTERS


@dataclass
class Section:
    name: str
    fields: list = field(default_factory=list)
    selection: str = ''


@dataclass
class Category:
    name: str
    description: str
    selector_label: str
    sections: list = field(default_factory=list)


DESCRIPTIONS = {
    'Progress': 'Currency, progression, and save-wide settings.',
    'Characters': 'Choose a character to edit their attributes and progression.',
    'Character': 'Character attributes, weapons, and abilities.',
    'Equipment': 'Equipment, supplies, and upgrades.',
    'Collection': 'Browse your items and collected records by section.',
    'Unlocks': 'Choose a section to manage its unlocks.',
    'Records': 'Profile statistics, run records, and combat totals.',
}


def kh2_inventory_section(key):
    """Resolve the native stock position before choosing a category."""
    from kh2_items import STOCK_ITEMS
    from kh2_relationships import stock_section
    item=STOCK_ITEMS.get(int(key.split(':')[1]))
    return stock_section(item[2]) if item else 'Other entries'


def organize_fields(game, fields):
    """Assign every field exactly once, with at most three top-level categories."""
    order = {
        'kh1': ('Progress', 'Characters', 'Collection'),
        'kh2': ('Progress', 'Characters', 'Collection'),
        'recom': ('Progress', 'Collection'),
        'bbs': ('Progress', 'Character', 'Collection'),
        'ddd': ('Progress', 'Characters', 'Collection'),
        'kh3': ('Progress', 'Characters', 'Collection'),
        'maxpayne': ('Equipment',),
        'gtav': ('Characters', 'Progress', 'Equipment'),
        'rdr2': ('Progress','Character','Collection'),
        'eldenring': ('Progress', 'Character', 'Collection'),
        're4_2005': ('Progress', 'Characters', 'Collection'),
        're5': ('Progress', 'Unlocks', 'Collection'),
        're6': ('Progress', 'Unlocks', 'Collection'),
        're1_hd': ('Progress', 'Equipment', 'Collection'),
        're2': ('Progress', 'Characters', 'Collection'),
        're3': ('Progress', 'Characters', 'Collection'),
        're4_remake': ('Progress', 'Characters', 'Collection'),
        're7': ('Progress', 'Characters', 'Collection'),
        're8': ('Progress', 'Character', 'Collection'),
        're9': ('Progress', 'Characters', 'Collection'),
        'webfishing': ('Progress', 'Equipment', 'Collection'),
        'ror2': ('Progress', 'Unlocks', 'Records'),
        'alice': ('Progress', 'Character', 'Collection'),
    }.get(game, ('Progress', 'Collection'))
    categories = {name: Category(name, DESCRIPTIONS[name],
                  'Character' if name == 'Characters' else 'Section') for name in order}

    for item in fields:
        group = item.group or 'Economy'
        category, section, selection = 'Progress', group, group
        if game=='eldenring':
            if group in ('Attributes','Vitals','Appearance','Equipment capacity','Spells','Equipment loadout','Tool loadout'):
                category='Character'
                if group=='Equipment loadout':section,selection=item.collection or group,'Equipment loadout'
                if group=='Tool loadout':section,selection=item.collection or group,'Tools and Physick'
                if group=='Appearance':section,selection=item.collection or group,'Appearance'
            elif group=='Spell collection':category,section,selection='Collection',item.collection or group,'Learned spells'
            elif group=='Add items':category,section,selection='Collection',item.collection or group,'Add items'
            elif group=='Add equipment':category,section,selection='Collection',item.collection or group,'Add equipment'
            elif group in ('Inventory','Storage'):
                category,section,selection='Collection',item.collection or group,group
            elif group=='World map':category,section,selection='Collection',item.collection or group,'World map'
        if game=='re1_hd':
            if group=='Defensive supplies':category='Equipment'
            elif group in ('Inventory','Item box'):
                category,section,selection='Collection',item.collection or group,group
        if game in ('re2','re3','re4_remake','re7','re8','re9'):
            if group=='Player health':
                category='Character' if game=='re8' else 'Characters'
                if game=='re9':section,selection='Health',item.collection or 'Player'
                if game=='re4_remake':section,selection='Health',item.collection or 'Player'
            elif game in ('re2','re3','re4_remake') and group=='Equipment capacity':
                category,section,selection='Collection','Case capacity' if game=='re4_remake' else 'Inventory capacity',item.collection or 'Inventory'
            elif group=='Currency':category='Progress'
            elif game=='re9' and group=='Weapon upgrades':
                category,section,selection='Collection','Attached upgrades',item.collection or 'Weapons'
            elif game=='re9' and group in ('Equipment','Weapon shortcuts'):
                category,section,selection='Collection',group,item.collection or 'Inventory'
            elif group in ('Difficulty','Combat records','Lifetime records','Completion records'):category='Progress'
            else:
                category='Collection'
                if 'quantities' in group:
                    section,selection=item.collection or 'Unidentified items',group.replace(' quantities','')
                    if game=='re9':section,selection='Existing items',item.collection or 'Inventory'
        if game=='gtav':
            category = 'Progress' if item.collection == 'World' else 'Equipment' if item.collection == 'Vehicles' or item.key.startswith('vehicle:') else 'Characters'
            if item.key.startswith(('weapon_shop:', 'weapon_ammo:', 'weapon_inventory:')):
                category = 'Equipment'
            section,selection=group,item.collection
            if item.key.startswith(('weapon_shop:', 'weapon_ammo:', 'weapon_inventory:')):
                section=group.split(' · ',1)[-1]
            if item.key.startswith('vehicle:'):
                section,selection=item.collection,'Vehicles'
        if game=='rdr2':
            if group in ('Player cores','Player progression','Honor'):category,section,selection='Character',group,'Player'
            elif group in ('Weapon condition','Horses'):category,section,selection='Collection',item.collection or group,group
            elif group=='Compendium':category,section,selection='Collection','Compendium: '+(item.collection or 'Records'),group
            elif group=='Unlocks':category,section,selection='Collection','Unlocks: '+(item.collection or 'Catalog'),group
            elif group=='Add supplies':category,section,selection='Collection','Add supplies: '+(item.collection or 'Supplies'),group
            elif group=='Weapon customization':category,section,selection='Collection','Customize: '+(item.collection or 'Weapons'),group
            elif group=='Inventory':category,section,selection='Collection',item.collection or group,group
            else:category,section,selection='Progress',group,group
        if game=='re5':
            if group=='Library files':category='Collection'
            elif group!='Currency':category='Unlocks'
        if game=='re6':
            if group=='Serpent emblems' or group.endswith((' supplies',' skills')):category='Collection'
            elif group=='Mercenaries records':category,section,selection='Collection','Results',item.collection or 'Mercenaries'
            elif group not in ('Currency','Difficulty'):category='Unlocks'
        if game=='re4_2005':
            if group in ('Player health','Ashley health'):
                category,section,selection='Characters','Health','Ashley' if group=='Ashley health' else 'Player'
            elif group in ('Save statistics','Combat statistics'):
                category,section,selection='Progress',group,group
            elif group in ('Weapon upgrades','Ammunition','Consumables'):
                category,section,selection='Collection',group,group
        if game in ('kh1', 'kh2'):
            if game=='kh1' and group=='Dalmatians':category,section,selection='Collection','Rescued puppies','Dalmatians'
            elif game=='kh2' and group in ('Forms','Summons'):category,section,selection='Characters',group,'Sora'
            elif game=='kh2' and group=='Reports':category,section,selection='Collection',group,group
            elif group=='Shared abilities':category,section,selection='Characters',group,'Party'
            elif game=='kh1' and group=='Magic shortcuts':category,section,selection='Characters',group,'Sora'
            elif item.key.startswith('inventory:'):
                category = 'Collection'
                if game == 'kh2':
                    section = item.collection or kh2_inventory_section(item.key)
                else:
                    section = group
                selection = section
            elif item.key.startswith('form:'):
                category, selection = 'Characters', 'Sora'
                section = item.label.split(' · ')[0] + ' form'
            elif item.key.startswith('character:') or item.key.split(':')[0] in tuple(str(i) for i in range(10)):
                character = int(item.key.split(':')[1] if game == 'kh2' else item.key.split(':')[0])
                selection = (KH2_CHARACTERS if game=='kh2' else KH1_CHARACTERS)[character]
                category, section = 'Characters', group if group in ('Equipment','Abilities','Magic','Summons','Companion AI') else 'Attributes'
            elif item.key.startswith('drive_'):
                category, section, selection = 'Characters', 'Drive Gauge', 'Sora'
            else:
                section = {'Difficulty': 'Difficulty', 'Economy': 'Currency', 'Progress': 'Level and experience'}.get(group, group)
                selection = section
        elif game == 'webfishing':
            if group in ('Appearance','Lures','Hotbar'):category,section,selection='Equipment',item.collection or group,group
            elif group in ('Cosmetics','Add items','Journal qualities'):
                category,section,selection='Collection',item.collection or group,group
            elif group=='Quests':category,section,selection='Progress','Quests','Quests'
            elif item.key.startswith('bait:') or group in ('Bait', 'Upgrades'):
                category = 'Equipment'
                section = 'Bait' if item.key.startswith('bait:') or group == 'Bait' else 'Rod and buddy upgrades'
            elif group in ('Inventory', 'Journal'):
                category, section = 'Collection', 'Items' if group == 'Inventory' else 'Fishing journal'
            else:
                section = 'Currency' if group == 'Economy' else 'Level and fishing progress'
            if group not in ('Appearance','Lures','Hotbar','Cosmetics','Add items','Journal qualities','Quests'):selection = section
        elif game == 'ror2':
            if item.fmt == 'xml-unlock':
                category, section = 'Unlocks', group
            elif group in ('Progress', 'Combat') or item.key.startswith('stat:'):
                category, section = 'Records', {'Progress': 'Run records', 'Combat': 'Combat statistics', 'Economy': 'Economy statistics'}.get(group, group)
                if item.collection:section=item.collection
            else:
                section = 'Currency'
            selection = section
        elif game == 'alice':
            if group in ('Health', 'Weapons', 'Skills', 'Dresses', 'DLC'):
                category = 'Character'
                section = {'Skills': 'Abilities', 'Dresses': 'Dress abilities', 'DLC': 'DLC weapon flags'}.get(group, group)
            elif group in ('Memories', 'Bottles', 'Snouts', 'Radula rooms', 'Enemy journal', 'Cinematics'):
                category, section = 'Collection', group
            else:
                section = {'Economy': 'Currency', 'Story and chapters': 'Story completion'}.get(group, group)
            selection = section
        elif game == 'recom':
            if item.key.startswith('card:') or group in ('Card acquisition','Extra card acquisition','Friend acquisition'):
                category = 'Collection'
            selection = section
        elif game == 'bbs':
            if group in ('Attributes','Abilities','Equipment','Finishers'):
                category = 'Character'
            elif group in ('Commands','Decks'):
                category = 'Collection'
            selection = item.collection or section
        elif game in ('ddd','kh3'):
            if game=='kh3' and group in ('Magic','Links','Shortcuts'):
                category,section,selection='Characters',group,'Sora'
            elif game=='kh3' and group=='Minigame records':
                category,section,selection='Collection',group,group
            if game=='ddd' and group in ('Dream Eaters','Spirit progression','Spirit appearance'):
                category,section,selection='Characters',{'Dream Eaters':'Attributes','Spirit progression':'Progress','Spirit appearance':'Appearance'}[group],item.collection or 'Spirit'
            if item.key.startswith('character:') or item.key.startswith('bonus:'):
                category, section = 'Characters', 'Attributes'
                if game=='kh3' and item.group in ('Equipment','Abilities','Companion AI'):section=item.group
                if game=='ddd' and item.group=='Equipment':section=item.group
                selection = item.key.split(':')[1] if item.key.startswith('character:') else 'Sora'
            elif item.key.startswith(('inventory:', 'material:')):
                category = 'Collection'
                section=item.collection or section;selection=section
        elif game == 'maxpayne':
            category, selection = 'Equipment', section

        target = categories[category]
        existing = next((entry for entry in target.sections if (entry.name, entry.selection) == (section, selection)), None)
        if existing is None:
            existing = Section(section, selection=selection)
            target.sections.append(existing)
        existing.fields.append(item)

    # Stable, useful first sections, regardless of the serialization order.
    priorities = ('Currency', 'Difficulty', 'Level and experience', 'Level and fishing progress',
                  'Story completion', 'Chapter select', 'Statistics', 'Attributes', 'Drive Gauge',
                  'Health', 'Weapons', 'Abilities', 'Dress abilities', 'DLC weapon flags',
                  'Items', 'Inventory', 'Materials', 'Accessories', 'Bait', 'Rod and buddy upgrades',
                  'Characters', 'Skills', 'Skins and recolors', 'Artifacts', 'Items and equipment',
                  'Memories', 'Bottles', 'Snouts', 'Radula rooms', 'Enemy journal', 'Cinematics')
    for category in categories.values():
        section_order = ('Items', 'Inventory', 'Consumables', 'Ammunition', 'Healing', 'Supplies', 'Crafting materials', 'Upgrade materials', 'Materials', 'Weapons', 'Accessories', 'Equipment', 'Special items', 'Other entries',
                         'Fishing journal', 'Memories', 'Bottles', 'Snouts', 'Radula rooms',
                         'Enemy journal', 'Cinematics', 'Unidentified items', 'Unidentified materials') if category.name == 'Collection' else priorities
        category.sections.sort(key=lambda section: (
            (('Sora', 'Donald', 'Goofy', 'Riku').index(section.selection) if section.selection in ('Sora', 'Donald', 'Goofy', 'Riku') else 4) if category.name == 'Characters' else 0,
            section_order.index(section.name) if section.name in section_order else len(section_order)))
    if game == 'gtav':
        equipment=categories.get('Equipment')
        if equipment and equipment.sections:
            equipment.selector_label='Character'
            names=('Michael','Franklin','Trevor','Vehicles')
            equipment.sections.sort(key=lambda s:(names.index(s.selection) if s.selection in names else 4,s.name.casefold()))
    return [category for category in categories.values() if category.sections]

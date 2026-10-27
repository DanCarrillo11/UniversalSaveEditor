"""Task-focused editor views; the native fields and writers remain unchanged.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from editor_layout import Category, Section, organize_fields
from collections import defaultdict


RECORD_GROUPS = frozenset(('Statistics','Save statistics','Combat statistics','Combat records',
    'Lifetime records','Completion records','Challenge records','Challenge reward records',
    'Chapter records','Minigame records','Mercenaries records','Compendium'))


def is_advanced(game, field):
    group=field.group
    if group in RECORD_GROUPS:
        return True
    if 'unidentified' in (field.label+' '+field.collection).casefold():
        return True
    if game=='rdr2':
        return (group in ('Unlocks','World clock') or field.key=='bounty:current'
                or group=='Add supplies' and field.value>0)
    if game=='gtav':
        return (field.key.startswith('weapon_shop:') or
                field.key.startswith('clothes:') and not field.key.endswith(':1') or
                field.key.startswith('player:') and field.key.rsplit(':',1)[-1] not in
                ('health','armour','max_health','max_armour') or
                group in ('Clock','Garage services'))
    if game=='ror2':
        return group in ('Progress','Combat','Logs','Newt Altars') or field.key.startswith('stat:')
    if game=='eldenring':
        return group=='Journey' or field.key=='runes_memory'
    if game in ('kh1','kh2','kh3','bbs','ddd','recom'):
        return group in ('Companion AI','Game settings')
    if game=='webfishing':
        return field.key=='fish_caught' or group=='Journal qualities'
    if game=='alice':
        return group in ('DLC','Story and chapters','Chapter select')
    return False


def section_help(game, section):
    groups={f.group for f in section.fields}
    if game=='rdr2':
        if 'Unlocks' in groups:
            return 'Catalogue availability only. This does not put an item in your inventory or grant its reward.'
        if 'Compendium' in groups:
            return 'Recorded history only. Marking a record does not acquire an animal, item or completion reward.'
        if 'Add supplies' in groups:
            return 'Enter how many to add. Zero leaves the item unchanged. Experimental acquisition has not been verified in the game.'
        if 'Inventory' in groups:
            return 'Change quantities of items already present in this save.'
        if 'Weapon condition' in groups:
            return 'Condition and compatible parts of this saved weapon. Selecting a part does not create another weapon.'
        if 'Horses' in groups:
            return 'Edit this saved horse. Renaming or changing its attributes does not create a horse or a stable slot.'
    if game=='gtav':
        if any(f.key.startswith('weapon_shop:') for f in section.fields):
            return 'Shop records only. Use the weapon inventory to put a weapon in your character’s loadout.'
        if any(f.key.startswith('clothes:') for f in section.fields):
            return 'Purchase individual garments here. Use Current clothes to change what the character wears.'
    if groups & RECORD_GROUPS:
        return 'Saved records and counters. Changing these does not automatically complete objectives or grant rewards.'
    return ''


def _add(categories, name, section, selection, field):
    category=next((c for c in categories if c.name==name),None)
    if category is None:
        category=Category(name,'','Section');categories.append(category)
    entry=next((s for s in category.sections if (s.name,s.selection)==(section,selection)),None)
    if entry is None:
        entry=Section(section,selection=selection);category.sections.append(entry)
    entry.fields.append(field)


def present_categories(game, fields, show_advanced=False):
    """Partition every actual field without copying/replacing its identity."""
    basic=[f for f in fields if not is_advanced(game,f)]
    advanced=[f for f in fields if is_advanced(game,f)]
    if game=='rdr2':
        categories=[Category(n,'','Section') for n in ('Character','Inventory','Weapons','Horse')]
        weapons=defaultdict(list)
        for f in basic:
            if f.group=='Weapon condition':
                identity=f.key.split(':')[1]
                if identity not in weapons[f.collection]:weapons[f.collection].append(identity)
        for f in basic:
            group=f.group
            if group in ('Weapon condition','Weapon customization'):
                # Keep condition and the weapon's own compatible parts together.
                title=f.collection or 'Saved weapons'
                identity=f.key.split(':')[1]
                if len(weapons[f.collection])>1 and identity in weapons[f.collection]:
                    title+=f' · Weapon {weapons[f.collection].index(identity)+1}'
                _add(categories,'Weapons',title,title,f)
            elif group=='Horses':
                _add(categories,'Horse',f.collection or 'Saved horse',f.collection or 'Saved horse',f)
            elif group in ('Inventory','Add supplies'):
                _add(categories,'Inventory',f.collection or 'Supplies',
                     'Add items' if group=='Add supplies' else 'Owned items',f)
            else:
                title={'Currency':'Money','Camp':'Camp funds','Player cores':'Health, stamina and Dead Eye',
                       'Player progression':'Experience and weight','Honor':'Honor','Bounties':'Bounties'}.get(group,group)
                _add(categories,'Character',title,title,f)
        inventory=next(c for c in categories if c.name=='Inventory')
        inventory.selector_label='Browse'
    else:
        categories=organize_fields(game,basic)
        if game=='gtav':
            equipment=next((c for c in categories if c.name=='Equipment'),None)
            if equipment:
                # Put the worn outfit and wardrobe before the long weapon list.
                equipment.sections.sort(key=lambda s:(('Michael','Franklin','Trevor','Vehicles').index(s.selection)
                    if s.selection in ('Michael','Franklin','Trevor','Vehicles') else 4,
                    0 if s.name=='Current clothes' else 1 if s.name.startswith('Wardrobe · ') else 2,
                    s.name.casefold()))
    categories=[c for c in categories if c.sections]
    if show_advanced and advanced:
        extra=Category('Advanced','Technical records and less common settings.','Section')
        for category in organize_fields(game,advanced):
            for section in category.sections:
                for f in section.fields:
                    _add([extra],'Advanced',section.name,section.selection,f)
        categories.append(extra)
    return categories


def bulk_actions(game, fields, preview=False):
    """Offer batch writes only for a named, coherent acquisition operation."""
    eligible=[f for f in fields if (preview or not f.readonly) and (f.boolean or f.fmt=='xml-unlock')]
    if not eligible:return []
    if game=='ror2' and all(f.fmt=='xml-unlock' for f in eligible):
        return [('Unlock section',1),('Restore section',None)]
    if all(f.key.startswith('clothes:') and f.key.endswith(':1') for f in eligible):
        return [('Acquire wardrobe section',1),('Restore section',None)]
    # Flags for unrelated gameplay effects, compendium records, equipped
    # weapon parts, and raw availability are never enabled together here.
    return []


def field_label(game, field):
    if game=='rdr2':
        return {'permanentdegradation':'Permanent wear','degradation':'Wear','soot':'Soot',
                'rust':'Rust','dirt':'Dirt','dirty':'Dirt','hungry':'Hunger',
                'bondingxp':'Bonding experience','weight':'Weight'}.get(field.key.rsplit(':',1)[-1],field.label)
    return field.label


def quick_actions(game, fields, preview=False):
    if game!='rdr2':return []
    groups={f.group for f in fields}
    actions=[]
    condition={f.key:0 for f in fields if (preview or not f.readonly) and f.group=='Weapon condition'
               and f.key.rsplit(':',1)[-1] in ('degradation','permanentdegradation','soot','rust','dirt')
               and f.minimum==0 and f.maximum==1}
    if condition and len({key.rsplit(':',1)[0] for key in condition})==1:
        actions.append(('Repair weapon',condition))
    cores={f.key:100 for f in fields if (preview or not f.readonly) and f.group in ('Player cores','Horses')
           and f.key.rsplit(':',1)[-1] in ('health_core','stamina_core','dead_eye_core')
           and f.minimum==0 and f.maximum==100}
    if cores:actions.append(('Refill horse cores' if 'Horses' in groups else 'Refill player cores',cores))
    return actions


def boolean_states(game, field):
    if field.key.startswith('add_talisman:'):return ('Not acquired','Acquire')
    if field.fmt=='xml-unlock':return ('Locked','Unlocked')
    if game=='maxpayne':return ('Not owned','Owned')
    if field.key.startswith('clothes:'):
        return {':0':('Unavailable','Available'),':1':('Not purchased','Purchased'),
                ':2':('Unseen','Seen')}.get(field.key[-2:],('Disabled','Enabled'))
    if field.key.startswith('weapon_shop:'):
        return ('Not purchased','Purchased') if 'purch_' in field.key else ('Unavailable','Available')
    if field.key.startswith('weapon_inventory:') and field.key.endswith(':present'):
        return ('Not carried','Carried')
    return ('Disabled','Enabled')

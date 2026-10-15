"""Allowlisted support reports; never serialize exceptions or save contents.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from dataclasses import dataclass
import json
import re
import sys
from catalog import BY_ID
from compatibility import evidence_label
from version import VERSION


@dataclass(frozen=True)
class Problem:
    code: str
    title: str
    message: str
    steps: tuple
    revision: int | None = None
    character: int | None = None

# Fixed guidance only: never show an arbitrary exception, path, identifier or
# save value. These are known editing conflicts, not unsupported-file errors.
EDIT_CONFLICTS=(
    ('kh2 magic shortcuts require', 'The selected KH2 shortcut needs a learned spell family.',
     ('Learn the spell in Sora’s Magic section or choose another shortcut.','The shortcut will use the selected learned tier.')),
    ('kh2 item shortcuts require', 'The selected KH2 shortcut needs an item equipped by Sora.',
     ('Equip the item in Sora’s item slots, with an available bag copy.','Then review the item and shortcut changes together.')),
    ('kh2 current drive cannot', 'Current Drive exceeds maximum Drive.',
     ('Lower current Drive or increase maximum Drive.','Reducing only the maximum automatically clamps the current gauge.')),
    ('kh2 new form acquisition resets', 'Acquiring a new Drive Form resets Anti points.',
     ('Reset the conflicting Anti-point edit or set it to zero.','Then review the form acquisition again.')),
    ('kh2 acquired forms require', 'An acquired Drive Form needs a positive saved level.',
     ('Choose a form level from 1 to 7 or reset the conflicting level edit.','Story availability is preserved.')),
    ('kh2 acquired summons require', 'Acquired summons need a positive saved summon level.',
     ('Choose a summon level from 1 to 7 or reset the conflicting level edit.','Story availability is preserved.')),
    ('kh2 ap budget:', 'Equipped abilities exceed the recognized KH2 AP budget.',
     ('Increase that character’s AP boosts, choose equipment with more AP, or unequip abilities.','Review all related changes together.')),
    ('kh2 bag transfer', 'The KH2 equipment transfer needs an available bag copy and enough space to return the old item.',
     ('Adjust the matching bag quantity or swap both equipment slots together.','Bag quantities are applied before equipment transfers.')),
    ('kh2 sora and dual-wield forms', 'Sora and his dual-wield forms cannot newly share the same Keyblade.',
     ('Choose a different Keyblade or swap both weapon slots together.','Review the resulting bag quantities.')),
    ('cannot transfer unsupported kh2 equipment', 'This KH2 equipment identity cannot be transferred safely.',
     ('Keep the existing item or choose a recognized item for the matching slot.','Unmapped and world-specific identities are preserved.')),
    ('a spell cannot appear twice in the memorized loadout', 'The same spell occupies more than one memory entry.',
     ('Remove the duplicate or select a different owned spell.','Spell entries compact automatically when you apply changes.')),
    ('the memorized spells exceed the available memory-slot capacity', 'The selected spells cost more memory slots than this character has available.',
     ('Choose fewer spells or spells with a lower memory cost.','Memory Stones and equipped Moon of Nokstella determine the saved capacity.')),
    ('the active spell position must point to the final memorized loadout', 'The active spell position does not match the final list.',
     ('Select an occupied position in the final compact list.','Choose None only when every memory entry is empty.')),
    ('critical-mode abilities cannot be removed while entering critical', 'An ability removal conflicts with entering Critical mode.',
     ('Keep the Critical abilities learned or reset their changes.','Then review the difficulty change again.')),
    ('critical-mode health conversion exceeds the supported range', 'Converting Critical-mode HP or MP would exceed the supported range.',
     ('Set explicit supported HP/MP values for the affected character.','Explicit vital edits take precedence over the automatic conversion.')),
    ('a kh1 magic shortcut must reference a spell available to sora', 'The selected magic family is unavailable to Sora.',
     ('Choose an available family or Empty.','Availability flags and spell tiers are separate; shortcuts do not award story upgrades.')),
    ('munny exceeds the available saved ledger range', 'The Munny balance would overflow the saved earned/spent ledger.',
     ('Choose a smaller balance.','Spending history is preserved rather than silently reset.')),
    ('a single-object item cannot have a quantity above 1', 'The selected item represents one object and cannot be duplicated as a stack.',
     ('Use quantity 1, or select a stackable item.','Existing ammunition and weapon quantities have separate limits.')),
    ('a shortcut must reference an acquired spell or link', 'The shortcut points to an unacquired command or spell tier.',
     ('Acquire the matching spell tier or Link in the same review, or choose a learned command.','Then review the shortcut again.')),
    ('a card with a positive quantity cannot have its acquisition disabled', 'The card quantity conflicts with its acquisition flag.',
     ('Keep acquisition enabled or reset that acquisition change.','Adding a mapped card quantity enables acquisition automatically.')),
    ('the hotbar cannot reference an item being removed', 'A hotbar slot refers to an item selected for removal.',
     ('Choose a surviving item or Empty for that hotbar slot.','Then review the removal again.')),
    ('restore other edits to an item before removing it', 'The same item has edits and a removal selected.',
     ('Reset that item’s quantity, size, quality or identity edits.','Keep its removal selected and review again.')),
    ('a removed item cannot remain locked', 'An item selected for removal is also selected as locked.',
     ('Disable its item-lock change or reset the removal.','Then review again.')),
    ('an equipped selection cannot be removed from its ownership list', 'An equipped cosmetic or lure is also selected for removal from your collection.',
     ('Keep it unlocked, or choose different equipment.','Then review again.')),
    ('add a positive quantity before selecting this bait', 'The selected bait has no saved quantity.',
     ('Add at least one unit of the selected bait.','Its acquisition is synchronized automatically.')),
    ('the active weapon slot must contain an enabled weapon', 'The selected active weapon slot is empty or disabled.',
     ('Equip a weapon in that slot, or select an occupied active slot.','Then review again.')),
    ('an equipped item must have a positive inventory quantity', 'An equipped item also has a zero-stock edit.',
     ('Give that inventory item at least one copy or reset its zero-stock edit.','Then review the equipment again.')),
    ('choose an item before setting a new item-box quantity', 'An empty item-box entry has a quantity but no selected item.',
     ('Choose the item in that entry’s Item selector.','Set its quantity and review again.')),
    ('an empty item cannot have a positive quantity', 'An entry selected as Empty still has a positive quantity edit.',
     ('Reset its quantity edit or set it to zero.','Then review the empty entry again.')),
    ('active ability stacks cannot exceed acquired stacks', 'An ability has more active stacks than acquired stacks.',
     ('Increase its acquired stacks or reduce its active stacks.','Then review again.')),
    ('the weapon level conflicts with its acquired ability', 'The weapon level and its acquisition flag disagree.',
     ('Use a positive weapon level with acquisition enabled, or level zero with acquisition disabled.','Reset one of the conflicting edits if needed.')),
    ('paint-pot count conflicts with the selected individual pickups', 'The paint-pot total conflicts with individual pickup changes.',
     ('Reset the total and edit individual pickups, or reset individual changes and choose the total.','Then review again.')),
    ('current hp cannot exceed maximum hp', 'Current health exceeds the selected maximum health.',
     ('Lower current health or increase maximum health for the same character.','Then review again.')),
)


def explain_error(error, operation='open'):
    text=str(error).casefold()
    if operation in ('review','apply') and isinstance(error,ValueError):
        for prefix,message,steps in EDIT_CONFLICTS:
            if text.startswith(prefix):return Problem('invalid_edit','Resolve conflicting edits',message,steps)
    revision=re.search(r'(?:save )?revision\s+(\d{1,10})(?!\d)',text)
    if revision and ('unsupported' in text or 'not supported' in text):
        value=int(revision[1]);character=re.search(r'(?:character|slot)\s+(\d{1,3})(?!\d)',text)
        slot=int(character[1]) if character else None
        return Problem('unsupported_revision','Save revision not supported',
            f'Character {slot} uses save revision {value}, which this editor does not support.' if slot else f'This save uses revision {value}, which this editor does not support.',
            ('Use the latest version of UniversalSaveEditor.','Check that the file belongs to the selected game and PC edition.','If it still fails, copy the diagnostic below when reporting the problem.'),value,slot)
    if isinstance(error,FileNotFoundError):
        return Problem('file_missing','Save file not found','The file was moved, renamed or removed.',
            ('Locate the save again with Open save or Locate in Recent saves.','Removing a recent entry only removes its shortcut.'))
    if isinstance(error,PermissionError):
        return Problem('file_access','Cannot access the save','The file is locked or this application cannot access its folder.',
            ('Close the game and any application using this file.','Check the file and folder permissions, then try again.'))
    if 'save changed' in text or 'original save changed' in text:
        return Problem('file_changed','The save changed after opening','Another application updated this file after you opened it.',
            ('Reopen the save to read its latest values.','Review your changes again before applying. The newer file was not overwritten.'))
    if any(word in text for word in ('steamid','account id','accountid','wrong account','authentication','decrypt','encrypted','digest')):
        return Problem('account_or_encryption','The encrypted save could not be opened','The original account information or encrypted save format could not be verified.',
            ('For copied saves, use the original owner’s SteamID64 when requested.','Check the selected game and PC edition. Renaming does not convert a save.','The diagnostic excludes account identifiers.'))
    if any(word in text for word in ('checksum','crc','integrity','fingerprint')):
        return Problem('integrity_check','Save integrity could not be verified','The integrity values or structure do not match the supported format. This alone does not prove that the game cannot load the file.',
            ('Check that you selected the correct game and edition.','If the save opens with an integrity warning, review the explicit repair option.','Unsupported player data cannot be fixed by ignoring its checks.'))
    if any(word in text for word in ('no active','no populated','no supported editable','populated slot','save point','typewriter')):
        return Problem('no_editable_records','No editable records found','This file has no supported player records or editable values for the selected editor.',
            ('Choose a populated gameplay save or the appropriate system profile.','Compatibility details explain which files and features are supported.'))
    if any(word in text for word in ('range','between','cannot exceed','below','overflow','unauthorized','calculated automatically','read-only','invalid character level','above the saved')):
        return Problem('invalid_edit','Review the selected values','One or more edits exceed a supported limit or conflict with related values.',
            ('Check the highlighted fields and their allowed ranges.','Reset the affected value if needed, then review again.'))
    if isinstance(error,OSError):
        return Problem('file_io','File operation could not be completed','The application could not read or write the selected file.',
            ('Check that the file is available and close applications using it.','When saving, check folder permissions and available disk space.'))
    return Problem('unsupported_format','Save format could not be read','The file may use a different edition, unsupported structure or incomplete data.',
        ('Check the selected game and save format in Compatibility details.','Try the latest application version. Renaming does not convert a file.','Copy the diagnostic to help investigate the unsupported variant.'))


def support_report(game=None, save=None, problem=None, operation='inspect', suffix=None, size=None, appearance=None,selected_record=None):
    """Positive whitelist: no raw errors, keys, values, paths, hashes or identities."""
    result={'application':'UniversalSaveEditor','version':VERSION,'portable':bool(getattr(sys,'frozen',False)),
            'operation':operation if operation in ('inspect','open','identify','scan','review','apply','restore') else 'inspect',
            'privacy':'No save contents, filenames, paths, account IDs or character names are included.'}
    if isinstance(game,str) and game in BY_ID:
        result['game']=game;result['platforms']=list(BY_ID[game].platforms);result['file_validation']=evidence_label(game)
    if appearance in ('light','dark'):result['appearance']=appearance
    allowed={'.sav','.sl2','.png','.mps','.bin','.xml','.psd','.cfg','.bak'}
    if isinstance(suffix,str) and suffix.casefold() in allowed:result['file_extension']=suffix.casefold()
    if type(size) is int and 0<=size<=64*1024*1024:result['file_bytes']=size
    if save is not None and save.game==game:
        result['active_records']=len(save.slots)
        result['editable_fields']=sum(not f.readonly for slot in save.slots for f in slot.fields)
        result['integrity_warnings']=len(save.warnings)
        if type(selected_record) is int and 0<=selected_record<len(save.slots):result['selected_record']=selected_record+1
    codes={'unsupported_revision','file_missing','file_access','file_changed','account_or_encryption','integrity_check','no_editable_records','invalid_edit','file_io','unsupported_format'}
    if problem is not None and problem.code in codes:
        result['problem']=problem.code
        if type(problem.revision) is int and 0<=problem.revision<=0xffffffff:result['save_revision']=problem.revision
        if type(problem.character) is int and 1<=problem.character<=100:result['character_number']=problem.character
    return json.dumps(result,indent=2,ensure_ascii=True)

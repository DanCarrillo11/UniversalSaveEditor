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


def explain_error(error, operation='open'):
    text=str(error).casefold()
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
    if any(word in text for word in ('range','between','cannot exceed','below','overflow','unauthorized','calculated automatically','invalid character level','above the saved')):
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

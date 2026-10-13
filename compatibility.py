"""Evidence for the shipped scope, not a guarantee of every game variant.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from dataclasses import dataclass
from catalog import BY_ID


@dataclass(frozen=True)
class Evidence:
    format: str
    files: str
    limits: str
    native_checked: bool = True
    gameplay: str = 'Edited saves have not been confirmed by loading them in the game.'

EVIDENCE = {
 'webfishing': Evidence('Steam player .sav files', 'A local player save was inspected; currency changes were reported working in-game.',
   'Existing inventory and journal entries only. Adding bait synchronizes its unlock state.', gameplay='Money changes confirmed in-game. Other editing features still need gameplay checks.'),
 'ror2': Evidence('Steam UserProfiles .xml files', 'A local Steam profile was inspected and automated edits are checked.',
   'Profile progression and unlock identifiers only. DLC requires ownership; no live-run inventory editing.'),
 'kh1': Evidence('Final Mix Steam KHFM_WW.png archives', 'Local and public PC archives were inspected, including multi-slot saves.',
   'Currency, difficulty, saved companion attributes, equipment slots and known ability entries. Unknown IDs and unexposed records are preserved. Equipment changes do not exchange bag quantities; ability AP and character-specific rules are not recalculated.'),
 'kh2': Evidence('Final Mix Steam KHIIFM_WW.png archives', 'Local and public populated PC archives were inspected.',
   'Populated save-point records only. Saved party attributes, equipment and ability lists; five main Drive Forms expose equipment/abilities. Slot counts, item auto-reload, story and world variants are preserved; no AP-cost or character-specific ability validation.'),
 'recom': Evidence('Steam KHReCoM_WW.png archives', 'Two public Steam fixtures and their mirrored currency/checksums were inspected.',
   'Card quantities do not rebuild decks or unlock story progress. Existing deck references are preserved.'),
 'bbs': Evidence('Final Mix Steam KHBbS_WW.png archives', 'Public PC archives were inspected and record lengths/checksums checked.',
   'Known commands and abilities only. HP counters, deck references and unknown identities are preserved.'),
 'ddd': Evidence('Steam Dream Drop Distance HD PNG archives', 'Public PC records were inspected and mirrored fields checked.',
   'Player records only. Sora/Riku progression and known inventory; system/theater records and unknown data are preserved.'),
 'kh3': Evidence('Steam encrypted KHIII_slot*.bin files', 'An encrypted public PC fixture was decrypted, edited and re-encrypted.',
   'Copied files need the original owner’s SteamID64. Difficulty does not recalculate starting bonuses; only exposed fields are editable.'),
 'maxpayne': Evidence('Original PC revision-48 .mps files', 'Three locally generated PC saves were parsed during format research.',
   'Weapon ownership, reserve ammunition and painkillers only. Health, Bullet Time, loaded rounds and checkpoint state are preserved.'),
 'alice': Evidence('Steam PersistentData_PC.PSD and GameConfig_PC.CFG', 'A local persistent profile and configuration were inspected.',
   'Persistent upgrades, flags and collectibles; configuration edits difficulty. Checkpoint position and active outfit are preserved.'),
 'eldenring': Evidence('Original Steam ER0000.sl2 files', 'Four public PC files were checked. Revisions 260/261 and new classes have synthetic tests; native revision-261 checking is pending.',
   'Revisions 65–261 with the known layout. Supported stackable goods can be added to held inventory; known existing weapons can be upgraded when their saved references agree. NG+ edits scaling only, not a story restart. No new weapons, quests, transfers, console or Nightreign support. Use edited saves offline.'),
 're4_2005': Evidence('Steam Ultimate HD Edition savegame00.sav', 'Four local revision-0x402 records were inspected.',
   'Pesetas, difficulty, health and statistics; existing supported case quantities and weapon tune-up tiers. Capacity can only increase; loaded ammunition and geometry are preserved. No new case objects, costumes or comprehensive unlocks.'),
 're1_hd': Evidence('HD Remaster PC encrypted save format', 'A public PC-format profile was checked for integrity and byte preservation.',
   'First mapped slot only. Other slots are preserved; existing inventory/item-box quantities do not change item identities.'),
 're5': Evidence('Steamworks savedata.bin profiles', 'A public Steamworks Gold profile was checked for integrity and in-memory edits.',
   'Profile currency and exposed flags only. Infinite-ammo flags do not grant weapons. Weapon upgrades, inventory and story remain unchanged.'),
 're6': Evidence('PC RE6 profile format', 'A public Steam profile was checked for integrity and in-memory edits.',
   'Skill points, Mercenaries flags, existing supplies and equipped campaign/Mercenaries skill slots. Skill purchase/unlock state, mode-specific skills, weapon identities, campaign progress and emblem encodings are preserved.'),
 're2': Evidence('RE2 (2019) Steam save envelopes', 'Documented layouts and synthetic Steam fixtures; native Steam file checking is pending.',
   'Player health, existing inventory quantities and exposed reward/library flags. Unknown identities and story state are preserved.', False),
 're3': Evidence('RE3 (2020) Steam save envelopes', 'Shared console payloads and synthetic Steam fixtures were checked; native Steam file checking is pending.',
   'Health, existing inventory quantities and exposed shop/reward flags. Console samples do not prove native Steam compatibility.', False),
 're4_remake': Evidence('RE4 (2023) Steam encrypted envelopes', 'Documented layouts and synthetic authenticated fixtures; native Steam file checking is pending.',
   'Extra-content points, Spinels and existing inventory quantities only. Copied files need the original SteamID64.', False),
 're7': Evidence('RE7 Steam save envelopes', 'Shared console payloads and synthetic Steam fixtures were checked; native Steam file checking is pending.',
   'Player health and existing item-box quantities only. Console samples do not prove native Steam compatibility.', False),
 're8': Evidence('Village Steam data*.bin save envelopes', 'A public shared console gameplay payload and synthetic Steam envelopes were checked; native Steam file checking is pending.',
   'Lei, CP, current health, existing stacks and separate extra-content flags. Single-item records, loaded ammunition, upgrades, story, challenge completion and DLC dependencies are preserved. Item/content names and game stack caps remain unmapped.', False),
 're9': Evidence('Steam Requiem gameplay saves and profiles', 'Nine native Steam files were authenticated and checked for identical output and in-memory edits.',
   'Player-specific saved health records, table-backed health upgrades, existing stacks and mapped attached part tiers. Player names/active variants, unknown item names, stack caps, item creation and original icons remain pending. Capacity upgrades can only increase; loaded ammunition, story and backup inventories are preserved. Gameplay/system files expose different options; content flags are separate.'),
}

# Scope describes exposed features; it is independent of file/gameplay evidence.
BROAD = frozenset(('webfishing','ror2','kh1','kh2'))
LIMITED = frozenset(('maxpayne','re1_hd','re2','re3','re4_remake','re7','re8'))

def coverage_label(game):
    if game in BROAD:return 'Broad coverage'
    if game in LIMITED:return 'Limited coverage'
    return 'Partial coverage'

def coverage_text(game):
    return coverage_label(game)+' · '+EVIDENCE[game].limits


def evidence_label(game):
    return 'PC files checked' if EVIDENCE[game].native_checked else 'PC file check pending'


def compatibility_text(game):
    item=BY_ID[game];evidence=EVIDENCE[game]
    return (f'{item.title}\n{item.subtitle}\n\n'
            f'Editor coverage · {coverage_label(game)}\n{item.description}\n'
            'No editor is currently classified as full support. Feature scope and in-game validation are separate.\n\n'
            f'Save format\n{evidence.format}\n\n'
            f'File checks · {evidence_label(game)}\n{evidence.files}\n\n'
            f'In-game checks\n{evidence.gameplay}\n\n'
            f'Scope and limits\n{evidence.limits}\n\n'
            'File checks and automated tests do not guarantee in-game loading or every game version. '
            'Changes apply directly to the opened file. No automatic backups are created.')

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
 'gtav': Evidence('Recognized PC SGTA5 story saves; Legacy / Enhanced', 'Two public Legacy files passed container checks and identical decode/encode. Enhanced checks are documented separately in docs/ROCKSTAR_PC.md.',
   'Existing cash/eight skills for each protagonist; recognized saved-player health/armor and maxima, stamina/reload/fire/drive-by/gang flags; clock and respray flags. Existing occupied garage records expose saved protections, license plates, named paint, window tint, smoke/neon RGB colors and guarded engine/brake/transmission/suspension/armor stages through checked typed records and matching vehicle kits. Recognized three/five-cell script inventories add/remove 35 base-slot weapons per protagonist, synchronize shared ammo, select mapped components/colors and update matching shop acquisition flags. Separate Ammu-Nation flags cover 40 weapons and accessories/colors. Typed wardrobe banks expose availability, purchase and seen flags for named static clothing, outfits, props and barber styles. Recognized current garments synchronize the character snapshot and active-player maps, acquiring the selected item. Hair/beard equipping, prop equipping, composite outfit assembly, dynamic DLC apparel, DLC weapon slot creation, vehicle creation/model swaps, properties, missions and online edits remain unsupported. Scripts may reset saved flags; gameplay and Enhanced-native validation remain pending.'),
 'rdr2': Evidence('Recognized encrypted PC SRDR Story Mode files', 'Three local PC story saves passed all ten payload checks and identical decode/encode; originals are preserved during validation.',
   'Cash; synchronized camp funds/honor; recognized player attributes; supplies, weapon condition, horses, compendium/history and clock. Guarded monetary bounties synchronize the native amount. Catalog unlocks do not grant ownership. Experimental acquisition supports custom amounts of 159 ordinary satchel supplies, including tonics, herbs, cooked food and Story Mode ammunition variants. Existing horse names synchronize inventory/script copies when both original names agree; ambiguous names stay protected. Weapon customization selects existing owned parts and replaces compatible existing leaf finishes/barrels/sights/rifling, synchronizing existing catalog flags for new variants. Weapon identity, part slots and GUIDs stay intact. Weapon/clothing acquisition, new component slots, stable management, camp upgrades, full story/challenge/reward dependencies and online state remain unsupported. Three native files passed structural checks; successful game loading is unverified.'),
 'webfishing': Evidence('Steam player .sav files', 'A local player save was inspected; currency changes were reported working in-game.',
   'Known item creation/replacement/removal, hotbar and item locks, original cosmetics/appearance/lures, existing quest progress and journal qualities. Selecting equipment grants mapped cosmetic/lure ownership; adding bait synchronizes acquisition. Missing quest records, rewards and unknown dependencies are preserved.', gameplay='Money changes confirmed in-game. Other editing features still need gameplay checks.'),
 'ror2': Evidence('Steam UserProfiles .xml files', 'A local Steam profile was inspected and automated edits are checked.',
   'Profile unlock identifiers and existing numeric statistics, including saved character/enemy/stage/item records. Unknown units/dependencies are explicit. DLC requires ownership; no live-run inventory editing.'),
 'kh1': Evidence('Final Mix Steam KHFM_WW.png archives', 'Local and public PC archives were inspected, including multi-slot saves.',
   'Currency, difficulty, saved companion attributes, equipment slots and known ability entries. Identified save-menu level/difficulty mirrors are synchronized. Unknown IDs and unexposed records are preserved. Equipment changes do not exchange bag quantities; per-character magic availability does not upgrade spell tiers. Four known shared movement-ability entries and three Sora magic-family shortcuts are editable. Shortcuts require availability and clear when its flag is disabled; spell tiers are separate. Ability AP and character-specific rules are not recalculated.'),
 'kh2': Evidence('Final Mix Steam KHIIFM_WW.png archives', 'Local and public populated PC archives were inspected.',
   'Populated save-point records only. Correct bag positions and separate item IDs; equipment changes transfer copies with stock/bounds and recognized standard AP checks. Six spell tiers and four shortcuts synchronize. Recognized form/summon/report acquisitions can be added, with level/Anti-point dependencies; current Drive follows maximum reductions. Only Valor/Master/Final expose offhand weapons. Auto-reload, companion AI and saved game options remain available. Slot counts, story and world variants are preserved. Complete character-specific behavior, growth/rewards, puzzles/journal and gameplay validation remain pending.'),
 'recom': Evidence('Steam KHReCoM_WW.png archives', 'Two public Steam fixtures and their mirrored currency/checksums were inspected.',
   'Card quantities and mapped acquisition flags; known completion flags can be added without clearing existing completion. Positive mapped card quantities enable acquisition. Decks, card costs, HP/CP and story events are not rebuilt. Native flag edits were reparsed; their in-game effect still needs verification.'),
 'bbs': Evidence('Final Mix Steam KHBbS_WW.png archives', 'Public PC archives were inspected and record lengths/checksums checked.',
   'Known commands/abilities, equipped Keyblades, finisher XP and references to existing commands. Observed multi-slot and unknown deck entries are protected. HP counters, complete deck-capacity rules and progression dependencies remain unmapped.'),
 'ddd': Evidence('Steam Dream Drop Distance HD PNG archives', 'Public PC records were inspected and mirrored fields checked.',
   'Sora/Riku progression, equipped Keyblades, known inventory and existing recognized spirit Attack/Magic/Defense. Populated known spirits also expose stored level, XP, maximum HP, Link Points, link count, RGB tint and recognized normal/shiny appearance. Level, XP and stats are independent; growth/rewards are not recalculated. Spirit creation, boards, affinity, rank, disposition, party/deck references, story and theater records are preserved.'),
 'kh3': Evidence('Steam encrypted KHIII_slot*.bin files', 'An encrypted public PC fixture was decrypted, edited and re-encrypted.',
   'Copied files need the original owner’s SteamID64. Party equipment, active weapon and known ability learned/equipped states are editable. Donald/Goofy AI, recognized innate Critical transitions and consistent Munny ledgers synchronize; unknown/equipment-derived state stays protected. Exact mapped equipment acquisition synchronizes; reserved flags are retained. Known magic tiers, Links, shortcut references and minigame records are editable. Acquisition order and unique identities are checked; matching shortcuts synchronize. AP costs, character-specific behavior, derived stats, rewards and story dependencies are not recalculated.'),
 'maxpayne': Evidence('Original PC revision-48 .mps files', 'Three locally generated PC saves were parsed during format research.',
   'Weapon ownership, reserve ammunition and painkillers only. Health, Bullet Time, loaded rounds and checkpoint state are preserved.'),
 'alice': Evidence('Steam PersistentData_PC.PSD and GameConfig_PC.CFG', 'A local persistent profile and configuration were inspected.',
   'Persistent upgrades, flags and collectibles; configuration edits difficulty. Checkpoint position and active outfit are preserved.'),
 'eldenring': Evidence('Original Steam ER0000.sl2 files', 'Four public PC files were checked. Revisions 260/261 and new classes have synthetic tests; native revision-261 checking is pending.',
   'Revisions 65–261 with the known layout. Supported stackable goods can be added to held inventory; known existing weapons can be upgraded when their saved references agree. Create 377 mapped base-game armaments and 559 armor pieces with separate native handles, acquisition counters and bounded variable-record growth. Creation requires a recognized physical layout, clean inventory capacity and verified zero padding; the anchored tail is preserved. Meteorite Staff cannot be reinforced. New equipment is unequipped at +0 without a custom Ash. NG+ edits scaling only, not a story restart. Named FACE appearance sliders and the saved death counter are editable; 263 mapped map visibility flags and increasing talisman capacity are editable. Models, unknown face blocks, body type and presets are preserved; map flags do not grant map-fragment items or travel eligibility. Owned memorized spells use 213 mapped costs, native compaction and validated active selection. Learn 171 mapped base-game spells using one-copy goods, item registration and acquisition counters; duplicates, malformed ownership and unowned DLC spells are protected. Casting requirements, quests and reward flags are unchanged. Six hand and four armor assignments select uniquely owned supported held copies; inventory indices, bare IDs, physical handles, dynamic identities and checked fingerprints synchronize. Exact armor categories and atomic swaps are enforced. Unknown global menu snapshots are preserved. Talisman/ammo/quick-item assignments, affinities/Ash attachment, DLC equipment creation, full quests, transfers, console and Nightreign support remain unavailable. Use edited saves offline.'),
 're4_2005': Evidence('Steam Ultimate HD Edition savegame00.sav', 'Four local revision-0x402 records were inspected.',
   'Pesetas, difficulty, health and statistics; existing supported case quantities and weapon tune-up tiers. Capacity can only increase; loaded ammunition and geometry are preserved. No new case objects, costumes or comprehensive unlocks.'),
 're1_hd': Evidence('HD Remaster PC encrypted save format', 'A public PC-format profile was checked for integrity and byte preservation.',
   'Recognized gameplay sections from the native directory. 131 documented inventory/item-box identities and the next clean empty box entry are editable. Composite/examinable item state and unknown ID 0x59 are preserved. Other sections, capacities, player identity and story remain unchanged; no new campaign slot is synthesized.'),
 're5': Evidence('Steamworks savedata.bin profiles', 'A public Steamworks Gold profile was checked for integrity and in-memory edits.',
   'Profile currency, costume/ammo/filter/library and 45 figure flags only. Infinite-ammo flags do not grant weapons. Weapon upgrades, inventory and story remain unchanged.'),
 're6': Evidence('PC RE6 profile format', 'A public Steam profile was checked for integrity and in-memory edits.',
   'Skill points, Mercenaries flags/results, uncollected emblems, named existing ammunition/herb reserves and equipped campaign/extra-mode slots. Last-selected difficulty and uncompleted Mercenaries records can be changed; existing nonzero completion bytes are protected. Depleted mapped reserves can be refilled; weapon and unknown count words remain read-only. Existing nonzero emblem encodings are preserved. Mode-specific skill compatibility, purchase/unlock state, weapon identities and campaign progress are not recalculated.'),
 're2': Evidence('RE2 (2019) Steam save envelopes', 'Documented layouts and synthetic Steam fixtures; native Steam file checking is pending.',
   'Saved difficulty, player health, existing quantities, increasing saved main-survivor inventory capacity, reward/library flags, completion/challenge records, acquisition statistics, a stored 4th Survivor timer and Ghost Survivors counters. Capacity preserves item/equipment layout and does not grant hip-pouch events. Unknown identities, adaptive rank, story and reward delivery are not synthesized.', False),
 're3': Evidence('RE3 (2020) Steam save envelopes', 'Shared console payloads and synthetic Steam fixtures were checked; native Steam file checking is pending.',
   'Health, existing quantities, increasing saved main-survivor inventory capacity, shop/reward flags and existing completion/challenge/combat and acquisition records. Capacity preserves item/equipment layout and does not grant hip-pouch events. Difficulty IDs, complete inventory and reward dependencies remain unmapped. Console samples do not prove native Steam compatibility.', False),
 're4_remake': Evidence('RE4 (2023) Steam encrypted envelopes', 'Documented layouts and synthetic authenticated fixtures; native Steam file checking is pending.',
   'Pesetas, points, Spinels, player/partner current and maximum health and increasing saved S–XXL case capacity in exact gameplay contexts. Maximum-health reductions clamp current health; explicit conflicting health edits are rejected. Existing quantities use exact saved virtual-stack caps where present. Profile-scoped costume/accessory/extra-shop/challenge flags and existing chapter/campaign records are editable. Full weapon upgrades, item creation, several reward names and gameplay dependencies remain unmapped. Case edits preserve geometry and do not change merchant purchases. Copied files need the original SteamID64.', False),
 're7': Evidence('RE7 Steam save envelopes', 'Shared console payloads and synthetic Steam fixtures were checked; native Steam file checking is pending.',
   'Saved difficulty, player health, existing item-box quantities, restarts, item-use statistics and existing DLC mode/completion flags. Inventory beyond the box, upgrade rules and complete unlock dependencies remain unmapped. Console samples do not prove native Steam compatibility.', False),
 're8': Evidence('Village Steam data*.bin save envelopes', 'A public shared console gameplay payload and synthetic Steam envelopes were checked; native Steam file checking is pending.',
   'Lei, CP, saved player health, existing stacks, separate content flags and existing lifetime/completion/combat, Mercenaries and DLC records. Single-item records, loaded ammunition, upgrades, story, challenge completion and DLC dependencies are preserved. Item/content names and game stack caps remain unmapped.', False),
 're9': Evidence('Steam Requiem gameplay saves and profiles', 'Nine native Steam files were authenticated and checked for identical output and in-memory edits.',
   'Player-specific saved health records, health-table upgrades, existing stacks, mapped attached parts and existing completion/combat/crafting/challenge and reward-claim records. Claim-state edits do not grant points. Player names/active variants, unknown item names, stack caps, item creation and original icons remain pending. Capacity upgrades can only increase; loaded ammunition, story and backup inventories are preserved. Populated carried equipment/weapon-shortcut references may select known owned weapons; paired indices/names synchronize. Empty/storage/backup/unresolved references are preserved. Gameplay/system files expose different options; content flags are separate.'),
}

# Scope describes exposed features; it is independent of file/gameplay evidence.
BROAD = frozenset(('webfishing','ror2','kh1','kh2'))
LIMITED = frozenset(('maxpayne','re2','re3','re4_remake','re7','re8','gtav','rdr2'))

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

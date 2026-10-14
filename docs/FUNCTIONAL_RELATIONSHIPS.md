# Equipment and spell relationships — v0.29.0-alpha

The catalogue remains 21 Steam editors. New games and artwork are paused.
This pass expands known operations; it does not complete every game or certify
successful game loading. See CURRENT_GAME_COMPLETION.md for all remaining gates.

## Requiem: owned equipment and weapon shortcuts

Only exact `_InventoryData` -> `Inventory.SaveData` carried (`Hand`) records
with a supported saved user, unique slot name and resolved owned `_PanelItems`
reference are eligible. Primary/weapon shortcuts offer known firearms; Secondary
offers known melee weapons. Armor, attachments, supplies and other categories
are not substituted for weapons. References require a single owned object.

Selecting an item updates `_ItemIndex` and the matching `_ItemIDName` together.
All offered item codes have the original UTF-16 length, so strings, arrays and
the encrypted payload do not resize. Item objects, geometry, ammo, attachment
tiers and account encryption remain unchanged. Empty or unresolved references,
duplicate slots, storage, backups and scene objects remain protected. This does
not create items, add slots, change a character or prove every weapon's runtime
character compatibility.

Seven populated native Steam gameplay files passed reference edits and
authenticated reparsing in memory. The original files were not overwritten.

## Elden Ring: memorized owned spells

The dynamic spell section follows held inventory and contains fourteen 8-byte
records plus an active index. Occupied pairs are `(MagicParam ID, ffffffff)`;
empty pairs are `(ffffffff, 0)`. A clean empty loadout uses active `ffffffff`.
The current list must be compact, unique, owned and known, and its spell
fingerprint must agree before controls appear.

Choices come from unique positive owned spell records in held common/key items.
213 exact spell identities, names and memory costs (1–3 slots) are mapped.
Capacity is two base slots plus up to eight saved Memory Stones, plus the
equipped Moon of Nokstella bonus in an unlocked talisman slot. Ambiguous or
unsupported source state is preserved rather than assigned guessed capacity.

Edits compact the final list, reject duplicates/excess cost, synchronize native
followers and hash entry 10, and retain the active index when valid. A now
out-of-range active position resets to zero; an empty list uses the sentinel.
Explicit active-position edits must match the final list. Export verification
checks the whole compact list instead of the old row numbers.

The loadout editor alone does not create spells or synthesize acquisition/quest
flags, and no attribute/FP requirements are waived. The separate base-game spell
acquisition controls are described below. Four public native files (28 active
characters) were inspected; 21 qualifying character records passed spell edits
and reparsing with every other character block unchanged. These files are not
independent gameplay certifications.

## Elden Ring: learn base-game spells

171 mapped base-game spell goods can be learned by creating exactly one held
common-inventory record. The same bounded writer used for goods registers the
`40000000 | ID` item, updates the held count and generates fresh acquisition
indices from both held common/key inventories. Existing registry entries keep
their flags. A clean empty common record, consistent counts and supported
registry header are required. No arrays or SL2 blocks resize.

Already-owned common or legacy key-item spells appear read-only. Removal,
duplicate ownership, malformed quantities and zero-quantity remnants are
protected. Unowned DLC spell IDs are not offered until their version/content
gate is established; already-owned DLC spells remain inspectable. Quests,
vendor stock, achievement flags and attribute/FP requirements are unchanged.
After applying, newly learned spells appear in the memory selectors. No spell
is automatically equipped or allowed to bypass memory capacity.

Four public native files with 28 active characters were inspected. 19 eligible
character records passed new spell acquisition, reparsing and preservation of
every other character block. Original reference files were not overwritten.
This is format evidence, not gameplay certification.

## RE4 Remake: Pesetas, health and case capacity

Pesetas must be the unique S32 `PTAS` of the top-level native
`InventoryManager.GameSaveData` section (`52dfdaa8`). Its input range is
0–9,999,999. Arbitrary matching bytes, merchant templates and nested sections
are not selected.

Health requires a recognized PlayerBase/ChCommonPl or PartnerBase/ChCommonPn
backup subclass directly in `CharacterManager.GameSaveData._CharacterSaves`
(`e381234f`). Generic CharacterBackup enemy entries are excluded. Current and
maximum HP must each be unique S32 values and initially consistent. Maximum
health edits clamp current HP when necessary; explicit current HP above the
final maximum is rejected. Injury/elimination, yellow-herb history, position,
story and unknown properties remain unchanged. Record labels do not assume
that every mode uses Leon/Ashley.

Increasing the native S–XXL case enum requires the exact
`InventorySaveDatas -> InventorySaveData.InventorySize` context, a unique
supported size and `IsTakeOverData == false`. The invalid/MAX sentinels are
excluded. Reductions are blocked to retain occupied geometry; no new inventory,
item, merchant purchase or acquisition event is synthesized.

These additions have synthetic encrypted fixtures and byte-preservation checks.
Native Steam file inspection and in-game loading are still pending.

## RE2/RE3: increasing current inventory capacity

Use the exact `InventoryManager.SaveData.DataLists -> inventory.Data` context,
as a standalone gameplay section or in the documented native
`SaveDataManager.GameSaveData.GameSaveDataList`. Require unique typed survivor
and size properties. Only the two primary survivors with supported even
capacities from 8 to 20 are eligible. The selector offers those even counts;
reductions are blocked, and bonus/unknown survivors or malformed layouts stay
protected.

Only `_CurrentSlotSize` changes. Item arrays/indices, equipment, shortcuts,
hip-pouch pickup events, rewards, progression and achievements are unchanged.
No inventory or item is created. Both editions have synthetic Steam encryption
and preservation tests. One eligible capacity record in a public RE3 shared
console payload passed a direct reparse/preservation check; that file is not
evidence of native Steam compatibility or game loading.

## DDD: existing populated Dream Eater details

The HD archive's known spirit array starts at record-relative `53a0`, with
102 entries of 256 bytes. New controls require a recognized species, a stored
level from 1 to 99, nonnegative S32 XP and positive S16 maximum HP. They expose
stored level (`+03`), XP (`+24` hex), Link Points (`+2c`), maximum HP (`+30`),
link count (`+4a`), RGB tint (`+20..+22`) and recognized normal/shiny appearance
(`+5c`, native values 1/2). Numeric bounds follow primitive encoding/editor
limits; they are not claimed to be game reward thresholds.

Level, XP and stats are independently stored and edited; no growth curve or
ability rewards are inferred. Names, species, rank/disposition, affinity bytes,
pet gauge, boards, party/deck references and unknown data are preserved. Unknown
appearance encodings and unpopulated/unsupported layouts are not overwritten.
Tint edits do not consume paint items or create spirits.

The positions match osdanova/KH_Editor's separate 256-byte model and the already
mapped Attack/Magic/Defense positions. 13 native PC reference spirits passed
88 new field edits and reparsing with their other data unchanged. Gameplay
validation, affinity/board rules, growth and spirit creation remain pending.

## KH1: magic-family shortcuts

The three byte references at record-relative `0844`–`0846` select Fire, Blizzard,
Thunder, Cure, Gravity, Stop, Aero or `ff` Empty. They refer to a magic family,
not an independently editable tier. Explicit choices require Sora's matching
availability bit. Disabling availability clears matching known shortcuts.
Unknown commands, spell tiers, reserved bits and other slots remain unchanged.

34 of 39 native reference records had available Sora magic suitable for a
shortcut check. All were patched/reparsed in memory, with explicit CRC repair
of the reference copy where required; the original archive remained unchanged.

## KH2: saved game options

Seven documented option bits expose vibration, navigation map, manual field
camera, command-menu stick/classic mode and horizontal/vertical camera reversal.
Each edit changes only its bit at record-relative `41a4`/`41a5`; unidentified
bits and settings stored outside this slot are preserved. They do not modify
story, items, spell acquisition or party state. 59 populated native PC records
passed option changes, explicit integrity repair on the reference copy and
reparsing; originals were not overwritten. In-game effect remains unverified.

## KH3: Critical transitions, ledger and companion behavior

Crossing the Critical boundary scales positive saved party HP/MP by one half
or two. Explicit HP/MP edits take precedence; dead/absent values remain zero.
The three recognized Sora Critical ability entries (`068`, `069`, `06a`) use
the observed absent `444` and innate learned `449`/`44b` words. Known absent
entries are granted on entry; those recognized innate entries are removed on
exit. Equipment-derived and unknown representations are preserved. Explicit
removal while entering Critical is rejected.

Starting items, bonus HP/MP, story, runtime multipliers and general AP budgets
are not rebuilt. This is not a complete recreation of a new-game setup.

Where `earned(0840) - spent(0844) == balance(0028)`, balance edits update earned
Munny and preserve spending history. Inconsistent ledgers are retained; overflow
is rejected. Read-only ledger values show the related change in final review.
Donald/Goofy combat style, ability use and recovery-item use are editable for
known saved enum values; their recovery target and unrelated state are preserved.
An encrypted native reference passed mode, balance and AI edits/reparsing.

## RE4 Remake: native virtual-stack capacities

When this exact `ArmouryItemSaveData` has one correctly typed, consistent
`VirtualStackableCountMax`, that cap bounds its `CurrVirtualStackCount`.
Valid native caps replace the arbitrary 999 editor bound. Single objects and
ambiguous, inconsistent or unsupported caps are read-only. Records without a
mapped cap retain their previous experimental scope; they are not described as
having a verified game cap. Item identities, capacity values, weapon state and
geometry remain unchanged. Native Steam/game-load checks remain pending.

## Validation boundaries

Synthetic tests cover ambiguity, protected contexts, paired references, whole
loadout verification, memory costs, duplicates, explicit overrides, hash updates,
encrypted output, source preservation and UI staging. They do not establish
unknown meanings, reward delivery or runtime behavior in untested games.

All-game completion still needs the unknown structures and related-state rules
listed in CURRENT_GAME_COMPLETION.md, plus in-game acceptance checks. An
upstream field called `Unknown`, an unlabelled bit or a trainer's live-memory
offset is not sufficient evidence for a new save-edit operation.

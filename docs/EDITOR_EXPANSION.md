# v0.18.0-alpha — Party, equipment and inventory expansion

This release adds verified file-format operations, not a claim of complete game
support or confirmed loading in-game. Changes apply directly to the opened file.
Downloaded fixtures and personal saves are not distributed or installed over
active game saves during validation.

## Kingdom Hearts Final Mix and II Final Mix

The Characters selector includes saved combat companions: KH1 excludes Pooh,
and absent zero-level companion records remain unexposed. KH2 covers all thirteen
named party records when present. Story/world-party availability is unchanged.

- KH1 adds saved level/experience, equipment and ability lists. KH2 adds equipment
  and abilities to its existing attributes; five main Drive Forms also expose
  their weapon and twenty-four-entry ability lists.
- Sora, Donald and Goofy weapon selectors filter Keyblade, Staff and Shield IDs.
  World companions retain their original weapon. Unidentified identities are
  read-only. Armor/accessory/item selectors edit only already unlocked slots;
  counts and auto-reload arrays are preserved.
- Existing abilities keep their order and duplicates. One empty entry is shown
  for adding a known ability; after applying, the next empty entry is exposed.
  Unknown identities remain read-only, including unrecognized ability flag bits.
- KH1's byte high bit means **unequipped**; KH2's ushort high bit means **equipped**.
  Choice indexes are UI values, translated to native IDs before checksum updates.
- Equipment edits do not exchange bag counts or recalculate equipment-derived
  attributes. Ability AP budgets, character-specific actions, mutually exclusive
  growth tiers and story availability are **not validated or recomputed**.
  Keep character-appropriate abilities; this is an advanced ability-list editor.

Layout: KH1 character `+4 + n*0x74`, weapon `+0x32`, XP `+0x3c`,
48 byte abilities `+0x40`; KH2 `+0x24f0 + n*0x114`, weapon `+0`,
armor/accessory/item arrays `+20/+36/+52`, 80 ushort abilities `+84`.
Main forms use `+0x32f4 + n*0x38`, weapon `+0`, 24 ushort abilities `+8`.
PNG block CRCs and KH2 internal checksums are refreshed; unrelated slots and
system records are preserved. KH1's expanded operations are marked experimental.

## Elden Ring

The Collection selector now includes **Add items**, alongside Inventory/Storage.
Only the existing supported stackable-goods catalogue is eligible: no weapons,
key items, quest objects, shared pot/perfume containers or unknown IDs are created.
Zero keeps an absent good absent. A depleted existing stack is reused; a new
stack uses a clean empty held record, updates the count and both native counters,
and registers its `0x40000000 | id` in the active item registry. Inventory sort IDs
use distinct stride-two buckets above existing held/key records; equip-list
counters advance by one only for a new record. Inconsistent counts, full pools,
unsupported registry headers and overflow fail closed. Creation is held-only;
storage retains existing-stack editing.

Known owned armaments expose reinforcement within +25/+10 limits. Their base
identity, affinity, Ash of War and handle stay unchanged. Equipped IDs in all
three character representations and the menu snapshot must agree before they
can be edited; their copies and weapon fingerprint then update together. The
historical highest weapon level only increases. Upgraded IDs are registered;
the old registry entry is retained, matching normal acquired-item history.

The native registry has an eight-byte header, an active list of eight-byte
ID/flag pairs (bounded to 7,000 entries) and an opaque preallocated tail. Insertions
retain the legacy prefix and Ash-of-War group, inserting only in the final sorted
ordinary segment. Tail bytes beyond the newly expanded active range are kept.

NG+ cycle (`0..7`) changes difficulty scaling; it **does not start a new journey**,
reset defeated bosses or change quests/graces. It is at `+0x6d` after the variable
unlocked-region list. Shared account data and other characters are retained.
Four public native files were checked in memory, including new goods and upgrades;
native revision-261 and loading edited files in-game remain unverified.

## Resident Evil 4 (2005), Steam Ultimate HD Edition

The Collection category adds existing case quantities and known weapon tune-up
tiers. Records begin at slot `+0x373c`, 384 entries of twelve bytes. The second
ushort holds stack quantity or the weapon's four upgrade nibbles. Weapon rounds
are preserved at `+4`, including low flag bits; `+6` and case coordinates,
rotation and presence bytes remain untouched. Only physically present known
case objects are exposed; unknown identities remain intact.

Firepower, firing speed, reload and capacity use per-weapon documented limits.
Capacity can only increase so existing loaded rounds are not invalidated. Unknown
or modded tiers are read-only. This does not rebuild merchant unlocks, place new
weapons, move objects, unlock costumes or provide arbitrary exclusive flags.
Changing a supported tier updates the selected slot's two CRCs only.
All four local records were patched/reparsed in memory with byte preservation;
edited-save loading in-game remains pending.

## Resident Evil 6

Campaign's three equipped skill IDs are at `1920`; eight Mercenaries sets of
three IDs are at `2344`. Selectors provide known campaign-compatible skills
`0..60`, including None, with an explicit preserved choice for an unknown current
ID. They translate selections to native unsigned words and update the additive
checksum. Skill purchase flags, mode-specific skills, infinite-ammo game settings,
emblems and campaign progression are not changed. Equipping a skill is not a
purchase/unlock guarantee. A public native Steam profile and synthetic boundary
fixtures were checked; loading edited output in-game remains pending.

## Still outside this release

Elden Ring boss/quest progression and new equipment creation; RE4 new case objects,
comprehensive unlocks and costumes; a full RE5 inventory/upgrade editor; the
unmapped HD Remaster slots; native Steam verification and broader mapped fields
for the RE2/RE3/RE4 Remake/RE7 readers. Other games retain their prior documented
scope. No editor is described as supporting everything.

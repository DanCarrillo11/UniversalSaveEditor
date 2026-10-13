# v0.25.0-alpha â€” Functionality across the existing catalogue

This update expands 17 existing editors. New games and artwork work are paused.
It does **not** certify complete support for every game. Unknown fields are not
turned into guessed controls, and file-level checks are separate from game loading.

## WEBFISHING

- Original cosmetic ownership, appearance selections, accessories, lure ownership
  and equipped lure. Selecting a cosmetic/lure grants its saved ownership entry.
- Existing item identities, quality/size, individual removal, item locks and hotbar
  assignment. Removal clears only matching hotbar/aquarium/locked references;
  reassigning a hotbar slot to a surviving item in the same edit is supported.
- Add ordinary fish, tools, furniture and other known inventory objects by choosing
  a total count. New objects use unique positive references, normal quality, size
  1 and empty tags. At most 500 new objects per apply and 10,000 total.
- Existing quest progress and journal quality memberships. Rewards are claimed in
  the game; reward amounts, tiers and completion lists are preserved.
- Equipped bait requires a positive saved quantity; adding bait still synchronizes
  its acquisition automatically. Concurrent variable-length changes are applied
  against original spans in descending order, with one final length update.

Unknown IDs, original encoded entries, tags and unrelated dictionary members are
retained. The operations do not synthesize missing quest/journal records. Original
variant widths are kept where possible; a hotbar reference above signed-int32
capacity widens to Godot's int64 encoding. Cosmetic compatibility, accessory limits,
quest rewards and gameplay loading need further checks.

## Kingdom Hearts

- KH1: per-character availability bits for seven magic families. Tier, story and
  shared acquisition state remain unchanged; unrelated bits are retained.
- KH2: per-item-slot auto-reload identities, using known consumables and already
  unlocked slots. This does not create inventory stock.
- KH3: party weapons, armor, accessories, consumables, active weapon selection and
  155 known ability identities. Acquisition/equipped bits are changed together;
  unseen and reserved flags are retained. Inconsistent existing flags are read-only.
  Bulk actions learn, equip learned, unequip or restore abilities. Exact mapped
  equipment names grant at least one inventory copy and the obtained bit; conflicting
  zero-stock edits are rejected. Unknown/world-specific weapons are retained.
- Birth by Sleep: character-specific equipped Keyblade, existing finisher XP, and
  deck references into the existing command pool. Unknown and observed multi-slot
  battle references are protected; descriptor modifier words stay unchanged.
- Dream Drop Distance: character-specific Keyblades and Attack/Magic/Defense for
  existing recognized Dream Eaters. Spirit identity, name, boards, affinity, XP,
  creation and party references are not changed.

Ability AP budgets, character-specific actions, complete story systems and missing
acquisition dependencies are not recalculated. Re:Chain of Memories retains its
existing card quantities, XP, money and difficulty scope; decks/CP/HP are unmapped.

## Resident Evil

- HD Remaster: parse the actual section directory rather than a fixed first-slot
  offset. All recognized gameplay sections can be selected. Edit known inventory
  and item-box identities, clear them, or fill the next clean empty item-box entry.
  Quantity, section size, unrelated slots/system data and SHA1 are preserved or
  updated as required. Creating a record does not create a playable campaign slot.
- RE5: 45 figure flags in their 64-bit mask, preserving reserved bits. Library-file
  labels follow the native bit order. Existing currency/costume/ammo flags remain.
- RE6: add uncollected Serpent Emblems without rewriting existing nonzero states;
  edit Solo/Duo Mercenaries rank, score, defeated enemies and combo records for ten
  stages and sixteen character variants. Add equipped skill slots for Siege,
  Onslaught, Survivors and Predator. Extra modes expose known shared IDs 0–96;
  mode compatibility and purchase records are not verified or automatically granted.
- RE2: saved difficulty, completion/challenge records, counterattacks and Ghost
  Survivors counters/flags. RE3: existing completion/challenge/combat counters.
- RE4 Remake: existing costume/accessory unlocks, extra-shop availability/purchase
  flags and challenge progress. Exact profile ancestry and a unique typed sibling
  identity are required; scene lookalikes and ambiguous IDs are excluded.
- RE7: saved difficulty, restarts and existing DLC completion/mode flags.
- Village: additional saved player health and existing lifetime/completion/combat
  records. The additional player's name is not assumed from its internal ID.
- Requiem: existing game-completion, combat, crafting, ink, blood and challenge
  progress records, alongside the earlier player health/inventory/attached upgrades.

Completion flags and counters do not independently synthesize rewards, purchases,
Steam achievements, scenario prerequisites or installed DLC. RE4 (2005) retains
its prior case quantities, upgrades, health, difficulty, money and statistics.
RE Engine array creation/resizing, full inventory layouts, named unlock identities
and several weapon/difficulty systems remain documented research work.

## Elden Ring and Risk of Rain 2

Elden Ring adds 96 named FACE appearance sliders and the saved death counter.
The FACE header must match before sliders are exposed. Body proportions, skin,
makeup, tattoos, hair and both eyes can be adjusted independently; model IDs,
unknown blocks, presets and body type stay unchanged. Only the selected character's
MD5 is updated. New weapons/armor, equipment placement, affinities/Ashes and complete
quest/Grace systems are still outside the verified scope.

Risk of Rain 2 exposes additional existing numeric profile statistics, including
per-character, enemy, stage and item records. Nonnumeric/duplicate XML remains
unchanged. Internal identifiers and unmapped units/dependencies are explicit.
Large categories show 100 records per page with section selection, full search and
changed-only filtering; edits survive page changes. This is profile editing, not
live-run inventory manipulation. Installed DLC still requires ownership.

Alice's persistent/configuration scope and Max Payne's tagged inventory scope
remain unchanged. Active Alice outfit/checkpoint remain excluded by user preference;
Max Payne health, Bullet Time and loaded rounds require a verified mapping.

## Validation

Synthetic checks exercise coupled ownership, concurrent array growth, high item
references, deletion/reference cleanup, readonly flags, reserved ability/figure
bits, multi-slot directories, malformed inputs, exact profile contexts, per-slot
preservation and paged UI editing. Preview examples are generated through adapters
from synthetic fixtures and contain no personal saves or writable offsets.

In-memory native checks cover WEBFISHING, Risk of Rain 2, KH1/KH2, BBS/DDD,
KH3, HD Remaster, RE5/RE6, four public Elden Ring files and nine Requiem files. Active
files are not overwritten during verification. Some samples share player data;
they are not independent gameplay certifications. Complete support and loading
edited saves in every game cannot yet be claimed.

Subsequent corrections and input improvements are documented in [v0.25.1 editor polish](EDITOR_POLISH.md). RE6 generic quantities are superseded by identified ammunition/herb reserves; weapon and unknown count words are protected.

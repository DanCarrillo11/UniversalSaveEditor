# KH1 spell tiers and acquisitions

The Steam Final Mix editor now distinguishes the seven shared spell-tier bytes
from each character's spell availability. Sora can learn or upgrade each family
through its three tiers. A new acquisition also enables Donald's matching spell
unless his availability is explicitly edited in the same transaction. Removing
Sora's spell preserves Donald's availability and the shared tier; matching Sora
shortcuts are cleared. Existing reserved bits and unsupported tiers are retained.

Under Characters > Sora > Summons, acquire Dumbo, Bambi, Genie, Tinker Bell,
Mushu or Simba. Additions append to the recognized compact list without changing
the existing order. Duplicate, unknown or noncompact lists are protected.
Existing acquisitions cannot be removed by this tool.

Progress includes the five learned Trinity colors and zero to five unspent Torn
Pages. Collection includes all 99 rescued puppy flags and a derived rescue count.
Trinities and puppies are add-only. Consumed-page history, activated Trinity
marks, chests, story progress, journal state and claimed rewards are preserved;
these controls do not automatically grant rewards or complete world events.

## Verification and limits

Independent regression checks cover bit order, compact-list ordering, reserved
bits, explicit Donald overrides, bounds, unsupported formats, immutable inputs,
category navigation and changes retained across search. File-level checks on 39
populated public Steam records applied 231 spell-tier changes, 145 new summons,
90 new Trinity colors, 2,274 puppy flags and 39 unspent-page requests. Every
record reparsed with valid integrity; the reference file and unrelated bytes,
including reward flags, remained unchanged.

These are file-level results, not an in-game verification. Recognized standard
AP budgets are now checked as described below. Remaining AP costs, equipment
relationships, complete growth, story/journal dependencies and reward delivery
remain incomplete. No full-support certification is claimed.

## Recognized AP budgets (v0.50)

Characters > select a character > Abilities shows equipped and available AP when
all active costs and equipped accessory identities are recognized. Availability
is saved base AP plus the standard bonuses of the unlocked accessory entries.
An equipped duplicate consumes its own AP. KH1's high bit means unequipped;
empty flagged entries consume none. Pooh and absent/unsupported characters do
not receive an inferred budget.

Ability, base-AP and accessory changes form one transaction. Increasing the
known AP deficit is rejected with an explanation; sufficient base AP or another
accessory can be selected in that same change. Existing inconsistent excess can
be preserved or reduced. This does not move stock, change learned growth,
recalculate other stats, or infer character-specific ability compatibility.

59 standard ability costs and 64 accessory AP rows were checked against the
original installed PC battle table; only the 54 named supported accessories are
used. Unknown active costs (including the two unmapped later ability IDs),
unidentified accessories, unsupported slot counts and non-byte derived capacity
hide the calculation. No budget is guessed for those cases or modified tables.
Public save inspection found 345 recognized character budgets across 39 records;
16 require their accessory bonuses to cover equipped costs. None exceeded the
calculated total. 345 base-AP changes and 66 enables of existing owned abilities
passed native reparsing, unrelated-byte checks and exact restoration of every
non-CRC byte. The original reference stayed unchanged. Loading edited saves in
the game is still unverified.

Format references and pinned revisions are listed in [SOURCES.md](../SOURCES.md).

## Equipment ownership and carried reserve (v0.52)

Normal equipped weapons and accessories now synchronize their saved ownership.
The count includes equipped accessories across recognized companions, including
duplicates. Selecting equipment adds only missing copies; unequipping does not
sell them. Explicit inventory edits cannot worsen an existing ownership deficit
or conflict with newly selected equipment. Existing unrelated deficits remain
unchanged. Sora's temporary Dream/wooden story weapons retain their context and
cannot be acquired through ordinary equipment or inventory controls.

Carried consumables use a separate reserve quantity. Replacing an unlocked item
slot returns its old copy and consumes the new one. All slot and reserve edits
are one transaction: swaps need no spare copy and final reserves must fit 0–99.
An explicit reserve quantity is the amount before these transfers. Hidden slots,
unknown identities, unsupported counts and absent characters are not inferred.
AP/HP/MP checks and review of automatic related changes remain active.

39 native records corroborate 405 recognized owned equipment configurations;
66 carried counts exceed reserve, so those representations must not be treated
alike. 39 accessory, 39 consumable and 35 normal weapon changes pass reparsing,
unrelated-byte checks and exact non-CRC restoration. Originals remain unchanged.
These file checks do not establish successful game loading or completion of
all growth, story, reward and character-specific equipment rules.

## Equipment-aware maximum HP and MP (v0.51)

The character's Attributes section shows recognized maximum HP and MP with
equipment. Base values remain separate. 54 accessory HP/MP pairs and 52 signed
weapon MP bonuses match the original PC battle table. Only supported character
weapon families contribute; world companions' unmapped MP behavior is preserved.

Base, current and equipment edits are checked together. Reducing a known maximum
clamps a previously valid current value; an explicitly requested excess is
rejected. Increasing the maximum does not heal or refill. Existing unexplained
excess, unknown equipment and modified/runtime effects are not recalculated.
Unsupported totals outside the byte range are not assigned guessed saturation.

39 public records contain 351 recognized HP and 117 MP configurations; 59 valid
current HP values exceed saved base HP, which must not be used as their limit.
351 HP and 117 MP base edits, with 350 HP and 108 MP automatic clamps, passed
reparsing, unrelated-byte checks and exact restoration of non-CRC bytes. The
original reference stayed unchanged. Loading edited saves is still unverified.

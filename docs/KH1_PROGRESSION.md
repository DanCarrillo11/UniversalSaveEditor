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

These are file-level results, not an in-game verification. AP budgets, equipment
relationships, complete growth, story/journal dependencies and reward delivery
remain incomplete. No full-support certification is claimed.

Format references and pinned revisions are listed in [SOURCES.md](../SOURCES.md).

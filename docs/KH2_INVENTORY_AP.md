# KH2 Final Mix: stock, AP and acquisition relationships

## Correct native stock positions

The bag has 320 byte positions at record-relative `3580`. Those positions are
not equipment/item IDs. Potion is stock position 0 / item ID 1; Kingdom Key is
position 33 / ID 41; Two Become One is position 280 / ID 543. Earlier versions
incorrectly reused some equipment IDs as stock labels and artwork identities.
The corrected adapter names 278 recognized stock positions, groups them by
their native item category and uses the separate item ID for existing artwork.
Six positions are exposed as spell tiers instead. Unmapped positions and
out-of-range quantities remain protected, without guessing an item identity.

Names and positions cross-check KingdomSaveEditor's InventoryType and OpenKH's
Final Mix item fixture. Dummy stock positions 72/73 remain protected. The 0–99
quantity bound is an editor bound; no wider runtime quantity range is inferred.

## Equipment transactions

Changing a recognized equipped item consumes one bag copy and returns the old
copy. Changes to multiple slots are processed as one transaction: two characters
can swap accessories without a spare bag copy. Explicit bag edits establish the
quantity before transfers; final review shows the resulting quantity.

Character weapons, armor/accessories, equipped consumables and the offhand
Keyblades for Valor, Master and Final participate. Auto-reload identities remain
independent. Wisdom/Limit do not expose unused offhand slots. New duplicate
Keyblade assignments between Sora and the three dual-wield forms are rejected;
changing both assignments together permits a swap. Missing stock, overflowing
returns, unsupported identities and mismatched slot categories are rejected.
Other equipment, inventory bytes, story and world variants remain unchanged.

## Recognized standard-data AP

For supported layouts, the adapter displays learned-ability AP used and available
AP from the standard character's level row, saved AP boosts and equipped item
bonuses. Equipment-granted abilities do not add learned-ability cost. Duplicate
saved learned entries remain separate. An edit cannot increase an existing AP
deficit; an already inconsistent reference is retained and can be improved.

The facts come from OpenKH's item and Final Mix level-table fixtures. Ability
cost is the byte at item entry +7 (Scan 2, Upper Slash 4, Combo Plus 1), not the
adjacent type byte. Equipment AP is stat entry +7. Some abbreviated variable-
structure documentation reverses the ability type/cost labels; the fixture and
published game-guide examples distinguish them.

Unknown active abilities, unsupported equipment/counts/levels and calculated
budgets above 255 leave this calculation unavailable. Modified game tables can
have different costs/growth; a save alone cannot identify those installed tables.
These checks do not certify every character-specific ability or growth rule.

## Magic, shortcuts, forms, summons and reports

Fire/Blizzard/Thunder/Cure use bytes `3594`–`3597`; Magnet/Reflect use `35cf`/
`35d0`. Each supports absent plus three learned tiers. Four shortcut words at
`36f8`–`36fe` follow changed spell tiers and clear on removal. Explicit spell
shortcuts require a learned family. Item shortcuts require Sora to carry that
consumable; removing its last equipped copy clears its matching shortcut unless
a conflicting explicit shortcut was requested. Unknown commands are preserved.

Recognized acquisition bits cover six forms, four summons and 13 Secret Ansem
Reports. Acquisitions can be added; existing acquisitions are protected against
removal. Newly acquired playable forms initialize a zero level to one and reset
only the documented Anti-point byte at `3410`; the other Antiform bytes remain
unchanged. Newly acquired summons initialize a zero summon level to one.
Conflicting explicit level/Anti-point edits are rejected. Current Drive clamps
when only its maximum is reduced; an explicit current/maximum conflict fails.

Acquisition does not rewrite story, journal completion, collection rewards,
achievements or form-growth rewards. World/story availability can still apply.
The five known playable form levels remain independent of their stored XP;
unknown Lion/Roxas/unused form rows are no longer mislabeled as progression.

## Evidence and remaining work

Tests cover exact bag indexes, item/art identity domains, byte preservation,
conserved swaps, failed transfers, AP conflicts, unknown encodings, spell tiers,
shortcut dependencies, acquisition masks and current/maximum Drive.

In-memory checks on 59 populated public Steam player records submitted 354
spell-tier requests, added 672 previously absent acquisition flags and verified
49 conserved weapon transfers. All edited records reparsed with valid integrity;
unrelated bytes and the original file were unchanged. Standard-data AP could be
calculated for 708 character records. 41 existing cost/budget mismatches were
retained; their cause and in-game behavior are not assumed from those files.

These are file-level checks, not in-game validation. Complete character rules,
growth/reward dependencies, puzzles, journal/story systems and all variants
remain pending. This release does not mark KH2 or the full catalogue complete.

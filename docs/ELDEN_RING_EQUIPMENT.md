# Elden Ring physical equipment creation

Under Inventory, choose Add weapons, Add head armor, Add chest armor,
Add arm armor or Add leg armor. Enter the number of copies to create, up to ten per
entry per application. There are 377 mapped base-game armaments (including
shields/catalysts) and 559 mapped base-game armor pieces. Existing copies stay
unchanged. New pieces enter held inventory unequipped, at +0, without a custom
Ash of War. Reinforce eligible weapons using their existing upgrade controls
after applying. Meteorite Staff is correctly protected as non-reinforceable.

## Required relationships

Each piece receives a separate physical GaItem record, unique native handle,
held-inventory row and acquisition-order entry. The item registry, inventory
count and its two counters update together. Native two-pass record order is
checked, including the compact Ash-of-War prefix and physical index holes.
Existing variable-size records remain byte-exact, including custom Ash links.

Weapon records grow by 13 bytes and armor records by eight bytes when replacing
an eight-byte empty record. Growth moves the following character data as one
bounded span. Only verified terminal zero padding may be consumed; the final
178 bytes remain at their original position. The complete output is reparsed,
and newly created physical records and held ownership are checked before saving.
Same-size edits, existing upgrades, spell changes, goods additions and edits to
other characters are applied before structural growth. Other characters,
global menu data, account data and regulation bytes are not shifted.

Combined requests must fit physical holes, clean inventory rows, registry and
counter limits, and verified padding. Equipment creation capacity explains why a
particular representation cannot be extended. Existing unknown data is preserved,
not discarded to make room. Decreasing a request or making fewer additions may
resolve a combined capacity conflict; no automatic repair of malformed records
is performed.

## Evidence and remaining scope

Regression checks cover native record order, distinct copies, existing custom
Ash references, growth above 512 bytes, anchored tail data, unrelated relocated
bytes, simultaneous edits, counter/registry overflow, exact menu collisions,
unsupported layouts, empty requests and interface navigation.

In-memory tests on four public PC files successfully created equipment in 18
character records. The samples overlap and are not 18 independent playthroughs.
Ten other records were protected because their terminal zero padding was
insufficient. Originals remained unchanged. These results establish structural
reparsing and byte preservation; loading the output inside Elden Ring has not
been verified.

Creation excludes DLC equipment, cut/debug identities, custom affinities and
Ash attachment. Owned loadout selection, armor alteration, quest/reward delivery,
gestures and full world/DLC progression are still incomplete. This is an expansion
of experimental Steam SL2 support, not full-support certification.

Pinned primary references are listed in [SOURCES.md](../SOURCES.md).

# Initial Rockstar PC Story Mode support

v0.36 adds GTA V and Red Dead Redemption 2 to the library. Both are labelled
Limited coverage. No full support or successful edited-save loading is claimed.

## GTA V — Legacy and Enhanced scope

The reader recognizes the PC `SGTA5####` story envelope, header version 1,
AES body at 0x108 and an exact framed PSIN/PMAP/PSCH/PSIG checksum region.
The native PSO schema must identify the signed-int statistic-pair structure
0x83125968, size 8, with its exact key/value field hashes, types and offsets.
Statistics are enumerated from that mapped block, not matched against arbitrary
bytes elsewhere in the file. Unknown structures are never rewritten.

Michael, Franklin and Trevor each expose existing cash plus Stamina, Shooting,
Strength, Stealth, Flying, Driving, Lung capacity and Special ability. A known
statistic must occur exactly once. Missing or duplicate entries remain protected;
out-of-range values are read-only. The editor bounds these skills to 0–100 and
cash to nonnegative signed int32. Editing a statistic does not create a playable
character, grant missions, rewards, weapons, vehicles, garages or clothing.

Both `Rockstar Games/GTA V/Profiles/*/SGTA5####` and
`Rockstar Games/GTAV Enhanced/Profiles/*/SGTA5####` are discovered under the
Windows Documents location, including a redirected OneDrive Documents folder.
There is one GTA V library entry. Matching is based on the actual file structure,
not merely its directory or name. This is not a Legacy/Enhanced conversion tool.

Two public Legacy files passed valid original integrity, byte-identical no-op
encoding, all 27 field edits per file and byte-identical restoration. The
originals remained unchanged. An Enhanced-specific native file was unavailable;
that verification remains pending and is explicit in Help & details. Discovery
of the Enhanced folder does not certify every Enhanced save revision.

### Expanded GTA V fields (v0.42)

Exact singleton schemas now expose the saved active protagonist's health, armor,
their maxima, and saved stamina/reload/fire/drive-by/gang flags. Only recognized
Michael/Franklin/Trevor model hashes qualify. This record is separate from the
three protagonists' statistics. Reducing a maximum clamps its current value;
explicit contradictory current/maximum edits are rejected. Editor maxima are
bounded to 1000, not advertised as engine limits. Unknown/nonfinite/out-of-range
states are protected. Scripts may reset saved flags or values after loading or
switching characters; no lasting cheat or achievement behavior is guaranteed.

World controls expose hour/minute/second and garage free/disabled respray flags.
Calendar, weather interpolation, wanted-level encoding, script globals, account
identifiers and unknown fields are preserved. In particular, the saved maximum
wanted-level encoding is not interpreted as a 0–5 star count.

Existing occupied garage vehicles expose six saved damage/tire protection flags
and up to eight printable ASCII license-plate characters. Root SafeHouses and
each VehiclesSavedInThisSafeHouse array must resolve bounded, correctly aligned
typed records with unique membership, valid counts and known 96/112-byte schemas.
Only bUsed=1 records with nonzero models qualify. Empty slots, orphan records,
invalid arrays and unknown encodings are untouched. Plate padding is checked;
the opaque pointer word is preserved. These controls do not create vehicles,
swap models, repair mechanical health, grant ownership, or edit tuning/liveries.

Two native Legacy references expose 48 and 69 total controls, depending on their
occupied vehicles. New fields pass individual exact-span edits, checksum
verification, combined edits and byte-identical restoration in plaintext and
encrypted copies. Originals remain unchanged. These are file-level checks;
game loading/persistence and Enhanced-specific native files remain unverified.
Weapon/ammunition inventory, property/clothing acquisition, collectibles and
mission/reward dependencies are still unsupported. **GTA V is not full support.**


### GTA V story weapon inventories and shop acquisition (v0.43)

The typed ScriptGlobals root and its embedded character-inventory path must match
the declared member hashes and bounded sizes. Both high PSCH offset bits are
resolved. Known three-cell (44 + 50 records) and five-cell (44 + 51 records)
shapes are distinguished; the count is a byte in an eight-byte VM cell, not u32.
All scalar types, offsets, first-row member names and unique slot membership are
checked. A separate unidentified fourth inventory snapshot is preserved.

Thirty-five named base slots can be added/removed for each protagonist. Slots
occupied by unexpected identities and duplicate identities are protected. Existing
named extra weapons expose supported ammunition/customization but new DLC slot
placement is not inferred. Ammunition updates synchronize carried weapons of the
same type and character; inconsistent pools stay read-only. Simultaneous conflicting
totals are rejected. The cap uses highest story shooting-skill capacity; runtime
skills may apply a lower cap. Non-ammo weapons do not get meaningless ammo controls.

The older color encoding is one bit in positions 20–27; modern records have a
separate tint field. Component bit positions also differ between revisions.
Only mapped components are exposed; unknown bits, cell padding and modern livery
color are preserved. Selecting competing components in one attachment point is
rejected. Installing one part replaces its recognized peers in that point.

Shop controls cover 40 weapons and mapped component/color acquisition. Each
SP0/SP1/SP2_WEAP_* bank must have exactly one correctly typed stat row. Masked
uint32 operations preserve unrelated flags, including signed bit 31. Purchasing
requires availability; attachment purchases unlock that attachment. Turning off
weapon availability also clears its shop purchase flag. Contradictory explicit
requests are rejected. Inventory additions/components/colors synchronize recognized
shop ownership without spending cash. Shop ownership alone does not put a weapon
in the carried inventory or bypass game-edition restrictions.

Three native references cover both inventory shapes. The first two are the public
Legacy references above; the third is a built-in PC template inspected statically
from the user-supplied reference editor. No template/resource is packaged. Checks
pass 1,191 individual masked shop edits per file, combined changes, requested-value
reparsing and all container checks in encrypted/plain copies. The originals remain
unchanged. Synthetic fixtures additionally exercise the extended 131072-byte
schema offset, invalid counts, duplicates, ammo consistency, acquisition dependencies,
one-hot/direct tints, component conflicts and opaque padding/livery preservation.

This remains partial coverage. Full DLC acquisition, vehicles/models/tuning,
properties, clothing, collectibles and complete mission/reward dependencies are
not implemented. Enhanced-native validation and edited-save game loading remain
unverified. File-level checks are not evidence of successful game loading.


### GTA V garage appearance and performance (v0.44)

The existing occupied-vehicle membership graph also gates its embedded variation
structure. Known 40/48-byte variation shapes must match the 96/112-byte parent;
every exposed member needs its exact hash, unsigned-byte type and declared offset.
Named primary/secondary/pearlescent/wheel paint use the 161 known palette indexes.
Window tint is bounded to its seven named values. Unknown/sentinel palette/tint
values are preserved rather than silently assigned a label. Smoke/neon RGB values
do not install or enable their corresponding modifications. Model names are read-only.

Performance edits follow the existing mods ATBINARYMAP: bounded PSO pointer,
count/capacity, typed eight-byte hash/byte pairs, sorted unique keys and unique
membership across vehicles are required. Existing engine/brake/transmission/
suspension/armor entries must match the named model's stored kit and its known
contiguous stage range. Stock is saved as 255; the UI shows Stock then stage 1
onwards. Unknown stages are not reinterpreted or clamped. EV models do not receive
unsupported transmission stages. No map rows or garage records are created.

A vehicle with no installed kit (255) and exactly one known model kit can initialize
that kit when applying an actual upgrade. An explicit stock no-op retains 255.
This initialization is an additional byte change; reverting a stage to stock does
not infer the earlier kit setup. Other map nodes, node padding, coordinates,
models, wheel/body/livery parameters and membership remain unchanged.

Two native Legacy files expose 15 and 55 new editable appearance/performance
controls, plus read-only model labels. Individual/combined edits pass exact-span,
requested-value reparsing and checksum checks in plaintext/encrypted copies.
Original files remain unchanged. Synthetic and UI tests cover both layouts,
default-kit activation, unknown kits, broken pointers, duplicate/unsorted maps,
opaque node bytes, palette/tint bounds, staging/reset and offline previews.
Successful in-game loading, persistence and Enhanced-native validation remain
unverified. Vehicle/model acquisition and complete body/wheel/livery tuning are
still unsupported; this is not full GTA V compatibility.

## RDR2

The PC `SRDR#####` story envelope has header version 4, AES body at 0x110 and
RSAV magic. Every framed PSO checksum region is bounded and indexed; overlapping
regions, malformed mapping/schema lengths and unsupported cipher envelopes fail.

The initial adapter exposed current carried cash. v0.37 adds the schema-gated
fields documented in [RDR2_FIELDS.md](RDR2_FIELDS.md); v0.38 adds camp funds,
synchronized horse XP, horse cores and recorded history. v0.39 adds guarded
monetary bounties, existing catalog unlock actions and experimental ordinary
satchel-supply acquisition. Cash resolves a unique typed CURRENCY_CASH record
in SLOTID_CURRENCY (CE548CF5), following only active inventory membership when
that graph exists. Orphan bytes and malformed graphs cannot supply a fallback
cash match. The signed 64-bit Quantity must be within 0..2147483647 cents;
the zero high word is preserved. The UI displays dollars and rejects more than
two decimal places rather than silently rounding. This serialized bound is not
a claim about the game's displayed money cap.

Historical earnings, weapon/clothing acquisition, stable slots,
missions, challenge rewards and online state stay unchanged. Console quick-code
addresses alone are not treated as PC field semantics.

Three local PC story files (manual saves and autosave) passed all ten original
payload checks, byte-identical no-op encoding, cash edits and byte-identical
restoration. Only in-memory copies were edited; personal files were unchanged.
These checks do not establish game-load success or any other mutable field.

## Integrity, writing and privacy

AES-256 ECB is limited to the recognized body; its length/alignment is checked.
Rockstar CHKS uses signed-byte Jenkins arithmetic, unlike ordinary name hashes.
Each region includes its CHKS record with its length/checksum words zeroed for
calculation. GTA V title and RDR2 date header checks are separate. Unknown
headers, gaps, padding, schema bytes and signatures remain preserved. Ordinary
field edits preserve length. Experimental supply acquisition uses bounded CODE
block growth, checked RSAV directory offsets and unchanged script chunks; see
the allocation assumptions in [RDR2_FIELDS.md](RDR2_FIELDS.md).
Original integrity mismatches require explicit repair; repair is not proof of
intact game state. The finished output is reparsed and requested values verified.

Apply replaces the opened save directly using its original name/location. No
automatic save backup or `.edited` file is introduced. Existing `.bak` files are
excluded from discovery and are not overwritten. No personal saves, decrypted
samples, account IDs, story titles or game executable are distributed. Offline
previews use synthetic fixtures. Source attribution is in SOURCES.md.

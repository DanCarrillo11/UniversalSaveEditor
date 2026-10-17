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

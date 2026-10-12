# v0.15.0-alpha — Resident Evil expansion

Eight initial experimental editors join Resident Evil 4 (2005), bringing the
library to 19 games. This release adds game-specific categories, automatic Steam
save discovery, complete portrait artwork and account-aware RE Engine opening.

- **HD Remaster:** first mapped slot only; difficulty, defensive supplies,
  save count and existing inventory/item-box quantities.
- **RE2:** player health, existing inventory quantities, reward and library flags.
- **RE3:** player health, existing inventory quantities, total shop points earned,
  shop-item possession and reward flags.
- **RE4 Remake:** extra content points, Spinels and existing inventory quantities.
- **RE5:** money, exchange points, costume/filter flags, 19 infinite-ammo flags
  and library-file flags. Infinite ammunition does not grant its weapon.
- **RE6:** Skill Points, Mercenaries character/costume and stage flags, No Mercy
  stages and existing character supply quantities.
- **RE7:** player health and existing item-box quantities.
- **Requiem:** money, Clear Points, extra-shop availability/acquisition/received
  flags, bonus content, artwork/figure availability and purchases, special options.

All changes apply directly to the opened file, keeping its name. No automatic
backup or `.edited` copy is created. Close the game before applying.

## Validation and limitations

RE5 and RE6 public Steam profiles, an HD Remaster public PC-format profile, and
nine native Requiem Steam files were checked for reading, integrity, identical
export and in-memory changes. RE3 and RE7 common serialized fields were also
checked against public console payloads; those are not PC fixtures.

RE2, RE3, RE4 Remake and RE7 still need real Steam fixture verification.
**No newly edited Resident Evil file has been loaded in-game.** Every new editor
is marked experimental; it is not full support for every game feature or variant.
HD Remaster supports one mapped slot. RE Engine collections use saved entry
numbers, and profiles and gameplay slots contain different options. Item identity,
story state, upgrades and other unexposed fields are preserved. DLC still requires
ownership. RE0 reading research has advanced, but editing is not enabled yet.

Download `UniversalSaveEditor.exe` under Assets and double-click it. Python and
an installer are not needed. The source ZIP also includes the portable executable.

# v0.29.0-alpha — Equipment, spells and character controls

This release adds owned Requiem weapon equipment/shortcuts, owned
Elden Ring memorized spells with memory costs and active selection, KH1 magic
shortcuts and KH3 Critical-mode relationships/companion behavior. RE4 Remake
uses consistent native virtual-stack capacities instead of a fixed 999 bound.
Updated offline previews include these functions.

It also adds RE4 Remake Pesetas, player/partner health
and increasing case capacity; learning 171 mapped base-game Elden Ring spells;
and populated DDD spirits' stored level/XP, maximum HP, Link Points, link count,
RGB tint and recognized normal/shiny appearance. Native reference edits verified
spell acquisition in 19 characters and the new DDD fields in 13 spirits. RE4
Remake additions have synthetic encrypted tests; native Steam checking remains
pending. None of these checks certifies in-game loading or full game support.
RE2/RE3 now also expose increasing supported main-survivor inventory capacity;
existing slots/equipment and hip-pouch pickup events stay unchanged. RE3's
shared console payload passed a capacity reparse check, which does not replace
native Steam checking.
KH2 also exposes seven documented saved camera/map/vibration/command-menu
options. Native option edits were reparsed across 59 reference player records;
reserved bits are retained and in-game effect remains unverified.

No new games or artwork are added. Complete support for all 21 games has not
been achieved. Unknown structures, full item creation, rewards and gameplay
validation remain documented work. See docs/FUNCTIONAL_RELATIONSHIPS.md and
docs/CURRENT_GAME_COMPLETION.md for exact implemented rules and pending gates.

Automated and native-file reparse checks are separate from loading an edited
save in its game. Existing game/profile variants expose different functions.

Download UniversalSaveEditor.exe under Assets and double-click it. The portable
application requires no installer or terminal setup; Code > Download ZIP also
includes the executable. Changes update the opened file directly, without
automatic backups.

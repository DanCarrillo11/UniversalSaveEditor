"""Factual UHD identities; shared tune-up limits cross-checked on native bytes.

Sources: nipkownix/re4_tweaks SDK and dubiousnerd/re4vr-save-editor presets.
No upstream implementation is incorporated. See SOURCES.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
# Maximum levels include the native exclusive tier where the same nibble is used.
WEAPONS={
 3:('Matilda',(6,1,3,7)),33:('Punisher',(7,3,3,6)),35:('Handgun',(7,3,3,6)),
 37:('Red9',(7,3,3,6)),39:('Blacktail',(7,3,3,6)),41:('Broken Butterfly',(7,1,3,4)),
 42:('Killer7',(3,1,3,3)),44:('Shotgun',(7,1,3,6)),45:('Striker',(6,1,3,7)),
 46:('Rifle',(7,1,3,6)),47:('Rifle (Semi-Auto)',(6,2,3,6)),48:('TMP',(7,1,3,6)),
 54:('Mine Thrower',(4,1,2,3)),55:('Handcannon',(7,1,3,7)),148:('Riot Gun',(7,1,3,6)),
}
QUANTITIES={
 0:('Magnum Ammo',10,'Ammunition'),4:('Handgun Ammo',50,'Ammunition'),
 7:('Rifle Ammo',10,'Ammunition'),17:('Bowgun Bolts',10,'Ammunition'),
 24:('Shotgun Shells',15,'Ammunition'),26:('Handcannon Ammo',10,'Ammunition'),
 32:('TMP Ammo',100,'Ammunition'),70:('Mine-Darts',10,'Ammunition'),114:('Arrows',10,'Ammunition'),
 1:('Hand Grenade',1,'Consumables'),2:('Incendiary Grenade',1,'Consumables'),14:('Flash Grenade',1,'Consumables'),
 5:('First Aid Spray',1,'Consumables'),6:('Green Herb',1,'Consumables'),
 8:('Chicken Egg',1,'Consumables'),9:('Brown Chicken Egg',1,'Consumables'),10:('Gold Chicken Egg',1,'Consumables'),
 18:('Mixed Herbs (G+G)',1,'Consumables'),19:('Mixed Herbs (G+G+G)',1,'Consumables'),
 20:('Mixed Herbs (G+R)',1,'Consumables'),21:('Mixed Herbs (G+R+Y)',1,'Consumables'),
 22:('Mixed Herbs (G+Y)',1,'Consumables'),25:('Red Herb',1,'Consumables'),28:('Yellow Herb',1,'Consumables'),
 149:('Black Bass',1,'Consumables'),151:('Black Bass (L)',1,'Consumables'),168:('Mixed Herbs (R+Y)',1,'Consumables'),
}

"""Factual campaign-compatible skill IDs; no purchase-mask interpretation.

Cross-checked with lightningdotnet/resident-evil-6-save-editor/tables.h.
Names are independently formatted here. See SOURCES.md.
SPDX-License-Identifier: GPL-3.0-or-later
"""
SKILLS={0:'None'}
for first,name,levels in ((1,'Firearm',3),(4,'Melee',3),(7,'Defense',3),(10,'Critical Hit',3),(13,'Piercing',3),(16,"J’avo Killer",2),(18,'Zombie Hunter',2)):
    for level in range(levels):SKILLS[first+level]=f'{name} · Level {level+1}'
SKILLS[20]='Grenade Power-Up'
for first,suffix in ((21,'Master'),(29,'Infinite Ammo')):
    for index,weapon in enumerate(('Handgun','Shotgun','Magnum','Sniper Rifle','Machine Pistol','Assault Rifle','Grenade Launcher','Crossbow')):
        SKILLS[first+index]=weapon+' · '+suffix
for index,ammo in enumerate(('Handgun Ammo','Shotgun Shells','Magnum Ammo','Sniper Ammo','Grenades','Arrows')):SKILLS[37+index]=ammo+' · Increased Pickup'
SKILLS.update({43:'Last Shot',44:'Stealth Movement',45:'Quick Reload',46:'Lock-On · Level 1',47:'Lock-On · Level 2',48:'Rock Steady · Level 1',49:'Rock Steady · Level 2',50:'Breakout',51:'Item Drop Increase',52:'Recovery · Level 1',53:'Recovery · Level 2',54:'Combat Gauge Boost · Level 1',55:'Combat Gauge Boost · Level 2',56:'Eagle Eye',57:'Team-Up',58:'Field Medic · Level 1',59:'Field Medic · Level 2',60:'Lone Wolf'})
MODE_SKILLS={0:'None',**{identifier:label for identifier,label in SKILLS.items() if 1<=identifier<=60}}
for identifier,label in enumerate(('Shooting Wild','Go for Broke','Time Bonus+','Combo Bonus+','Limit Breaker','Blitz Play',
    'Quick Shot Damage Increase','Power Counter','Second Wind','Martial Arts Master','Target Master','Last Stand','Revenge',
    'Preemptive Strike','Gunslinger','Dying Breath','Pharmacist','Medic','First Responder','Take It Easy','Natural Healing',
    'Creature Point Boost','Creature Point Increase','Training'),61):MODE_SKILLS[identifier]=label
for first,name in ((85,'Creature Offense'),(88,'Creature Defense'),(91,'Creature Health'),(94,'Creature Stamina')):
    for level in range(3):MODE_SKILLS[first+level]=f'{name} · Level {level+1}'

"""Remaining functional gates for the current catalogue, separate from evidence.

SPDX-License-Identifier: GPL-3.0-or-later
A named pending gate is not an estimate of completion or gameplay validation.
"""
GAPS={
    'gtav':'Enhanced-native validation; DLC weapon acquisition; new vehicles/model swaps and complete body/wheel/livery tuning; properties; hair/props/composite outfits; mission, collectible and reward dependencies.',
    'rdr2':'Weapon/clothing acquisition; missing weapon-part slots; stable management; camp upgrades; complete story/challenge/reward dependencies; runtime allocation and in-game persistence verification.',
    'eldenring':'Affinities/Ash attachment; DLC equipment creation; Grace, gesture, boss and quest prerequisites; appearance model/preset dependencies; broader save revisions and in-game verification. Existing owned talisman loadouts do not grant items or recalculate derived stats.',
    're1_hd':'Player health/equipment verification; remaining inventory composite/examination state and capacities; progression/system unlocks; in-game verification.',
    're2':'Complete named item/equipment identities and inventory-slot state; reward delivery dependencies; native Steam and in-game verification.',
    're3':'Gameplay difficulty identity; complete inventory/equipment/shop dependencies; native Steam and in-game verification.',
    're4_remake':'Native Steam validation of gameplay fields; inventory geometry and new item creation; complete weapon upgrades and named reward dependencies; in-game verification.',
    're4_2005':'Verified case footprints/placement, new item acquisition and equipment relationships; weapon-capacity tables, costumes and complete unlocks; in-game verification.',
    're5':'Steamworks inventory/equipment, weapon upgrades and campaign records; reward/ownership dependencies and in-game verification.',
    're6':'Purchased/owned-skill relationships, full weapon identities and loaded rounds, campaign/checkpoint dependencies and in-game verification.',
    're7':'Inventory outside the item box; exact upgrade/unlock dependencies; native Steam and in-game verification.',
    're8':'Named item/content identities, game stack limits, weapon upgrades, capacity and gameplay difficulty relationships; native Steam and in-game verification.',
    're9':'Named/active character variants, complete named unlocks, verified stack limits, item creation, full equipment/weapon relationships and non-lazy difficulty representations; adaptive-rank/reward dependencies and in-game verification.',
    'webfishing':'Missing quest/collection record creation, reward and remaining customization dependencies; in-game verification beyond currency.',
    'ror2':'Remaining exact record/unlock names, units and dependencies; in-game verification. Live-run inventory is outside the persisted profile format.',
    'kh1':'AP/equipment/stock dependencies, full character/growth rules and journal/story/reward relationships; in-game verification.',
    'kh2':'Complete character-specific behavior, growth/reward rules, named puzzles/journal/story systems and in-game verification. Standard AP checks, stock transfers, spells/shortcuts and recognized acquisitions already exist.',
    'recom':'HP/CP, sleights and full decks/card-state dependencies; native confirmation of all acquisition/completion states and in-game verification.',
    'bbs':'HP counter semantics, full command footprints/capacity and acquisition, D-Link/finisher and story dependencies; in-game verification.',
    'ddd':'Dream Eater growth/XP and affinity levels, boards/creation, full command decks and progression/reward dependencies; in-game verification.',
    'kh3':'Full character/AP/equipment rules, remaining sea/form commands, minigame rewards and named progression dependencies; in-game verification.',
    'maxpayne':'Serialized health, Bullet Time, loaded ammunition and supported player-state relationships; in-game verification.',
    'alice':'Remaining persistent/configuration dependencies and in-game verification. Active outfit and checkpoint editing remain excluded by the user.',
}

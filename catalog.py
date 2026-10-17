"""Public compatibility catalogue. Availability is explicit, never inferred."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Platform:
    name: str
    icon: str

PLATFORMS = {'steam': Platform('Steam', 'steam.svg')}

@dataclass(frozen=True)
class Game:
    id: str
    title: str
    subtitle: str
    family: str
    accent: str
    editable: bool
    description: str
    experimental: bool = False
    platforms: tuple[str, ...] = ('steam',)

GAMES = (
    Game('gtav','GRAND THEFT AUTO V','Legacy / Enhanced · PC Story Mode','GRAND THEFT AUTO','#80b78d',True,'Michael, Franklin and Trevor · Cash · Stamina · Shooting · Strength · Stealth · Flying · Driving · Lung capacity · Special ability',True),
    Game('rdr2','RED DEAD REDEMPTION 2','PC Story Mode','RED DEAD REDEMPTION','#c85d5d',True,'Cash and camp funds · Honor · Cores and XP · Existing supplies · Weapon condition · Horses · Compendium · Statistics',True),
    Game('eldenring','ELDEN RING','Original game · Steam','ELDEN RING','#c9b580',True,'Runes · Attributes · Automatic level · Current vitals · Appearance · Map visibility · Talisman capacity · Learn base-game spells · Spell loadouts · Inventory and storage · Add goods · Create weapons and armor · Weapon upgrades · NG+ scaling',True),
    Game('re1_hd','RESIDENT EVIL','HD Remaster · Steam','RESIDENT EVIL','#a3b5a3',True,'Multiple save records · Difficulty · Defensive supplies · Inventory and item box · 131 documented item identities · Item replacement and creation',True),
    Game('re2','RESIDENT EVIL 2','2019 Remake · Steam','RESIDENT EVIL','#98adc7',True,'Difficulty · Player health · Existing inventory quantities · Rewards · Completion and challenge records · Ghost Survivors',True),
    Game('re3','RESIDENT EVIL 3','2020 Remake · Steam','RESIDENT EVIL','#aebac9',True,'Player health · Existing inventory quantities · Shop points and flags · Rewards · Completion, challenge and combat records',True),
    Game('re4_remake','RESIDENT EVIL 4','2023 Remake · Steam','RESIDENT EVIL','#b6a58a',True,'Pesetas · Spinels · Player and partner health · Case capacity · Existing inventory quantities and saved capacities · Extra shop and content flags · Chapter records',True),
    Game('re4_2005','RESIDENT EVIL 4 (2005)','Ultimate HD Edition · Steam','RESIDENT EVIL','#b7a78c',True,'Pesetas · Difficulty · Player and Ashley health · Case quantities · Weapon upgrades · Save and combat statistics',True),
    Game('re5','RESIDENT EVIL 5','Steamworks · Steam','RESIDENT EVIL','#bcac73',True,'Money · Exchange points · Costumes · Infinite ammo flags · Screen filters · Library files · Figures',True),
    Game('re6','RESIDENT EVIL 6','PC profile · Steam','RESIDENT EVIL','#b0babc',True,'Skill points · Equipped skills and extra modes · Mercenaries characters, costumes, stages and results · Serpent emblems · Last selected difficulty · Named reserve ammunition and herbs',True),
    Game('re7','RESIDENT EVIL 7 BIOHAZARD','PC saves · Steam','RESIDENT EVIL','#c2b389',True,'Difficulty · Player health · Existing item box quantities · Restarts · Saved DLC completion flags · Item-use statistics',True),
    Game('re8','RESIDENT EVIL VILLAGE','Resident Evil 8 · Steam','RESIDENT EVIL','#baa885',True,'Lei · Challenge points · Saved player health · Existing stacks · Extra content flags · Completion, combat, Mercenaries and lifetime records',True),
    Game('re9','RESIDENT EVIL REQUIEM','PC saves and profiles · Steam','RESIDENT EVIL','#a7b7bd',True,'Money · Clear points · Player health and upgrades · Existing inventory and item box stacks · Attached weapon upgrades · Owned equipment and weapon shortcuts · Content flags · Challenge and lifetime records',True),
    Game('webfishing','WEBFISHING','Steam · Local save','WEBFISHING','#b6e7aa',True,'Economy · Level and XP · Bait and lures · Upgrades · Cosmetics and appearance · Inventory and item creation · Hotbar · Quests and journal'),
    Game('ror2','RISK OF RAIN 2','Steam · Local profile','RISK OF RAIN','#e7b26f',True,'Characters · Skills · Skins · Artifacts · Items · Logs · Coins · Saved statistics by character, enemy, stage and item'),
    Game('kh1','KINGDOM HEARTS','Final Mix · Steam','KINGDOM HEARTS','#b4b5f6',True,'Munny · Difficulty · Party attributes and XP · Weapons and accessories · Abilities and magic availability · Magic shortcuts · Items and materials',True),
    Game('recom','RE:CHAIN OF MEMORIES','HD 1.5 + 2.5 ReMIX · Steam','KINGDOM HEARTS','#e2bc9d',True,'Moogle Points · Experience · Difficulty · Card quantities and acquisition · Friend flags · Completion flags',True),
    Game('kh2','KINGDOM HEARTS II','Final Mix · Steam','KINGDOM HEARTS','#91c7ea',True,'Munny · Difficulty · Experience · Party attributes · Equipment transfers · AP budgets · Magic and shortcuts · Forms and summons · Reports · Inventory',True),
    Game('bbs','BIRTH BY SLEEP','Final Mix · Steam','KINGDOM HEARTS','#c5a5df',True,'Munny · Medals · Difficulty · Level and XP · Attributes · Keyblades · Existing decks and finishers · Commands and abilities',True),
    Game('ddd','DREAM DROP DISTANCE','HD 2.8 Final Chapter Prologue · Steam','KINGDOM HEARTS','#96d9c7',True,'Munny · Difficulty · Sora and Riku · Drop Points · Keyblades · Dream Eater stats, XP, Link Points and colors · Inventory',True),
    Game('kh3','KINGDOM HEARTS III','Steam · Encrypted PC saves','KINGDOM HEARTS','#a5c9ef',True,'Munny · Difficulty · Level and XP · Party attributes · Companion AI · Critical-mode transitions · Equipment · Abilities · Magic and Links · Shortcuts · Minigame records · Inventory and materials',True),
    Game('maxpayne','MAX PAYNE','Steam · Local saves','MAX PAYNE','#dca7a0',True,'Weapons · Reserve ammunition · Painkillers',True),
    Game('alice','ALICE: MADNESS RETURNS','Steam · Profile and difficulty','ALICE','#8ab6d6',True,'Teeth · Weapons · Abilities · Dresses · Collectibles · Chapters · Difficulty',True),
)
BY_ID = {game.id:game for game in GAMES}

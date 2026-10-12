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
    Game('eldenring','ELDEN RING','Original game · Steam','ELDEN RING','#c9b580',True,'Runes · Attributes · Automatic level · Current vitals · Inventory and storage stacks · Add goods · Weapon upgrades · NG+ scaling',True),
    Game('re1_hd','RESIDENT EVIL','HD Remaster · Steam','RESIDENT EVIL','#a3b5a3',True,'Mapped slot 1 · Difficulty · Defensive supplies · Inventory and item box quantities',True),
    Game('re2','RESIDENT EVIL 2','2019 Remake · Steam','RESIDENT EVIL','#98adc7',True,'Player health · Existing inventory quantities · Reward flags · Library files',True),
    Game('re3','RESIDENT EVIL 3','2020 Remake · Steam','RESIDENT EVIL','#aebac9',True,'Player health · Existing inventory quantities · Shop points and item flags · Rewards',True),
    Game('re4_remake','RESIDENT EVIL 4','2023 Remake · Steam','RESIDENT EVIL','#b6a58a',True,'Extra content points · Spinels · Existing inventory quantities',True),
    Game('re4_2005','RESIDENT EVIL 4 (2005)','Ultimate HD Edition · Steam','RESIDENT EVIL','#b7a78c',True,'Pesetas · Difficulty · Player and Ashley health · Case quantities · Weapon upgrades · Save and combat statistics',True),
    Game('re5','RESIDENT EVIL 5','Steamworks · Steam','RESIDENT EVIL','#bcac73',True,'Money · Exchange points · Costumes · Infinite ammo flags · Screen filters · Library files',True),
    Game('re6','RESIDENT EVIL 6','PC profile · Steam','RESIDENT EVIL','#b0babc',True,'Skill points · Equipped skills · Mercenaries characters, costumes and stages · Existing supply quantities',True),
    Game('re7','RESIDENT EVIL 7 BIOHAZARD','PC saves · Steam','RESIDENT EVIL','#c2b389',True,'Player health · Existing item box quantities',True),
    Game('re9','RESIDENT EVIL REQUIEM','PC saves and profiles · Steam','RESIDENT EVIL','#a7b7bd',True,'Money · Clear points · Extra shop flags · Bonus content · Artwork · Figures',True),
    Game('webfishing','WEBFISHING','Steam · Local save','WEBFISHING','#b6e7aa',True,'Economy · Level and XP · Bait · Upgrades · Inventory · Fishing journal'),
    Game('ror2','RISK OF RAIN 2','Steam · Local profile','RISK OF RAIN','#e7b26f',True,'Characters · Skills · Skins · Artifacts · Items · Logs · Coins and statistics'),
    Game('kh1','KINGDOM HEARTS','Final Mix · Steam','KINGDOM HEARTS','#b4b5f6',True,'Munny · Difficulty · Party attributes and XP · Equipped weapons and accessories · Abilities · Items · Materials',True),
    Game('recom','RE:CHAIN OF MEMORIES','HD 1.5 + 2.5 ReMIX · Steam','KINGDOM HEARTS','#e2bc9d',True,'Moogle Points · Experience · Difficulty · Attack, magic, item, map and enemy cards',True),
    Game('kh2','KINGDOM HEARTS II','Final Mix · Steam','KINGDOM HEARTS','#91c7ea',True,'Munny · Difficulty · Experience · Party attributes · Equipped weapons, armor and accessories · Abilities · Drive Forms · Inventory',True),
    Game('bbs','BIRTH BY SLEEP','Final Mix · Steam','KINGDOM HEARTS','#c5a5df',True,'Munny · Medals · Difficulty · Level and XP · Attributes · Commands · Abilities',True),
    Game('ddd','DREAM DROP DISTANCE','HD 2.8 Final Chapter Prologue · Steam','KINGDOM HEARTS','#96d9c7',True,'Munny · Difficulty · Sora and Riku · Level and XP · Drop Points · Inventory',True),
    Game('kh3','KINGDOM HEARTS III','Steam · Encrypted PC saves','KINGDOM HEARTS','#a5c9ef',True,'Munny · Difficulty · Level and XP · Party attributes · Inventory · Materials',True),
    Game('maxpayne','MAX PAYNE','Steam · Local saves','MAX PAYNE','#dca7a0',True,'Weapons · Reserve ammunition · Painkillers',True),
    Game('alice','ALICE: MADNESS RETURNS','Steam · Profile and difficulty','ALICE','#8ab6d6',True,'Teeth · Weapons · Abilities · Dresses · Collectibles · Chapters · Difficulty',True),
)
BY_ID = {game.id:game for game in GAMES}

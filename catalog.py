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
    Game('re4_2005','RESIDENT EVIL 4 (2005)','Ultimate HD Edition · Steam','RESIDENT EVIL','#b7a78c',True,'Pesetas · Difficulty · Player and Ashley health · Save and combat statistics',True),
    Game('webfishing','WEBFISHING','Steam · Local save','WEBFISHING','#b6e7aa',True,'Economy · Level and XP · Bait · Upgrades · Inventory · Fishing journal'),
    Game('ror2','RISK OF RAIN 2','Steam · Local profile','RISK OF RAIN','#e7b26f',True,'Characters · Skills · Skins · Artifacts · Items · Logs · Coins and statistics'),
    Game('kh1','KINGDOM HEARTS','Final Mix · Steam','KINGDOM HEARTS','#b4b5f6',True,'Munny · Difficulty · Attributes · Items · Materials · Weapons · Accessories'),
    Game('recom','RE:CHAIN OF MEMORIES','HD 1.5 + 2.5 ReMIX · Steam','KINGDOM HEARTS','#e2bc9d',True,'Moogle Points · Experience · Difficulty · Attack, magic, item, map and enemy cards',True),
    Game('kh2','KINGDOM HEARTS II','Final Mix · Steam','KINGDOM HEARTS','#91c7ea',True,'Munny · Difficulty · Experience · Character attributes · Drive Forms · Inventory',True),
    Game('bbs','BIRTH BY SLEEP','Final Mix · Steam','KINGDOM HEARTS','#c5a5df',True,'Munny · Medals · Difficulty · Level and XP · Attributes · Commands · Abilities',True),
    Game('ddd','DREAM DROP DISTANCE','HD 2.8 Final Chapter Prologue · Steam','KINGDOM HEARTS','#96d9c7',True,'Munny · Difficulty · Sora and Riku · Level and XP · Drop Points · Inventory',True),
    Game('kh3','KINGDOM HEARTS III','Steam · Encrypted PC saves','KINGDOM HEARTS','#a5c9ef',True,'Munny · Difficulty · Level and XP · Party attributes · Inventory · Materials',True),
    Game('maxpayne','MAX PAYNE','Steam · Local saves','MAX PAYNE','#dca7a0',True,'Weapons · Reserve ammunition · Painkillers',True),
    Game('alice','ALICE: MADNESS RETURNS','Steam · Profile and difficulty','ALICE','#8ab6d6',True,'Teeth · Weapons · Abilities · Dresses · Collectibles · Chapters · Difficulty',True),
)
BY_ID = {game.id:game for game in GAMES}

"""Public compatibility catalogue. Availability is explicit, never inferred."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Game:
    id: str
    title: str
    subtitle: str
    family: str
    accent: str
    editable: bool
    description: str

GAMES = (
    Game('webfishing','WEBFISHING','Steam · Local save','WEBFISHING','#b6e7aa',True,'Economy · Level and XP · Bait · Upgrades · Inventory · Fishing journal'),
    Game('ror2','RISK OF RAIN 2','Steam · Local profile','RISK OF RAIN','#e7b26f',True,'Characters · Skills · Skins · Artifacts · Items · Logs · Coins and statistics'),
    Game('kh1','KINGDOM HEARTS','Final Mix · Steam','KINGDOM HEARTS','#b4b5f6',True,'Munny · Attributes · Items · Materials · Weapons · Accessories'),
    Game('recom','RE:CHAIN OF MEMORIES','HD 1.5 + 2.5 ReMIX · Steam','KINGDOM HEARTS','#e2bc9d',False,'Editor in development · Decks, cards, and progress pending'),
    Game('kh2','KINGDOM HEARTS II','Final Mix · Steam','KINGDOM HEARTS','#91c7ea',False,'Editor in development · Progress, attributes, and inventory pending'),
    Game('bbs','BIRTH BY SLEEP','Final Mix · Steam','KINGDOM HEARTS','#c5a5df',False,'Editor in development · Characters, commands, and inventory pending'),
    Game('maxpayne','MAX PAYNE','PC · Local saves','MAX PAYNE','#dca7a0',False,'Editor in development · Progress, weapons, and player state pending'),
)
BY_ID = {game.id:game for game in GAMES}

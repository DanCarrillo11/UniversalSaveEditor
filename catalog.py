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
    Game('webfishing','WEBFISHING','Steam · Partida local','WEBFISHING','#b6e7aa',True,'Economía · Nivel y XP · Cebos · Mejoras · Inventario · Diario de pesca'),
    Game('ror2','RISK OF RAIN 2','Steam · Perfil local','RISK OF RAIN','#e7b26f',True,'Personajes · Habilidades · Skins · Artefactos · Objetos · Registros · Monedas y estadísticas'),
    Game('kh1','KINGDOM HEARTS','Final Mix · Steam','KINGDOM HEARTS','#b4b5f6',True,'Platines · Atributos · Objetos · Materiales · Armas · Accesorios'),
    Game('recom','RE:CHAIN OF MEMORIES','HD 1.5 + 2.5 ReMIX · Steam','KINGDOM HEARTS','#e2bc9d',False,'Editor en desarrollo · Mazos, cartas y progreso pendientes'),
    Game('kh2','KINGDOM HEARTS II','Final Mix · Steam','KINGDOM HEARTS','#91c7ea',False,'Editor en desarrollo · Progreso, atributos e inventario pendientes'),
    Game('bbs','BIRTH BY SLEEP','Final Mix · Steam','KINGDOM HEARTS','#c5a5df',False,'Editor en desarrollo · Personajes, comandos e inventario pendientes'),
    Game('maxpayne','MAX PAYNE','PC · Partidas locales','MAX PAYNE','#dca7a0',False,'Editor en desarrollo · Progreso, armas y estado pendientes'),
)
BY_ID = {game.id:game for game in GAMES}

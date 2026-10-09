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
    Game('webfishing','WEBFISHING','Un rato junto al lago','WEBFISHING','#b6e7aa',True,'Economía, nivel, XP, cebos, mejoras, objetos existentes y diario de pesca.'),
    Game('kh1','KINGDOM HEARTS','Final Mix · Steam','KINGDOM HEARTS','#b4b5f6',True,'Platines, atributos de Sora, Donald y Goofy; objetos, materiales, armas y accesorios.'),
    Game('recom','RE:CHAIN OF MEMORIES','HD 1.5 + 2.5 ReMIX · Steam','KINGDOM HEARTS','#e2bc9d',False,'Archivo detectado cuando existe. Lectura y edición pendientes de implementar y validar.'),
    Game('kh2','KINGDOM HEARTS II','Final Mix · Steam','KINGDOM HEARTS','#91c7ea',False,'Se incorporará con un adaptador y pruebas específicos para KH II.'),
    Game('bbs','BIRTH BY SLEEP','Final Mix · Steam','KINGDOM HEARTS','#c5a5df',False,'Pendiente: separar los registros y validar las partidas de cada personaje.'),
    Game('maxpayne','MAX PAYNE','El comienzo de la caída','MAX PAYNE','#dca7a0',False,'Necesitamos partidas de ejemplo para investigar y validar su formato.'),
)
BY_ID = {game.id:game for game in GAMES}

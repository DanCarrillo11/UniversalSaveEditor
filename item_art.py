"""Original-game item artwork and labels; unknown identities have no substitute.

The RE2 atlas coordinates/identity table adapt RE2REmakeSRT under MIT.
Copyright (c) 2019 Travis J. Gutjahr. See assets/items/RE2_SRT_LICENSE.txt.
Artwork belongs to Capcom; no generated assets or automatic downloads.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent/'assets/items'

@dataclass(frozen=True)
class ItemArt:
    name: str
    category: str
    atlas: str
    rect: tuple

@lru_cache(maxsize=1)
def catalogue():
    result={}
    try:
        data=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
        if data.get('schema')!=1:return result
        for game,items in data['games'].items():
            for identifier,entry in items.items():
                atlas=entry['atlas'];rect=entry['rect']
                if not isinstance(atlas,str) or not atlas.endswith('.png'):continue
                path=ROOT/atlas
                if not path.resolve().is_relative_to(ROOT.resolve()):continue
                if len(rect)!=4 or any(type(v)!=int for v in rect):continue
                x,y,w,h=rect
                if min(x,y)<0 or not 1<=w<=512 or not 1<=h<=512 or x+w>4096 or y+h>4096:continue
                if not isinstance(entry['name'],str) or not isinstance(entry['category'],str):continue
                result[game,int(identifier)]=ItemArt(entry['name'],entry['category'],atlas,tuple(rect))
    except (OSError,ValueError,KeyError,TypeError):
        return {}
    return result

def item_art(game,identifier):
    if type(identifier)!=int or identifier<=0:return None
    return catalogue().get((game,identifier))

@lru_cache(maxsize=16)
def _atlas(name):
    # QApplication must already exist. Qt validates decoding and we bound dimensions.
    from PySide6.QtGui import QImageReader,QPixmap
    reader=QImageReader(str(ROOT/name));size=reader.size()
    if not 0<size.width()<=4096 or not 0<size.height()<=4096:return QPixmap()
    return QPixmap.fromImage(reader.read())

@lru_cache(maxsize=256)
def item_pixmap(game,identifier,size=64):
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt,QRect
    art=item_art(game,identifier)
    if art is None:return QPixmap()
    atlas=_atlas(art.atlas);rect=QRect(*art.rect)
    if atlas.isNull() or not atlas.rect().contains(rect):return QPixmap()
    return atlas.copy(rect).scaled(size,size,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)

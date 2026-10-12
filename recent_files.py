"""Local shortcuts only. History clearing never deletes save files.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from pathlib import Path
import json
import os
from catalog import BY_ID

LIMIT=10


def identity(path):
    return os.path.normcase(os.path.abspath(path))


def read_history(encoded):
    if not isinstance(encoded,str) or len(encoded)>65536:return []
    try:items=json.loads(encoded)
    except (ValueError,TypeError):return []
    if not isinstance(items,list):return []
    result=[];seen=set()
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('game'),str) or item['game'] not in BY_ID:continue
        path=item.get('path');slot=item.get('slot',0)
        if not isinstance(path,str) or not path or len(path)>4096 or '\0' in path or not Path(path).is_absolute():continue
        key=identity(path)
        if key in seen:continue
        seen.add(key)
        result.append({'game':item['game'],'path':key,'slot':slot if type(slot) is int and 0<=slot<100 else 0})
        if len(result)==LIMIT:break
    return result


def remember(items,game,path,slot=0):
    key=identity(path)
    current={'game':game,'path':key,'slot':slot}
    return read_history(json.dumps([current]+[item for item in items if identity(item['path'])!=key]))


def forget(items,path):
    key=identity(path)
    return [item for item in items if identity(item['path'])!=key]

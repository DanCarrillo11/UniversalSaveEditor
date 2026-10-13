"""Offline read-only examples generated from synthetic adapter fixtures.

No saves, credentials, raw bytes or writable offsets are packaged here.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from pathlib import Path
import json
from functools import lru_cache
from core import Field,Slot
from catalog import BY_ID

ROOT=Path(__file__).resolve().parent

@lru_cache(maxsize=1)
def preview_catalogue():
    data=json.loads((ROOT/'assets/editor-previews.json').read_text(encoding='utf-8'))
    if data.get('schema')!=1:raise ValueError('Unsupported preview catalogue.')
    return data['games']

class EditorPreview:
    is_preview=True
    def __init__(self,game):
        if game not in BY_ID:raise ValueError('Unknown editor.')
        data=preview_catalogue()
        self.game=game;self.warnings=[];self.account_id=None;self.slots=[]
        self.notes=['Example values only. Actual fields depend on the opened save, character and file type. No editor is classified as full support.']
        for sample in data[game]:
            fields=[]
            for entry in sample['fields']:
                options=dict(entry);options['choices']=tuple(options.get('choices',()))
                options['art_choices']=tuple(options.get('art_choices',()))
                fields.append(Field(**options,offset=-1,readonly=True))
            self.slots.append(Slot(sample['name'],fields))
        if not self.slots:raise ValueError('This editor has no preview examples.')

    def patched(self,*args,**kwargs):
        raise ValueError('Preview only. Open a real save file before applying changes.')

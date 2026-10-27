"""Small shared search vocabulary for visible editor controls.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from functools import lru_cache
import unicodedata

VOCABULARY=(('money','currency','cash','munny','runes','lei','pesetas','teeth','dinero','dientes'),
            ('health','hp','hearts','vida','salud'),
            ('xp','experience','experiencia'),
            ('ammo','ammunition','municion','municiones'),
            ('difficulty','dificultad'))
ALIASES={word:group for group in VOCABULARY for word in group}


@lru_cache(maxsize=8192)
def normalized(text):
    text=unicodedata.normalize('NFKD',text).casefold()
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in text
                           if not unicodedata.combining(c)).split())


def matches_query(text, query, aliases=True):
    if not query.strip():return True
    text=normalized(text)
    words=text.split()
    for term in normalized(query).split():
        candidates=ALIASES.get(term,(term,)) if aliases else (term,)
        if not any(word in words if len(word)<=2 else word in text for word in candidates):
            return False
    return True

"""Shared light and dark interface colors. SPDX-License-Identifier: GPL-3.0-or-later."""
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PALETTES={
    'light': {
        'canvas':'#F5F5F7','surface':'#FFFFFF','sidebar':'#EDEEF2','input':'#F1F2F6',
        'text':'#1C1C1E','secondary':'#5C5C66','muted':'#71717A','line':'#DCDDE3',
        'hover':'#E9ECF2','accent':'#006FE6','accentHover':'#005DC6',
        'selection':'#E5F0FF','selectionText':'#005BBE',
        'disabledSurface':'#E8E9EE','disabledText':'#90929C',
        'warningSurface':'#FFF2DC','warningText':'#805400','warningLine':'#E6C894',
        'infoSurface':'#ECF4FF','infoText':'#375C8A','infoLine':'#D4E5FB',
        'invalidSurface':'#FFF0EE','error':'#B83227','success':'#197047','scroll':'#B2B5BF',
    },
    'dark': {
        'canvas':'#171719','surface':'#242426','sidebar':'#1D1D1F','input':'#303034',
        'text':'#F5F5F7','secondary':'#B6B6BE','muted':'#9999A5','line':'#3A3A3F',
        'hover':'#353538','accent':'#087BEB','accentHover':'#1989F8',
        'selection':'#193856','selectionText':'#93C5FF',
        'disabledSurface':'#28282C','disabledText':'#767682',
        'warningSurface':'#3D3020','warningText':'#F1C57F','warningLine':'#645135',
        'infoSurface':'#253344','infoText':'#ADCBEF','infoLine':'#38516C',
        'invalidSurface':'#422829','error':'#FF9A91','success':'#66D49A','scroll':'#55555D',
    },
}

def stylesheet(theme):
    colors=PALETTES.get(theme,PALETTES['light'])
    source=(ROOT/'theme.qss').read_text(encoding='utf-8')
    colors={**colors,'checkIcon':(ROOT/'assets/ui/check.svg').as_posix()}
    for name,value in colors.items():source=source.replace('@'+name+'@',value)
    return source

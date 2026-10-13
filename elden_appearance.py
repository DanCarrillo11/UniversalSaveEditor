"""Named original FACE sliders; unknown models/shape blocks stay untouched.

GPL-3.0-or-later. Format facts adapted from oisis/EldenRing-SaveForge,
backend/core/offset_defs.go. See SOURCES.md and docs/ELDEN_RING_FORMAT.md.
"""
import struct

def appearance_fields(raw,start,Field):
    if raw[start:start+16]!=struct.pack('<I4s2I',0xffffffff,b'FACE',4,0x120):return []
    specs=[]
    def slider(offset,name,category='Skin and makeup'):specs.append((offset,name,category))
    def color(offset,name,category='Skin and makeup'):
        for i,channel in enumerate(('Red','Green','Blue')):slider(offset+i,name+' · '+channel,category)
    for i,name in enumerate(('Head','Chest','Abdomen','Right arm','Right leg','Left arm','Left leg')):
        slider(0xb0+i,name,'Body proportions')
    color(0xb7,'Skin');slider(0xba,'Skin luster');slider(0xbb,'Pores');slider(0xbc,'Stubble')
    slider(0xbd,'Dark circles');color(0xbe,'Dark circles');slider(0xc1,'Cheek makeup');color(0xc2,'Cheek makeup')
    for offset,name in ((0xc5,'Eyeliner'),(0xc9,'Lower eyeshadow'),(0xcd,'Upper eyeshadow'),(0xd1,'Lipstick')):
        slider(offset,name);color(offset+1,name)
    for offset,name in ((0xd5,'Horizontal position'),(0xd6,'Vertical position'),(0xd7,'Angle'),(0xd8,'Expansion')):
        slider(offset,'Tattoo · '+name,'Tattoo and body hair')
    color(0xd9,'Tattoo','Tattoo and body hair')
    slider(0xde,'Body hair','Tattoo and body hair');color(0xdf,'Body hair','Tattoo and body hair')
    for base,side in ((0xe2,'Right'),(0xee,'Left')):
        color(base,side+' iris','Eyes');slider(base+3,side+' iris size','Eyes')
        slider(base+4,side+' eye clouding','Eyes');color(base+5,side+' eye clouding','Eyes')
        color(base+8,side+' eye white','Eyes');slider(base+11,side+' eye position','Eyes')
    for base,name in ((0xfa,'Hair'),(0x100,'Beard'),(0x106,'Eyebrows')):
        color(base,name,'Hair and facial hair')
        for i,part in enumerate(('Luster','Roots','White hairs'),3):slider(base+i,name+' · '+part,'Hair and facial hair')
    color(0x10c,'Eyelashes','Hair and facial hair');color(0x10f,'Eyepatch','Hair and facial hair')
    return [Field(f'appearance:{offset:x}',name,raw[start+offset],start+offset,'<B',0,255,'Appearance',collection=category,
                  note='Original named appearance slider (0–255). Model IDs, face-shape block, body type, presets and unknown bytes are preserved.')
            for offset,name,category in specs]

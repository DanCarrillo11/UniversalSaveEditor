"""Regenerate UI examples from synthetic fixtures, never from personal saves.

Run from the repository root with the development/test dependencies installed.
The packaged application reads only the resulting JSON, not these fixtures.
"""
from pathlib import Path
import sys,json,struct,ast,inspect,textwrap
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from core import Save,png_chunks
from catalog import GAMES
from test_core import variant,ror2,alice
from test_alice import configuration
from test_expansion import kh_fixture,elden_ready,re4_ready
from test_kh_extra import archive,kh3_plain
from test_maxpayne import inventory_fixture
from test_re_hd import fixture as hd
from test_re5 import fixture as re5
from test_re6 import fixture as re6
from test_re_engine import stream,wrap,ACCOUNT
from test_village import fixture as village

def fishing():
    payload=variant({'inventory':[{'id':'fish_lake_salmon','quality':1,'size':1.0}],
        'money':100,'loan_left':0,'bait_inv':{n:0 for n in ('worms','cricket','leech','minnow','squid','nautilus','gildedworm')},
        'bait_unlocked':['','worms'],'max_bait':10,'level':1,'xp':0.0,'fish_caught':0,'cash_total':0.0,
        'rod_power':0,'rod_speed':0,'rod_chance':0,'rod_luck':0,'buddy_level':0,'buddy_speed':0,
        'journal':{'lake':{'fish_lake_salmon':{'count':1,'record':1.0}}}})
    return struct.pack('<I',len(payload))+payload

def profile():
    tree=ast.parse(textwrap.dedent(inspect.getsource(Save._ror2)))
    specs=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stat_specs' for t in n.targets))
    return ('<UserProfile><coins>0</coins><stats>'+''.join(f'<stat name="{key}">0</stat>' for key in specs)+'</stats></UserProfile>').encode()

def populated_kh(game):
    raw,record,*_=kh_fixture(game);raw=bytearray(raw)
    from kh_party import KH1_CHARACTERS,KH2_CHARACTERS
    for c,name in enumerate(KH1_CHARACTERS if game=='kh1' else KH2_CHARACTERS):
        base=record+(4+c*0x74 if game=='kh1' else 0x24f0+c*0x114)
        raw[base if game=='kh1' else base+15]=20
    if game=='kh2':
        struct.pack_into('<H',raw,record+0x24f0,41)
        struct.pack_into('<I',raw,record+8,Save._kh2_checksum(raw[record:record+0x10fc0]))
    # Update only the synthetic fixture's PNG checksum.
    import zlib
    start,end=next((s,e) for n,s,e in png_chunks(raw,allow_sqex_crc=True) if n==b'sqEX')
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw)

def kh_extra(game):
    raw=bytearray(archive(game,1));save=Save(raw,game);record,length=save.extra_kh.records[0]
    if game=='bbs':
        from kh_extra_tables import BBS_COMMANDS
        from kh_pc import bbs_checksum
        identifier=next(i for i,n in BBS_COMMANDS.items() if n=='Balloon Letter')
        struct.pack_into('<3H',raw,record+0x3498,identifier,1,0)
        struct.pack_into('<I',raw,record+12,bbs_checksum(raw[record:record+length]))
    elif game=='ddd':
        from kh_extra_tables import DDD_ITEMS
        identifier=next(i for i,(n,g) in DDD_ITEMS.items() if n=='Potion')
        struct.pack_into('<H',raw,record+0xc004,identifier);raw[record+0xc009]=1
    import zlib
    start,end=next((s,e) for n,s,e in png_chunks(raw,allow_sqex_crc=True) if n==b'sqEX')
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw)

def generate():
    result={}
    factories={'webfishing':fishing,'ror2':profile,'alice':alice,'kh1':lambda:populated_kh('kh1'),
        'kh2':lambda:populated_kh('kh2'),'recom':lambda:archive('recom',1),'bbs':lambda:kh_extra('bbs'),
        'ddd':lambda:kh_extra('ddd'),'kh3':kh3_plain,'eldenring':lambda:elden_ready(True),
        'maxpayne':inventory_fixture,'re1_hd':hd,'re4_2005':re4_ready,'re5':re5,'re6':re6,'re8':village}
    for game in GAMES:
        samples=[('Example save',factories[game.id]())] if game.id in factories else [('Gameplay and profile fields · example',wrap(stream(game.id),game.id))]
        if game.id=='alice':samples.append(('Game configuration · example',configuration()))
        result[game.id]=[]
        for name,raw in samples:
            save=Save(raw,game.id,account_id=ACCOUNT if game.id in ('re4_remake','re9') else None)
            entries=[]
            for field in save.slots[0].fields:
                item=asdict(field);item.pop('offset');item.pop('readonly')
                item['value']=max(field.minimum,min(field.maximum,field.value))
                entries.append(item)
            result[game.id].append({'name':name,'fields':entries})
    return {'schema':1,'source':'Synthetic adapter fixtures; illustrative examples, not personal save data','games':result}

if __name__=='__main__':
    data=generate();(ROOT/'assets/editor-previews.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print({g:sum(len(s['fields']) for s in samples) for g,samples in data['games'].items()})

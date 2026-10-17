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
from test_requiem import fixture as requiem
from test_rockstar import fixture as rockstar

def fishing():
    payload=variant({'inventory':[{'id':'fish_lake_salmon','quality':1,'size':1.0,'ref':42,'tags':[]}],
        'money':100,'loan_left':0,'bait_inv':{n:0 for n in ('worms','cricket','leech','minnow','squid','nautilus','gildedworm')},
        'bait_unlocked':['','worms'],'bait_selected':'worms','max_bait':10,'level':1,'xp':0.0,'fish_caught':0,'cash_total':0.0,
        'rod_power':0,'rod_speed':0,'rod_chance':0,'rod_luck':0,'buddy_level':0,'buddy_speed':0,
        'cosmetics_unlocked':[],'cosmetics_equipped':{'species':'species_cat','hat':'','accessory':[]},
        'lure_unlocked':[],'lure_selected':'','hotbar':{'1':42,'2':0},'locked_refs':[],
        'quests':{'example':{'title':'Fishing quest','progress':0,'goal_amt':10}},
        'journal':{'lake':{'fish_lake_salmon':{'count':1,'record':1.0,'quality':[0]}}}})
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
        for c,weapon in enumerate((41,75,49)):
            base=record+0x24f0+c*0x114
            struct.pack_into('<H',raw,base,weapon)
            struct.pack_into('<H',raw,base+20,67)
            struct.pack_into('<3H',raw,base+84,0x52,0,0)
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
        from kh_feature_tables import BBS_COMMAND_KINDS
        from kh_pc import bbs_checksum
        for n,kind in enumerate(('Attack','Movement','Shotlock','Finisher')):
            identifier=next(i for i,(title,k) in BBS_COMMAND_KINDS.items() if k==kind)
            struct.pack_into('<5H',raw,record+0x3498+n*10,identifier,1,0,0,1)
            if kind=='Finisher':struct.pack_into('<HHI',raw,record+0x5644,identifier,1,0)
        struct.pack_into('<H',raw,record+0x59fa,1)
        for deck in range(3):
            for n in range(19):struct.pack_into('<3H',raw,record+0x5a2c+deck*0xc4+n*6,0xffff,0xffff,255)
            for n,reference in ((0,0),(8,1),(18,2)):struct.pack_into('<H',raw,record+0x5a2c+deck*0xc4+n*6,reference)
        struct.pack_into('<I',raw,record+12,bbs_checksum(raw[record:record+length]))
    elif game=='ddd':
        from kh_extra_tables import DDD_ITEMS
        identifier=next(i for i,(n,g) in DDD_ITEMS.items() if n=='Potion')
        struct.pack_into('<H',raw,record+0xc004,identifier);raw[record+0xc009]=1
        struct.pack_into('<2H',raw,record+0xd2e8,512,528)
        raw[record+0x53a0]=1;raw[record+0x53a0+61:record+0x53a0+64]=bytes((10,10,10))
        spirit=record+0x53a0;raw[spirit+3]=10;raw[spirit+32:spirit+35]=bytes((128,37,12))
        struct.pack_into('<i',raw,spirit+36,1000);struct.pack_into('<h',raw,spirit+44,20)
        struct.pack_into('<h',raw,spirit+48,100);raw[spirit+92]=1
    elif game=='recom':
        from kh_pc import recom_checksum
        struct.pack_into('<i',raw,record+0x2d54,1)
        struct.pack_into('<I',raw,record+4,recom_checksum(raw[record+16:record+length]))
    import zlib
    start,end=next((s,e) for n,s,e in png_chunks(raw,allow_sqex_crc=True) if n==b'sqEX')
    struct.pack_into('>I',raw,end,zlib.crc32(raw[start-4:end]))
    return bytes(raw)

def elden_example():
    from test_functional_settings import elden_appearance
    from test_elden_spells import ready
    from test_elden_equipment_creation import ready as physical
    from test_elden_loadouts import fixture as equipment
    from test_elden_tools import fixture as tools
    return tools(source=equipment(source=physical(source=ready(source=elden_appearance()[0])[0])))

def kh3_example():
    import zlib
    raw=bytearray(kh3_plain());base=0x1880
    raw[base+0x80]=1;raw[base+0x81]=3;raw[base+0x84]=1
    struct.pack_into('<I',raw,12,zlib.crc32(raw[16:0x94f4e8]))
    return bytes(raw)

def re4_remake_example():
    from test_village import Writer
    from test_remake_context import fixture as remake
    from re_engine_container import ReEngineEnvelope
    writer=Writer();writer.data=bytearray(16)
    writer.data.extend(ReEngineEnvelope(remake(),'re4_remake',account_id=ACCOUNT).payload)
    writer.root(0x84db4327,[('saveAccessoryDatas',-1,[(0x3862c64c,[('_ID',7,('<i',1000)),('_IsUnlock',2,('<B',0))])]),
        ('saveCostumeDatas',-1,[(0xa4ad52ff,[('_ID',7,('<i',100)),('_IsUnlock',2,('<B',0))])])])
    writer.root(0x4d4f1555,[('SaveRecordExShopList',-1,[(0xb567676c,[('ElementData',17,(0x48d2099d,[('_BonusID',7,('<i',1)),
        ('_IsUnlock',2,('<B',0)),('_IsBuy',2,('<B',0))]))])]),
        ('SaveRecordList',-1,[(0x237579b8,[('_RecordID',7,('<i',1)),('_IsUnlock',2,('<B',0)),('_Count',7,('<i',0))])])])
    return wrap(bytes(writer.data[16:]),'re4_remake')

def generate():
    from test_remake_inventory_capacity import fixture as remake_capacity
    from test_rdr2_features import fixture as rdr2_example
    result={}
    factories={'gtav':rockstar,'rdr2':lambda:rdr2_example(records=True),
        'webfishing':fishing,'ror2':profile,'alice':alice,'kh1':lambda:populated_kh('kh1'),
        'kh2':lambda:populated_kh('kh2'),'recom':lambda:kh_extra('recom'),'bbs':lambda:kh_extra('bbs'),
        'ddd':lambda:kh_extra('ddd'),'kh3':kh3_example,'eldenring':elden_example,
        'maxpayne':inventory_fixture,'re1_hd':hd,'re4_2005':re4_ready,'re4_remake':re4_remake_example,
        're5':re5,'re6':re6,'re8':village,'re9':lambda:requiem(parts=True,equipment=True),
        're2':lambda:remake_capacity('re2'),'re3':lambda:remake_capacity('re3')}
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

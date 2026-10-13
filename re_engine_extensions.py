"""Additional saved settings, records and unlocks with exact type identities.

GPL-3.0-or-later. Property identities were checked against the pinned
kvasszn/ree-save-editor format metadata; no SDK assets are distributed.
These operations edit existing records only, never scene objects or arrays.
"""
from collections import defaultdict
import struct
from re_hashes import murmur32

# The ranges below are editor input bounds, not claims about reward thresholds.
EXTRA_SPECS = {
    're2': (
        (0x41f30892,'GetItemCount','Items obtained','Lifetime records','<i',999999999),
        (0x4e4210f9,'The4thClearPlayTime','The 4th Survivor clear-time record','Completion records','<Q',2**63-1),
        (0xa31dc018,'CurrentDifficulty','Difficulty','Difficulty','<i',2),
        (0x2412050a,'CounterAttackNumber','Counterattacks','Combat records','<i',999999999),
        (0x4e4210f9,'IsClearedGame','Scenario completed','Completion records','<B',1),
        (0x4e4210f9,'IsClearedRecord','Challenge completed','Challenge records','<B',1),
        (0x4e4210f9,'RecordProgressNumber','Challenge progress','Challenge records','<i',999999999),
        (0xb6f9870b,'IsClearedRogueGame_Normal','Ghost Survivors scenario completed','Ghost Survivors','<B',1),
        (0xb6f9870b,'IsClearedRogueGame_Training','Training scenario completed','Ghost Survivors','<B',1),
        (0xb6f9870b,'IsClearedRogueRecord','Ghost Survivors challenge completed','Ghost Survivors','<B',1),
        (0xb6f9870b,'RecordProgressNumber','Challenge progress','Ghost Survivors','<i',999999999),
        (0xb6f9870b,'DefeatEnemyCount_Normal','Enemies defeated','Ghost Survivors','<I',999999999),
        (0xb6f9870b,'DefeatEnemyCount_Training','Training enemies defeated','Ghost Survivors','<I',999999999),
        (0xb6f9870b,'UseHandGunBulletCount_Normal','Handgun bullets used','Ghost Survivors','<I',999999999),
        (0xb6f9870b,'UseHandGunBulletCount_Training','Training handgun bullets used','Ghost Survivors','<I',999999999),
        (0xb6f9870b,'RoguePlayCount','Ghost Survivors runs','Ghost Survivors','<i',999999999),
        (0xb6f9870b,'RogueRaccoonFigureCount','Mr. Raccoon figures','Ghost Survivors','<i',999999999),
    ),
    're3': (
        (0x5f30b0dd,'GetItemCount','Items obtained','Lifetime records','<i',999999999),
        (0xbacebc1e,'DeadCount','Deaths','Combat records','<i',999999999),
        (0x7bcf2d1f,'NemesisDownCount','Nemesis knockdowns','Combat records','<i',999999999),
        (0x7bcf2d1f,'EmergencyAvoidanceCount','Perfect dodges','Combat records','<i',999999999),
        (0x7bcf2d1f,'VomitingCount','Vomiting events','Combat records','<i',999999999),
        (0x9e45778c,'CounterAttackNumber','Counterattacks','Combat records','<i',999999999),
        (0x4ff2c755,'IsClearedGame','Scenario completed','Completion records','<B',1),
        (0x4ff2c755,'IsClearedRecord','Challenge completed','Challenge records','<B',1),
        (0x4ff2c755,'RecordProgressNumber','Challenge progress','Challenge records','<i',999999999),
    ),
    're4_remake': (
        (0x5f2dc096,'_KillCount','Chapter kills','Chapter records','<i',999999999),
        (0x5f2dc096,'_DamageCount','Chapter damage events','Chapter records','<i',999999999),
        (0x5f2dc096,'_SaveCount','Chapter saves','Chapter records','<i',999999999),
        (0x5f2dc096,'_HookShotCount','Chapter hook shots','Chapter records','<i',999999999),
        (0x7334449f,'_GameClearTime','Campaign clear-time record','Completion records','<Q',2**63-1),
        (0x3862c64c,'_IsUnlock','Accessory unlocked','Accessories','<B',1),
        (0xa4ad52ff,'_IsUnlock','Costume unlocked','Costumes','<B',1),
        (0x48d2099d,'_IsUnlock','Bonus available','Extra content','<B',1),
        (0x48d2099d,'_IsBuy','Bonus purchased','Extra content','<B',1),
        (0x237579b8,'_IsUnlock','Challenge unlocked','Challenge records','<B',1),
        (0x237579b8,'_Count','Challenge progress','Challenge records','<i',999999999),
    ),
    're7': (
        (0x1db1bef4,'_successJustGuardCount','Successful timed guards','Combat records','<I',999999999),
        (0x1db1bef4,'_openedItemBoxCount','Item boxes opened','Lifetime records','<I',999999999),
        (0x1db1bef4,'_antiqueCoinCount','Antique coins collected statistic','Lifetime records','<I',999999999),
        (0x1db1bef4,'_useStabilizersCount','Stabilizers used statistic','Lifetime records','<I',999999999),
        (0x1db1bef4,'_useSteroidsCount','Steroids used statistic','Lifetime records','<I',999999999),
        (0x1db1bef4,'_useHealingCount','Healing items used','Lifetime records','<I',999999999),
        (0x76e7226f,'ClearFlagArray','DLC completion entry','DLC modes','<B',1),
        (0x76e7226f,'ClearFlagArrayHard','DLC hard-mode completion entry','DLC modes','<B',1),
        (0x90e78581,'_clearCount','DLC game completions','Completion records','<I',999999999),
        (0xf627f2fd,'GameDifficulty','Difficulty','Difficulty','<i',2),
        (0xf627f2fd,'RestartCount','Restarts','Combat records','<i',999999999),
        (0xae97aa2f,'IsSurvivalUnlocked','Survival unlocked','DLC modes','<B',1),
        (0xae97aa2f,'IsSurvivalPlusUnlocked','Survival+ unlocked','DLC modes','<B',1),
        (0x4bd87bec,'IsNormalModeCleared','Normal mode completed','DLC modes','<B',1),
        (0xa78a4649,'IsBadEndCleared','Bad ending completed','DLC modes','<B',1),
        (0xa78a4649,'IsTrueEndCleared','True ending completed','DLC modes','<B',1),
    ),
    're8': (
        (0x2c6618d5,'ClearedStageCount','Mercenaries stages cleared','Mercenaries records','<i',999999999),
        (0x2c6618d5,'KillEnemyCount','Mercenaries kills','Mercenaries records','<i',999999999),
        (0x2c6618d5,'GetAbilityCount','Mercenaries abilities obtained','Mercenaries records','<i',999999999),
        (0x79d310f9,'ActionCount','Mercenaries action count','Mercenaries records','<i',999999999),
        (0x40082379,'CountOfDead','DLC player deaths','Combat records','<i',999999999),
        (0x40082379,'CountOfGameClears','DLC player completions','Completion records','<i',999999999),
        (0x09df4207,'CountOfGameClears','DLC completions','Completion records','<i',999999999),
        (0x5055ec19,'IsCleared','Unique challenge completed','Challenge records','<B',1),
        (0x00346547,'SaveHealthPl2000','Additional player health','Player health','<f',10000),
        (0x1c003475,'CountOfGameClears','Game completions','Completion records','<i',999999999),
        (0x1c003475,'TotalGotMoney','Total Lei earned','Lifetime records','<i',2147483647),
        (0xb1a52427,'CountOfDead','Deaths','Combat records','<i',999999999),
        (0xb1a52427,'UsedMoney','Lei spent','Lifetime records','<i',2147483647),
        (0xb1a52427,'CountOfGameClears','Player game completions','Completion records','<i',999999999),
        (0xb1a52427,'CountOfCompound','Crafted items','Lifetime records','<i',999999999),
    ),
    're9': (
        (0x9d8901e7,'ReceivedClearPoint','Challenge points received','Challenge reward records','<B',1),
        (0x5ec19702,'ClearCount','Game completions','Completion records','<i',999999999),
        (0x6ba744fd,'TotalClearCount','Total game completions','Completion records','<i',999999999),
        (0x6ba744fd,'NewGameCount','New games started','Lifetime records','<i',999999999),
        (0x5ae81fa1,'_GameOverCount','Game overs','Combat records','<i',999999999),
        (0x88bd59c3,'_CraftCount','Crafted items','Lifetime records','<i',999999999),
        (0xa4603085,'_AttackCount','Attacks','Combat records','<i',999999999),
        (0xa4603085,'_DefeatCount','Enemies defeated','Combat records','<i',999999999),
        (0xf36d4d87,'_SaveInkCount','Ink ribbons used','Lifetime records','<i',999999999),
        (0xf36d4d87,'_BloodCollectCount','Blood collections','Lifetime records','<i',999999999),
        (0xa89f5fcb,'ProgressCount','Challenge progress','Challenge records','<I',999999999),
    ),
}
DIFFICULTIES={'re2':('Assisted','Standard','Hardcore'),'re7':('Easy','Normal','Madhouse')}
# A recognizable child in a world object is not a profile unlock. Require its
# exact profile parent and one correctly typed sibling ID for RE4 records.
CONTEXTS={
    0x3862c64c: (0x84db4327,'_ID','Accessory'),
    0xa4ad52ff: (0x84db4327,'_ID','Costume'),
    0x48d2099d: (0x4d4f1555,'_BonusID','Bonus'),
    0x237579b8: (0x4d4f1555,'_RecordID','Challenge'),
}

class EngineExtensions:
    def __init__(self,nodes,data,game):
        self.data=data;self.game=game;self.ids=defaultdict(list)
        for n in nodes:
            config=CONTEXTS.get(n.owner)
            if config and n.field==murmur32(config[1].encode()) and n.kind==7 and n.fmt=='<i' and n.size==4:
                self.ids[n.owner,n.path[:-1]].append(n)

    def allowed(self,node):
        config=CONTEXTS.get(node.owner)
        if self.game!='re4_remake' or not config:return True
        candidates=self.ids.get((node.owner,node.path[:-1]),())
        return len(candidates)==1 and any(o==config[0] for o,_,_ in node.path)

    def describe(self,node,label,group):
        config=CONTEXTS.get(node.owner)
        note='Changes the existing saved record only. Reward delivery, online achievements, scenario flags and related counters are not synthesized.'
        if self.game=='re4_remake' and config:
            n=self.ids[node.owner,node.path[:-1]][0]
            identity=struct.unpack_from('<i',self.data,n.offset)[0]
            label=f'{config[2]} ID {identity} · {label}'
            note='Existing profile entry only. Does not grant DLC ownership or install content. Related scenario state and other unlock flags are preserved.'
        if group=='Difficulty':
            note='Changes the saved gameplay difficulty. Adaptive rank, completion records and platform achievements are preserved.'
        elif 'time record' in label:
            note+=' Saved timer units are not mapped; this is not displayed as seconds.'
        elif group=='Chapter records':
            note+=' The chapter identity and its stored difficulty are preserved.'
        elif group=='Challenge reward records':
            note='Saved claimed-reward state only. Does not add or subtract points, change challenge progress or grant platform achievements.'
        return label,note

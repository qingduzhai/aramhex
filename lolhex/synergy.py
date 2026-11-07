# -*- coding: utf-8 -*-
"""
海克斯符文与装备流派协同推导引擎 (AramHex Synergy Engine 4.0)
汇聚海克斯大乱斗 4.0 (Patch 16.20/16.21) 官方全量统计与前沿短视频绝活攻略：
1. 海克斯 ➡️ 流派归属与核心装备联动路线 (Item Synergy Hints)
2. 4.0 绝活联动：小蜜蜂狗熊/卡莎、装甲冲击纯肉亚索/石头人、双珠光大腕女警/卢锡安、低音轰鸣人马、蓝色屏障卡萨丁、泰坦念经剑圣、超凡邪恶抽血赵信
3. 双轨决策分类器 (Lift主判据 + 置信度 + 核心/稳妥/陷阱/刷新)
4. 双修英雄动态流派转轨 (Playstyle Pivots)
"""

from __future__ import annotations
import json
from typing import Any

# ==========================================
# 1. 英雄 ➡️ 默认流派映射表 (173 位英雄)
# ==========================================
HERO_ARCHETYPE_MAP = {
    # 坦克前排 / 护甲魔抗
    '54': 'Tank_Frontline', '14': 'Tank_Frontline', '33': 'Tank_Frontline', '31': 'Tank_Frontline',
    '32': 'Tank_Frontline', '78': 'Tank_Frontline', '12': 'Tank_Frontline', '111': 'Tank_Frontline',
    '89': 'Tank_Frontline', '57': 'Tank_Frontline', '223': 'Tank_Frontline', '497': 'Tank_Frontline',
    '876': 'Tank_Frontline', '154': 'Tank_Frontline', '106': 'Tank_Frontline', '201': 'Tank_Frontline',
    '44': 'Tank_Frontline', '516': 'Tank_Frontline', '3': 'Tank_Frontline', '27': 'Tank_Frontline',
    '72': 'Tank_Frontline', '20': 'Tank_Frontline', '36': 'Tank_Frontline', '53': 'Tank_Frontline',
    '98': 'Tank_Frontline', '113': 'Tank_Frontline', '412': 'Tank_Frontline', '526': 'Tank_Frontline',
    '897': 'Tank_Frontline',

    # AD 远距离 Poke / 技能穿甲流
    '81': 'AD_Spellcaster_Poke', '42': 'AD_Spellcaster_Poke', '126': 'AD_Spellcaster_Poke',
    '901': 'AD_Spellcaster_Poke', '41': 'AD_Spellcaster_Poke',

    # 混合攻击特效 / 攻速流
    '145': 'ADC_Hybrid_OnHit', '96': 'ADC_Hybrid_OnHit', '110': 'ADC_Hybrid_OnHit',
    '67': 'ADC_Hybrid_OnHit', '429': 'ADC_Hybrid_OnHit', '10': 'ADC_Hybrid_OnHit',
    '4': 'ADC_Hybrid_OnHit', '200': 'ADC_Hybrid_OnHit',

    # 经典暴击 ADC
    '22': 'ADC_Crit', '51': 'ADC_Crit', '222': 'ADC_Crit', '18': 'ADC_Crit',
    '236': 'ADC_Crit', '202': 'ADC_Crit', '119': 'ADC_Crit', '15': 'ADC_Crit',
    '29': 'ADC_Crit', '498': 'ADC_Crit', '523': 'ADC_Crit', '360': 'ADC_Crit',
    '221': 'ADC_Crit', '895': 'ADC_Crit', '166': 'ADC_Crit', '133': 'ADC_Crit',
    '104': 'ADC_Crit', '203': 'ADC_Crit', '23': 'ADC_Crit', '235': 'ADC_Crit',
    '804': 'ADC_Crit',

    # AP 爆发秒人 / 远距离法系
    '17': 'AP_Burst_Poke', '21': 'AP_Burst_Poke', '99': 'AP_Burst_Poke', '115': 'AP_Burst_Poke',
    '101': 'AP_Burst_Poke', '161': 'AP_Burst_Poke', '63': 'AP_Burst_Poke', '45': 'AP_Burst_Poke',
    '25': 'AP_Burst_Poke', '134': 'AP_Burst_Poke', '61': 'AP_Burst_Poke', '112': 'AP_Burst_Poke',
    '103': 'AP_Burst_Poke', '34': 'AP_Burst_Poke', '136': 'AP_Burst_Poke', '268': 'AP_Burst_Poke',
    '69': 'AP_Burst_Poke', '74': 'AP_Burst_Poke', '30': 'AP_Burst_Poke', '127': 'AP_Burst_Poke',
    '90': 'AP_Burst_Poke', '518': 'AP_Burst_Poke', '13': 'AP_Burst_Poke', '147': 'AP_Burst_Poke',
    '37': 'AP_Burst_Poke', '16': 'AP_Burst_Poke', '50': 'AP_Burst_Poke', '163': 'AP_Burst_Poke',
    '711': 'AP_Burst_Poke', '8': 'AP_Burst_Poke', '142': 'AP_Burst_Poke', '910': 'AP_Burst_Poke',
    '1': 'AP_Burst_Poke', '43': 'AP_Burst_Poke', '117': 'AP_Burst_Poke', '902': 'AP_Burst_Poke',
    '267': 'AP_Burst_Poke', '350': 'AP_Burst_Poke', '40': 'AP_Burst_Poke', '26': 'AP_Burst_Poke',
    '427': 'AP_Burst_Poke', '432': 'AP_Burst_Poke', '9': 'AP_Burst_Poke', '893': 'AP_Burst_Poke',
    '28': 'AP_Burst_Poke', '38': 'AP_Burst_Poke', '60': 'AP_Burst_Poke', '76': 'AP_Burst_Poke',
    '79': 'AP_Burst_Poke', '84': 'AP_Burst_Poke', '85': 'AP_Burst_Poke', '105': 'AP_Burst_Poke',
    '131': 'AP_Burst_Poke', '800': 'AP_Burst_Poke', '805': 'AP_Burst_Poke',

    # AP 持续灼烧 / 技能急速流
    '68': 'AP_Burn_Haste', '143': 'AP_Burn_Haste', '517': 'AP_Burn_Haste', '888': 'AP_Burn_Haste',

    # 战士重装 / 吸血持续作战
    '266': 'Bruiser_Drain', '122': 'Bruiser_Drain', '86': 'Bruiser_Drain', '875': 'Bruiser_Drain',
    '157': 'Bruiser_Drain', '777': 'Bruiser_Drain', '24': 'Bruiser_Drain', '39': 'Bruiser_Drain',
    '92': 'Bruiser_Drain', '58': 'Bruiser_Drain', '75': 'Bruiser_Drain', '82': 'Bruiser_Drain',
    '164': 'Bruiser_Drain', '114': 'Bruiser_Drain', '887': 'Bruiser_Drain', '420': 'Bruiser_Drain',
    '240': 'Bruiser_Drain', '2': 'Bruiser_Drain', '80': 'Bruiser_Drain', '48': 'Bruiser_Drain',
    '77': 'Bruiser_Drain', '6': 'Bruiser_Drain', '19': 'Bruiser_Drain', '62': 'Bruiser_Drain',
    '5': 'Bruiser_Drain', '83': 'Bruiser_Drain', '233': 'Bruiser_Drain', '799': 'Bruiser_Drain',
    '254': 'Bruiser_Drain', '102': 'Bruiser_Drain', '120': 'Bruiser_Drain', '11': 'Bruiser_Drain',
    '59': 'Bruiser_Drain', '64': 'Bruiser_Drain', '141': 'Bruiser_Drain', '150': 'Bruiser_Drain',
    '234': 'Bruiser_Drain', '421': 'Bruiser_Drain', '904': 'Bruiser_Drain',

    # 物理刺客爆发
    '238': 'Assassin_Lethality', '91': 'Assassin_Lethality', '55': 'Assassin_Lethality',
    '121': 'Assassin_Lethality', '107': 'Assassin_Lethality', '245': 'Assassin_Lethality',
    '35': 'Assassin_Lethality', '246': 'Assassin_Lethality', '7': 'Assassin_Lethality',
    '56': 'Assassin_Lethality', '555': 'Assassin_Lethality', '950': 'Assassin_Lethality'
}

# ==========================================
# 2. 4.0 标准流派公式与核心装备母版 (芝士小知识公式出装)
# ==========================================
ARCHETYPE_BUILD_TEMPLATES = {
    'ADC_Crit': {
        'name': '4.0暴击破甲流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3033', 'name': '凡性的提醒'},
            {'id': '6676', 'name': '收集者'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3046', 'name': '幻影之舞'}
        ]
    },
    'ADC_Hybrid_OnHit': {
        'name': '4.0攻击特效攻速流',
        'items': [
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3302', 'name': '界弓'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3085', 'name': '卢安娜的飓风'}
        ]
    },
    'AD_Spellcaster_Poke': {
        'name': '4.0穿甲技能Poke流',
        'items': [
            {'id': '3142', 'name': '幽梦之灵'},
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'},
            {'id': '6692', 'name': '星蚀'},
            {'id': '3004', 'name': '魔宗'}
        ]
    },
    'AP_Burst_Poke': {
        'name': '4.0极速法爆秒杀流',
        'items': [
            {'id': '4645', 'name': '影焰'},
            {'id': '4646', 'name': '风暴狂涌'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '3135', 'name': '虚空之杖'},
            {'id': '3157', 'name': '中娅沙漏'}
        ]
    },
    'AP_Burn_Haste': {
        'name': '4.0面具灼烧折磨流',
        'items': [
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3135', 'name': '虚空之杖'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'}
        ]
    },
    'Bruiser_Drain': {
        'name': '4.0重装战士突进流',
        'items': [
            {'id': '6697', 'name': '狂妄'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'},
            {'id': '3053', 'name': '斯特拉克的挑战护手'}
        ]
    },
    'Tank_Frontline': {
        'name': '4.0心之钢巨像坦克流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '2502', 'name': '无终恨意'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '3075', 'name': '荆棘之甲'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    'Assassin_Lethality': {
        'name': '4.0极致穿甲爆发流',
        'items': [
            {'id': '6697', 'name': '狂妄'},
            {'id': '3142', 'name': '幽梦之灵'},
            {'id': '6696', 'name': '公理圆弧'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'},
            {'id': '6676', 'name': '收集者'}
        ]
    }
}

# ==========================================
# 3. 4.0 质变海克斯专属锚点出装 (Pivot Anchors)
# ==========================================
AUGMENT_PIVOT_ANCHORS: dict[str, dict[str, Any]] = {
    # 3086: 小蜜蜂！！！ (Gold) - 4次40%攻击特效触发
    '3086': {
        'build_name': '小蜜蜂连锁特效流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 3049: 装甲冲击 (Gold) - 技能后普攻2.5倍额外护甲范围物伤，无CD
    '3049': {
        'build_name': '纯肉装甲冲击流',
        'items': [
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '3075', 'name': '荆棘之甲'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    },
    # 3018: 大腕 (Prismatic) - 攻速转爆伤，配合暴击大招直接秒杀
    '3018': {
        'build_name': '大腕攻速转爆伤流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '6676', 'name': '收集者'},
            {'id': '3036', 'name': '多米尼克领主的问候'}
        ]
    },
    # 1048: 珠光护手 (Prismatic) - 技能暴击，乘算放大
    '1048': {
        'build_name': '法术暴击秒杀流',
        'items': [
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'},
            {'id': '4646', 'name': '风暴狂涌'}
        ]
    },
    # 3123: 珠光手镯 (Gold) - 单技能暴击乘算
    '3123': {
        'build_name': '珠光单技暴击流',
        'items': [
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3135', 'name': '虚空之杖'}
        ]
    },
    # 1092: 易损 (Gold) - 全技能暴击乘算
    '1092': {
        'build_name': '易损全技能暴击流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '6676', 'name': '收集者'},
            {'id': '3036', 'name': '多米尼克领主的问候'}
        ]
    },
    # 3078: 鼓声暴起 低音轰鸣 (Gold) - 施法极大加移速攻速，人马被动移速转攻击力
    '3078': {
        'build_name': '低音轰鸣移速疾风流',
        'items': [
            {'id': '6697', 'name': '狂妄'},
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6333', 'name': '死亡之舞'}
        ]
    },
    # 3051: 蓝色屏障 (Silver) - 耗蓝450%转护盾，无CD，卡萨丁/琴女超强
    '3051': {
        'build_name': '蓝色巨盾永动机',
        'items': [
            {'id': '3003', 'name': '炽天使之拥'},
            {'id': '3027', 'name': '时光之杖'},
            {'id': '3004', 'name': '魔宗'}
        ]
    },
    # 1001: 泰坦的坚决 (Prismatic) - 挨打叠双抗法强，剑圣念经回血无敌
    '1001': {
        'build_name': '泰坦挨打双抗流',
        'items': [
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 1390: 超凡邪恶 (Gold) - 命中永久叠法强，赵信第三刀抽血泵
    '1390': {
        'build_name': '超凡邪恶抽血泵',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 1225: 双刀流 (Prismatic) - 极速双发普攻
    '1225': {
        'build_name': '极速双刀狂暴流',
        'items': [
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3302', 'name': '界弓'}
        ]
    },
    # 3118: 奥术公理 (Gold) - 3秒击杀返还冷却，储存达120%解锁无限大招
    '3118': {
        'build_name': '无限大招储存流',
        'items': [
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '3161', 'name': '朔极之矛'}
        ]
    },
    # 3116: 将他们放倒倒倒 (Gold)
    '3116': {
        'build_name': '放倒暴击强控流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '6676', 'name': '收集者'},
            {'id': '6333', 'name': '死亡之舞'}
        ]
    },
    # 1134: 亮出你的剑 (Prismatic)
    '1134': {
        'build_name': '近战重装吸血流',
        'items': [
            {'id': '3078', 'name': '三相之力'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 1058: 秘术冲拳 (Prismatic)
    '1058': {
        'build_name': '普攻减CD特效流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 1019: 全凭身法 (Prismatic)
    '1019': {
        'build_name': '移速攻速连携流',
        'items': [
            {'id': '3046', 'name': '幻影之舞'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 1151: 面包和奶酪 (Gold)
    '1151': {
        'build_name': '技能急速无限连',
        'items': [
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6675', 'name': '纳沃利烁刃'},
            {'id': '6655', 'name': '卢登的伙伴'}
        ]
    },
    # 1332: 恶魔契约 (Prismatic)
    '1332': {
        'build_name': '恶魔高法强斩杀流',
        'items': [
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'},
            {'id': '4646', 'name': '风暴狂涌'}
        ]
    },
    # 1310: 虚空幼体 (Gold)
    '1310': {
        'build_name': '面具灼烧召唤流',
        'items': [
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'}
        ]
    },
    # 1018: 巨像的勇气 (Prismatic)
    '1018': {
        'build_name': '万血巨像前排流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '3075', 'name': '荆棘之甲'}
        ]
    },
    # 1041: 歌利亚巨人 (Prismatic)
    '1041': {
        'build_name': '万血体型巨人流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 1115 / 1071 / 1170: 万用瞄准镜系列
    '1115': {
        'build_name': '超远程安全点杀流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '6676', 'name': '收集者'}
        ]
    },
    '1071': {
        'build_name': '超远程安全点杀流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '6676', 'name': '收集者'}
        ]
    },
    '1170': {
        'build_name': '超远程安全点杀流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '6676', 'name': '收集者'}
        ]
    },
    # 1088: 终极刷新 (Prismatic)
    '1088': {
        'build_name': '大招无限连环秒杀流',
        'items': [
            {'id': '6696', 'name': '公理圆弧'},
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6697', 'name': '狂妄'}
        ]
    },
    # 1054: 物法皆修 (Prismatic)
    '1054': {
        'build_name': '双修混伤破甲流',
        'items': [
            {'id': '3302', 'name': '界弓'},
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3078', 'name': '三相之力'}
        ]
    },
    # 1149: 不动如山 (Silver)
    '1149': {
        'build_name': '金刚不坏双抗流',
        'items': [
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3075', 'name': '荆棘之甲'},
            {'id': '3065', 'name': '振奋盔甲'}
        ]
    },
    # 1152: 钢化你心 (Gold)
    '1152': {
        'build_name': '双倍心之钢巨像流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '3068', 'name': '日炎圣盾'}
        ]
    },
    # 1015: 死亡之环 (Prismatic)
    '1015': {
        'build_name': '死亡之环反哺核弹流',
        'items': [
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 1029: 虚幻武器 (Gold)
    '1029': {
        'build_name': '虚幻普攻特效引爆流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3100', 'name': '巫妖之祸'},
            {'id': '3115', 'name': '纳什之牙'}
        ]
    },
    # 1113: 老练狙神 (Gold)
    '1113': {
        'build_name': '老练狙神超距穿透流',
        'items': [
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 2087: 大法师 (Prismatic)
    '2087': {
        'build_name': '大法师无限互刷连招流',
        'items': [
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '4637', 'name': '峡谷制造者'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 3081: 命运之武器 (Gold)
    '3081': {
        'build_name': '命运武器属性狂飙流',
        'items': [
            {'id': '6695', 'name': '巨蛇之牙'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3100', 'name': '巫妖之祸'}
        ]
    },
    # 2140: 升级：贪欲九头蛇 (Gold)
    '2140': {
        'build_name': '升级顺劈巨额吸血流',
        'items': [
            {'id': '3074', 'name': '贪欲九头蛇'},
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 1324: 蛋白粉奶昔 (Prismatic)
    '1324': {
        'build_name': '双抗护盾回血狂暴流',
        'items': [
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '3302', 'name': '界弓'}
        ]
    },
    # 2016: 注魔 (Silver)
    '2016': {
        'build_name': '注魔蓝量普攻暴击流',
        'items': [
            {'id': '3004', 'name': '魔宗'},
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3115', 'name': '纳什之牙'}
        ]
    },
    # 1004: 回归基本功 (Prismatic)
    '1004': {
        'build_name': '基本功被动爆发流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '3100', 'name': '巫妖之祸'}
        ]
    },
    # 1081: 踢踏舞 (Prismatic)
    '1081': {
        'build_name': '踢踏舞万速暴击流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3031', 'name': '无尽之刃'}
        ]
    },
    # 1129: 神射法师 (Gold)
    '1129': {
        'build_name': '神射法师暴击邪修流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3100', 'name': '巫妖之祸'}
        ]
    },
    # 1204: 叠角龙 (Silver)
    '1204': {
        'build_name': '叠角龙超级叠钢流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '3748', 'name': '巨型九头蛇'}
        ]
    },
    # 2129: 地形专家 (Gold)
    '2129': {
        'build_name': '地形专家无限控制流',
        'items': [
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 2010: 双发快射 (Prismatic)
    '2010': {
        'build_name': '双发快射极速特效流',
        'items': [
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3302', 'name': '界弓'}
        ]
    },
    # 2123: 超负荷 (Prismatic)
    '2123': {
        'build_name': '超负荷法术机关枪流',
        'items': [
            {'id': '3003', 'name': '炽天使之拥'},
            {'id': '3027', 'name': '时光之杖'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 2102: 高压锅 (Gold)
    '2102': {
        'build_name': '高压锅重装反伤流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3068', 'name': '日炎圣盾'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    }
}

# ==========================================
# 4. 4.0 绝活英雄双修/特化转轨规则 (Hero Playstyle Pivots)
# ==========================================
DUAL_PLAYSTYLE_PROFILES: dict[str, dict[str, Any]] = {
    # 沃利贝尔 (Volibear 106) -> 小蜜蜂电刀连锁闪电流 (抖音实战绝活)
    '106': {
        'candidate_augments': {'3086', '1058', '1225', '1029'},
        'build_name': '小蜜蜂连锁雷暴流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 卡莎 (Kai'Sa 145) -> 小蜜蜂 W 双电浆瞬间引爆 / 虚幻武器
    '145': {
        'candidate_augments': {'3086', '1048', '3123', '1029'},
        'build_name': '小蜜蜂双电浆核弹流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 图奇 (Twitch 29) -> 小蜜蜂毒雾爆杀 / 双刀流
    '29': {
        'candidate_augments': {'3086', '1225', '1310'},
        'build_name': '小蜜蜂剧毒爆杀流',
        'items': [
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 凯特琳 (Caitlyn 51) -> 双珠光 + 大腕 颗秒女警 / 最万用瞄准镜
    '51': {
        'candidate_augments': {'3018', '1048', '3123', '1092', '1115'},
        'build_name': '大腕珠光颗秒流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '6676', 'name': '收集者'},
            {'id': '3036', 'name': '多米尼克领主的问候'}
        ]
    },
    # 卢锡安 (Lucian 236) -> 大腕 + 珠光 + 易损 10万大招
    '236': {
        'candidate_augments': {'3018', '1048', '3123', '1092'},
        'build_name': '大腕易损十万大招流',
        'items': [
            {'id': '3085', 'name': '卢安娜的飓风'},
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3036', 'name': '多米尼克领主的问候'}
        ]
    },
    # 赫卡里姆 (Hecarim 120) -> 低音轰鸣 74% 胜率亲爹流 / 罪恶快感 / 扳机炼狱 / 保持坚定
    '120': {
        'candidate_augments': {'3078', '3049', '1151', '3004', '2005', '2076'},
        'build_name': '低音轰鸣74胜率流',
        'items': [
            {'id': '6697', 'name': '狂妄'},
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6333', 'name': '死亡之舞'}
        ]
    },
    # 卡萨丁 (Kassadin 38) -> 蓝色屏障 800 点巨盾永动机
    '38': {
        'candidate_augments': {'3051', '1048', '3123'},
        'build_name': '蓝色巨盾永动机',
        'items': [
            {'id': '3027', 'name': '时光之杖'},
            {'id': '3004', 'name': '魔宗'},
            {'id': '3003', 'name': '炽天使之拥'}
        ]
    },
    # 娑娜 (Sona 37) -> 蓝色屏障高频刷新护盾
    '37': {
        'candidate_augments': {'3051', '1151', '1310'},
        'build_name': '蓝色琴音巨盾流',
        'items': [
            {'id': '3003', 'name': '大天使之杖'},
            {'id': '4628', 'name': '星界驱驰'},
            {'id': '3110', 'name': '冰霜之心'}
        ]
    },
    # 易 (Master Yi 11) -> 泰坦的坚决 肉身成圣念经流
    '11': {
        'candidate_augments': {'1001', '1225', '1058'},
        'build_name': '肉身成圣念经流',
        'items': [
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 赵信 (Zhao Xin 5) -> 超凡邪恶 抽血泵流派 / 虚幻武器AP血魔流 (瞬间回2000血)
    '5': {
        'candidate_augments': {'1390', '1058', '1225', '1029'},
        'build_name': '法强抽血泵流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 亚索 (Yasuo 157) / 永恩 (Yone 777) -> 装甲冲击纯肉一Q千血
    '157': {
        'candidate_augments': {'3049', '1225', '1058'},
        'build_name': '纯肉装甲冲击流',
        'items': [
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '3075', 'name': '荆棘之甲'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    },
    '777': {
        'candidate_augments': {'3049', '1225', '1058'},
        'build_name': '纯肉装甲冲击流',
        'items': [
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '3075', 'name': '荆棘之甲'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    },
    # 墨菲特 (Malphite 54) -> 装甲冲击纯肉 / AP秒杀 / 终极刷新
    '54': {
        'candidate_augments': {'3049', '1048', '3123', '1332', '1088'},
        'build_name': '纯肉装甲冲击流',
        'items': [
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3075', 'name': '荆棘之甲'}
        ]
    },
    # 希瓦娜 (Shyvana 102) -> 强化Q装甲冲击 / 魔龙吐息AP
    '102': {
        'candidate_augments': {'3049', '1048', '1310'},
        'build_name': '装甲冲击魔龙流',
        'items': [
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    },
    # 菲奥娜 (Fiora 114) / 卡蜜尔 (Camille 164) -> 装甲冲击邪修6锁子甲
    '114': {
        'candidate_augments': {'3049', '1134', '1058'},
        'build_name': '邪修装甲冲击流',
        'items': [
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    },
    '164': {
        'candidate_augments': {'3049', '1134', '1058'},
        'build_name': '装甲冲击真伤流',
        'items': [
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3110', 'name': '冰霜之心'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    },
    # 韦鲁斯 (Varus 110) -> AP 枯萎引爆流
    '110': {
        'candidate_augments': {'1048', '3123', '1151', '1332', '1310', '3170'},
        'build_name': 'AP枯萎引爆流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 金克丝 (Jinx 222) / 厄运小姐 (Miss Fortune 21) -> 双刀流极速狂暴
    '222': {
        'candidate_augments': {'1225', '1019', '1001'},
        'build_name': '极速双刀狂暴流',
        'items': [
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3302', 'name': '界弓'}
        ]
    },
    '21': {
        'candidate_augments': {'1225', '1048', '3123'},
        'build_name': '双刀特效弹幕流',
        'items': [
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3302', 'name': '界弓'}
        ]
    },
    # 提莫 (Teemo 17) -> 虚幻武器电刀一击流 / 大法师无限蘑菇 (乐子绝活)
    '17': {
        'candidate_augments': {'1048', '1001', '1019', '1058', '3086', '1029', '2087', '2018'},
        'build_name': '虚幻电刀一击流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3100', 'name': '巫妖之祸'},
            {'id': '3115', 'name': '纳什之牙'}
        ]
    },
    # 茂凯 (Maokai 57) -> 树苗消耗 AP 流
    '57': {
        'candidate_augments': {'1310', '1151', '1332', '3118'},
        'build_name': '树苗面具折磨流',
        'items': [
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'}
        ]
    },
    # 特朗德尔 (Trundle 48) -> 乐子爽飞边子：无限E柱子折磨流 / 地形专家
    '48': {
        'candidate_augments': {'1151', '1058', '1149', '3118', '2129'},
        'build_name': '无限冰柱折磨流',
        'items': [
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'},
            {'id': '3068', 'name': '日炎圣盾'}
        ]
    },
    # 赛恩 (Sion 14) -> 乐子爽飞边子：万血自爆核弹流 / 连拨击锤多重射击
    '14': {
        'candidate_augments': {'1018', '1041', '1152', '1149', '2055', '2010'},
        'build_name': '万血自爆核弹流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3083', 'name': '狂徒铠甲'},
            {'id': '3075', 'name': '荆棘之甲'}
        ]
    },
    # 塞拉斯 (Sylas 517) -> 乐子爽飞边子：邪修暴击神射流 / 雪球突进血魔流
    '517': {
        'candidate_augments': {'1058', '1048', '1134', '1151', '1129'},
        'build_name': '神射暴击邪修流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3100', 'name': '巫妖之祸'}
        ]
    },
    # 深渊巨口 (Kog'Maw 96) -> 乐子爽飞边子：小蜜蜂双刀特效机关枪
    '96': {
        'candidate_augments': {'3086', '1225', '1048', '3123'},
        'build_name': '蜜蜂双刀机关枪',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 兽灵行者 乌迪尔 (Udyr 77) -> 萧天帝秒杀火凤流 (乐子绝活)
    '77': {
        'candidate_augments': {'1004', '1054', '1048', '3123', '1029'},
        'build_name': '萧天帝秒杀火凤流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '3100', 'name': '巫妖之祸'}
        ]
    },
    # 披甲龙龟 拉莫斯 (Rammus 33) -> 蛋白粉5.0攻速龙龟 (乐子绝活)
    '33': {
        'candidate_augments': {'1324', '1379', '3049', '1225'},
        'build_name': '蛋白粉5.0攻速龙龟',
        'items': [
            {'id': '3302', 'name': '界弓'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 酒桶 古拉加斯 (Gragas 79) -> 连锁反应一R核弹秒人流 (乐子绝活)
    '79': {
        'candidate_augments': {'2078', '1048', '3123', '1088', '1029'},
        'build_name': '连锁核弹秒人流',
        'items': [
            {'id': '6656', 'name': '风暴狂涌'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 机械先驱 维克托 (Viktor 112) -> 老练狙神无限射线流 (乐子绝活)
    '112': {
        'candidate_augments': {'1113', '1048', '3123', '3118'},
        'build_name': '老练狙神无限射线流',
        'items': [
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 傲之追猎者 雷恩加尔 (Rengar 107) -> 大法师无限双W回血流 (乐子绝活)
    '107': {
        'candidate_augments': {'2087', '1058', '1151', '1048'},
        'build_name': '大法师无限回血流',
        'items': [
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '4637', 'name': '峡谷制造者'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 蛮族之王 泰达米尔 (Tryndamere 23) -> 无限真男人暴击流 (乐子绝活)
    '23': {
        'candidate_augments': {'3118', '1058', '1088', '1225'},
        'build_name': '无限真男人暴击流',
        'items': [
            {'id': '6675', 'name': '纳沃利烁刃'},
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3031', 'name': '无尽之刃'}
        ]
    },
    # 恶魔小丑 萨科 (Shaco 35) -> 小丑学院无限分身流 (乐子绝活)
    '35': {
        'candidate_augments': {'1310', '1088', '1048', '3118'},
        'build_name': '小丑学院无限分身流',
        'items': [
            {'id': '3118', 'name': '残疫'},
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 潮汐海灵 菲兹 (Fizz 105) -> 炽燃穿梭秒杀流 / 炼狱导管电刀流 (乐子绝活)
    '105': {
        'candidate_augments': {'3116', '1048', '3123', '1058', '1045', '1029'},
        'build_name': '炽燃穿梭秒杀流',
        'items': [
            {'id': '3100', 'name': '巫妖之祸'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 正义天使 凯尔 (Kayle 10) -> 冲拳无限无敌流 / 千码瞄准镜 (乐子绝活)
    '10': {
        'candidate_augments': {'1058', '1088', '1048', '1004', '1115'},
        'build_name': '冲拳无限无敌流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 沙漠死神 内瑟斯 (Nasus 75) -> 五重顺劈焚烬流 / 邦！超速叠Q (乐子绝活)
    '75': {
        'candidate_augments': {'2140', '3049', '1152', '1001', '2111'},
        'build_name': '五重顺劈焚烬流',
        'items': [
            {'id': '3074', 'name': '贪欲九头蛇'},
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 雪原双子 努努和威朗普 (Nunu 20) -> 死亡之环吞噬核弹流 (乐子绝活)
    '20': {
        'candidate_augments': {'1015', '1048', '1152', '3118'},
        'build_name': '死亡之环吞噬核弹流',
        'items': [
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '3083', 'name': '狂徒铠甲'}
        ]
    },
    # 虚空女皇 卑尔维斯 (BelVeth 200) -> 极限千击万仞流 / 将他们放倒 (乐子绝活)
    '200': {
        'candidate_augments': {'3116', '1225', '1058', '1001'},
        'build_name': '极限千击万仞流',
        'items': [
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'}
        ]
    },
    # 卡牌大师 崔斯特 (Twisted Fate 4) -> 命运之武器超距点杀流 (乐子绝活)
    '4': {
        'candidate_augments': {'3081', '1029', '1048', '3118'},
        'build_name': '命运之武器超距点杀流',
        'items': [
            {'id': '6695', 'name': '巨蛇之牙'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3100', 'name': '巫妖之祸'}
        ]
    },
    # 麦林炮手 崔丝塔娜 (Tristana 18) -> 暴击飞弹界弓流 / 注魔AP核弹流 (乐子绝活)
    '18': {
        'candidate_augments': {'2016', '3018', '1048', '1225', '1133', '1092'},
        'build_name': '暴击飞弹界弓/注魔AP核弹流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3302', 'name': '界弓'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'}
        ]
    },
    # 蒸汽机器人 布里茨 (Blitzcrank 53) -> 大法师无限R雷暴流 (乐子绝活)
    '53': {
        'candidate_augments': {'2087', '1048', '1030', '3118'},
        'build_name': '大法师无限R雷暴流',
        'items': [
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 戏命师 烬 (Jhin 202) -> 踢踏舞万速瘸天帝 (乐子绝活)
    '202': {
        'candidate_augments': {'1081', '1019', '1115', '3018'},
        'build_name': '踢踏舞万速瘸天帝',
        'items': [
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '6676', 'name': '收集者'}
        ]
    },
    # 海洋之灾 普朗克 (Gangplank 41) -> 大法师无限大核弹流 (乐子绝活)
    '41': {
        'candidate_augments': {'2087', '1048', '3118', '3018'},
        'build_name': '大法师无限大核弹流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '6676', 'name': '收集者'},
            {'id': '3078', 'name': '三相之力'}
        ]
    },
    # 未来守护者 杰斯 (Jayce 126) -> 千码瞄准大腕重炮流 (乐子绝活)
    '126': {
        'candidate_augments': {'1115', '1071', '3018', '1092'},
        'build_name': '千码瞄准大腕重炮流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '6676', 'name': '收集者'}
        ]
    },
    # 寒冰射手 艾希 (Ashe 22) -> 大法师泉水指挥官流 / 针插垫 (乐子绝活)
    '22': {
        'candidate_augments': {'2087', '2135', '2018', '1088'},
        'build_name': '大法师泉水指挥官流',
        'items': [
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '4645', 'name': '影焰'},
            {'id': '4628', 'name': '视界专注'}
        ]
    },
    # 河流之王 塔姆 (Tahm Kench 223) -> 虚幻武器三重被动流 (乐子绝活)
    '223': {
        'candidate_augments': {'1029', '1152', '3049', '1018'},
        'build_name': '虚幻武器三重被动流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '3068', 'name': '日炎圣盾'},
            {'id': '6662', 'name': '冰脉护手'}
        ]
    },
    # 符文法师 瑞兹 (Ryze 13) -> 超负荷法术加特林流 (乐子绝活)
    '13': {
        'candidate_augments': {'2123', '1030', '3051', '1048'},
        'build_name': '超负荷法术加特林流',
        'items': [
            {'id': '3003', 'name': '炽天使之拥'},
            {'id': '3027', 'name': '时光之杖'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 复仇焰魂 布兰德 (Brand 63) -> 过路兵全向破绽折磨流 (乐子绝活)
    '63': {
        'candidate_augments': {'2098', '1045', '1048', '1310'},
        'build_name': '过路兵全向破绽折磨流',
        'items': [
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 山隐之焰 奥恩 (Ornn 516) -> 精怪魔法重装爆轰流 (乐子绝活)
    '516': {
        'candidate_augments': {'1194', '1149', '1018', '1152'},
        'build_name': '精怪魔法重装爆轰流',
        'items': [
            {'id': '8020', 'name': '深渊面具'},
            {'id': '3068', 'name': '日炎圣盾'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 涤魂圣枪 赛娜 (Senna 235) -> 虚幻电刀隔空叠魂流 (乐子绝活)
    '235': {
        'candidate_augments': {'1029', '1081', '1115', '1092'},
        'build_name': '虚幻电刀隔空叠魂流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3031', 'name': '无尽之刃'}
        ]
    },
    # 铁铠冥魂 莫德凯撒 (Mordekaiser 82) -> 导管圣火领域折磨流 (乐子绝活)
    '82': {
        'candidate_augments': {'1045', '2088', '1149', '1018'},
        'build_name': '导管圣火领域折磨流',
        'items': [
            {'id': '3116', 'name': '瑞莱的冰晶节杖'},
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '4637', 'name': '峡谷制造者'}
        ]
    },
    # 德玛西亚皇子 嘉文四世 (Jarvan IV 59) -> 地形专家自爆AP皇子 (乐子绝活)
    '59': {
        'candidate_augments': {'2129', '1048', '1029', '1088'},
        'build_name': '地形专家自爆AP皇子',
        'items': [
            {'id': '6656', 'name': '风暴狂涌'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 暗夜猎手 薇恩 (Vayne 67) -> 双发快射破败十六环流 (乐子绝活)
    '67': {
        'candidate_augments': {'2010', '2055', '1225', '1058'},
        'build_name': '双发快射破败十六环流',
        'items': [
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3302', 'name': '界弓'}
        ]
    },
    # 德玛西亚之力 盖伦 (Garen 86) -> 快步双突进挺进旋转流 (乐子绝活)
    '86': {
        'candidate_augments': {'2064', '3049', '1019', '1134'},
        'build_name': '快步双突进挺进旋转流',
        'items': [
            {'id': '3078', 'name': '三相之力'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    }
}


def get_synergy_item_hint(store: Any, hero_id: str | None, augment_id: str | None) -> dict[str, Any] | None:
    """
    根据英雄与所选海克斯，推导最契合的 Top 3 核心装备路线：
    1. 优先查英雄特化转轨 (Dual Playstyle Override)；
    2. 其次查质变海克斯专属锚点 (Pivot Anchor)；
    3. 最后结合英雄主定位流派 (Archetype Fallback)；
    4. 自动补全装备的本地图标元数据与胜率信息。
    """
    if not hero_id or not augment_id:
        return None

    hid_str = str(hero_id)
    aid_str = str(augment_id)

    # 1. 优先尝试原版 dataset 的显式 hero_augment_items.json
    if hasattr(store, "augment_items"):
        try:
            hint = store.augment_items(hero_id, augment_id)
            if hint and hint.get("items"):
                hint_copy = dict(hint)
                hint_copy["title"] = "核心协同出装 · 统计优选"
                hint_copy["footer"] = "选该符文后的推荐装备配合"
                return hint_copy
        except Exception:
            pass

    items_dict = getattr(store, "items", {}) or {}

    def format_item(item_info: dict[str, Any]) -> dict[str, Any]:
        iid = str(item_info["id"])
        meta = items_dict.get(iid, {})
        name = item_info.get("name") or meta.get("name") or iid
        icon = meta.get("icon")
        return {
            "item": iid,
            "name": name[:24],
            "icon": icon,
            "games": item_info.get("games"),
            "win": item_info.get("win")
        }

    # 2. 检查英雄专属特化转轨 (如狗熊小蜜蜂、女警双珠光大腕、人马低音轰鸣、卡萨丁蓝色屏障、剑圣泰坦念经)
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        if aid_str in dual["candidate_augments"]:
            rows = [format_item(x) for x in dual["items"][:3]]
            return {
                "source": "stats",
                "title": f"绝活协同路线 · {dual['build_name']}",
                "footer": "4.0攻略首选：符文触发绝活质变，建议搭配此套路线",
                "items": rows
            }

    # 3. 检查质变海克斯全局专属锚点
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        anchor = AUGMENT_PIVOT_ANCHORS[aid_str]
        rows = [format_item(x) for x in anchor["items"][:3]]
        return {
            "source": "stats",
            "title": f"核心协同路线 · {anchor['build_name']}",
            "footer": "质变符文联动：选该符文后的推荐核心出装",
            "items": rows
        }

    # 4. 英雄默认主流派母版
    archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES['Bruiser_Drain'])
    rows = [format_item(x) for x in template["items"][:3]]
    return {
        "source": "stats",
        "title": f"核心协同路线 · {template['name']}",
        "footer": "标准流派公式：选该符文后的推荐出装",
        "items": rows
    }


# 4.0 核心海克斯解读词条
AUGMENT_META_EXPLANATIONS: dict[str, str] = {
    '3086': "小蜜蜂：施放技能附加4次攻击特效！狗熊/老鼠/卡莎/大嘴触发质变秒杀",
    '3049': "装甲冲击：技能后普攻造成2.5倍额外护甲范围物伤无CD！堆护甲肉装成核弹",
    '3018': "大腕：获得的3/4攻速转暴击伤害！女警R/卢锡安R暴击伤害翻数倍",
    '1048': "珠光护手：全技能可暴击并放大伤害，与无尽/大腕乘算输出拉满",
    '3123': "珠光手镯：单技能暴击质变，法系爆发极品搭配",
    '1092': "易损：技能全暴击并与珠光护手乘算叠加，伤害成倍翻升",
    '3078': "低音轰鸣：放技能极大加移速攻速，人马被动移速转攻击力，胜率高达74%",
    '3051': "蓝色屏障：消耗蓝量450%转护盾无内置CD！卡萨丁一个大跳800+巨盾",
    '1001': "泰坦的坚决：挨打叠层给高额双抗法强，剑圣W冥想70%减伤念经回血无敌",
    '1390': "超凡邪恶：技能命中永久叠加法强，赵信被动70%AP回血化身极速抽血泵",
    '1225': "双刀流：射程减半但攻速翻倍极速双发，金克丝/女枪/剑圣质变",
    '3118': "奥术公理：3秒击杀储存大招冷却，储存达120%全英雄解锁无限大招",
    '3116': "将他们放倒：暴击附加高额控制伤害，爆发收割利器",
    '1058': "秘术冲拳：普攻缩减基础技能冷却，技能无限循环",
    '1134': "亮出你的剑：近战普攻与吸血大幅强化，战士对拼极品",
    '1015': "死亡之环：治疗转化为对周围敌人的高额伤害！努努/剑圣/塞拉斯化身移动自爆核弹",
    '1029': "虚幻武器：技能命中附加攻击特效！提莫/卡牌/酒桶/乌迪尔秒人流神级被动",
    '1113': "老练狙神：技能随飞行距离大幅增伤并缩短冷却！维克托无限超距高伤射线",
    '2087': "大法师：释放技能返还另一技能30%原始冷却！雷恩加尔双W无限回血不屈战神",
    '3081': "命运之武器：参与击杀永久为首件装备提供高额属性！第一件出巨蛇之牙性价比破表",
    '2140': "升级：贪欲九头蛇：普攻触发多次九头蛇顺劈，狗头Q顺劈5次清屏吸血",
    '1324': "蛋白粉奶昔：双抗按百分比增加治疗与护盾！龙龟/琴女化身传奇不死战神",
    '2016': "注魔：攻击特效附加最大法力值百分比魔法伤害且可暴击！崔丝塔娜AP核弹",
    '1004': "回归基本功：基础技能被封印但大幅提高被动与终极技能伤害！乌迪尔萧天帝秒杀",
    '2078': "连锁反应：技能击杀或伤害引发连锁爆炸，酒桶一R全屏核弹清场"
}


def classify_augment_tier(store: Any, hero_id: str | None, augment_id: str | None,
                          win_rate: float | None, score: float | None, games: int | None) -> dict[str, str]:
    """
    双轨制决策分类器：
    返回徽章标签（badge）、图标（icon）与简明建议（label）。

    徽章只由实测数据（Lift + 样本量）决定；静态绝活表（AUGMENT_META_EXPLANATIONS /
    AUGMENT_PIVOT_ANCHORS）只提供机制解读文案。没有数据支撑的「核心」徽章会和按数据
    算出的 verdict（如「建议刷新」）在浮窗上自相矛盾，所以这里不再给静态表直通核心。
    """
    aid_str = str(augment_id or "")
    expl = AUGMENT_META_EXPLANATIONS.get(aid_str)
    g = games or 0

    # 1. 大样本高 Lift（Delta ≥ +2.5pp 且样本充足）：核心徽章必须有实测数据支撑
    if score is not None and score >= 2.5 and g >= 400:
        if expl:
            summary = f"4.0质变核心：{expl}"
        else:
            summary = f"流派核心符文，相对该英雄基准提升 {score:+.1f}pp"
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": summary
        }

    # 2. 泛用万金油 (稳妥)
    if (win_rate is not None and win_rate >= 0.518) and (score is None or score >= -0.2):
        return {
            "badge": "🛡️ 稳妥",
            "tag": "evergreen",
            "summary": "泛用万金油符文，容错率高、发挥稳定"
        }

    # 3. 陷阱提示 (负 Lift 且胜率低)
    if score is not None and score <= -1.8 and g >= 300:
        return {
            "badge": "⚠️ 陷阱",
            "tag": "trap",
            "summary": f"版本陷阱！相比该英雄基准降低 {abs(score):.1f}pp，建议刷新"
        }

    # 4. 低于基准期望，建议刷新
    if score is not None and score < -0.5:
        return {
            "badge": "🎲 慎选",
            "tag": "reroll",
            "summary": "低于基准期望，可优先考虑掷骰刷新"
        }

    # 5. 兜底：有机制解读的照常展示（含没有数据的新符文），但徽章不越级抬成核心
    return {
        "badge": "✨ 可选",
        "tag": "normal",
        "summary": expl or "契合常规对局，正常可选"
    }


# ==========================================
# 5. 局内双符文/多符文联动协同矩阵 (Combo Synergy Matrix)
#    每条只维护「有什么交互」：名称、机制描述、必出装备。
#    「加多少分」由 fit.computed_combo_bonus 按 交互类型(COMBO_TYPES) × 机制耦合度 推导，
#    各条里的 bonus 字段是旧版攻略视频拍的手工值，仅留档，不再参与计算。
# ==========================================
AUGMENT_COMBOS: list[dict[str, Any]] = [
    # 1. 珠光护手 + 易损 (天命双法爆)
    {
        "pair": {"1048", "1092"},
        "bonus": 7.5,
        "name": "天命双法爆",
        "desc": "全技能暴击与暴击伤害乘算叠加，伤害成倍翻升极速秒杀前排！",
        "core_items": [
            {"id": "3031", "name": "无尽之刃", "reason": "法爆核心：爆伤加成与技能暴击乘算质变"},
            {"id": "4645", "name": "影焰", "reason": "法爆核心：暴击法穿与残血必爆"},
            {"id": "3089", "name": "灭世者的死亡之帽", "reason": "法爆核心：法强基数最大化"}
        ]
    },
    # 2. 珠光手镯 + 易损
    {
        "pair": {"3123", "1092"},
        "bonus": 5.5,
        "name": "手镯暴击联动",
        "desc": "核心单技暴击叠加易损全技能暴击加成，单点技能直接斩杀！",
        "core_items": [
            {"id": "3031", "name": "无尽之刃", "reason": "暴击伤害乘算质变"},
            {"id": "4645", "name": "影焰", "reason": "暴击法穿与残血暴击"}
        ]
    },
    # 3. 珠光护手 + 珠光手镯
    {
        "pair": {"1048", "3123"},
        "bonus": 5.0,
        "name": "双重法术暴击",
        "desc": "全技能暴击叠加核心技能超额爆伤，法系输出突破天花板！",
        "core_items": [
            {"id": "3089", "name": "灭世者的死亡之帽", "reason": "拉高法强基础乘算"},
            {"id": "4645", "name": "影焰", "reason": "法爆法穿核心"},
            {"id": "3031", "name": "无尽之刃", "reason": "爆伤放大"}
        ]
    },
    # 4. 珠光护手 + 大腕
    {
        "pair": {"1048", "3018"},
        "bonus": 7.0,
        "name": "大腕法爆核弹",
        "desc": "攻速转高额爆伤与技能暴击完美联动，伤害乘算质变！",
        "core_items": [
            {"id": "3031", "name": "无尽之刃", "reason": "爆伤天花板"},
            {"id": "6676", "name": "收集者", "reason": "暴击斩杀"},
            {"id": "3036", "name": "多米尼克领主的问候", "reason": "破甲穿透"}
        ]
    },
    # 5. 小蜜蜂 + 双刀流 (极速特效融化)
    {
        "pair": {"3086", "1225"},
        "bonus": 8.0,
        "name": "蜜蜂极速双刀",
        "desc": "双刀流翻倍普攻频次瞬间触发小蜜蜂4次40%攻击特效，融化一切！",
        "core_items": [
            {"id": "3087", "name": "斯塔缇克电刃", "reason": "特效高频闪电弹射"},
            {"id": "3115", "name": "纳什之牙", "reason": "高额AP附加魔法伤害"},
            {"id": "3153", "name": "破败王者之刃", "reason": "当前生命百分比伤害"}
        ]
    },
    # 6. 小蜜蜂 + 秘术冲拳
    {
        "pair": {"3086", "1058"},
        "bonus": 6.5,
        "name": "冲拳无限蜜蜂",
        "desc": "普攻减技能CD，技能触发小蜜蜂特效，技能与特效永动循环！",
        "core_items": [
            {"id": "3115", "name": "纳什之牙", "reason": "特效高频AP输出"},
            {"id": "3087", "name": "斯塔缇克电刃", "reason": "范围清场"},
            {"id": "3124", "name": "鬼索的狂暴之刃", "reason": "双重特效触发"}
        ]
    },
    # 7. 双刀流 + 秘术冲拳
    {
        "pair": {"1225", "1058"},
        "bonus": 7.0,
        "name": "双刀极限连打",
        "desc": "双发普攻每次减少2.5秒基础技能CD，所有小技能几乎无CD！",
        "core_items": [
            {"id": "3153", "name": "破败王者之刃", "reason": "双刀双重破败吸血"},
            {"id": "3302", "name": "界弓", "reason": "双穿双抗快速叠满"},
            {"id": "3124", "name": "鬼索的狂暴之刃", "reason": "攻速特效上限"}
        ]
    },
    # 8. 装甲冲击 + 巨像的勇气
    {
        "pair": {"3049", "1018"},
        "bonus": 6.5,
        "name": "重装装甲巨像",
        "desc": "巨额护盾与抗性配合装甲冲击2.5倍额外护甲范围AOE，又肉又秒人！",
        "core_items": [
            {"id": "3110", "name": "冰霜之心", "reason": "超高护甲直接转化装甲冲击巨额伤害"},
            {"id": "3075", "name": "荆棘之甲", "reason": "高护甲反伤重伤"},
            {"id": "3084", "name": "心之钢", "reason": "血量成长与巨像联动"}
        ]
    },
    # 9. 装甲冲击 + 不动如山
    {
        "pair": {"3049", "1149"},
        "bonus": 6.0,
        "name": "不动如山装甲核弹",
        "desc": "站立极大幅度抬高双抗，直接将装甲冲击范围额外伤害拉满！",
        "core_items": [
            {"id": "3110", "name": "冰霜之心", "reason": "极高护甲与技能急速"},
            {"id": "3075", "name": "荆棘之甲", "reason": "护甲最大化"},
            {"id": "6665", "name": "千变者贾修", "reason": "战斗中双抗再按百分比提升"}
        ]
    },
    # 10. 巨像的勇气 + 歌利亚巨人
    {
        "pair": {"1018", "1041"},
        "bonus": 7.0,
        "name": "万血泰坦双巨人",
        "desc": "双重体型与生命值乘算放大，心之钢伤害与面板血量突破两万！",
        "core_items": [
            {"id": "3084", "name": "心之钢", "reason": "超大体型超远钢人，伤害乘算放大"},
            {"id": "3083", "name": "狂徒铠甲", "reason": "巨额基础生命值"},
            {"id": "3075", "name": "荆棘之甲", "reason": "高额护甲补充前排坦度"}
        ]
    },
    # 11. 巨像的勇气 + 钢化你心
    {
        "pair": {"1018", "1152"},
        "bonus": 6.0,
        "name": "巨像超速叠钢",
        "desc": "心之钢叠加效率翻倍，配合巨像护盾形成不死前排！",
        "core_items": [
            {"id": "3084", "name": "心之钢", "reason": "核心叠钢装，层数飞涨"},
            {"id": "3083", "name": "狂徒铠甲", "reason": "回血永动机"},
            {"id": "6665", "name": "千变者贾修", "reason": "持久战抗性"}
        ]
    },
    # 12. 蓝色屏障 + 尤里卡
    {
        "pair": {"3051", "1030"},
        "bonus": 6.5,
        "name": "蓝盾无限刷新",
        "desc": "法强转急速配合消耗法力450%转护盾，技能无限放，护盾无限刷！",
        "core_items": [
            {"id": "3003", "name": "炽天使之拥", "reason": "高额蓝量、法强与终极护盾"},
            {"id": "3027", "name": "时光之杖", "reason": "成长法力值与续航"},
            {"id": "3004", "name": "魔宗", "reason": "法力值双重转化"}
        ]
    },
    # 13. 蓝色屏障 + 由心及物
    {
        "pair": {"3051", "1056"},
        "bonus": 6.0,
        "name": "法力护甲双壁垒",
        "desc": "蓝量抵扣伤害叠加耗蓝450%超大护盾，形成双重法力防御壁垒！",
        "core_items": [
            {"id": "3003", "name": "炽天使之拥", "reason": "法力值与护盾核心"},
            {"id": "3110", "name": "冰霜之心", "reason": "高额法力值与护甲"},
            {"id": "3027", "name": "时光之杖", "reason": "生命与法力双丰收"}
        ]
    },
    # 14. 终极刷新 + 奥术公理
    {
        "pair": {"1088", "3118"},
        "bonus": 7.0,
        "name": "无限大招连环轰炸",
        "desc": "大招刷新与奥术公理储存冷却互相覆盖，团战全程连续释放大招！",
        "core_items": [
            {"id": "6696", "name": "公理圆弧", "reason": "击杀减大招CD，双重回蓝回大"},
            {"id": "3161", "name": "朔极之矛", "reason": "高额技能急速与技能增伤"},
            {"id": "6697", "name": "狂妄", "reason": "击杀滚雪球攻击力"}
        ]
    },
    # 15. 终极刷新 + 鼓声暴起 低音轰鸣
    {
        "pair": {"1088", "3078"},
        "bonus": 6.5,
        "name": "疾风大招收割流",
        "desc": "施法加极端移速攻速，大招秒人立刻刷新，连环疾跑追击！",
        "core_items": [
            {"id": "6697", "name": "狂妄", "reason": "收割攻击力叠加"},
            {"id": "3161", "name": "朔极之矛", "reason": "施法急速与技能增伤"},
            {"id": "6333", "name": "死亡之舞", "reason": "击杀解流血回血"}
        ]
    },
    # 16. 泰坦的坚决 + 超凡邪恶
    {
        "pair": {"1001", "1390"},
        "bonus": 6.5,
        "name": "泰坦邪恶不死血泵",
        "desc": "挨打叠双抗法强 + 技能命中永久叠法强，AP加成回血与硬度无解！",
        "core_items": [
            {"id": "3065", "name": "振奋盔甲", "reason": "回血与治疗效果放大25%"},
            {"id": "6665", "name": "千变者贾修", "reason": "叠层双抗"},
            {"id": "3089", "name": "灭世者的死亡之帽", "reason": "AP法强乘算放大"}
        ]
    },
    # 17. 大腕 + 最万用的瞄准镜 / 更万用
    {
        "pair": {"3018", "1115"},
        "bonus": 6.0,
        "name": "千里之外核弹狙击",
        "desc": "超远射程提供绝对安全距离，攻速转爆伤一击毙命！",
        "core_items": [
            {"id": "3031", "name": "无尽之刃", "reason": "爆伤转化天花板"},
            {"id": "3094", "name": "疾射火炮", "reason": "再次拉长首发攻击射程"},
            {"id": "6676", "name": "收集者", "reason": "暴击穿甲斩杀"}
        ]
    },
    {
        "pair": {"3018", "1071"},
        "bonus": 5.0,
        "name": "超远爆伤狙击",
        "desc": "射程提升拉大身位，大腕爆伤加成输出拉满！",
        "core_items": [
            {"id": "3031", "name": "无尽之刃", "reason": "暴击爆伤放大"},
            {"id": "6676", "name": "收集者", "reason": "斩杀穿甲"}
        ]
    },
    # 18. 秘术冲拳 + 鼓声暴起 低音轰鸣
    {
        "pair": {"1058", "3078"},
        "bonus": 6.5,
        "name": "冲拳极速疾风连招",
        "desc": "施法加极端攻速移速，超高攻速又让冲拳疯狂减小技能CD，全程鬼畜连招！",
        "core_items": [
            {"id": "3153", "name": "破败王者之刃", "reason": "高攻速百分比吸血"},
            {"id": "3161", "name": "朔极之矛", "reason": "急速增伤"},
            {"id": "6333", "name": "死亡之舞", "reason": "持续作战免暴毙"}
        ]
    },
    # 19. 死亡之环 + 易损
    {
        "pair": {"1015", "1092"},
        "bonus": 6.5,
        "name": "死亡飞弹连锁风暴",
        "desc": "死亡之环将回血转化为全场伤害，易损让范围持续伤害无限触发暴击，连环引爆！",
        "core_items": [
            {"id": "3065", "name": "振奋盔甲", "reason": "提升治疗与环伤害"},
            {"id": "3083", "name": "狂徒铠甲", "reason": "超高生命与持续回复"}
        ]
    },
    # 20. 小蜜蜂 + 虚幻武器
    {
        "pair": {"3086", "1029"},
        "bonus": 7.5,
        "name": "蜜蜂虚幻全额引爆",
        "desc": "小蜜蜂多段攻击特效与虚幻武器技能附带普攻特效完美契合，瞬间打出满额爆发与多次三环！",
        "core_items": [
            {"id": "3087", "name": "斯塔缇克电刃", "reason": "电刀连锁电击"},
            {"id": "3115", "name": "纳什之牙", "reason": "高额法强特效伤害"}
        ]
    },
    # 21. 死亡之环 + 魔法飞弹
    {
        "pair": {"1015", "1133"},
        "bonus": 6.0,
        "name": "环噬飞弹永动爆鸣",
        "desc": "死亡之环群体伤害不断触发魔法飞弹，飞弹命中又造成多段伤害，全程自动轰炸！",
        "core_items": [
            {"id": "3065", "name": "振奋盔甲", "reason": "巨额治疗放大伤害"},
            {"id": "3089", "name": "灭世者的死亡之帽", "reason": "AP法强基数提升"}
        ]
    },
    # 22. 升级：贪欲九头蛇 + 钢化你心
    {
        "pair": {"2140", "1152"},
        "bonus": 5.5,
        "name": "巨人体魄顺劈狂澜",
        "desc": "钢化你心大幅提升生命上限，升级贪欲九头蛇一击顺劈多次，体型与AOE范围毁天灭地！",
        "core_items": [
            {"id": "3074", "name": "贪欲九头蛇", "reason": "高额吸血顺劈"},
            {"id": "3084", "name": "心之钢", "reason": "无限叠生命上限"}
        ]
    },
    # 23. 蓝色屏障 + 奥术公理
    {
        "pair": {"3051", "3118"},
        "bonus": 5.5,
        "name": "巨盾大招无限流转",
        "desc": "蓝色屏障提供基于耗蓝的巨厚护盾保障生存，奥术公理快速刷新大招实现攻防一体！",
        "core_items": [
            {"id": "3003", "name": "炽天使之拥", "reason": "超大蓝量巨额护盾"},
            {"id": "3027", "name": "时光之杖", "reason": "生命法力续航成长"}
        ]
    },
    # 24. 连锁反应 + 珠光护手
    {
        "pair": {"2078", "1048"},
        "bonus": 6.5,
        "name": "连锁核弹全域融化",
        "desc": "连锁反应的爆炸伤害与珠光护手法爆结合，击杀一人瞬间引发全场暴击爆轰！",
        "core_items": [
            {"id": "6656", "name": "风暴狂涌", "reason": "斩杀加速连环爆炸"},
            {"id": "4645", "name": "影焰", "reason": "残血必爆"},
            {"id": "3089", "name": "灭世者的死亡之帽", "reason": "最大化法强"}
        ]
    },
    # 25. 命运之武器 + 虚幻武器
    {
        "pair": {"3081", "1029"},
        "bonus": 6.0,
        "name": "命运虚幻超距连击",
        "desc": "命运之武器为首件装备提供无限成长属性，虚幻武器让技能触发普攻特效，远程瞬间融化敌方！",
        "core_items": [
            {"id": "6695", "name": "巨蛇之牙", "reason": "纯攻击力穿甲低成本高成长"},
            {"id": "3094", "name": "疾射火炮", "reason": "超远首发攻击"},
            {"id": "3100", "name": "巫妖之祸", "reason": "耀光高爆发"}
        ]
    },
    # 26. 叠角龙 + 钢化你心
    {
        "pair": {"1204", "1152"},
        "bonus": 7.5,
        "name": "叠角狂澜八倍叠钢",
        "desc": "叠角龙体型角倍数与钢化你心双倍叠钢叠加，心之钢成长效率最高达8.7倍，血量无限狂飙！",
        "core_items": [
            {"id": "3084", "name": "心之钢", "reason": "核心叠钢"},
            {"id": "3083", "name": "狂徒铠甲", "reason": "基础生命放大"},
            {"id": "3748", "name": "巨型九头蛇", "reason": "生命转高额普攻攻击力"}
        ]
    },
    # 27. 超凡邪恶 + 尤里卡
    {
        "pair": {"1390", "1030"},
        "bonus": 8.0,
        "name": "邪恶尤里卡法神永动",
        "desc": "超凡邪恶无限永久叠法强，尤里卡将法强全额转化为巨额技能急速，全英雄所有技能零冷却！",
        "core_items": [
            {"id": "3089", "name": "灭世者的死亡之帽", "reason": "法强乘算天花板"},
            {"id": "3003", "name": "炽天使之拥", "reason": "无限蓝量与超厚护盾"},
            {"id": "4645", "name": "影焰", "reason": "法术残血暴击"}
        ]
    },
    # 28. 双发快射 + 秘术冲拳
    {
        "pair": {"2010", "1058"},
        "bonus": 7.0,
        "name": "双发冲拳极速刷招",
        "desc": "双发快射每次普攻触发双重命中，完美触发秘术冲拳双倍返还技能冷却，技能秒刷！",
        "core_items": [
            {"id": "3153", "name": "破败王者之刃", "reason": "双发高额吸血与特效"},
            {"id": "3124", "name": "鬼索的狂暴之刃", "reason": "特效层数翻倍"},
            {"id": "3302", "name": "界弓", "reason": "双穿双抗快速成型"}
        ]
    },
    # 29. 踢踏舞 + 全凭身法
    {
        "pair": {"1081", "1019"},
        "bonus": 7.0,
        "name": "踢踏身法万速天帝",
        "desc": "踢踏舞攻击叠加移速攻击力，全凭身法移速与攻速闭环互转，移速突破上万，一枪瞬秒满血！",
        "core_items": [
            {"id": "3087", "name": "斯塔缇克电刃", "reason": "电刀弹射全额叠加踢踏舞层数"},
            {"id": "3094", "name": "疾射火炮", "reason": "超远首发开移速"},
            {"id": "3031", "name": "无尽之刃", "reason": "万攻暴击一枪秒杀"}
        ]
    },
    # 30. 地形专家 + 面包和奶酪
    {
        "pair": {"2129", "1151"},
        "bonus": 6.5,
        "name": "地形封路无限领域",
        "desc": "创造或经过地形获得巨额急速与减伤，配合面包和奶酪技能极速，地形技能无缝衔接无限折磨！",
        "core_items": [
            {"id": "3161", "name": "朔极之矛", "reason": "急速最大化"},
            {"id": "3116", "name": "瑞莱的冰晶节杖", "reason": "减速封路控制"},
            {"id": "6665", "name": "千变者贾修", "reason": "双抗坦度"}
        ]
    },
    # 31. 高压锅 + 巨像的勇气
    {
        "pair": {"2102", "1018"},
        "bonus": 6.5,
        "name": "高压巨像全域熔炉",
        "desc": "巨像提供巨厚生命与护盾，高压锅将承伤转化为强力范围灼烧与爆炸，被控被围殴时反伤直接团灭敌方！",
        "core_items": [
            {"id": "3084", "name": "心之钢", "reason": "血量基数提升"},
            {"id": "3068", "name": "日炎圣盾", "reason": "双重范围火甲灼烧"},
            {"id": "6665", "name": "千变者贾修", "reason": "抗性最大化"}
        ]
    }
]

# 组合交互类型（算分用，见 fit.computed_combo_bonus）：手工表只维护「有什么交互」，
# 「加多少分」由交互类型 × 机制耦合度推导，不再用攻略视频拍的手工数值。
COMBO_TYPES: dict[frozenset, str] = {
    frozenset({"1048", "1092"}): "multiplicative",  # 珠光护手×易损：技能暴击×全技能暴击乘算
    frozenset({"3123", "1092"}): "multiplicative",
    frozenset({"1048", "3123"}): "multiplicative",
    frozenset({"1048", "3018"}): "multiplicative",  # 大腕爆伤×技能暴击
    frozenset({"3086", "1225"}): "frequency",       # 小蜜蜂×双刀流：触发×频率
    frozenset({"3086", "1058"}): "frequency",
    frozenset({"1225", "1058"}): "frequency",
    frozenset({"3049", "1018"}): "additive",        # 装甲冲击×巨像：同套坦装堆叠
    frozenset({"3049", "1149"}): "resource",        # 不动如山供双抗，装甲冲击转伤害
    frozenset({"1018", "1041"}): "additive",        # 双巨人堆血
    frozenset({"1018", "1152"}): "additive",
    frozenset({"3051", "1030"}): "resource",        # 尤里卡法强转急速→多放技能→多耗蓝→盾
    frozenset({"3051", "1056"}): "resource",        # 法力互转双壁垒
    frozenset({"1088", "3118"}): "resource",        # 大招冷却循环
    frozenset({"1088", "3078"}): "frequency",       # 刷新给更多施法，低音轰鸣吃施法频次
    frozenset({"1001", "1390"}): "additive",        # 都叠法强/双抗
    frozenset({"3018", "1115"}): "multiplicative",  # 射程保输出环境×爆伤
    frozenset({"3018", "1071"}): "multiplicative",
    frozenset({"1058", "3078"}): "frequency",       # 冲拳攻速刷CD×施法加速
    frozenset({"1015", "1092"}): "multiplicative",  # 死亡之环持续伤害吃易损暴击
    frozenset({"3086", "1029"}): "frequency",       # 小蜜蜂×虚幻武器：特效互触
    frozenset({"1015", "1133"}): "frequency",       # 环伤不断触发飞弹
    frozenset({"2140", "1152"}): "additive",        # 堆血
    frozenset({"3051", "3118"}): "resource",        # 蓝量→盾，大招循环
    frozenset({"2078", "1048"}): "multiplicative",  # 连锁爆炸吃法爆
    frozenset({"3081", "1029"}): "multiplicative",  # 命运武器放大首件装备×特效
    frozenset({"1204", "1152"}): "additive",        # 叠钢堆血
    frozenset({"1390", "1030"}): "resource",        # 超凡叠法强，尤里卡法强转急速
    frozenset({"2010", "1058"}): "frequency",       # 双发×冲拳：双倍触发
    frozenset({"1081", "1019"}): "frequency",       # 移速攻速闭环互转
    frozenset({"2129", "1151"}): "resource",        # 地形急速×技能急速
    frozenset({"2102", "1018"}): "additive",        # 堆血
}

AUGMENT_CONFLICTS: list[dict[str, Any]] = [
    {
        "pair": {"3018", "1225"},
        "penalty": -5.0,
        "reason": "【大腕】已将攻速转化为爆伤，与【双刀流】降低射程增加攻速产生机制冲突！"
    },
    {
        "pair": {"1225", "1115"},
        "penalty": -4.0,
        "reason": "【双刀流】射程减半抵消了【最万用的瞄准镜】超远射程收益，容易断输出节奏！"
    },
    {
        "pair": {"1054", "1004"},
        "penalty": -4.0,
        "reason": "【回归基本功】封印基础小技能，导致【物法皆修】频繁施法与普攻交替机制失效！"
    }
]


# 联动加分递减与封顶：单组按表值，第二组起按 30% 计入，总量不超过单组最大值。
# 手工组合分只是机制先验，不能无限叠盖过实测胜率差（实测 Δ 通常只有 ±3pp）。
COMBO_BONUS_CAP = 8.0
COMBO_STACK_DECAY = 0.3


def evaluate_combo_synergies(candidate_aid: str, acquired_aids: list[str]) -> dict[str, Any]:
    """
    计算当前候选海克斯 candidate_aid 与局内已选海克斯 acquired_aids 的多符文联动协同与冲突：
    返回:
    - bonus: float (联动总加分，机制推导值递减叠加并封顶，见 COMBO_BONUS_CAP / COMBO_STACK_DECAY)
    - penalty: float (冲突扣分)
    - net_score: float (净增减分)
    - reasons: list[str] (联动理由)
    - conflicts: list[str] (冲突警告)
    - core_items: list[dict] (推荐必出装备)

    加多少分由 fit.computed_combo_bonus 推导（交互类型 × 机制耦合度），不再用攻略视频拍的手工值；
    表里没有的组合按共享机制推算（标注「推算」、封顶 GENERIC_CAP）。
    """
    from . import fit as fit_mod

    if not candidate_aid or not acquired_aids:
        return {"bonus": 0.0, "penalty": 0.0, "net_score": 0.0, "reasons": [], "conflicts": [], "core_items": []}

    cand = str(candidate_aid)
    acq_set = {str(a) for a in acquired_aids if a and str(a) != cand}

    bonuses: list[float] = []
    penalty = 0.0
    reasons = []
    conflicts = []
    core_items = []
    seen_item_ids = set()
    curated_partners: set[str] = set()

    for combo in AUGMENT_COMBOS:
        pair = combo["pair"]
        if cand in pair:
            other = (pair - {cand}).pop()
            if other in acq_set:
                curated_partners.add(other)
                calc = fit_mod.computed_combo_bonus(cand, other, itype=COMBO_TYPES.get(frozenset(pair)), curated=True)
                bonuses.append(calc["bonus"])
                type_cn = fit_mod.INTERACTION_CN[calc["type"]]
                shared = f"（共享：{'、'.join(calc['shared'])}）" if calc["shared"] else "（机制模型外，人工确认）"
                reasons.append(f"★ 组合联动【{combo['name']}】· {type_cn}算分 {calc['bonus']:+.1f}pp{shared}：{combo['desc']}")
                for it in combo.get("core_items", []):
                    if it["id"] not in seen_item_ids:
                        seen_item_ids.add(it["id"])
                        core_items.append(it)

    for conf in AUGMENT_CONFLICTS:
        pair = conf["pair"]
        if cand in pair:
            other = (pair - {cand}).pop()
            if other in acq_set:
                curated_partners.add(other)  # 有冲突的组合不再推算正联动（冲突即结论）
                penalty += conf["penalty"]
                conflicts.append(conf["reason"])

    # 表里没有的组合：共享机制够强也推算给分（封顶 GENERIC_CAP，写明是推算不是评审值）
    for other in sorted(acq_set - curated_partners):
        calc = fit_mod.computed_combo_bonus(cand, other)
        if calc["bonus"] > 0:
            bonuses.append(calc["bonus"])
            reasons.append(f"◇ 机制联动（推算）· {fit_mod.INTERACTION_CN[calc['type']]} {calc['bonus']:+.1f}pp"
                           f"（共享：{'、'.join(calc['shared'])}）")

    # 多组联动递减叠加并封顶（见 COMBO_BONUS_CAP / COMBO_STACK_DECAY）
    bonus = 0.0
    if bonuses:
        bonuses.sort(reverse=True)
        bonus = min(COMBO_BONUS_CAP, bonuses[0] + COMBO_STACK_DECAY * sum(bonuses[1:]))

    return {
        "bonus": round(bonus, 2),
        "penalty": round(penalty, 2),
        "net_score": round(bonus + penalty, 2),
        "reasons": reasons,
        "conflicts": conflicts,
        "core_items": core_items
    }


def get_augment_core_items(augment_id: str, store: Any = None, hero_id: str | None = None) -> list[dict[str, Any]]:
    """
    获取单个海克斯专属的核心必出质变装备。
    支持结合英雄专属特化与主流流派母版补全。
    """
    aid_str = str(augment_id or "")
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        return AUGMENT_PIVOT_ANCHORS[aid_str].get("items", [])

    if hero_id:
        hid_str = str(hero_id)
        if hid_str in DUAL_PLAYSTYLE_PROFILES:
            dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
            if aid_str in dual["candidate_augments"]:
                return dual["items"]
        hint = get_synergy_item_hint(store, hid_str, aid_str)
        if hint and hint.get("items"):
            return [{"id": x.get("item") or x.get("id"), "name": x.get("name", "")} for x in hint["items"]]

    return []


def get_hero_rune_build(hero_id: str | None, acquired_aids: list[str] | None, store: Any = None) -> dict[str, Any]:
    """
    推导英雄当前最契合的【符文专精流派出装】：
    1. 若局内已选海克斯 (acquired_aids)，优先推导海克斯强联动（如小蜜蜂狗熊、珠光大腕女警、心之钢反甲、双刀流等）；
    2. 若暂未选海克斯，结合英雄在 4.0 绝活攻略中的主流定位，生成【预备推荐流派】，并在选入符文后动态转轨；
    3. 返回完整 5 件神装路线（含 ID、名称、图标），并附带流派质变联动机制解析。
    """
    hid_str = str(hero_id or "")
    acq_list = [str(a) for a in (acquired_aids or []) if a]
    items_dict = getattr(store, "items", {}) or {}
    aug_dict = getattr(store, "augments", {}) or {}

    def format_item(it: dict[str, Any]) -> dict[str, Any]:
        iid = str(it.get("id") or it.get("item") or "")
        meta = items_dict.get(iid, {})
        name = it.get("name") or meta.get("name") or iid
        icon = it.get("icon") or meta.get("icon")
        return {"id": iid, "item": iid, "name": name, "icon": icon}

    aug_details = []
    for aid in acq_list:
        ameta = aug_dict.get(aid, {})
        aug_details.append({
            "id": aid,
            "name": ameta.get("name", aid),
            "rarity": ameta.get("rarity", "")
        })

    matched_build = None
    matched_explanation = ""
    matched_source = ""
    combo_items = []

    # 1. 尝试从已持海克斯组合与转轨中匹配
    # 1.1 组合联动匹配 (AUGMENT_COMBOS)
    if len(acq_list) >= 2:
        for i in range(len(acq_list)):
            for j in range(i + 1, len(acq_list)):
                pair = {acq_list[i], acq_list[j]}
                for combo in AUGMENT_COMBOS:
                    if combo["pair"] == pair:
                        matched_build = combo.get("name")
                        matched_explanation = f"激活【{combo['name']}】组合：{combo['desc']}"
                        matched_source = f"组合联动【{combo['name']}】"
                        combo_items = combo.get("core_items", [])
                        break
                if matched_build:
                    break
            if matched_build:
                break

    # 1.2 英雄特化转轨匹配 (DUAL_PLAYSTYLE_PROFILES)
    if not matched_build and hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        for aid in acq_list:
            if aid in dual["candidate_augments"]:
                aname = (aug_dict.get(aid) or {}).get("name") or aid
                matched_build = dual["build_name"]
                matched_explanation = f"已选质变符文【{aname}】：触发 4.0 绝活流派质变，专属装备路线直接拉满！"
                matched_source = f"绝活符文【{aname}】"
                combo_items = dual["items"]
                break

    # 1.3 单海克斯锚点匹配 (AUGMENT_PIVOT_ANCHORS)
    if not matched_build:
        for aid in acq_list:
            if aid in AUGMENT_PIVOT_ANCHORS:
                anchor = AUGMENT_PIVOT_ANCHORS[aid]
                aname = (aug_dict.get(aid) or {}).get("name") or aid
                matched_build = anchor["build_name"]
                matched_explanation = f"已选符文【{aname}】：该符文机制大幅改变出装优先级，推荐优先合成上述核心装备。"
                matched_source = f"质变符文【{aname}】"
                combo_items = anchor["items"]
                break

    # 1.4 若局内有符文已选成功匹配
    if matched_build and combo_items:
        archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES['Bruiser_Drain'])
        full_items = list(combo_items)
        seen_ids = {str(it.get("id") or it.get("item")) for it in full_items}
        for it in template.get("items", []):
            iid = str(it.get("id") or it.get("item"))
            if iid not in seen_ids:
                seen_ids.add(iid)
                full_items.append(it)
            if len(full_items) >= 5:
                break

        return {
            "build_name": matched_build,
            "status_label": f"已根据【{matched_source}】质变转轨",
            "is_rune_adapted": True,
            "items": [format_item(x) for x in full_items[:5]],
            "explanation": matched_explanation,
            "augments": aug_details
        }

    # 2. 未匹配到专属海克斯（或尚未选择海克斯）时的推荐流派
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        full_items = list(dual["items"])
        archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES['Bruiser_Drain'])
        seen_ids = {str(it.get("id") or it.get("item")) for it in full_items}
        for it in template.get("items", []):
            iid = str(it.get("id") or it.get("item"))
            if iid not in seen_ids:
                seen_ids.add(iid)
                full_items.append(it)
            if len(full_items) >= 5:
                break
        return {
            "build_name": dual["build_name"],
            "status_label": "4.0 绝活流派预备推荐（选入海克斯后动态转轨）",
            "is_rune_adapted": False,
            "items": [format_item(x) for x in full_items[:5]],
            "explanation": "该英雄在 4.0 版本的强力打法。三选一若刷出对应质变海克斯将彻底激活！",
            "augments": aug_details
        }

    archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES['Bruiser_Drain'])
    return {
        "build_name": template["name"],
        "status_label": "4.0 标准流派推荐（选入海克斯后动态转轨）",
        "is_rune_adapted": False,
        "items": [format_item(x) for x in template["items"][:5]],
        "explanation": "当前为该英雄主流出装公式。局内选择海克斯符文后，将实时推导专属质变出装路线。",
        "augments": aug_details
    }


def get_acquired_augments_build_advice(acquired_aids: list[str], store: Any = None) -> list[dict[str, Any]]:
    """
    根据本局已选海克斯列表，汇总当前海克斯流派推荐的核心必出装备。
    """
    if not acquired_aids:
        return []

    advice_items = []
    seen_ids = set()

    # 1. 先查组合联动装备
    acq_list = [str(a) for a in acquired_aids if a]
    for i in range(len(acq_list)):
        for j in range(i + 1, len(acq_list)):
            pair = {acq_list[i], acq_list[j]}
            for combo in AUGMENT_COMBOS:
                if combo["pair"] == pair:
                    for it in combo.get("core_items", []):
                        if it["id"] not in seen_ids:
                            seen_ids.add(it["id"])
                            advice_items.append({**it, "source": f"组合联动【{combo['name']}】"})

    # 2. 再查各个单海克斯的专属锚点出装
    for aid in acq_list:
        if aid in AUGMENT_PIVOT_ANCHORS:
            anchor = AUGMENT_PIVOT_ANCHORS[aid]
            for it in anchor.get("items", []):
                if it["id"] not in seen_ids:
                    seen_ids.add(it["id"])
                    advice_items.append({**it, "source": f"符文【{anchor['build_name']}】"})

    return advice_items

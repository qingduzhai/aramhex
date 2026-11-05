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
    '72': 'Tank_Frontline',

    # AD 远距离 Poke / 技能穿甲流
    '81': 'AD_Spellcaster_Poke', '42': 'AD_Spellcaster_Poke', '126': 'AD_Spellcaster_Poke',
    '901': 'AD_Spellcaster_Poke', '41': 'AD_Spellcaster_Poke',

    # 混合攻击特效 / 攻速流
    '145': 'ADC_Hybrid_OnHit', '96': 'ADC_Hybrid_OnHit', '110': 'ADC_Hybrid_OnHit',
    '67': 'ADC_Hybrid_OnHit', '429': 'ADC_Hybrid_OnHit', '10': 'ADC_Hybrid_OnHit',
    '4': 'ADC_Hybrid_OnHit',

    # 经典暴击 ADC
    '22': 'ADC_Crit', '51': 'ADC_Crit', '222': 'ADC_Crit', '18': 'ADC_Crit',
    '236': 'ADC_Crit', '202': 'ADC_Crit', '119': 'ADC_Crit', '15': 'ADC_Crit',
    '29': 'ADC_Crit', '498': 'ADC_Crit', '523': 'ADC_Crit', '360': 'ADC_Crit',
    '221': 'ADC_Crit', '895': 'ADC_Crit', '166': 'ADC_Crit', '133': 'ADC_Crit',
    '104': 'ADC_Crit', '203': 'ADC_Crit',

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

    # 战士重装 / 吸血持续作战
    '266': 'Bruiser_Drain', '122': 'Bruiser_Drain', '86': 'Bruiser_Drain', '875': 'Bruiser_Drain',
    '157': 'Bruiser_Drain', '777': 'Bruiser_Drain', '24': 'Bruiser_Drain', '39': 'Bruiser_Drain',
    '92': 'Bruiser_Drain', '58': 'Bruiser_Drain', '75': 'Bruiser_Drain', '82': 'Bruiser_Drain',
    '164': 'Bruiser_Drain', '114': 'Bruiser_Drain', '887': 'Bruiser_Drain', '420': 'Bruiser_Drain',
    '240': 'Bruiser_Drain', '2': 'Bruiser_Drain', '80': 'Bruiser_Drain', '48': 'Bruiser_Drain',
    '77': 'Bruiser_Drain', '6': 'Bruiser_Drain', '19': 'Bruiser_Drain', '62': 'Bruiser_Drain',
    '5': 'Bruiser_Drain', '83': 'Bruiser_Drain', '233': 'Bruiser_Drain', '799': 'Bruiser_Drain',
    '254': 'Bruiser_Drain', '213': 'Bruiser_Drain', '102': 'Bruiser_Drain', '120': 'Bruiser_Drain',
    '11': 'Bruiser_Drain',

    # 物理刺客爆发
    '238': 'Assassin_Lethality', '91': 'Assassin_Lethality', '55': 'Assassin_Lethality',
    '121': 'Assassin_Lethality', '107': 'Assassin_Lethality', '245': 'Assassin_Lethality',
    '35': 'Assassin_Lethality', '246': 'Assassin_Lethality', '7': 'Assassin_Lethality'
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
    }
}

# ==========================================
# 4. 4.0 绝活英雄双修/特化转轨规则 (Hero Playstyle Pivots)
# ==========================================
DUAL_PLAYSTYLE_PROFILES: dict[str, dict[str, Any]] = {
    # 沃利贝尔 (Volibear 106) -> 小蜜蜂电刀连锁闪电流 (抖音实战绝活)
    '106': {
        'candidate_augments': {'3086', '1058', '1225'},
        'build_name': '小蜜蜂连锁雷暴流',
        'items': [
            {'id': '3087', 'name': '斯塔缇克电刃'},
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 卡莎 (Kai'Sa 145) -> 小蜜蜂 W 双电浆瞬间引爆
    '145': {
        'candidate_augments': {'3086', '1048', '3123'},
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
    # 凯特琳 (Caitlyn 51) -> 双珠光 + 大腕 颗秒女警
    '51': {
        'candidate_augments': {'3018', '1048', '3123', '1092'},
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
    # 赫卡里姆 (Hecarim 120) -> 低音轰鸣 74% 胜率亲爹流
    '120': {
        'candidate_augments': {'3078', '3049', '1151'},
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
    # 赵信 (Zhao Xin 5) -> 超凡邪恶 抽血泵流派
    '5': {
        'candidate_augments': {'1390', '1058', '1225'},
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
    # 墨菲特 (Malphite 54) -> 装甲冲击纯肉 / AP秒杀
    '54': {
        'candidate_augments': {'3049', '1048', '3123', '1332'},
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
    # 提莫 (Teemo 17) -> 普攻特效攻速流
    '17': {
        'candidate_augments': {'1001', '1019', '1058', '3086'},
        'build_name': '毒素特效攻速流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3153', 'name': '破败王者之刃'}
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
                hint["title"] = "核心协同出装 · 统计优选"
                hint["footer"] = "选该符文后的推荐装备配合"
                return hint
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
    '1134': "亮出你的剑：近战普攻与吸血大幅强化，战士对拼极品"
}


def classify_augment_tier(store: Any, hero_id: str | None, augment_id: str | None,
                          win_rate: float | None, score: float | None, games: int | None) -> dict[str, str]:
    """
    双轨制决策分类器：
    返回徽章标签（badge）、图标（icon）与简明建议（label）。
    结合 4.0 绝活海克斯库与官方大数据置信度。
    """
    aid_str = str(augment_id or "")

    # 1. 4.0 顶级质变核心符文
    if aid_str in AUGMENT_META_EXPLANATIONS:
        expl = AUGMENT_META_EXPLANATIONS[aid_str]
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": f"4.0质变核心：{expl}"
        }

    # 2. 质变海克斯锚点
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": "质变核心符文，改变打法并提供极高胜率上限"
        }

    # 3. 大样本极高 Lift (Delta > +2.5pp)
    if score is not None and score >= 2.5 and (games or 0) >= 400:
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": f"流派核心符文，相对该英雄基准提升 {score:+.1f}pp"
        }

    # 4. 泛用万金油 (稳妥)
    if (win_rate is not None and win_rate >= 0.518) and (score is None or score >= -0.2):
        return {
            "badge": "🛡️ 稳妥",
            "tag": "evergreen",
            "summary": "泛用万金油符文，容错率高、发挥稳定"
        }

    # 5. 陷阱提示 (负 Lift 且胜率低)
    if score is not None and score <= -1.8 and (games or 0) >= 300:
        return {
            "badge": "⚠️ 陷阱",
            "tag": "trap",
            "summary": f"版本陷阱！相比该英雄基准降低 {abs(score):.1f}pp，建议刷新"
        }

    # 6. 低于基准期望，建议刷新
    if score is not None and score < -0.5:
        return {
            "badge": "🎲 慎选",
            "tag": "reroll",
            "summary": "低于基准期望，可优先考虑掷骰刷新"
        }

    return {
        "badge": "✨ 可选",
        "tag": "normal",
        "summary": "契合常规对局，正常可选"
    }

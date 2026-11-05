# -*- coding: utf-8 -*-
"""
海克斯符文与装备流派协同推导引擎 (AramHex Synergy Engine)
为海克斯大乱斗提供：
1. 海克斯 ➡️ 流派归属与核心装备联动路线 (Item Synergy Hints)
2. 双轨决策分类器 (Lift主判据 + 置信度 + 核心/万金油/陷阱判定)
3. 双修英雄动态流派转轨 (Playstyle Pivots)
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
    '254': 'Bruiser_Drain', '213': 'Bruiser_Drain', '102': 'Bruiser_Drain',

    # 物理刺客爆发
    '238': 'Assassin_Lethality', '91': 'Assassin_Lethality', '55': 'Assassin_Lethality',
    '121': 'Assassin_Lethality', '107': 'Assassin_Lethality', '245': 'Assassin_Lethality',
    '35': 'Assassin_Lethality', '246': 'Assassin_Lethality', '7': 'Assassin_Lethality'
}

# ==========================================
# 2. 流派母版与核心装备配置
# ==========================================
ARCHETYPE_BUILD_TEMPLATES = {
    'ADC_Crit': {
        'name': '暴击破甲流',
        'items': [
            {'id': '3031', 'name': '无尽之刃'},
            {'id': '3033', 'name': '凡性的提醒'},
            {'id': '6676', 'name': '收集者'},
            {'id': '3046', 'name': '幻影之舞'},
            {'id': '3085', 'name': '卢安娜的飓风'}
        ]
    },
    'ADC_Hybrid_OnHit': {
        'name': '攻击特效攻速流',
        'items': [
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3302', 'name': '界弓'},
            {'id': '3091', 'name': '智慧末刃'}
        ]
    },
    'AD_Spellcaster_Poke': {
        'name': '穿甲技能Poke流',
        'items': [
            {'id': '3142', 'name': '幽梦之灵'},
            {'id': '6692', 'name': '星蚀'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'},
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '3004', 'name': '魔宗'}
        ]
    },
    'AP_Burst_Poke': {
        'name': '法爆极速秒杀流',
        'items': [
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'},
            {'id': '4646', 'name': '风暴狂涌'},
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '3135', 'name': '虚空之杖'}
        ]
    },
    'AP_Burn_Haste': {
        'name': '面具灼烧急速流',
        'items': [
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '2503', 'name': '黯炎火炬'},
            {'id': '3118', 'name': '残疫'},
            {'id': '3116', 'name': '瑞莱的冰晶节杖'},
            {'id': '3165', 'name': '莫雷洛秘典'}
        ]
    },
    'Bruiser_Drain': {
        'name': '重装战士吸血流',
        'items': [
            {'id': '3078', 'name': '三相之力'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3065', 'name': '振奋盔甲'},
            {'id': '3053', 'name': '斯特拉克的挑战护手'}
        ]
    },
    'Tank_Frontline': {
        'name': '心之钢巨像坦克流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '2502', 'name': '无终恨意'},
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '3068', 'name': '日炎圣盾'},
            {'id': '3075', 'name': '荆棘之甲'}
        ]
    },
    'Assassin_Lethality': {
        'name': '极致穿甲爆发流',
        'items': [
            {'id': '3142', 'name': '幽梦之灵'},
            {'id': '6692', 'name': '星蚀'},
            {'id': '6676', 'name': '收集者'},
            {'id': '6697', 'name': '狂妄'},
            {'id': '6694', 'name': '塞瑞尔达的怨恨'}
        ]
    }
}

# ==========================================
# 3. 质变海克斯专属锚点出装 (Pivot Anchors)
# ==========================================
AUGMENT_PIVOT_ANCHORS: dict[str, dict[str, Any]] = {
    # 亮出你的剑
    '1134': {
        'build_name': '近战重装吸血流',
        'items': [
            {'id': '3078', 'name': '三相之力'},
            {'id': '6333', 'name': '死亡之舞'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 珠光护手 / 魔法飞弹 / 法爆类
    '3009': {
        'build_name': '法术暴击秒杀流',
        'items': [
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'},
            {'id': '4646', 'name': '风暴狂涌'}
        ]
    },
    # 秘术冲拳
    '1058': {
        'build_name': '普攻减CD特效流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 万用瞄准镜
    '1001': {
        'build_name': '超远射程攻速流',
        'items': [
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '6672', 'name': '海妖杀手'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 巨像的勇气
    '1018': {
        'build_name': '前排护盾肉弹流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '2502', 'name': '无终恨意'},
            {'id': '6665', 'name': '千变者贾修'}
        ]
    },
    # 全凭身法
    '1019': {
        'build_name': '移速攻速连携流',
        'items': [
            {'id': '3046', 'name': '幻影之舞'},
            {'id': '3094', 'name': '疾射火炮'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 面包和奶酪
    '1151': {
        'build_name': '技能急速无限连流',
        'items': [
            {'id': '3161', 'name': '朔极之矛'},
            {'id': '6675', 'name': '纳沃利烁刃'},
            {'id': '6655', 'name': '卢登的伙伴'}
        ]
    },
    # 恶魔契约
    '1332': {
        'build_name': '恶魔高法强斩杀流',
        'items': [
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'},
            {'id': '4646', 'name': '风暴狂涌'}
        ]
    },
    # 命运之武器
    '3081': {
        'build_name': '命运附魔输出流',
        'items': [
            {'id': '3078', 'name': '三相之力'},
            {'id': '3153', 'name': '破败王者之刃'},
            {'id': '3031', 'name': '无尽之刃'}
        ]
    },
    # 神圣雪球
    '1392': {
        'build_name': '雪球开团强突流',
        'items': [
            {'id': '3084', 'name': '心之钢'},
            {'id': '6665', 'name': '千变者贾修'},
            {'id': '2502', 'name': '无终恨意'}
        ]
    },
    # 虚空幼体 / 小丑学院
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
# 4. 双修/特化英雄转轨规则 (Hero Playstyle Pivots)
# ==========================================
DUAL_PLAYSTYLE_PROFILES: dict[str, dict[str, Any]] = {
    # 韦鲁斯 (Varus) -> AP 爆鸣流
    '110': {
        'candidate_augments': {'3009', '1151', '1332', '3170', '1310'},
        'build_name': 'AP枯萎引爆流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 提莫 (Teemo) -> 普攻特效攻速流
    '17': {
        'candidate_augments': {'1001', '1019', '1058', '3124'},
        'build_name': '毒素特效攻速流',
        'items': [
            {'id': '3115', 'name': '纳什之牙'},
            {'id': '3124', 'name': '鬼索的狂暴之刃'},
            {'id': '3153', 'name': '破败王者之刃'}
        ]
    },
    # 墨菲特 (Malphite) -> 卢登核弹法爆流
    '54': {
        'candidate_augments': {'3009', '1332', '1392', '1151'},
        'build_name': '核弹大招秒杀流',
        'items': [
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 加里奥 (Galio) -> AP秒人流
    '3': {
        'candidate_augments': {'3009', '1332', '1151'},
        'build_name': '法强进场秒人流',
        'items': [
            {'id': '6655', 'name': '卢登的伙伴'},
            {'id': '4645', 'name': '影焰'},
            {'id': '3089', 'name': '灭世者的死亡之帽'}
        ]
    },
    # 希瓦娜 (Shyvana) -> 魔龙吐息 AP 流
    '102': {
        'candidate_augments': {'3009', '1151', '1332', '1310'},
        'build_name': '魔龙吐息AP流',
        'items': [
            {'id': '6653', 'name': '兰德里的折磨'},
            {'id': '3089', 'name': '灭世者的死亡之帽'},
            {'id': '4645', 'name': '影焰'}
        ]
    },
    # 茂凯 (Maokai) -> 树苗消耗 AP 流
    '57': {
        'candidate_augments': {'1310', '1151', '1332'},
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
    1. 优先查质变海克斯专属锚点 (Pivot Anchor)；
    2. 其次查英雄双修转轨 (Dual Playstyle Override)；
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

    # 2. 检查质变海克斯锚点
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        anchor = AUGMENT_PIVOT_ANCHORS[aid_str]
        rows = [format_item(x) for x in anchor["items"][:3]]
        return {
            "source": "stats",
            "title": f"核心协同路线 · {anchor['build_name']}",
            "footer": "选该符文后的推荐装备配合",
            "items": rows
        }

    # 3. 检查双修英雄转轨
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        if aid_str in dual["candidate_augments"]:
            rows = [format_item(x) for x in dual["items"][:3]]
            return {
                "source": "stats",
                "title": f"流派转轨推荐 · {dual['build_name']}",
                "footer": "符文触发转轨，建议搭配此套出装",
                "items": rows
            }

    # 4. 英雄默认主流派母版
    archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES['Bruiser_Drain'])
    rows = [format_item(x) for x in template["items"][:3]]
    return {
        "source": "stats",
        "title": f"核心协同路线 · {template['name']}",
        "footer": "选该符文后的推荐装备配合",
        "items": rows
    }


def classify_augment_tier(store: Any, hero_id: str | None, augment_id: str | None,
                          win_rate: float | None, score: float | None, games: int | None) -> dict[str, str]:
    """
    双轨制决策分类器：
    返回徽章标签（badge）、图标（icon）与简明建议（label）。
    """
    aid_str = str(augment_id or "")

    # 质变核心
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": "质变核心符文，改变打法并提供极高胜率上限"
        }

    # 大样本极高 Lift (Delta > +2.5pp)
    if score is not None and score >= 2.5 and (games or 0) >= 400:
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": f"流派核心符文，相对该英雄基准提升 {score:+.1f}pp"
        }

    # 泛用万金油
    if (win_rate is not None and win_rate >= 0.518) and (score is None or score >= -0.2):
        return {
            "badge": "🛡️ 稳妥",
            "tag": "evergreen",
            "summary": "泛用万金油符文，容错率高、发挥稳定"
        }

    # 陷阱提示 (负 Lift 且胜率低)
    if score is not None and score <= -1.8 and (games or 0) >= 300:
        return {
            "badge": "⚠️ 陷阱",
            "tag": "trap",
            "summary": f"版本陷阱！相比该英雄基准降低 {abs(score):.1f}pp，建议刷新"
        }

    # 普通平庸 / 局数少
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

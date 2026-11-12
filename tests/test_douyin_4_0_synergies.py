# -*- coding: utf-8 -*-
"""
验证抖音 4.0 绝活攻略规则库与出装联动
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lolhex import synergy
from lolhex import recommend

def test_volibear_bee_synergy():
    # 沃利贝尔 + 小蜜蜂
    hint = synergy.get_synergy_item_hint(None, "106", "3086")
    assert hint is not None
    assert "小蜜蜂连锁雷暴流" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3087" in item_ids  # 电刀
    assert "3115" in item_ids  # 纳什之牙

def test_caitlyn_bigshot_synergy():
    # 凯特琳 + 大腕
    hint = synergy.get_synergy_item_hint(None, "51", "3018")
    assert hint is not None
    assert "颗秒" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3031" in item_ids  # 无尽之刃
    assert "6676" in item_ids  # 收集者

def test_hecarim_bass_synergy():
    # 赫卡里姆 + 低音轰鸣
    hint = synergy.get_synergy_item_hint(None, "120", "3078")
    assert hint is not None
    assert "低音轰鸣" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6697" in item_ids  # 狂妄
    assert "3161" in item_ids  # 朔极之矛

def test_kassadin_blue_barrier_synergy():
    # 卡萨丁 + 蓝色屏障
    hint = synergy.get_synergy_item_hint(None, "38", "3051")
    assert hint is not None
    assert "蓝色巨盾" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3003" in item_ids or "3027" in item_ids

def test_yi_titan_synergy():
    # 剑圣 + 泰坦的坚决
    hint = synergy.get_synergy_item_hint(None, "11", "1001")
    assert hint is not None
    assert "肉身成圣" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3065" in item_ids  # 振奋

def test_zhaoxin_super_evil_synergy():
    # 赵信 + 超凡邪恶
    hint = synergy.get_synergy_item_hint(None, "5", "1390")
    assert hint is not None
    assert "抽血泵" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3087" in item_ids  # 电刀
    assert "3089" in item_ids  # 帽子

def test_yasuo_armor_impact_synergy():
    # 亚索 + 装甲冲击
    hint = synergy.get_synergy_item_hint(None, "157", "3049")
    assert hint is not None
    assert "纯肉装甲冲击流" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3110" in item_ids  # 冰霜之心
    assert "3075" in item_ids  # 荆棘之甲

def test_kaisa_bee_synergy():
    # 卡莎 + 小蜜蜂
    hint = synergy.get_synergy_item_hint(None, "145", "3086")
    assert hint is not None
    assert "双电浆" in hint["title"]

def test_jinx_dual_wield_synergy():
    # 金克丝 + 双刀流
    hint = synergy.get_synergy_item_hint(None, "222", "1225")
    assert hint is not None
    assert "双刀" in hint["title"]

def test_tier_classifier_4_0():
    tier_bee = synergy.classify_augment_tier(None, "106", "3086", 0.55, 3.0, 500)
    assert tier_bee["badge"] == "🌟 核心"
    assert "小蜜蜂" in tier_bee["summary"]

    tier_bass = synergy.classify_augment_tier(None, "120", "3078", 0.62, 5.0, 600)
    assert tier_bass["badge"] == "🌟 核心"
    assert "低音轰鸣" in tier_bass["summary"]

def test_udyr_xiao_tiandi_synergy():
    # 乌迪尔 + 回归基本功
    hint = synergy.get_synergy_item_hint(None, "77", "1004")
    assert hint is not None
    assert "萧天帝" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3115" in item_ids
    assert "3089" in item_ids

def test_rammus_protein_synergy():
    # 拉莫斯 + 蛋白粉奶昔
    hint = synergy.get_synergy_item_hint(None, "33", "1324")
    assert hint is not None
    assert "蛋白粉" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3302" in item_ids
    assert "3124" in item_ids

def test_gragas_chain_reaction_synergy():
    # 古拉加斯 + 连锁反应
    hint = synergy.get_synergy_item_hint(None, "79", "2078")
    assert hint is not None
    assert "连锁核弹" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6656" in item_ids

def test_viktor_sniper_synergy():
    # 维克托 + 老练狙神
    hint = synergy.get_synergy_item_hint(None, "112", "1113")
    assert hint is not None
    assert "老练狙神" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6655" in item_ids

def test_rengar_archmage_synergy():
    # 雷恩加尔 + 大法师
    hint = synergy.get_synergy_item_hint(None, "107", "2087")
    assert hint is not None
    assert "大法师" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3065" in item_ids

def test_tryndamere_axiom_synergy():
    # 泰达米尔 + 奥术公理
    hint = synergy.get_synergy_item_hint(None, "23", "3118")
    assert hint is not None
    assert "真男人" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6675" in item_ids

def test_shaco_academy_synergy():
    # 萨科 + 小丑学院
    hint = synergy.get_synergy_item_hint(None, "35", "1310")
    assert hint is not None
    assert "小丑学院" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3118" in item_ids

def test_fizz_takedown_synergy():
    # 菲兹 + 将他们放倒倒倒
    hint = synergy.get_synergy_item_hint(None, "105", "3116")
    assert hint is not None
    assert "炽燃穿梭" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3100" in item_ids

def test_kayle_punch_synergy():
    # 凯尔 + 秘术冲拳
    hint = synergy.get_synergy_item_hint(None, "10", "1058")
    assert hint is not None
    assert "冲拳无限无敌" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3115" in item_ids

def test_nasus_hydra_synergy():
    # 内瑟斯 + 升级：贪欲九头蛇
    hint = synergy.get_synergy_item_hint(None, "75", "2140")
    assert hint is not None
    assert "五重顺劈" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3074" in item_ids

def test_nunu_circle_of_death_synergy():
    # 努努 + 死亡之环
    hint = synergy.get_synergy_item_hint(None, "20", "1015")
    assert hint is not None
    assert "死亡之环" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3065" in item_ids

def test_belveth_takedown_synergy():
    # 卑尔维斯 + 将他们放倒倒倒
    hint = synergy.get_synergy_item_hint(None, "200", "3116")
    assert hint is not None
    assert "极限千击万仞" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6672" in item_ids

def test_twisted_fate_destiny_weapon_synergy():
    # 崔斯特 + 命运之武器
    hint = synergy.get_synergy_item_hint(None, "4", "3081")
    assert hint is not None
    assert "命运之武器" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6695" in item_ids

def test_tristana_infusion_synergy():
    # 崔丝塔娜 + 注魔
    hint = synergy.get_synergy_item_hint(None, "18", "2016")
    assert hint is not None
    assert "注魔AP核弹" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3115" in item_ids

def test_new_augment_combos_evaluation():
    # 联动分已由机制推导（类型 × 耦合度），不再用攻略视频拍的手工值
    # 死亡之环 (1015) + 易损 (1092)：乘算，但机制向量零共享 → 人工确认档 0.5 → 6.0×0.5
    eval_res = synergy.evaluate_combo_synergies("1015", ["1092"])
    assert eval_res["bonus"] == 3.0
    assert any("死亡飞弹连锁风暴" in r for r in eval_res["reasons"])

    # 小蜜蜂 (3086) + 虚幻武器 (1029)：共享攻击特效满耦合 → 频次放大 5.5
    eval_res2 = synergy.evaluate_combo_synergies("3086", ["1029"])
    assert eval_res2["bonus"] == 5.5
    assert any("蜜蜂虚幻全额引爆" in r for r in eval_res2["reasons"])

    # 升级贪欲九头蛇 (2140) + 钢化你心 (1152)：堆血线性叠加，耦合 0.4 → 2.5×0.4
    eval_res3 = synergy.evaluate_combo_synergies("2140", ["1152"])
    assert eval_res3["bonus"] == 1.0
    assert any("巨人体魄顺劈狂澜" in r for r in eval_res3["reasons"])

def test_blitzcrank_archmage_synergy():
    # 布里茨 + 大法师 (2087)
    hint = synergy.get_synergy_item_hint(None, "53", "2087")
    assert hint is not None
    assert "大法师无限R" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6655" in item_ids  # 卢登
    assert "4645" in item_ids  # 影焰

def test_jhin_tap_dance_synergy():
    # 烬 + 踢踏舞 (1081)
    hint = synergy.get_synergy_item_hint(None, "202", "1081")
    assert hint is not None
    assert "瘸天帝" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3094" in item_ids  # 火炮
    assert "3031" in item_ids  # 无尽

def test_gangplank_archmage_synergy():
    # 普朗克 + 大法师 (2087)
    hint = synergy.get_synergy_item_hint(None, "41", "2087")
    assert hint is not None
    assert "大法师无限大" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3031" in item_ids  # 无尽
    assert "6676" in item_ids  # 收集者

def test_jayce_sniper_synergy():
    # 杰斯 + 最万用的瞄准镜 (1115)
    hint = synergy.get_synergy_item_hint(None, "126", "1115")
    assert hint is not None
    assert "千码瞄准" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3031" in item_ids

def test_ashe_archmage_synergy():
    # 艾希 + 大法师 (2087)
    hint = synergy.get_synergy_item_hint(None, "22", "2087")
    assert hint is not None
    assert "泉水指挥官" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6655" in item_ids

def test_tahmkench_mirage_synergy():
    # 塔姆 + 虚幻武器 (1029)
    hint = synergy.get_synergy_item_hint(None, "223", "1029")
    assert hint is not None
    assert "三重被动" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3084" in item_ids  # 心之钢

def test_ryze_overload_synergy():
    # 瑞兹 + 超负荷 (2123)
    hint = synergy.get_synergy_item_hint(None, "13", "2123")
    assert hint is not None
    assert "超负荷法术加特林" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3003" in item_ids

def test_brand_enpassant_synergy():
    # 布兰德 + 吃过路兵 (2098)
    hint = synergy.get_synergy_item_hint(None, "63", "2098")
    assert hint is not None
    assert "过路兵全向破绽" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6653" in item_ids  # 面具

def test_ornn_magic_synergy():
    # 奥恩 + 精怪魔法 (1194)
    hint = synergy.get_synergy_item_hint(None, "516", "1194")
    assert hint is not None
    assert "精怪魔法重装爆轰" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "8020" in item_ids  # 深渊面具

def test_senna_mirage_synergy():
    # 赛娜 + 虚幻武器 (1029)
    hint = synergy.get_synergy_item_hint(None, "235", "1029")
    assert hint is not None
    assert "隔空叠魂" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3087" in item_ids  # 电刀

def test_mordekaiser_conduit_synergy():
    # 莫德凯撒 + 炼狱导管 (1045)
    hint = synergy.get_synergy_item_hint(None, "82", "1045")
    assert hint is not None
    assert "导管圣火领域" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3116" in item_ids  # 冰杖

def test_jarvan_terrain_synergy():
    # 嘉文四世 + 地形专家 (2129)
    hint = synergy.get_synergy_item_hint(None, "59", "2129")
    assert hint is not None
    assert "地形专家自爆AP皇子" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "6656" in item_ids

def test_vayne_rapid_fire_synergy():
    # 薇恩 + 双发快射 (2010)
    hint = synergy.get_synergy_item_hint(None, "67", "2010")
    assert hint is not None
    assert "双发快射破败十六环" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3153" in item_ids  # 破败

def test_garen_quickstride_synergy():
    # 盖伦 + 快步 (2064)
    hint = synergy.get_synergy_item_hint(None, "86", "2064")
    assert hint is not None
    assert "快步双突进挺进旋转" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3078" in item_ids

def test_sylas_sniper_mage_synergy():
    # 塞拉斯 + 神射法师 (1129)
    hint = synergy.get_synergy_item_hint(None, "517", "1129")
    assert hint is not None
    assert "神射暴击邪修" in hint["title"]
    item_ids = [x["item"] for x in hint["items"]]
    assert "3031" in item_ids  # 无尽

def test_combos_26_to_31_evaluation():
    # 联动分为机制推导值（类型 × 耦合度），断言即算分公式的预期
    # 26. 叠角龙 (1204) + 钢化你心 (1152)：堆血线性叠加满耦合 1.0 → 2.5
    res26 = synergy.evaluate_combo_synergies("1204", ["1152"])
    assert res26["bonus"] == 2.5
    assert any("叠角狂澜八倍叠钢" in r for r in res26["reasons"])

    # 27. 超凡邪恶 (1390) + 尤里卡 (1030)：法强/急速资源转化满耦合 → 5.0
    res27 = synergy.evaluate_combo_synergies("1390", ["1030"])
    assert res27["bonus"] == 5.0
    assert any("邪恶尤里卡法神永动" in r for r in res27["reasons"])

    # 28. 双发快射 (2010) + 秘术冲拳 (1058)：频次满耦合 → 5.5
    res28 = synergy.evaluate_combo_synergies("2010", ["1058"])
    assert res28["bonus"] == 5.5
    assert any("双发冲拳极速刷招" in r for r in res28["reasons"])

    # 29. 踢踏舞 (1081) + 全凭身法 (1019)：频次满耦合 → 5.5
    res29 = synergy.evaluate_combo_synergies("1081", ["1019"])
    assert res29["bonus"] == 5.5
    assert any("踢踏身法万速天帝" in r for r in res29["reasons"])

    # 30. 地形专家 (2129) + 面包和奶酪 (1151)：资源转化，耦合 0.8 → 4.0
    res30 = synergy.evaluate_combo_synergies("2129", ["1151"])
    assert res30["bonus"] == 4.0
    assert any("地形封路无限领域" in r for r in res30["reasons"])

    # 31. 高压锅 (2102) + 巨像的勇气 (1018)：堆血线性叠加 → 2.5
    res31 = synergy.evaluate_combo_synergies("2102", ["1018"])
    assert res31["bonus"] == 2.5
    assert any("高压巨像全域熔炉" in r for r in res31["reasons"])


def test_nov12_douyin_round_new_combos_and_pivots(store):
    # 单曲红人 (3060) + 纯粹主义者 (2018)：资源转化满耦合
    c1 = synergy.evaluate_combo_synergies("3060", ["2018"])
    assert c1["bonus"] == 5.0
    assert any("单曲纯粹轰天炮" in r for r in c1["reasons"])

    # 深红钴蓝闪光 (3088) + 虚幻武器 (1029)：频次放大高耦合（共享 on_hit + cdr ≈ 0.9 → 5.0）
    c2 = synergy.evaluate_combo_synergies("3088", ["1029"])
    assert c2["bonus"] == 5.0
    assert any("红蓝虚幻无限火力" in r for r in c2["reasons"])

    # 迷人蝴蝶 (3163) + 蛋白粉奶昔 (1324)：治疗护盾资源转化
    c3 = synergy.evaluate_combo_synergies("3163", ["1324"])
    assert c3["bonus"] > 0
    assert any("蛋白蝴蝶核弹流" in r for r in c3["reasons"])

    # 珠光护手 (1048) + 大腕 (3018)：乘算双修爆伤
    c4 = synergy.evaluate_combo_synergies("1048", ["3018"])
    assert c4["bonus"] > 0
    assert any("大腕法爆核弹" in r for r in c4["reasons"])

    # 由心及物 (1056) + 巫妖大脑 (3094)：半神瑞天帝双转化
    c5 = synergy.evaluate_combo_synergies("1056", ["3094"])
    assert c5["bonus"] > 0
    assert any("半神瑞天帝双转化" in r for r in c5["reasons"])

    # 装甲冲击 (3049) + 泰坦的坚决 (1001)：避坑负联动警告
    cf = synergy.evaluate_combo_synergies("3049", ["1001"])
    assert cf["penalty"] == -3.5
    assert any("泰坦的坚决" in r for r in cf["conflicts"])

    # 弹跳蜜蜂 (3048) 与新版命运之武器 (3081) 锚点装备
    assert "3048" in synergy.AUGMENT_PIVOT_ANCHORS
    b_bee = synergy.get_augment_core_items("3048", store)
    assert any(x["id"] == "2517" for x in b_bee)
    b_destiny = synergy.get_augment_core_items("3081", store)
    assert any(x["id"] == "2517" for x in b_destiny)

    # 亚恒 (904) 与 菲奥娜 (114) 更新后流派档案
    rb_zaahen = synergy.get_hero_rune_build("904", ["3078"], store)
    assert rb_zaahen["is_rune_adapted"] is True
    assert len(rb_zaahen["full_six_items"]) == 6
    rb_fiora = synergy.get_hero_rune_build("114", ["3078"], store)
    assert rb_fiora["is_rune_adapted"] is True
    assert any(x["id"] == "2517" for x in rb_fiora["items"])

    # 联盟张三新增：手镯+大腕 (3123+3018)、嗡嗡+纯粹 (3058+2018)、男枪/EZ/纳尔档案、登峰造极境/王冠之重
    c_zw = synergy.evaluate_combo_synergies("3123", ["3018"])
    assert c_zw["bonus"] > 0 and any("手镯大腕核弹R" in r for r in c_zw["reasons"])
    c_bp = synergy.evaluate_combo_synergies("3058", ["2018"])
    assert c_bp["bonus"] > 0 and any("嗡嗡纯粹急速流" in r for r in c_bp["reasons"])
    assert "3159" in synergy.AUGMENT_PIVOT_ANCHORS
    assert "3132" in synergy.AUGMENT_PIVOT_ANCHORS
    assert synergy.get_hero_rune_build("104", ["3123"], store)["is_rune_adapted"] is True
    assert synergy.get_hero_rune_build("81", ["3048"], store)["is_rune_adapted"] is True
    assert synergy.get_hero_rune_build("150", ["3086"], store)["is_rune_adapted"] is True




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

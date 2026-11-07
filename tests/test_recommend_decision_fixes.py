# -*- coding: utf-8 -*-
"""推荐与决策层修复的回归测试（2026-11 review）：

1. 联动加分递减 + 封顶，不能无限叠盖过实测胜率差；
2. 「核心」徽章必须有实测数据支撑，静态绝活表只提供解读文案；
3. 「样本偏少」只影响首选资格，分数差的薄样本卡照样标「建议刷新」；
4. 徽章判定用全体局数口径和联动加权前的分数；
5. 三选一关闭时的自动已持记录是推测：快速出现新一组（刷新）要撤回，隔得久才转正。
"""
import time

import pytest

from lolhex import recommend, synergy
from lolhex.config import Settings
from lolhex.engine import Engine


# ---------- 1. 联动加分递减 + 封顶 ----------

def test_combo_bonus_diminishing_and_capped():
    # 单组联动保持机制推导值（珠光×易损：乘算满耦合 6.0）
    single = synergy.evaluate_combo_synergies("1092", ["1048"])
    assert single["bonus"] == 6.0

    # 多组联动：最大一组全额，其余按 30% 计入，且总量封顶不超过单组最大值
    stacked = synergy.evaluate_combo_synergies("1092", ["1048", "3123", "1015"])
    assert len(stacked["reasons"]) == 3  # 三组联动理由都还在
    assert stacked["bonus"] == synergy.COMBO_BONUS_CAP
    assert stacked["bonus"] <= 8.0  # 修复前这里是 19.5pp，足以让任何实测陷阱卡当首选

    # 两组：6.0 + 0.3 × 6.0
    two = synergy.evaluate_combo_synergies("1092", ["1048", "3123"])
    assert two["bonus"] == pytest.approx(min(8.0, 6.0 + 0.3 * 6.0), 0.01)


# ---------- 2. 徽章必须数据驱动 ----------

def test_core_badge_requires_data():
    # 静态绝活表里的符文、但完全没有数据：不能给「核心」，只给解读文案
    nodata = synergy.classify_augment_tier(None, "106", "3086", None, None, None)
    assert nodata["tag"] == "normal"
    assert "小蜜蜂" in nodata["summary"]  # 机制解读仍然展示

    # 小样本也不够核心门槛
    thin = synergy.classify_augment_tier(None, "106", "3086", 0.55, 3.0, 100)
    assert thin["tag"] != "core"

    # 有数据支撑（大样本高 Lift）仍然是核心，且带绝活解读
    core = synergy.classify_augment_tier(None, "106", "3086", 0.55, 3.0, 500)
    assert core["tag"] == "core"
    assert "小蜜蜂" in core["summary"]

    # 实测陷阱：就算在静态绝活表里，徽章也必须按数据说成陷阱
    trap = synergy.classify_augment_tier(None, "106", "3086", 0.44, -2.5, 800)
    assert trap["tag"] == "trap"


# ---------- 3 / 4. verdict 顺序与徽章口径 ----------

def _teemo_rows(store, games, wins):
    ids = ["2128", "1029", "1373"]
    rows = store.dataset.table(None)[1]["17"]
    for aid, n, win in zip(ids, games, wins):
        rows[aid] = {"games": n, "wins": round(n * win), "win_rate": win}
    return ids


def test_thin_few_with_bad_score_is_reroll_not_ok(store):
    # 999 局的「few」薄样本卡分数很差：修复前因为 thin 分支被一律标「可选」
    ids = _teemo_rows(store, [3000, 999, 2000], [.55, .40, .53])
    ev = recommend.evaluate(store, "17", ids)
    thin_row = ev["slots"][1]
    assert thin_row.get("thin") == "few"
    assert thin_row["verdict"] == "reroll"
    # 分数好的薄样本卡仍然只是不作首选、标「可选」
    ids = _teemo_rows(store, [3000, 999, 2000], [.55, .62, .53])
    ev = recommend.evaluate(store, "17", ids)
    thin_row = ev["slots"][1]
    assert thin_row.get("thin") == "few"
    assert thin_row["verdict"] == "ok"


def test_badge_uses_score_before_synergy(store):
    # 1058 自身实测是陷阱（大样本 -1.9pp），被已持 1225 的联动 +7.0 加回正分。
    # 徽章看符文自身强度：必须用联动加权前的分数，不能跟着加权变成「核心」。
    ids = ["1058", "1029", "2128"]
    rows = store.dataset.table(None)[1]["17"]
    rows["1058"] = {"games": 30000, "wins": round(30000 * .51), "win_rate": .51}
    ev = recommend.evaluate(store, "17", ids, acquired_augments=["1225"])
    slot = ev["slots"][0]
    assert slot["combo_synergy"]["bonus"] == synergy.evaluate_combo_synergies("1058", ["1225"])["bonus"]
    assert slot["score"] > 0  # 折算后的联动分把它从负分拉回正分
    assert slot["decision_tag"] == "trap"  # 但徽章按加权前的 -1.9pp 判定
    # 1029 自身大样本高 Lift：徽章口径用全体局数，是核心
    assert ev["slots"][1]["decision_tag"] == "core"


# ---------- 5. 推测已持记录的撤回与转正 ----------

def _engine_with_offer(store, tmp_path):
    eng = Engine(Settings(), home=tmp_path, store=store)
    eng.state["hero_id"] = "17"
    eng.state["phase"] = "ingame"
    eng.state["acquired_augments"] = []
    from lolhex.vision.detector import Offer
    offer = Offer(["1058", "1029", "2128"], [], [], [None] * 3)
    eng._on_offer(offer)
    eng._on_offer(None)  # 三选一关闭：推测记录首选 1029
    assert eng.state["acquired_augments"] == ["1029"]
    return eng, Offer


def test_reroll_withdraws_speculative_record(store, tmp_path):
    eng, Offer = _engine_with_offer(store, tmp_path)
    # 关闭后立刻出现新一组：刚才是在刷新，撤回误记
    eng._on_offer(Offer(["2128", "1373", "1058"], [], [], [None] * 3))
    assert eng.state["acquired_augments"] == []
    assert eng.state["_acquired_guess"] is None


def test_pick_confirmed_after_withdraw_window(store, tmp_path):
    eng, Offer = _engine_with_offer(store, tmp_path)
    # 超过撤回窗口才出现新一组：玩家已经选完，记录转正
    eng.state["_acquired_guess"]["at"] = time.monotonic() - eng.ACQUIRED_GUESS_WITHDRAW_S - 1
    eng._on_offer(Offer(["2128", "1373", "1058"], [], [], [None] * 3))
    assert eng.state["acquired_augments"] == ["1029"]
    assert eng.state["_acquired_guess"] is None


def test_manual_record_confirms_guess(store, tmp_path):
    eng, Offer = _engine_with_offer(store, tmp_path)
    # 玩家手动确认过同一个符文：即使快速刷新也不撤回
    eng.record_acquired_augment("1029")
    assert eng.state["_acquired_guess"] is None
    eng._on_offer(Offer(["2128", "1373", "1058"], [], [], [None] * 3))
    assert eng.state["acquired_augments"] == ["1029"]

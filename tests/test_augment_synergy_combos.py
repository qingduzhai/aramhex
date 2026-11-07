# -*- coding: utf-8 -*-
import pytest
from lolhex import recommend, synergy
from lolhex.engine import Engine
from lolhex.config import Settings


def test_evaluate_combo_synergies_bonus_and_items():
    # 珠光护手 (1048) + 易损 (1092) -> 天命双法爆
    # 算分：乘算 6.0 × 满耦合（共享 暴击爆发/法强 min 权重和 1.5，截断到 1.0）= +6.0
    res = synergy.evaluate_combo_synergies("1092", ["1048"])
    assert res["bonus"] == 6.0
    assert res["penalty"] == 0.0
    assert res["net_score"] == 6.0
    assert any("天命双法爆" in r for r in res["reasons"])
    assert any("乘算" in r for r in res["reasons"])
    assert any(it["name"] == "无尽之刃" for it in res["core_items"])
    assert any(it["name"] == "影焰" for it in res["core_items"])


def test_evaluate_combo_synergies_conflict():
    # 大腕 (3018) + 双刀流 (1225) -> 机制冲突 (-5.0 penalty)
    res = synergy.evaluate_combo_synergies("1225", ["3018"])
    assert res["penalty"] == -5.0
    assert res["bonus"] == 0.0
    assert res["net_score"] == -5.0
    assert any("大腕" in c and "双刀流" in c for c in res["conflicts"])


def test_get_augment_core_items_and_build_advice():
    # 小蜜蜂 (3086) 专属锚点装备
    core_items = synergy.get_augment_core_items("3086")
    assert len(core_items) >= 2
    assert any(it["name"] == "斯塔缇克电刃" for it in core_items)

    # 局内已持符文出装建议
    advice = synergy.get_acquired_augments_build_advice(["1048", "1092"])
    assert len(advice) >= 2
    assert any("天命双法爆" in it.get("source", "") for it in advice)


def test_recommend_evaluate_with_acquired_augments_nodata_augmented(store):
    # Candidate slots: 易损 (1092)
    slots = ["1092", "1029", "2128"]

    # Baseline evaluation without acquired augments: 1092 has no base stats
    ev_base = recommend.evaluate(store, "17", slots, acquired_augments=[])
    assert ev_base["slots"][0]["score"] is None

    # 已持珠光护手 (1048) 时，1092 命中「天命双法爆」组合；但 1092 在本英雄/全服统计里一局都没有，
    # 属「新海克斯无数据」：联动只展示、不计分，零数据的卡不能靠手工组合表当上首选。
    ev_synergy = recommend.evaluate(store, "17", slots, acquired_augments=["1048"])
    slot_synergy = ev_synergy["slots"][0]

    assert slot_synergy["verdict"] == "nodata"
    assert slot_synergy["score"] is None
    assert slot_synergy["combo_synergy"]["bonus"] == 6.0
    assert any("不计分" in r for r in slot_synergy["reasons"])
    assert any("天命双法爆" in r for r in slot_synergy["reasons"])
    assert len(slot_synergy["must_buy_items"]) > 0
    assert any(it["name"] == "无尽之刃" for it in slot_synergy["must_buy_items"])
    # 首选仍然是有实测数据的 1029（虚幻武器），而不是零数据的组合卡
    assert ev_synergy["slots"][1]["verdict"] == "best"
    assert "联动加权推荐" not in ev_synergy["advice"]


def test_recommend_evaluate_with_acquired_augments_tiered(store):
    # 安妮（纯法师）候选虚幻武器 (1029)，已持小蜜蜂 (3086) -> 蜜蜂虚幻全额引爆（表值 +7.5）。
    # 1029 的攻击特效机制和安妮不契合：联动分按机制契合折算后计入，不给全额。
    slots = ["1029", "2128", "1373"]

    ev_base = recommend.evaluate(store, "1", slots, acquired_augments=[])
    score_base = ev_base["slots"][0]["score"]
    assert score_base is not None

    ev_synergy = recommend.evaluate(store, "1", slots, acquired_augments=["3086"])
    slot_synergy = ev_synergy["slots"][0]

    from lolhex import fit
    gate = fit.combo_gate("1029", "1")
    raw = synergy.evaluate_combo_synergies("1029", ["3086"])["bonus"]
    applied = round(raw * gate, 2)
    assert 0 < gate < 1  # 安妮不是普攻流派：联动分折算
    assert slot_synergy["score"] == pytest.approx(score_base + applied, 0.01)
    assert slot_synergy["combo_synergy"]["bonus"] == raw  # 机制推导的原始分保留
    assert slot_synergy["combo_synergy"]["applied_score"] == applied
    assert any("蜜蜂虚幻全额引爆" in r for r in slot_synergy["reasons"])
    assert any("机制契合折算" in r for r in slot_synergy["reasons"])
    assert any(it["name"] == "斯塔缇克电刃" for it in slot_synergy["must_buy_items"])


def test_engine_acquired_augments_state_and_clear(store, tmp_path):
    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["hero_id"] = "17"
    eng.state["offer"] = {"slots": ["1058", "1029", "2128"]}
    eng.state["phase"] = "ingame"

    # Initially empty
    assert eng.state["acquired_augments"] == []
    
    # Record augment
    eng.record_acquired_augment("1225")
    assert eng.state["acquired_augments"] == ["1225"]
    assert eng.snapshot()["acquired_augments"] == ["1225"]
    
    # Evaluation should reflect synergy
    ev = eng.state.get("evaluation")
    assert ev is not None
    assert ev["slots"][0]["combo_synergy"]["bonus"] == synergy.evaluate_combo_synergies("1058", ["1225"])["bonus"]

    # Record second augment
    eng.record_acquired_augment("3086")
    assert eng.state["acquired_augments"] == ["1225", "3086"]

    # Remove first augment
    eng.remove_acquired_augment(0)
    assert eng.state["acquired_augments"] == ["3086"]

    # Clear augments
    eng.clear_acquired_augments()
    assert eng.state["acquired_augments"] == []

    # Clear on game end
    eng.record_acquired_augment("1225")
    assert len(eng.state["acquired_augments"]) == 1
    eng._on_game_end()
    assert eng.state["acquired_augments"] == []


def test_get_hero_rune_build(store):
    # Volibear empty augments: preparatory build
    b_empty = synergy.get_hero_rune_build("106", [], store)
    assert b_empty["is_rune_adapted"] is False
    assert len(b_empty["items"]) == 5
    assert "预备" in b_empty["status_label"]

    # Volibear with 3086 (Beehive): specialized dual playstyle
    b_bee = synergy.get_hero_rune_build("106", ["3086"], store)
    assert b_bee["is_rune_adapted"] is True
    assert "小蜜蜂" in b_bee["build_name"]
    assert any("电刃" in it["name"] for it in b_bee["items"])
    assert any("破败" in it["name"] for it in b_bee["items"])

    # Combo pair: 1048 (珠光护手) + 1092 (易损)
    b_combo = synergy.get_hero_rune_build("51", ["1048", "1092"], store)
    assert b_combo["is_rune_adapted"] is True
    assert any(term in b_combo["build_name"] for term in ["法爆", "双法爆", "天命", "暴"])


def test_engine_auto_record_on_offer_close(store, tmp_path):
    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["hero_id"] = "17"
    eng.state["phase"] = "ingame"
    eng.state["acquired_augments"] = []

    from lolhex.vision.detector import Offer
    mock_offer = Offer(["1058", "1029", "2128"], [], [], [None]*3)
    eng._on_offer(mock_offer)
    assert eng.state["offer"] is not None
    assert eng.state["evaluation"] is not None

    eng._on_offer(None)
    assert eng.state["offer"] is None
    assert len(eng.state["acquired_augments"]) == 1
    assert eng.state["acquired_augments"][0] == "1029"


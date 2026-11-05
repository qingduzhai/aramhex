# -*- coding: utf-8 -*-
import pytest
from lolhex import recommend, synergy
from lolhex.engine import Engine
from lolhex.config import Settings


def test_evaluate_combo_synergies_bonus_and_items():
    # 珠光护手 (1048) + 易损 (1092) -> 天命双法爆 (+7.5 bonus)
    res = synergy.evaluate_combo_synergies("1092", ["1048"])
    assert res["bonus"] == 7.5
    assert res["penalty"] == 0.0
    assert res["net_score"] == 7.5
    assert any("天命双法爆" in r for r in res["reasons"])
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

    # Evaluation with 珠光护手 (1048) acquired: 1092 gets synergy score of 7.5
    ev_synergy = recommend.evaluate(store, "17", slots, acquired_augments=["1048"])
    slot_synergy = ev_synergy["slots"][0]
    
    assert slot_synergy["score"] == 7.5
    assert slot_synergy["combo_synergy"]["bonus"] == 7.5
    assert any("天命双法爆" in r for r in slot_synergy["reasons"])
    assert len(slot_synergy["must_buy_items"]) > 0
    assert any(it["name"] == "无尽之刃" for it in slot_synergy["must_buy_items"])
    assert "联动加权推荐" in ev_synergy["advice"]


def test_recommend_evaluate_with_acquired_augments_tiered(store):
    # 秘术冲拳 (1058) in slots, and 双刀流 (1225) acquired -> 双刀极限连打 (+7.0)
    slots = ["1058", "1029", "2128"]
    
    ev_base = recommend.evaluate(store, "17", slots, acquired_augments=[])
    score_base = ev_base["slots"][0]["score"]
    assert score_base is not None

    ev_synergy = recommend.evaluate(store, "17", slots, acquired_augments=["1225"])
    slot_synergy = ev_synergy["slots"][0]
    
    assert slot_synergy["score"] == pytest.approx(score_base + 7.0, 0.01)
    assert slot_synergy["combo_synergy"]["bonus"] == 7.0
    assert any("双刀极限连打" in r for r in slot_synergy["reasons"])
    assert any(it["name"] == "破败王者之刃" for it in slot_synergy["must_buy_items"])


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
    assert ev["slots"][0]["combo_synergy"]["bonus"] == 7.0

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

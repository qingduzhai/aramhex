# -*- coding: utf-8 -*-
import pytest
from lolhex import synergy
from lolhex.engine import Engine
from lolhex.config import Settings


def test_derive_mechanic_build_various_types(store):
    # 1013: 星界躯体 (生命成长) on Darius (122)
    res_tank = synergy.derive_mechanic_build("1013", "122", store)
    assert res_tank is not None
    arch, name, mech, expl = res_tank
    assert arch == "Tank_Frontline"
    assert "肉坦" in name
    assert mech == "hp"

    # 1022: 灵巧 (普攻特效/攻速) on Jinx (222)
    res_onhit = synergy.derive_mechanic_build("1022", "222", store)
    assert res_onhit is not None
    arch, name, mech, expl = res_onhit
    assert arch == "ADC_Hybrid_OnHit"
    assert "特效攻速" in name

    # 1048: 珠光护手 (法术暴击/爆发) on Lux (99)
    res_ap = synergy.derive_mechanic_build("1048", "99", store)
    assert res_ap is not None
    arch, name, mech, expl = res_ap
    assert arch == "AP_Burst_Poke"
    assert "法" in name

    # 1151: 面包和奶酪 (急速) on Zed (238)
    res_cdr = synergy.derive_mechanic_build("1151", "238", store)
    assert res_cdr is not None
    arch, name, mech, expl = res_cdr
    assert arch == "AD_Spellcaster_Poke"
    assert "技能" in name


def test_get_hero_rune_build_dynamic_item_pivot(store):
    # 1013 on Darius (122) should dynamically transform recommended items to Tank (Heartsteel)
    res = synergy.get_hero_rune_build("122", ["1013"], store)
    assert res["is_rune_adapted"] is True
    item_names = [it["name"] for it in res["items"]]
    assert "心之钢" in item_names
    assert "巨神" in res["build_name"]

    # 1022 on Jinx (222) should dynamically transform recommended items to OnHit (BotRK / Kraken)
    res_jinx = synergy.get_hero_rune_build("222", ["1022"], store)
    assert res_jinx["is_rune_adapted"] is True
    jinx_items = [it["name"] for it in res_jinx["items"]]
    assert any(x in jinx_items for x in ("破败王者之刃", "海妖杀手", "鬼索的狂暴之刃"))


def test_engine_record_acquired_augment_switch_and_offer_close(tmp_path, store):
    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["phase"] = "ingame"
    eng.state["hero_id"] = "122"
    eng.state["offer"] = {"slots": ["1013", "1022", "1048"]}
    eng.state["evaluation"] = {
        "slots": [
            {"verdict": "ok", "augment_id": "1013"},
            {"verdict": "ok", "augment_id": "1022"},
            {"verdict": "best", "augment_id": "1048"},
        ]
    }

    # Player clicks slot 1 (1022)
    eng.record_acquired_augment("1022")
    assert eng.state["acquired_augments"] == ["1022"]

    # Player changes mind within the same offer and clicks slot 0 (1013)
    eng.record_acquired_augment("1013")
    assert eng.state["acquired_augments"] == ["1013"], "Should replace choice within same offer"

    # Offer closes: engine._on_offer(None)
    eng._on_offer(None)

    # Acquired augments must NOT append the default 'best' 1048
    assert eng.state["acquired_augments"] == ["1013"], "Explicit pick must prevent best_slot guess on close"


def test_control_panel_pick_slot_toggle(store, tmp_path):
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from lolhex.ui.overlay import ControlPanel

    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["phase"] = "ingame"
    eng.state["hero_id"] = "122"
    eng.state["offer"] = {"slots": ["1013", "1022", "1048"]}
    eng.state["evaluation"] = {
        "slots": [
            {"verdict": "ok", "augment_id": "1013", "name": "星界躯体"},
            {"verdict": "ok", "augment_id": "1022", "name": "灵巧"},
            {"verdict": "best", "augment_id": "1048", "name": "珠光护手"},
        ]
    }

    cp = ControlPanel(eng)
    try:
        # Click slot 0 (1013)
        cp._link("pick_slot:0")
        assert eng.state["acquired_augments"] == ["1013"]

        # Click slot 0 again -> toggle off (deselect)
        cp._link("pick_slot:0")
        assert eng.state["acquired_augments"] == []

        # Click slot 1 (1022)
        cp._link("pick_slot:1")
        assert eng.state["acquired_augments"] == ["1022"]
    finally:
        cp.close()

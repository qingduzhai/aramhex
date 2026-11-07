# -*- coding: utf-8 -*-
"""机制契合层（fit.py）测试：

1. 先验方向：攻击特效型符文对普攻特效英雄高契合、对纯法师几乎为零；
2. 绝活档案是英雄级覆盖（狗熊是坦克流派，被动攻击特效契合小蜜蜂）；
3. 先验随局数淡出，大样本完全由实测数据说了算（不和英雄×符文胜率重复计算）；
4. 联动分按契合度折算；
5. 「几乎不选」兜底：机制先验 + 全服Δ折算，只减不加分。
"""
import pytest

from lolhex import fit, recommend


def test_fit_direction_onhit_vs_mage():
    f_on, note_on = fit.fit_adjustment("3086", "96")   # 大嘴：攻击特效攻速流
    f_off, _ = fit.fit_adjustment("3086", "37")        # 琴女：纯法师
    assert f_on >= 1.0 and "攻击特效" in note_on
    assert f_off <= 0.2
    # 从未收录的符文 / 不在流派表的英雄：没有先验
    assert fit.fit_adjustment("9999", "96")[0] == 0.0
    assert fit.fit_adjustment("3086", "9999")[0] == 0.0
    assert fit.fit_adjustment("3086", None)[0] == 0.0


def test_dual_profile_overrides_archetype():
    # 狗熊（坦克前排流派，表内攻击特效亲和为 0）被动带攻击特效：绝活档案把它抬上去
    f_dual, note = fit.fit_adjustment("3086", "106")
    assert f_dual >= fit.DUAL_FIT_MIN
    assert "绝活" in note or "攻击特效" in note


def test_combo_gate_scales_by_fit():
    assert fit.combo_gate("3086", "96") == 1.0            # 契合拉满：联动全额
    assert fit.combo_gate("3086", "37") < 0.5             # 不契合：折算到下限附近
    assert fit.combo_gate("3086", None) == 1.0            # 未识别英雄：不折算
    assert fit.combo_gate("9999", "96") == fit.COMBO_GATE_FLOOR  # 未收录符文：下限


def test_fit_prior_fades_with_games(store):
    # 提莫的虚幻武器在绝活档案里（先验 +1.2）。胜率恰好等于英雄基准时，分数全部来自先验：
    # 250 局先验权重大，4 万局几乎为零——实测样本一大，推荐完全由数据决定
    rows = store.dataset.table(None)[1]["17"]
    base = store.dataset.table(None)[0]["17"]["win_rate"]
    rows["1029"] = {"games": 250, "wins": round(250 * base), "win_rate": base}
    small = recommend.evaluate(store, "17", ["1029", None, None])["slots"][0]
    rows["1029"] = {"games": 40000, "wins": round(40000 * base), "win_rate": base}
    big = recommend.evaluate(store, "17", ["1029", None, None])["slots"][0]
    assert small["score"] > big["score"] > 0
    assert big["score"] < 0.05
    assert any("随局数淡出" in x for x in small["reasons"])
    # 面板 delta 与三选一同口径
    from lolhex.panel import hero_panel
    d = {a["id"]: a["delta"] for a in hero_panel(store, "17")["augments"]}
    assert abs(d["1029"] - big["score"]) < 0.01


def test_rare_falls_back_to_global_fit(store):
    # 安妮（hero "1"）没有官方数据：2128 在提莫的统计里（全服有数据）但安妮一局没拿。
    # 修复前固定 -3.0；现在按 机制先验 + 全服Δ折算，只减不加分、下限 -3.0。
    ev = recommend.evaluate(store, "1", ["2128", "1029", None])
    slot = ev["slots"][0]
    assert slot["basis"] == "global_fit"
    assert -3.0 <= slot["score"] <= -0.2
    assert any("全英雄" in x for x in slot["reasons"])


def test_rare_fit_reduces_penalty_but_never_positive(store):
    # 同样是「几乎不选」：法强机制契合安妮的 1332 罚得轻，生命机制的 1204 罚得重；
    # 但机制契合再好也不会越过 -0.2（零英雄数据不允许变正分），也不当首选
    store.ranks["augments"]["1332"] = {"win": 0.58, "games": 5000}
    store.ranks["augments"]["1204"] = {"win": 0.45, "games": 5000}
    ev = recommend.evaluate(store, "1", ["1332", "1204", "1029"])
    s_fit, s_no = ev["slots"][0], ev["slots"][1]
    assert s_fit["basis"] == s_no["basis"] == "global_fit"
    assert s_fit["score"] > s_no["score"]
    assert s_fit["score"] <= -0.2
    assert ev["best_index"] == 2  # 首选仍是有实测数据的卡
    assert ev["slots"][2]["verdict"] == "best"


def test_all_bundled_heroes_have_archetype():
    import json
    from pathlib import Path
    from lolhex.synergy import HERO_ARCHETYPE_MAP

    static_path = Path(__file__).resolve().parent.parent / "lolhex" / "data" / "static_bundled.json"
    heroes = json.loads(static_path.read_text(encoding="utf-8"))["heroes"]
    missing = [hid for hid in heroes if hid not in HERO_ARCHETYPE_MAP]
    assert not missing, f"Heroes missing from HERO_ARCHETYPE_MAP: {missing}"
    for hid, arch in HERO_ARCHETYPE_MAP.items():
        assert arch in fit.ARCHETYPE_AFFINITY, f"Unknown archetype {arch} for hero {hid}"


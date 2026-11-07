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


def test_expanded_augment_mechanics_and_clean_rules():
    import re
    from lolhex import synergy

    # 机制向量扩充至 120+ 个在役海克斯，所有机制维度均合法
    assert len(fit.AUGMENT_MECHANICS) >= 120
    for aid, mech in fit.AUGMENT_MECHANICS.items():
        assert aid.isdigit() and mech
        for k, w in mech.items():
            assert k in fit.MECHANIC_CN and 0 < w <= 1.0

    # 统一阈值常数单调有序，且 recommend 与 synergy 共用
    assert fit.CORE_MIN_DELTA > fit.SAFE_MIN_DELTA > fit.CAUTION_BELOW == recommend.REROLL_BELOW > fit.TRAP_MAX_DELTA
    assert recommend.REROLL_GAP == fit.REROLL_GAP

    # 静态文案已与代码分离并剔除硬编码胜率百分比（如「74%胜率」）
    for aid, text in synergy.AUGMENT_META_EXPLANATIONS.items():
        assert not re.search(r"\d+(\.\d+)?%\s*胜率|胜率.*\d+%", text), f"Stale winrate in {aid}: {text}"
    for hid, prof in synergy.DUAL_PLAYSTYLE_PROFILES.items():
        assert "胜率" not in prof["build_name"], f"Stale winrate in hero {hid}: {prof['build_name']}"


def test_band_blend_fades_fit_with_weighted_band_sample():
    # 全体 30000 局（几乎无先验）但高分段仅 150 局（w=0.5）：分段模式下先验按加权淡出，不被全体局数完全抹平
    fade_all_only = recommend.fit_fade_factor(30000, 300)
    fade_blended = recommend.fit_fade_factor(30000, 300, band_games=150, band_weight=0.5)
    assert fade_all_only < 0.02
    assert fade_blended == pytest.approx(0.5 * (300 / 450) + 0.5 * (300 / 30300), 1e-4)
    assert fade_blended > 0.30



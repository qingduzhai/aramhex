# -*- coding: utf-8 -*-
"""符文对联动算分（机制推导，替代攻略视频手工值）：

1. 交互类型 × 机制耦合度决定加分：乘算 > 频次 > 资源 > 线性叠加；
2. 机制模型没覆盖到的人工确认组合按 0.5 耦合档计，不给零分也不虚高；
3. 表里没有的组合按共享机制推算，封顶、标注「推算」；
4. 冲突保持人工评审值。
"""
import pytest

from lolhex import fit, synergy


def test_computed_bonus_types_and_coupling():
    # 乘算满耦合：珠光×易损（共享暴击爆发、法强，min 权重和 1.5 截断 1.0）
    c = fit.computed_combo_bonus("1048", "1092", itype="multiplicative", curated=True)
    assert c["bonus"] == 6.0 and c["type"] == "multiplicative"
    # 频次满耦合：小蜜蜂×双刀流（共享攻击特效 + 普攻频次）
    c = fit.computed_combo_bonus("3086", "1225", itype="frequency", curated=True)
    assert c["bonus"] == 5.5
    # 资源转化部分耦合：蓝屏障×由心及物（共享蓝量 0.8）
    c = fit.computed_combo_bonus("3051", "1056", itype="resource", curated=True)
    assert c["bonus"] == 4.0 and c["coupling"] == pytest.approx(0.8)
    # 线性叠加：双巨人堆血
    c = fit.computed_combo_bonus("1018", "1041", itype="additive", curated=True)
    assert c["bonus"] == 2.5


def test_curated_floor_for_pairs_outside_mechanic_model():
    # 低音轰鸣×终极刷新：机制向量零共享，但人工确认有施法循环交互 → 0.5 档
    c = fit.computed_combo_bonus("1088", "3078", itype="frequency", curated=True)
    assert c["coupling"] == 0.0
    assert c["bonus"] == pytest.approx(5.5 * 0.5, 0.05)


def test_generic_inference_for_uncurated_pairs():
    # 双刀流×双发快射不在组合表：共享 攻击特效/普攻频次 强耦合 → 推算分（封顶）
    res = synergy.evaluate_combo_synergies("1225", ["2010"])
    assert res["bonus"] == fit.GENERIC_CAP
    assert any("推算" in r for r in res["reasons"])

    # 共享机制太弱的不给分
    res = synergy.evaluate_combo_synergies("1018", ["1092"])
    assert res["bonus"] == 0.0

    # 类型推断：攻击特效/频次→frequency，暴击/爆发→multiplicative
    assert fit.infer_interaction_type("3086", "2010") == "frequency"
    assert fit.infer_interaction_type("3018", "3116") == "multiplicative"
    assert fit.infer_interaction_type("3051", "2123") == "resource"


def test_conflicts_stay_manual_and_suppress_generic_bonus():
    res = synergy.evaluate_combo_synergies("1225", ["3018"])
    assert res["penalty"] == -5.0
    assert res["bonus"] == 0.0  # 已判冲突的组合不再推算正联动（冲突即结论）


def test_empirical_pair_shrinkage_blends_and_overrides_prior(store):
    # 1. 无实测 pairs 数据时：100% 退回机制推导值（6.0）
    s0 = fit.shrink_pair_bonus(6.0, None, 0.50)
    assert s0["bonus"] == 6.0 and s0["games"] == 0

    # 2. 200 局（恰好等于 PAIR_SHRINK_K=200）：实测 Lift (+10pp) 与机制先验 (+6pp) 各信一半 → +8.0pp
    s_mid = fit.shrink_pair_bonus(6.0, {"games": 200, "wins": 120, "win": 0.60}, 0.50)
    assert s_mid["bonus"] == pytest.approx(8.0, 0.01)

    # 3. 网红组合在大样本（4000 局）实测反而掉胜率（45% vs 基准 50% = -5.0pp）：
    #    收缩后变为负分，evaluate_combo_synergies 将其计入 penalty 而非正加分
    res_trap = synergy.evaluate_combo_synergies(
        "1092", ["1048"],
        pair_stats={"1048+1092": {"games": 4000, "wins": 1800, "win": 0.45}},
        baseline_win=0.50,
    )
    assert res_trap["bonus"] == 0.0
    assert res_trap["penalty"] < -4.0
    assert any("实测共现 4000局" in r for r in res_trap["reasons"])

    # 4. DataStore.hero_augment_pairs 过滤 excluded_augments 并规范化键序
    store.dataset.meta["excluded_augments"] = {"1337": {"name": "尊我为王", "reason": "偏差"}}
    store.dataset._tables["opt:hero_augment_pairs.json"] = {
        "17": {
            "1092+1048": {"games": 300, "wins": 180},
            "1337+1048": {"games": 500, "wins": 400},
        }
    }
    store.dataset.manifest["files"]["hero_augment_pairs.json"] = {"sha256": "0" * 64}
    try:
        pairs = store.hero_augment_pairs("17")
        assert "1048+1092" in pairs
        assert "1048+1337" not in pairs and "1337+1048" not in pairs
    finally:
        store.dataset.manifest["files"].pop("hero_augment_pairs.json", None)
        store.dataset._tables.pop("opt:hero_augment_pairs.json", None)


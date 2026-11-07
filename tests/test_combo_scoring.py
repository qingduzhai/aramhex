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

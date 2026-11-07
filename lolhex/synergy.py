# -*- coding: utf-8 -*-
"""
海克斯符文与装备流派协同推导引擎 (AramHex Synergy Engine 4.0)
静态规则与文案存放在 lolhex/data/synergy_rules.json（与代码逻辑分离，便于随版本独立维护）：
1. 海克斯 ➡️ 流派归属与核心装备联动路线 (Item Synergy Hints)
2. 4.0 绝活联动与双修英雄动态流派转轨 (Playstyle Pivots)
3. 数据驱动决策分类器 (Lift主判据 + 置信度 + 核心/稳妥/陷阱/慎选/可选)
4. 局内双符文/多符文联动算分与实测 pairs 贝叶斯收缩融合
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_RULES_PATH = Path(__file__).resolve().parent / "data" / "synergy_rules.json"


def _load_synergy_rules(path: Path = _RULES_PATH) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    dual: dict[str, dict[str, Any]] = {}
    for hid, prof in (raw.get("dual_playstyle_profiles") or {}).items():
        p = dict(prof)
        p["candidate_augments"] = set(str(x) for x in prof.get("candidate_augments", []))
        dual[str(hid)] = p
    combos: list[dict[str, Any]] = []
    for c in raw.get("augment_combos") or []:
        row = dict(c)
        row["pair"] = set(str(x) for x in c.get("pair", []))
        combos.append(row)
    combo_types: dict[frozenset[str], str] = {
        frozenset(k.split("+")): v for k, v in (raw.get("combo_types") or {}).items()
    }
    conflicts: list[dict[str, Any]] = []
    for c in raw.get("augment_conflicts") or []:
        row = dict(c)
        row["pair"] = set(str(x) for x in c.get("pair", []))
        conflicts.append(row)
    return {
        "HERO_ARCHETYPE_MAP": dict(raw.get("hero_archetype_map") or {}),
        "ARCHETYPE_BUILD_TEMPLATES": dict(raw.get("archetype_build_templates") or {}),
        "AUGMENT_PIVOT_ANCHORS": dict(raw.get("augment_pivot_anchors") or {}),
        "DUAL_PLAYSTYLE_PROFILES": dual,
        "AUGMENT_META_EXPLANATIONS": dict(raw.get("augment_meta_explanations") or {}),
        "AUGMENT_COMBOS": combos,
        "COMBO_TYPES": combo_types,
        "AUGMENT_CONFLICTS": conflicts,
    }


_RULES = _load_synergy_rules()

HERO_ARCHETYPE_MAP: dict[str, str] = _RULES["HERO_ARCHETYPE_MAP"]
ARCHETYPE_BUILD_TEMPLATES: dict[str, dict[str, Any]] = _RULES["ARCHETYPE_BUILD_TEMPLATES"]
AUGMENT_PIVOT_ANCHORS: dict[str, dict[str, Any]] = _RULES["AUGMENT_PIVOT_ANCHORS"]
DUAL_PLAYSTYLE_PROFILES: dict[str, dict[str, Any]] = _RULES["DUAL_PLAYSTYLE_PROFILES"]
AUGMENT_META_EXPLANATIONS: dict[str, str] = _RULES["AUGMENT_META_EXPLANATIONS"]
AUGMENT_COMBOS: list[dict[str, Any]] = _RULES["AUGMENT_COMBOS"]
COMBO_TYPES: dict[frozenset[str], str] = _RULES["COMBO_TYPES"]
AUGMENT_CONFLICTS: list[dict[str, Any]] = _RULES["AUGMENT_CONFLICTS"]


def get_synergy_item_hint(store: Any, hero_id: str | None, augment_id: str | None) -> dict[str, Any] | None:
    """
    根据英雄与所选海克斯，推导最契合的 Top 3 核心装备路线：
    1. 优先查原版 dataset 的显式 hero_augment_items.json；
    2. 其次查英雄特化转轨 (Dual Playstyle Override)；
    3. 再次查质变海克斯专属锚点 (Pivot Anchor)；
    4. 最后结合英雄主定位流派 (Archetype Fallback)。
    """
    if not hero_id or not augment_id:
        return None

    hid_str = str(hero_id)
    aid_str = str(augment_id)

    # 1. 优先尝试原版 dataset 的显式 hero_augment_items.json
    if hasattr(store, "augment_items"):
        try:
            hint = store.augment_items(hero_id, augment_id)
            if hint and hint.get("items"):
                hint_copy = dict(hint)
                hint_copy["title"] = "核心协同出装 · 统计优选"
                hint_copy["footer"] = "选该符文后的推荐装备配合"
                return hint_copy
        except Exception:
            pass

    items_dict = getattr(store, "items", {}) or {}

    def format_item(item_info: dict[str, Any]) -> dict[str, Any]:
        iid = str(item_info["id"])
        meta = items_dict.get(iid, {})
        name = item_info.get("name") or meta.get("name") or iid
        icon = meta.get("icon")
        return {
            "item": iid,
            "name": name[:24],
            "icon": icon,
            "games": item_info.get("games"),
            "win": item_info.get("win")
        }

    # 2. 检查英雄专属特化转轨
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        if aid_str in dual["candidate_augments"]:
            rows = [format_item(x) for x in dual["items"][:3]]
            return {
                "source": "stats",
                "title": f"绝活协同路线 · {dual['build_name']}",
                "footer": "4.0攻略首选：符文触发绝活质变，建议搭配此套路线",
                "items": rows
            }

    # 3. 检查质变海克斯全局专属锚点
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        anchor = AUGMENT_PIVOT_ANCHORS[aid_str]
        rows = [format_item(x) for x in anchor["items"][:3]]
        return {
            "source": "stats",
            "title": f"核心协同路线 · {anchor['build_name']}",
            "footer": "质变符文联动：选该符文后的推荐核心出装",
            "items": rows
        }

    # 4. 英雄默认主流派母版
    archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
    rows = [format_item(x) for x in template["items"][:3]]
    return {
        "source": "stats",
        "title": f"核心协同路线 · {template['name']}",
        "footer": "标准流派公式：选该符文后的推荐出装",
        "items": rows
    }


def classify_augment_tier(store: Any, hero_id: str | None, augment_id: str | None,
                          win_rate: float | None, score: float | None, games: int | None) -> dict[str, str]:
    """
    数据驱动决策分类器：
    返回徽章标签（badge）、标签代号（tag）与简明建议（summary）。

    徽章只由实测数据（Lift + 样本量）决定，阈值与 recommend.py 统一取自 fit.py；
    静态绝活表（AUGMENT_META_EXPLANATIONS）只提供纯机制解读文案（不含硬编码过期胜率）。
    """
    from . import fit as fit_mod

    aid_str = str(augment_id or "")
    expl = AUGMENT_META_EXPLANATIONS.get(aid_str)
    g = games or 0

    # 1. 大样本高 Lift（Delta ≥ CORE_MIN_DELTA 且样本 ≥ CORE_MIN_GAMES）：核心徽章必须有实测数据支撑
    if score is not None and score >= fit_mod.CORE_MIN_DELTA and g >= fit_mod.CORE_MIN_GAMES:
        if expl:
            summary = f"4.0质变核心：{expl}"
        else:
            summary = f"流派核心符文，相对该英雄基准提升 {score:+.1f}pp"
        return {
            "badge": "🌟 核心",
            "tag": "core",
            "summary": summary
        }

    # 2. 泛用万金油 (稳妥)
    if (win_rate is not None and win_rate >= fit_mod.SAFE_MIN_WIN) and (score is None or score >= fit_mod.SAFE_MIN_DELTA):
        return {
            "badge": "🛡️ 稳妥",
            "tag": "evergreen",
            "summary": "泛用万金油符文，容错率高、发挥稳定"
        }

    # 3. 陷阱提示 (负 Lift 且样本达标)
    if score is not None and score <= fit_mod.TRAP_MAX_DELTA and g >= fit_mod.TRAP_MIN_GAMES:
        return {
            "badge": "⚠️ 陷阱",
            "tag": "trap",
            "summary": f"版本陷阱！相比该英雄基准降低 {abs(score):.1f}pp，建议刷新"
        }

    # 4. 低于基准期望，建议刷新
    if score is not None and score < fit_mod.CAUTION_BELOW:
        return {
            "badge": "🎲 慎选",
            "tag": "reroll",
            "summary": "低于基准期望，可优先考虑掷骰刷新"
        }

    # 5. 兜底：有机制解读的照常展示（含没有数据的新符文），但徽章不越级抬成核心
    return {
        "badge": "✨ 可选",
        "tag": "normal",
        "summary": expl or "契合常规对局，正常可选"
    }


# 联动加分递减与封顶：单组按表值，第二组起按 30% 计入，总量不超过单组最大值。
# 手工组合分只是机制先验，不能无限叠盖过实测胜率差（实测 Δ 通常只有 ±3pp）。
COMBO_BONUS_CAP = 8.0
COMBO_STACK_DECAY = 0.3


def _pair_key(aid_a: str, aid_b: str) -> str:
    return "+".join(sorted((str(aid_a), str(aid_b)), key=lambda x: int(x) if x.isdigit() else x))


def evaluate_combo_synergies(candidate_aid: str, acquired_aids: list[str], *,
                             pair_stats: dict[str, dict] | None = None,
                             baseline_win: float | None = None) -> dict[str, Any]:
    """
    计算当前候选海克斯 candidate_aid 与局内已选海克斯 acquired_aids 的多符文联动协同与冲突：
    返回:
    - bonus: float (联动总加分，机制推导值与实测 pairs 收缩后递减叠加并封顶)
    - penalty: float (冲突扣分)
    - net_score: float (净增减分)
    - reasons: list[str] (联动理由)
    - conflicts: list[str] (冲突警告)
    - core_items: list[dict] (推荐必出装备)

    加多少分由 fit.computed_combo_bonus 推导（交互类型 × 机制耦合度），不再用攻略视频拍的手工值；
    若传入实测共现表 pair_stats（来自 hero_augment_pairs.json），则按 fit.shrink_pair_bonus
    将机制先验向实测共现 Lift 收缩；无实测 pairs 数据时 100% 使用机制推导分。
    """
    from . import fit as fit_mod

    if not candidate_aid or not acquired_aids:
        return {"bonus": 0.0, "penalty": 0.0, "net_score": 0.0, "reasons": [], "conflicts": [], "core_items": []}

    cand = str(candidate_aid)
    acq_set = {str(a) for a in acquired_aids if a and str(a) != cand}
    pairs_map = pair_stats or {}

    bonuses: list[float] = []
    penalty = 0.0
    reasons = []
    conflicts = []
    core_items = []
    seen_item_ids = set()
    curated_partners: set[str] = set()

    for combo in AUGMENT_COMBOS:
        pair = combo["pair"]
        if cand in pair:
            other = (pair - {cand}).pop()
            if other in acq_set:
                curated_partners.add(other)
                calc = fit_mod.computed_combo_bonus(cand, other, itype=COMBO_TYPES.get(frozenset(pair)), curated=True)
                p_row = pairs_map.get(_pair_key(cand, other))
                shrunk = fit_mod.shrink_pair_bonus(calc["bonus"], p_row, baseline_win)
                eff_bonus = shrunk["bonus"]
                type_cn = fit_mod.INTERACTION_CN[calc["type"]]
                shared = f"（共享：{'、'.join(calc['shared'])}）" if calc["shared"] else "（机制模型外，人工确认）"
                emp_note = (f" · 实测共现 {shrunk['games']}局胜率 {shrunk['win'] * 100:.1f}%"
                            f"（收缩后 {eff_bonus:+.1f}pp）" if shrunk["games"] > 0 else "")
                if eff_bonus > 0:
                    bonuses.append(eff_bonus)
                elif eff_bonus < 0:
                    penalty += eff_bonus
                reasons.append(f"★ 组合联动【{combo['name']}】· {type_cn}算分 {calc['bonus']:+.1f}pp{shared}{emp_note}：{combo['desc']}")
                for it in combo.get("core_items", []):
                    if it["id"] not in seen_item_ids:
                        seen_item_ids.add(it["id"])
                        core_items.append(it)

    for conf in AUGMENT_CONFLICTS:
        pair = conf["pair"]
        if cand in pair:
            other = (pair - {cand}).pop()
            if other in acq_set:
                curated_partners.add(other)  # 有冲突的组合不再推算正联动（冲突即结论）
                penalty += conf["penalty"]
                conflicts.append(conf["reason"])

    # 表里没有的组合：共享机制够强或有实测共现数据时也推算给分
    for other in sorted(acq_set - curated_partners):
        calc = fit_mod.computed_combo_bonus(cand, other)
        p_row = pairs_map.get(_pair_key(cand, other))
        shrunk = fit_mod.shrink_pair_bonus(calc["bonus"], p_row, baseline_win)
        eff_bonus = shrunk["bonus"]
        if eff_bonus > 0:
            bonuses.append(eff_bonus)
            shared_part = f"（共享：{'、'.join(calc['shared'])}）" if calc["shared"] else ""
            if shrunk["games"] > 0:
                reasons.append(f"◇ 实测共现联动 · {shrunk['games']}局胜率 {shrunk['win'] * 100:.1f}%"
                               f"（收缩后 {eff_bonus:+.1f}pp）{shared_part}")
            else:
                reasons.append(f"◇ 机制联动（推算）· {fit_mod.INTERACTION_CN[calc['type']]} {eff_bonus:+.1f}pp"
                               f"{shared_part}")

    # 多组联动递减叠加并封顶（见 COMBO_BONUS_CAP / COMBO_STACK_DECAY）
    bonus = 0.0
    if bonuses:
        bonuses.sort(reverse=True)
        bonus = min(COMBO_BONUS_CAP, bonuses[0] + COMBO_STACK_DECAY * sum(bonuses[1:]))

    return {
        "bonus": round(bonus, 2),
        "penalty": round(penalty, 2),
        "net_score": round(bonus + penalty, 2),
        "reasons": reasons,
        "conflicts": conflicts,
        "core_items": core_items
    }


def get_augment_core_items(augment_id: str, store: Any = None, hero_id: str | None = None) -> list[dict[str, Any]]:
    """
    获取单个海克斯专属的核心必出质变装备。
    支持结合英雄专属特化与主流流派母版补全。
    """
    aid_str = str(augment_id or "")
    if aid_str in AUGMENT_PIVOT_ANCHORS:
        return AUGMENT_PIVOT_ANCHORS[aid_str].get("items", [])

    if hero_id:
        hid_str = str(hero_id)
        if hid_str in DUAL_PLAYSTYLE_PROFILES:
            dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
            if aid_str in dual["candidate_augments"]:
                return dual["items"]
        hint = get_synergy_item_hint(store, hid_str, aid_str)
        if hint and hint.get("items"):
            return [{"id": x.get("item") or x.get("id"), "name": x.get("name", "")} for x in hint["items"]]

    return []


def get_hero_rune_build(hero_id: str | None, acquired_aids: list[str] | None, store: Any = None) -> dict[str, Any]:
    """
    推导英雄当前最契合的【符文专精流派出装】：
    1. 若局内已选海克斯 (acquired_aids)，优先推导海克斯强联动；
    2. 若暂未选海克斯，结合英雄在 4.0 绝活攻略中的主流定位，生成【预备推荐流派】，并在选入符文后动态转轨；
    3. 返回完整 5 件神装路线（含 ID、名称、图标），并附带流派质变联动机制解析。
    """
    hid_str = str(hero_id or "")
    acq_list = [str(a) for a in (acquired_aids or []) if a]
    items_dict = getattr(store, "items", {}) or {}
    aug_dict = getattr(store, "augments", {}) or {}

    def format_item(it: dict[str, Any]) -> dict[str, Any]:
        iid = str(it.get("id") or it.get("item") or "")
        meta = items_dict.get(iid, {})
        name = it.get("name") or meta.get("name") or iid
        icon = it.get("icon") or meta.get("icon")
        return {"id": iid, "item": iid, "name": name, "icon": icon}

    aug_details = []
    for aid in acq_list:
        ameta = aug_dict.get(aid, {})
        aug_details.append({
            "id": aid,
            "name": ameta.get("name", aid),
            "rarity": ameta.get("rarity", "")
        })

    matched_build = None
    matched_explanation = ""
    matched_source = ""
    combo_items = []

    # 1.1 组合联动匹配 (AUGMENT_COMBOS)
    if len(acq_list) >= 2:
        for i in range(len(acq_list)):
            for j in range(i + 1, len(acq_list)):
                pair = {acq_list[i], acq_list[j]}
                for combo in AUGMENT_COMBOS:
                    if combo["pair"] == pair:
                        matched_build = combo.get("name")
                        matched_explanation = f"激活【{combo['name']}】组合：{combo['desc']}"
                        matched_source = f"组合联动【{combo['name']}】"
                        combo_items = combo.get("core_items", [])
                        break
                if matched_build:
                    break
            if matched_build:
                break

    # 1.2 英雄特化转轨匹配 (DUAL_PLAYSTYLE_PROFILES)
    if not matched_build and hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        for aid in acq_list:
            if aid in dual["candidate_augments"]:
                aname = (aug_dict.get(aid) or {}).get("name") or aid
                matched_build = dual["build_name"]
                matched_explanation = f"已选质变符文【{aname}】：触发 4.0 绝活流派质变，专属装备路线直接拉满！"
                matched_source = f"绝活符文【{aname}】"
                combo_items = dual["items"]
                break

    # 1.3 单海克斯锚点匹配 (AUGMENT_PIVOT_ANCHORS)
    if not matched_build:
        for aid in acq_list:
            if aid in AUGMENT_PIVOT_ANCHORS:
                anchor = AUGMENT_PIVOT_ANCHORS[aid]
                aname = (aug_dict.get(aid) or {}).get("name") or aid
                matched_build = anchor["build_name"]
                matched_explanation = f"已选符文【{aname}】：该符文机制大幅改变出装优先级，推荐优先合成上述核心装备。"
                matched_source = f"质变符文【{aname}】"
                combo_items = anchor["items"]
                break

    # 1.4 若局内有符文已选成功匹配
    if matched_build and combo_items:
        archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
        full_items = list(combo_items)
        seen_ids = {str(it.get("id") or it.get("item")) for it in full_items}
        for it in template.get("items", []):
            iid = str(it.get("id") or it.get("item"))
            if iid not in seen_ids:
                seen_ids.add(iid)
                full_items.append(it)
            if len(full_items) >= 5:
                break

        return {
            "build_name": matched_build,
            "status_label": f"已根据【{matched_source}】质变转轨",
            "is_rune_adapted": True,
            "items": [format_item(x) for x in full_items[:5]],
            "explanation": matched_explanation,
            "augments": aug_details
        }

    # 2. 未匹配到专属海克斯（或尚未选择海克斯）时的推荐流派
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        full_items = list(dual["items"])
        archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
        seen_ids = {str(it.get("id") or it.get("item")) for it in full_items}
        for it in template.get("items", []):
            iid = str(it.get("id") or it.get("item"))
            if iid not in seen_ids:
                seen_ids.add(iid)
                full_items.append(it)
            if len(full_items) >= 5:
                break
        return {
            "build_name": dual["build_name"],
            "status_label": "4.0 绝活流派预备推荐（选入海克斯后动态转轨）",
            "is_rune_adapted": False,
            "items": [format_item(x) for x in full_items[:5]],
            "explanation": "该英雄在 4.0 版本的强力打法。三选一若刷出对应质变海克斯将彻底激活！",
            "augments": aug_details
        }

    archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
    return {
        "build_name": template["name"],
        "status_label": "4.0 标准流派推荐（选入海克斯后动态转轨）",
        "is_rune_adapted": False,
        "items": [format_item(x) for x in template["items"][:5]],
        "explanation": "当前为该英雄主流出装公式。局内选择海克斯符文后，将实时推导专属质变出装路线。",
        "augments": aug_details
    }


def get_acquired_augments_build_advice(acquired_aids: list[str], store: Any = None) -> list[dict[str, Any]]:
    """
    根据本局已选海克斯列表，汇总当前海克斯流派推荐的核心必出装备。
    """
    if not acquired_aids:
        return []

    advice_items = []
    seen_ids = set()

    # 1. 先查组合联动装备
    acq_list = [str(a) for a in acquired_aids if a]
    for i in range(len(acq_list)):
        for j in range(i + 1, len(acq_list)):
            pair = {acq_list[i], acq_list[j]}
            for combo in AUGMENT_COMBOS:
                if combo["pair"] == pair:
                    for it in combo.get("core_items", []):
                        if it["id"] not in seen_ids:
                            seen_ids.add(it["id"])
                            advice_items.append({**it, "source": f"组合联动【{combo['name']}】"})

    # 2. 再查各个单海克斯的专属锚点出装
    for aid in acq_list:
        if aid in AUGMENT_PIVOT_ANCHORS:
            anchor = AUGMENT_PIVOT_ANCHORS[aid]
            for it in anchor.get("items", []):
                if it["id"] not in seen_ids:
                    seen_ids.add(it["id"])
                    advice_items.append({**it, "source": f"符文【{anchor['build_name']}】"})

    return advice_items

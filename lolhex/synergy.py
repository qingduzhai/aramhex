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


def derive_mechanic_build(aid_str: str, hero_id: str | None, store: Any = None) -> tuple[str, str, str, str] | None:
    """
    基于海克斯符文的属性与机制权重（fit.AUGMENT_MECHANICS 或关键词），
    结合英雄基础定位，动态推导契合该机制的职业模板、流派名及机制解读。
    返回 (arch_key, custom_build_name, top_mech, explanation) 或 None。
    """
    if not aid_str:
        return None
    from . import fit as fit_mod
    aug_mechanics = getattr(fit_mod, "AUGMENT_MECHANICS", {})
    mech_cn = getattr(fit_mod, "MECHANIC_CN", {})
    aug_dict = getattr(store, "augments", {}) or {}

    ameta = aug_dict.get(str(aid_str), {})
    aname = ameta.get("name") or str(aid_str)
    adesc = ameta.get("desc") or ""
    mechs = dict(aug_mechanics.get(str(aid_str), {}))

    if not mechs:
        txt = aname + " " + adesc
        if "暴击" in txt:
            mechs["crit"] = 0.9
        if any(x in txt for x in ("特效", "攻击附带", "普攻", "攻速", "攻击速度")):
            mechs["on_hit"] = 0.9
        if any(x in txt for x in ("最大生命", "生命值", "体型", "额外生命", "巨像", "巨人")):
            mechs["hp"] = 0.9
        if any(x in txt for x in ("护甲", "魔抗", "双抗", "抗性", "坦度")):
            mechs["armor"] = 0.9
        if any(x in txt for x in ("法术强度", "法强", "法术暴击", "魔法伤害")):
            mechs["ap"] = 0.9
        if any(x in txt for x in ("技能急速", "冷却缩减", "终极技能")):
            mechs["cdr"] = 0.9
        if any(x in txt for x in ("护盾", "治疗", "圣光")):
            mechs["heal_shield"] = 0.9
        if any(x in txt for x in ("吸血", "全能吸血", "生命偷取")):
            mechs["drain"] = 0.9

    if not mechs:
        return None

    top_mech, top_weight = max(mechs.items(), key=lambda kv: kv[1])
    if top_weight < 0.4:
        return None

    mech_name = mech_cn.get(top_mech, top_mech)
    hid_str = str(hero_id or "")
    base_arch = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    is_ap = base_arch in ("AP_Burst_Poke", "AP_Burn_Haste")

    arch_key = None
    custom_name = None

    if top_mech in ("hp", "armor"):
        arch_key = "Tank_Frontline"
        custom_name = "巨神前线肉坦流"
    elif top_mech == "crit":
        arch_key = "AP_Burst_Poke" if is_ap else "ADC_Crit"
        custom_name = "法术暴击流" if is_ap else "暴击终结流"
    elif top_mech in ("on_hit", "attack_freq"):
        arch_key = "ADC_Hybrid_OnHit"
        custom_name = "普攻特效攻速流"
    elif top_mech == "burn":
        arch_key = "AP_Burn_Haste"
        custom_name = "折磨急速灼烧流"
    elif top_mech == "ap":
        arch_key = "AP_Burst_Poke"
        custom_name = "法术爆发流" if is_ap else "法系双修爆发流"
    elif top_mech == "burst":
        arch_key = "AP_Burst_Poke" if is_ap else "Assassin_Lethality"
        custom_name = "法系核弹爆发流" if is_ap else "穿甲爆发刺客流"
    elif top_mech == "cdr":
        arch_key = "AP_Burn_Haste" if is_ap else "AD_Spellcaster_Poke"
        custom_name = "折磨急速技能流" if is_ap else "穿甲急速技能流"
    elif top_mech in ("drain", "melee"):
        arch_key = "Tank_Frontline" if base_arch == "Tank_Frontline" else "Bruiser_Drain"
        custom_name = "不灭回复肉坦流" if base_arch == "Tank_Frontline" else "不灭吸血重装流"

    if arch_key and arch_key in ARCHETYPE_BUILD_TEMPLATES:
        expl = f"符文【{aname}】（主打机制：{mech_name}）：已根据机制动态将推荐出装调整至契合路线。"
        return (arch_key, custom_name, top_mech, expl)
    return None


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

    # 3.5 机制与词条动态推导 (Mechanic & Stat-driven Dynamic Pivot)
    derived = derive_mechanic_build(aid_str, hid_str, store)
    if derived:
        arch_key, custom_name, top_mech, expl = derived
        t = ARCHETYPE_BUILD_TEMPLATES[arch_key]
        rows = [format_item(x) for x in t["items"][:3]]
        return {
            "source": "stats",
            "title": f"核心协同路线 · {custom_name}",
            "footer": "符文机制联动：选该符文后的推荐核心出装",
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
        return {
            "bonus": 0.0, "penalty": 0.0, "net_score": 0.0,
            "reasons": [], "conflicts": [], "core_items": [],
            "combos": [], "conflict_details": [],
        }

    cand = str(candidate_aid)
    acq_set = {str(a) for a in acquired_aids if a and str(a) != cand}
    pairs_map = pair_stats or {}

    bonuses: list[float] = []
    penalty = 0.0
    reasons = []
    conflicts = []
    core_items = []
    combos = []
    conflict_details = []
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
                combos.append({
                    "name": combo["name"],
                    "partner_id": other,
                    "bonus": round(eff_bonus, 2),
                    "raw_bonus": calc["bonus"],
                    "type": calc["type"],
                    "type_cn": type_cn,
                    "desc": combo["desc"],
                    "curated": True,
                    "core_items": list(combo.get("core_items", [])),
                    "followup_items": list(combo.get("followup_items", [])),
                    "boots": dict(combo["boots"]) if combo.get("boots") else None,
                    "archetype": combo.get("archetype"),
                })
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
                conflict_details.append({
                    "partner_id": other,
                    "penalty": conf["penalty"],
                    "reason": conf["reason"],
                })

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
            combos.append({
                "name": "实测共现联动" if shrunk["games"] > 0 else f"{fit_mod.INTERACTION_CN[calc['type']]}联动",
                "partner_id": other,
                "bonus": round(eff_bonus, 2),
                "raw_bonus": calc["bonus"],
                "type": calc["type"],
                "type_cn": fit_mod.INTERACTION_CN[calc["type"]],
                "shared": list(calc["shared"]),
                "curated": False,
                "core_items": [],
            })

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
        "core_items": core_items,
        "combos": combos,
        "conflict_details": conflict_details,
    }


def _enrich_item(it: dict[str, Any], store: Any = None, tag: str = "") -> dict[str, Any]:
    items_dict = getattr(store, "items", {}) or {}
    iid = str(it.get("id") or it.get("item") or "")
    meta = items_dict.get(iid, {})
    name = it.get("name") or meta.get("name") or iid
    icon = it.get("icon") or meta.get("icon")
    out: dict[str, Any] = {
        "id": iid,
        "item": iid,
        "name": name,
        "icon": icon,
    }
    if it.get("win") is not None:
        out["win"] = it.get("win")
    if it.get("games") is not None:
        out["games"] = it.get("games")
    if tag or it.get("tag"):
        out["tag"] = tag or it.get("tag")
    return out


def get_augment_core_items(augment_id: str, store: Any = None, hero_id: str | None = None) -> list[dict[str, Any]]:
    """
    获取单个海克斯专属的核心必出质变装备。
    优先级：英雄专属绝活转轨 > 海克斯全局质变锚点 > 显式统计/主流流派母版补全。
    自动补全装备图标（icon）与标准字段（id / item / name）。
    """
    if isinstance(store, str) and not isinstance(hero_id, str):
        store, hero_id = hero_id, store
    aid_str = str(augment_id or "")
    if hero_id:
        hid_str = str(hero_id)
        if hid_str in DUAL_PLAYSTYLE_PROFILES:
            dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
            if aid_str in dual["candidate_augments"]:
                return [_enrich_item(x, store, tag="⚡绝活必出") for x in dual.get("items", [])]

    if aid_str in AUGMENT_PIVOT_ANCHORS:
        return [_enrich_item(x, store, tag="🎯质变核心") for x in AUGMENT_PIVOT_ANCHORS[aid_str].get("items", [])]

    if hero_id:
        hid_str = str(hero_id)
        hint = get_synergy_item_hint(store, hid_str, aid_str)
        if hint and hint.get("items"):
            return [_enrich_item(x, store, tag="推荐核心") for x in hint["items"]]

    return []


def get_potential_combos_for_augment(augment_id: str | None, store: Any = None,
                                     exclude_aids: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
    """查询某个海克斯在人工精选组合表（AUGMENT_COMBOS）中可搭配的联动伙伴与组合信息。"""
    if not augment_id:
        return []
    from . import fit as fit_mod
    aid_str = str(augment_id)
    excl = {str(x) for x in (exclude_aids or []) if x}
    aug_dict = getattr(store, "augments", {}) or {}
    out = []
    for combo in AUGMENT_COMBOS:
        pair = combo["pair"]
        if aid_str in pair:
            partner_id = (pair - {aid_str}).pop()
            if partner_id in excl:
                continue
            p_meta = aug_dict.get(partner_id) or {}
            p_name = p_meta.get("name") or partner_id
            calc = fit_mod.computed_combo_bonus(aid_str, partner_id, itype=COMBO_TYPES.get(frozenset(pair)), curated=True)
            out.append({
                "combo_name": combo["name"],
                "partner_id": partner_id,
                "partner_name": p_name,
                "bonus": round(calc.get("bonus") or combo.get("bonus") or 3.5, 1),
                "desc": combo.get("desc", ""),
                "core_items": [_enrich_item(x, store, tag="★联动必出") for x in combo.get("core_items", [])],
            })
    return out


def get_potential_combos_for_acquired(acquired_aids: list[str] | None, store: Any = None,
                                       extra_store: Any = None) -> list[dict[str, Any]]:
    """根据本局已持海克斯列表，提示后续三选一值得留意的联动海克斯目标。"""
    if not acquired_aids:
        return []
    if (store is None or isinstance(store, str)) and extra_store is not None:
        store = extra_store
    acq_list = [str(x) for x in acquired_aids if x]
    acq_set = set(acq_list)
    aug_dict = getattr(store, "augments", {}) or {}
    seen_targets: set[tuple[str, str]] = set()
    out = []
    for aid in acq_list:
        held_name = (aug_dict.get(aid) or {}).get("name") or aid
        for pc in get_potential_combos_for_augment(aid, store, exclude_aids=acq_set):
            key = (aid, pc["partner_id"])
            if key not in seen_targets:
                seen_targets.add(key)
                out.append({
                    **pc,
                    "held_id": aid,
                    "held_name": held_name,
                })
    return out


def _short_build_name(name: str) -> str:
    """去掉英雄名前缀（如『狗熊 · 小蜜蜂连锁雷暴流』→『小蜜蜂连锁雷暴流』），方便局内紧凑展示。"""
    if "·" in name:
        return name.split("·", 1)[1].strip()
    return name.strip()


def get_augment_synergy_profile(store: Any, hero_id: str | None, augment_id: str | None,
                                combo_synergy: dict[str, Any] | None = None,
                                acquired_aids: list[str] | None = None) -> dict[str, Any]:
    """
    综合推导单张候选海克斯卡片的【强提示联动档案与对应核心出装】：
    涵盖：
    1. 局内已持多符文组合联动（combo）与冲突（conflict）
    2. 英雄专属 4.0 绝活流派转轨（dual）
    3. 质变海克斯全局核心锚点（pivot）
    4. 显式统计优选出装（dataset）与可凑组合预告（potential_combos）
    5. 英雄常规流派兜底（archetype）
    """
    aid_str = str(augment_id or "")
    hid_str = str(hero_id or "")
    aug_dict = getattr(store, "augments", {}) or {}
    cs = combo_synergy or {}
    acq_set = {str(x) for x in (acquired_aids or []) if x}

    potential_combos = get_potential_combos_for_augment(aid_str, store, exclude_aids=acq_set)

    # 汇总装备（优先组合必出 -> 绝活转轨 -> 质变锚点 -> 统计/主流流派）
    combo_raw_items = cs.get("core_items") or []
    combo_items = [_enrich_item(x, store, tag="★联动必出") for x in combo_raw_items]

    dual_prof = DUAL_PLAYSTYLE_PROFILES.get(hid_str) if hid_str else None
    is_dual = bool(dual_prof and aid_str in dual_prof.get("candidate_augments", set()))
    anchor_prof = AUGMENT_PIVOT_ANCHORS.get(aid_str)
    is_pivot = bool(anchor_prof)

    explicit_hint = None
    if hid_str and aid_str and hasattr(store, "augment_items"):
        try:
            h = store.augment_items(hid_str, aid_str)
            if h and h.get("items"):
                explicit_hint = h
        except Exception:
            pass

    # 合并去重装备列表
    merged_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def _add_items(rows: list[dict[str, Any]], default_tag: str) -> None:
        for r in rows:
            enriched = _enrich_item(r, store, tag=r.get("tag") or default_tag)
            iid = enriched["id"]
            if iid and iid not in seen_ids:
                seen_ids.add(iid)
                merged_items.append(enriched)

    _add_items(combo_items, "★联动必出")
    if is_dual and dual_prof:
        _add_items(dual_prof.get("items", []), "⚡绝活必出")
    if is_pivot and anchor_prof:
        _add_items(anchor_prof.get("items", []), "🎯质变核心")
    if explicit_hint:
        _add_items(explicit_hint.get("items", []), "📊统计优选")
    if hid_str and not merged_items:
        archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
        _add_items(template.get("items", []), "流派推荐")

    # 判定最高优先级的联动类型与强提示文案
    kind = "archetype"
    is_special = False
    badge_prefix = ""
    build_name = ""
    route_title = "推荐核心出装"
    synergy_line = ""
    sub_line = ""

    combos_list = cs.get("combos") or []
    conflict_list = cs.get("conflict_details") or []

    if cs.get("bonus", 0) > 0 and combos_list:
        kind = "combo"
        is_special = True
        top_c = max(combos_list, key=lambda x: (1 if x.get("curated") else 0, x.get("bonus", 0)))
        p_id = str(top_c.get("partner_id") or "")
        p_name = (aug_dict.get(p_id) or {}).get("name") or p_id
        c_name = top_c.get("name") or "符文联动"
        gate = cs.get("gate", 1.0)
        eff_val = cs.get("bonus", 0.0) * gate
        if top_c.get("curated"):
            badge_prefix = f"🔥 联动【{c_name[:6]}】" if len(c_name) <= 6 else "🔥 联动质变"
            build_name = c_name
            route_title = f"🔥 联动必出 · {c_name}"
            synergy_line = f"★ 配已持【{p_name}】→【{c_name}】({eff_val:+.1f})"
            sub_line = top_c.get("desc", "")
        else:
            badge_prefix = "🔥 联动加成"
            build_name = c_name
            route_title = f"🔥 联动推荐 · 配【{p_name}】"
            shared_str = "、".join(top_c.get("shared") or [])
            shared_tail = f"·{shared_str}" if shared_str else ""
            synergy_line = f"★ 与已持【{p_name}】联动 {eff_val:+.1f}pp{shared_tail}"
    elif cs.get("penalty", 0) < 0:
        kind = "conflict"
        is_special = True
        badge_prefix = "⛔ 机制冲突"
        if conflict_list:
            p_id = str(conflict_list[0].get("partner_id") or "")
            p_name = (aug_dict.get(p_id) or {}).get("name") or p_id
            synergy_line = f"⚠ 与已持【{p_name}】机制冲突（{cs['penalty'] * cs.get('gate', 1.0):.1f}pp）"
            sub_line = conflict_list[0].get("reason", "")
        else:
            synergy_line = f"⚠ 与已持符文机制冲突（{cs['penalty'] * cs.get('gate', 1.0):.1f}pp）"
    elif is_dual and dual_prof:
        kind = "dual"
        is_special = True
        badge_prefix = "⚡ 绝活质变"
        build_name = _short_build_name(dual_prof["build_name"])
        route_title = f"⚡ 绝活必出 · {build_name}"
        synergy_line = f"⚡ 本英雄绝活：【{build_name}】"
        if potential_combos:
            pc0 = potential_combos[0]
            sub_line = f"🔗 可凑联动：配【{pc0['partner_name']}】→【{pc0['combo_name']}】"
    elif is_pivot and anchor_prof:
        kind = "pivot"
        is_special = True
        badge_prefix = "🎯 流派质变"
        build_name = _short_build_name(anchor_prof["build_name"])
        route_title = f"🎯 质变必出 · {build_name}"
        synergy_line = f"🎯 质变路线：【{build_name}】"
        if potential_combos:
            pc0 = potential_combos[0]
            sub_line = f"🔗 可凑联动：配【{pc0['partner_name']}】→【{pc0['combo_name']}】"
    elif explicit_hint:
        kind = "dataset"
        is_special = True
        badge_prefix = "📊 专属出装"
        build_name = "统计优选出装"
        route_title = "📊 符文协同出装 · 统计优选"
        if potential_combos:
            pc0 = potential_combos[0]
            synergy_line = f"🔗 可凑联动：配【{pc0['partner_name']}】→【{pc0['combo_name']}】"
    else:
        if hid_str:
            archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
            template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
            build_name = template["name"]
            route_title = f"💡 推荐出装 · {build_name}"
        if potential_combos:
            pc0 = potential_combos[0]
            synergy_line = f"🔗 可凑联动：配【{pc0['partner_name']}】→【{pc0['combo_name']}】"

    # 确定流派匹配的后续补强装（第4、5件）与专属靴子
    default_arch = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    matched_arch = default_arch
    raw_followups: list[dict[str, Any]] = []
    raw_boots: dict[str, Any] | None = None

    if kind == "combo" and combos_list:
        top_c = max(combos_list, key=lambda x: (1 if x.get("curated") else 0, x.get("bonus", 0)))
        if top_c.get("archetype"):
            matched_arch = top_c["archetype"]
        raw_followups.extend(top_c.get("followup_items") or [])
        raw_boots = top_c.get("boots")
    if is_dual and dual_prof:
        if kind != "combo" and dual_prof.get("archetype"):
            matched_arch = dual_prof["archetype"]
        raw_followups.extend(dual_prof.get("followup_items") or [])
        if not raw_boots:
            raw_boots = dual_prof.get("boots")
    if is_pivot and anchor_prof:
        if kind not in ("combo", "dual") and anchor_prof.get("archetype"):
            matched_arch = anchor_prof["archetype"]
        raw_followups.extend(anchor_prof.get("followup_items") or [])
        if not raw_boots:
            raw_boots = anchor_prof.get("boots")

    arch_template = ARCHETYPE_BUILD_TEMPLATES.get(matched_arch, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
    raw_followups.extend(arch_template.get("items") or [])
    raw_followups.extend(arch_template.get("situational_items") or [])
    if not raw_boots:
        raw_boots = arch_template.get("boots") or {"id": "3158", "name": "明朗之靴"}

    core_three = merged_items[:3]
    full_items: list[dict[str, Any]] = [dict(x, role="core") for x in core_three]
    full_seen = {x["id"] for x in full_items}
    if "6656" in full_seen or "4646" in full_seen:
        full_seen.update({"6656", "4646"})
    followup_items: list[dict[str, Any]] = []
    for f_it in raw_followups:
        enriched_f = _enrich_item(f_it, store, tag="成型补强")
        enriched_f["role"] = "followup"
        fid = enriched_f["id"]
        if fid and fid not in full_seen:
            full_seen.add(fid)
            if fid in ("6656", "4646"):
                full_seen.update({"6656", "4646"})
            full_items.append(enriched_f)
            followup_items.append(enriched_f)
            if len(full_items) >= 5:
                break

    boots_item = _enrich_item(raw_boots, store, tag="👟推荐靴子")
    boots_item["role"] = "boots"

    items_box = None
    if core_three and hid_str:
        items_box = {
            "source": "synergy",
            "kind": kind,
            "is_special": is_special,
            "title": route_title,
            "items": core_three,
        }

    return {
        "kind": kind,
        "is_special": is_special,
        "badge_prefix": badge_prefix,
        "build_name": build_name,
        "route_title": route_title,
        "synergy_line": synergy_line,
        "sub_line": sub_line,
        "potential_combos": potential_combos,
        "items": core_three,
        "followup_items": followup_items[:2],
        "full_items": full_items[:5],
        "boots": boots_item,
        "full_six_items": [boots_item] + full_items[:5],
        "items_box": items_box,
    }


def get_hero_rune_build(hero_id: str | None, acquired_aids: list[str] | None, store: Any = None) -> dict[str, Any]:
    """
    推导英雄当前最契合的【符文专精流派出装】：
    1. 若局内已选海克斯 (acquired_aids)，优先推导海克斯强联动；
    2. 若暂未选海克斯，结合英雄在 4.0 绝活攻略中的主流定位，生成【预备推荐流派】，并在选入符文后动态转轨；
    3. 返回完整 5 件成装路线（items）+ 专属靴子（boots）+ 完整 6 神装（full_six_items），并附带流派质变联动机制解析。
    """
    hid_str = str(hero_id or "")
    acq_list = [str(a) for a in (acquired_aids or []) if a]
    items_dict = getattr(store, "items", {}) or {}
    aug_dict = getattr(store, "augments", {}) or {}

    def format_item(it: dict[str, Any], role: str = "core", tag: str = "") -> dict[str, Any]:
        iid = str(it.get("id") or it.get("item") or "")
        meta = items_dict.get(iid, {})
        name = it.get("name") or meta.get("name") or iid
        icon = it.get("icon") or meta.get("icon")
        return {
            "id": iid,
            "item": iid,
            "name": name,
            "icon": icon,
            "role": role,
            "tag": tag or it.get("tag") or ("★符文必出" if role == "core" else ("👟推荐靴子" if role == "boots" else "成型补强")),
        }

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
    combo_items: list[dict[str, Any]] = []
    matched_followups: list[dict[str, Any]] = []
    matched_boots: dict[str, Any] | None = None
    matched_arch: str | None = None

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
                        combo_items = list(combo.get("core_items", []))
                        matched_followups = list(combo.get("followup_items", []))
                        matched_boots = combo.get("boots")
                        matched_arch = combo.get("archetype")
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
                matched_explanation = f"已选质变符文【{aname}】：触发 4.0 绝活流派质变，专属 6 神装路线直接拉满！"
                matched_source = f"绝活符文【{aname}】"
                combo_items = list(dual["items"])
                matched_followups = list(dual.get("followup_items", []))
                matched_boots = dual.get("boots")
                matched_arch = dual.get("archetype")
                break

    # 1.3 单海克斯锚点匹配 (AUGMENT_PIVOT_ANCHORS)
    if not matched_build:
        for aid in acq_list:
            if aid in AUGMENT_PIVOT_ANCHORS:
                anchor = AUGMENT_PIVOT_ANCHORS[aid]
                aname = (aug_dict.get(aid) or {}).get("name") or aid
                matched_build = anchor["build_name"]
                matched_explanation = f"已选符文【{aname}】：该符文机制大幅改变出装优先级，推荐按上述专属 6 神装顺序合成。"
                matched_source = f"质变符文【{aname}】"
                combo_items = list(anchor["items"])
                matched_followups = list(anchor.get("followup_items", []))
                matched_boots = anchor.get("boots")
                matched_arch = anchor.get("archetype")
                break

    # 1.4 机制与词条动态推导 (Mechanic & Stat-driven Dynamic Pivot)
    if not matched_build and acq_list:
        from . import fit as fit_mod
        mech_cn = getattr(fit_mod, "MECHANIC_CN", {})
        for aid in reversed(acq_list):
            derived = derive_mechanic_build(aid, hid_str, store)
            if derived:
                arch_key, custom_name, top_mech, expl = derived
                aname = (aug_dict.get(aid) or {}).get("name") or aid
                mech_name = mech_cn.get(top_mech, top_mech)
                t = ARCHETYPE_BUILD_TEMPLATES[arch_key]
                matched_build = custom_name
                matched_explanation = f"检测到已选符文【{aname}】（主打机制：{mech_name}）：已根据机制动态将出装转轨至契合的核心路线上！"
                matched_source = f"符文【{aname}】({mech_name})"
                combo_items = list(t.get("items", []))
                matched_followups = list(t.get("situational_items", []))
                matched_boots = t.get("boots")
                matched_arch = arch_key
                break

    trigger_augments = []
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        for caid in sorted(DUAL_PLAYSTYLE_PROFILES[hid_str].get("candidate_augments", [])):
            trigger_augments.append({
                "id": caid,
                "name": (aug_dict.get(caid) or {}).get("name") or caid,
            })
    next_combos = get_potential_combos_for_acquired(acq_list, store)

    # 1.4 若局内有符文已选成功匹配：按流派自洽体系补齐第4、5件与专属鞋子（避免转轨串味）
    if matched_build and combo_items:
        arch_key = matched_arch or HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(arch_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])

        # 若同时持有其他同体系质变海克斯，将其核心装也纳入后续候选
        secondary_candidates: list[dict[str, Any]] = []
        for aid in acq_list:
            if aid in AUGMENT_PIVOT_ANCHORS:
                sec_anchor = AUGMENT_PIVOT_ANCHORS[aid]
                if sec_anchor.get("archetype") == arch_key:
                    secondary_candidates.extend(sec_anchor.get("items", []))

        core_formatted = [format_item(x, role="core", tag="★符文必出") for x in combo_items[:3]]
        seen_ids = {x["id"] for x in core_formatted}
        if "6656" in seen_ids or "4646" in seen_ids:
            seen_ids.update({"6656", "4646"})

        followup_pool = secondary_candidates + matched_followups + list(template.get("items", [])) + list(template.get("situational_items", []))
        followup_formatted: list[dict[str, Any]] = []
        for it in followup_pool:
            iid = str(it.get("id") or it.get("item") or "")
            if iid and iid not in seen_ids:
                seen_ids.add(iid)
                if iid in ("6656", "4646"):
                    seen_ids.update({"6656", "4646"})
                followup_formatted.append(format_item(it, role="followup", tag="成型补强"))
            if len(core_formatted) + len(followup_formatted) >= 5:
                break

        final_five = (core_formatted + followup_formatted)[:5]
        boots_raw = matched_boots or template.get("boots") or {"id": "3158", "name": "明朗之靴"}
        boots_formatted = format_item(boots_raw, role="boots", tag="👟推荐靴子")

        return {
            "build_name": matched_build,
            "status_label": f"已根据【{matched_source}】质变转轨",
            "is_rune_adapted": True,
            "items": final_five,
            "boots": boots_formatted,
            "full_six_items": [boots_formatted] + final_five,
            "core_count": len(core_formatted),
            "explanation": matched_explanation,
            "augments": aug_details,
            "trigger_augments": trigger_augments,
            "next_combos": next_combos,
        }

    # 2. 未匹配到专属海克斯（或尚未选择海克斯）时的推荐流派
    if hid_str in DUAL_PLAYSTYLE_PROFILES:
        dual = DUAL_PLAYSTYLE_PROFILES[hid_str]
        arch_key = dual.get("archetype") or HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
        template = ARCHETYPE_BUILD_TEMPLATES.get(arch_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
        core_formatted = [format_item(x, role="core", tag="⚡绝活核心") for x in dual["items"][:3]]
        seen_ids = {x["id"] for x in core_formatted}
        if "6656" in seen_ids or "4646" in seen_ids:
            seen_ids.update({"6656", "4646"})

        followup_pool = list(dual.get("followup_items", [])) + list(template.get("items", [])) + list(template.get("situational_items", []))
        followup_formatted = []
        for it in followup_pool:
            iid = str(it.get("id") or it.get("item") or "")
            if iid and iid not in seen_ids:
                seen_ids.add(iid)
                if iid in ("6656", "4646"):
                    seen_ids.update({"6656", "4646"})
                followup_formatted.append(format_item(it, role="followup", tag="成型补强"))
            if len(core_formatted) + len(followup_formatted) >= 5:
                break

        final_five = (core_formatted + followup_formatted)[:5]
        boots_raw = dual.get("boots") or template.get("boots") or {"id": "3158", "name": "明朗之靴"}
        boots_formatted = format_item(boots_raw, role="boots", tag="👟推荐靴子")

        trig_names = "、".join(f"【{t['name']}】" for t in trigger_augments[:4])
        expl = (f"该英雄在 4.0 版本的强力绝活打法。三选一若刷出 {trig_names} 将彻底激活质变！"
                if trig_names else "该英雄在 4.0 版本的强力打法。三选一若刷出对应质变海克斯将彻底激活！")
        return {
            "build_name": dual["build_name"],
            "status_label": "4.0 绝活流派预备推荐（选入海克斯后动态转轨）",
            "is_rune_adapted": False,
            "items": final_five,
            "boots": boots_formatted,
            "full_six_items": [boots_formatted] + final_five,
            "core_count": len(core_formatted),
            "explanation": expl,
            "augments": aug_details,
            "trigger_augments": trigger_augments,
            "next_combos": next_combos,
        }

    archetype_key = HERO_ARCHETYPE_MAP.get(hid_str, "Bruiser_Drain")
    template = ARCHETYPE_BUILD_TEMPLATES.get(archetype_key, ARCHETYPE_BUILD_TEMPLATES["Bruiser_Drain"])
    raw_five = template["items"][:5]
    final_five = [
        format_item(x, role="core" if i < 3 else "followup", tag="核心推荐" if i < 3 else "成型补强")
        for i, x in enumerate(raw_five)
    ]
    boots_raw = template.get("boots") or {"id": "3158", "name": "明朗之靴"}
    boots_formatted = format_item(boots_raw, role="boots", tag="👟推荐靴子")
    return {
        "build_name": template["name"],
        "status_label": "4.0 标准流派推荐（选入海克斯后动态转轨）",
        "is_rune_adapted": False,
        "items": final_five,
        "boots": boots_formatted,
        "full_six_items": [boots_formatted] + final_five,
        "core_count": 3,
        "explanation": "当前为该英雄主流 6 神装公式。局内选择海克斯符文后，将实时推导专属质变出装路线。",
        "augments": aug_details,
        "trigger_augments": trigger_augments,
        "next_combos": next_combos,
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
                            advice_items.append({**_enrich_item(it, store, tag="★联动必出"),
                                                 "source": f"组合联动【{combo['name']}】"})

    # 2. 再查各个单海克斯的专属锚点出装
    for aid in acq_list:
        if aid in AUGMENT_PIVOT_ANCHORS:
            anchor = AUGMENT_PIVOT_ANCHORS[aid]
            for it in anchor.get("items", []):
                if it["id"] not in seen_ids:
                    seen_ids.add(it["id"])
                    advice_items.append({**_enrich_item(it, store, tag="🎯质变核心"),
                                         "source": f"符文【{anchor['build_name']}】"})

    return advice_items

# -*- coding: utf-8 -*-
from unittest.mock import MagicMock
import pytest
from PySide6.QtWidgets import QApplication
from lolhex.engine import Engine
from lolhex.config import Settings
from lolhex.ui.mainwindow import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_mainwindow_synergy_and_must_buy_items_ui(qapp, store, tmp_path):
    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["hero_id"] = "17"
    eng.state["offer"] = {"slots": ["1058", "1029", "2128"]}
    eng.state["phase"] = "ingame"

    overlay = MagicMock()
    overlay.hotkey = None
    win = MainWindow(eng, overlay)
    win.show()
    try:
        # First evaluate without acquired augments
        eng._reevaluate()
        win.refresh()
        
        # Card 0 initially has no combo bonus
        text_before = win.offer_cards[0].text()
        assert "★ 联动加成" not in text_before

        # Pick augment 1225 into acquired list
        eng.record_acquired_augment("1225")
        win.refresh()

        # Acquired chip bar should show 1225 name
        assert "双刀流" in win.acq_chips_label.text()

        # Card 0 (1058 秘术冲拳) should now show combo bonus with acquired 1225 and must buy items
        text_after = win.offer_cards[0].text()
        assert "★ 联动加成" in text_after
        assert "💡 核心必出" in text_after
        assert "破败王者之刃" in text_after

        # Hero build tab should show the acquired augments core items section
        hero_html = win.tab_hero.text()
        assert "★ 本局已持符文专属必出装备" in hero_html
        assert "海妖杀手" in hero_html or "鬼索的狂暴之刃" in hero_html

        # Button for 1225 should be highlighted as selected and allow deselect/change
        eng.state["offer"] = {"slots": ["1225", "1029", "2128"]}
        eng._reevaluate()
        win.refresh()
        assert "本局已选定" in win.offer_pick_btns[0].text()
        assert win.offer_pick_btns[0].isEnabled()
    finally:
        win.close()


def test_badge_layer_strong_synergy_and_equipment_box(qapp, store, tmp_path):
    """验证游戏内三选一悬浮层 BadgeLayer 对海克斯联动及对应装备的强提示与悬浮装备框。"""
    from lolhex.ui.overlay import BadgeLayer
    from lolhex.vision.window import Rect

    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["hero_id"] = "17"  # 迅捷斥候 提莫
    eng.record_acquired_augment("1225")  # 双刀流
    eng.state["offer"] = {
        "slots": ["1058", "1029", "2128"],  # 1058 秘术冲拳 -> 触发【双刀冲拳永动机】
        "boxes": [
            (450, 260, 730, 720),
            (820, 260, 1100, 720),
            (1190, 260, 1470, 720),
        ],
    }
    eng.state["phase"] = "ingame"
    eng._reevaluate()

    snap = eng.snapshot()
    ev = snap["evaluation"]
    assert "双刀极限连打" in ev["advice"] or "联动" in ev["advice"]

    slot0 = ev["slots"][0]
    prof = slot0["synergy_profile"]
    assert prof["kind"] == "combo"
    assert prof["build_name"] == "双刀极限连打"
    assert "双刀流" in prof["synergy_line"]
    assert "双刀极限连打" in prof["synergy_line"]
    assert prof["items_box"] is not None
    assert len(prof["items_box"]["items"]) >= 2
    assert prof["items_box"]["items"][0]["tag"] == "★联动必出"

    layer = BadgeLayer()
    layer.icons = eng.icons
    try:
        layer.update_from(snap, Rect(0, 0, 1920, 1080))
        assert layer._effective_hint(slot0) is not None
        layouts = layer._badge_layout(snap)
        assert len(layouts) == 3
        r0, label0, _col0, lines0, _badge0, hint_rect0, *_ = layouts[0]
        assert "联动" in label0
        assert any("双刀极限连打" in ln for ln in lines0)
        assert any("破败王者之刃" in ln for ln in lines0)
        assert any("含联动" in ln for ln in lines0)
        assert hint_rect0 is not None
    finally:
        layer.close()


def test_mainwindow_and_control_panel_equipment_visibility(qapp, store, tmp_path):
    """验证主界面与游戏内浮窗 ControlPanel 中海克斯对应装备图标、流派标题及后续联动预告。"""
    from lolhex.ui.overlay import ControlPanel

    s = Settings()
    eng = Engine(s, home=tmp_path, store=store)
    eng.state["hero_id"] = "17"  # 提莫
    eng.state["offer"] = {"slots": ["1225", "1029", "2128"]}
    eng.state["phase"] = "ingame"
    eng._reevaluate()

    overlay = MagicMock()
    overlay.hotkey = None
    win = MainWindow(eng, overlay)
    win.show()
    panel = ControlPanel(eng, "top-right")
    try:
        win.refresh()
        # 尚未选入时，第一张卡（1225 双刀流）应展示流派质变核心与可凑组合预告、带图标的核心必出装备
        card0_html = win.offer_cards[0].text()
        assert "🎯 流派质变核心" in card0_html
        assert "极速双刀狂暴流" in card0_html
        assert "海妖杀手" in card0_html
        assert "可凑组合" in card0_html
        assert "蜜蜂极速双刀" in card0_html

        # 选入 1225 后，已持栏应直接显示对应必出装备与后续留意联动海克斯
        eng.record_acquired_augment("1225")
        win.refresh()
        acq_html = win.acq_chips_label.text()
        assert "已持海克斯对应必出装备" in acq_html
        assert "海妖杀手" in acq_html
        assert "后续三选一重点留意联动" in acq_html
        assert "蜜蜂极速双刀" in acq_html or "秘术冲拳" in acq_html

        # 出装与加点页的推荐海克斯列表也应直接展示每个海克斯对应的装备
        hero_html = win.tab_hero.text()
        assert "推荐海克斯（含联动流派与对应必出装备）" in hero_html
        assert "💡对应装备：" in hero_html

        # 游戏内浮窗展开时同样显示联动信息与快捷选入链接
        panel.expanded = True
        panel.update_from(eng.snapshot())
        panel_html = panel.info.text()
        assert "符文专属出装" in panel_html
        assert "👟" in panel_html
        assert "下轮留意" in panel_html
        assert "蜜蜂极速双刀" in panel_html or "秘术冲拳" in panel_html
    finally:
        panel.close()
        win.close()


def test_complete_six_item_builds_and_no_cross_archetype_pollution(store, tmp_path):
    """验证所有 4.0 核心流派（32组组合、53个双流派、44个质变锚点、8套模板）均具备完整6神装且转轨英雄无跨系装备污染。"""
    from lolhex import synergy
    from lolhex.data.icons import IconCache

    icons = IconCache(tmp_path)

    # 1. 验证全部 32 组 AUGMENT_COMBOS 具备 3核心 + 2补强 + 1靴子 = 6件不重复神装
    for c in synergy.AUGMENT_COMBOS:
        core = c.get("core_items") or []
        fup = c.get("followup_items") or []
        boots = c.get("boots") or {}
        assert len(core) == 3, f"Combo {c['name']} core_items != 3"
        assert len(fup) == 2, f"Combo {c['name']} followup_items != 2"
        assert boots.get("id"), f"Combo {c['name']} missing boots"
        six = [boots["id"]] + [x["id"] for x in core] + [x["id"] for x in fup]
        assert len(set(six)) == 6, f"Combo {c['name']} has duplicate items: {six}"
        for iid in six:
            p = icons.local("item", iid, None)
            assert p, f"Missing offline icon for {iid}"

    # 2. 验证全部 53 个 DUAL_PLAYSTYLE_PROFILES 具备完整6神装
    for hid, prof in synergy.DUAL_PLAYSTYLE_PROFILES.items():
        core = prof.get("items") or []
        fup = prof.get("followup_items") or []
        boots = prof.get("boots") or {}
        assert len(core) == 3, f"Dual {hid} items != 3"
        assert len(fup) == 2, f"Dual {hid} followup_items != 2"
        assert boots.get("id"), f"Dual {hid} missing boots"
        six = [boots["id"]] + [x["id"] for x in core] + [x["id"] for x in fup]
        assert len(set(six)) == 6, f"Dual {hid} has duplicate items: {six}"

        # 触发该英雄绝活流派后，get_hero_rune_build 返回完整6神装且无原定位串味
        triggers = sorted(prof.get("candidate_augments") or [])
        rb = synergy.get_hero_rune_build(hid, triggers[:1], store)
        assert len(rb["items"]) == 5
        assert rb["boots"] is not None
        assert len(rb["full_six_items"]) == 6
        assert len({it["id"] for it in rb["full_six_items"]}) == 6

    # 3. 验证全部 44 个 AUGMENT_PIVOT_ANCHORS 具备完整6神装
    for aid, anc in synergy.AUGMENT_PIVOT_ANCHORS.items():
        core = anc.get("items") or []
        fup = anc.get("followup_items") or []
        boots = anc.get("boots") or {}
        assert len(core) == 3, f"Pivot {aid} items != 3"
        assert len(fup) == 2, f"Pivot {aid} followup_items != 2"
        assert boots.get("id"), f"Pivot {aid} missing boots"
        six = [boots["id"]] + [x["id"] for x in core] + [x["id"] for x in fup]
        assert len(set(six)) == 6, f"Pivot {aid} has duplicate items: {six}"

    # 4. 重点验证跨系转轨英雄不会混入原定位装备（如坦克亚索不混入无尽/轻语，AP韦鲁斯不混入海妖/破败）
    rb_yasuo_tank = synergy.get_hero_rune_build("157", ["3049"], store)  # 亚索 + 护甲冲击
    yasuo_item_ids = {it["id"] for it in rb_yasuo_tank["full_six_items"]}
    assert "3031" not in yasuo_item_ids and "3033" not in yasuo_item_ids  # 不含无尽/凡性
    assert rb_yasuo_tank["boots"]["id"] == "3047"  # 铁板靴

    rb_varus_ap = synergy.get_hero_rune_build("110", ["1048"], store)  # 韦鲁斯 + 珠光护手
    varus_item_ids = {it["id"] for it in rb_varus_ap["full_six_items"]}
    assert "6672" not in varus_item_ids and "3153" not in varus_item_ids  # 不含海妖/破败
    assert rb_varus_ap["boots"]["id"] == "3020"  # 法穿鞋



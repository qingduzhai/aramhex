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

        # Button for 1225 should be disabled and marked as acquired if 1225 was in offer
        eng.state["offer"] = {"slots": ["1225", "1029", "2128"]}
        eng._reevaluate()
        win.refresh()
        assert win.offer_pick_btns[0].text() == "✔ 本局已持"
        assert not win.offer_pick_btns[0].isEnabled()
    finally:
        win.close()

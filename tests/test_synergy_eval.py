# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lolhex import recommend
from lolhex import synergy

def test_synergy_rules():
    # 1. Test pivot anchor
    hint_pivot = synergy.get_synergy_item_hint(None, "51", "1134")
    assert hint_pivot is not None
    assert "近战重装" in hint_pivot["title"]
    assert len(hint_pivot["items"]) == 3

    # 2. Test dual playstyle override (Varus with augment 3170 / Q skill augment)
    hint_varus_q = synergy.get_synergy_item_hint(None, "110", "3170")
    assert hint_varus_q is not None
    assert "枯萎" in hint_varus_q["title"] or "AP" in hint_varus_q["title"]

    # 3. Test default archetype (Caitlyn Crit)
    hint_cait = synergy.get_synergy_item_hint(None, "51", "1001")
    assert hint_cait is not None
    assert len(hint_cait["items"]) == 3

    # 4. Test classifier
    c1 = synergy.classify_augment_tier(None, "51", "1134", 0.58, 5.2, 800)
    assert c1["tag"] == "core"

    c2 = synergy.classify_augment_tier(None, "51", "9999", 0.44, -2.5, 500)
    assert c2["tag"] == "trap"

def test_recommend_evaluate_with_synergy(store):
    slots = ["1058", "1134", "1001"]
    res = recommend.evaluate(store, "51", slots)
    assert "slots" in res
    assert len(res["slots"]) == 3

    for r in res["slots"]:
        assert "decision_badge" in r
        assert "must_buy_items" in r
        hint = synergy.get_synergy_item_hint(store, "51", r["augment_id"])
        assert "title" in hint
        assert "items" in hint
        assert len(hint["items"]) > 0
        tag = r.get("decision_tag")
        badge = r.get("decision_badge")
        title = hint["title"]
        items = [x["name"] for x in hint["items"]]
        sys.stdout.buffer.write(f"\nAugment: {r.get('name')} | Badge: {badge} | Route: {title} | Items: {items}\n".encode("utf-8", "replace"))

    sys.stdout.buffer.write(b"\nAll synergy tests passed successfully!\n")

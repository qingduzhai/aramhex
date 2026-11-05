import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lolhex.config import Settings
from lolhex.engine import Engine
from lolhex import recommend

settings = Settings()
engine = Engine(settings)
store = engine.store

test_cases = [
    ('17', '提莫 (Teemo)', ['3009', '1134', '1029']),      # 珠光护手 (AP法爆) vs 亮出你的剑 (AD暴击) vs 狂暴
    ('110', '韦鲁斯 (Varus)', ['1058', '1001', '1332']),   # 秘术冲拳 (穿甲Poke) vs 万用瞄准镜 (特效射手) vs 恶魔契约
    ('54', '墨菲特 (Malphite)', ['3009', '1018', '2128']),  # 珠光护手 (AP核弹) vs 巨像勇气 (纯肉坦克) vs 蛮勇
    ('145', '卡莎 (KaiSa)', ['1134', '1151', '1310']),     # 亮出你的剑 (暴击流) vs 面包奶酪 (极速技能流) vs 召唤流
]

out_lines = []
for hid, hero_name, augment_ids in test_cases:
    out_lines.append('=' * 75)
    out_lines.append(f"【测试英雄】: {hero_name} (ID: {hid})")
    ev = recommend.evaluate(store, hid, augment_ids)
    out_lines.append(f"  全局总评: {ev['advice']}")
    for slot in ev['slots']:
        name = slot.get('name')
        aid = slot.get('augment_id')
        verdict = slot.get('verdict')
        badge = slot.get('decision_badge', '')
        tag = slot.get('decision_tag', '')
        score = slot.get('score')
        win = slot.get('win')
        win_str = f"{win * 100:.1f}%" if win is not None else "无数据"
        hint = slot.get('item_hint')

        out_lines.append("  " + "-" * 65)
        out_lines.append(f"  卡片 [{name}] (ID:{aid}) | 决策: {badge} 【{tag}】 | 状态: {verdict} | 评分: {score} | 胜率: {win_str}")
        if slot.get('reasons'):
            out_lines.append(f"    评估依据: {slot['reasons'][0]}")
        if hint:
            title = hint.get('title', '装备指引')
            items_str = " -> ".join([f"{it['name']}(ID:{it['item']})" for it in hint.get('items', [])])
            out_lines.append(f"    🎯 装备联动路线: {title}")
            out_lines.append(f"       核心装备推荐: {items_str}")
out_lines.append('=' * 75)

sys.stdout.buffer.write(('\n'.join(out_lines) + '\n').encode('utf-8'))

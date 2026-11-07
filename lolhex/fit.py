# -*- coding: utf-8 -*-
"""符文 × 英雄机制契合层（先验）与联动算分推导。

海克斯的价值在这个模式里本质是英雄条件触发的：小蜜蜂要攻击特效载体、蓝色屏障要高耗蓝、
装甲冲击要堆护甲。实测胜率（贝叶斯平滑 Δ）仍是主判据，本层只提供机制先验，用在三处：

1. 打分：score += fit × fade_factor。等价于把平滑基准从「英雄平均」换成「英雄平均 + 机制先验」，
   先验影响随局数淡出（分段模式下按分段与全体局数加权淡出），大样本完全由实测数据说了算；
2. 无数据兜底：「几乎不选」不再是固定 -3.0，而是 机制先验 + 全服Δ折算（只减不加分）；
3. 联动门控：组合加分按候选符文与本英雄的机制契合度折算（COMBO_GATE_FLOOR ~ 100%）。

机制标签是手工与描述对齐的规则知识：量级封顶 ±FIT_CAP、只会在数据不足时影响结果，
数据一多自动失效。英雄只取流派（HERO_ARCHETYPE_MAP），不在表里的英雄先验为 0，
绝活档案（DUAL_PLAYSTYLE_PROFILES）是英雄级覆盖：狗熊是坦克流派，但被动攻击特效契合小蜜蜂。
"""

from __future__ import annotations

from .synergy import DUAL_PLAYSTYLE_PROFILES, HERO_ARCHETYPE_MAP

# ==========================================
# 统一决策阈值常数（recommend.py 与 synergy.py 共用同一套标尺）
# 锚定 16.22 全量 21,311 组（英雄×符文 ≥250 局）实测平滑 Δ 分布：
# P10=-4.27pp, P25=-2.71pp, P50=-1.01pp, P75=+0.68pp, P90=+2.28pp, P95=+3.29pp, P99=+5.70pp
# ==========================================
CORE_MIN_DELTA = 2.5    # 🌟 核心徽章最低实测提升（约前 8% 顶级契合）
CORE_MIN_GAMES = 400    # 🌟 核心徽章最低样本量门槛
SAFE_MIN_WIN = 0.518    # 🛡️ 稳妥徽章最低胜率
SAFE_MIN_DELTA = -0.2   # 🛡️ 稳妥徽章最低相对基准 Δ（亦为 global_fit 零英雄数据上限）
REROLL_BELOW = -0.5     # 建议刷新 / 🎲 慎选徽章共用阈值（低于英雄基准 0.5pp 以上）
CAUTION_BELOW = REROLL_BELOW
TRAP_MAX_DELTA = -1.8   # ⚠️ 陷阱徽章阈值（约后 20% 明显负提升）
TRAP_MIN_GAMES = 300    # ⚠️ 陷阱徽章最低样本量门槛
REROLL_GAP = 2.0        # 比同屏首选低 2 个百分点以上建议刷新

FIT_CAP = 1.5           # 机制先验最大 ±1.5pp，远小于实测 Δ 的典型量级
FIT_SCALE = 0.75        # 机制权重和 → 先验分数的换算系数
DUAL_FIT_MIN = FIT_CAP  # 绝活档案命中的英雄 × 符文：攻略组确认过的质变组合，先验与联动门控都拉满
COMBO_GATE_FLOOR = 0.3  # 机制不契合时，组合加分/扣分按 30% 折算（机制仍在，收益打折）

# 流派 → 机制亲和度（0~1）。没列的机制视为 0：先验只加分不扣分，不契合 = 没有先验。
ARCHETYPE_AFFINITY: dict[str, dict[str, float]] = {
    "ADC_Hybrid_OnHit": {"on_hit": 1.0, "attack_freq": 1.0, "range": 0.8, "crit": 0.5,
                         "ap": 0.3, "movespeed": 0.4},
    "ADC_Crit": {"crit": 1.0, "attack_freq": 0.9, "range": 1.0, "on_hit": 0.5,
                 "movespeed": 0.5, "burst": 0.4},
    "AD_Spellcaster_Poke": {"cdr": 1.0, "range": 0.8, "burst": 0.8, "mana": 0.5,
                            "movespeed": 0.3},
    "AP_Burst_Poke": {"cdr": 1.0, "ap": 1.0, "mana": 0.9, "burst": 1.0, "on_hit": 0.1},
    "AP_Burn_Haste": {"cdr": 1.0, "ap": 0.8, "mana": 0.6, "burst": 0.5, "heal_shield": 0.4},
    "Bruiser_Drain": {"melee": 1.0, "drain": 1.0, "on_hit": 0.6, "hp": 0.6,
                      "movespeed": 0.5, "cdr": 0.5, "attack_freq": 0.4, "armor": 0.4},
    "Tank_Frontline": {"hp": 1.0, "armor": 1.0, "heal_shield": 0.8, "melee": 0.5,
                       "movespeed": 0.3, "drain": 0.3},
    "Assassin_Lethality": {"burst": 1.0, "melee": 1.0, "cdr": 0.8, "movespeed": 0.7,
                           "crit": 0.4},
}

# 符文 → 触发/受益机制（权重 0~1）。覆盖 124 个机制明确的战斗/联动符文；纯经济/随机/雪球娱乐类不设先验（为 0）。
AUGMENT_MECHANICS: dict[str, dict[str, float]] = {
    # --- 核心质变与联动锚点（首批 48 个） ---
    "3086": {"on_hit": 1.0, "attack_freq": 0.6},                # 小蜜蜂：技能附加攻击特效
    "3049": {"armor": 1.0, "melee": 0.4},                       # 装甲冲击：额外护甲转伤害
    "3018": {"attack_freq": 1.0, "crit": 1.0},                  # 大腕：攻速转爆伤
    "1048": {"ap": 0.8, "burst": 1.0},                          # 珠光护手：技能暴击
    "3123": {"ap": 0.6, "burst": 0.8},                          # 珠光手镯
    "1092": {"burst": 1.0, "ap": 0.5},                          # 易损：全技能暴击乘算
    "3078": {"movespeed": 1.0, "attack_freq": 0.6},             # 低音轰鸣
    "3051": {"mana": 1.0, "heal_shield": 0.5},                  # 蓝色屏障：耗蓝转护盾
    "1001": {"armor": 0.8, "hp": 0.6, "ap": 0.4},               # 泰坦的坚决
    "1390": {"ap": 1.0, "cdr": 0.5},                            # 超凡邪恶：命中叠法强
    "1225": {"attack_freq": 1.0, "on_hit": 1.0},                # 双刀流
    "3118": {"cdr": 1.0},                                       # 奥术公理
    "3116": {"crit": 0.8, "burst": 0.6},                        # 将他们放倒
    "1134": {"melee": 1.0, "drain": 0.6},                       # 亮出你的剑
    "1058": {"attack_freq": 0.8, "cdr": 0.8, "on_hit": 0.6},    # 秘术冲拳
    "1019": {"movespeed": 1.0, "attack_freq": 0.6},             # 全凭身法
    "1151": {"cdr": 1.0},                                       # 面包和奶酪
    "1332": {"ap": 1.0},                                        # 恶魔契约
    "1310": {"ap": 0.6, "cdr": 0.6},                            # 虚空幼体
    "1018": {"hp": 1.0, "heal_shield": 0.5},                    # 巨像的勇气
    "1041": {"hp": 1.0},                                        # 歌利亚巨人
    "1115": {"range": 1.0, "attack_freq": 0.5},                 # 万用瞄准镜系列
    "1071": {"range": 1.0, "attack_freq": 0.5},
    "1170": {"range": 1.0, "attack_freq": 0.5},
    "1088": {"cdr": 0.8, "burst": 0.6},                         # 终极刷新
    "1054": {"on_hit": 0.8, "attack_freq": 0.6, "ap": 0.5},     # 物法皆修
    "1149": {"armor": 1.0},                                     # 不动如山
    "1152": {"hp": 1.0},                                        # 钢化你心
    "1015": {"drain": 1.0, "heal_shield": 0.8},                 # 死亡之环：治疗转伤害
    "1029": {"on_hit": 1.0, "cdr": 0.4},                        # 虚幻武器
    "1113": {"range": 0.8, "cdr": 0.6},                         # 老练狙神
    "2087": {"cdr": 1.0},                                       # 大法师
    "3081": {"attack_freq": 0.6, "on_hit": 0.4},                # 命运之武器
    "2140": {"melee": 0.8, "drain": 0.6, "hp": 0.4},            # 升级：贪欲九头蛇
    "1324": {"armor": 0.8, "heal_shield": 1.0},                 # 蛋白粉奶昔
    "2016": {"mana": 0.8, "on_hit": 0.8, "crit": 0.6},          # 注魔
    "1004": {"ap": 0.6, "burst": 0.6},                          # 回归基本功
    "1081": {"movespeed": 0.8, "attack_freq": 0.8, "crit": 0.6},  # 踢踏舞
    "1129": {"crit": 0.6, "ap": 0.6},                           # 神射法师
    "1204": {"hp": 1.0},                                        # 叠角龙
    "2129": {"cdr": 0.8},                                       # 地形专家
    "2010": {"attack_freq": 1.0, "on_hit": 1.0},                # 双发快射
    "2123": {"mana": 0.8, "cdr": 0.6, "ap": 0.6},               # 超负荷
    "2102": {"hp": 1.0, "armor": 0.6},                          # 高压锅
    "1030": {"ap": 0.8, "cdr": 1.0},                            # 尤里卡
    "1056": {"mana": 0.8, "armor": 0.5},                        # 由心及物
    "1133": {"ap": 0.7, "cdr": 0.4},                            # 魔法飞弹
    "2078": {"ap": 0.6, "burst": 0.8},                          # 连锁反应

    # --- 16.22 在役战斗海克斯全量机制扩充（+76 个） ---
    "1005": {"heal_shield": 0.9, "movespeed": 0.5},             # 喂呜喂呜：移速+低血量治疗护盾提升
    "1006": {"melee": 0.7, "on_hit": 0.6, "burst": 0.5},        # 利刃华尔兹：突进附带伤害
    "1013": {"hp": 0.9, "armor": 0.4},                          # 星界躯体：高额生命值
    "1020": {"hp": 0.7, "drain": 0.6},                          # 黎明使者的坚决：低血量持续回复最大生命值
    "1022": {"attack_freq": 0.9},                               # 灵巧：获得攻击速度
    "1026": {"movespeed": 1.0},                                 # 唯快不破：移速差转化为额外伤害
    "1028": {"attack_freq": 0.5, "cdr": 0.5},                   # 侵蚀：持续叠加双抗击碎
    "1036": {"attack_freq": 0.8, "on_hit": 0.8},                # 火上浇油：普攻无限叠加灼烧
    "1037": {"heal_shield": 1.0},                               # 急救用具：治疗和护盾强度
    "1038": {"burst": 0.9},                                     # 有始有终：先攻+黑暗收割爆发
    "1045": {"cdr": 0.9, "ap": 0.6},                            # 炼狱导管：技能叠加灼烧缩减基础冷却
    "1047": {"crit": 0.9},                                      # 关键暴击：获得暴击几率
    "1051": {"attack_freq": 0.9, "on_hit": 0.7},                # 点亮他们！：每4次攻击发射魔法飞弹
    "1057": {"heal_shield": 0.6, "armor": 0.5},                 # 山脉龙魂：脱战护盾
    "1060": {"drain": 0.6, "mana": 0.6},                        # 海洋龙魂：伤害回血回蓝
    "1063": {"armor": 0.8, "melee": 0.6},                       # 狂徒豪气：突进叠双抗
    "1067": {"drain": 0.6, "cdr": 0.6},                         # 活力焕发：施法回复生命值
    "1068": {"cdr": 0.9},                                       # 循环往复：技能急速任务
    "1073": {"movespeed": 0.8, "melee": 0.4},                   # 暗影疾奔：位移/隐身给移速
    "1076": {"heal_shield": 0.9},                               # 天音爆：治疗护盾触发周围真实伤害
    "1077": {"crit": 0.9, "drain": 0.8},                        # 灵魂虹吸：暴击几率+暴击生命偷取
    "1079": {"attack_freq": 1.0, "on_hit": 0.7, "range": 0.5},  # 战争交响乐：致命节奏+征服者
    "1080": {"crit": 0.8, "armor": 0.5},                        # 会心防御：暴击几率减伤
    "1084": {"burst": 0.8},                                     # 穿针引线：双穿
    "1087": {"attack_freq": 0.8, "on_hit": 0.8},                # 台风：普攻分裂飞弹施加特效
    "1095": {"heal_shield": 1.0, "armor": 0.5},                 # 风语者的祝福：治疗护盾加双抗
    "1097": {"ap": 0.9},                                        # 巫师式思考：获得法强
    "1098": {"cdr": 0.9, "movespeed": 0.9},                     # 急急小子：技能急速转移速
    "1103": {"cdr": 0.9},                                       # 面包和黄油：Q技能急速
    "1118": {"heal_shield": 0.9, "crit": 0.7},                  # 会心治疗：治疗护盾暴击
    "1138": {"drain": 1.0},                                     # 渴血：全能吸血
    "1141": {"heal_shield": 1.0},                               # 全心为你：友军治疗护盾强化
    "1150": {"cdr": 0.9},                                       # 面包和果酱：W技能急速
    "1156": {"ap": 1.0},                                        # 沃格勒特的巫师帽：大棒+法强帽合成
    "1180": {"ap": 0.6, "heal_shield": 0.7},                    # 超强大脑：法强转护盾
    "1181": {"hp": 1.0, "attack_freq": 0.5},                    # 重量级打击手：普攻附带最大生命值物伤
    "1195": {"movespeed": 0.6, "attack_freq": 0.5},             # 巨人杀手：移速+对大体型增伤
    "1205": {"ap": 0.9},                                        # 物理转魔法：额外AD转法强
    "1206": {"burst": 0.6, "attack_freq": 0.5},                 # 魔法转物理：法强转额外AD
    "1211": {"burst": 1.0},                                     # 杀戮时间到了：大招储存伤害引爆
    "1214": {"melee": 0.8, "cdr": 0.6},                         # 旋转至胜：旋转技能急速与增伤
    "1305": {"movespeed": 0.9},                                 # 练腿日：移速与减速抗性
    "1311": {"mana": 1.0, "ap": 0.6, "heal_shield": 0.5},       # 溢流：耗蓝翻倍，基于最大法力值提升技能伤害与治疗护盾
    "1318": {"ap": 0.7, "cdr": 0.5},                            # 升级：中娅
    "1319": {"hp": 0.8, "armor": 0.6},                          # 升级：献祭（日炎/璀璨回响）
    "1320": {"crit": 0.7, "burst": 0.8},                        # 升级：收集者
    "1322": {"movespeed": 0.8, "attack_freq": 0.8},             # 罪恶快感：参与击杀加移速攻速
    "1325": {"burst": 0.9},                                     # 玻璃大炮：减血量增真实伤害
    "1328": {"crit": 1.0, "attack_freq": 0.9},                  # 暴击律动：暴击叠攻速
    "1336": {"crit": 1.0, "burst": 0.7},                        # 升级：无尽之刃
    "1344": {"drain": 0.7, "movespeed": 0.6, "hp": 0.5},        # 最终形态：开大给最大生命值护盾、全能吸血与移速
    "1349": {"cdr": 0.9, "burst": 0.6},                         # 终极唤醒：开大重置基础技能冷却
    "1353": {"hp": 1.0},                                        # 坦克引擎：参与击杀叠最大生命值
    "1361": {"hp": 0.9, "armor": 0.8},                          # 艾卡西亚的陷落：日炎+璀璨回响合成
    "1375": {"hp": 0.8, "armor": 0.4},                          # 吞噬灵魂：定身敌方提供最大生命值
    "1379": {"attack_freq": 0.9, "heal_shield": 0.8},           # 升级：花晓之剑
    "1388": {"cdr": 1.0},                                       # 无限循环往复：高额技能急速
    "1415": {"ap": 0.7, "cdr": 0.6},                            # 双生火焰：技能伤害发射魔法飞弹
    "1996": {"cdr": 0.6, "on_hit": 0.6, "drain": 0.5},          # 升级：耀光
    "2004": {"heal_shield": 1.0},                               # 信念者的强化：治疗护盾攒层处决
    "2009": {"attack_freq": 0.8, "on_hit": 0.8},                # 狂热者：普攻额外飞弹施加特效
    "2018": {"cdr": 1.0, "ap": 0.6},                            # 纯粹主义者 - 术师：攻速转技能急速
    "2073": {"drain": 0.9, "cdr": 0.5},                         # 虹吸：技能伤害治疗自身
    "2076": {"armor": 0.9, "melee": 0.5},                       # 保持坚定：技能伤害提供双抗
    "2091": {"melee": 0.9, "drain": 0.8},                       # 无尽大杀四方：环形挥砍物伤与治疗
    "2096": {"range": 0.8, "attack_freq": 0.8},                 # 小小的额外帮助：技能期间加射程和攻速
    "2100": {"cdr": 1.0},                                       # 急速之追求：技能命中叠急速
    "2104": {"heal_shield": 1.0},                               # 灵魄炸弹：治疗护盾攒群体治疗护盾弹
    "2126": {"attack_freq": 0.8, "cdr": 0.7},                   # 装填：普攻缩减技能冷却
    "2132": {"drain": 0.9},                                     # 术士果汁盒：全能吸血
    "2133": {"range": 0.6, "attack_freq": 0.7, "on_hit": 0.6},  # 仁慈打击：施法后普攻加射程攻速与附伤
    "2138": {"armor": 0.9},                                     # 自适应防护：技能命中叠双抗
    "2141": {"melee": 0.9, "drain": 0.7, "hp": 0.6},            # 终极九头蛇
    "2143": {"melee": 0.8, "drain": 0.8, "hp": 0.5},            # 升级：焚天
    "2144": {"heal_shield": 0.9},                               # 加固护盾
    "2157": {"melee": 0.8, "drain": 0.8},                       # 升级：死亡之舞
    "3016": {"attack_freq": 1.0, "on_hit": 0.9},                # 伤不过三：三环真实伤害
    "3025": {"heal_shield": 0.8, "movespeed": 0.6},             # 音之屏障：护盾提供移速
    "3036": {"mana": 0.9, "cdr": 0.6, "ap": 0.5},               # 翻倍时间：连招魔伤并提供最大法力值
    "3048": {"attack_freq": 0.7, "on_hit": 0.7},                # 弹跳蜜蜂：施法后普攻弹跳
    "3052": {"range": 1.0, "on_hit": 0.7},                      # 远射天资：远距离普攻附带攻击特效
    "3053": {"hp": 0.9, "melee": 0.5},                          # 热舞怪兽：施法加生命值与减速
    "3055": {"cdr": 0.9},                                       # 终极循环往复：终极技能急速
    "3058": {"attack_freq": 1.0, "on_hit": 0.9},                # 嗡嗡怪兽：AD转攻速且普攻附带魔法特效
    "3059": {"mana": 1.0, "ap": 1.0},                           # 没法力，没问题：装备法力值转法强且总法强提升
    "3085": {"attack_freq": 0.9},                               # 灵魂乐流：施法提供攻速
    "3088": {"attack_freq": 0.7, "cdr": 0.7, "on_hit": 0.5},    # 深红钴蓝闪光：普攻触发技能标记并减CD
    "3094": {"ap": 1.0},                                        # 巫妖大脑：获得法强
    "3129": {"attack_freq": 0.7, "drain": 0.8, "cdr": 0.5},     # 吸元秘术：普攻附伤回血、施法减CD
    "3131": {"attack_freq": 0.8, "drain": 0.9, "melee": 0.5},   # 屹立不倒：低血量加攻速与生命偷取
    "3134": {"armor": 0.8, "melee": 0.7, "attack_freq": 0.5},   # 孤勇者：周围敌人越多加攻速与双抗
    "3149": {"heal_shield": 1.0},                               # 一起抱抱：治疗护盾折射友军
    "3150": {"ap": 0.8, "burst": 0.9},                          # 升级：风暴狂涌
    "3163": {"heal_shield": 0.9, "ap": 0.5},                    # 迷人蝴蝶：治疗护盾攒蝴蝶飞弹
}

MECHANIC_CN = {"on_hit": "攻击特效", "attack_freq": "普攻频次", "range": "射程", "crit": "暴击",
               "ap": "法强", "cdr": "技能急速", "mana": "蓝量", "hp": "生命成长", "armor": "双抗",
               "heal_shield": "治疗护盾", "melee": "近战", "drain": "吸血回复",
               "movespeed": "移速", "burst": "技能爆发"}


def fit_adjustment(augment_id: str | None, hero_id: str | None) -> tuple[float, str]:
    """机制契合先验 (Δpp, 说明)，∈ [0, FIT_CAP]。

    只加分不扣分：不契合 = 没有先验（数据说了算），不发明负先验。
    未知英雄 / 未收录符文返回 (0.0, "")；绝活档案是英雄级覆盖（至少 DUAL_FIT_MIN）。
    """
    aid = str(augment_id or "")
    hid = str(hero_id or "")
    dual = DUAL_PLAYSTYLE_PROFILES.get(hid)
    dual_hit = bool(dual and aid in dual["candidate_augments"])
    mech = AUGMENT_MECHANICS.get(aid)
    aff = ARCHETYPE_AFFINITY.get(HERO_ARCHETYPE_MAP.get(hid, ""), {})

    fit = 0.0
    tops: list[str] = []
    if mech and aff:
        contrib = sorted(((w * aff.get(m, 0.0), m) for m, w in mech.items()), reverse=True)
        raw = sum(c for c, _ in contrib)
        fit = max(-FIT_CAP, min(FIT_CAP, raw * FIT_SCALE))
        tops = [MECHANIC_CN[m] for c, m in contrib if c > 0.15][:2]
    if dual_hit:
        fit = max(fit, DUAL_FIT_MIN)

    if fit <= 0:
        return 0.0, ""
    if dual_hit and not tops:
        note = "绝活机制契合（英雄技能组直接触发）"
    elif tops:
        note = "机制契合：" + "、".join(tops)
    else:
        note = "机制契合"
    return round(fit, 2), note


def combo_gate(augment_id: str | None, hero_id: str | None) -> float:
    """联动分折算系数：机制契合拉满为 1.0，完全不契合为 COMBO_GATE_FLOOR；未识别英雄不折算。"""
    if not hero_id:
        return 1.0
    f, _ = fit_adjustment(augment_id, hero_id)
    return round(COMBO_GATE_FLOOR + (1.0 - COMBO_GATE_FLOOR) * min(f, FIT_CAP) / FIT_CAP, 3)


# ==========================================
# 符文对交互算分：加多少分由机制推导，不再用攻略视频拍的手工值
# ==========================================
#
# 两个维度：
# 1. 交互类型（基础分）：两个符文怎么相互作用——
#    multiplicative 乘算：一个产出触发（暴击/特效），另一个放大同一乘区，伤害按乘法叠；
#    frequency      频次放大：一个产出触发，另一个提高触发频率（攻速/施法循环）；
#    resource       资源转化：一个产出资源（蓝量/法强/护甲/急速），另一个消费或转化它；
#    additive       线性叠加：同属性堆叠（双巨人堆血），边际递减，最弱。
# 2. 机制耦合度（系数 0~1）：两个符文在 AUGMENT_MECHANICS 里共享的维度按 min(权重) 求和，
#    共享越多、权重越高，联动越强。共享 1.0 以上视为满耦合。
#
# 基础分的量级锚定实测 Δ（典型 ±3pp，P99=+5.70pp）：顶级质变组合 5~6pp，线性叠加 1~2.5pp，
# 和单卡强度差同量级，再由递减叠加和 COMBO_BONUS_CAP 兜底。

INTERACTION_BASE = {"multiplicative": 6.0, "frequency": 5.5, "resource": 5.0, "additive": 2.5}
INTERACTION_CN = {"multiplicative": "乘算", "frequency": "频次放大",
                  "resource": "资源转化", "additive": "线性叠加"}

CURATED_COUPLING_FLOOR = 0.5  # 人工确认有交互、但机制向量没覆盖到的组合：按 0.5 耦合计（模型不完整，不是没交互）
GENERIC_MIN_COUPLING = 0.4    # 未收录的组合：耦合至少这么多才给推算分
GENERIC_CAP = 3.0             # 推算分封顶：没经过人工评审的组合不给高分
PAIR_SHRINK_K = 200           # 双符文实测 pairs 收缩常数：200 局时实测 Lift 与机制先验各信一半


def mechanic_coupling(aid_a: str | None, aid_b: str | None) -> tuple[float, list[str]]:
    """两个符文共享机制维度的耦合度（min 权重求和）和前两个共享维度的中文名。"""
    ma = AUGMENT_MECHANICS.get(str(aid_a or ""))
    mb = AUGMENT_MECHANICS.get(str(aid_b or ""))
    if not ma or not mb:
        return 0.0, []
    shared = sorted(((min(wa, mb[m]), m) for m, wa in ma.items() if m in mb), reverse=True)
    return sum(c for c, _ in shared), [MECHANIC_CN[m] for _, m in shared[:2]]


def infer_interaction_type(aid_a: str | None, aid_b: str | None) -> str:
    """没人工标类型时按共享机制推断：触发/频次→frequency，暴击/爆发→乘算，资源维度→转化，其余→叠加。"""
    ma = AUGMENT_MECHANICS.get(str(aid_a or ""), {})
    mb = AUGMENT_MECHANICS.get(str(aid_b or ""), {})
    shared = set(ma) & set(mb)
    if shared & {"on_hit", "attack_freq", "movespeed"}:
        return "frequency"
    if shared & {"crit", "burst"}:
        return "multiplicative"
    if shared & {"mana", "ap", "cdr", "armor", "drain", "heal_shield"}:
        return "resource"
    return "additive"


def computed_combo_bonus(aid_a: str | None, aid_b: str | None,
                         itype: str | None = None, curated: bool = False) -> dict:
    """符文对联动加分的机制推导值。

    返回 {bonus, type, coupling, shared}：
    - curated=True（在人工组合表里）：共享机制为 0 时按 CURATED_COUPLING_FLOOR 计——
      人工确认过有交互，是机制模型没覆盖（如低音轰鸣×终极刷新的施法循环），不是没有；
    - curated=False（推算）：耦合不到 GENERIC_MIN_COUPLING 不给分，且封顶 GENERIC_CAP。
    """
    coupling, shared = mechanic_coupling(aid_a, aid_b)
    itype = itype or infer_interaction_type(aid_a, aid_b)
    raw_coupling = coupling
    if coupling <= 0 and curated:
        coupling = CURATED_COUPLING_FLOOR
    bonus = INTERACTION_BASE[itype] * min(1.0, coupling)
    if not curated:
        if raw_coupling < GENERIC_MIN_COUPLING:
            bonus = 0.0
        bonus = min(bonus, GENERIC_CAP)
    return {"bonus": round(bonus, 1), "type": itype, "coupling": round(raw_coupling, 2),
            "shared": shared}


def shrink_pair_bonus(mech_bonus: float, pair_row: dict | None,
                      baseline_win: float | None, k_pair: int = PAIR_SHRINK_K) -> dict:
    """将机制推导联动分（先验）与双符文实测共现胜率（hero_augment_pairs.json）按贝叶斯收缩融合：

        shrunk = (n * empirical_lift + k_pair * mech_bonus) / (n + k_pair)

    - 无实测 pairs 数据（pair_row 为空或无 baseline_win）时：100% 返回 mech_bonus，平滑退化；
    - 样本充足（n >> k_pair）时：由实测共现 Lift 主导（若某网红组合实测反而掉胜率，会如实收缩为低分或负分）。
    """
    if not pair_row or baseline_win is None:
        return {"bonus": round(mech_bonus, 2), "empirical_lift": None, "games": 0, "win": None}
    games = int(pair_row.get("games") or 0)
    win = pair_row.get("win")
    if games <= 0 or win is None:
        return {"bonus": round(mech_bonus, 2), "empirical_lift": None, "games": 0, "win": None}
    emp_lift = (win - baseline_win) * 100.0
    shrunk = (games * emp_lift + k_pair * mech_bonus) / (games + k_pair)
    return {
        "bonus": round(shrunk, 2),
        "empirical_lift": round(emp_lift, 2),
        "games": games,
        "win": win,
    }

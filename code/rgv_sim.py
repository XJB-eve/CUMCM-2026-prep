# -*- coding: utf-8 -*-
"""
2018 CUMCM B 题  智能 RGV 动态调度  —  离散事件仿真
================================================================
情形一：单工序（每台 CNC 均可独立加工）
调度原则：就近原则（最小时间代价 f = t_move + t_updown + t_wash）

系统布局（4 列 × 2 排，共 8 台 CNC）：
        列0    列1    列2    列3
 右侧   CNC1   CNC3   CNC5   CNC7      (奇数号)
 左侧   CNC2   CNC4   CNC6   CNC8      (偶数号)
 RGV 初始位于 CNC1# / CNC2# 正中间（列0）。
 假设：同列两台 CNC(奇/偶) 间移动时间为 0（题目假设 2）。

参数三组数据均取自 2018-B 官方赛题（并经获奖论文源码逐字核对）。
"""

SHIFT = 8 * 3600          # 一个班次 = 8 小时 = 28800 秒

# ---- 三组系统作业参数 -------------------------------------------------------
#   mv  = (移动1单位, 移动2单位, 移动3单位) 秒
#   t0  = 单工序加工时间 秒
#   ldw = (奇号CNC上下料, 偶号CNC上下料) 秒
#   wash= 清洗时间 秒
#   p1,p2 = 双工序 工序1 / 工序2 加工时间 秒
GROUPS = {
    1: dict(mv=(20, 33, 46), t0=560, ldw=(28, 31), wash=25, p1=400, p2=378),
    2: dict(mv=(23, 41, 59), t0=580, ldw=(30, 35), wash=30, p1=280, p2=500),
    3: dict(mv=(18, 32, 46), t0=545, ldw=(27, 32), wash=25, p1=455, p2=182),
}


def col(k):
    """CNC 编号 k(1..8) -> 所在列号 0..3"""
    return (k - 1) // 2


def make_move(mv):
    """返回列间移动时间函数：move(c1,c2) = mv[列距-1]，同列为 0"""
    table = [0, mv[0], mv[1], mv[2]]
    return lambda c1, c2: table[abs(c1 - c2)]


def updown(k, ldw):
    """CNC k 的一次上下料时间：奇号取 ldw[0]，偶号取 ldw[1]"""
    return ldw[0] if k % 2 == 1 else ldw[1]


def simulate_single(g, record=False, fail_p=0.0, rng=None):
    """
    单工序离散事件仿真（就近原则）。
    返回加工完成的成料数量 count；record=True 时同时返回调度明细。
    fail_p>0 时启用随机故障（情形三）：每装入一件生料以 fail_p 概率故障，
      故障件报废（不计数），该 CNC 停机 = 部分加工时长 + 维修时长 U(600,1200)s。
    """
    move = make_move(g['mv'])
    t0, wash, ldw = g['t0'], g['wash'], g['ldw']

    t = 0                     # 当前时刻
    pos = 0                   # RGV 当前所在列（初始列 0 = CNC1#/2# 中间）
    finish = [None] * 9       # finish[k]: CNC k 当前料的加工完成时刻；None=空机床
    good = [True] * 9         # good[k]: CNC k 在加工的料是否合格（故障则报废）
    count = 0
    log = []

    while True:
        # 班次结束：RGV 在 8 小时内不再有空闲去承接新料 -> 停止
        if t >= SHIFT:
            break

        # ---- 就近原则选料 ----------------------------------------------------
        # RGV 空闲时移动至候选 CNC 并可就地等待；下料开始时刻
        #   start = max(RGV 到达时刻, 该 CNC 加工完成时刻)。
        # 选取规则：下料开始最早者（尽早取料、减少虚耗）；并列时取时间代价
        #   f = 移动 + 上下料 + 清洗 最小者（即“就近”）；再并列取小编号。
        best = None           # (下料开始, 时间代价, k)
        for k in range(1, 9):
            mvt = move(pos, col(k))
            arrive = t + mvt
            start = arrive if finish[k] is None else max(arrive, finish[k])
            cost = mvt + updown(k, ldw) + wash
            key = (start, cost, k)
            if best is None or key < best:
                best = key

        start, _, k = best
        loaded = finish[k] is not None            # 该机床此前是否已有产出
        harvest = loaded and good[k]              # 仅合格熟料才可收成
        unload_done = start + updown(k, ldw)       # 下料/上料（同时）完成时刻

        if harvest:
            count += 1                            # 取出一件熟料 -> 清洗后成 1 件成料
            if record:
                log.append((count, k, start, unload_done))
            t = unload_done + wash                # RGV 清洗占用，位置不变
        else:
            t = unload_done                       # 首次上料或报废件，无清洗

        # 装入新生料，判定是否故障
        if fail_p and rng.random() < fail_p:
            fail_off = rng.random() * t0          # 加工到中途发生故障
            repair = 600 + 600 * rng.random()     # 维修 10~20 分钟
            finish[k] = unload_done + fail_off + repair
            good[k] = False                       # 该料报废
        else:
            finish[k] = unload_done + t0          # 新生料正常加工
            good[k] = True
        pos = col(k)

    return (count, log) if record else count


def schedule_single(g, n_pieces=16):
    """情形一调度明细：返回前 n_pieces 件成料的
    (物料序号, 加工CNC编号, 上料开始时刻, 下料开始时刻)，按下料先后排序。"""
    move = make_move(g['mv'])
    t0, wash, ldw = g['t0'], g['wash'], g['ldw']
    t, pos = 0, 0
    finish = [None] * 9
    load_start = [None] * 9          # 各 CNC 当前料的上料开始时刻
    pieces = []                      # (cnc, 上料开始, 下料开始)
    while len(pieces) < n_pieces + 8:
        best = None
        for k in range(1, 9):
            mvt = move(pos, col(k))
            arrive = t + mvt
            start = arrive if finish[k] is None else max(arrive, finish[k])
            key = (start, mvt + updown(k, ldw) + wash, k)
            if best is None or key < best:
                best = key
        start, _, k = best
        loaded = finish[k] is not None
        unload_done = start + updown(k, ldw)
        if loaded:
            pieces.append((k, load_start[k], start))   # 该 CNC 旧料此刻下料
            t = unload_done + wash
        else:
            t = unload_done
        load_start[k] = start                          # 新料此刻上料
        finish[k] = unload_done + t0
        pos = col(k)
    pieces.sort(key=lambda p: p[2])
    return [(i + 1, k, ls, us) for i, (k, ls, us) in enumerate(pieces[:n_pieces])]


# ============================================================================
# 情形二：双工序
# 忠实移植自官方获奖论文附录的定步长时间步进算法（就近原则）。
#   typ[k-1] ∈ {0,1}：0 = 工序1 CNC，1 = 工序2 CNC
#   full ∈ {0,1}：RGV 是否正载着一件半熟料
#   S[k]：CNC k 剩余加工时间（>0 加工中，≤0 已完成待取）
#   B[k]：CNC k 是否有产出（工序1→半熟料 / 工序2→熟料）
#   L[full][i][j]：i→j 移动时间；full=1 时禁止移动到同工序类型的机床（置 INF）
# ============================================================================
INF = 5000


def _colidx(x):
    """1-索引列号：CNC x -> (x+1)//2（与官方 C 代码整除一致）"""
    return (x + 1) // 2


def simulate_double(g, typ, T_shift=SHIFT, fail_p=0.0, rng=None, principle='near'):
    """双工序仿真，typ 为长度 8 的 0/1 列表，返回成料数。
    principle ∈ {'near','fifo','hrrn'}：就近 / 先到先服务 / 高响应比优先。
    fail_p>0 时启用随机故障（情形三）。"""
    ons, tws, ths = g['mv']
    pro = [g['p1'], g['p2']]
    rep = [0] + [g['ldw'][0] if k % 2 == 1 else g['ldw'][1] for k in range(1, 9)]
    pd = g['wash']
    TT = [0] + list(typ)                       # 1-索引工序类型
    move_units = (0, ons, tws, ths)

    # 预计算移动矩阵 L[full][i][j]
    L = [[[0] * 9 for _ in range(9)] for _ in range(2)]
    for k in range(2):
        for i in range(1, 9):
            for j in range(1, 9):
                d = abs(_colidx(j) - _colidx(i))
                v = move_units[d] if d <= 3 else 0
                if k == 1 and TT[i] == TT[j]:  # 满载禁止同类型机床
                    v = INF
                L[k][i][j] = v

    full = 0
    S = [0] * 9      # 剩余加工时间
    B = [0] * 9      # 是否有产出
    T = [0] * 9      # 各 CNC 的时间代价
    num = 0
    time = 0
    pos = 0          # RGV 初始位于 CNC1#/2# 中间

    while time < T_shift:
        # ---- 评估：计算到各 CNC 的时间代价 ----
        for j in range(1, 9):
            T[j] = L[full][pos][j] + rep[j] + B[j] * TT[j] * pd
            if (S[j] - L[full][pos][j]) > 0:            # RGV 到达时仍在加工 -> 需等待，弃选
                T[j] += INF
            if full == 0 and B[j] == 0 and TT[j]:       # 空手去无熟料的工序2机床 -> 无意义
                T[j] += INF
        # ---- 选择：按调度原则选下一台 CNC ----
        valid = [j for j in range(1, 9) if T[j] < INF]      # 到达即可服务的候选
        if not valid or principle == 'near':
            nx = 1                                          # 就近：最小时间代价
            for j in range(2, 9):
                if T[j] < T[nx]:
                    nx = j
        elif principle == 'fifo':                           # 先到先服务：等待最久（S 最小）
            js = min(valid, key=lambda j: (S[j], j))
            nx = js if S[js] < 0 else min(valid, key=lambda j: (T[j], j))
        elif principle == 'random':                         # 随机调度（用于最优性检验）
            nx = valid[rng.randrange(len(valid))]
        else:                                               # HRRN：响应比 (-S+T)/T 最大
            nx = max(valid, key=lambda j: ((-S[j] + T[j]) / T[j], -j))

        if T[nx] < INF:                                 # 可直接前往
            tc = T[nx]
            for i in range(1, 9):
                S[i] -= tc                              # 时间推进 tc，各 CNC 同步扣减
            if TT[nx] == 0:
                S[nx] = pro[0]                          # 工序1：装生料，加工 pro1
            elif TT[nx] == 1 and full == 1:
                S[nx] = pro[1] - B[nx] * pd             # 工序2：装半熟料，加工 pro2
            time += tc
            num += B[nx] * TT[nx]                       # 服务一台有熟料的工序2机床 -> 成料 +1
            pos = nx
            t_full = full
            full = B[nx] * (1 - TT[nx])                 # 从工序1取到半熟料则满载
            B[nx] = 1 if TT[nx] == 0 else t_full
            # 随机故障：新装入料以 fail_p 概率故障、报废、停机维修
            if fail_p and B[nx] and rng.random() < fail_p:
                S[nx] = int(rng.random() * pro[TT[nx]] + 600 + 600 * rng.random())
                B[nx] = 0
        else:                                           # 无可服务机床，等待 1 秒
            time += 1
            for i in range(1, 9):
                S[i] -= 1
    return num


def simulate_single_fs(g, principle='near'):
    """单工序定步长仿真（忠实官方 Case1 算法），支持三种调度原则。
    用于验证：单工序下就近/FIFO/HRRN 三原则结果完全相同（均 383/360/393）。"""
    ons, tws, ths = g['mv']
    pro = g['t0']
    rep = [0] + [g['ldw'][0] if k % 2 else g['ldw'][1] for k in range(1, 9)]
    pd = g['wash']
    mu = (0, ons, tws, ths)
    L = [[0] * 9 for _ in range(9)]
    for i in range(1, 9):
        for j in range(1, 9):
            d = abs(_colidx(j) - _colidx(i))
            L[i][j] = mu[d] if d <= 3 else 0
    S = [0] * 9
    B = [0] * 9
    T = [0] * 9
    num = time = pos = 0
    while time < SHIFT:
        for j in range(1, 9):
            T[j] = L[pos][j] + rep[j] + B[j] * pd
            if (S[j] - L[pos][j]) > 0:
                T[j] += INF
        valid = [j for j in range(1, 9) if T[j] < INF]
        if not valid or principle == 'near':
            nx = min(range(1, 9), key=lambda j: (T[j], j))
        elif principle == 'fifo':
            js = min(valid, key=lambda j: (S[j], j))
            nx = js if S[js] < 0 else min(valid, key=lambda j: (T[j], j))
        else:
            nx = max(valid, key=lambda j: ((-S[j] + T[j]) / T[j], -j))
        if T[nx] < INF:
            for i in range(1, 9):
                S[i] -= T[nx]
            S[nx] = pro - B[nx] * pd
            time += T[nx]
            num += B[nx]
            pos = nx
            B[nx] = 1
        else:
            time += 1
            for i in range(1, 9):
                S[i] -= 1
    return num


def enumerate_layouts(g, principle='near'):
    """遍历 2^8=256 种工序分配，返回该原则下 (最大成料数, 最优布局元组)。"""
    from itertools import product
    best = (-1, None)
    for combo in product((0, 1), repeat=8):
        if 0 not in combo or 1 not in combo:           # 至少各有一台工序1/工序2
            continue
        n = simulate_double(g, list(combo), principle=principle)
        if n > best[0]:
            best = (n, combo)
    return best


# 情形二各组最优 (工序布局, 达到该最优的调度原则)，由三原则各自枚举后取最优得出
BEST_LAYOUT = {
    1: [0, 1, 0, 1, 0, 1, 0, 1],   # 1-2-1-2-1-2-1-2
    2: [1, 0, 1, 0, 1, 0, 1, 0],   # 2-1-2-1-2-1-2-1
    3: [0, 0, 1, 0, 1, 0, 0, 1],   # 1-1-2-1-2-1-1-2
}
BEST_PRINCIPLE = {1: 'near', 2: 'fifo', 3: 'near'}   # 组2 需 FIFO/HRRN 方达 212


def monte_carlo(kind, g, typ=None, n=3000, fail_p=0.01, seed=20260720, principle='near'):
    """情形三蒙特卡洛：重复 n 次带故障仿真，返回 (均值, 最小, 最大, 全部样本)。"""
    import random
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        if kind == 'single':
            vals.append(simulate_single(g, fail_p=fail_p, rng=rng))
        else:
            vals.append(simulate_double(g, typ, fail_p=fail_p, rng=rng, principle=principle))
    return sum(vals) / len(vals), min(vals), max(vals), vals


def random_optimality_check(gid, n=20000, seed=1):
    """最优性检验：在最优布局上随机调度 n 次，看能否超过启发式最优解。
    返回 (启发式最优, 随机最好, 超过次数)。"""
    import random
    rng = random.Random(seed)
    g = GROUPS[gid]
    heur = simulate_double(g, BEST_LAYOUT[gid], principle=BEST_PRINCIPLE[gid])
    best_rand, exceed = 0, 0
    for _ in range(n):
        v = simulate_double(g, BEST_LAYOUT[gid], principle='random', rng=rng)
        best_rand = max(best_rand, v)
        exceed += (v > heur)
    return heur, best_rand, exceed


if __name__ == '__main__':
    print("情形一（单工序）三原则 —— 复现官方结果 383 / 360 / 393")
    print("-" * 56)
    ref1 = {1: 383, 2: 360, 3: 393}
    ok = True
    for gid in (1, 2, 3):
        near = simulate_single(GROUPS[gid])                      # 事件驱动（就近）
        fifo = simulate_single_fs(GROUPS[gid], 'fifo')           # 定步长
        hrrn = simulate_single_fs(GROUPS[gid], 'hrrn')
        ok &= (near == fifo == hrrn == ref1[gid])
        print(f"  Group{gid}: 就近{near} FIFO{fifo} HRRN{hrrn}  "
              f"official {ref1[gid]}  eff {near/8:.3f}/h")
    print("ALL REPRODUCED (三原则一致)" if ok else "MISMATCH")

    print("\n情形二（双工序）三原则 × 256 布局枚举 —— 取最优")
    print("-" * 56)
    ref2 = {1: 253, 2: 212, 3: 241}
    for gid in (1, 2, 3):
        res = {p: enumerate_layouts(GROUPS[gid], p) for p in ('near', 'fifo', 'hrrn')}
        best_p = max(res, key=lambda p: res[p][0])
        n, layout = res[best_p]
        lab = '-'.join('1' if t == 0 else '2' for t in layout)
        print(f"  Group{gid}: 就近{res['near'][0]} FIFO{res['fifo'][0]} "
              f"HRRN{res['hrrn'][0]} -> 最优{n}({best_p}) {lab} "
              f"eff {n/8:.3f}/h (official {ref2[gid]})")

    print("\n情形三（随机故障 1%）蒙特卡洛 3000 次 —— 效率下降评估")
    print("-" * 56)
    for gid in (1, 2, 3):
        pr = BEST_PRINCIPLE[gid]
        b_s = simulate_single(GROUPS[gid])
        m_s, lo_s, hi_s, _ = monte_carlo('single', GROUPS[gid])
        b_d = simulate_double(GROUPS[gid], BEST_LAYOUT[gid], principle=pr)
        m_d, lo_d, hi_d, _ = monte_carlo('double', GROUPS[gid], typ=BEST_LAYOUT[gid], principle=pr)
        print(f"  Group{gid} 单工序 {b_s}->均{m_s:5.1f}(区间{lo_s}-{hi_s}) 降{(b_s-m_s)/8:.3f}/h"
              f" | 双工序 {b_d}->均{m_d:5.1f} 降{(b_d-m_d)/8:.3f}/h")



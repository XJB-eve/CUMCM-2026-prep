# -*- coding: utf-8 -*-
"""生成论文插图（统一专业风格），输出到 CUMCMThesis/figures/。运行：py make_figures.py"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import rgv_sim as R

# ---- 中文字体 ----
for f in ['Microsoft YaHei', 'SimHei', 'SimSun']:
    try:
        matplotlib.font_manager.findfont(f, fallback_to_default=False)
        plt.rcParams['font.sans-serif'] = [f]
        break
    except Exception:
        continue

# ---- 统一专业风格 ----
plt.rcParams.update({
    'axes.unicode_minus': False,
    'font.size': 11,
    'axes.titlesize': 12.5,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.edgecolor': '#8a8a8a',
    'axes.linewidth': 0.9,
    'axes.grid': True,
    'axes.axisbelow': True,
    'grid.color': '#e8e8e8',
    'grid.linewidth': 0.8,
    'xtick.color': '#444444',
    'ytick.color': '#444444',
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
})
BLUE, RED, GREEN, GRAY = '#2E5A88', '#C0562E', '#3E8E6F', '#8a8a8a'
DPI = 200

OUT = os.path.join('..', 'CUMCMThesis', 'figures')
os.makedirs(OUT, exist_ok=True)


def _clean(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, bbox_inches='tight', pad_inches=0.08)
    plt.close(fig)
    print('  saved', name)


# ========== 图：系统布局示意 ==========
def fig_layout():
    fig, ax = plt.subplots(figsize=(8.2, 3.5))
    for c in range(4):
        x = 1 + c * 2.35
        for yc, tag in [(2.25, 2 * c + 2), (0.15, 2 * c + 1)]:
            ax.add_patch(FancyBboxPatch((x, yc), 1.65, 1.05, boxstyle="round,pad=0.04",
                         fc='#eef4fb', ec=BLUE, lw=1.6))
            ax.text(x + 0.82, yc + 0.52, f'CNC{tag}#', ha='center', va='center',
                    fontsize=10.5, color='#1b3a5c')
    ax.add_patch(plt.Rectangle((0.3, 1.35), 10.55, 0.5, fc='#ededed', ec='#7a7a7a', lw=1))
    ax.text(2.6, 1.6, 'RGV 直线轨道', ha='center', va='center', fontsize=10.5, color='#333')
    ax.add_patch(FancyBboxPatch((4.95, 1.3), 1.15, 0.6, boxstyle="round,pad=0.03",
                 fc=RED, ec='#7a2f18', lw=1))
    ax.text(5.52, 1.6, 'RGV', ha='center', va='center', color='w', fontsize=9.5, weight='bold')
    ax.annotate('上料传送带', xy=(0.3, 1.6), xytext=(-1.55, 1.6), fontsize=9.5, va='center',
                color=GREEN, arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=1.4))
    ax.annotate('', xy=(12.1, 1.6), xytext=(10.85, 1.6),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=1.4))
    ax.text(12.2, 1.6, '下料传送带', fontsize=9.5, va='center', color=GREEN)
    ax.set_xlim(-2.5, 14.2)
    ax.set_ylim(-0.35, 3.6)
    ax.axis('off')
    ax.set_title('智能加工系统布局示意（8 台 CNC 分列轨道两侧，RGV 往返上下料与清洗）',
                 fontsize=11.5)
    save(fig, 'layout.png')


# ========== 图：技术路线流程图 ==========
def fig_flowchart():
    fig, ax = plt.subplots(figsize=(5.6, 6.4))
    steps = [
        ('系统机理刻画', 'RGV 移动 / 上下料 / 清洗 / 唯一性时序', '#eef4fb', BLUE),
        ('0-1 规划建模', '以成料数最大为目标；识别为 NP 问题', '#eef4fb', BLUE),
        ('三原则离散事件仿真', '就近原则 · FIFO 原则 · HRRN 原则', '#fdf0e9', RED),
        ('蒙特卡洛检验', '随机故障评估 + 随机调度最优性检验', '#ecf6f1', GREEN),
        ('调度策略与系统效率', '给出具体调度方案与作业效率', '#f2f2f2', '#555555'),
    ]
    n = len(steps)
    y0, h, gap = 5.55, 0.82, 0.44
    for i, (title, sub, fc, ec) in enumerate(steps):
        y = y0 - i * (h + gap)
        ax.add_patch(FancyBboxPatch((0.6, y), 4.4, h, boxstyle="round,pad=0.04",
                     fc=fc, ec=ec, lw=1.7))
        ax.text(2.8, y + h * 0.62, title, ha='center', va='center',
                fontsize=11.5, weight='bold', color='#222')
        ax.text(2.8, y + h * 0.22, sub, ha='center', va='center', fontsize=8.6, color='#555')
        if i < n - 1:
            ax.add_patch(FancyArrowPatch((2.8, y), (2.8, y - gap),
                         arrowstyle='-|>', mutation_scale=16, color='#888', lw=1.6))
    ax.set_xlim(0, 5.6)
    ax.set_ylim(y0 - (n - 1) * (h + gap) - 0.2, y0 + h + 0.2)
    ax.axis('off')
    save(fig, 'flowchart.png')


# ========== 图：情形一 RGV 调度轨迹 ==========
def fig_traj():
    _, log = R.simulate_single(R.GROUPS[1], record=True)
    ts, poss = [], []
    for _, k, start, _ in log:
        if start > 2600:
            break
        ts.append(start)
        poss.append(R.col(k) + 1)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(ts, poss, '-o', color=BLUE, ms=5, lw=1.6, mfc='white', mec=BLUE, mew=1.3)
    ax.set_xlabel('时间 t / s')
    ax.set_ylabel('RGV 所在位置（列）')
    ax.set_yticks([1, 2, 3, 4])
    ax.set_ylim(0.6, 4.4)
    ax.set_title('情形一 就近原则下 RGV 调度轨迹（第一组，前 ~2600 s）')
    _clean(ax)
    save(fig, 'case1_traj.png')


# ========== 图：三组产量对比 ==========
def fig_results():
    single = [R.simulate_single(R.GROUPS[g]) for g in (1, 2, 3)]
    double = [R.simulate_double(R.GROUPS[g], R.BEST_LAYOUT[g],
                                principle=R.BEST_PRINCIPLE[g]) for g in (1, 2, 3)]
    x = range(3)
    w = 0.36
    fig, ax = plt.subplots(figsize=(7, 3.7))
    b1 = ax.bar([i - w / 2 for i in x], single, w, label='单工序', color=BLUE, ec='white')
    b2 = ax.bar([i + w / 2 for i in x], double, w, label='双工序', color=RED, ec='white')
    ax.bar_label(b1, fontsize=9.5, padding=2)
    ax.bar_label(b2, fontsize=9.5, padding=2)
    ax.set_xticks(list(x))
    ax.set_xticklabels(['第一组', '第二组', '第三组'])
    ax.set_ylabel('成料数量 / 件')
    ax.set_ylim(0, 440)
    ax.set_title('三组数据单 / 双工序最优成料数量对比')
    ax.legend(frameon=False)
    ax.grid(axis='x', visible=False)
    _clean(ax)
    save(fig, 'results_bar.png')


# ========== 图：情形三 蒙特卡洛产量分布 ==========
def fig_mc():
    _, _, _, vs = R.monte_carlo('single', R.GROUPS[1], n=3000)
    mean = sum(vs) / len(vs)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.hist(vs, bins=range(min(vs), 385, 3), color=GREEN, ec='white', alpha=0.9)
    ax.axvline(383, color=BLUE, ls='--', lw=1.6, label='无故障基准 383')
    ax.axvline(mean, color=RED, ls='-', lw=1.6, label=f'有故障均值 {mean:.1f}')
    ax.set_xlabel('一个班次成料数量 / 件')
    ax.set_ylabel('频数')
    ax.set_title('情形三 蒙特卡洛产量分布（第一组单工序，3000 次）')
    ax.legend(frameon=False)
    ax.grid(axis='x', visible=False)
    _clean(ax)
    save(fig, 'case3_hist.png')


# ========== 图：灵敏度分析 ==========
def fig_sens():
    base = R.GROUPS[1]

    def run(**kw):
        g = dict(base)
        g.update(kw)
        return R.simulate_single(g)
    o, e = base['ldw']
    rows = [
        ('加工时间 $t_0$', run(t0=532), run(t0=588)),
        ('上下料时间', run(ldw=(round(o * .95), round(e * .95))),
                     run(ldw=(round(o * 1.05), round(e * 1.05)))),
        ('移动时间', run(mv=tuple(round(x * .95) for x in base['mv'])),
                   run(mv=tuple(round(x * 1.05) for x in base['mv']))),
    ]
    labels = [r[0] for r in rows]
    y = range(len(rows))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7, 3.1))
    b1 = ax.barh([i + w / 2 for i in y], [r[1] for r in rows], w,
                 label='参数 $-5\\%$', color=BLUE, ec='white')
    b2 = ax.barh([i - w / 2 for i in y], [r[2] for r in rows], w,
                 label='参数 $+5\\%$', color=RED, ec='white')
    ax.axvline(383, color='#333', ls='--', lw=1.1, label='基准 383')
    ax.bar_label(b1, fontsize=9.5, padding=2)
    ax.bar_label(b2, fontsize=9.5, padding=2)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    ax.set_xlim(300, 420)
    ax.set_xlabel('成料数量 / 件')
    ax.set_title('情形一成料数对关键参数 $\\pm5\\%$ 扰动的灵敏度（第一组）')
    ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.22),
              ncol=3, fontsize=9.5)
    ax.grid(axis='y', visible=False)
    _clean(ax)
    save(fig, 'sensitivity.png')


if __name__ == '__main__':
    print('生成图表到', os.path.abspath(OUT))
    fig_layout()
    fig_flowchart()
    fig_traj()
    fig_results()
    fig_mc()
    fig_sens()
    print('全部完成')

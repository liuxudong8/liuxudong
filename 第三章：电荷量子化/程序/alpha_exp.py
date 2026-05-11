import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# ========== 彻底解决所有乱码问题 ==========
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'cm'  # 强制用CM字体渲染公式

# ====================== 1. 论文几何基础参数 ======================
alpha_exp = 1 / 137.036

# 正二十面体结构参数
edge_num = 30
G = 5 * (1.0 / edge_num) * (1.0 / (4 * math.pi))
sin_theta12 = math.sqrt(3.0 / 10.0)
alpha_std = sin_theta12 * G

# 临界尺度（靠近10^-22 m）
r_critical = 3e-22
k_max = 10

# ====================== 2. 临界区有效α计算公式 ======================
def alpha_effective(r, rc=r_critical, alpha0=alpha_std, k=k_max):
    log_r = math.log10(r)
    log_rc = math.log10(rc)
    distance = abs(log_r - log_rc)
    
    rc_min = rc * 0.2
    rc_max = rc * 10

    if r > rc_max:
        return alpha0
    elif r > rc_min and r < rc_max:
        max_fluct = k * math.exp(-distance / 0.5)
        fluct = np.random.uniform(0, max_fluct)
        return fluct * alpha0
    else:
        ratio = r / rc
        return alpha0 * (ratio ** 2)

# ====================== 3. 批量计算 + 绘图（纯文本版） ======================
def calc_alpha_near_rc():
    r_list = np.logspace(-23, -19, 500)
    alpha_list = [alpha_effective(r) for r in r_list]
    
    # 打印关键数值
    print("=" * 65)
    print(f"理论标准α: {alpha_std:.8f}, 1/α: {1/alpha_std:.6f}")
    print(f"实验值α: {alpha_exp:.8f}, 1/α: {1/alpha_exp:.6f}")
    print(f"临界尺度: {r_critical:.2e} m (10^-22 ~ 10^-21之间，偏左)")
    print("=" * 65)

    # 绘图
    fig, ax = plt.subplots(figsize=(12,7))
    ax.semilogx(r_list, alpha_list, color='#2E86AB', linewidth=1.2, label='有效耦合 α_eff(r)')
    ax.axhline(y=alpha_std, color='#A23B72', linestyle='--', linewidth=1.5, label='理论定值 α_std ≈ 1/137')
    ax.axvline(x=r_critical, color='#F18F01', linestyle='-.', linewidth=1.5, label='临界中心 r_c ≈ 3×10^-22 m')
    
    # 强制X轴用普通文本显示，不使用科学计数法上标
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xticks([1e-23, 1e-22, 1e-21, 1e-20, 1e-19])
    ax.set_xticklabels(['1e-23', '1e-22', '1e-21', '1e-20', '1e-19'])
    
    ax.set_xlabel("空间尺度 r (m)", fontsize=12)
    ax.set_ylabel("有效精细结构常数 α_eff", fontsize=12)
    ax.set_title("正二十面体相位膜模型：临界尺度附近精细结构常数涨落（中心靠近1e-22 m）", fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    calc_alpha_near_rc()
    
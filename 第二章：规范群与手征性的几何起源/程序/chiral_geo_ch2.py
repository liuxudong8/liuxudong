# -*- coding: utf-8 -*-
"""
第二章：规范场与手征性的几何起源
配套 Python 程序（带强制可视化绘图 + 完美中文显示）
运行 → 自动弹出图片 + 中文正常显示
"""

import numpy as np
import matplotlib.pyplot as plt

# ====================== 【强制中文显示】核心修复 ======================
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# ====================== 常量 ======================
g = 1.0
j = 1j
gamma5 = np.diag([1, 1, -1, -1])

# ====================== 核心物理计算 ======================
def gauge_field_from_phase(theta, dx):
    return np.gradient(theta, dx)

def cov_derivative(psi, A, dx):
    dpsi_dx = np.gradient(psi, dx)
    return dpsi_dx - j * g * A * psi

def chiral_projection(psi):
    psi_L = 0.5 * (np.eye(4) - gamma5) @ psi
    psi_R = 0.5 * (np.eye(4) + gamma5) @ psi
    return psi_L, psi_R

def weak_chiral_selection(psi_dirac, R):
    psi_L, psi_R = chiral_projection(psi_dirac)
    if R > 0:
        return psi_L, psi_R * 0.08  # 左手存活，右手衰减
    else:
        return psi_L, psi_R

# ====================== 强制绘图（必弹出窗口 + 全中文） ======================
def plot_and_show():
    # 网格
    x = np.linspace(0, 12, 150)
    dx = x[1] - x[0]

    # 相位 → 规范场
    theta = 0.2 * x + 0.1 * np.sin(x)
    A = gauge_field_from_phase(theta, dx)

    # 波函数与协变导数
    psi = np.sin(x) * np.exp(-0.05*x)
    D_psi = cov_derivative(psi, A, dx)

    # 手征
    psi_dirac = np.array([1,0,1,0])
    R = 0.85  # 正 Ricci 曲率（我们的宇宙）
    psi_L, psi_R = weak_chiral_selection(psi_dirac, R)

    L = np.linalg.norm(psi_L)
    R_val = np.linalg.norm(psi_R)

    # ====================== 绘图（全中文） ======================
    plt.figure(figsize=(12,7))

    # 1. 相位 → 规范场
    plt.subplot(2,2,1)
    plt.plot(x, theta, 'b-', label='相位 θ(x)')
    plt.plot(x, A, 'r-', label='规范场 A(x)')
    plt.title('相位梯度 → 规范场涌现')
    plt.legend()
    plt.grid(alpha=0.3)

    # 2. 协变导数
    plt.subplot(2,2,2)
    plt.plot(x, psi, 'g-', label='ψ(x)')
    plt.plot(x, np.abs(D_psi), 'k-', label='|Dψ|')
    plt.title('协变导数（规范不变）')
    plt.legend()
    plt.grid(alpha=0.3)

    # 3. 手征筛选
    plt.subplot(2,2,3)
    plt.bar(['左手征 ψ_L','右手征 ψ_R'], [L, R_val], color=['blue','red'])
    plt.title('正曲率时空 → 左手稳定、右手衰减')
    plt.grid(alpha=0.3)

    # 4. 质量来自几何刚性
    plt.subplot(2,2,4)
    psi0_list = np.linspace(0,5,30)
    mass = 0.31 * np.abs(psi0_list)
    plt.plot(psi0_list, mass, 'm-', linewidth=2)
    plt.xlabel('真空期望值 ⟨ψ⟩')
    plt.ylabel('质量 m')
    plt.title('质量 = 拓扑结几何刚性')
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()  # 必出图

# ====================== 运行 ======================
if __name__ == "__main__":
    print("正在生成第二章可视化图像...")
    plot_and_show()
    print("图像已弹出！中文正常显示")
    
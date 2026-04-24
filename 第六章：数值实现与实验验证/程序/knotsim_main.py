# =============================================================================
# KnotSim 完整主程序
# 离散关联网络 + 编织动力学 + 拓扑结识别 + 混合角计算 + 可视化
# 可直接放入书稿第6章：数值实现与实验验证
# =============================================================================
import numpy as np
import random
import networkx as nx
from sympy import Poly, symbols
import matplotlib.pyplot as plt

# ====================== 修复中文显示 ======================
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 负号正常显示

# ====================== 1. 离散网络生成器 ======================
def generate_discrete_network(num_nodes, connection_prob=0.3):
    nodes = list(range(num_nodes))
    adjacency_matrix = np.zeros((num_nodes, num_nodes), dtype=complex)
    edges = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < connection_prob:
                psi = np.exp(1j * random.uniform(0, 2 * np.pi))
                adjacency_matrix[i, j] = psi
                adjacency_matrix[j, i] = np.conj(psi)
                edges.append((i, j))
    return nodes, edges, adjacency_matrix

# ====================== 2. 编织强度动力学演化 ======================
def psi_dynamics_step(adjacency_matrix, hbar=1.0, alpha=0.1, beta=0.01, gamma=0.001, dt=0.01):
    N = adjacency_matrix.shape[0]
    D = np.diag(np.sum(np.abs(adjacency_matrix), axis=1))
    L = D - adjacency_matrix
    phase = np.angle(adjacency_matrix)
    C = np.sum(phase, axis=1, keepdims=True) @ np.ones((1, N)) / (2 * np.pi)
    dPsi_dt = (1 / (1j * hbar)) * (
        alpha * (L @ adjacency_matrix)
        - beta * (np.abs(adjacency_matrix)**2) * adjacency_matrix
        + gamma * C
    )
    return adjacency_matrix + dPsi_dt * dt

# ====================== 3. 拓扑结识别与稳定性 ======================
def detect_topological_knots(adjacency_matrix, psi_threshold=0.5):
    N = adjacency_matrix.shape[0]
    G = nx.Graph()
    for i in range(N):
        for j in range(i + 1, N):
            if abs(adjacency_matrix[i, j]) >= psi_threshold:
                G.add_edge(i, j)
    cycles = []
    try:
        for cycle in nx.cycle_basis(G):
            if len(cycle) >= 3:
                cycles.append(cycle)
    except:
        pass
    stable_knots = []
    for cycle in cycles:
        psi_values = []
        for k in range(len(cycle)):
            i = cycle[k]
            j = cycle[(k + 1) % len(cycle)]
            psi_values.append(abs(adjacency_matrix[i, j]))
        min_psi = min(psi_values)
        stable = min_psi > psi_threshold
        stable_knots.append({"cycle": cycle, "min_psi": min_psi, "stable": stable})
    return stable_knots

# ====================== 4. 拓扑不变量计算 ======================
def jones_polynomial_31():
    q = symbols('q')
    return Poly(q**4 - q**3 - q, q)

def compute_chern_number(adjacency_matrix):
    N = adjacency_matrix.shape[0]
    phase = np.angle(adjacency_matrix)
    grad_phase = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j:
                grad_phase[i, j] = phase[i, j] - phase[i, 0]
    return np.sum(grad_phase) / (2 * np.pi)

def compute_mixing_angles():
    phi = (1 + np.sqrt(5)) / 2
    V31 = 1.542
    theta12 = np.arcsin(np.sqrt(1 / V31**2)) * 180 / np.pi
    theta23 = np.arctan(phi) * 180 / np.pi
    theta13 = np.arcsin(1 / (2 * phi**2)) * 180 / np.pi
    return {"θ₁₂": theta12, "θ₂₃": theta23, "θ₁₃": theta13}

# ====================== 5. 可视化模块 ======================
def visualize_psi_network(adjacency_matrix, title="KnotSim 完整可视化"):
    N = adjacency_matrix.shape[0]
    G = nx.Graph()
    edge_widths, edge_colors = [], []
    for i in range(N):
        for j in range(i + 1, N):
            psi = adjacency_matrix[i, j]
            if abs(psi) > 1e-3:
                G.add_edge(i, j)
                edge_widths.append(abs(psi) * 3)
                edge_colors.append(np.angle(psi))
    pos = nx.spring_layout(G, seed=42)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    nx.draw_networkx_nodes(G, pos, ax=ax1, node_color='lightblue', node_size=300)
    nx.draw_networkx_edges(G, pos, ax=ax1, width=edge_widths, edge_color='black')
    nx.draw_networkx_labels(G, pos, ax=ax1)
    ax1.set_title("振幅 |Ψ|")
    ax1.axis('off')

    edges = nx.draw_networkx_edges(G, pos, ax=ax2, edge_color=edge_colors, edge_cmap=plt.cm.hsv, width=2)
    nx.draw_networkx_labels(G, pos, ax=ax2)
    plt.colorbar(edges, ax=ax2, label="相位(rad)")
    ax2.set_title("相位 ∠Ψ")
    ax2.axis('off')

    node_phases = np.array([np.angle(np.sum(adjacency_matrix[i, :])) for i in range(N)])
    nx.draw_networkx_nodes(G, pos, ax=ax3, node_color=node_phases, cmap=plt.cm.hsv, node_size=300)
    nx.draw_networkx_edges(G, pos, ax=ax3, width=1, edge_color='gray')
    nx.draw_networkx_labels(G, pos, ax=ax3)
    plt.colorbar(ax3.collections[0], ax=ax3, label="拓扑相位")
    ax3.set_title("拓扑相位")
    ax3.axis('off')

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()

# ====================== 主函数：一键全流程 ======================
if __name__ == "__main__":
    print("=" * 60)
    print("        KnotSim 离散关联网络模拟系统（完整版）")
    print("=" * 60)

    # 1. 生成网络
    nodes, edges, adj = generate_discrete_network(12, 0.4)
    print(f"✅ 生成网络：{len(nodes)} 节点，{len(edges)} 条关联")

    # 2. 动力学演化
    adj_evolved = psi_dynamics_step(adj)
    print("✅ 完成编织强度动力学演化 1 步")

    # 3. 检测拓扑结
    knots = detect_topological_knots(adj_evolved, 0.3)
    print(f"✅ 检测到 {len(knots)} 个拓扑环")
    for k in knots:
        print(f"   环：{k['cycle']} | 最小Ψ：{k['min_psi']:.2f} | 稳定：{k['stable']}")

    # 4. 拓扑计算
    chern = compute_chern_number(adj_evolved)
    angles = compute_mixing_angles()
    print(f"✅ 陈数近似：{chern:.2f}")
    print("✅ 轻子混合角（理论值）：")
    for name, val in angles.items():
        print(f"   {name} = {val:.2f}°")

    # 5. 可视化
    print("✅ 打开可视化界面...")
    visualize_psi_network(adj_evolved)

    print("\n🎉 KnotSim 全流程运行完成！")
    
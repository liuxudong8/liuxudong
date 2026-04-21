import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ==============================
# 【关键修复】中文显示配置
# ==============================
# 优先使用系统常见中文字体，确保跨平台兼容
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题
rcParams['font.family'] = 'sans-serif'

# ==============================
# KnotSim 第1章 1.1 离散关联网络公理体系
# 1.1.1 节点与关联的代数定义
# 1.1.2 编织强度 Ψ 的动力学方程
# ==============================

# 基础参数（自然单位制）
N_NODE = 8          # 节点数（最小创世单元）
I = 1j              # 虚数单位
hbar = 1.0          # 约化普朗克常数
alpha = 0.1         # 扩散系数（关联传播强度）
beta = 0.05         # 非线性系数（自局域化强度）
gamma = 0.02        # 荷耦合系数（拓扑荷耦合）
dt = 0.01           # 时间步长
TOTAL_STEP = 100    # 总演化步数

# ========== 1.1.1 节点与关联 代数定义 ==========
class Vertex:
    """节点 (Vertex) 基元：宇宙的离散基元"""
    def __init__(self, vid):
        self.vid = vid          # 节点唯一标识
        self.charge = 0         # 拓扑守恒荷（后续章节扩展）

class Edge:
    """关联 (Edge) 基元：节点间的定向、加权二元关系"""
    def __init__(self, vi, vj, psi_init=1+0*I):
        self.vi = vi            # 起点节点ID
        self.vj = vj            # 终点节点ID
        self.psi = psi_init     # 编织强度 Ψ（复振幅）
        self.tau = 1.0          # 关联时延（涌现几何的尺度因子）

class DiscreteNetwork:
    """离散关联网络：宇宙本体，无先验时空/场/对称"""
    def __init__(self, n_node):
        self.n_node = n_node
        self.V = [Vertex(i) for i in range(n_node)]  # 节点集合
        self.E = []                                  # 关联集合
        self.adj = np.zeros((n_node, n_node), dtype=complex)  # 复邻接矩阵A

    def add_edge(self, i, j, psi=1+0*I):
        """添加定向关联，更新邻接矩阵"""
        e = Edge(i, j, psi)
        self.E.append(e)
        self.adj[i, j] = psi

    def degree_matrix(self):
        """度矩阵D：节点关联强度和，D_ii = Σ_j |A_ij|"""
        return np.diag(np.sum(np.abs(self.adj), axis=1))

    def laplacian_matrix(self):
        """拉普拉斯算子L = D - A：网络曲率/刚性的核心算子"""
        D = self.degree_matrix()
        return D - self.adj

# ========== 1.1.2 编织强度 Ψ 动力学方程 ==========
def psi_dynamics(network, L, C):
    """
    KnotSim 核心动力学方程：
    iħ ∂Ψ/∂t = α·(LΨ) - β·|Ψ|²Ψ + γ·C
    输入：网络实例、拉普拉斯矩阵L、守恒荷矩阵C
    输出：Ψ的时间导数dΨ/dt
    """
    psi = network.adj
    lap_term = alpha * L @ psi          # 拉普拉斯扩散项：关联传播，空间涌现
    nonlin_term = beta * np.abs(psi)**2 * psi  # 非线性自局域项：结的稳定化
    charge_term = gamma * C             # 拓扑荷耦合项：规范荷/电荷的底层来源
    dpsi_dt = (lap_term - nonlin_term + charge_term) / (I * hbar)
    return dpsi_dt

# ========== 创世初始化：最小闭环网络（结的雏形） ==========
net = DiscreteNetwork(N_NODE)
# 构建链式关联 + 闭环，形成8节点环（最小拓扑结）
for i in range(N_NODE - 1):
    net.add_edge(i, i+1, psi=0.5+0.3*I)
net.add_edge(N_NODE-1, 0, psi=0.5+0.3*I)  # 闭环，形成拓扑非平庸结构

# ========== 守恒荷矩阵C（均匀拓扑荷背景） ==========
C = np.ones((N_NODE, N_NODE), dtype=complex) * 0.1

# ========== 预计算拉普拉斯矩阵（静态网络假设） ==========
L = net.laplacian_matrix()

# ========== 动力学演化与数据记录 ==========
psi_history = []
for step in range(TOTAL_STEP):
    # 记录边(0,1)的编织强度Ψ，用于可视化
    psi_history.append(np.copy(net.adj[0, 1]))
    # 计算Ψ的时间导数
    dpsi_dt = psi_dynamics(net, L, C)
    # 欧拉法时间演化
    net.adj += dpsi_dt * dt

# ========== 可视化：编织强度Ψ的动力学演化 ==========
plt.figure(figsize=(12, 5))
# 绘制振幅|Ψ|
plt.plot(np.abs(psi_history), color='#1f77b4', linewidth=2, label=r'$|\Psi|$（振幅）')
# 绘制相位arg(Ψ)
plt.plot(np.angle(psi_history), color='#ff7f0e', linewidth=2, label=r'$\arg(\Psi)$（相位）')

# 【中文正常显示】标题、坐标轴、图例
plt.title('1.1.2 编织强度 Ψ 动力学演化', fontsize=18, pad=20)
plt.xlabel('演化步数', fontsize=14, labelpad=12)
plt.ylabel('振幅 / 相位', fontsize=14, labelpad=12)
plt.legend(fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tick_params(axis='both', labelsize=14)
plt.tight_layout()  # 自动调整布局，避免标签被截断
plt.show()

# ========== 控制台输出：公理体系结构验证 ==========
print("===== KnotSim 第1章 1.1 公理体系输出 =====")
print(f"节点数：{net.n_node}")
print(f"关联数：{len(net.E)}")
print("\n复邻接矩阵 A（实部，保留3位小数）：")
print(np.round(np.real(net.adj), 3))
print("\n拉普拉斯矩阵 L（实部，保留3位小数）：")
print(np.round(np.real(L), 3))
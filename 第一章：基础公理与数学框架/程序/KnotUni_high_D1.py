import numpy as np
import matplotlib
# 仅保留正确的中文配置
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D
import time

# ======================
# 核心配置参数
# ======================
POINT_COUNT = 80          # 粒子数量
BASE_EDGE_DIST = 2.0      # 高维结连接阈值
FADE_DURATION = 8.0       # 高维结完全褪去时间（秒）
ROTATE_SPEED = 0.25       # 3D视图旋转速度
INIT_EXPAND = 1.0         # 初始膨胀倍数
EXPAND_RATE = 0.0012      # 3D空间膨胀速率（匀速）

# ======================
# 高维点数据结构
# ======================
class Point:
    def __init__(self, v):
        self.v = np.array(v, dtype=np.float64)
        self.original_v = np.array(v, dtype=np.float64)  # 记录原始位置，用于膨胀

def generate_universe():
    """一次性生成5维高维结宇宙（仅创世一次）"""
    high_dim = 5
    # 生成高维随机点
    pts = [Point(np.random.randn(high_dim) * 1.2) for _ in range(POINT_COUNT)]
    edges = []
    
    # 计算高维空间下的连接阈值
    dist_threshold = BASE_EDGE_DIST * (high_dim / 3)
    
    # 构建高维结的边连接
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = np.linalg.norm(pts[i].v - pts[j].v)
            if dist < dist_threshold:
                edges.append((i, j))
    return pts, edges, high_dim

# ======================
# 主程序：宇宙演化
# ======================
class KnotUniverse:
    def __init__(self, root):
        self.root = root
        self.root.title("高维结创世 → 3D宇宙膨胀（最终稳定版）")
        self.root.geometry("1200x800")
        self.root.configure(bg='#000010')

        # 一次性生成宇宙（大爆炸）
        self.pts, self.edges, self.high_dim = generate_universe()
        
        # 膨胀状态
        self.expand_scale = INIT_EXPAND
        # 时间驱动的褪去逻辑（避免浮点误差）
        self.start_time = time.time()
        self.fade_duration = FADE_DURATION
        # 旋转角度
        self.rotate_angle = 0.0

        # 初始化3D绘图
        self.fig = plt.figure(figsize=(11, 8), facecolor='#000010')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#000010')
        
        # 绑定画布到Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # 信息面板
        self.info_label = ttk.Label(
            root, 
            text="💥 大爆炸已触发，宇宙开始演化...", 
            foreground="#00FF9E", 
            background="#000010", 
            font=("Consolas", 12)
        )
        self.info_label.pack(pady=5, padx=10, fill=tk.X)

        # 启动动画循环
        self.update_loop()

    def update_loop(self):
        """主循环：永久运行，驱动膨胀、褪去、旋转"""
        if not self.root.winfo_exists():
            return
            
        # 1. 计算流逝时间（时间驱动，避免帧误差）
        elapsed_time = time.time() - self.start_time
        
        # 2. 3D空间持续膨胀
        self.expand_scale += EXPAND_RATE
        
        # 3. 高维结透明度计算（严格钳制在0-1范围，彻底解决负数问题）
        fade_progress = min(1.0, elapsed_time / self.fade_duration)
        current_alpha = max(0.0, 1.0 - fade_progress)  # 双重保障：max(0.0, ...)
        
        # 4. 更新旋转角度
        self.rotate_angle = (self.rotate_angle + ROTATE_SPEED) % 360
        
        # 5. 重绘画面：传入fade_progress，解决NameError
        self.draw(current_alpha, elapsed_time, fade_progress)
        
        # 6. 约60fps循环
        self.root.after(16, self.update_loop)

    def draw(self, current_alpha, elapsed_time, fade_progress):
        """绘制3D宇宙：高维结褪去 + 空间膨胀"""
        ax = self.ax
        ax.clear()
        ax.set_facecolor('#000010')
        
        # 计算3D投影坐标，应用膨胀缩放
        p3 = np.array([p.original_v[:3] * self.expand_scale for p in self.pts])

        # 绘制高维结连线（随时间透明化）
        for i, j in self.edges:
            ax.plot(
                p3[[i, j], 0], p3[[i, j], 1], p3[[i, j], 2],
                color='#FF6600', alpha=current_alpha * 0.6, linewidth=0.8
            )

        # 绘制3D粒子（随宇宙膨胀适度放大）
        point_size = np.clip(15 + self.expand_scale, 5, 100)
        ax.scatter(
            p3[:, 0], p3[:, 1], p3[:, 2],
            c='#00E5FF', s=point_size, alpha=0.9
        )

        # 3D立方体边界（随膨胀同步放大，模拟宇宙空间扩展）
        space_bound = self.expand_scale * 2.5
        ax.set_xlim(-space_bound, space_bound)
        ax.set_ylim(-space_bound, space_bound)
        ax.set_zlim(-space_bound, space_bound)

        # 设置视角
        ax.view_init(20, self.rotate_angle)
        ax.set_title(
            f"高维结宇宙演化 | 维度：{self.high_dim}D → 3D | 膨胀倍数: {self.expand_scale:.2f}x",
            color='white', fontsize=14
        )

        # 更新信息面板：fade_progress已作为参数传入，无作用域错误
        fade_percent = min(100, fade_progress * 100)
        self.info_label.config(
            text=f"💥 创世状态：大爆炸已完成 | 高维结褪去进度：{fade_percent:.1f}% | 3D宇宙尺度：{self.expand_scale:.2f}x"
        )
        
        # 刷新画布
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = KnotUniverse(root)
    root.mainloop()
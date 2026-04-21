# import sys
# sys.path.append("..")  # 把上级目录 KNOTSIM_4 加入搜索路径

import numpy as np
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D
import time
import threading
from matplotlib.colors import LinearSegmentedColormap
import pygame  # 新增：音频播放库
import math  # 新增：数学计算
from scipy.io import wavfile

# 保留原有导入（即使未使用也保持兼容）
from new_particles.particle import NewParticle
from new_materials.material import Material
from particle_info import CAS_NEW_PARTICLE_INFO
import sys
import os

# ======================
# 核心参数
# ======================
DEFAULT_POINT_COUNT = 50
MIN_POINT = 10
MAX_POINT = 400
EDGE_DIST = 1.8
PLOT1_DIM = 4
PLOT2_DIM = 5
PLOT3_DIM = 3
FADE_TIME = 5
ROTATE_SPEED = 0.3
# 维度范围：大于3维，随机范围4-10维
MIN_HIGH_DIM = 4
MAX_HIGH_DIM = 10

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller 打包后会创建临时文件夹，路径存在 _MEIPASS 里
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境下用当前目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 新增：阈值相关参数
THRESHOLD_TRIGGER_RATIO = 0.03  # 触发大爆炸的阈值比例（总点对的30%）
THRESHOLD_ANIM_DURATION = 3.0  # 阈值判定动画时长（秒）
BANG_SOUND_PATH = resource_path("big_bang.wav")  # 大爆炸音效文件路径（需自行准备）

# 配色
CMAP_HIGH = LinearSegmentedColormap.from_list('deepspace', ['#001f3f', '#0074D9', '#7FDBFF', '#FFFFFF'])
CMAP_4D = LinearSegmentedColormap.from_list('redshift', ['#1A0000', '#8B0000', '#FF4500', '#FFA07A'])
CMAP_5D = LinearSegmentedColormap.from_list('orangenebula', ['#2B1B00', '#FF8C00', '#FFD700', '#FFFFE0'])
CMAP_3D = LinearSegmentedColormap.from_list('purplevoid', ['#1E002E', '#800080', '#9370DB', '#E6E6FA'])

# ======================
# 初始化音频
# ======================
pygame.mixer.init()
# 加载音效（若文件不存在则跳过，避免报错）
def make_big_bang_sound(filename="big_bang.wav"):
    sample_rate = 44100
    duration = 1.0  # 1秒
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 生成爆炸波形（低频+衰减噪声）
    boom = np.sin(2 * np.pi * 100 * t) * np.exp(-t * 3)  # 低频嗡鸣
    noise = np.random.normal(0, 0.5, t.shape) * np.exp(-t * 5)  # 爆炸噪声
    signal = (boom + noise) * 0.3
    
    # 转为16位PCM
    signal = np.int16(signal * 32767)
    wavfile.write(filename, sample_rate, signal)
try:
    bang_sound = pygame.mixer.Sound(BANG_SOUND_PATH)
    #make_big_bang_sound()
except:
    bang_sound = None
    print(f"提示：未找到音效文件 {BANG_SOUND_PATH}，将跳过音效播放")

# ======================
# 高维点生成
# ======================
class Point:
    def __init__(self, v):
        self.v = np.array(v)



def generate(point_count, high_dim):
    """生成指定维度的高维点和边（新增阈值判定过程）"""
    pts = [Point(np.random.randn(high_dim)*0.7) for _ in range(point_count)]
    edges = []
    # 统计大于阈值的点对数量（新增：分步生成，用于减速展示）
    threshold_count = 0
    total_pairs = point_count * (point_count - 1) // 2
    # 新增：记录生成过程（用于动画）
    generate_steps = []
    
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            dist = np.linalg.norm(pts[i].v - pts[j].v)
            if dist < EDGE_DIST:
                edges.append((i,j))
                threshold_count += 1
                # 记录每一步的生成状态
                generate_steps.append({
                    'edges': edges.copy(),
                    'count': threshold_count,
                    'progress': threshold_count / total_pairs if total_pairs > 0 else 0
                })
    return pts, edges, threshold_count, generate_steps, total_pairs

# ======================
# 主程序（新增阈值动画+音效）
# ======================
class KnotUniGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("高维结宇宙")
        self.root.geometry("1400x800")
        self.root.configure(bg='#000010')

        # 随机初始化高维维度（>3）
        self.high_dim = np.random.randint(MIN_HIGH_DIM, MAX_HIGH_DIM + 1)
        # 状态
        self.point_count = DEFAULT_POINT_COUNT
        # 新增：阈值相关状态
        self.threshold_triggered = False  # 是否触发大爆炸
        self.threshold_anim_running = False  # 阈值动画是否运行
        self.threshold_anim_progress = 0.0  # 阈值动画进度
        self.generate_steps = []  # 生成过程记录
        self.total_pairs = 0  # 总点对数量
        
        # 初始化生成（新增生成过程记录）
        self.pts, self.edges, self.threshold_count, self.generate_steps, self.total_pairs = generate(self.point_count, self.high_dim)
        
        self.running = True
        self.show1 = True
        self.show2 = True
        self.show3 = True
        self.rotate_angle = 0

        # 粒子消散效果
        self.dim4_alpha = 1.0
        self.dim5_alpha = 1.0
        # 结解开进度
        self.unravel_progress = 0.0
        self.unravel_stage = "初始状态"

        # 线程
        self.anim_thread = None
        # 新增：阈值动画线程
        self.threshold_thread = None

        # 布局（保持原有）
        main_pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=1)
        self.left = ttk.Frame(main_pane, width=500)
        self.right = ttk.Frame(main_pane, width=900)  # 加宽右侧区域
        main_pane.add(self.left)
        main_pane.add(self.right)

        # 左侧布局：绘图区 + 信息框（保持不变）
        left_top = ttk.Frame(self.left)
        left_top.pack(fill=tk.BOTH, expand=1)
        left_bottom = ttk.Frame(self.left)
        left_bottom.pack(fill=tk.X, padx=5, pady=5)

        # 左图
        self.fig_l = plt.figure(figsize=(5,7), facecolor='#000010')
        self.ax_l = self.fig_l.add_subplot(111, projection='3d')
        self.ax_l.set_facecolor('#000010')
        self.canv_l = FigureCanvasTkAgg(self.fig_l, left_top)
        self.canv_l.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # 左侧动态信息框（新增阈值进度）
        self.info_label = ttk.Label(
            left_bottom,
            text="",
            wraplength=480,
            justify=tk.LEFT,
            background='#000010',
            foreground='lightgreen'
        )
        self.info_label.pack(fill=tk.X)
        # 初始化信息框内容
        self.update_info_text()

        # 右侧布局：绘图区 + 结解开信息框
        right_top = ttk.Frame(self.right)
        right_top.pack(fill=tk.BOTH, expand=1)
        right_bottom = ttk.Frame(self.right)
        right_bottom.pack(fill=tk.X, padx=5, pady=5)

        # 右图
        self.fig_r = plt.figure(figsize=(8,8), facecolor='#000010')
        self.ax1 = self.fig_r.add_subplot(2,2,1, facecolor='#000010')
        self.ax2 = self.fig_r.add_subplot(2,2,2, facecolor='#000010')
        self.ax3 = self.fig_r.add_subplot(2,2,3, projection='3d', facecolor='#000010')
        self.fig_r.tight_layout()
        self.canv_r = FigureCanvasTkAgg(self.fig_r, right_top)
        self.canv_r.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # 右侧新增：高维结解开信息框
        self.knot_info_label = ttk.Label(
            right_bottom,
            text="",
            wraplength=850,
            justify=tk.LEFT,
            background='#000010',
            foreground='#FFD700',  # 金色文字
            font=('SimHei', 10, 'bold')
        )
        self.knot_info_label.pack(fill=tk.X)
        # 初始化结解开信息
        self.update_knot_info_text()

        # 按钮（保持原有）
        ctr = ttk.Frame(root)
        ctr.pack(side=tk.BOTTOM, pady=10)
        ttk.Button(ctr, text="🔄 重塑宇宙", command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctr, text="❌ 退出", command=self.on_exit).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctr, text="📖 新粒子解释", command=self.show_cas_info).pack(side=tk.LEFT, padx=5)
        self.msg = ttk.Label(ctr, text="初始：阈值判定中...")
        self.msg.pack(side=tk.LEFT, padx=10)

        # 滑块（保持原有）
        top = ttk.Frame(root)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        ttk.Label(top, text="粒子数：").pack(side=tk.LEFT)
        self.slider = ttk.Scale(top, from_=MIN_POINT, to=MAX_POINT, command=self.on_slide)
        self.slider.set(self.point_count)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 启动（新增阈值动画启动）
        self.update_loop()
        self.start_threshold_animation()  # 启动阈值判定动画
        self.restart_anim_thread()
        self.draw_all()

    def update_info_text(self):
        """更新左侧信息框文本（新增阈值进度）"""
        total_pairs = self.total_pairs
        threshold_ratio = self.threshold_count / total_pairs if total_pairs > 0 else 0
        trigger_ratio = THRESHOLD_TRIGGER_RATIO
        
        # 新增阈值状态文本
        threshold_status = "未触发"
        if self.threshold_triggered:
            threshold_status = "✅ 已触发大爆炸"
        elif self.threshold_anim_running:
            threshold_status = f"判定中（进度：{self.threshold_anim_progress:.1%}）"
        elif threshold_ratio >= trigger_ratio:
            threshold_status = "即将触发大爆炸"

        info_text = (
            f"当前高维空间维度：{self.high_dim}维\n"
            f"生成粒子（点）数量：{self.point_count} 个\n"
            f"边生成阈值：{EDGE_DIST}（欧氏距离）\n"
            f"总点对数量：{total_pairs} 个\n"
            f"大于阈值的点对数量：{self.threshold_count} 个（{threshold_ratio:.1%}）\n"
            f"触发大爆炸阈值：{trigger_ratio:.1%} 点对比例\n"
            f"阈值状态：{threshold_status}\n"
            f"当前生成边（线）数量：{len(self.edges)} 条\n"
            f"形成高维网/结结构：已构建 {self.high_dim} 维拓扑网络"
        )
        self.info_label.config(text=info_text)

    def update_knot_info_text(self):
        """更新右侧高维结解开信息框（新增阈值触发状态）"""
        # 计算总体解开进度
        total_fade_steps = FADE_TIME * 2 * 1000 / 20  # 总帧数
        current_step = (1.0 - self.dim4_alpha) * FADE_TIME * 1000 / 20 + (1.0 - self.dim5_alpha) * FADE_TIME * 1000 / 20
        self.unravel_progress = min(100, (current_step / total_fade_steps) * 100)

        # 更新解开阶段（新增阈值触发判断）
        if not self.threshold_triggered:
            self.unravel_stage = "等待阈值触发：高维结未激活"
        elif self.unravel_progress < 10:
            self.unravel_stage = "初始状态：高维结完整存在"
        elif self.unravel_progress < 50:
            self.unravel_stage = "第一阶段：4维结开始松解，维度结构逐渐瓦解"
        elif self.unravel_progress < 90:
            self.unravel_stage = "第二阶段：5维结快速解开，高维信息向3维坍缩"
        else:
            self.unravel_stage = "最终阶段：仅保留3维实体，高维结完全解开"

        # 计算剩余高维连接数
        remaining_high_dim_edges = int(len(self.edges) * ((self.dim4_alpha + self.dim5_alpha) / 2))
        
        knot_text = (
            f"📌 高维结解开状态（{self.high_dim}维 → 3维）\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"阈值触发状态：{'✅ 已触发' if self.threshold_triggered else '❌ 未触发'}\n"
            f"解开进度：{self.unravel_progress:.1f}%\n"
            f"当前阶段：{self.unravel_stage}\n"
            f"4维结透明度：{self.dim4_alpha:.2f}（剩余{self.dim4_alpha*100:.0f}%）\n"
            f"5维结透明度：{self.dim5_alpha:.2f}（剩余{self.dim5_alpha*100:.0f}%）\n"
            f"剩余高维连接数：{remaining_high_dim_edges}/{len(self.edges)} 条\n"
            f"解开速度：{ROTATE_SPEED:.1f}°/帧（与3维旋转同步）"
        )
        self.knot_info_label.config(text=knot_text)

    # ======================
    # 新增：阈值判定动画
    # ======================
    def start_threshold_animation(self):
        """启动阈值判定减速动画"""
        if self.threshold_thread and self.threshold_thread.is_alive():
            return
        self.threshold_anim_running = True
        self.threshold_anim_progress = 0.0
        self.threshold_thread = threading.Thread(target=self.threshold_animation, daemon=True)
        self.threshold_thread.start()

    def threshold_animation(self):
        """阈值判定动画逻辑（减速展示生成过程）"""
        start_time = time.time()
        total_duration = THRESHOLD_ANIM_DURATION
        
        # 逐步展示边的生成过程
        while time.time() - start_time < total_duration and self.running:
            elapsed = time.time() - start_time
            self.threshold_anim_progress = elapsed / total_duration
            
            # 更新当前显示的边（按进度展示）
            if self.generate_steps:
                step_idx = min(int(self.threshold_anim_progress * len(self.generate_steps)), len(self.generate_steps)-1)
                current_step = self.generate_steps[step_idx]
                self.edges = current_step['edges']
                self.threshold_count = current_step['count']
            
            # 检查是否触发阈值
            current_ratio = self.threshold_count / self.total_pairs if self.total_pairs > 0 else 0
            if current_ratio >= THRESHOLD_TRIGGER_RATIO and not self.threshold_triggered:
                self.trigger_big_bang()  # 触发大爆炸
            
            time.sleep(0.02)  # 减速展示
            
        self.threshold_anim_running = False
        # 最终检查阈值触发
        final_ratio = self.threshold_count / self.total_pairs if self.total_pairs > 0 else 0
        if final_ratio >= THRESHOLD_TRIGGER_RATIO and not self.threshold_triggered:
            self.trigger_big_bang()

    def trigger_big_bang(self):
        """触发大爆炸（播放音效+标记状态）"""
        self.threshold_triggered = True
        self.msg.config(text=f"{self.high_dim}维宇宙：✅ 大爆炸已触发！")
        
        # 播放大爆炸音效
        if bang_sound:
            bang_sound.play()
            
        
        # 更新信息
        self.update_info_text()
        self.update_knot_info_text()

    # ======================
    # 主线程安全循环（保持原有）
    # ======================
    def update_loop(self):
        if self.running:
            self.rotate_angle += ROTATE_SPEED
            self.update_fade()
            self.update_knot_info_text()  # 每次更新都刷新结解开信息
            self.draw_all()
            self.root.after(20, self.update_loop)

    def update_fade(self):
        if not self.show1 and self.dim4_alpha > 0:
            self.dim4_alpha -= 0.012  # 4维消散速度
        if not self.show2 and self.dim5_alpha > 0:
            self.dim5_alpha -= 0.012  # 5维消散速度

    # ======================
    # 基础功能（新增阈值重置）
    # ======================
    def on_slide(self, v):
        self.point_count = int(float(v))
        # 重新生成点和边（包含生成过程）
        self.pts, self.edges, self.threshold_count, self.generate_steps, self.total_pairs = generate(self.point_count, self.high_dim)
        # 重置阈值状态
        self.threshold_triggered = False
        self.threshold_anim_running = False
        self.start_threshold_animation()  # 重新启动阈值动画
        self.update_info_text()  # 滑块调整时更新信息

    def restart_anim_thread(self):
        if self.anim_thread and self.anim_thread.is_alive():
            self.running = False
            self.anim_thread.join(timeout=0.5)
        self.running = True
        self.dim4_alpha = 1.0
        self.dim5_alpha = 1.0
        self.unravel_progress = 0.0
        self.unravel_stage = "初始状态"
        self.anim_thread = threading.Thread(target=self.anim, daemon=True)
        self.anim_thread.start()

    def reset(self):
        """重塑宇宙：随机更换维度，重新生成点边（重置阈值状态）"""
        # 重新随机生成高维维度（>3）
        self.high_dim = np.random.randint(MIN_HIGH_DIM, MAX_HIGH_DIM + 1)
        # 重新生成点、边和阈值统计
        self.pts, self.edges, self.threshold_count, self.generate_steps, self.total_pairs = generate(self.point_count, self.high_dim)
        # 重置阈值状态
        self.threshold_triggered = False
        self.threshold_anim_running = False
        # 重置其他状态
        self.show1 = True
        self.show2 = True
        self.show3 = True
        self.rotate_angle = 0
        self.dim4_alpha = 1.0
        self.dim5_alpha = 1.0
        self.unravel_progress = 0.0
        self.unravel_stage = "初始状态"
        # 重启阈值动画
        self.start_threshold_animation()
        self.msg.config(text=f"已重置：{self.high_dim}维宇宙，阈值判定中...")
        self.update_info_text()  # 重置后更新信息
        self.update_knot_info_text()  # 重置结解开信息
        self.restart_anim_thread()

    def on_exit(self):
        self.running = False
        pygame.mixer.quit()  # 关闭音频
        self.root.destroy()
    
    def show_cas_info(self):
        """保留完整的国科大新粒子说明功能"""
        from tkinter import messagebox
        messagebox.showinfo("国科大新粒子说明", CAS_NEW_PARTICLE_INFO)

    # ======================
    # 维度消失动画（保持原有）
    # ======================
    def anim(self):
        try:
            time.sleep(FADE_TIME)
            if self.running and self.threshold_triggered:  # 仅阈值触发后才开始消散
                self.show1 = False
                self.msg.config(text=f"{self.high_dim}维宇宙：4维结已消散")

            time.sleep(FADE_TIME)
            if self.running and self.threshold_triggered:  # 仅阈值触发后才开始消散
                self.show2 = False
                self.msg.config(text=f"{self.high_dim}维宇宙：仅保留3维实体")
        except:
            pass

    # ======================
    # 绘图（新增阈值触发后才显示右侧投影）
    # ======================
    def draw_all(self):
        self.draw_left()
        self.draw_right()
        self.canv_l.draw()
        self.canv_r.draw()

    def draw_left(self):
        ax = self.ax_l
        ax.clear()
        ax.set_facecolor('#000010')
        p3 = self.project(self.pts, 3)

        # 绘制边（阈值触发前为黄色，触发后为绿色）
        edge_color = 'gold' if not self.threshold_triggered else 'lime'
        for i,j in self.edges:
            ax.plot(p3[[i,j],0], p3[[i,j],1], p3[[i,j],2], c=edge_color, alpha=0.6)
        
        # 绘制点（阈值触发后变色）
        point_color = 'orange' if not self.threshold_triggered else 'deepskyblue'
        ax.scatter(p3[:,0],p3[:,1],p3[:,2], s=24, c=point_color)

        # 新增：阈值触发后显示爆炸效果
        if self.threshold_triggered:
            ax.text2D(0.5, 0.95, "💥 大爆炸！", transform=ax.transAxes, 
                     fontsize=12, color='red', ha='center', weight='bold')

        ax.view_init(30, self.rotate_angle)
        ax.set_title(f"{self.high_dim}D 高维空间", color='white')

    def draw_right(self):
        a1,a2,a3 = self.ax1, self.ax2, self.ax3
        a1.clear(); a2.clear(); a3.clear()

        # 仅阈值触发后才显示右侧投影
        if not self.threshold_triggered:
            # 2D 轴用 text，3D 轴用 text2D
            a1.text(0.5, 0.5, "等待阈值触发...", ha='center', va='center', transform=a1.transAxes, color='gray')
            a2.text(0.5, 0.5, "等待阈值触发...", ha='center', va='center', transform=a2.transAxes, color='gray')
            a3.text2D(0.5, 0.5, "等待阈值触发...", ha='center', va='center', transform=a3.transAxes, color='gray')
            a1.set_title("4维投影（未激活）", color='gray')
            a2.set_title("5维投影（未激活）", color='gray')
            a3.set_title("3维实体（未激活）", color='gray')
            return

        # 触发后正常绘制投影
        p4 = self.project(self.pts, PLOT1_DIM)
        p5 = self.project(self.pts, PLOT2_DIM)
        p3 = self.project(self.pts, PLOT3_DIM)

        # 4维：消失后残留粒子 → 慢慢解散
        if self.show1 or self.dim4_alpha > 0.02:
            a1.scatter(p4[:,0], p4[:,1], c='crimson', s=25, alpha=self.dim4_alpha)
        a1.set_title("4维投影", color='white')

        # 5维：消失后残留粒子 → 慢慢解散
        if self.show2 or self.dim5_alpha > 0.02:
            a2.scatter(p5[:,0], p5[:,1], c='orange', s=25, alpha=self.dim5_alpha)
        a2.set_title("5维投影", color='white')

        # 3维：永久保留 + 正常旋转
        a3.scatter(p3[:,0],p3[:,1],p3[:,2], c='mediumpurple', s=30)
        a3.set_title("3维实体", color='white')
        a3.view_init(45, self.rotate_angle + 90)

    def project(self, points, dim):
        """投影函数（封装为类方法）"""
        return np.array([p.v[:dim] for p in points])

if __name__ == "__main__":
    root = tk.Tk()
    KnotUniGUI(root)
    root.mainloop()
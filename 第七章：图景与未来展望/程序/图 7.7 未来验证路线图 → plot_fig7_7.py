import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']

fig, ax = plt.subplots(figsize=(12,5))
ax.set_xlim(0,10)
ax.set_ylim(0,6)
ax.axis('off')

steps = [
    (1,5,"公理 + ψ场动力学"),
    (3,5,"KnotSim 数值平台"),
    (5,5,"拓扑谱数据库"),
    (7,5,"232阿秒实验"),
    (9,5,"宇宙学 Λ(t) 检验")
]

for i,(x,y,lab) in enumerate(steps):
    ax.text(x,y,lab,ha='center',fontsize=12,
            bbox=dict(boxstyle='round',facecolor='lightblue'))
    if i < len(steps)-1:
        ax.arrow(x+0.7,y,0.6,0,head_width=0.1,head_length=0.1,color='k')

ax.text(5,2.5,"统一图景证实与完善",ha='center',fontsize=14,
        bbox=dict(boxstyle='round',facecolor='lightgreen'))

plt.title('图7.7 未来实验与数值验证路线图')
plt.tight_layout()
plt.savefig('fig7_7.png',dpi=300)
plt.show()
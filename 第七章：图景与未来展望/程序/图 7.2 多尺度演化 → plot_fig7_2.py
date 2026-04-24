import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']

scales = [1e-35, 1e-10, 1, 1e26]
labels = ['普朗克尺度\n离散流形', '原子尺度\n规范场', '宏观尺度\n广义相对论', '宇宙尺度\nΛCDM']
yvals = [0.2, 0.5, 0.8, 0.95]

plt.figure(figsize=(10,4))
plt.plot(scales, yvals, 'ko-', lw=3, ms=10)
for x,y,l in zip(scales,yvals,labels):
    plt.text(x,y+0.04,l,ha='center',fontsize=11)
plt.xscale('log')
plt.ylim(0,1.2)
plt.xlabel('尺度 (m)')
plt.ylabel('连续程度 / 曲率')
plt.title('图7.2 多尺度演化与连续极限的涌现')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig7_2.png',dpi=300)
plt.show()
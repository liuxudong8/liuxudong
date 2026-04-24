import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

x, y = np.meshgrid(np.linspace(-3,3,100), np.linspace(-3,3,100))
z = np.exp(-((x-1)**2 + y**2)/2) + np.exp(-((x+1)**2 + (y-1)**2)/2) + np.exp(-((x)**2 + (y+1.5)**2)/2)

peaks = np.array([[1,0],[-1,1],[0,-1.5]])

fig, (ax1, ax2, ax3) = plt.subplots(1,3,figsize=(15,4))

ax1.contourf(x,y,z,cmap='coolwarm')
ax1.scatter(peaks[:,0], peaks[:,1], color='red',s=60,label='顶点 |ψ|² 极大')
ax1.set_title('(a) 顶点提取')
ax1.legend()
ax1.axis('equal')

ax2.contourf(x,y,z,cmap='coolwarm')
ax2.scatter(peaks[:,0], peaks[:,1], color='red',s=60)
for i in range(len(peaks)):
    for j in range(i+1, len(peaks)):
        ax2.plot([peaks[i,0], peaks[j,0]], [peaks[i,1], peaks[j,1]], 'b-',lw=2)
ax2.set_title('(b) 相位相干边')
ax2.axis('equal')

ax3.contourf(x,y,z,cmap='coolwarm')
ax3.scatter(peaks[:,0], peaks[:,1], color='red',s=60)
for i in range(len(peaks)):
    for j in range(i+1, len(peaks)):
        ax3.plot([peaks[i,0], peaks[j,0]], [peaks[i,1], peaks[j,1]], 'b-',lw=2)
ax3.fill([0,1,-1],[0,0,-1.5], color='green',alpha=0.3)
ax3.set_title('(c) 稳定高维单形')
ax3.axis('equal')

plt.suptitle('图7.1 离散流形 $M_d$ 的生成与演化')
plt.tight_layout()
plt.savefig('fig7_1.png',dpi=300)
plt.show()
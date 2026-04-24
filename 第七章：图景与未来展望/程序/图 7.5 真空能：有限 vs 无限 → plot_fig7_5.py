import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']

fig, (ax1, ax2) = plt.subplots(1,2,figsize=(12,5))

x = np.linspace(0,10,200)
y = x**4
ax1.plot(x,y,'b-',lw=3)
ax1.set_ylim(0,1000)
ax1.set_title('传统场论：无穷积分（发散）')
ax1.text(4,600,r'$\rho \sim \int d^4k \to \infty$',fontsize=14)

xs = np.linspace(0,10,15)
ys = np.minimum(0.1*xs**2, 10)
ax2.scatter(xs,ys,c='red',s=40)
ax2.set_ylim(0,12)
ax2.set_title('离散框架：有限求和（收敛）')
ax2.text(3,7,r'$\rho \sim \sum_{\sigma\in M_d} \mu(\sigma)$',fontsize=14)

plt.suptitle('图7.5 真空能：有限求和 vs 无穷积分')
plt.tight_layout()
plt.savefig('fig7_5.png',dpi=300)
plt.show()
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']

t = np.linspace(0,500,200)
tau = 232
F = 1 - np.exp(-t/tau)

fig, (ax1, ax2) = plt.subplots(2,1,figsize=(8,8))

ax1.axis('off')
ax1.set_xlim(-2,2)
ax1.set_ylim(-1,1)
ax1.scatter(-1,0,color='blue',s=300,label='电子1')
ax1.scatter(1,0,color='blue',s=300,label='电子2')
ax1.arrow(-0.8,0,1.6,0,color='red',lw=3,head_width=0.05)
ax1.text(0,0.5,r'$a_0$ 相位传播',ha='center',fontsize=14)
ax1.set_title('纠缠的拓扑融合过程')

ax2.plot(t, F, 'b-', lw=3)
ax2.axvline(tau, color='red', ls='--', label=r'$\tau=232$ 阿秒')
ax2.set_xlabel('时间 (as)')
ax2.set_ylabel('纠缠保真度')
ax2.set_title(r'$F(t)=1-e^{-t/\tau}$')
ax2.legend()
ax2.grid(alpha=0.3)

plt.suptitle('图7.6 232阿秒纠缠时间的几何约束')
plt.tight_layout()
plt.savefig('fig7_6.png',dpi=300)
plt.show()
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jn

plt.rcParams['font.sans-serif'] = ['SimHei']

r = np.linspace(0,10,500)
j2 = jn(2,r)
j3 = jn(3,r)
j5 = jn(5,r)

plt.figure(figsize=(10,5))
plt.plot(r, j2, label=r'$j_2(r)$ → $θ_{12}$',lw=2)
plt.plot(r, j3, label=r'$j_3(r)$ → $θ_{23}$',lw=2)
plt.plot(r, j5, label=r'$j_5(r)$ → $θ_{13}$',lw=2)
plt.axhline(0,color='k',ls='--',alpha=0.5)
plt.xlabel('r')
plt.ylabel('球贝塞尔函数')
plt.title('图7.4 CKM 混合角的几何起源')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig7_4.png',dpi=300)
plt.show()
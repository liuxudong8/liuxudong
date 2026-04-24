import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']

fig, ax = plt.subplots(figsize=(8,9))
ax.set_ylim(0,10)
ax.set_xlim(-5,5)
ax.axis('off')

ax.fill_between([-5,5],0,2,color='saddlebrown',label='引力：大地')
ax.text(0,1,'引力：大地之形',ha='center',fontsize=14,c='white')

def tree(x,label,color):
    ax.plot([x,x],[2,6],color=color,lw=6)
    ax.text(x,6.5,label,ha='center',fontsize=12)

tree(-3,'电磁力', 'blue')
tree(0,'弱力', 'orange')
tree(3,'强力', 'red')

ax.scatter(-3,7,color='blue',s=150,label='粒子：果实')
ax.scatter(0,7.2,color='red',s=150)
ax.scatter(3,7.1,color='green',s=150)
ax.text(0,9,'大地无需言说，万物自织其形',ha='center',fontsize=16)

plt.title('图7.3 大地·树·果：四种相互作用的几何归约',y=0.93)
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig('fig7_3.png',dpi=300)
plt.show()
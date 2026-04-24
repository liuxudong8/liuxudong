import numpy as np
import random

def generate_discrete_network(num_nodes, connection_prob=0.3):
    nodes = list(range(num_nodes))
    adjacency_matrix = np.zeros((num_nodes, num_nodes), dtype=complex)
    edges = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < connection_prob:
                psi = np.exp(1j * random.uniform(0, 2 * np.pi))
                adjacency_matrix[i, j] = psi
                adjacency_matrix[j, i] = np.conj(psi)
                edges.append((i, j))
    return nodes, edges, adjacency_matrix

if __name__ == "__main__":
    nodes, edges, adj = generate_discrete_network(10, 0.3)
    print("节点数:", len(nodes))
    print("关联数:", len(edges))
    print("邻接矩阵:\n", adj)
    
import numpy as np
import networkx as nx

def detect_topological_knots(adjacency_matrix, psi_threshold=0.5):
    N = adjacency_matrix.shape[0]
    G = nx.Graph()
    for i in range(N):
        for j in range(i + 1, N):
            if abs(adjacency_matrix[i, j]) >= psi_threshold:
                G.add_edge(i, j)
    cycles = []
    try:
        for cycle in nx.cycle_basis(G):
            if len(cycle) >= 3:
                cycles.append(cycle)
    except:
        pass
    stable_knots = []
    for cycle in cycles:
        psi_values = []
        for k in range(len(cycle)):
            i = cycle[k]
            j = cycle[(k + 1) % len(cycle)]
            psi_values.append(abs(adjacency_matrix[i, j]))
        min_psi = min(psi_values)
        stable = min_psi > psi_threshold
        stable_knots.append({
            "cycle": cycle,
            "min_psi": min_psi,
            "stable": stable
        })
    return stable_knots

if __name__ == "__main__":
    from network_generator import generate_discrete_network
    nodes, edges, adj = generate_discrete_network(8, 0.6)
    knots = detect_topological_knots(adj, psi_threshold=0.3)
    print("识别到拓扑结:")
    for knot in knots:
        print(f"路径: {knot['cycle']}, 最小Ψ: {knot['min_psi']:.3f}, 稳定: {knot['stable']}")
        
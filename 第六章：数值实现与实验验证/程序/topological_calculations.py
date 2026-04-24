import numpy as np
from sympy import Poly, symbols

def jones_polynomial_31():
    q = symbols('q')
    V = Poly(q**4 - q**3 - q, q)
    return V

def compute_chern_number(adjacency_matrix):
    N = adjacency_matrix.shape[0]
    phase = np.angle(adjacency_matrix)
    grad_phase = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j:
                grad_phase[i, j] = phase[i, j] - phase[i, 0]
    chern = np.sum(grad_phase) / (2 * np.pi)
    return chern

def compute_mixing_angles():
    phi = (1 + np.sqrt(5)) / 2
    V31 = 1.542
    theta12 = np.arcsin(np.sqrt(1 / (V31**2))) * 180 / np.pi
    theta23 = np.arctan(phi) * 180 / np.pi
    theta13 = np.arcsin(1 / (2 * phi**2)) * 180 / np.pi
    return {"theta12": theta12, "theta23": theta23, "theta13": theta13}

if __name__ == "__main__":
    V = jones_polynomial_31()
    print("三叶结Jones多项式:", V)
    from network_generator import generate_discrete_network
    nodes, edges, adj = generate_discrete_network(6, 0.7)
    chern = compute_chern_number(adj)
    print("近似陈数:", chern)
    angles = compute_mixing_angles()
    print("轻子混合角:")
    for k, v in angles.items():
        print(f"{k}: {v:.2f}°")
        
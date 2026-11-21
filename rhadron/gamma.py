"""Euclidean gamma matrices in the DeGrand-Rossi basis (Chroma / QUDA / PyQUDA convention).
gamma[0..3] = gamma_x, gamma_y, gamma_z, gamma_t;  gamma5 = g_x g_y g_z g_t = diag(1, 1, -1, -1)."""
import numpy as np

i = 1j
G = np.zeros((4, 4, 4), dtype=complex)
G[0] = [[0, 0, 0, i], [0, 0, i, 0], [0, -i, 0, 0], [-i, 0, 0, 0]]
G[1] = [[0, 0, 0, -1], [0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0]]
G[2] = [[0, 0, i, 0], [0, 0, 0, -i], [-i, 0, 0, 0], [0, i, 0, 0]]
G[3] = [[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
G5 = G[0] @ G[1] @ G[2] @ G[3]
ONE = np.eye(4, dtype=complex)
C = G[1] @ G[3]  # charge conjugation C = gamma_y gamma_t (DeGrand-Rossi): C g_mu C^-1 = -g_mu^T
P_PLUS = 0.5 * (ONE + G[3])
P_MINUS = 0.5 * (ONE - G[3])

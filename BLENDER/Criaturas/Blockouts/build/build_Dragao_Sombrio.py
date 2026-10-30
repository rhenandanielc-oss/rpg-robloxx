# Dragao Sombrio (Terras Corrompidas): varios chifres, espinhos maiores em fileira dupla, asas com esporas (mais recortadas).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dragao_base import *
P = {"largura": 1.0, "pescoco": 1.0, "raio_pescoco": 1.1, "perna": 1.15, "cabeca": 1.1, "dedos": DEDOS, "espinho": 3.6, "espinho_r": 1.0, "espinho_seg": 8,
     "fileiras": (-0.9, 0.9), "espora": 4.0,
     "chifres": [{"pts": [(1.5, -1.6, 2.3), (2.6, 0.6, 4.4), (2.9, 3.0, 5.0), (2.6, 4.6, 4.2)], "r": 0.9},
                 {"pts": [(2.2, -0.4, 1.4), (3.6, 1.6, 2.2), (4.6, 3.6, 2.2)], "r": 0.6},
                 {"pts": [(2.1, -3.6, -0.6), (3.2, -2.6, -1.4)], "r": 0.4},
                 {"pts": [(0.8, -0.2, 2.8), (1.0, 2.0, 4.4)], "r": 0.45}]}
if __name__ == "__main__":
    a = args(); construir("Dragao_Sombrio", a.pose, P); salvar(a.out)


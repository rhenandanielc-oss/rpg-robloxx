# Dragao Glacial (Tundra Congelada): mais esguio, pescoco mais longo, chifres retos, espinhos cristalinos altos e finos.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dragao_base import *
P = {"largura": 0.85, "pescoco": 1.15, "raio_pescoco": 0.95, "perna": 1.0, "cabeca": 1.05, "dedos": DEDOS, "espinho": 3.2, "espinho_r": 0.75, "espinho_seg": 6,
     "chifres": [{"pts": [(1.3, -1.4, 2.4), (1.8, 2.2, 5.2), (2.1, 4.4, 6.6)], "r": 0.7},
                 {"pts": [(2.0, -0.6, 1.4), (3.0, 2.2, 2.6)], "r": 0.45}]}
if __name__ == "__main__":
    a = args(); construir("Dragao_Glacial", a.pose, P); salvar(a.out)


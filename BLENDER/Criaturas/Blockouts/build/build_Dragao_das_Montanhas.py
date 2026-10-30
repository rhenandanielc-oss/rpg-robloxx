# Dragao das Montanhas (Montanhas Altas): robusto, placas rochosas largas, par de chifres curvos para tras.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dragao_base import *
P = {"largura": 1.0, "pescoco": 1.0, "raio_pescoco": 1.2, "perna": 1.25, "cabeca": 1.15, "dedos": DEDOS, "espinho": 3.0, "espinho_r": 1.3, "espinho_seg": 6,
     "chifres": [{"pts": [(1.6, -1.4, 2.3), (2.7, 1.0, 3.6), (3.3, 3.4, 2.8), (3.5, 5.0, 0.8)], "r": 0.95}]}
if __name__ == "__main__":
    a = args(); construir("Dragao_das_Montanhas", a.pose, P); salvar(a.out)


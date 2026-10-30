# Lobo Ancestral (Floresta Ancestral): esguio/atletico, ombro 6,5 (oficial 5,5-7).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lobo_base import *
if __name__ == "__main__":
    a = args()
    construir("Lobo_Ancestral", a.pose, {"escala": 1.0, "largura": 1.0, "colar": 1.0, "cauda": 1.0, "perna": 1.25})
    salvar(a.out)


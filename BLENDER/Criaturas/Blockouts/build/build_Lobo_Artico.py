# Lobo Artico (Tundra Congelada): "mais robusto" (RPG_02), ombro 6,6 (oficial 5,5-7).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lobo_base import *
if __name__ == "__main__":
    a = args()
    construir("Lobo_Artico", a.pose, {"escala": 6.6 / 6.5, "largura": 1.2, "colar": 1.25, "cauda": 1.05, "perna": 1.4,
                           "dorso": -0.35, "calcas": 1, "ventre": 0.35, "passada": {"DE": -8, "DD": 16, "TE": 17, "TD": -4}})
    salvar(a.out)



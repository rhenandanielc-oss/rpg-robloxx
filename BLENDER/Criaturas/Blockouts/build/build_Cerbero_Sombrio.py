# Cerbero Sombrio (Terras Corrompidas). RPG_02: "corpo quadrupede canino musculoso com tres cabecas"; 12-16 studs ate os
# ombros (usado 14). Base canina dos Lobos com 3 pescocos/cabecas e parametros de musculatura (# inferred).
# A silhueta oficial esta em 3/4 e fundida a rochas: so comparacao visual (sem IoU).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lobo_base import *
if __name__ == "__main__":
    a = args()
    construir("Cerbero_Sombrio", a.pose, {"escala": 14 / 6.5, "largura": 1.4, "colar": 1.3, "cauda": 0.75, "perna": 1.55,
                                          "dorso": 0.0, "ventre": 0.2, "cabecas": 3, "oficial": "12-16 ombro"})
    salvar(a.out)


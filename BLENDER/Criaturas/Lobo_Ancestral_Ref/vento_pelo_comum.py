"""Formula UNICA do balanco do pelo ao vento (a mesma do VentoPelo_Cliente.luau no Roblox) + gerador do modulo Luau.
A forca do pelo segue a forca do vento do jogo (workspace.GlobalWind, que o clima muda) somada ao ar do proprio
movimento. Unidades: vento em studs/s; angulos em graus.
- forca(w): 0 -> MINIMO (pelo nunca 100% parado); REF studs/s -> ~1 (vento forte); tempestade -> ate MAXIMO.
- rajada lenta + tremulacao; as frequencias SOBEM com o vento (tempestade tremula mais rapido).
Uso (gerar o modulo): blender -b rig9/Lobo_Ancestral_Rig.blend -P vento_pelo_comum.py -- <saida.luau>"""
import math
MINIMO, REF, EXPOENTE, MAXIMO = 0.10, 12.0, 0.85, 1.75
AR_MOVIMENTO = 0.12                       # fracao da velocidade do corpo que vira vento relativo no pelo
# amplitude base (graus) por osso e fase; o lado D/E e as cadeias "...2" ja vem com fases proprias
AMP = {"PeloNuca1": (11, 0.0), "PeloNuca2": (14, 0.9), "PeloJubaE1": (11, 0.4), "PeloJubaD1": (11, 0.7), "PeloJubaE2": (14, 1.3),
       "PeloJubaD2": (14, 1.6), "PeloBochechaE": (6, 0.2), "PeloBochechaD": (6, 0.5), "PeloPeito1": (9, 0.6), "PeloPeito2": (12, 1.4),
       "PeloDorso1": (6, 1.0), "PeloDorso2": (6, 1.8), "PeloBarriga": (9, 2.2), "PeloCotoveloE": (8, 0.3), "PeloCotoveloD": (8, 0.8),
       "PeloCoxaE": (6, 2.6), "PeloCoxaD": (6, 2.9), "JubaE": (4, 0.5), "JubaD": (4, 0.8), "JubaPeito": (3, 1.1),
       "Cauda1": (2, 0.0), "Cauda2": (3, 0.45), "Cauda3": (4, 0.9), "Cauda4": (5, 1.35), "Cauda5": (6, 1.8), "Cauda6": (7, 2.25), "Cauda7": (7.5, 2.7)}
def forca(w):
    return min(MAXIMO, MINIMO + (max(w, 0.0) / REF) ** EXPOENTE)
def freqs(w):
    return 0.22 + 0.02 * w, 1.3 + 0.10 * w, 2.6 + 0.20 * w
def ganho(t, fase, w):
    f1, f2, f3 = freqs(w)
    return (0.55 + 0.30 * math.sin(2 * math.pi * f1 * t + fase) + 0.12 * math.sin(2 * math.pi * f2 * t + 1.7 * fase)
            + 0.05 * math.sin(2 * math.pi * f3 * t + 2.3 * fase))

if __name__ == "__main__":
    import bpy, sys, os
    OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
    BD = bpy.data.objects["Lobo_Ancestral_Rig"].data.bones
    linhas = []
    for nm, (amp, fase) in AMP.items():
        if nm not in BD: continue
        d = (BD[nm].tail_local - BD[nm].head_local).normalized()
        gx, gy, gz = d.x, d.z, -d.y                                   # Blender (z para cima) -> glTF/Roblox (y para cima)
        linhas.append('\t%s = {amp = %g, fase = %g, dir = Vector3.new(%.4f, %.4f, %.4f)},' % (nm, amp, fase, gx, gy, gz))
    txt = """-- PeloVento_Lobo (ModuleScript) - GERADO por BLENDER/Criaturas/Lobo_Ancestral_Ref/vento_pelo_comum.py (nao editar a mao).
-- Ossos de pelo do Lobo Ancestral: amplitude base (graus), fase e direcao da mecha no REPOUSO, no espaco do modelo
-- (glTF, Y para cima; frente do lobo = +Z no glTF - o importador do Roblox pode girar: conferir no Studio).
return {
	curva = {minimo = %g, ref = %g, expoente = %g, maximo = %g, arMovimento = %g},
	ossos = {
%s
	},
}
""" % (MINIMO, REF, EXPOENTE, MAXIMO, AR_MOVIMENTO, "\n".join(linhas))
    open(OUT, "w", encoding="utf-8").write(txt); print("MODULO", OUT, len(linhas), "ossos")

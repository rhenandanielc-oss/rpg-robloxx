"""Gradiente de pesos na dobradica da asa (cabeca de wing_1): a asa gira como bloco e a fronteira asa/corpo era uma linha
em dente de serra de 1-2 arestas; no bater (60+ graus) a raiz do braco atravessava o dorso e saia em lascas. Aqui, perto
da dobradica, a fracao da asa no peso cresce suave ao longo do braco: f = suave((s - S0) / (S1 - S0)), s = distancia ao
longo do braco a partir da dobradica (negativo = para dentro do corpo); o resto vai para a coluna mais proxima.
O efeito some radialmente (RAIO) para nao criar degrau. Uso: blender -b X.blend -P dobradica_asa.py [-- S0 S1 RAIO]"""
import bpy, sys
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
S0 = float(args[0]) if args else -0.03; S1 = float(args[1]) if len(args) > 1 else 0.08
RAIO = float(args[2]) if len(args) > 2 else 0.13
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}; gn = {g.name: g.index for g in M.vertex_groups}
def suave(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def eh_asa(n): return n.startswith(("wing_", "shoulder_"))
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12))); return (p - (a + ab * t)).length
COLUNA = [n for n in ("spine_0", "spine_1", "spine_2", "spine_3") if n in gn]
SEGC = {n: (A.data.bones[n].head_local, A.data.bones[n].tail_local) for n in COLUNA}
mud = 0; vg = M.vertex_groups
for s in ("l", "r"):
    b = A.data.bones["wing_1_" + s]; H = b.head_local.copy(); u = (b.tail_local - b.head_local).normalized()
    sinal = 1 if H.x > 0 else -1
    for v in M.data.vertices:
        p = v.co; d = (p - H).length
        if d > RAIO or p.x * sinal < 0.05: continue
        W = {gi[g.group]: g.weight for g in v.groups if g.weight > 1e-5}
        if any(n.startswith(("front_", "collar_", "back_", "tail")) for n, w in W.items() if w > 0.3): continue
        wa = {n: w for n, w in W.items() if eh_asa(n)}; wc = {n: w for n, w in W.items() if not eh_asa(n)}
        f = suave((((p - H).dot(u)) - S0) / (S1 - S0))
        if not wa: wa = {"wing_1_" + s: 1.0}
        if not wc: wc = {min(COLUNA, key=lambda n: dist_seg(p, *SEGC[n])): 1.0}
        sa, sc_ = sum(wa.values()), sum(wc.values())
        novo = {n: f * w / sa for n, w in wa.items()}
        for n, w in wc.items(): novo[n] = novo.get(n, 0) + (1 - f) * w / sc_
        g = 1 - suave((d - RAIO * 0.6) / (RAIO * 0.4))            # some na borda do raio
        tot = sum(W.values()) or 1.0
        fin = {n: (1 - g) * W.get(n, 0) / tot + g * novo.get(n, 0) for n in set(W) | set(novo)}
        top = sorted(fin.items(), key=lambda t: -t[1])[:4]; ss = sum(w for _, w in top) or 1.0
        for x in list(v.groups): vg[x.group].remove([v.index])
        for n, w in top:
            if w / ss > 0.01: vg[n].add([v.index], w / ss, "REPLACE")
        mud += 1
print("DOBRADICA vertices", mud, "S0", S0, "S1", S1, "RAIO", RAIO)
bpy.ops.wm.save_mainfile()
print("DOBRADICA_OK")

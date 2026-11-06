# E2 - ferrao (RPG_02 oficial: ferroada com a cauda, toxina biologica inata). A ponta em losango do Ashwing
# e REMODELADA (mesmos vertices, UV e pesos): bulbo de glandula + gancho curvo para baixo, como no painel 04.
# Nao cria malha nova nem material novo (mantem 1 material para o Roblox).
# Uso: blender -b Wyvern_E1.blend -P 02_ferrao.py -- <saida.blend> [comprimento] [curva_graus]
import bpy, sys, math, json
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]; COMP = float(argv[1]) if len(argv) > 1 else 5.5; CURVA = float(argv[2]) if len(argv) > 2 else 105.0
mesh = bpy.data.objects["Wyvern"]; me = mesh.data
ys = [v.co.y for v in me.vertices]; y_max = max(ys)
Y0 = y_max - 5.5           # inicio do losango original (fatia y+2,5 da inspecao)
BIN = 0.25
# perfil atual por fatia: centro z e meias-larguras
fat = {}
for v in me.vertices:
    if v.co.y >= Y0 - 0.5:
        k = int((v.co.y - Y0) // BIN)
        f = fat.setdefault(k, [1e9, -1e9, 1e9, -1e9]); f[0] = min(f[0], v.co.x); f[1] = max(f[1], v.co.x); f[2] = min(f[2], v.co.z); f[3] = max(f[3], v.co.z)
def perfil(y):
    f = fat[int((y - Y0) // BIN)]
    return (f[0] + f[1]) / 2, (f[2] + f[3]) / 2, max((f[1] - f[0]) / 2, 0.02), max((f[3] - f[2]) / 2, 0.02)
xc0, zc0, hw0, hh0 = perfil(Y0 - 0.3)
R0 = (hw0 + hh0) / 2                       # raio da cauda antes da ponta
L0 = y_max - Y0
def raio(t):
    # bulbo da glandula (sobe suave ate 2,1x no t=0,22) e depois o gancho afina ate a ponta
    if t < 0.22: return R0 * (1 + 1.1 * (0.5 - 0.5 * math.cos(math.pi * t / 0.22)))
    u = (t - 0.22) / 0.78
    return R0 * 2.1 * (1 - u) ** 1.15 + 0.02
# linha central em arco no plano y-z (curva para baixo/frente), integrada em passos
N = 200; C = [Vector((xc0, Y0, zc0))]; ang = [0.0]
for i in range(1, N + 1):
    t = i / N; a = math.radians(CURVA) * t ** 1.6
    C.append(C[-1] + Vector((0, math.cos(a), -math.sin(a))) * (COMP / N)); ang.append(a)
def centro(t):
    i = min(N - 1, int(t * N)); f = t * N - i
    return C[i].lerp(C[i + 1], f), ang[i] + (ang[i + 1] - ang[i]) * f
novo = {}
for v in me.vertices:
    y = v.co.y
    if y < Y0: continue
    t = (y - Y0) / L0
    xc, zc, hw, hh = perfil(y)
    p = Vector(((v.co.x - xc) / hw, (v.co.z - zc) / hh))
    if p.length > 1: p.normalize()
    r = raio(t); c, a = centro(t)
    # secao transversal girada junto com a tangente (normal = z local inclinado)
    nz = Vector((0, math.sin(a), math.cos(a)))
    novo[v.index] = c + Vector((p.x * r, 0, 0)) + nz * (p.y * r)
# suaviza a transicao: mistura nos 0,4 iniciais
for v in me.vertices:
    if v.index in novo:
        t = (v.co.y - Y0) / L0
        w = min(1.0, t / 0.04)
        novo[v.index] = v.co.lerp(novo[v.index], w)
if me.shape_keys:
    base = me.shape_keys.reference_key
    for kb in me.shape_keys.key_blocks:
        if kb == base: continue
        for i, c in novo.items(): kb.data[i].co = c + (kb.data[i].co - base.data[i].co)
    for i, c in novo.items(): base.data[i].co = c
for i, c in novo.items(): me.vertices[i].co = c
me.update()
# a ponta fica no ultimo osso da cauda: reforca o peso em tail_10 a partir do bulbo
g10 = mesh.vertex_groups["tail_10"]
for i in novo:
    v = me.vertices[i]
    if (ys[i] - Y0) / L0 > 0.3:
        for g in v.groups: g.weight = 0.0
        g10.add([i], 1.0, "REPLACE")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("RJSON" + json.dumps({"Y0": round(Y0, 2), "R0": round(R0, 3), "vertices_remodelados": len(novo), "comp": COMP, "curva": CURVA}) + "RFIM")

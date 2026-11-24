"""Aura de FOGO A4 (20/11) - pedido "Cerbero Sombrio - fogo mais realista, brilhante e impactante". Copia de revisao: abre
aura/CR_Cerbero_Fogo_A3.blend (A3 aceita, intacta) e grava aura/A4/CR_Cerbero_Fogo_A4.blend.
Muda (Blender; valores [A TESTAR]):
  * PELE: sem pintura laranja (decisao do usuario 20/11 "nao quero seu corpo alaranjado, somente o fogo"): o shader da A3 fica
    so como brasa quase nula (x0,03); o pelo continua escuro e visivel entre as chamas. A integracao vem da LUZ local do fogo.
  * CHAMAS espalhadas pelo corpo (juba das 3 cabecas, pescocos, peito, ombros, dorso, flancos, pernas por fora, cauda):
    pontos amostrados na superficie pelo peso "fogo" da A3 x manchas de intensidade (ruido de baixa frequencia) -> areas mais
    densas e intervalos com pelo visivel; distancia minima entre bases (sem grade regular). Cada ponto = lingua principal +
    lingua "filha" (divisao), presas ao osso de maior peso do vertice (a base acompanha a pele no movimento).
  * CICLO DE VIDA no shader (cada lingua com fase/periodo proprios): nasce, cresce, divide, sobe soltando a base e some; a
    cada ciclo muda um pouco de posicao lateral e de altura (ruido por ciclo) -> sem repeticao sincronizada.
  * Movimento: sobe com turbulencia e pontas curvas; inclinacao para tras e estiramento pela propriedade de cena "inclina"
    (corrida = 1) com ATRASO na metade traseira ("inclina_atraso").
  * Brilho: nucleo amarelo so nos pontos mais quentes, laranja vivo, vermelho na base; forca maior que a A3 mas com teto
    (detalhes de olhos/focinho/dentes preservados: rosto sem chamas).
  * Luz local: 9 luzes pontuais pequenas presas aos ossos (juba x3, peito, dorso x2, quadril, cauda, ombro) com cintilacao.
  * Furia: propriedade de cena "violeta" (0/1) troca a rampa das chamas e a cor das luzes para o violeta (mesmo movimento).
r4 (20/11, pedido "ajustar o dorso"): a fileira de chamas na crista lia como espinhos -> peso 0,30 na crista (mais nos
lados), distancia minima irregular 1,1-2,0, alturas sorteadas x0,6/0,85/1,0/1,25, inclinacao lateral propria, filha para
qualquer lado. r3 guardada em A4/r3_antes_dorso/.
Uso: blender -b -t 2 CR_Cerbero_Fogo_A3.blend -P fogo_A4.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector as V, Matrix, noise
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.threads_mode = "FIXED"; sc.render.threads = 2; rnd = random.Random(23)
rig = bpy.data.objects["Cerbero_Rig"]
for o in [o for o in bpy.data.objects if o.name.startswith("ChamaA3_")]: bpy.data.objects.remove(o)      # chamas da A3 saem (a A3 fica intacta no arquivo dela)
if rig.animation_data:
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
CAB, CORPO = bpy.data.objects["Cerbero_Cabecas"], bpy.data.objects["Cerbero_Corpo"]
BD = rig.data.bones
for k in ("inclina", "inclina_atraso", "violeta"): sc[k] = 0.0
# ------------------------------------------------------------------ pele: a pintura da A3 vira so brasa fraca
for o in (CAB, CORPO):
    for m in o.data.materials:
        b_ = m.node_tree.nodes.get("Principled BSDF")
        if b_: b_.inputs["Emission Strength"].default_value = 0.03
# ------------------------------------------------------------------ nos
def lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)
C_BRASA, C_VERM, C_LAR, C_AMAR = lin("4a0600"), lin("d02000"), lin("ff6a00"), lin("ffd65a")
V_ESC, V_MED, V_CLA, V_NUC = lin("1e0033"), lin("6a1bd6"), lin("a65cff"), lin("efe2ff")
def no(nt, tipo, **kw):
    n_ = nt.nodes.new(tipo)
    for k, v in kw.items(): setattr(n_, k, v)
    return n_
def op(nt, oper, a, b=None):
    n_ = nt.nodes.new("ShaderNodeMath"); n_.operation = oper
    for i_, x in enumerate((a, b)):
        if x is None: continue
        if isinstance(x, (int, float)): n_.inputs[i_].default_value = x
        else: nt.links.new(x, n_.inputs[i_])
    return n_.outputs[0]
def rampa(nt, fator, cores):
    cr = no(nt, "ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0, 0, 0, 1); el[1].position, el[1].color = 1.0, cores[3]
    for pos, c in ((0.15, cores[0]), (0.42, cores[1]), (0.70, cores[2]), (0.86, cores[2])):
        e = el.new(pos); e.color = c
    nt.links.new(fator, cr.inputs[0]); return cr.outputs[0]
def suave(nt, a, b, x):
    mr = no(nt, "ShaderNodeMapRange", interpolation_type="SMOOTHSTEP"); mr.inputs["From Min"].default_value = a; mr.inputs["From Max"].default_value = b
    nt.links.new(x, mr.inputs["Value"]); return mr.outputs[0]
def attr(nt, nome, tipo="OBJECT"): return no(nt, "ShaderNodeAttribute", attribute_type=tipo, attribute_name=nome).outputs["Fac"]
# ------------------------------------------------------------------ material da lingua A4 (ciclo de vida no shader)
mc = bpy.data.materials.new("M_Chama_A4"); nt = mc.node_tree; nt.nodes.clear()
out = no(nt, "ShaderNodeOutputMaterial"); em = no(nt, "ShaderNodeEmission"); trn = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
nt.links.new(trn.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
tv = no(nt, "ShaderNodeValue", name="tempo").outputs[0]
sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0]); u_, v_ = sp.outputs["X"], sp.outputs["Y"]
fase, periodo, forca, semente = attr(nt, "fase"), attr(nt, "periodo"), attr(nt, "forca"), attr(nt, "semente")
inclina = op(nt, "MAXIMUM", attr(nt, "inclina", "VIEW_LAYER"), attr(nt, "inclina_atraso", "VIEW_LAYER"))
violeta = attr(nt, "violeta", "VIEW_LAYER")
t_ciclo = op(nt, "ADD", op(nt, "DIVIDE", tv, periodo), fase)
idade = op(nt, "FRACT", t_ciclo); ciclo = op(nt, "FLOOR", t_ciclo)
def wn(desloc):
    w = no(nt, "ShaderNodeTexWhiteNoise", noise_dimensions="1D")
    nt.links.new(op(nt, "ADD", op(nt, "ADD", ciclo, op(nt, "MULTIPLY", semente, 97.0)), desloc), w.inputs["W"]); return w.outputs["Value"]
desvio = op(nt, "MULTIPLY", op(nt, "SUBTRACT", wn(0.0), 0.5), 0.26)                 # muda de posicao a cada ciclo
h_ciclo = op(nt, "ADD", 0.70, op(nt, "MULTIPLY", wn(17.0), 0.45))                    # e de altura
cresce = suave(nt, 0.0, 0.32, idade)
solta = op(nt, "MULTIPLY", suave(nt, 0.62, 1.0, idade), 0.32)          # r3: base sobe pouco (nao flutuar)                        # no fim a base solta e sobe
altura = op(nt, "MULTIPLY", op(nt, "MULTIPLY", cresce, h_ciclo), op(nt, "ADD", 0.92, op(nt, "MULTIPLY", inclina, 0.30)))
vn = op(nt, "DIVIDE", op(nt, "SUBTRACT", v_, solta), op(nt, "MAXIMUM", op(nt, "MULTIPLY", altura, 0.80), 0.02))   # 0 base .. 1 ponta
ritmo = op(nt, "ADD", 0.8, op(nt, "MULTIPLY", semente, 0.7))
vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", u_, 2.6), vec.inputs["X"])
nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", v_, 2.2), op(nt, "MULTIPLY", tv, op(nt, "MULTIPLY", ritmo, 2.4))), vec.inputs["Y"])
nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 2.4; nz.inputs["Detail"].default_value = 5.0
nz.inputs["Distortion"].default_value = 1.2; nt.links.new(vec.outputs[0], nz.inputs["Vector"])
nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", semente, 31.0), op(nt, "MULTIPLY", tv, 0.6)), nz.inputs["W"])
turb = op(nt, "SUBTRACT", nz.outputs["Fac"], 0.5)
vnc = op(nt, "MINIMUM", op(nt, "MAXIMUM", vn, 0.0), 1.0)
nz2 = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz2.inputs["Scale"].default_value = 0.9; nz2.inputs["Detail"].default_value = 1.0
nt.links.new(vec.outputs[0], nz2.inputs["Vector"]); nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", semente, 13.0), op(nt, "MULTIPLY", tv, 0.35)), nz2.inputs["W"])
onda = op(nt, "SUBTRACT", nz2.outputs["Fac"], 0.5)                                              # r2: balanco largo (labareda ondulada)
curva = op(nt, "ADD", op(nt, "MULTIPLY", turb, op(nt, "MULTIPLY", op(nt, "POWER", vnc, 1.1), 0.95)), op(nt, "MULTIPLY", onda, op(nt, "MULTIPLY", vnc, 0.9)))
dx = op(nt, "ABSOLUTE", op(nt, "SUBTRACT", op(nt, "SUBTRACT", u_, op(nt, "ADD", 0.5, desvio)), curva))
larg = op(nt, "MULTIPLY", op(nt, "POWER", op(nt, "SUBTRACT", 1.0, vnc), 0.75), 0.25)          # r2: lingua fina (r1 virava gota de vela)
forma = op(nt, "SUBTRACT", larg, dx)
fib = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); fib.inputs["Scale"].default_value = 7.0; fib.inputs["Detail"].default_value = 3.0
vf = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", u_, 6.0), vf.inputs["X"]); nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", v_, 1.2), op(nt, "MULTIPLY", tv, 1.8)), vf.inputs["Y"])
nt.links.new(vf.outputs[0], fib.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", semente, 7.0), fib.inputs["W"])
dens = op(nt, "MULTIPLY", op(nt, "MULTIPLY", forma, 6.5), op(nt, "ADD", 0.45, nz.outputs["Fac"]))      # r2: borda macia
dens = op(nt, "MULTIPLY", dens, op(nt, "ADD", 0.70, op(nt, "MULTIPLY", fib.outputs["Fac"], 0.6)))         # fios/estrias da labareda
dens = op(nt, "MINIMUM", op(nt, "MAXIMUM", dens, 0.0), 1.0)
dentro = op(nt, "MULTIPLY", op(nt, "GREATER_THAN", vn, 0.0), op(nt, "LESS_THAN", vn, 1.0))
raiz = op(nt, "POWER", op(nt, "MINIMUM", op(nt, "MULTIPLY", vnc, 8.0), 1.0), 0.8)   # r3: base presente, colada ao pelo         # raiz macia, aderente ao pelo
vida = op(nt, "MULTIPLY", suave(nt, 0.0, 0.10, idade), op(nt, "SUBTRACT", 1.0, suave(nt, 0.78, 1.0, idade)))
dens = op(nt, "MULTIPLY", op(nt, "MULTIPLY", op(nt, "MULTIPLY", dens, dentro), raiz), vida)
# nucleo quente localizado: centro da lingua no terco de baixo; base vermelha
nucleo = op(nt, "MULTIPLY", op(nt, "SUBTRACT", 1.0, op(nt, "MINIMUM", op(nt, "MULTIPLY", dx, 7.0), 1.0)), op(nt, "SUBTRACT", 1.0, suave(nt, 0.15, 0.65, vnc)))
calor = op(nt, "MULTIPLY", dens, op(nt, "ADD", op(nt, "SUBTRACT", 0.82, op(nt, "MULTIPLY", vnc, 0.50)), op(nt, "MULTIPLY", nucleo, 0.32)))   # r2: menos amarelo
calor = op(nt, "MINIMUM", op(nt, "MULTIPLY", calor, forca), 1.0)
cor = no(nt, "ShaderNodeMix", data_type="RGBA"); nt.links.new(rampa(nt, calor, (C_BRASA, C_VERM, C_LAR, C_AMAR)), cor.inputs["A"])
nt.links.new(rampa(nt, calor, (V_ESC, V_MED, V_CLA, V_NUC)), cor.inputs["B"]); nt.links.new(violeta, cor.inputs["Factor"])
nt.links.new(cor.outputs["Result"], em.inputs["Color"])
nt.links.new(op(nt, "MULTIPLY", op(nt, "POWER", calor, 1.2), 5.5), em.inputs["Strength"])      # mais forte que a A3 (2,4), com teto pela rampa
nt.links.new(op(nt, "MINIMUM", op(nt, "MULTIPLY", dens, 1.4), 1.0), mx.inputs[0])
try: mc.surface_render_method = "BLENDED"
except Exception: pass
# ------------------------------------------------------------------ pontos na superficie
def malha_mundo(o):
    dg = bpy.context.evaluated_depsgraph_get(); me = o.evaluated_get(dg).to_mesh()
    tri = []
    nomes = {g.index: g.name for g in o.vertex_groups}
    for p in me.polygons:
        vs = [me.vertices[i] for i in p.vertices]
        f = sum(me.attributes["fogo"].data[i].value for i in p.vertices) / len(vs) if "fogo" in me.attributes else 0
        osso = None; melhor = 0
        for vv in vs:
            for g in vv.groups:
                nm = nomes.get(g.group)
                if nm in BD and g.weight > melhor: melhor, osso = g.weight, nm
        tri.append((o.matrix_world @ p.center, (o.matrix_world.to_3x3() @ p.normal).normalized(), p.area * (o.matrix_world.median_scale ** 2), f, osso))
    o.evaluated_get(dg).to_mesh_clear(); return tri
FACES = malha_mundo(CORPO) + malha_mundo(CAB)
CABS = {k: (BD["Cabeca" + k].head_local.copy(), (BD["Cabeca" + k].tail_local - BD["Cabeca" + k].head_local).normalized()) for k in "CED"}
def zona(osso):
    if osso is None: return None
    for chave, z in (("Pescoco", "juba"), ("Cabeca", "juba"), ("Escapula", "ombro"), ("Coluna3", "peito"), ("Coluna", "dorso"), ("Pelve", "quadril"),
                     ("Cauda", "cauda"), ("Braco", "perna"), ("Antebraco", "perna"), ("Coxa", "perna"), ("Canela", "perna")):
        if osso.startswith(chave): return z
    return None                                                # maos, pes, dedos, mandibulas: sem chama
ALT = {"juba": (4.2, 7.2), "ombro": (2.4, 3.8), "peito": (2.2, 3.6), "dorso": (2.0, 5.6), "quadril": (2.6, 4.0), "cauda": (3.2, 5.6), "perna": (1.4, 2.4)}   # r2: mais altas
LARG = {"juba": (1.9, 2.8), "ombro": (1.3, 1.9), "peito": (1.2, 1.8), "dorso": (1.5, 2.2), "quadril": (1.4, 2.0), "cauda": (1.3, 1.9), "perna": (0.8, 1.2)}
ALVO_N = {"juba": 46, "ombro": 8, "peito": 10, "dorso": 20, "quadril": 10, "cauda": 10, "perna": 16}
cand = {}
for (P, N, A, f, osso) in FACES:
    z = zona(osso)
    if z is None or f < 0.08: continue
    if osso.startswith("Cabeca"):                               # rosto limpo: so atras dos olhos
        hb, fw = CABS[osso[-1]]
        if (P - hb).dot(fw) > -0.9: continue
    mancha = 0.35 + 0.65 * max(0.0, min(1.0, 0.5 + 0.9 * noise.noise(P * 0.16)))          # areas de intensidade
    if z == "perna" and N.z < -0.2: continue
    peso = A * f * mancha
    if z == "dorso" and N.z > 0.80: peso *= 0.30                 # r4: menos chamas na crista (fileira de espinhos), mais nos lados
    cand.setdefault(z, []).append((peso, P, N, osso, mancha))
SITIOS = []
for z, lst in cand.items():
    tot = sum(c[0] for c in lst); escolhidos = []
    tent = 0
    while len(escolhidos) < ALVO_N[z] and tent < 6000:
        tent += 1; r = rnd.random() * tot; acc = 0
        for c in lst:
            acc += c[0]
            if acc >= r: break
        w, P, N, osso, mancha = c
        dmin = 0.9 if z == "perna" else (rnd.uniform(1.1, 2.0) if z == "dorso" else 1.15)   # r4: espacamento irregular no dorso
        if any((P - e[0]).length < dmin for e in escolhidos): continue
        escolhidos.append((P, N, osso, mancha))
    for P, N, osso, mancha in escolhidos: SITIOS.append((z, P, N, osso, mancha))
print("SITIOS", len(SITIOS), {z: sum(1 for s in SITIOS if s[0] == z) for z in ALT}, flush=True)
# ------------------------------------------------------------------ linguas
ALVO = bpy.data.objects.get("AlvoCamera") or bpy.data.objects.new("AlvoCamera", None)
if ALVO.name not in sc.objects: sc.collection.objects.link(ALVO)
LINGUAS = []
def plano(nome, larg, alt):
    mm = bpy.data.meshes.new(nome); bmc = bmesh.new(); uvl = bmc.loops.layers.uv.new()
    L = larg * 1.6
    vs = [bmc.verts.new((-L / 2, 0, 0)), bmc.verts.new((L / 2, 0, 0)), bmc.verts.new((L / 2, 0, alt * 1.3)), bmc.verts.new((-L / 2, 0, alt * 1.3))]
    f_ = bmc.faces.new(vs)
    for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    bmc.to_mesh(mm); bmc.free(); return mm
def driver_rot(o, r0, r1, traseira):
    for i in range(3):
        fc = o.driver_add("rotation_euler", i); d = fc.driver; d.type = "SCRIPTED"
        var = d.variables.new(); var.name = "k"; var.type = "SINGLE_PROP"
        var.targets[0].id_type = "SCENE"; var.targets[0].id = sc; var.targets[0].data_path = '["%s"]' % ("inclina_atraso" if traseira else "inclina")
        d.expression = "%.5f + (%.5f) * k" % (r0[i], r1[i] - r0[i])
def lingua(z, base, nrm, osso, alt, larg, fase, periodo, forca, filho):
    o = bpy.data.objects.new("ChamaA4_%03d" % len(LINGUAS), plano("ChamaA4", larg, alt)); sc.collection.objects.link(o); o.data.materials.append(mc)
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = osso
    def orient(up):
        zz = up.normalized(); y = V((0, -1, 0)); x = y.cross(zz).normalized(); y = zz.cross(x)
        return Matrix.Translation(base) @ Matrix((x, y, zz)).transposed().to_4x4()
    incl = (nrm * (0.45 if z != "juba" else 0.3) + V((0, 0.22, 1))).normalized()
    if z == "dorso": incl = (incl + V((rnd.uniform(-0.35, 0.35), rnd.uniform(-0.2, 0.25), 0))).normalized()   # r4: cada uma pende para um lado
    o.matrix_world = orient((incl + V((0, 1.25, -0.1))).normalized()); bpy.context.view_layer.update(); r1 = tuple(o.rotation_euler)   # correndo: para tras
    o.matrix_world = orient(incl); bpy.context.view_layer.update(); r0 = tuple(o.rotation_euler)
    driver_rot(o, r0, r1, base.y > 1.0)                        # metade traseira responde com atraso
    o["fase"], o["periodo"], o["forca"], o["semente"] = fase, periodo, forca, rnd.random()
    c = o.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"; c.lock_axis = "LOCK_Z"
    LINGUAS.append({"nome": o.name, "zona": z, "osso": osso, "base": [round(x_, 3) for x_ in base], "altura": round(alt, 2), "largura": round(larg, 2),
                    "periodo_s": round(periodo, 2), "filho": filho})
for (z, P, N, osso, mancha) in SITIOS:
    a0, a1 = ALT[z]; l0, l1 = LARG[z]
    alt = rnd.uniform(a0, a1) * (0.8 + 0.4 * mancha); larg = rnd.uniform(l0, l1)
    if z == "dorso": alt *= rnd.choice((0.6, 0.85, 1.0, 1.25)); larg *= rnd.uniform(0.85, 1.3)   # r4: alturas bem diferentes
    per = rnd.uniform(0.75, 1.35); fs = rnd.random(); fz = 0.75 + 0.55 * mancha
    base = P - N * 0.30
    lingua(z, base, N, osso, alt, larg, fs, per, fz, False)
    lado = N.cross(V((0, 0, 1)))
    lado = lado.normalized() if lado.length > 1e-4 else V((1, 0, 0))
    lingua(z, base + lado * larg * 0.30 * rnd.choice((-1, 1)), N, osso, alt * 0.72, larg * 0.75, (fs + 0.38 + rnd.uniform(-0.08, 0.08)) % 1.0, per * rnd.uniform(0.9, 1.1), fz * 0.85, True)   # divisao
print("LINGUAS", len(LINGUAS), flush=True)
# ------------------------------------------------------------------ luz local do fogo
LUZES = []
for nome, osso, desl, en in (("Luz_JubaC", "PescocoC2", (0, 0, 2.2), 900), ("Luz_JubaE", "PescocoE2", (0, 0, 2.0), 700), ("Luz_JubaD", "PescocoD2", (0, 0, 2.0), 700),
                             ("Luz_Peito", "Coluna3", (0, -2.5, -1.0), 500), ("Luz_Dorso1", "Coluna2", (0, 0, 2.6), 650), ("Luz_Dorso2", "Coluna1", (0, 0, 2.4), 600),
                             ("Luz_Quadril", "Pelve", (0, 0.5, 2.2), 500), ("Luz_Cauda", "Cauda3", (0, 0, 1.2), 450), ("Luz_Ombro", "EscapulaE", (-1.2, 0, 1.0), 350)):
    ld = bpy.data.lights.new(nome, "POINT"); ld.shadow_soft_size = 1.2; ld.color = (1.0, 0.42, 0.12); ld.use_shadow = False
    lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo)
    b = BD[osso]; lo.parent = rig; lo.parent_type = "BONE"; lo.parent_bone = osso
    lo.matrix_world = Matrix.Translation(b.head_local + V(desl)); s_ = rnd.uniform(0, 30)
    fc = ld.driver_add("energy"); d = fc.driver; d.type = "SCRIPTED"; d.expression = "%d*(0.82+0.11*sin(frame*0.71+%.2f)+0.07*sin(frame*1.93+%.2f))" % (en, s_, s_ * 2)
    for i, (c0, c1) in enumerate(((1.0, 0.55), (0.42, 0.25), (0.12, 1.0))):     # laranja -> violeta (Furia)
        fc = ld.driver_add("color", i); d = fc.driver; d.type = "SCRIPTED"
        var = d.variables.new(); var.name = "vi"; var.type = "SINGLE_PROP"; var.targets[0].id_type = "SCENE"; var.targets[0].id = sc; var.targets[0].data_path = '["violeta"]'
        d.expression = "%.3f + (%.3f) * vi" % (c0, c1 - c0)
    LUZES.append({"nome": nome, "osso": osso, "watts_blender": en})
rig.data.pose_position = "POSE"
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Fogo_A4.blend"))
nz_ = {z: sum(1 for s in SITIOS if s[0] == z) for z in ALT}
rob_pc = len(SITIOS); rob_cel = math.ceil(len(SITIOS) / 2)
json.dump({"versao": "A4", "sitios": len(SITIOS), "linguas": len(LINGUAS), "por_zona": nz_, "linguas_detalhe": LINGUAS, "luzes": LUZES,
           "pele": "pintura da A3 x0,08 (so brasa fraca); pelo escuro visivel; integracao por luz local",
           "estimativa_roblox_A_TESTAR": {
               "pc": {"emissores": rob_pc, "taxa_por_emissor": 3, "vida_s": 0.9, "particulas_vivas": round(rob_pc * 3 * 0.9),
                      "luzes": "1 PointLight por criatura (nao 9): limite de luzes do Roblox; a cintilacao vai no Brightness"},
               "celular": {"emissores": rob_cel, "taxa_por_emissor": 2, "vida_s": 0.8, "particulas_vivas": round(rob_cel * 2 * 0.8), "luzes": "nenhuma (so emissao)"},
               "observacao": "a lingua 'filha' do Blender vira a variacao de tamanho/rotacao da mesma particula no Roblox; medir no Roblox"}},
          open(os.path.join(OUT, "aura_A4.json"), "w"), indent=1, ensure_ascii=False)
print("FOGO_A4_OK", len(SITIOS), len(LINGUAS), flush=True)

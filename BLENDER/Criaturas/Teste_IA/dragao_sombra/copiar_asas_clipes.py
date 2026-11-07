"""Troca SO as curvas dos ossos das asas (wing_* e shoulder_*, o conjunto ASA do gerador) dos clipes deste .blend pelas de
outro .blend do mesmo esqueleto, regerado com outra pose de asa (06/11, usuario: "nao quero a asa do dragao dobrada em
nenhuma animacao"). O resto do corpo fica como esta: as correcoes de cauda/cabeca/frenagem/laco ja aprovadas nao se perdem.
So entram as acoes que existem nos dois arquivos e tem o mesmo intervalo de quadros.
Uso: blender -b <alvo.blend> -P copiar_asas_clipes.py -- <regerado.blend> <saida.blend> [nomes,separados]"""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]; FONTE, SAIDA = a[0], a[1]
SO = set(a[2].split(",")) if len(a) > 2 else None
def eh_asa(path):
    return path.startswith('pose.bones["wing_') or path.startswith('pose.bones["shoulder_')
def curvas(act):
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, act.slots[0]) if act.slots else None
        if cb is not None: return cb.fcurves, cb
    except Exception: pass
    return act.fcurves, None
alvos = {x.name: x for x in bpy.data.actions if x.name.startswith("Silverwing_")}
with bpy.data.libraries.load(FONTE) as (src, dst):
    dst.actions = [n for n in src.actions if "." not in n and (n in alvos or "_Rampa_" in n) and (SO is None or n.replace("Silverwing_", "") in SO)]
trocadas, puladas = [], []
for novo in list(dst.actions):
    if novo is None: continue
    nome = novo.name.split(".")[0] if novo.name not in alvos else novo.name
    velho = alvos.get(nome)
    if not velho:                                                  # clipe novo (ex.: *_Rampa_*): entra inteiro
        if "_Rampa_" in nome: novo.name = nome; novo.use_fake_user = True; trocadas.append((nome, "novo"))
        continue
    if tuple(map(round, velho.frame_range)) != tuple(map(round, novo.frame_range)): puladas.append((nome, "intervalo")); bpy.data.actions.remove(novo); continue
    fv, cbv = curvas(velho); fn, _ = curvas(novo)
    for fc in [c for c in fv if eh_asa(c.data_path)]: fv.remove(fc)
    n = 0
    for c in fn:
        if not eh_asa(c.data_path): continue
        d = fv.new(c.data_path, index=c.array_index, group_name=c.group.name if c.group else "")
        d.keyframe_points.add(len(c.keyframe_points))
        for k, kp in enumerate(c.keyframe_points):
            d.keyframe_points[k].co = kp.co; d.keyframe_points[k].interpolation = kp.interpolation
            d.keyframe_points[k].handle_left = kp.handle_left; d.keyframe_points[k].handle_right = kp.handle_right
        d.update(); n += 1
    trocadas.append((nome, n)); bpy.data.actions.remove(novo)
for x in bpy.data.actions: x.use_fake_user = True
print("ASAS trocadas", len(trocadas), "acoes;", "curvas por acao", sorted({str(n) for _, n in trocadas}))
print("ASAS puladas", puladas)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA); print("COPIAR_ASAS_OK", SAIDA)

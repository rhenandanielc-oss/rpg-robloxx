"""v29: confere que as acoes preservadas sao IDENTICAS entre dois blends (todas as curvas, todos os quadros inteiros e meios quadros).
Uso: blender -b <blend_novo> -P comparar_acoes_v29.py -- <blend_base> <saida_json> <acoes separadas por virgula>"""
import bpy, sys, json
import os
a = sys.argv[sys.argv.index("--") + 1:]; BASE, OUTJ, ACS = os.path.abspath(a[0]), a[1], a[2].split(",")
with bpy.data.libraries.load(BASE, link=False) as (src, dst): dst.actions = [n + "" for n in src.actions if n in ACS]
REL = {}
for nome in ACS:
    novo = next(x for x in bpy.data.actions if x.name == nome and x.library is None and not x.name.endswith(".001"))
    base = bpy.data.actions.get(nome + ".001")
    def curvas(ac):
        cb = ac.layers[0].strips[0].channelbag(ac.slots[0]); return {(c.data_path, c.array_index): c for c in cb.fcurves}
    cn, cbs = curvas(novo), curvas(base); f0, f1 = novo.frame_range; mx = 0.0; mi = 0.0; mi_ult = 0.0
    assert set(cn) == set(cbs), nome
    for kk, c in cn.items():
        for i in range(int(f0) * 2, int(f1) * 2 + 1):
            d_ = abs(c.evaluate(i / 2) - cbs[kk].evaluate(i / 2)); mx = max(mx, d_)
            if i % 2 == 0: mi = max(mi, d_)
            if i >= int(f1) * 2 - 2: mi_ult = max(mi_ult, d_)
    REL[nome] = {"curvas": len(cn), "quadros": [f0, f1], "quadros_base": list(base.frame_range), "dif_max": mx, "dif_max_quadros_inteiros": mi, "dif_max_ultimo_quadro": mi_ult}
    print("CMP", nome, REL[nome], flush=True)
json.dump(REL, open(OUTJ, "w"), indent=1); print("COMPARAR_ACOES_V29_OK", flush=True)

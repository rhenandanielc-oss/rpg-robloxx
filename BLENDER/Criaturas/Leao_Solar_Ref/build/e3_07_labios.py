"""E3: escurece no albedo a margem dos labios e a pele das comissuras (atributo de face "labio" gravado pelo e3_05),
como a borda escura da boca da referencia. Uso:
  blender -b <e3.blend> -P e3_07_labios.py -- exportar <saida.npz>
  python e3_07_labios.py aplicar <textura.png> <labios.npz> <saida.png>"""
import sys
if "--" in sys.argv:
    import bpy, numpy as np
    A = sys.argv[sys.argv.index("--") + 1:]
    me = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0].data; uv = me.uv_layers.active.data
    at = me.attributes["labio"].data; tri, val = [], []
    for p in me.polygons:
        x = at[p.index].value
        if x <= 0: continue
        l = list(p.loop_indices)
        for i in range(1, len(l) - 1): tri.append([uv[l[0]].uv[:], uv[l[i]].uv[:], uv[l[i + 1]].uv[:]]); val.append(x)
    np.savez_compressed(A[1], tri=np.array(tri, np.float32), valor=np.array(val, np.float32)); print("LABIOS_EXPORT", len(tri))
else:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    tex, dados, out = sys.argv[2:5]
    im = np.asarray(Image.open(tex).convert("RGB")).astype(np.float32) / 255; H, W = im.shape[:2]
    d = np.load(dados); m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
    for t, x in zip(d["tri"], d["valor"]): dr.polygon([(u * W, (1 - v) * H) for u, v in t], fill=int(255 * x))
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)[..., None] / 255
    escuro = np.array([0.20, 0.13, 0.11], np.float32) * (0.8 + 0.4 * im.mean(-1, keepdims=True))
    Image.fromarray((np.clip(im * (1 - 0.85 * m) + escuro * 0.85 * m, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out); print("LABIOS_OK", out)

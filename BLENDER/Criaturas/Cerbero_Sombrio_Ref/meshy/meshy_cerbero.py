"""Meshy API para o Cerbero Sombrio (creditos do usuario; cada etapa so roda com OK explicito dele).
Adaptado de Coruja_da_Floresta_Ref/meshy/meshy_coruja.py. Pedido: DOCS/pedidos/2026-11-17-cerbero-sombrio-meshy.md.
  etapa saldo:  le o saldo de creditos (nao gasta).
  etapa imagem: Image to Image (nano-banana-2, ~6 cr) a partir da referencia -> mesmo cerbero em pose neutra de RIG,
                bocas fechadas, fundo neutro, multi-vista. Salva em <saida>/imagem/.
  etapa 3d:     Multi-Image to 3D (meshy-7.1, textura 4K + PBR, ~30 cr) a partir das vistas escolhidas.
A chave vem SO da variavel de ambiente de usuario MESHY_API_KEY (HKCU\\Environment); nunca e impressa nem gravada.
Uso: python -I meshy_cerbero.py saldo
     python -I meshy_cerbero.py imagem <ref.png> <saida_dir>
     python -I meshy_cerbero.py 3d <saida_dir> <img1.png> [img2.png ...]"""
import base64, json, os, sys, time, urllib.request, winreg
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k: CHAVE = winreg.QueryValueEx(k, "MESHY_API_KEY")[0]
BASE = "https://api.meshy.ai/openapi/v1/"
def req(url, corpo=None):
    r = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, method="POST" if corpo else "GET",
                               headers={"Authorization": "Bearer " + CHAVE, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=180) as h: return json.loads(h.read())
def data_uri(caminho):
    mime = "image/png" if caminho.lower().endswith(".png") else "image/jpeg"
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(caminho, "rb").read()).decode())
def esperar(rota, tid):
    while True:
        t = req(BASE + rota + "/" + tid)
        print(rota, t["status"], t.get("progress"), flush=True)
        if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
            print("creditos:", t.get("consumed_credits"), t.get("task_error") or "", flush=True); return t
        time.sleep(10)
PROMPT_IMG = ("Recreate exactly this same dark fantasy cerberus from the reference image: one heavy muscular canine body, "
              "exactly four digitigrade legs with large clawed paws, one tapered bushy tail, exactly three broad canine heads on "
              "three short readable necks rooted in one massive shoulder girdle, the center head higher and the two side heads "
              "lower and angled slightly outward. Broad angular skulls, compact canine muzzles, dark red eyes, ALL THREE MOUTHS "
              "CLOSED with clear jaw seams. Short charcoal-black fur in broad sculpted clumps, a few fitted corrupted stone plates "
              "on the shoulders and along the spine, restrained thin crimson fissures painted on the plates. Keep a small clear "
              "gap between the three necks and between the legs; keep the back behind the necks smooth and low for a future "
              "saddle. Show the FULL BODY standing still on flat ground in a neutral RIGGING pose: all four legs straight and "
              "planted, symmetric, tail relaxed straight back, the three heads looking forward-outward as in the reference, calm "
              "expression. Plain flat light-gray studio background, soft even neutral lighting, no ground, no smoke, no flames, "
              "no saddle, no props, no cropping, the whole creature visible including tail tip and all paws, realistic fantasy "
              "style, game creature concept sheet.")
etapa = sys.argv[1]
if etapa == "saldo":
    print("saldo:", req(BASE + "balance").get("balance"))
elif etapa == "imagem":
    ref, out = sys.argv[2], os.path.join(sys.argv[3], "imagem"); os.makedirs(out, exist_ok=True)
    tid = req(BASE + "image-to-image", {"ai_model": "nano-banana-2", "prompt": PROMPT_IMG, "reference_image_urls": [data_uri(ref)],
                                        "generate_multi_view": True})["result"]
    print("tarefa", tid, flush=True)
    t = esperar("image-to-image", tid)
    for i, u in enumerate(t.get("image_urls") or []):
        urllib.request.urlretrieve(u, os.path.join(out, "cerbero_neutro_%d.png" % i)); print("salvo", i)
    json.dump({"tarefa": tid, "prompt": PROMPT_IMG, "creditos": t.get("consumed_credits"), "status": t["status"]},
              open(os.path.join(out, "tarefa.json"), "w"), indent=1)
elif etapa == "3d":
    out = os.path.join(sys.argv[2], "modelo"); os.makedirs(out, exist_ok=True); imgs = sys.argv[3:]
    corpo = {"image_urls": [data_uri(p) for p in imgs], "ai_model": "meshy-7.1", "should_texture": True, "enable_pbr": True,
             "texture_resolution": "4k", "should_remesh": False, "target_formats": ["glb", "fbx"], "image_enhancement": True}
    tid = req(BASE + "multi-image-to-3d", corpo)["result"]; print("tarefa", tid, flush=True)
    t = esperar("multi-image-to-3d", tid)
    if t["status"] == "SUCCEEDED":
        for fmt, u in t["model_urls"].items():
            if u: urllib.request.urlretrieve(u, os.path.join(out, "CR_Cerbero_meshy." + fmt.replace("pre_remeshed_glb", "pre.glb")))
        for nome, u in (t.get("texture_urls") or [{}])[0].items():
            if u: urllib.request.urlretrieve(u, os.path.join(out, "T_meshy_%s.png" % nome))
        for nome, u in (t.get("thumbnail_urls") or {}).items():
            if u: urllib.request.urlretrieve(u, os.path.join(out, "thumb_%s.png" % nome))
    json.dump({"tarefa": tid, "imagens": imgs, "creditos": t.get("consumed_credits"), "status": t["status"]},
              open(os.path.join(out, "tarefa.json"), "w"), indent=1)

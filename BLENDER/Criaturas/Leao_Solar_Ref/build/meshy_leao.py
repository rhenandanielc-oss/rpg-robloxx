"""Meshy (API paga do usuario) para o Leao Solar: saldo e Multi-Image to 3D com as 3 vistas da referencia principal.
A chave vem SO da variavel de ambiente de usuario MESHY_API_KEY (registro HKCU\\Environment); nunca e impressa.
Uso: python meshy_leao.py saldo
     python meshy_leao.py gerar <saida_dir> <img1.png> [img2.png ...]   (1-4 imagens; GASTA CREDITOS)"""
import base64, json, os, sys, time, urllib.request, winreg
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k: CHAVE = winreg.QueryValueEx(k, "MESHY_API_KEY")[0]
BASE = "https://api.meshy.ai/openapi/v1/"
def req(url, corpo=None):
    r = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, method="POST" if corpo else "GET",
                               headers={"Authorization": "Bearer " + CHAVE, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=180) as h: return json.loads(h.read())
def data_uri(caminho): return "data:image/png;base64," + base64.b64encode(open(caminho, "rb").read()).decode()
if sys.argv[1] == "saldo":
    print("SALDO", req(BASE + "balance")); sys.exit()
OUT = sys.argv[2]; IMGS = sys.argv[3:]; os.makedirs(OUT, exist_ok=True)
TEXTURA = ("Realistic adult male lion, natural anatomy. Short golden ochre body fur with lighter cream belly, muzzle and chin. "
           "Huge voluminous mane of long curved tapering locks in deep layers: bright golden yellow on top and at the tips, "
           "vivid orange in the middle layers, copper and reddish orange in the deep and lower layers. Amber eyes, dark "
           "triangular nose. Long tail with a large orange tuft. No fire, no glow, no baked lighting.")
corpo = {"image_urls": [data_uri(p) for p in IMGS], "ai_model": "latest", "topology": "triangle", "target_polycount": 200000,
         "should_remesh": True, "symmetry_mode": "on", "should_texture": True, "enable_pbr": True,
         "texture_prompt": TEXTURA}
tid = req(BASE + "multi-image-to-3d", corpo)["result"]; print("criada", tid, flush=True)
while True:
    time.sleep(15)
    t = req(BASE + "multi-image-to-3d/" + tid)
    print(t["status"], t.get("progress"), flush=True)
    if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"): break
json.dump({k: t.get(k) for k in ("id", "status", "consumed_credits", "created_at", "finished_at", "task_error")},
          open(os.path.join(OUT, "tarefa.json"), "w"), indent=1)
print("FIM", t["status"], "creditos:", t.get("consumed_credits"), t.get("task_error") or "")
if t["status"] == "SUCCEEDED":
    for fmt, url in (t.get("model_urls") or {}).items():
        if url and fmt in ("glb", "fbx"): urllib.request.urlretrieve(url, os.path.join(OUT, "Leao_Solar_meshy." + fmt))
    for i, tex in enumerate(t.get("texture_urls") or []):
        for nome, url in tex.items():
            if url: urllib.request.urlretrieve(url, os.path.join(OUT, "tex%d_%s.png" % (i, nome)))
    if t.get("thumbnail_url"): urllib.request.urlretrieve(t["thumbnail_url"], os.path.join(OUT, "miniatura.png"))

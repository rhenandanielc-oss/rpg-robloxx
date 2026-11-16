"""Image to 3D do Meshy a partir da referencia do Lobo Artico (1 tarefa; meshy-7.1, PBR 4K = 30 creditos).
A chave vem SO da variavel de ambiente de usuario MESHY_API_KEY (registro HKCU\\Environment); nunca e impressa.
Entrada: recorte da referencia so no lobo (ref/lobo-artico-recorte.png, gerado por este script).
Uso: python meshy_lobo_img3d.py <saida_dir> [saldo]"""
import base64, json, os, sys, time, urllib.request, winreg
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(sys.argv[1])
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k: CHAVE = winreg.QueryValueEx(k, "MESHY_API_KEY")[0]
BASE = "https://api.meshy.ai/openapi/v1"
def req(url, corpo=None):
    r = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, method="POST" if corpo else "GET",
                               headers={"Authorization": "Bearer " + CHAVE, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=180) as h: return json.loads(h.read())
print("saldo_antes", req(BASE + "/balance").get("balance"), flush=True)
if len(sys.argv) > 2 and sys.argv[2] == "saldo": sys.exit(0)
REC = os.path.join(AQUI, "ref", "lobo-artico-recorte.png")
Image.open(os.path.join(AQUI, "ref", "lobo-artico-referencia.png")).convert("RGB").crop((170, 0, 1520, 941)).save(REC)
img = "data:image/png;base64," + base64.b64encode(open(REC, "rb").read()).decode()
corpo = {"image_url": img, "ai_model": "meshy-7.1", "should_remesh": False, "should_texture": True, "enable_pbr": True,
         "texture_resolution": "4k", "texture_image_url": img, "image_enhancement": True, "target_formats": ["glb", "fbx"],
         "multi_view_thumbnails": True}
tid = req(BASE + "/image-to-3d", corpo)["result"]; print("criada", tid, flush=True)
os.makedirs(OUT, exist_ok=True)
while True:
    time.sleep(15)
    t = req(BASE + "/image-to-3d/" + tid)
    if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"): break
    print(t["status"], t.get("progress"), flush=True)
print(t["status"], "creditos:", t.get("consumed_credits"), t.get("task_error") or "", flush=True)
if t["status"] == "SUCCEEDED":
    for fmt, url in t["model_urls"].items():
        if url and fmt in ("glb", "fbx"): urllib.request.urlretrieve(url, os.path.join(OUT, "CR_LoboArtico_meshy." + fmt))
    for nome, url in (t.get("texture_urls") or [{}])[0].items():
        if url: urllib.request.urlretrieve(url, os.path.join(OUT, "tex_%s.png" % nome))
    for nome, url in (t.get("thumbnail_urls") or {}).items():
        if url: urllib.request.urlretrieve(url, os.path.join(OUT, "vista_%s.png" % nome))
    if t.get("thumbnail_url"): urllib.request.urlretrieve(t["thumbnail_url"], os.path.join(OUT, "miniatura.png"))
    json.dump({k: t.get(k) for k in ("id", "status", "consumed_credits", "created_at", "finished_at")},
              open(os.path.join(OUT, "tarefa.json"), "w"))
print("saldo_depois", req(BASE + "/balance").get("balance"), flush=True)
print("MESHY_FIM")

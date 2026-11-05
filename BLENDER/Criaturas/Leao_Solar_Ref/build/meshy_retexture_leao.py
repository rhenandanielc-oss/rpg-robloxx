"""Meshy Retexture da malha E2 (tarefa Multi-Image anterior), mantendo a UV original, com a referencia principal como
estilo por imagem. GASTA CREDITOS. A chave vem SO da variavel de ambiente de usuario MESHY_API_KEY; nunca e impressa.
Uso: python meshy_retexture_leao.py <task_id_origem> <ref.png> <saida_dir>"""
import base64, json, os, sys, time, urllib.request, urllib.error, winreg
TID, REF, OUT = sys.argv[1:4]; os.makedirs(OUT, exist_ok=True)
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k: CHAVE = winreg.QueryValueEx(k, "MESHY_API_KEY")[0]
API = "https://api.meshy.ai/openapi/v1/retexture"
def req(url, corpo=None):
    r = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, method="POST" if corpo else "GET",
                               headers={"Authorization": "Bearer " + CHAVE, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=180) as h: return json.loads(h.read())
    except urllib.error.HTTPError as e: print("HTTP", e.code, e.read()[:400]); raise
corpo = {"input_task_id": TID, "image_style_url": "data:image/png;base64," + base64.b64encode(open(REF, "rb").read()).decode(),
         "enable_original_uv": True, "enable_pbr": True, "ai_model": "meshy-6", "remove_lighting": True, "target_formats": ["glb"]}
tid = req(API, corpo)["result"]; print("criada", tid, flush=True)
while True:
    time.sleep(15); t = req(API + "/" + tid); print(t["status"], t.get("progress"), flush=True)
    if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"): break
json.dump({k: t.get(k) for k in ("id", "status", "consumed_credits", "created_at", "finished_at", "task_error")},
          open(os.path.join(OUT, "tarefa.json"), "w"), indent=1)
print("FIM", t["status"], "creditos:", t.get("consumed_credits"), t.get("task_error") or "")
if t["status"] == "SUCCEEDED":
    if (t.get("model_urls") or {}).get("glb"): urllib.request.urlretrieve(t["model_urls"]["glb"], os.path.join(OUT, "Leao_Solar_retexture.glb"))
    for i, tex in enumerate(t.get("texture_urls") or []):
        for nome, url in tex.items():
            if url: urllib.request.urlretrieve(url, os.path.join(OUT, "tex%d_%s.png" % (i, nome)))
    if t.get("thumbnail_url"): urllib.request.urlretrieve(t["thumbnail_url"], os.path.join(OUT, "miniatura.png"))

"""Image to 3D do Meshy a partir da referencia do Lobo Ancestral (base HIGH para a malha de jogo).
A chave vem SO da variavel de ambiente de usuario MESHY_API_KEY (registro HKCU\\Environment); nunca e impressa.
Uso: python -I meshy_img3d.py saldo                       -> so consulta o saldo (nao gasta credito)
     python -I meshy_img3d.py gerar <imagem> <saida_dir>   -> cria a tarefa (meshy-7.1, geometria 2k, textura 4k PBR: 35 creditos)
     python -I meshy_img3d.py baixar <task_id> <saida_dir> -> acompanha/baixa uma tarefa ja criada"""
import base64, json, os, sys, time, urllib.request, winreg
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k: CHAVE = winreg.QueryValueEx(k, "MESHY_API_KEY")[0]
BASE = "https://api.meshy.ai/openapi"
def req(url, corpo=None):
    r = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, method="POST" if corpo else "GET",
                               headers={"Authorization": "Bearer " + CHAVE, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=180) as h: return json.loads(h.read())

def baixar(tid, out):
    os.makedirs(out, exist_ok=True)
    while True:
        t = req(BASE + "/v1/image-to-3d/" + tid)
        print(t["status"], t.get("progress"), flush=True)
        if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"): break
        time.sleep(20)
    print("creditos:", t.get("consumed_credits"), t.get("task_error") or "", flush=True)
    if t["status"] == "SUCCEEDED":
        urllib.request.urlretrieve(t["model_urls"]["glb"], os.path.join(out, "lobo_meshy.glb"))
        for nome, url in (t.get("texture_urls") or [{}])[0].items():
            if url: urllib.request.urlretrieve(url, os.path.join(out, "tex_%s.png" % nome))
        for lado, url in (t.get("thumbnail_urls") or {}).items():
            if url: urllib.request.urlretrieve(url, os.path.join(out, "miniatura_%s.png" % lado))
    json.dump({k: t.get(k) for k in ("id", "status", "consumed_credits", "created_at", "finished_at", "task_error")},
              open(os.path.join(out, "tarefa.json"), "w"), indent=1)
    print("MESHY_FIM")

modo = sys.argv[1]
if modo == "saldo":
    print("saldo:", req(BASE + "/v1/balance").get("balance"))
elif modo == "gerar":
    img, out = sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
    uri = "data:image/png;base64," + base64.b64encode(open(img, "rb").read()).decode()
    corpo = {"image_url": uri, "ai_model": "meshy-7.1", "geometry_resolution": "2k", "should_texture": True,
             "enable_pbr": True, "texture_resolution": "4k", "should_remesh": False, "image_enhancement": True,
             "target_formats": ["glb"], "multi_view_thumbnails": True}
    tid = req(BASE + "/v1/image-to-3d", corpo)["result"]
    open(os.path.join(out, "task_id.txt"), "w").write(tid); print("criada", tid, flush=True)
    baixar(tid, out)
elif modo == "baixar":
    baixar(sys.argv[2], sys.argv[3])

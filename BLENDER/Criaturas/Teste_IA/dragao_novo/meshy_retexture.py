"""AI Texturing (Retexture) do Meshy na malha de jogo do CR_Dragao, mantendo a UV original (as texturas servem na
malha que vai receber o rig). Duas variantes: estilo por IMAGEM (referencia) e por TEXTO. 10 creditos cada (4K, PBR).
A chave vem SO da variavel de ambiente de usuario MESHY_API_KEY (registro HKCU\\Environment); nunca e impressa.
Uso: python -I meshy_retexture.py <low.glb> <ref.png> <saida_dir> [imagem,texto]"""
import base64, json, os, sys, time, urllib.request, winreg
LOW, REF, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
VARS = (sys.argv[4] if len(sys.argv) > 4 else "imagem,texto").split(",")
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k: CHAVE = winreg.QueryValueEx(k, "MESHY_API_KEY")[0]
API = "https://api.meshy.ai/openapi/v1/retexture"
def req(url, corpo=None):
    r = urllib.request.Request(url, data=json.dumps(corpo).encode() if corpo else None, method="POST" if corpo else "GET",
                               headers={"Authorization": "Bearer " + CHAVE, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as h: return json.loads(h.read())
def data_uri(caminho, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(caminho, "rb").read()).decode())
TEXTO = ("Realistic fantasy red dragon, high detail game texture. Overlapping red-orange scales with darker gaps and "
         "lighter raised edges; larger plate-like scales on back, shoulders, forearms and thighs, smaller scales on head and neck. "
         "Cream ivory segmented belly plates from throat to the underside of the tail tip. Ivory horns with darker base and "
         "ring ridges, ivory claws. Red spikes along the spine. Wing membranes translucent orange-red with subtle darker veins, "
         "wing finger bones lighter peach. Amber eyes. No baked lighting.")
base = {"model_url": data_uri(LOW, "application/octet-stream"), "enable_original_uv": True, "enable_pbr": True,
        "texture_resolution": "4k", "ai_model": "meshy-6", "remove_lighting": True, "target_formats": ["glb"]}
tarefas = {}
for v in VARS:
    corpo = dict(base)
    if v == "imagem": corpo["image_style_url"] = data_uri(REF, "image/png")
    else: corpo["text_style_prompt"] = TEXTO
    tarefas[v] = req(API, corpo)["result"]; print("criada", v, tarefas[v], flush=True)
pend = dict(tarefas)
while pend:
    time.sleep(15)
    for v, tid in list(pend.items()):
        t = req(API + "/" + tid)
        if t["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
            print(v, t["status"], "creditos:", t.get("consumed_credits"), t.get("task_error") or "", flush=True)
            if t["status"] == "SUCCEEDED":
                d = os.path.join(OUT, v); os.makedirs(d, exist_ok=True)
                urllib.request.urlretrieve(t["model_urls"]["glb"], os.path.join(d, "CR_Dragao_meshy_%s.glb" % v))
                for nome, url in (t.get("texture_urls") or [{}])[0].items():
                    if url: urllib.request.urlretrieve(url, os.path.join(d, "%s.png" % nome))
                if t.get("thumbnail_url"): urllib.request.urlretrieve(t["thumbnail_url"], os.path.join(d, "miniatura.png"))
                json.dump({k: t[k] for k in ("id", "status", "consumed_credits", "created_at", "finished_at")},
                          open(os.path.join(d, "tarefa.json"), "w"))
            del pend[v]
        else:
            print(v, t["status"], t.get("progress"), flush=True)
print("MESHY_FIM")

"""Empacota os clipes JSON APROVADOS da fauna da Floresta Ancestral (Cervo, Javali, Coruja) em StringValues para o Studio,
sem HTTP e sem publicar animacoes (mesmo formato/codificador do Lobo Ancestral: Lobo_Ancestral_Ref/studio/empacotar_lobo.py).
Grava studio/dados/<Animal>/<Clipe>.txt + studio/fauna_dados.project.json + studio/inventario.json; depois
  rojo build studio/fauna_dados.project.json -o studio/FaunaFloresta.rbxm   (o usuario faz Insert from File)
Formato: linha 1 nome|fps|loop|quadros|ossos ; #M|marcadores ; #V|velocidade|rotacao_raiz|fonte ; Osso|canal|S<v> ou E<deltas>.
Canais 1..7 = qx qy qz qw tx ty tz (pose local do osso no Blender). Uso: python studio/empacotar_fauna.py"""
import json, os, glob, hashlib
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
PADRAO = [0, 0, 0, 1, 0, 0, 0]
def enc(vals):
    out = []; prev = 0
    for v in vals:
        q = round(v * 10000); d = q - prev; prev = q; z = (-d * 2 - 1) if d < 0 else d * 2
        while True:
            c = z & 31; z >>= 5
            if z: out.append(A[c | 32])
            else: out.append(A[c]); break
    return "".join(out)
# bases APROVADAS (ver LEIA-ME de cada animal); a ordem importa: lote posterior substitui o mesmo nome
FONTES = {
    "Cervo": ["Cervo_do_Bosque_Ref/rig/clipes_r2"],                                   # 31 clipes, rig r2 (todos os lotes)
    "Javali": ["Javali_Silvestre_Ref/rig/clipes_LA", "Javali_Silvestre_Ref/rig/clipes_LB",
               "Javali_Silvestre_Ref/rig/clipes_LC", "Javali_Silvestre_Ref/rig/clipes_LD_r2",
               "Javali_Silvestre_Ref/rig/clipes_LE", "Javali_Silvestre_Ref/rig/clipes_LF"],   # 24 + Chifrada (LE) + Beber (LF, 17/11), rig r4
    "Coruja": ["Coruja_da_Floresta_Ref/rig/clipes_LA_r2", "Coruja_da_Floresta_Ref/rig/clipes_LB",
               "Coruja_da_Floresta_Ref/rig/clipes_LC_r2", "Coruja_da_Floresta_Ref/rig/clipes_LD",
               "Coruja_da_Floresta_Ref/rig/clipes_LE"],  # 32 clipes + Beber (lote E, 17/11), rig r4
}
# lotes de onde so entram alguns clipes (o lote E regrava a Corrida so para o render de revisao)
SO = {("Javali", "clipes_LE"): ("Chifrada",)}   # por (animal, pasta): a coruja tambem tem um clipes_LE
# clipes PARCIAIS: so estes ossos vao para o Studio (o adaptador poe peso 0 nos demais) -> tocam por cima de outro clipe
PARCIAIS = {("Javali", "Chifrada"): ("Pescoco", "Pescoco2", "Cabeca", "OrelhaE", "OrelhaD")}
if __name__ == "__main__":
    inv = {}; arvore = {"$className": "Folder", "AdaptadorFauna": {"$path": "AdaptadorFauna.luau"}}
    for animal, pastas in FONTES.items():
        clipes = {}
        for p in pastas:
            for f in sorted(glob.glob(os.path.join(RAIZ, p, "json", animal + "_*.json"))):
                nm_ = os.path.basename(f)[len(animal) + 1:-5]
                if (animal, os.path.basename(p)) in SO and nm_ not in SO[(animal, os.path.basename(p))]: continue
                clipes[nm_] = (f, os.path.basename(p))
        os.makedirs(os.path.join(AQUI, "dados", animal), exist_ok=True)
        dados = {"$className": "Folder"}; inv[animal] = {}
        for nome, (f, lote) in sorted(clipes.items()):
            d = json.load(open(f, encoding="utf-8")); n = d["quadros"]; ossos = [o for o in d["ossos"] if o in PARCIAIS.get((animal, nome), d["ossos"])]
            mk = ",".join("%s=%.4f" % (m["nome"], m["t"]) for m in d.get("marcadores", []))
            L = ["%s|%d|%d|%d|%s" % (nome, d["fps"], 1 if d["loop"] else 0, n, ",".join(ossos)), "#M|" + mk,
                 "#V|%.4f|%.2f|%s" % (d.get("velocidade", 0.0) or 0.0, d.get("giro_graus_s", 0.0) or 0.0, lote)]
            for b in ossos:
                arr = d["ossos"][b]; assert len(arr) == 7 * n, (animal, nome, b)
                for k in range(7):
                    ch = [arr[i * 7 + k] for i in range(n)]
                    if max(ch) - min(ch) < 1e-5:
                        if abs(ch[0] - PADRAO[k]) < 1e-5: continue
                        L.append("%s|%d|S%.5f" % (b, k + 1, ch[0]))
                    else: L.append("%s|%d|E%s" % (b, k + 1, enc(ch)))
            txt = "\n".join(L)
            open(os.path.join(AQUI, "dados", animal, nome + ".txt"), "w", encoding="utf-8", newline=chr(10)).write(txt)
            dados[nome] = {"$path": "dados/%s/%s.txt" % (animal, nome)}
            inv[animal][nome] = {"fonte": os.path.relpath(f, RAIZ).replace("\\", "/"), "lote": lote, "quadros": n, "fps": d["fps"],
                                 "duracao": d["duracao"], "loop": d["loop"], "velocidade": d.get("velocidade"), "ossos": len(ossos),
                                 "bytes": len(txt), "md5_json": hashlib.md5(open(f, "rb").read()).hexdigest()}
        arvore[animal] = {"$className": "Folder", "Dados": dados}
        print(animal, len(clipes), "clipes", sum(v["bytes"] for v in inv[animal].values()), "bytes")
    json.dump({"name": "FaunaFloresta", "tree": arvore}, open(os.path.join(AQUI, "fauna_dados.project.json"), "w"), indent=1)
    json.dump(inv, open(os.path.join(AQUI, "inventario.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

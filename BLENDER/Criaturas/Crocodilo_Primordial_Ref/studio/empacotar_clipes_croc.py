"""Empacota os JSON do Crocodilo Primordial (clipes/Crocodilo_*.json) em texto compacto para o Studio, sem HTTP
(mesmo formato do AdaptadorUrso, mas proprio do crocodilo). Por clipe, um StringValue em
ServerStorage.Crocodilo_Piloto.Dados_Clipes:
  linha 1: nome|fps|loop(0/1)|quadros|Osso1,Osso2,...
  demais : Osso|canal(1..7)|S<valor> (constante)  ou  Osso|canal|E<deltas> (inteiros x1e4, delta, zigzag, base64 5 bits
           + bit de continuacao). Canais: qx qy qz qw tx ty tz = matrix_basis do Blender. Canais constantes iguais ao
           padrao (q identidade, t zero) sao omitidos; o adaptador preenche.
Eventos da sincronizacao do JSON (s) vao em Dados_Clipes.Eventos_<clipe> = "nome=t;nome=t".
Grava lotes envio_NN.luau de ate ~LIMITE bytes (enviados um por vez pelo execute_luau, sem travar o Studio).
Uso: python empacotar_clipes_croc.py <dir_clipes> <dir_saida> [LIMITE]"""
import json, sys, os, glob
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
def enc(vals):
    out = []; prev = 0
    for v in vals:
        q = round(v * 10000); d = q - prev; prev = q; z = (-d * 2 - 1) if d < 0 else d * 2
        while True:
            c = z & 31; z >>= 5
            if z: out.append(A[c | 32])
            else: out.append(A[c]); break
    return "".join(out)
pasta, saida = sys.argv[1], sys.argv[2]; LIMITE = int(sys.argv[3]) if len(sys.argv) > 3 else 350000
os.makedirs(saida, exist_ok=True)
PADRAO = [0, 0, 0, 1, 0, 0, 0]
CAB = ('local raiz = game.ServerStorage:FindFirstChild("Crocodilo_Piloto") or Instance.new("Folder"); raiz.Name = "Crocodilo_Piloto"; raiz.Parent = game.ServerStorage\n'
       'local dados = raiz:FindFirstChild("Dados_Clipes") or Instance.new("Folder"); dados.Name = "Dados_Clipes"; dados.Parent = raiz\nlocal v\n')
RODA = '\nlocal r = 0 for _, c in ipairs(dados:GetChildren()) do r += 1 end return "Dados_Clipes: " .. r .. " valores"'
lotes = []; atual = []; tam = 0; resumo = []
for f in sorted(glob.glob(os.path.join(pasta, "Crocodilo_*.json"))):
    d = json.load(open(f, encoding="utf-8")); n = d["quadros"]; nome = d["nome"]
    L = ["%s|%d|%d|%d|%s" % (nome, d["fps"], 1 if d["loop"] else 0, n, ",".join(d["ossos"].keys()))]
    for b, arr in d["ossos"].items():
        for k in range(7):
            ch = [arr[i * 7 + k] for i in range(n)]
            if max(ch) - min(ch) < 1e-5:
                if abs(ch[0] - PADRAO[k]) < 1e-5: continue
                L.append("%s|%d|S%.5f" % (b, k + 1, ch[0]))
            else: L.append("%s|%d|E%s" % (b, k + 1, enc(ch)))
    txt = "\n".join(L)
    ev = (d.get("sincronizacao") or {}).get("eventos") or {}
    p = ['v = dados:FindFirstChild("%s"); if v then v:Destroy() end' % nome,
         'v = Instance.new("StringValue"); v.Name = "%s"; v.Value = [==[%s]==]; v.Parent = dados' % (nome, txt)]
    if ev:
        s = ";".join("%s=%.4f" % (k, t) for k, t in ev.items())
        p += ['v = dados:FindFirstChild("Eventos_%s"); if v then v:Destroy() end' % nome,
              'v = Instance.new("StringValue"); v.Name = "Eventos_%s"; v.Value = "%s"; v.Parent = dados' % (nome, s)]
    bloco = "\n".join(p)
    if atual and tam + len(bloco) > LIMITE: lotes.append(atual); atual = []; tam = 0
    atual.append(bloco); tam += len(bloco); resumo.append((nome, n, len(txt)))
if atual: lotes.append(atual)
for i, l in enumerate(lotes):
    open(os.path.join(saida, "envio_%02d.luau" % (i + 1)), "w", encoding="utf-8", newline=chr(10)).write(CAB + "\n".join(l) + RODA)
for nome, n, b in resumo: print("CLIPE", nome, n, "quadros", b, "bytes")
print("LOTES", len(lotes), [os.path.getsize(os.path.join(saida, "envio_%02d.luau" % (i + 1))) for i in range(len(lotes))])

"""Empacota os JSON do urso (rig/clipes) num texto compacto para enviar ao Studio sem HTTP (o place principal tem
HttpEnabled=false e nao alteramos a configuracao). Formato por clipe (StringValue):
  linha 1: nome|fps|loop(0/1)|quadros
  demais : Osso|canal(1..7)|S<valor>  (canal constante)  ou  Osso|canal|E<deltas>  (inteiros x1e4, delta, zigzag,
           base64 de 5 bits + bit de continuacao). Canais: qx qy qz qw tx ty tz (matrix_basis do Blender).
Uso: python empacotar_clipes.py ../clipes Urso_Repouso Urso_Andar Urso_Rigir -> grava dados_<clipe>.txt e envio.luau"""
import json, sys, os
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
pasta = sys.argv[1]; partes = []
for nome in sys.argv[2:]:
    d = json.load(open(os.path.join(pasta, nome + ".json"), encoding="utf-8")); n = d["quadros"]
    L = ["%s|%d|%d|%d" % (d["nome"], d["fps"], 1 if d["loop"] else 0, n)]
    for b, arr in d["ossos"].items():
        for k in range(7):
            ch = [arr[i * 7 + k] for i in range(n)]
            L.append("%s|%d|%s" % (b, k + 1, ("S%.5f" % ch[0]) if max(ch) - min(ch) < 1e-5 else "E" + enc(ch)))
    txt = "\n".join(L); open("dados_%s.txt" % nome, "w", encoding="utf-8").write(txt)
    partes.append('v = Instance.new("StringValue"); v.Name = "%s"; v.Value = [==[%s]==]; v.Parent = dados' % (nome, txt))
    print(nome, len(txt), "bytes")
lua = ('local raiz = game.ServerStorage:FindFirstChild("Urso_v2_Piloto") or Instance.new("Folder"); raiz.Name = "Urso_v2_Piloto"; raiz.Parent = game.ServerStorage\n'
       'local dados = raiz:FindFirstChild("Dados_Clipes") or Instance.new("Folder"); dados.Name = "Dados_Clipes"; dados.Parent = raiz\n'
       'for _, c in ipairs(dados:GetChildren()) do c:Destroy() end\nlocal v\n' + "\n".join(partes) + '\nreturn #dados:GetChildren()')
open("envio_dados.luau", "w", encoding="utf-8").write(lua); print("envio", len(lua))

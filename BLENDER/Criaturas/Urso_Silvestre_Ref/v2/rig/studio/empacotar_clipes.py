"""Empacota os JSON do urso (rig/clipes) num texto compacto para enviar ao Studio sem HTTP (o place principal tem
HttpEnabled=false e nao alteramos a configuracao). Formato por clipe (StringValue):
  linha 1: nome|fps|loop(0/1)|quadros
  demais : Osso|canal(1..7)|S<valor>  (canal constante)  ou  Osso|canal|E<deltas>  (inteiros x1e4, delta, zigzag,
           base64 de 5 bits + bit de continuacao). Canais: qx qy qz qw tx ty tz (matrix_basis do Blender).
Uso: python empacotar_clipes.py ../clipes Urso_Repouso Urso_Andar Urso_Rugir -> grava dados_<clipe>.txt e envio_dados.luau
     python empacotar_clipes.py ../clipes --saida envio_lote2.luau --acrescentar Urso_Corrida ... -> so acrescenta/substitui
     esses clipes (NAO apaga os demais) e grava os perfis v(t)/giro do manifesto em Dados_Clipes.Perfis_<clipe>
     --compacto: omite canais constantes iguais ao padrao (q identidade, t zero); o AdaptadorUrso os preenche"""
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
args = sys.argv[2:]; SAIDA = "envio_dados.luau"; ACRESC = "--acrescentar" in args
if "--saida" in args: i = args.index("--saida"); SAIDA = args[i + 1]; del args[i:i + 2]
COMPACTO = "--compacto" in args; PADRAO = [0, 0, 0, 1, 0, 0, 0]   # qx qy qz qw tx ty tz
args = [a for a in args if a not in ("--acrescentar", "--compacto")]
pasta = sys.argv[1]; partes = []
man = json.load(open(os.path.join(pasta, "manifesto_clipes.json"), encoding="utf-8"))
for nome in args:
    d = json.load(open(os.path.join(pasta, nome + ".json"), encoding="utf-8")); n = d["quadros"]
    L = ["%s|%d|%d|%d" % (d["nome"], d["fps"], 1 if d["loop"] else 0, n)]
    if COMPACTO: L[0] += "|" + ",".join(d["ossos"].keys())          # lista dos ossos: detecta osso faltando
    for b, arr in d["ossos"].items():
        for k in range(7):
            ch = [arr[i * 7 + k] for i in range(n)]
            const = max(ch) - min(ch) < 1e-5
            if COMPACTO and const and abs(ch[0] - PADRAO[k]) < 1e-5: continue     # canal = padrao: o adaptador preenche
            L.append("%s|%d|%s" % (b, k + 1, ("S%.5f" % ch[0]) if const else "E" + enc(ch)))
    txt = "\n".join(L); open("dados_%s.txt" % nome, "w", encoding="utf-8").write(txt)
    partes.append('v = dados:FindFirstChild("%s"); if v then v:Destroy() end' % nome)
    partes.append('v = Instance.new("StringValue"); v.Name = "%s"; v.Value = [==[%s]==]; v.Parent = dados' % (nome, txt))
    m = man.get(nome[5:], {}); perf = m.get("v_perfil_PARAMETRO"); giro = m.get("giro_graus_s_PROPOSTA"); vel = m.get("velocidade_studs_s_PROPOSTA")
    if ACRESC:   # parametros tecnicos da simulacao (NAO regras do jogo): v constante, giro ou perfil v(t) por quadro
        p = "v=%s;giro=%s;perfil=%s" % (vel or 0, giro or 0, ",".join("%.4f" % x for x in perf) if perf else "")
        partes.append('v = dados:FindFirstChild("Perfis_%s"); if v then v:Destroy() end' % nome)
        partes.append('v = Instance.new("StringValue"); v.Name = "Perfis_%s"; v.Value = "%s"; v.Parent = dados' % (nome, p))
    print(nome, len(txt), "bytes")
lua = ('local raiz = game.ServerStorage:FindFirstChild("Urso_v2_Piloto") or Instance.new("Folder"); raiz.Name = "Urso_v2_Piloto"; raiz.Parent = game.ServerStorage\n'
       'local dados = raiz:FindFirstChild("Dados_Clipes") or Instance.new("Folder"); dados.Name = "Dados_Clipes"; dados.Parent = raiz\n'
       + ('' if ACRESC else 'for _, c in ipairs(dados:GetChildren()) do c:Destroy() end\n') + 'local v\n' + "\n".join(partes)
       + '\nlocal r = {} for _, c in ipairs(dados:GetChildren()) do table.insert(r, c.Name .. "=" .. #c.Value) end table.sort(r) return table.concat(r, " ")')
open(SAIDA, "w", encoding="utf-8").write(lua); print("envio", SAIDA, len(lua))

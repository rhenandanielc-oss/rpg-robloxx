"""Patches do 'poder ativo' (27/11) nos servidores Sol, Investida e Furia. Aplica nos arquivos locais e gera
patches_poder_ativo.lua (mesmas trocas, para aplicar no Studio). Uso: python patches_poder_ativo.py"""
import os, json
AQUI = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(AQUI)
CHK = '\tif cerbero:GetAttribute("PoderAtivo") then log("recusado: poder ativo (" .. tostring(cerbero:GetAttribute("PoderAtivo")) .. ")") return end\n'
P = {
 "sol/SolInfernal_Servidor.server.luau": ("SolInfernal_Servidor", [
  ('\testado.ocupado = true\n\tlocal roxo = cerbero:GetAttribute("Furia") == true\n\tlog(string.format("lancando',
   CHK + '\tcerbero:SetAttribute("PoderAtivo", "Sol"); cerbero:SetAttribute("MordidaBloqueada", true)   -- poder ativo (27/11)\n\testado.ocupado = true\n\tlocal roxo = cerbero:GetAttribute("Furia") == true\n\tlog(string.format("lancando'),
  ('\t\t\tbola:Destroy()\n\t\t\testado.prontoEm = os.clock() + C.Recarga * C.RecargaInterrompida\n',
   '\t\t\tbola:Destroy()\n\t\t\tcerbero:SetAttribute("PoderAtivo", nil); cerbero:SetAttribute("MordidaBloqueada", nil)\n\t\t\testado.prontoEm = os.clock() + C.Recarga * C.RecargaInterrompida\n'),
  ('\tbola:SetAttribute("Escala", 1); bola:SetAttribute("Voando", true)\n',
   '\tbola:SetAttribute("Escala", 1); bola:SetAttribute("Voando", true)\n\tcerbero:SetAttribute("MordidaBloqueada", nil)   -- disparou: pode morder\n'),
  ('\tbola:Destroy()\n\testado.prontoEm = os.clock() + C.Recarga\n',
   '\tbola:Destroy()\n\tcerbero:SetAttribute("PoderAtivo", nil)\n\testado.prontoEm = os.clock() + C.Recarga\n'),
 ]),
 "investida/Investida_Servidor.server.luau": ("Investida_Servidor", [
  ('\testado.ocupado = true; estado.dono = dono; estado.dirAlvo = nil; donoRastro = dono\n',
   CHK + '\tcerbero:SetAttribute("PoderAtivo", "Investida")   -- poder ativo (27/11); mordida liberada no boost\n\testado.ocupado = true; estado.dono = dono; estado.dirAlvo = nil; donoRastro = dono\n'),
  ('\t\t\t\t\t\tsobre = {modelo = m, h = h, inicio = os.clock(), danoFeito = false}\n',
   '\t\t\t\t\t\tsobre = {modelo = m, h = h, inicio = os.clock(), danoFeito = false}\n\t\t\t\t\t\tcerbero:SetAttribute("MordidaBloqueada", true)\n'),
  ('\t\t\t\tsobre = nil\n',
   '\t\t\t\tsobre = nil\n\t\t\t\tcerbero:SetAttribute("MordidaBloqueada", nil)\n'),
  ('\t\t\t\t\t\ttocar("Cerbero_InvestidaImpacto", 0.08)\n',
   '\t\t\t\t\t\ttocar("Cerbero_InvestidaImpacto", 0.08)\n\t\t\t\t\t\tcerbero:SetAttribute("MordidaBloqueada", true)\n'),
  ('\testado.ocupado = false; estado.dono = nil\n',
   '\testado.ocupado = false; estado.dono = nil\n\tcerbero:SetAttribute("PoderAtivo", nil); cerbero:SetAttribute("MordidaBloqueada", nil)\n'),
 ]),
 "vigilia/VigiliaFuria_Servidor.server.luau": ("VigiliaFuria_Servidor", [
  ('\testado.ocupado = true\n\tlog(string.format("FURIA',
   CHK + '\tcerbero:SetAttribute("PoderAtivo", "Furia"); cerbero:SetAttribute("MordidaBloqueada", true)   -- poder ativo so no rugido (27/11)\n\testado.ocupado = true\n\tlog(string.format("FURIA'),
  ('\t\tcerbero:SetAttribute("MultDano", C.FuriaMultDano)\n',
   '\t\tcerbero:SetAttribute("MultDano", C.FuriaMultDano)\n\t\tcerbero:SetAttribute("PoderAtivo", nil); cerbero:SetAttribute("MordidaBloqueada", nil)\n\t\tcerbero:SetAttribute("FuriaSustentada", true)   -- Mordida_Servidor: cabecas independentes, +15% de velocidade de ataque\n'),
  ('\t\tcerbero:SetAttribute("MultDano", 1); cerbero:SetAttribute("Furia", false); cerbero:SetAttribute("FuriaFade", nil)\n',
   '\t\tcerbero:SetAttribute("MultDano", 1); cerbero:SetAttribute("Furia", false); cerbero:SetAttribute("FuriaFade", nil)\n\t\tcerbero:SetAttribute("FuriaSustentada", nil)\n'),
 ]),
}
lua = ["return {"]
for arq, (nome, pares) in P.items():
    p = os.path.join(BASE, arq); s = open(p, encoding="utf-8").read()
    if "PoderAtivo" in s: print("ja aplicado:", arq); continue
    for a, b in pares:
        assert s.count(a) == 1, (arq, a[:60], s.count(a)); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s); print("ok", arq)
    lua.append('\t{"%s", {' % nome)
    for a, b in pares: lua.append("\t\t{[==[%s]==], [==[%s]==]}," % (a, b))
    lua.append("\t}},")
lua.append("}")
open(os.path.join(AQUI, "patches_poder_ativo.lua"), "w", encoding="utf-8", newline="\n").write("\n".join(lua) + "\n")

"""Gera instalar_golpe_colossal.luau (rodar no Studio, modo EDIT, place rpg_roblox, com o Studio reservado):
  1) dados do clipe GolpeColossal em ServerStorage.Urso_v2_Piloto.Dados_Clipes (so acrescenta);
  2) KeyframeSequence Urso_GolpeColossal em Urso_v2_Piloto.Animacoes (prioridade Action2) + atributo ImpactoS do JSON;
  3) ModuleScript PoderesUrso_Servidor em Urso_v2_Piloto.Poderes e EfeitosUrso_Cliente em ReplicatedStorage.Urso_v2_Lab.
Nao cria Script/LocalScript que rode sozinho: o laboratorio liga os modulos durante o Play (teste_golpe_colossal.luau).
Uso: python gerar_instalador.py"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
envio = open(os.path.join(D, "envio_golpe_colossal.luau"), encoding="utf-8").read()
envio = envio[:envio.rindex("local r = {}")]                      # tira o return final do envio
ev = json.load(open(os.path.join(D, "..", "..", "poderes", "clipes", "Urso_GolpeColossal.json"), encoding="utf-8"))["eventos"]
srv = open(os.path.join(D, "PoderesUrso_Servidor.luau"), encoding="utf-8").read()
cli = open(os.path.join(D, "EfeitosUrso_Cliente.luau"), encoding="utf-8").read()
for s in (srv, cli): assert "]=====]" not in s
lua = envio + '''
-- 2) KeyframeSequence (adaptador proprio do urso) + instante do impacto marcado no Blender
local P = game.ServerStorage.Urso_v2_Piloto
local A = require(P.AdaptadorUrso:Clone())
local modelo = workspace.Teste_Urso_v2.Urso_Silvestre_v2_Piloto
local kfs, faltam, np = A.montar(modelo, "Urso_GolpeColossal", Enum.AnimationPriority.Action2)
local velho = P.Animacoes:FindFirstChild("Urso_GolpeColossal"); if velho then velho:Destroy() end
kfs:SetAttribute("ImpactoS", %s); kfs:SetAttribute("ImpactoQuadro", %d); kfs:SetAttribute("RugidoS", %s); kfs.Parent = P.Animacoes
-- 3) modulos (fonte gravada pelo instalador; versoes no repo: rig/studio/poderes/*.luau)
local pod = P:FindFirstChild("Poderes") or Instance.new("Folder"); pod.Name = "Poderes"; pod.Parent = P
local s = pod:FindFirstChild("PoderesUrso_Servidor") or Instance.new("ModuleScript"); s.Name = "PoderesUrso_Servidor"
s.Source = [=====[%s]=====]; s.Parent = pod
local lab = game.ReplicatedStorage:FindFirstChild("Urso_v2_Lab") or Instance.new("Folder"); lab.Name = "Urso_v2_Lab"; lab.Parent = game.ReplicatedStorage
local c = lab:FindFirstChild("EfeitosUrso_Cliente") or Instance.new("ModuleScript"); c.Name = "EfeitosUrso_Cliente"
c.Source = [=====[%s]=====]; c.Parent = lab
return string.format("KFS kf=%%d poses=%%d faltam=%%s impacto=%%s | dados=%%d | modulos ok", #kfs:GetChildren(), np, table.concat(faltam, ","), tostring(kfs:GetAttribute("ImpactoS")), #P.Dados_Clipes.Urso_GolpeColossal.Value)
''' % (ev["impacto_s"], ev["impacto_quadro"], ev.get("rugido_s", "nil"), srv, cli)
open(os.path.join(D, "instalar_golpe_colossal.luau"), "w", encoding="utf-8").write(lua)
print("INSTALADOR_OK", len(lua), "bytes; impacto", ev)

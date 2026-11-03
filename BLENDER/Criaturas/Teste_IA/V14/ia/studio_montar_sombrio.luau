-- studio_montar_sombrio.luau (Studio, modo Edit, DEPOIS do Import 3D de dragao_sombra/final/SB_Dragao_Sombrio_v4.glb):
-- (copia do studio_montar_glacial.luau) cria o DRAGAO SOMBRIO montavel ("Sombrio") AO LADO do Dragao das Montanhas, sem substituir nada. Mesmo esqueleto e
-- mesmos nomes de ossos -> montaria, IA, sons e MovimentoVivo funcionam; clipes em ReplicatedStorage.Animacoes_Sombrio
-- (prefixo Sombrio_, ja montados). Kit de SOMBRA PENDENTE (decisao do usuario): FormaRegional "Sombrio" nao esta no
-- ConfigCombate (so os ataques basicos); nada de Fogo ou Gelo e copiado.
-- Seguranca: o importado nao e apagado ate o Sombrio existir; um Sombrio anterior vai para
-- ServerStorage.Dragoes_Retirados com data. Tudo reversivel (apagar workspace.Sombrio). Os outros dragoes nao sao tocados.
local SS = game:GetService("ServerStorage")
local importado
for _, m in ipairs(workspace:GetChildren()) do
	if m:IsA("Model") and not m.Name:find("^Silverwing") and m.Name ~= "Glacial" and m.Name ~= "Sombrio" and m:FindFirstChild("Silverwing_Detalhes", true) then importado = m end
end
assert(importado, "importacao do SB_Dragao_Sombrio_v4.glb nao encontrada no Workspace (Import 3D primeiro)")
local base = workspace:FindFirstChild("Silverwing"); assert(base, "Silverwing (referencia de escala/pivo) nao encontrado")
local RENOMEIA = {["Silverwing"] = "Silverwing_Corpo", ["Silverwing.001"] = "Silverwing_Asas"}
for _, d in ipairs(importado:GetDescendants()) do
	if d:IsA("MeshPart") and RENOMEIA[d.Name] then d.Name = RENOMEIA[d.Name] end
end
local m = importado:Clone()
m:ScaleTo(17.5)                                                  -- mesma escala do CR (o GLB usa as mesmas unidades)
for _, d in ipairs(m:GetDescendants()) do
	if d:IsA("Bone") then assert(d.Name ~= "head" and d.Name ~= "mouth_lower", "GLB com nomes do Blender: reexporte com exportar_sombrio.py") end
	if d:IsA("BasePart") then d.Anchored = true end
	if d:IsA("MeshPart") then d.DoubleSided = true end
end
local rp = m:FindFirstChild("RootPart")
if rp then rp.CanCollide = false; rp.CanQuery = false; rp.CanTouch = false; rp.CastShadow = false end
m.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
-- atributos de montaria/camera/escala do Silverwing (mesmas patas e asas), identidade propria do Sombrio
for k, v in pairs(base:GetAttributes()) do if not k:find("^RBX_") then m:SetAttribute(k, v) end end
m:SetAttribute("FormaRegional", "Sombrio"); m:SetAttribute("ElementoNato", "Sombra"); m:SetAttribute("ElementosDesbloqueados", "")
m:SetAttribute("NomeExibicao", "Dragao Sombrio"); m:SetAttribute("PastaAnimacoes", "Sombrio"); m:SetAttribute("PerfilMovimento", "Silverwing")
m:SetAttribute("TesteScriptsMontanhas", nil)
m:SetAttribute("HabilidadesForma", "")                   -- kit de sombra pendente: HUD sem habilidades (patch_hud_habilidades_forma)
m:SetAttribute("Versao", "Sombrio v9 (03/11: acabamento, crina, boca com paredes internas)")
m:SetAttribute("Origem", "Modelo proprio (Blender, dragao_sombra/criar_sombrio.py) + esqueleto Silverwing; TESTE")
-- pivo -> pes igual ao do Silverwing (montaria e IA movem por PivotTo contando com essa altura)
local function pes(mod)
	local y = math.huge
	for _, b in ipairs(mod:GetDescendants()) do if b:IsA("Bone") and b.Name:find("toes_tip") then y = math.min(y, b.WorldPosition.Y) end end
	return y
end
local acima = base:GetPivot().Position.Y - pes(base)
local prim = m.PrimaryPart
prim.PivotOffset = CFrame.new(0, (pes(m) + acima) - prim.Position.Y, 0)
m:PivotTo(base:GetPivot() * CFrame.new(90, 0, 0))                -- do outro lado do Silverwing (o Glacial fica a -90)
m.Name = "Sombrio"
local velho = workspace:FindFirstChild("Sombrio")
if velho then
	local guard = SS:FindFirstChild("Dragoes_Retirados") or Instance.new("Folder"); guard.Name = "Dragoes_Retirados"; guard.Parent = SS
	velho.Name = "Sombrio_" .. os.date("!%Y%m%d_%H%M%S"); velho.Parent = guard
end
m.Parent = workspace
importado:Destroy()
return "Sombrio criado em " .. tostring(m:GetPivot().Position)

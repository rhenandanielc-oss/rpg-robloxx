-- patch_vfx_neutro.luau (Studio, modo Edit) — achado no teste do Glacial selvagem (02/11): sem elemento ativo, os
-- impactos dos ataques BASICOS (mordida/garra/cauda) e a reacao do alvo caiam no padrao "Fogo" (chamas e fumaca
-- laranja num dragao de gelo). Agora um dragao sem elemento ativo e que NAO e do Montanhas usa o perfil "Neutro":
-- poeira/estilhaco claro, sem fogo, sem luz quente. Nao e um poder de gelo (kit pendente): so o impacto fisico.
-- O Dragao das Montanhas nao muda.
local RS, SS = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage")
local alvos = {VFX = RS.Combate_Dragoes.VFXCombate}
if alvos.VFX.Source:find("PATCH_VFX_NEUTRO", 1, true) then return "ja aplicado" end
local novo = {}; for k, s in pairs(alvos) do novo[k] = s.Source:gsub("\r\n", "\n") end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true); assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end
troca("VFX", [=[	Ar = {cor = C3(215, 235, 245), luz = C3(220, 240, 255), nucleo = {C3(255, 255, 255), C3(220, 240, 250), C3(190, 215, 230), C3(160, 185, 200)}},
}]=], [=[	Ar = {cor = C3(215, 235, 245), luz = C3(220, 240, 255), nucleo = {C3(255, 255, 255), C3(220, 240, 250), C3(190, 215, 230), C3(160, 185, 200)}},
	-- PATCH_VFX_NEUTRO (02/11): impacto fisico sem elemento (dragao cujo kit ainda nao existe): poeira/estilhaco claro
	Neutro = {cor = C3(225, 232, 240), luz = C3(225, 235, 250), nucleo = {C3(248, 250, 255), C3(215, 224, 235), C3(178, 188, 202), C3(140, 150, 165)}},
}]=])
troca("VFX", [=[	local f = fatorLOD(m:GetPivot().Position); local el = d.el or "Fogo"; local P = PERFIL[el]]=],
	[=[	-- sem elemento: Montanhas segue no Fogo; outras formas (Glacial com kit pendente) usam o impacto Neutro
	local semEl = (m:GetAttribute("FormaRegional") ~= "Montanhas") and "Neutro" or "Fogo"
	local f = fatorLOD(m:GetPivot().Position); local el = d.el or semEl; local P = PERFIL[el] or PERFIL.Neutro]=])
for k in pairs(alvos) do local f, e = loadstring(novo[k]); assert(f, k .. " nao compila: " .. tostring(e)) end
local bk = SS:FindFirstChild("Backup_VFX_Neutro_2026-11-02")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_VFX_Neutro_2026-11-02"
	for k, s in pairs(alvos) do local c = s:Clone(); c.Name = k .. "__" .. s.Name; c.Parent = bk end
	bk.Parent = SS
end
for k, s in pairs(alvos) do s.Source = novo[k] end
return "aplicado"

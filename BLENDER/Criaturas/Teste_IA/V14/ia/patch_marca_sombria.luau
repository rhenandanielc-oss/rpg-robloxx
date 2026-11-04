-- patch_marca_sombria.luau (Studio, Edit) — Marca Sombria do Dragao Sombrio + estado de combate para o Rastro do Breu.
-- Gerado por marca_trocas.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico ServerStorage.Backup_Marca_Sombria_2026-11-03.
local SS = game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local novos = {}
do local s = game.ServerScriptService.Combate_Dragao.ConfigCombate; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_MARCA_SOMBRIA", 1, true) or src:find("Marca Sombria (Dragao Sombrio", 1, true) then return "ja aplicado" end
  src = troca(src, [==[	elementosForma = {Montanhas = {"Fogo"}, Glacial = {"Gelo"}},]==], [==[	elementosForma = {Montanhas = {"Fogo"}, Glacial = {"Gelo"}, Sombrio = {"Sombra"}},   -- PATCH_MARCA_SOMBRIA (03/11): Sombrio = Sombra]==])
  src = troca(src, [==[	passivasForma = {Montanhas = {"SangueDeMagma", "Burning"}, Glacial = {"SangueGlacial", "Frostbite"}},]==], [==[	passivasForma = {Montanhas = {"SangueDeMagma", "Burning"}, Glacial = {"SangueGlacial", "Frostbite"}, Sombrio = {"MarcaSombria", "RastroBreu"}},]==])
  src = troca(src, [==[		Frostbite = {max = 100, basico = 10,]==], [==[		-- Marca Sombria (Sombrio, 03/11; NAO_APROVADO): ate max marcas por alvo e por origem; +porMarca de dano Sombra por
		-- marca; sem acerto por decaiApos s, cai 1 marca a cada decaiIntervalo s
		MarcaSombria = {max = 5, porMarca = 0.06, decaiApos = 6, decaiIntervalo = 1.5},
		Frostbite = {max = 100, basico = 10,]==])
  assert(loadstring(src), "ConfigCombate.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao.Passivas; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_MARCA_SOMBRIA", 1, true) or src:find("Marca Sombria (Dragao Sombrio", 1, true) then return "ja aplicado" end
  src = src:gsub("%s*return P%s*$", "

") .. [==[
-- ===== Marca Sombria (Dragao Sombrio, kit definido pelo usuario em 03/11; numeros NAO_APROVADO) =================
-- Acertos de Sombra do Sombrio acumulam marcas no alvo (por ORIGEM: cada Sombrio so ve as proprias). Cada marca
-- aumenta o dano Sombra dele contra esse alvo (linear, com teto; ticks de dano usam o multiplicador mas NAO marcam).
-- Sem lentidao nem stun. Sem novos acertos, as marcas caem uma a uma. Atributos no alvo (so para o visual e para o
-- Rastro do Breu): MarcaSombria = total; MarcaSombria_<nome da origem> = marcas daquela origem.
local marcas = {}                                                   -- [alvo] = {[fonte] = {n, ultimo, prox}}
P.marcas = marcas
local function atribMarca(alvo)
	local tot = 0
	for f, e in pairs(marcas[alvo] or {}) do tot += e.n; alvo:SetAttribute("MarcaSombria_" .. f.Name, e.n > 0 and e.n or nil) end
	alvo:SetAttribute("MarcaSombria", tot > 0 and tot or nil)
	local CS = game:GetService("CollectionService")                 -- tag para o visual no cliente (sem varrer o workspace)
	if tot > 0 then CS:AddTag(alvo, "MarcaSombria") else CS:RemoveTag(alvo, "MarcaSombria") end
end
function P.marcasDe(fonte, alvo) local t = marcas[alvo]; local e = t and t[fonte]; return e and e.n or 0 end
function P.alvosMarcados(fonte)                                     -- lista de alvos com marca desta origem
	local l = {}; for a, t in pairs(marcas) do if t[fonte] and t[fonte].n > 0 and a.Parent then table.insert(l, a) end end; return l
end
function P.multiplicadorMarca(fonte, alvo)
	if not P.tem(fonte, "MarcaSombria") then return 1 end
	return 1 + Cfg.passivas.MarcaSombria.porMarca * P.marcasDe(fonte, alvo)
end
function P.aplicarMarca(fonte, alvo)
	if not (fonte and alvo and alvo.Parent) or not P.tem(fonte, "MarcaSombria") then return false end
	local M_ = Cfg.passivas.MarcaSombria
	local t = marcas[alvo]; if not t then t = {}; marcas[alvo] = t end
	local e = t[fonte]; if not e then e = {n = 0}; t[fonte] = e end
	e.n = math.min(M_.max, e.n + 1); e.ultimo = os.clock(); e.prox = nil
	atribMarca(alvo); return true
end
function P.consumirMarcas(fonte, alvo)                              -- (Eclipse Draconico, futuro): devolve quantas havia
	local n = P.marcasDe(fonte, alvo); if n > 0 then marcas[alvo][fonte] = nil; atribMarca(alvo) end; return n
end
task.spawn(function()
	while true do
		task.wait(0.25)
		local M_ = Cfg.passivas.MarcaSombria; local t0 = os.clock()
		for alvo, t in pairs(marcas) do
			local h = alvo.Parent and alvo:FindFirstChildOfClass("Humanoid")
			if not alvo.Parent or (h and h.Health <= 0) then
				if alvo.Parent then for f in pairs(t) do alvo:SetAttribute("MarcaSombria_" .. f.Name, nil) end; alvo:SetAttribute("MarcaSombria", nil); game:GetService("CollectionService"):RemoveTag(alvo, "MarcaSombria") end
				marcas[alvo] = nil
			else
				local mudou = false
				for f, e in pairs(t) do
					if not f.Parent then t[f] = nil; alvo:SetAttribute("MarcaSombria_" .. f.Name, nil); mudou = true
					elseif t0 - e.ultimo > M_.decaiApos then
						e.prox = e.prox or t0
						if t0 >= e.prox then e.n -= 1; e.prox = t0 + M_.decaiIntervalo; mudou = true end
						if e.n <= 0 then t[f] = nil; alvo:SetAttribute("MarcaSombria_" .. f.Name, nil) end
					end
				end
				if mudou then atribMarca(alvo) end
				if next(t) == nil then marcas[alvo] = nil end
			end
		end
	end
end)
return P]==] .. "\n"
  assert(loadstring(src), "Passivas.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao.Nucleo; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_MARCA_SOMBRIA", 1, true) or src:find("Marca Sombria (Dragao Sombrio", 1, true) then return "ja aplicado" end
  src = troca(src, [==[		dano *= Passivas.vulnerabilidade(a)                             -- Frostbite: alvo muito congelado sofre mais]==], [==[		dano *= Passivas.vulnerabilidade(a)                             -- Frostbite: alvo muito congelado sofre mais
		if Passivas.tem(fonte, "MarcaSombria") then el = el or "Sombra"; if el == "Sombra" then dano *= Passivas.multiplicadorMarca(fonte, a) end end   -- PATCH_MARCA_SOMBRIA]==])
  src = troca(src, [==[		Passivas.marcarCombate(fonte)
	end
	return ok]==], [==[		Passivas.marcarCombate(fonte)
		if el == "Sombra" then Passivas.aplicarMarca(fonte, a) end      -- PATCH_MARCA_SOMBRIA: acerto (nao tick) marca
	end
	if ok then local t = workspace:GetServerTimeNow(); if fonte then fonte:SetAttribute("UltimoCombate", t) end; a:SetAttribute("UltimoCombate", t) end   -- PATCH_MARCA_SOMBRIA: Rastro do Breu
	return ok]==])
  assert(loadstring(src), "Nucleo.luau nao compila"); table.insert(novos, {s, src}) end
if not SS:FindFirstChild("Backup_Marca_Sombria_2026-11-03") then local f = Instance.new("Folder"); f.Name = "Backup_Marca_Sombria_2026-11-03"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end
for _, x in ipairs(novos) do x[1].Source = x[2] end
return "aplicado: ConfigCombate + Passivas + Nucleo (" .. #novos .. "); backup ServerStorage.Backup_Marca_Sombria_2026-11-03"

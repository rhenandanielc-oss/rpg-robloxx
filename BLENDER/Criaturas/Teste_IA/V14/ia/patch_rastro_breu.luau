-- patch_rastro_breu.luau (Studio, modo Edit) — passiva Rastro do Breu do Dragao Sombrio, etapa 1 (modo exploracao).
-- Autorizado pelo usuario em 03/11 ("Sim, comecar"). Tudo-ou-nada:
--  1) Montaria_Dragao_Servidor: a velocidade-ALVO no chao (andar/correr para frente) e no voo livre e multiplicada por
--     (1 + RastroBonus). RastroBonus so existe em modelos com a passiva (Sombrio): os outros dragoes nao mudam.
--  2) Scripts novos: ServerScriptService.RastroBreu_Servidor e StarterPlayer.StarterPlayerScripts.RastroBreu_Cliente
--     (fonte servida em http://127.0.0.1:8766/sombrio/).
-- Backup unico: ServerStorage.Backup_Rastro_Breu_2026-11-03 (Montaria antes do patch). Reversivel: restaurar o backup e
-- apagar os 2 scripts novos.
local HS, SS, SSS = game:GetService("HttpService"), game:GetService("ServerStorage"), game:GetService("ServerScriptService")
local MS = SSS.Montaria_Dragao_Servidor
local src = MS.Source:gsub("\r\n", "\n")
local function troca(a, b)
	local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(src, a, j + 1, true), "trecho repetido: " .. a:sub(1, 70))
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1)
end
if not src:find("PATCH_RASTRO_BREU", 1, true) then
	troca([=[		if e.f > 0.1 then alvo = (e.correr and (m:GetAttribute("VelCorrer") or Cfg.correrVel) or (m:GetAttribute("VelAndar") or Cfg.andarVel)) * math.min(e.f, 1)]=],
		[=[		if e.f > 0.1 then alvo = (e.correr and (m:GetAttribute("VelCorrer") or Cfg.correrVel) or (m:GetAttribute("VelAndar") or Cfg.andarVel)) * math.min(e.f, 1)
			* (1 + (m:GetAttribute("RastroBonus") or 0))                                -- PATCH_RASTRO_BREU (03/11): passiva do Sombrio]=])
	troca([=[	local alvoVel = arr and ARR.velAr or f > 0.1 and (e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f or 0]=],
		[=[	local alvoVel = arr and ARR.velAr or f > 0.1 and (e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f * (1 + (m:GetAttribute("RastroBonus") or 0)) or 0   -- PATCH_RASTRO_BREU]=])
	assert(loadstring(src), "Montaria nao compila depois do patch")
	if not SS:FindFirstChild("Backup_Rastro_Breu_2026-11-03") then
		local f = Instance.new("Folder"); f.Name = "Backup_Rastro_Breu_2026-11-03"; MS:Clone().Parent = f; f.Parent = SS
	end
	MS.Source = src
end
local function script(classe, pai, nome, url)
	local fonte = HS:GetAsync(url, true):gsub("\r\n", "\n"); assert(loadstring(fonte), nome .. " nao compila")
	local s = pai:FindFirstChild(nome) or Instance.new(classe); s.Name = nome; s.Source = fonte; s.Parent = pai
end
script("Script", SSS, "RastroBreu_Servidor", "http://127.0.0.1:8766/sombrio/RastroBreu_Servidor.server.luau")
script("LocalScript", game:GetService("StarterPlayer").StarterPlayerScripts, "RastroBreu_Cliente", "http://127.0.0.1:8766/sombrio/RastroBreu_Cliente.client.luau")
return "aplicado: Montaria (2 trechos) + RastroBreu_Servidor + RastroBreu_Cliente; backup ServerStorage.Backup_Rastro_Breu_2026-11-03"

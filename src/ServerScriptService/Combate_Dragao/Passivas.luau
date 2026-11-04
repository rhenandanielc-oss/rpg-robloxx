-- Passivas (ModuleScript, ServerScriptService.Combate_Dragao) — passivas do combate, AUTORIDADE DO SERVIDOR.
-- Oficial 30/10/2026 (Dragao das Montanhas): Sangue de Magma e Burning. Numeros em ConfigCombate.passivas (PROVISORIOS).
--  * Sangue de Magma: o dano de Fogo recebido e reduzido (resistencia natural); dano significativo recebido dentro de uma
--    janela ativa um reforco ofensivo temporario (multiplicador no dano causado), com intervalo minimo entre ativacoes.
--  * Burning: so e aplicado pelo Nucleo DEPOIS de um acerto que causou dano (nunca em ataque que errou). Uma queimadura
--    por alvo e por origem: novos acertos renovam a duracao (sem empilhar dano), com teto de renovacoes e de duracao
--    total. Cada tick revalida o alvo (vivo, fora de zona segura, PvP ainda ativo para jogadores, nao imune) e aplica
--    o dano pelo mesmo caminho do Nucleo (Humanoid ou vida do guardiao), reduzido pela resistencia a Fogo do alvo.
-- O cliente so recebe atributos (Queimando, SangueMagmaFim) para os efeitos visuais discretos.
local Players = game:GetService("Players")
local Cfg = require(script.Parent.ConfigCombate)

local P = {}
local N                                                             -- Nucleo (injetado em P.ligar, evita require circular)
function P.ligar(nucleo) N = nucleo end

local function agora() return workspace:GetServerTimeNow() end
local function forma(m) return m and m:GetAttribute("FormaRegional") end
function P.tem(m, nome)
	local l = Cfg.passivasForma[forma(m) or ""]; return l ~= nil and table.find(l, nome) ~= nil
end

-- ===== Sangue de Magma ==========================================================================================
local recebido = {}                                                 -- [modelo] = {{t, dano}, ...} dentro da janela
local proxAtivacao = {}                                             -- [modelo] = os.clock() liberado
function P.multiplicadorOfensivo(m)
	if not P.tem(m, "SangueDeMagma") then return 1 end
	return (m:GetAttribute("SangueMagmaFim") or 0) > agora() and Cfg.passivas.SangueDeMagma.multiplicadorOfensivo or 1
end
-- dragao (modelo) vai receber 'dano' do elemento 'el': devolve o dano final e registra para a ativacao
function P.danoRecebido(m, dano, el)
	if not P.tem(m, "SangueDeMagma") then return dano end
	local S = Cfg.passivas.SangueDeMagma
	if el == "Fogo" then dano *= (1 - S.resistenciaFogo) end
	local l = recebido[m] or {}; recebido[m] = l
	local t = os.clock(); table.insert(l, {t, dano})
	local soma = 0
	for i = #l, 1, -1 do if t - l[i][1] > S.janela then table.remove(l, i) else soma += l[i][2] end end
	local max = m:GetAttribute("VidaMax") or 600
	if soma >= S.limiar * max and t >= (proxAtivacao[m] or 0) then
		proxAtivacao[m] = t + S.intervalo; recebido[m] = {}
		m:SetAttribute("SangueMagmaFim", agora() + S.duracao)
		if N then N.FX:FireAllClients({d = m, hab = "SangueDeMagma", fase = "ativar", duracao = S.duracao, el = "Fogo"}) end
	end
	return dano
end
-- resistencia a Fogo de QUALQUER alvo (atributo generico ResistenciaFogo 0..1, ou a passiva do dragao)
function P.resistenciaFogo(alvo)
	if P.tem(alvo, "SangueDeMagma") then return Cfg.passivas.SangueDeMagma.resistenciaFogo end
	return math.clamp(alvo:GetAttribute("ResistenciaFogo") or 0, 0, 1)
end

-- ===== Burning ==================================================================================================
local queimas = {}                                                  -- [alvo] = {[fonte] = {fim, prox, inicio, renov}}
P.queimas = queimas
local function marcar(alvo)
	local fim = 0
	for _, q in pairs(queimas[alvo] or {}) do fim = math.max(fim, q.fim) end
	alvo:SetAttribute("Queimando", fim > 0 and fim or nil)
end
function P.aplicarBurning(fonte, alvo)
	if not (fonte and alvo and alvo.Parent) or not P.tem(fonte, "Burning") then return false end
	local B = Cfg.passivas.Burning
	if alvo:GetAttribute(B.imuneAtributo) then return false end
	if P.resistenciaFogo(alvo) >= 1 then return false end
	local porFonte = queimas[alvo] or {}; queimas[alvo] = porFonte
	local q = porFonte[fonte]; local t = agora()
	if q and q.fim > t then
		-- renova (nao empilha): duracao volta ao maximo, limitada por renovacoes e pela duracao total continua
		if q.renov < B.renovaMax then
			q.renov += 1
			q.fim = math.min(t + B.duracao, q.inicio + B.duracaoMaxTotal)
		end
	else
		porFonte[fonte] = {fim = t + B.duracao, prox = t + B.intervalo, inicio = t, renov = 0}
	end
	marcar(alvo)
	return true
end
local function encerrar(alvo, fonte)
	local porFonte = queimas[alvo]; if not porFonte then return end
	porFonte[fonte] = nil
	if next(porFonte) == nil then queimas[alvo] = nil end
	if alvo.Parent then marcar(alvo) end
end
-- o alvo ainda pode ser ferido por esta fonte? (mesmas regras do Nucleo no momento do acerto, revistas a cada tick)
local function aindaValido(fonte, alvo)
	if not (alvo.Parent and fonte.Parent) then return false end
	local r = alvo:FindFirstChild("HumanoidRootPart") or alvo.PrimaryPart; if not r then return false end
	if N.emZonaSegura(r.Position) then return false end
	if alvo:GetAttribute(Cfg.passivas.Burning.imuneAtributo) then return false end
	local h = alvo:FindFirstChildOfClass("Humanoid")
	if h then
		if h.Health <= 0 then return false end
		local plr = Players:GetPlayerFromCharacter(alvo); local dono = fonte:GetAttribute("DonoUserId")
		if plr and dono and (plr.UserId == dono or workspace:GetAttribute(Cfg.pvpAtivoAtributo) ~= true) then return false end
		return true
	end
	return alvo:GetAttribute("GuardiaoNinho") ~= nil and not alvo:GetAttribute("Incapacitado")
end
task.spawn(function()
	while true do
		task.wait(0.2)
		local t = agora(); local B = Cfg.passivas.Burning
		for alvo, porFonte in pairs(queimas) do
			for fonte, q in pairs(porFonte) do
				if q.fim <= t or not aindaValido(fonte, alvo) then encerrar(alvo, fonte)
				elseif t >= q.prox then
					q.prox += B.intervalo
					local dano = B.danoTick                    -- resistencia a Fogo aplicada em N.ferir (uma vez so)
					if dano > 0 and N then N.ferir(fonte, alvo, dano, "Fogo", "Burning", "leve", true) end
				end
			end
		end
	end
end)

-- ===== PATCH_KIT_GELO: Sangue Glacial e Frostbite (Dragao Glacial, oficial 02/11) ==================================
function P.resistenciaGelo(alvo)
	if P.tem(alvo, "SangueGlacial") then return Cfg.passivas.SangueGlacial.resistenciaGelo end
	return math.clamp(alvo:GetAttribute("ResistenciaGelo") or 0, 0, 1)
end
function P.marcarCombate(m)                                          -- Sangue Glacial: brilho frio em combate (visual)
	if m and P.tem(m, "SangueGlacial") then m:SetAttribute("SangueGlacialFim", agora() + Cfg.passivas.SangueGlacial.combateJanela) end
end
local frost = {}                                                    -- [alvo] = {v, ultimo, congeladoAte, imuneAte, ws, pulo}
P.frost = frost
function P.vulnerabilidade(alvo)
	local f = frost[alvo]; if not f then return 1 end
	local F = Cfg.passivas.Frostbite; return 1 + F.vulnerabMax * f.v / F.max
end
local function aplicarLentidao(alvo, f)
	local h = alvo:FindFirstChildOfClass("Humanoid"); if not h then return end
	local F = Cfg.passivas.Frostbite
	if not f.ws then f.ws = h.WalkSpeed; f.pulo = h.UseJumpPower and h.JumpPower or h.JumpHeight end
	local congelado = (f.congeladoAte or 0) > os.clock()
	h.WalkSpeed = congelado and 0 or f.ws * (1 - F.lentidaoMax * f.v / F.max)
	if h.UseJumpPower then h.JumpPower = congelado and 0 or f.pulo else h.JumpHeight = congelado and 0 or f.pulo end
end
local function soltarFrost(alvo)
	local f = frost[alvo]; frost[alvo] = nil; if not f then return end
	local h = alvo.Parent and alvo:FindFirstChildOfClass("Humanoid")
	if h and f.ws then h.WalkSpeed = f.ws; if h.UseJumpPower then h.JumpPower = f.pulo else h.JumpHeight = f.pulo end end
	if alvo.Parent then alvo:SetAttribute("Frostbite", nil); alvo:SetAttribute("Congelado", nil) end
end
function P.aplicarFrostbite(fonte, alvo, qtd)
	if not (fonte and alvo and alvo.Parent) or not qtd or qtd <= 0 or not P.tem(fonte, "Frostbite") then return false end
	local F = Cfg.passivas.Frostbite
	if alvo:GetAttribute(F.imuneAtributo) or P.tem(alvo, "SangueGlacial") then return false end
	local f = frost[alvo]; if not f then f = {v = 0}; frost[alvo] = f end
	if (f.imuneAte or 0) > os.clock() then qtd *= 0.4 end            -- logo apos descongelar acumula mais devagar
	f.v = math.min(F.max, f.v + qtd); f.ultimo = os.clock()
	if f.v >= F.max and (f.imuneAte or 0) <= os.clock() then
		f.congeladoAte = os.clock() + F.congelaDur; f.imuneAte = f.congeladoAte + F.imuneCongelarPor
		alvo:SetAttribute("Congelado", agora() + F.congelaDur)
		if N then N.FX:FireAllClients({d = fonte, hab = "Frostbite", fase = "congelar", alvo = alvo, duracao = F.congelaDur, el = "Gelo"}) end
	end
	alvo:SetAttribute("Frostbite", math.floor(f.v))
	aplicarLentidao(alvo, f)
	return true
end
task.spawn(function()
	while true do
		local dt = task.wait(0.2)
		local F = Cfg.passivas.Frostbite; local t = os.clock()
		for alvo, f in pairs(frost) do
			if not alvo.Parent then frost[alvo] = nil
			else
				if f.congeladoAte and t >= f.congeladoAte then              -- descongela: volta a um acumulo medio
					f.congeladoAte = nil; f.v = math.min(f.v, F.aposCongelar); f.ultimo = t; alvo:SetAttribute("Congelado", nil)
				end
				if not f.congeladoAte and t - (f.ultimo or 0) > F.decaiApos then f.v -= F.decaiPorSeg * dt end
				local h = alvo:FindFirstChildOfClass("Humanoid")
				if f.v <= 0 or (h and h.Health <= 0) then soltarFrost(alvo)
				else alvo:SetAttribute("Frostbite", math.floor(f.v)); aplicarLentidao(alvo, f) end
			end
		end
	end
end)

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
P.intervaloMarca = {}                                              -- PATCH_SOPRO_UMBRAL: [fonte] = s, enquanto um jato continuo dura
function P.aplicarMarca(fonte, alvo)
	if not (fonte and alvo and alvo.Parent) or not P.tem(fonte, "MarcaSombria") then return false end
	local M_ = Cfg.passivas.MarcaSombria
	local t = marcas[alvo]; if not t then t = {}; marcas[alvo] = t end
	local e = t[fonte]; if not e then e = {n = 0}; t[fonte] = e end
	local iv = P.intervaloMarca[fonte]                              -- jato continuo: no maximo 1 marca por intervalo (renova a duracao)
	if iv and e.marcou and os.clock() - e.marcou < iv then e.ultimo = os.clock(); e.prox = nil; return false end
	e.n = math.min(M_.max, e.n + 1); e.ultimo = os.clock(); e.prox = nil; e.marcou = os.clock()
	atribMarca(alvo); return true
end
function P.consumirMarcas(fonte, alvo)                              -- Eclipse Draconico: zera as marcas desta origem; devolve quantas havia
	local n = P.marcasDe(fonte, alvo)
	if n > 0 then marcas[alvo][fonte] = nil; alvo:SetAttribute("MarcaSombria_" .. fonte.Name, nil); atribMarca(alvo) end   -- PATCH_ECLIPSE_DRACONICO: limpa o atributo da origem
	return n
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
return P

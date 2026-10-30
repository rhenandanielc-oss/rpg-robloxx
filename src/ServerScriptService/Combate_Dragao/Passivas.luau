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
return P

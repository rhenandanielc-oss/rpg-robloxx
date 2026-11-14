-- ToxinaFerrao (ModuleScript, ServerScriptService.Combate_Wyvern) — passiva TOXINA DO FERRAO da Wyvern. AUTORIDADE DO SERVIDOR.
-- Regras oficiais (RPG_02, ficha da Wyvern; kit aprovado pelo usuario 13/11/2026):
--  * intoxicacao biologica LEVE e inata (anatomia, NAO elemento: o dano dos ticks sai sem elemento, nao usa resistencias);
--  * a FERROADA aplica a toxina;
--  * novas ferroadas e ataques basicos RENOVAM o efeito sem multiplicar o dano: a Mordida so renova um alvo ja intoxicado,
--    nunca aplica; a renovacao devolve a duracao maxima, sem somar dano, com teto de duracao continua;
--  * antidotos e purificacao removem ou reduzem: T.remover(alvo) / T.reduzir(alvo, segundos) para os sistemas futuros
--    (nao ha antidoto no projeto ainda); atributo ImuneToxina = true no alvo bloqueia aplicacao e encerra a atual.
-- Uma intoxicacao por alvo e por fonte; ticks pelo caminho unico de dano do Nucleo (N.ferir com ehTick = true: nao gera
-- nova reacao/renovacao). Cada tick revalida o alvo (vivo, fora de zona segura, PvP para jogadores, guardiao derrotavel).
-- Cliente: atributo Intoxicado (hora do servidor do fim) para o efeito visual discreto.
-- Numeros PROVISORIOS (balanceamento): duracao, intervalo, dano por tick, teto.
local Players = game:GetService("Players")
local CfgC = require(game:GetService("ServerScriptService"):WaitForChild("Combate_Dragao"):WaitForChild("ConfigCombate"))
local T = {}
T.CONFIG = {
	formas = {Wyvern = true},
	aplicaCom = {Ferroada = true},           -- tipos de acerto que aplicam
	renovaCom = {Ferroada = true, Mordida = true, MordidaAerea = true},   -- basicos que renovam um alvo ja intoxicado
	duracao = 6, intervalo = 1.5, danoTick = 2,      -- PROVISORIO
	duracaoMaxTotal = 18,                    -- teto de uma intoxicacao continua (s) (PROVISORIO)
	imuneAtributo = "ImuneToxina",
}
local N                                      -- Nucleo (injetado em T.ligar)
function T.ligar(nucleo) N = nucleo end
local function agora() return workspace:GetServerTimeNow() end
local function forma(m) return m and m:GetAttribute("FormaRegional") end
function T.tem(m) return T.CONFIG.formas[forma(m) or ""] == true end

local tox = {}                               -- [alvo] = {[fonte] = {fim, prox, inicio, renov}}
T.ativas = tox
local CS = game:GetService("CollectionService")
T.TAG = "ToxinaFerrao_Alvo"                  -- o cliente acompanha so os alvos com esta tag (sem varrer o Workspace)
local function marcar(alvo)
	local fim = 0
	for _, q in pairs(tox[alvo] or {}) do fim = math.max(fim, q.fim) end
	alvo:SetAttribute("Intoxicado", fim > 0 and fim or nil)
	if fim > 0 then CS:AddTag(alvo, T.TAG) else CS:RemoveTag(alvo, T.TAG) end
end
local function encerrar(alvo, fonte)
	local pf = tox[alvo]; if not pf then return end
	if fonte then pf[fonte] = nil else tox[alvo] = nil end
	if tox[alvo] and next(tox[alvo]) == nil then tox[alvo] = nil end
	if alvo.Parent then marcar(alvo) end
end

-- chamado pelo Nucleo depois de um acerto (nao tick) que causou dano
function T.aoAcertar(fonte, alvo, tipo)
	if not (fonte and alvo and alvo.Parent) or not T.tem(fonte) then return false end
	local C = T.CONFIG
	if alvo:GetAttribute(C.imuneAtributo) then return false end
	local pf = tox[alvo]; local q = pf and pf[fonte]; local t = agora()
	local ativa = q and q.fim > t
	if ativa then
		if not C.renovaCom[tipo] then return false end
		q.renov += 1
		q.fim = math.min(t + C.duracao, q.inicio + C.duracaoMaxTotal)   -- renova sem somar dano; teto continuo
	else
		if not C.aplicaCom[tipo] then return false end                  -- Mordida nao aplica
		pf = pf or {}; tox[alvo] = pf
		pf[fonte] = {fim = t + C.duracao, prox = t + C.intervalo, inicio = t, renov = 0}
	end
	marcar(alvo)
	return true
end
-- antidoto / purificacao (sistemas futuros): remove tudo ou reduz a duracao restante
function T.remover(alvo) encerrar(alvo, nil); return true end
function T.reduzir(alvo, s)
	for _, q in pairs(tox[alvo] or {}) do q.fim -= s end
	marcar(alvo); return true
end

local function aindaValido(fonte, alvo)
	if not (alvo.Parent and fonte.Parent) then return false end
	if alvo:GetAttribute(T.CONFIG.imuneAtributo) then return false end
	local r = alvo:FindFirstChild("HumanoidRootPart") or alvo.PrimaryPart; if not r then return false end
	if N and N.emZonaSegura(r.Position) then return false end
	local h = alvo:FindFirstChildOfClass("Humanoid")
	if h then
		if h.Health <= 0 then return false end
		local plr = Players:GetPlayerFromCharacter(alvo); local dono = fonte:GetAttribute("DonoUserId")
		if plr and dono and (plr.UserId == dono or workspace:GetAttribute(CfgC.pvpAtivoAtributo) ~= true) then return false end
		return true
	end
	return alvo:GetAttribute("GuardiaoNinho") ~= nil and not alvo:GetAttribute("Incapacitado")
end
task.spawn(function()
	while true do
		task.wait(0.25)
		local t = agora(); local C = T.CONFIG
		for alvo, pf in pairs(tox) do
			for fonte, q in pairs(pf) do
				if q.fim <= t or not aindaValido(fonte, alvo) then encerrar(alvo, fonte)
				elseif t >= q.prox then
					q.prox += C.intervalo
					if N and C.danoTick > 0 then N.ferir(fonte, alvo, C.danoTick, nil, "Toxina", "leve", true) end
				end
			end
		end
	end
end)
return T

-- IA_FaunaFloresta/Anim - adaptador de animacao do piloto. Monta o KeyframeSequence pelo AdaptadorFauna
-- (ReplicatedStorage.FaunaFloresta) e registra com AnimationClipProvider (id temporario, so no Studio; nada publicado).
-- base = laco (locomocao/repouso, troca com fade); acao = clipe unico por cima. Falha de carga e registrada, nunca silenciada.
local ACP = game:GetService("AnimationClipProvider")
local RS = game:GetService("ReplicatedStorage")
local Fab = require(RS:WaitForChild("FaunaFloresta"):WaitForChild("AdaptadorFauna"))
local Perfis = require(script.Parent:WaitForChild("Perfis"))

local A = {}
A.__index = A
local ids = {}            -- [especie..nome] = id registrado (compartilhado entre exemplares da mesma especie)
A.falhas = {}

local function idDe(especie, modelo, nome)
	local k = especie .. "_" .. nome
	if ids[k] == nil then
		local Ad = Fab.para(especie); Ad.forcarConvencao = true     -- convencao nova medida 16/11 (erro <= 0,005 stud)
		local ok, res = pcall(function()
			local kfs = Ad.montar(modelo, nome)
			return ACP:RegisterAnimationClip(kfs)
		end)
		if ok then ids[k] = res else ids[k] = false; table.insert(A.falhas, k .. ": " .. tostring(res)); warn("[FaunaIA] clipe falhou", k, res) end
	end
	return ids[k] or nil
end

local porModelo = setmetatable({}, { __mode = "k" })   -- reaproveita as faixas ao reiniciar (limite de faixas do Animator)
function A.novo(modelo, especie)
	if porModelo[modelo] then local s = porModelo[modelo]; s:pararTudo(0.1); return s end
	local self = setmetatable({}, A)
	porModelo[modelo] = self
	self.m, self.especie = modelo, especie
	local ac = modelo:FindFirstChildOfClass("AnimationController") or Instance.new("AnimationController", modelo)
	self.an = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
	self.faixas = {}
	self.Ad = Fab.para(especie)
	return self
end

function A:faixa(nome)
	local f = self.faixas[nome]
	if f == nil then
		local id = idDe(self.especie, self.m, nome)
		if not id then self.faixas[nome] = false; return nil end
		local a = Instance.new("Animation"); a.AnimationId = id
		f = self.an:LoadAnimation(a); self.faixas[nome] = f
	end
	return f or nil
end

function A:duracao(nome) local c = self.Ad.clipe(nome); return (c.quadros - (c.loop and 0 or 1)) / c.fps end

function A:preCarregar(lista) for _, n in ipairs(lista) do self:faixa(n); task.wait() end end

-- laco base (repouso/locomocao). vel = AdjustSpeed
function A:base(nome, fade, vel)
	local f = self:faixa(nome); if not f then return nil end
	if self.baseNome ~= nome then
		local old = self.baseNome and self.faixas[self.baseNome]
		f:Play(fade or 0.25); self.baseNome = nome
		if old and old ~= f then old:Stop(fade or 0.25) end
	end
	f:AdjustSpeed(vel or 1)
	return f
end

-- clipe unico por cima da base
function A:acao(nome, fade, vel)
	self:pararAcao(fade)
	local f = self:faixa(nome); if not f then return nil end
	f:Play(fade or 0.15); f:AdjustSpeed(vel or 1); self.acaoNome = nome
	return f
end
-- clipe PARCIAL por cima de tudo (ex.: Chifrada, Action2): nao ocupa o lugar da acao, entao a troca de estado nao o corta
function A:sobre(nome, fade, vel)
	local f = self:faixa(nome); if not f then return nil end
	f:Play(fade or 0.08); f:AdjustSpeed(vel or 1)
	return f
end
function A:pararAcao(fade)
	local f = self.acaoNome and self.faixas[self.acaoNome]
	if f and f.IsPlaying then f:Stop(fade or 0.15) end
	self.acaoNome = nil
end
function A:pararTudo(fade)
	for _, f in pairs(self.faixas) do if f then f:Stop(fade or 0.2) end end
	self.baseNome, self.acaoNome = nil, nil
end

-- v_perfil do clipe (m/s do Blender) no tempo t; nil se o clipe nao tem perfil
function A:perfil(nome, t)
	local p = Perfis[self.especie] and Perfis[self.especie][nome]
	if not p then return nil end
	local x = math.clamp(t * 30, 0, #p - 1)
	local i = math.floor(x); local f = x - i
	return p[i + 1] + ((p[math.min(i + 2, #p)]) - p[i + 1]) * f
end

return A

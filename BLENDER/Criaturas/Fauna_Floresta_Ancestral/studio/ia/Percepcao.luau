-- IA_FaunaFloresta/Percepcao - escolhe o alvo (jogador vivo, ou alvo falso de teste com a tag em DEBUG) com
-- frequencia limitada, linha de visao e histerese: entra no alerta em raioAlerta, sai so acima de raioSairAlerta;
-- troca de alvo so se o novo estiver 25% mais perto (disputa entre dois jogadores sem alternar).
local Players = game:GetService("Players")
local CS = game:GetService("CollectionService")
local Config = require(script.Parent:WaitForChild("Config"))

local P = {}
P.__index = P

local function raizDe(inst)
	if inst:IsA("Model") then
		local h = inst:FindFirstChildOfClass("Humanoid")
		if h and h.Health <= 0 then return nil end
		return inst:FindFirstChild("HumanoidRootPart") or inst.PrimaryPart
	end
	return inst:IsA("BasePart") and inst or nil
end

function P.alvos()
	local r = {}
	for _, pl in ipairs(Players:GetPlayers()) do
		local c = pl.Character; local hrp = c and raizDe(c)
		if hrp and hrp:IsDescendantOf(workspace) then table.insert(r, { inst = c, parte = hrp, nome = pl.Name }) end
	end
	if Config.DEBUG then
		for _, t in ipairs(CS:GetTagged(Config.TAG_ALVO_TESTE)) do
			local p = raizDe(t)
			if p and p:IsDescendantOf(workspace) then table.insert(r, { inst = t, parte = p, nome = t.Name }) end
		end
	end
	return r
end

function P.novo(modelo, cfg)
	local self = setmetatable({}, P)
	self.m, self.cfg = modelo, cfg.percepcao
	self.rp = RaycastParams.new(); self.rp.FilterType = Enum.RaycastFilterType.Exclude
	self.ultimo = -1e9; self.alvo = nil; self.dist = math.huge; self.leituras = 0
	return self
end

function P:olhos()
	local pv = self.m:GetPivot()
	return pv.Position + Vector3.new(0, self.cfg.alturaOlhos * self.m:GetScale(), 0)
end

function P:visivel(a, origem)
	self.rp.FilterDescendantsInstances = { self.m, a.inst }
	local d = a.parte.Position - origem
	local hit = workspace:Raycast(origem, d, self.rp)
	return hit == nil
end

-- atualiza no maximo a cada 'intervalo'; devolve alvo atual (tabela) e distancia
function P:atualizar(agora)
	if agora - self.ultimo < self.cfg.intervalo then return self.alvo, self.dist end
	self.ultimo = agora; self.leituras += 1
	local o = self:olhos()
	local melhor, dMelhor = nil, math.huge
	local atual, dAtual = nil, math.huge
	for _, a in ipairs(P.alvos()) do
		local d = (a.parte.Position - o).Magnitude
		if d <= self.cfg.raioSairAlerta and self:visivel(a, o) then
			if self.alvo and a.inst == self.alvo.inst then atual, dAtual = a, d end
			if d < dMelhor then melhor, dMelhor = a, d end
		end
	end
	if atual and not (melhor and dMelhor < dAtual * 0.75) then melhor, dMelhor = atual, dAtual end
	-- sem alvo atual: so adota novo dentro do raioAlerta (histerese de entrada)
	if not self.alvo and melhor and dMelhor > self.cfg.raioAlerta then melhor, dMelhor = nil, math.huge end
	self.alvo, self.dist = melhor, dMelhor
	return self.alvo, self.dist
end

return P

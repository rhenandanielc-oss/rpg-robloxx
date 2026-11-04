-- RastroBreu_Servidor (Script, ServerScriptService) — passiva RASTRO DO BREU do Dragao Sombrio (aprovada pelo usuario
-- em 03/11/2026; ver DOCS/criaturas/dragao-sombrio.md §5).
--  * MODO EXPLORACAO: fora de combate, depois de correr (chao) ou voar continuamente por tempoAtiva segundos, ganha um
--    impulso de velocidade; ao cair abaixo do limiar (parar/andar devagar) o impulso some e a contagem recomeca;
--    curvas NAO zeram a contagem enquanto a velocidade se mantem (o usuario nao deu regra de penalidade por curva).
--  * MODO COMBATE: ao PERSEGUIR um inimigo com Marca Sombria aplicada por ESTE Sombrio (Passivas.marcas): o alvo esta a
--    frente (cone em relacao ao rumo), dentro do alcance, e a distancia esta diminuindo. Fugir de um alvo marcado, ou
--    marcas so de outro dragao, nao dao bonus. Termina ao deixar de perseguir ou quando as marcas acabam (inclusive se
--    forem consumidas). Com varios marcados, vale o mais alinhado.
--  * Os bonus NAO se somam: vale o maior (combate tem prioridade). Ticks de dano nao mexem na velocidade.
--  * O servidor decide tudo e publica atributos; a montaria aplica RastroBonus na velocidade-ALVO (nunca na aceleracao
--    nem nas velocidades compartilhadas) e o cliente desenha os rastros (RastroBreu_Cliente).
-- Atributos: RastroModo ("exploracao" | "combate" | nil), RastroBonus, RastroCarga (0..1, progresso da exploracao),
-- RastroAlvo (nome do alvo perseguido, depuracao). Por enquanto so com o dragao MONTADO.
-- NUMEROS NAO_APROVADO (prototipo, pendentes de balanceamento).
local RunService = game:GetService("RunService")
local Cfg = require(game:GetService("ReplicatedStorage"):WaitForChild("Montaria_Dragoes"):WaitForChild("ConfigMontaria"))
local Passivas = require(script.Parent:WaitForChild("Combate_Dragao"):WaitForChild("Passivas"))

local P = {                                   -- NAO_APROVADO
	formas = {Sombrio = true},                -- so formas com a passiva
	tempoAtiva = 4,                           -- s de movimento continuo ate o impulso de exploracao
	bonusExploracao = 0.15,                   -- +15% na velocidade-alvo
	bonusCombate = 0.20,                      -- +20% perseguindo alvo com marca propria
	alcanceCombate = 150,                     -- studs
	coneCombate = 35,                         -- graus em relacao ao rumo
	limiarVoo = 0.8,                          -- fracao de Cfg.vooVel que conta como "voando" (ar)
	folgaChao = 2,                            -- acima de VelAndar + folga conta como "correndo" (chao)
	combateJanela = 6,                        -- s depois do ultimo dano causado/recebido = "em combate"
	passo = 0.1,                              -- s entre avaliacoes
}

local estado = {}                             -- [modelo] = {t = s acumulados, dist = {[alvo] = distancia anterior}}
local function emMovimento(m)
	local v = m:GetAttribute("Velocidade") or 0
	local modo = m:GetAttribute("MontariaModo")
	if modo == "chao" then return v > (m:GetAttribute("VelAndar") or Cfg.andarVel) + P.folgaChao end
	if modo == "voo" then return v >= Cfg.vooVel * P.limiarVoo end
	if modo == "decolando" or modo == "pousando" then return nil end      -- transicao: nao soma nem zera
	return false
end
local function emCombate(m)
	if m:GetAttribute("EmAtaque") then return true end
	local u = m:GetAttribute("UltimoCombate")
	return u ~= nil and workspace:GetServerTimeNow() - u < P.combateJanela
end
local function raiz(a) return a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart end
local function perseguindo(m, s)
	if (m:GetAttribute("Velocidade") or 0) < 3 then s.dist = {}; return nil end
	local p = m:GetPivot(); local rumo = p.LookVector
	local melhor, melhorAng
	local dist = {}
	for _, alvo in ipairs(Passivas.alvosMarcados(m)) do
		local r = raiz(alvo)
		if r then
			local v = r.Position - p.Position; local d = v.Magnitude
			dist[alvo] = d
			if d <= P.alcanceCombate and d > 1 then
				local ang = math.deg(math.acos(math.clamp(rumo:Dot(v.Unit), -1, 1)))
				local fecha = s.dist[alvo] == nil or d < s.dist[alvo] - 0.05
				if ang <= P.coneCombate and fecha and (not melhorAng or ang < melhorAng) then melhor, melhorAng = alvo, ang end
			end
		end
	end
	s.dist = dist
	return melhor
end
local function limpar(m)
	estado[m] = nil
	if m.Parent then for _, k in ipairs({"RastroModo", "RastroBonus", "RastroCarga", "RastroAlvo"}) do m:SetAttribute(k, nil) end end
end
local function por(m, k, v) if m:GetAttribute(k) ~= v then m:SetAttribute(k, v) end end

local acum = 0
RunService.Heartbeat:Connect(function(dt)
	acum += dt; if acum < P.passo then return end
	local d = acum; acum = 0
	for m, _ in pairs(estado) do if not m.Parent or not m:GetAttribute("Controlador") then limpar(m) end end
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and P.formas[m:GetAttribute("FormaRegional") or ""] and m:GetAttribute("Controlador") then
			local s = estado[m] or {t = 0, dist = {}}; estado[m] = s
			local combate = emCombate(m)
			-- exploracao: so fora de combate
			local mov = emMovimento(m)
			if mov == true and not combate then s.t += d
			elseif mov == false or combate then s.t = 0 end
			-- combate: perseguicao de alvo com marca propria (independe do tempo de corrida)
			local alvo = perseguindo(m, s)
			local modo, bonus
			if alvo then modo, bonus = "combate", P.bonusCombate
			elseif s.t >= P.tempoAtiva then modo, bonus = "exploracao", P.bonusExploracao end
			por(m, "RastroModo", modo); por(m, "RastroBonus", bonus); por(m, "RastroAlvo", alvo and alvo.Name or nil)
			por(m, "RastroCarga", s.t > 0 and math.floor(math.min(1, s.t / P.tempoAtiva) * 10 + 0.5) / 10 or nil)
		end
	end
end)

-- OlhosCrocodilo_Cliente (LocalScript em StarterPlayerScripts) - O1, 17/11 [PROPOSTA]. SO VISUAL (cada cliente desenha):
-- * olhar: escolhe o alvo (atributo "AlvoOlhar" do modelo, Vector3, se o servidor definir; senao o boneco/jogador mais
--   perto a frente), gira o globo (OlhoE/OlhoD) em ~0,08 s (sacada) e segura com micro-sacadas. O alvo e calculado no
--   referencial da CABECA a cada quadro: quando a cabeca (clipes) vira para o alvo, o olho volta sozinho ao centro =
--   o olho guia a cabeca. Sem alvo: olhadas de lado ocasionais.
-- * piscada irregular: intervalo 2,5-7 s, as vezes dupla; fecha 0,08 s, segura 0,03, abre 0,19.
-- * entrar na agua (atributo Submerso vira true): fecha rapido (0,07), segura ate 0,45 s, reabre ja submerso.
-- Ossos do rig O1 (34): OlhoE/D, PalpebraSupE/D, PalpebraInfE/D. Convencao giro180y: frente do olho = +Y do osso;
-- fechar = Sup +22 graus e Inf -17 graus no X do osso (no Blender, -22 / +17). Os clipes de corpo nao gravam estes ossos.
local RS = game:GetService("RunService")
local T = workspace:WaitForChild("Teste_Crocodilo")
local FECHA_SUP, FECHA_INF = math.rad(22), math.rad(-17)
local OLHAR_MAX = math.rad(22)         -- giro maximo do globo (a borda do globo nao aparece ate ~25 graus)
local ALCANCE, CONE = 45, math.rad(110)   -- olhos laterais: alvo bem a frente fica a ~76 graus do eixo de cada olho
                                          -- (com 75 o olho alternava 0/22 graus); ate 110 os dois convergem para a frente

local estado = nil
local function preparar(croc)
	local function b(n) return croc:FindFirstChild(n, true) end
	if not (b("OlhoE") and b("PalpebraSupE")) then return nil end
	return {croc = croc, cab = b("Cabeca"),
		olho = {b("OlhoE"), b("OlhoD")}, sup = {b("PalpebraSupE"), b("PalpebraSupD")}, inf = {b("PalpebraInfE"), b("PalpebraInfD")},
		proxPisca = os.clock() + 1.5, piscaIni = -1, aguaIni = -1, sub = croc:GetAttribute("Submerso") == true,
		olharAtual = {Vector3.yAxis, Vector3.yAxis}, micro = Vector3.zero, proxMicro = 0, desvio = Vector3.zero, proxDesvio = os.clock() + 3}
end

local function curvaPisca(t)                     -- 0..1 fechamento
	if t < 0 then return 0 end
	if t < 0.08 then return t / 0.08 end
	if t < 0.11 then return 1 end
	if t < 0.30 then local u = (t - 0.11) / 0.19; return 1 - u * u * (3 - 2 * u) end
	return 0
end
local function curvaAgua(t)
	if t < 0 then return 0 end
	if t < 0.07 then return t / 0.07 end
	if t < 0.45 then return 1 end
	if t < 0.80 then local u = (t - 0.45) / 0.35; return 1 - u * u * (3 - 2 * u) end
	return 0
end

local function alvo(e)
	local a = e.croc:GetAttribute("AlvoOlhar")
	if typeof(a) == "Vector3" then return a end
	local cabCF = e.cab.TransformedWorldCFrame
	local melhor, dm = nil, ALCANCE
	local cands = {}
	local arena = T:FindFirstChild("Arena")
	if arena then for _, m in ipairs(arena:GetChildren()) do if m:IsA("Model") then table.insert(cands, m) end end end
	for _, p in ipairs(game.Players:GetPlayers()) do if p.Character then table.insert(cands, p.Character) end end
	for _, m in ipairs(cands) do
		local ok, cf = pcall(function() return m:GetPivot() end)
		if ok then
			local d = cf.Position - cabCF.Position
			local visto = false                                     -- dentro do campo de visao de algum olho (repouso)
			for _, o in ipairs(e.olho) do
				local base = o.TransformedWorldCFrame * o.Transform:Inverse()
				if base:VectorToObjectSpace(cf.Position - base.Position).Unit.Y > math.cos(CONE) then visto = true end
			end
			if visto and d.Magnitude < dm then melhor, dm = cf.Position + Vector3.new(0, 1.5, 0), d.Magnitude end
		end
	end
	return melhor
end

local function girarPara(osso, dirLocal)        -- rotacao do +Y do osso ate dirLocal, limitada
	local y = Vector3.yAxis
	local ang = math.acos(math.clamp(y:Dot(dirLocal), -1, 1))
	if ang < 1e-4 then return CFrame.identity end
	local eixo = y:Cross(dirLocal).Unit
	return CFrame.fromAxisAngle(eixo, math.min(ang, OLHAR_MAX))
end

-- PreSimulation (depois do passo do Animator): o Animator devolve ao repouso, a cada quadro, os ossos que nenhum
-- clipe grava; ajustar aqui faz o valor valer ate o render (no RenderStepped ele era zerado antes de valer).
RS.PreSimulation:Connect(function(dt)
	local croc = T:FindFirstChild("Crocodilo_Primordial")
	if not croc then estado = nil; return end
	if not estado or estado.croc ~= croc then estado = preparar(croc); if not estado then return end end
	local e, agora = estado, os.clock()
	-- piscada irregular
	if agora >= e.proxPisca then
		e.piscaIni = agora
		e.proxPisca = agora + (math.random() < 0.15 and 0.42 or (2.5 + math.random() * 4.5))
	end
	-- entrar na agua
	local sub = croc:GetAttribute("Submerso") == true
	if sub and not e.sub then e.aguaIni = agora end
	e.sub = sub
	local f = math.max(curvaPisca(agora - e.piscaIni), curvaAgua(agora - e.aguaIni))
	-- olhar
	local p = alvo(e)
	if agora >= e.proxMicro then
		e.micro = Vector3.new(math.random() - 0.5, 0, math.random() - 0.5) * 0.05; e.proxMicro = agora + 0.3 + math.random() * 0.5
	end
	if not p and agora >= e.proxDesvio then
		e.desvio = (math.random() < 0.5) and Vector3.zero or Vector3.new((math.random() - 0.5) * 0.7, 0, (math.random() - 0.5) * 0.25)
		e.proxDesvio = agora + 2 + math.random() * 3
	end
	for i = 1, 2 do
		local o = e.olho[i]
		o.Transform = CFrame.identity
		local base = o.TransformedWorldCFrame                       -- referencial de repouso do olho (segue a cabeca)
		local dir
		if p then
			local alcance = base:VectorToObjectSpace((p - base.Position)).Unit
			local frontal = alcance.Y > math.cos(CONE)
			dir = frontal and (alcance + e.micro).Unit or Vector3.yAxis
		else
			dir = (Vector3.yAxis + e.desvio).Unit
		end
		-- sacada: aproxima rapido (constante ~0,03 s)
		local k = 1 - math.exp(-dt / 0.03)
		e.olharAtual[i] = e.olharAtual[i]:Lerp(dir, k).Unit
		o.Transform = girarPara(o, e.olharAtual[i])
		e.sup[i].Transform = CFrame.Angles(FECHA_SUP * f, 0, 0)
		e.inf[i].Transform = CFrame.Angles(FECHA_INF * f, 0, 0)
	end
end)

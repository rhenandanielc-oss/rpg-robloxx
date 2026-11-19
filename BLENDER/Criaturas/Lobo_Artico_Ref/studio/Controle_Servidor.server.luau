-- Controle_Servidor (Script, Workspace.Teste_LoboArtico) - CONTROLADOR DE ENSAIO do Lobo Artico (usuario 16/11/2026:
-- "Controlador do lobo"). AUTORIDADE DO SERVIDOR: o cliente so manda a intencao (direcao no plano + marcha pedida); o
-- servidor decide marcha, transicoes, giro, chao e velocidade, e move o modelo por PivotTo (RootPart ancorada).
-- Nao e a montaria oficial (sela leve a partir do Adulto ainda nao existe) nem a IA: e a camada de locomocao que os dois
-- vao usar, testada com um jogador "assumindo" o lobo no place isolado.
-- Marchas (velocidades do proprio clipe, patas casadas): Andar 3,0 / Trote 6,667 / Corrida 20,357 studs/s, vezes
-- MultVelocidade (Uivo: 1,15) com o clipe tocado no mesmo ritmo. (A PROPOSTA 24.2 de 35 studs/s NAO esta aprovada.)
-- Trocas de marcha sempre pelos clipes aprovados, com o deslocamento do Blender (Movimento_LoboArtico) quadro a quadro:
--   parado -> Andar (fade; nao ha clipe RepousoParaAndar) | parado + correr -> Arrancada -> Corrida
--   Andar <-> Trote (AndarParaTrote / TroteParaAndar) | Trote <-> Corrida (TroteParaCorrida / CorridaParaTrote)
--   Corrida sem direcao -> Frenagem -> parado | Andar sem direcao -> fade para Repouso (desliza: falta AndarParaRepouso)
--   parado com direcao a mais de 60 graus -> VirarEsquerda/VirarDireita (90 graus no lugar)
-- Giro andando (PROVISORIO): Andar 60, Trote 70, Corrida 45 graus/s. Sem chao a frente: para (nao anda no ar).
-- Esquiva: o lobo ainda nao tem sistema de esquiva; MultEsquiva so e lido para o HUD/teste.
-- Falhas tratadas: intencao velha (>0,6 s sem pacote) = soltar o comando; jogador sai = solta e o lobo freia; pacote
-- invalido/rapido demais e ignorado; Uivo (atributo Parado) freia antes e bloqueia o movimento.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local KSP = game:GetService("KeyframeSequenceProvider")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local lib = game:GetService("ReplicatedStorage"):WaitForChild("Animacoes_LoboArtico")
local Mov = require(lib:WaitForChild("Movimento_LoboArtico"))

local CFG = {
	giro = {Andar = 60, Trote = 70, Corrida = 45},       -- graus/s andando (PROVISORIO)
	anguloVirar = 60,                                     -- parado: acima disso vira no lugar com o clipe
	alcanceAssumir = 25,                                  -- studs do personagem ao lobo para assumir
	pacoteVelho = 0.6, pacotesPorSeg = 30,
	fade = 0.25,
}
-- r4 (18/11, idades): Escala (Idade_Servidor) encolhe/aumenta o corpo; o deslocamento dos clipes de transicao e o
-- apoio a frente acompanham a escala.
-- r5 (19/11, pedido "prossiga" sobre a velocidade do filhote): a velocidade da idade passa a ser RELATIVA AO TAMANHO.
-- O clipe toca a MultVelocidade (Filhote 1,15 = passada 15% mais rapida) e o deslocamento e o do clipe x Escala x mult:
-- patas casadas sem o clipe a 2,9x. Filhote: 0,40 x 1,15 = 46% dos studs/s do Adulto. Copia da r4: Controle_Servidor_r4.
local function esc() return lobo:GetAttribute("Escala") or 1 end
local function ritmoDe(mult) return mult end
local ORDEM = {"Andar", "Trote", "Corrida"}
local SUBIR = {Andar = "AndarParaTrote", Trote = "TroteParaCorrida"}
local DESCER = {Trote = "TroteParaAndar", Corrida = "CorridaParaTrote"}
local MARCHA_PEDIDA = {andar = "Andar", trote = "Trote", correr = "Corrida"}

local rede = pasta:FindFirstChild("Rede_Controle") or Instance.new("RemoteEvent")
rede.Name = "Rede_Controle"; rede.Parent = pasta

-- faixas (o controlador e dono de Repouso/locomocao; Uivo_Servidor toca as do Uivo com prioridade Action)
local animator = lobo.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", lobo.AnimationController)
local faixas = {}
local function faixa(n)
	if not faixas[n] then
		local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib["LoboArtico_" .. n])
		faixas[n] = animator:LoadAnimation(a)
	end
	return faixas[n]
end
for _, n in ipairs({"Repouso", "Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "AndarParaTrote", "TroteParaAndar",
	"TroteParaCorrida", "CorridaParaTrote", "VirarEsquerda", "VirarDireita"}) do faixa(n) end
local tocando
local function tocar(n, ritmo, fade)
	fade = fade or CFG.fade
	local f = faixa(n)
	if tocando ~= n then
		for nome, t in pairs(faixas) do if nome ~= n and t.IsPlaying then t:Stop(fade) end end
		f:Play(fade, 1, ritmo or 1); tocando = n
	end
	f:AdjustSpeed(ritmo or 1)
	return f
end

-- chao
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.IgnoreWater = true
local function chao(p)
	local lista = {lobo}
	for _, j in ipairs(Players:GetPlayers()) do if j.Character then table.insert(lista, j.Character) end end
	rp.FilterDescendantsInstances = lista
	for _, h in ipairs({4, 10}) do
		local r = workspace:Raycast(p + Vector3.new(0, h, 0), Vector3.new(0, -(h + 6), 0), rp)
		if r then return r.Position.Y end
	end
	return nil
end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function angulo(a, b) return math.atan2(a.Z * b.X - a.X * b.Z, a.X * b.X + a.Z * b.Z) end   -- + = esquerda

-- estado
local E = {modo = "Parado", marcha = nil, clipe = nil, base = nil, destino = nil, frear = false}
local ctrl = {jogador = nil, dir = Vector3.zero, marcha = "Trote", t = 0, n = 0, janela = 0}
local function publicar()
	lobo:SetAttribute("CtrlModo", E.modo); lobo:SetAttribute("CtrlMarcha", E.marcha or "")
	lobo:SetAttribute("CtrlClipe", E.clipe or "")
end
local function soltar(motivo)
	local j = ctrl.jogador
	if j and j.Character and j.Character:FindFirstChild("HumanoidRootPart") then j.Character.HumanoidRootPart.Anchored = false end
	ctrl.jogador = nil; ctrl.dir = Vector3.zero
	lobo:SetAttribute("Controlador", 0); lobo:SetAttribute("CtrlSoltoPor", motivo or "")
end

local function curva(nome, t)                     -- posicao/giro do clipe no tempo t (interpola quadros a 30 fps)
	local c = Mov.Curvas[nome]; local q = math.clamp(t * Mov.Fps, 0, #c - 1)
	local i = math.floor(q); local f = q - i
	local a = c[i + 1]; local b = c[math.min(i + 2, #c)]
	local e = esc()
	return (a[1] + (b[1] - a[1]) * f) * e, (a[2] + (b[2] - a[2]) * f) * e, a[3] + (b[3] - a[3]) * f
end

local function iniciarClipe(nome, destino, ritmo)
	E.modo = "Clipe"; E.clipe = nome; E.destino = destino; E.base = lobo:GetPivot()
	tocando = nil                                   -- o mesmo clipe duas vezes seguidas (Virar, Virar) precisa recomecar
	tocar(nome, ritmo, 0.15).TimePosition = 0
	publicar()
end
local function entrarLaco(m) E.modo = "Laco"; E.marcha = m; E.clipe = nil; tocar(m, ritmoDe(lobo:GetAttribute("MultVelocidade") or 1)); publicar() end
local function entrarParado(fade) E.modo = "Parado"; E.marcha = nil; E.clipe = nil; tocar("Repouso", 1, fade); publicar() end

local FRENTE_PATAS = 4.5                           -- patas dianteiras ~3,9 a frente do pivo (rest_v41) + folga
local function temChao(cf)                         -- pivo E a frente das patas dianteiras
	return chao(cf.Position) ~= nil and chao(cf.Position + plano(cf.LookVector).Unit * FRENTE_PATAS * esc()) ~= nil
end
local function moverPara(cf, soPivo)              -- aplica com o chao; false se nao ha chao (nao anda no ar)
	local y = chao(cf.Position)
	if not y or (not soPivo and not temChao(cf)) then return false end
	local atual = lobo:GetPivot().Position.Y
	local ny = atual + math.clamp(y - atual, -0.6, 0.6)
	lobo:PivotTo(CFrame.new(cf.Position.X, ny, cf.Position.Z) * cf.Rotation)
	return true
end

entrarParado(0)
lobo:SetAttribute("Controlador", 0); lobo:SetAttribute("VelAtual", 0)

RunService.Heartbeat:Connect(function(dt)
	-- r3 (16/11, kit): durante um poder que move o lobo (Cometa, Avalanche) o Kit_Servidor e dono do movimento e das
	-- faixas; o controlador so espera e, ao voltar, retoma do Repouso
	if lobo:GetAttribute("PoderAtivo") then
		if E.modo ~= "Pausado" then E.modo = "Pausado"; E.clipe = nil; tocando = nil
			for _, t in pairs(faixas) do if t.IsPlaying then t:Stop(0.15) end end end
		lobo:SetAttribute("VelAtual", lobo:GetAttribute("VelPoder") or 0)
		return
	elseif E.modo == "Pausado" then
		entrarParado(0.2)
	end
	local mult = lobo:GetAttribute("MultVelocidade") or 1
	local agora = os.clock()
	-- intencao valida (Uivo/Parado, pacote velho ou sem controlador = sem direcao)
	local dir = ctrl.dir
	if not ctrl.jogador or agora - ctrl.t > CFG.pacoteVelho or lobo:GetAttribute("Parado") or E.frear then dir = Vector3.zero end
	if lobo:GetAttribute("Parado") and E.modo ~= "Parado" and E.modo ~= "Clipe" then
		-- Uivo comecou com o lobo andando (nao deveria: o servidor do Uivo recusa em movimento) -> para ja
		entrarParado(0.2)
	end
	local pedida = MARCHA_PEDIDA[ctrl.marcha] or "Trote"
	local pv = lobo:GetPivot()
	local frente = plano(pv.LookVector).Unit
	local vel = 0

	if E.modo == "Clipe" then
		local f = faixas[E.clipe]
		f:AdjustSpeed((E.clipe == "VirarEsquerda" or E.clipe == "VirarDireita") and 1 or ritmoDe(mult))
		local len = (#Mov.Curvas[E.clipe] - 1) / Mov.Fps
		local t = f.IsPlaying and f.TimePosition or len
		local dx, dz, g = curva(E.clipe, t)
		local alvo = E.base * CFrame.new(dx, 0, dz) * CFrame.Angles(0, g, 0)
		local x0, z0 = curva(E.clipe, math.max(0, t - dt))
		vel = (Vector3.new(dx, 0, dz) - Vector3.new(x0, 0, z0)).Magnitude / math.max(dt, 1e-3) * mult
		local girando = (E.clipe == "VirarEsquerda" or E.clipe == "VirarDireita")   -- vira no lugar: so o pivo precisa de chao
		if not moverPara(alvo, girando) then entrarParado(0.2); lobo:SetAttribute("CtrlBloqueio", "sem chao @" .. string.format("%.1f", agora)) end
		if E.modo == "Clipe" and (t >= len - 0.02 or not f.IsPlaying) then
			if E.destino then entrarLaco(E.destino) else entrarParado(0.2) end
		end
	elseif E.modo == "Parado" then
		if dir.Magnitude > 0.1 then
			local a = angulo(frente, dir)
			if math.abs(a) > math.rad(CFG.anguloVirar) then
				iniciarClipe(a > 0 and "VirarEsquerda" or "VirarDireita", nil, 1)
			elseif not temChao(pv * CFrame.new(0, 0, -1)) then
				-- r2: sem chao a frente fica parado (antes alternava Parado/Andar a cada quadro na borda)
				lobo:SetAttribute("CtrlBloqueio", "sem chao a frente @" .. string.format("%.1f", agora))
			elseif pedida == "Corrida" then
				iniciarClipe("Arrancada", "Corrida", ritmoDe(mult))
			else
				entrarLaco("Andar")
			end
		end
	elseif E.modo == "Laco" then
		local m = E.marcha
		if dir.Magnitude < 0.1 then
			if m == "Corrida" then iniciarClipe("Frenagem", nil, ritmoDe(mult))
			elseif m == "Trote" then iniciarClipe("TroteParaAndar", "Andar", ritmoDe(mult))
			else entrarParado(0.3) end
		else
			local iA, iP = table.find(ORDEM, m), table.find(ORDEM, pedida)
			if iP > iA and SUBIR[m] then iniciarClipe(SUBIR[m], ORDEM[iA + 1], ritmoDe(mult))
			elseif iP < iA and DESCER[m] then iniciarClipe(DESCER[m], ORDEM[iA - 1], ritmoDe(mult))
			else
				tocar(m, ritmoDe(mult))
				local a = angulo(frente, dir)
				local passo = math.clamp(a, -math.rad(CFG.giro[m]) * dt, math.rad(CFG.giro[m]) * dt)
				local rot = CFrame.Angles(0, passo, 0) * pv.Rotation
				local v = Mov.Velocidade[m] * mult * esc()
				local p = pv.Position + plano(rot.LookVector).Unit * v * dt
				if moverPara(CFrame.new(p) * rot) then vel = v
				else lobo:SetAttribute("CtrlBloqueio", "sem chao @" .. string.format("%.1f", agora))
					if m == "Corrida" then entrarParado(0.25) else entrarParado(0.3) end end
			end
		end
	end
	if E.frear and E.modo == "Parado" then
		E.frear = false
		local cb = E.aoParar; E.aoParar = nil; if cb then task.spawn(cb) end
	end
	lobo:SetAttribute("VelAtual", math.floor(vel * 100 + 0.5) / 100)
end)

rede.OnServerEvent:Connect(function(j, acao, a1, a2)
	if acao == "assumir" then
		if ctrl.jogador and ctrl.jogador ~= j then return end
		local hrp = j.Character and j.Character:FindFirstChild("HumanoidRootPart")
		if not hrp or (hrp.Position - lobo:GetPivot().Position).Magnitude > CFG.alcanceAssumir then
			lobo:SetAttribute("CtrlRecusa", "longe para assumir"); return
		end
		ctrl.jogador = j; ctrl.t = os.clock(); hrp.Anchored = true
		lobo:SetAttribute("Controlador", j.UserId); lobo:SetAttribute("CtrlSoltoPor", "")
		return
	end
	if j ~= ctrl.jogador then return end              -- so quem assumiu
	if acao == "soltar" then soltar("jogador"); return end
	if acao == "mover" then
		local agora = os.clock()
		if agora - ctrl.janela > 1 then ctrl.janela = agora; ctrl.n = 0 end
		ctrl.n += 1
		if ctrl.n > CFG.pacotesPorSeg then return end                        -- rapido demais: ignora
		if typeof(a1) ~= "Vector3" or a1 ~= a1 then return end              -- tipo errado / NaN
		local d = plano(a1)
		if d.X ~= d.X or d.Z ~= d.Z or math.abs(d.X) > 1e3 or math.abs(d.Z) > 1e3 then return end
		ctrl.dir = d.Magnitude > 1e-3 and d.Unit * math.min(d.Magnitude, 1) or Vector3.zero
		ctrl.marcha = MARCHA_PEDIDA[a2] and a2 or "trote"
		ctrl.t = agora
		return
	end
	if acao == "uivo" then
		-- freia antes (Corrida -> Frenagem etc.) e so entao pede o Uivo ao servidor do Uivo
		if E.frear then return end
		local pedir = pasta:FindFirstChild("Pedir_Uivo")
		if not pedir then return end
		if E.modo == "Parado" then pedir:Fire(j.UserId); return end
		E.frear = true; E.aoParar = function() pedir:Fire(j.UserId) end
	end
end)

Players.PlayerRemoving:Connect(function(j) if j == ctrl.jogador then soltar("saiu do jogo") end end)
pasta:SetAttribute("Controle_Versao", "r5 19/11 (velocidade da idade relativa ao tamanho) | r4 18/11 (idades: escala no deslocamento e ritmo do clipe; r3 pausa durante PoderAtivo)")

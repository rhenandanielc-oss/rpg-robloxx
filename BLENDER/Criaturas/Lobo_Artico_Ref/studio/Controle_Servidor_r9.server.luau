-- r9 20/11 (usuario: "arrume onde o lobo vira sem fisica / anda com as pernas paradas / pes flutuando"):
--   * sem chao a frente (toca estreita) o lobo nao gira mais o pivo no lugar: vira pelos clipes de passos (giroPara);
--   * INCLINACAO: o corpo acompanha o terreno (frente/tras e lado/lado, amostras sob as patas, suave, max 25 graus); o
--     controlador trabalha no pivo "puro" (so rumo) e a inclinacao e aplicada no fim de cada quadro em torno do meio das patas;
--   * PATAS NO CHAO: parado (e sem poder/pose deitada), IKControl por pata (raiz Umero/Coxa -> ponta Dedos/DedosPe) com
--     alvo no chao sob a posicao de repouso da pata (avaliado no cliente pelo Animator). Copia da r8b: Controle_Servidor_r8b.
-- r8b 20/11 (Play no rpg_roblox): so gira se o erro DEPOIS do giro ficar >= 5 graus menor que o atual (no modo preciso um
-- alvo a 25 graus fazia o lobo ir e voltar: 45 para um lado, 45 de volta). Copia da r8: Controle_Servidor_r8.
-- r8 20/11: VIRADAS NATURAIS. Parado, o corpo nao gira mais sobre as patas plantadas ("shift lock"):
--   zona morta de 35 graus (40 logo depois de um giro; a cabeca cobre esse desvio - OlharAlvo para o cliente) ou 20/30 quando a
--   IA pede giro PRECISO (IA_Olhar(dir, true): contato de mordida, cone 30); direcao do alvo suavizada (0,4 s) e o desvio
--   precisa persistir 0,3 s antes de iniciar um giro (simulacao: oscilacao +-12 graus -> 1 giro, antes 10); 35-60 graus -> clipe
--   VirarCurtoEsquerda/Direita (45 graus com passos, anim_v44b) se existir na biblioteca; acima de 60 -> VirarEsquerda/Direita
--   (90 graus com passos). O rumo externo segue a curva do proprio clipe (Movimento_LoboArtico: Curvas.VirarCurto*), sem
--   reiniciar no meio. Sem o clipe curto, cai no giro lento da r7 (LEGADO, marcado em CtrlGiroLegado). OlharAlvo = direcao
--   pedida (para a cabeca acompanhar no cliente, ainda nao feito). Copia da r7: Controle_Servidor_r7.
-- r7 19/11: IA_Olhar (orientacao sem deslocamento para o contato de ataque da IA). Copia da r6b: Controle_Servidor_r6b.
-- r6 19/11: ganchos da IA selvagem (IA_Mover, IA_Parar; selvagem nao pode ser assumido). Copia da r5: Controle_Servidor_r5.
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
	zonaMorta = 35, zonaMortaApos = 40, posGiroSeg = 1.0,  -- r8: parado, desvio ate isso nao gira o corpo [PROPOSTA][A TESTAR]
	zonaPrecisa = 20, zonaPrecisaApos = 30,               -- r8: IA pediu precisao (contato de mordida)
	suavOlhar = 0.4, persisteGiro = 0.3,                  -- r8: s de suavizacao da direcao e de persistencia do desvio
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
-- r6 (19/11, IA selvagem): a IA do servidor manda a MESMA intencao do jogador (direcao no plano + marcha) por um
-- BindableEvent; so vale sem jogador no controle. A locomocao (clipes, transicoes, chao, giro) e a mesma do ensaio.
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
-- r8: viradas curtas so se o clipe E a curva existirem (sem eles, giro LEGADO da r7)
local TEM_CURTO = lib:FindFirstChild("LoboArtico_VirarCurtoEsquerda") and lib:FindFirstChild("LoboArtico_VirarCurtoDireita")
	and Mov.Curvas.VirarCurtoEsquerda and Mov.Curvas.VirarCurtoDireita and true or false
if TEM_CURTO then faixa("VirarCurtoEsquerda"); faixa("VirarCurtoDireita") end
local function ehVirar(n) return n ~= nil and n:sub(1, 5) == "Virar" end
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
local ctrl = {jogador = nil, dir = Vector3.zero, marcha = "Trote", t = 0, n = 0, janela = 0, olhar = nil, olharT = 0}
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

local fimGiro, foraDesde = 0, nil
local function giroPara(a, preciso)                 -- r8: clipe de giro para o desvio a (rad); nil = zona morta/espera; "LEGADO" = sem clipe curto
	local apos = os.clock() - fimGiro < CFG.posGiroSeg
	local zm = preciso and (apos and CFG.zonaPrecisaApos or CFG.zonaPrecisa) or (apos and CFG.zonaMortaApos or CFG.zonaMorta)
	local g = math.abs(a)
	if g <= math.rad(zm) then foraDesde = nil; return nil end
	foraDesde = foraDesde or os.clock()
	if os.clock() - foraDesde < CFG.persisteGiro then return nil end      -- histerese no tempo: desvio passageiro nao gira
	foraDesde = nil
	local longo = g > math.rad(CFG.anguloVirar)
	if not longo and not TEM_CURTO then return "LEGADO" end
	local angClipe = math.rad(longo and 90 or 45)
	if math.abs(g - angClipe) > g - math.rad(5) then return nil end      -- r8b: o giro nao melhoraria (evita ir e voltar)
	if longo then return a > 0 and "VirarEsquerda" or "VirarDireita" end
	return a > 0 and "VirarCurtoEsquerda" or "VirarCurtoDireita"
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
-- r9: inclinacao com o terreno + patas no chao (IKControl) ------------------------------------------------------------------
local INCL = {pitch = 0, roll = 0, ultimo = nil, max = math.rad(25), suave = 0.15}
local function soRumo(cf)
	local f = plano(cf.LookVector); if f.Magnitude < 1e-3 then f = Vector3.new(0, 0, -1) end
	return CFrame.lookAt(cf.Position, cf.Position + f.Unit)
end
local function tirarInclinacao()                      -- inicio do quadro: o controlador trabalha no pivo so com rumo
	local pv = lobo:GetPivot()
	if INCL.ultimo and pv == INCL.ultimo and INCL.puro then lobo:PivotTo(INCL.puro); return end
	if math.abs(pv.LookVector.Y) > 1e-4 or math.abs(pv.RightVector.Y) > 1e-4 then lobo:PivotTo(soRumo(pv)) end
end
local function aplicarInclinacao(dt)
	local puro = lobo:GetPivot(); local e = esc()
	local function y(lx, lz) return chao((puro * CFrame.new(lx * e, 0, lz * e)).Position) end
	local yF, yT, yE, yD = y(0, -3.65), y(0, 2.06), y(-1.3, -0.8), y(1.1, -0.8)
	local tp, tr = 0, 0
	if yF and yT then tp = math.clamp(math.atan2(yF - yT, 5.71 * e), -INCL.max, INCL.max) end
	if yE and yD then tr = math.clamp(math.atan2(yD - yE, 2.4 * e), -INCL.max, INCL.max) end
	local k = 1 - math.exp(-dt / INCL.suave)
	INCL.pitch += (tp - INCL.pitch) * k; INCL.roll += (tr - INCL.roll) * k
	local C = CFrame.new(0, 0, -0.8 * e)                                 -- meio das patas
	local final = puro * C * CFrame.Angles(INCL.pitch, 0, INCL.roll) * C:Inverse()
	lobo:PivotTo(final); INCL.ultimo = lobo:GetPivot(); INCL.puro = puro
	lobo:SetAttribute("InclinacaoGraus", math.floor(math.deg(INCL.pitch) * 10) / 10)
end
local IKS = {}
do
	local ac = lobo:FindFirstChildOfClass("AnimationController")
	local ossos = {}; for _, d in ipairs(lobo:GetDescendants()) do if d:IsA("Bone") then ossos[d.Name] = d end end
	for k, c in pairs({DE = {"Umero_E", "Dedos_E"}, DD = {"Umero_D", "Dedos_D"}, TE = {"Coxa_E", "DedosPe_E"}, TD = {"Coxa_D", "DedosPe_D"}}) do
		local raiz, ponta = ossos[c[1]], ossos[c[2]]
		if ac and raiz and ponta then
			local at = Instance.new("Attachment"); at.Name = "IK_" .. k .. "_" .. pasta:GetFullName():gsub("%.", "_"); at.Parent = workspace.Terrain
			local ik = ac:FindFirstChild("IK_Pata_" .. k) or Instance.new("IKControl")
			ik.Name = "IK_Pata_" .. k; ik.Type = Enum.IKControlType.Position; ik.ChainRoot = raiz; ik.EndEffector = ponta; ik.Target = at
			ik.Weight = 0; ik.SmoothTime = 0.1; ik.Parent = ac
			IKS[k] = {ik = ik, at = at, ponta = ponta}
		end
	end
	pasta.Destroying:Connect(function() for _, v in pairs(IKS) do v.at:Destroy() end end)
end
local POSES_EM_PE = {Ameaca = true, Alerta = true, AmeacaEntrar = true, AmeacaSair = true, InvestidaAviso = true}
local function atualizarPatas()
	local poseIA = lobo:GetAttribute("IA_Pose")
	local ativo = E.modo == "Parado" and not lobo:GetAttribute("PoderAtivo") and (poseIA == nil or POSES_EM_PE[poseIA])
	local pv = lobo:GetPivot(); local puro = INCL.puro or soRumo(pv)
	for _, v in pairs(IKS) do
		if ativo then
			local off = pv:ToObjectSpace(v.ponta.WorldCFrame).Position                -- repouso da ponta em relacao ao pivo
			local P = puro * off; local gy = chao(Vector3.new(P.X, P.Y, P.Z))
			if gy then v.at.WorldPosition = Vector3.new(P.X, gy + off.Y, P.Z); v.ik.Weight = 1 else v.ik.Weight = 0 end
		else
			v.ik.Weight = 0
		end
	end
end
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
	tirarInclinacao()                                                       -- r9
	local mult = lobo:GetAttribute("MultVelocidade") or 1
	local agora = os.clock()
	-- intencao valida (Uivo/Parado, pacote velho ou sem controlador = sem direcao)
	local dir = ctrl.dir
	if not (ctrl.jogador or ctrl.ia) or agora - ctrl.t > CFG.pacoteVelho or lobo:GetAttribute("Parado") or E.frear then dir = Vector3.zero end
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
		f:AdjustSpeed(ehVirar(E.clipe) and 1 or ritmoDe(mult))
		local len = (#Mov.Curvas[E.clipe] - 1) / Mov.Fps
		local t = f.IsPlaying and f.TimePosition or len
		local dx, dz, g = curva(E.clipe, t)
		local alvo = E.base * CFrame.new(dx, 0, dz) * CFrame.Angles(0, g, 0)
		local x0, z0 = curva(E.clipe, math.max(0, t - dt))
		vel = (Vector3.new(dx, 0, dz) - Vector3.new(x0, 0, z0)).Magnitude / math.max(dt, 1e-3) * mult
		local girando = ehVirar(E.clipe)               -- vira no lugar: so o pivo precisa de chao
		if not moverPara(alvo, girando) then entrarParado(0.2); lobo:SetAttribute("CtrlBloqueio", "sem chao @" .. string.format("%.1f", agora)) end
		if E.modo == "Clipe" and (t >= len - 0.02 or not f.IsPlaying) then
			if ehVirar(E.clipe) then fimGiro = agora end   -- r8: histerese da zona morta conta do fim do giro
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
				-- r9: em vez de girar o pivo no lugar (r6b, "shift lock"), vira para a intencao com os clipes de passos
				local g = giroPara(a, true)
				if g and g ~= "LEGADO" then iniciarClipe(g, nil, 1) end
			elseif pedida == "Corrida" then
				iniciarClipe("Arrancada", "Corrida", ritmoDe(mult))
			else
				entrarLaco("Andar")
			end
		elseif ctrl.olhar and agora - ctrl.olharT < CFG.pacoteVelho and not lobo:GetAttribute("Parado") then
			-- r7 (IA selvagem, contato de ataque): so ORIENTA para o alvo, sem andar. Acima de anguloVirar usa o clipe de
			-- virada aprovado; abaixo gira devagar no lugar (giro do Andar), sem giro instantaneo.
			-- r8: direcao suavizada (alvo oscilando nao faz tremer); zona morta -> o corpo fica (cabeca acompanha no cliente)
			ctrl.olharF = ctrl.olharF and (ctrl.olharF:Lerp(ctrl.olhar, 1 - math.exp(-dt / CFG.suavOlhar))) or ctrl.olhar
			if ctrl.olharF.Magnitude < 1e-3 then ctrl.olharF = ctrl.olhar end
			ctrl.olharF = ctrl.olharF.Unit
			local a = angulo(frente, ctrl.olharF)
			lobo:SetAttribute("OlharAlvo", ctrl.olhar)
			local g = giroPara(a, ctrl.olharPreciso)
			lobo:SetAttribute("CtrlGiroLegado", g == "LEGADO" or nil)
			if g == "LEGADO" then                          -- sem clipe curto instalado: comportamento da r7 (giro lento do pivo)
				local passo = math.clamp(a, -math.rad(CFG.giro.Andar) * dt, math.rad(CFG.giro.Andar) * dt)
				lobo:PivotTo(CFrame.new(pv.Position) * CFrame.Angles(0, passo, 0) * pv.Rotation)
			elseif g then
				iniciarClipe(g, nil, 1)
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
	aplicarInclinacao(dt); atualizarPatas()                                 -- r9
end)

rede.OnServerEvent:Connect(function(j, acao, a1, a2)
	if acao == "assumir" then
		if lobo:GetAttribute("Selvagem") then lobo:SetAttribute("CtrlRecusa", "lobo selvagem"); return end   -- r6: selvagem nao e montavel
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
-- r6: ganchos da IA (servidor -> servidor)
local evIA = pasta:FindFirstChild("IA_Mover") or Instance.new("BindableEvent"); evIA.Name = "IA_Mover"; evIA.Parent = pasta
evIA.Event:Connect(function(d, marcha)
	if ctrl.jogador then return end
	if typeof(d) ~= "Vector3" or d ~= d then return end
	d = plano(d)
	ctrl.dir = d.Magnitude > 1e-3 and d.Unit * math.min(d.Magnitude, 1) or Vector3.zero
	ctrl.marcha = MARCHA_PEDIDA[marcha] and marcha or "andar"; ctrl.t = os.clock(); ctrl.ia = true
	if ctrl.dir.Magnitude > 0.1 then ctrl.olhar = nil; ctrl.olharF = nil end               -- r7: andar cancela o "so olhar"
end)
-- r7: IA_Olhar(direcao) = vira para a direcao SEM andar (vale enquanto chegar pedido; mesma validacao do IA_Mover)
local evOlhar = pasta:FindFirstChild("IA_Olhar") or Instance.new("BindableEvent"); evOlhar.Name = "IA_Olhar"; evOlhar.Parent = pasta
evOlhar.Event:Connect(function(d, preciso)
	if ctrl.jogador then return end
	ctrl.olharPreciso = preciso == true                                   -- r8: contato de mordida pede giro preciso
	if typeof(d) ~= "Vector3" or d ~= d then return end
	d = plano(d); if d.Magnitude < 1e-3 then return end
	ctrl.olhar = d.Unit; ctrl.olharT = os.clock(); ctrl.dir = Vector3.zero; ctrl.t = os.clock(); ctrl.ia = true
end)
local evIAuivo = pasta:FindFirstChild("IA_PedirUivo") or Instance.new("BindableEvent"); evIAuivo.Name = "IA_PedirUivo"; evIAuivo.Parent = pasta
evIAuivo.Event:Connect(function()
	if ctrl.jogador or E.frear then return end
	local pedirU = pasta:FindFirstChild("IA_Uivo"); if not pedirU then return end
	if E.modo == "Parado" then pedirU:Fire(); return end
	E.frear = true; E.aoParar = function() pedirU:Fire() end
end)
pasta:SetAttribute("Controle_Versao", "r9 20/11 (inclinacao + patas no chao; sem giro de pivo) | r8b 20/11 (giro so se melhora) | r8 20/11 (viradas naturais: zona morta, VirarCurto com passos) | r7 19/11 (IA_Olhar: orienta sem andar) | r6b 19/11 (ganchos da IA selvagem; gira no lugar sem chao a frente) | r5 19/11 (velocidade da idade relativa ao tamanho) | r4 18/11 (idades: escala no deslocamento e ritmo do clipe; r3 pausa durante PoderAtivo)")

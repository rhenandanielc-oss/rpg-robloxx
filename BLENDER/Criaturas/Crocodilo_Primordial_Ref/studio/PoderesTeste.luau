-- PoderesTeste (ModuleScript em ServerStorage.Crocodilo_Piloto) - PROTOTIPOS [PROPOSTA] dos 4 poderes historicos do
-- Crocodilo Primordial (Mordida de Agarrao, Giro Predatorio, Submersao, Cauda de Mare), SO NA ARENA DE TESTE.
-- Kit oficial, elemento, passiva e regra do agarrao PvP: PENDENTES. Tudo roda no SERVIDOR (alvo, alcance, estado,
-- efeitos e cancelamento); o agarrao so aceita bonecos com o atributo BonecoTeste. Um poder por vez (estado unico).
-- Saida limpa em: fim normal, cancelar(), alvo removido/morto, crocodilo removido. M.log guarda os eventos (evidencia).
local RS = game:GetService("RunService")
local PASTA = game.ServerStorage.Crocodilo_Piloto
local CFG = require(PASTA.ConfigPoderes_Teste)
local T = require(PASTA.TestePlayCrocodilo)
local M = {log = {}}
local modelo = workspace.Teste_Crocodilo.Crocodilo_Primordial
local PIVO0 = modelo:GetPivot()
local BASE = PIVO0                     -- P4: posicao/altura de repouso atual (M.posicionar e o fim da Submersao mudam)
local RepS = game:GetService("ReplicatedStorage")
local FX = RepS:FindFirstChild("Crocodilo_FX") or Instance.new("RemoteEvent")      -- efeitos SO visuais no cliente
FX.Name = "Crocodilo_FX"; FX.Parent = RepS
local AVISO = RepS:FindFirstChild("Crocodilo_SoltarAliado") or Instance.new("RemoteEvent")   -- 19/11: opcao "Soltar aliado" (cliente mostra o botao)
AVISO.Name = "Crocodilo_SoltarAliado"; AVISO.Parent = RepS
local function fx(tipo, ...) FX:FireAllClients(tipo, ...) end
local est = {poder = nil, alvo = nil, cons = {}, gen = 0, t0 = 0}
local avisarAliados                                          -- (definida na secao Soltar aliado)

local function log(...)
	local s = string.format("%.2f ", os.clock() - est.t0) .. string.format(...)
	table.insert(M.log, s); print("[PoderesTeste] " .. s)
end
local function osso(n) return modelo:FindFirstChild(n, true) end
local function limparCons() for _, c in ipairs(est.cons) do c:Disconnect() end; est.cons = {} end
local function alvoValido(a)
	if not a or not a.Parent or not a:IsDescendantOf(workspace) then return false end
	if CFG.SoBonecos and not a:GetAttribute("BonecoTeste") then return false end
	local h = a:FindFirstChildOfClass("Humanoid"); return h ~= nil and h.Health > 0
end
-- 16/11 (P3): o pivo do crocodilo muda de altura sempre por transicao suave (antes: PivotTo direto = salto de 2,4)
local function moverPivo(destino, dur)
	est.mov = (est.mov or 0) + 1; local tok = est.mov
	if dur <= 0 or not modelo:IsDescendantOf(workspace) then modelo:PivotTo(destino); return end
	local ini = modelo:GetPivot(); local t0 = os.clock()
	task.spawn(function()
		while est.mov == tok do
			local u = math.min(1, (os.clock() - t0) / dur); u = u * u * (3 - 2 * u)
			modelo:PivotTo(ini:Lerp(destino, u))
			if u >= 1 then break end
			RS.Heartbeat:Wait()
		end
	end)
end
-- ================================================================ P4: agua REAL (Terrain Water) medida no servidor
-- superficie = 1o impacto com agua; fundo = 1o solido ignorando a agua. A placa Agua_Teste (vidro) nao conta como agua.
local function medirAgua(pos)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	p.FilterDescendantsInstances = {modelo, workspace.Teste_Crocodilo:FindFirstChild("Arena")}
	local o = Vector3.new(pos.X, pos.Y + 60, pos.Z); local d = Vector3.new(0, -240, 0)
	local r1 = workspace:Raycast(o, d, p); p.IgnoreWater = true; local r2 = workspace:Raycast(o, d, p)
	local fundo = r2 and r2.Position.Y or -math.huge
	if r1 and r1.Material == Enum.Material.Water then return r1.Position.Y, fundo end
	return nil, fundo
end
local C_ = CFG.Corpo
local function montado() return modelo:GetAttribute("Montado") == true end      -- P4b: com cavaleiro afunda mais
local function extraMont() return montado() and CFG.Submersao.extra_montado or 0 end
local function profMin() return C_.topo + CFG.Submersao.folga_topo + extraMont() + CFG.Submersao.folga_fundo end
local function yEspreita(sup) return sup - C_.olhos + C_.pivo end            -- olhos/narinas na superficie
local function ySubmerso(sup) return sup - CFG.Submersao.folga_topo - extraMont() - C_.topo + C_.pivo end
-- P4b: presa a frente (so bonecos de teste): distancia da cabeca e angulo com a direcao do crocodilo
local function presaAFrente(cf)
	local cab = cf.Position + cf.LookVector * C_.cabeca
	local melhor, dm = nil, CFG.Submersao.deteccao
	for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
		if a:GetAttribute("BonecoTeste") and a.Parent and a:FindFirstChildOfClass("Humanoid") and a:FindFirstChildOfClass("Humanoid").Health > 0 then
			local c = (a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart); local v = c and (c.Position - cab)
			if v then
				local plano = Vector3.new(v.X, 0, v.Z)
				local ang = plano.Magnitude > 0.1 and math.deg(math.acos(math.clamp(plano.Unit:Dot(Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit), -1, 1))) or 0
				if plano.Magnitude <= dm and ang <= CFG.Submersao.cone then melhor, dm = a, plano.Magnitude end
			end
		end
	end
	return melhor, dm
end
local function naAltura(cf, y) return CFrame.new(cf.X, y, cf.Z) * cf.Rotation end
local function centro(a) local r = a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart; return r and r.Position end

-- O2 (19/11): o SERVIDOR diz para onde os olhos olham (atributo AlvoOlhar, Vector3; nil = o cliente escolhe sozinho).
-- So visual: o OlhosCrocodilo_Cliente gira os globos. Atualiza a 10 Hz (nao a cada quadro) para poupar rede.
-- Emboscada = presa detectada; Agarrao = alvo ate o contato e o alvo preso; Giro = alvo preso; Giro de Emboscada = pouso.
local function olharPara(p) modelo:SetAttribute("AlvoOlhar", p) end
local function seguirOlhar(g, fonte)                   -- fonte() -> Vector3 ou nil; para sozinho no fim do poder
	local acum = 1
	olharPara(fonte())
	table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
		if est.gen ~= g then return end
		acum += dt; if acum < 0.1 then return end; acum = 0
		olharPara(fonte())
	end))
end
local function olharAlvo(a) return function() local p = a and a.Parent and centro(a); return p and p + Vector3.new(0, 1, 0) end end

-- Agarrao PvP (19/11, numeros APROVADOS, A TESTAR). Boneco com atributo PvP=true simula a criatura de um jogador;
-- atributo Porte = pequeno/medio/grande/colossal. Imunidade e reducao de controle ficam em atributos do alvo (tempo do servidor).
local function agora() return workspace:GetServerTimeNow() end
local function ehPvP(a) return a ~= nil and a:GetAttribute("PvP") == true end
local function forcaIdade() return CFG.AgarraoPvP.forca_idade[modelo:GetAttribute("Idade") or "Adulto"] or 1 end
local function fatorControle(a) local t = a:GetAttribute("ControleReduzidoAte"); return (t and agora() < t) and CFG.AgarraoPvP.reduz or 1 end
-- Vitima montada (usuario 19/11): antes da mordida o CAVALEIRO PULA rapidamente e nao e agarrado; depois conta como aliado.
-- Convencao de teste: ObjectValue "Cavaleiro" dentro da montaria aponta o cavaleiro. Destino (usuario 19/11, "pular mais perto"):
-- AO LADO da cabeca do crocodilo, do lado em que o cavaleiro esta, para ja cair no alcance de bater (aliado).
local function pularCavaleiro(g, montaria, cav)
	local P = CFG.AgarraoPvP
	task.delay(P.pulo_atraso, function()
		if est.gen ~= g or not cav.Parent then return end
		local ov = montaria:FindFirstChild("Cavaleiro"); if ov then ov:Destroy() end
		est.cavaleiro = cav                                   -- o cavaleiro que pulou e aliado da montaria
		for _, w in ipairs(cav:GetDescendants()) do if w:IsA("WeldConstraint") and w.Name == "SelaTeste" then w:Destroy() end end
		cav:SetAttribute("Montado", false)
		local ini = cav:GetPivot(); local cf = modelo:GetPivot()
		local cab = osso("Cabeca"); local hp = cab and cab.TransformedWorldCFrame.Position or (cf.Position + cf.LookVector * C_.cabeca)
		local lado = cf.RightVector * (((ini.Position - cf.Position):Dot(cf.RightVector) >= 0) and 1 or -1)
		local fimXZ = hp + lado * P.pulo_lado - cf.LookVector * P.pulo_recuo
		local _, fundo = medirAgua(fimXZ); local fim = Vector3.new(fimXZ.X, math.max(fundo, -1000) + 2.5, fimXZ.Z)
		log("MONTADA: cavaleiro %s pula da %s antes da mordida, para o lado da cabeca do crocodilo (%.1f de lado)", cav.Name, montaria.Name, P.pulo_lado)
		local t = 0
		while t < P.pulo_dur do
			local dt = RS.Heartbeat:Wait(); if not cav.Parent then return end; t = math.min(P.pulo_dur, t + dt); local u = t / P.pulo_dur
			cav:PivotTo(CFrame.new(ini.Position:Lerp(fim, u) + Vector3.new(0, 4 * P.pulo_altura * u * (1 - u), 0)) * ini.Rotation)
		end
		cav:SetAttribute("Pulou", true)
		local hum, raiz = cav:FindFirstChildOfClass("Humanoid"), cav:FindFirstChild("HumanoidRootPart")   -- jogador: volta a andar
		if hum then hum.Sit = false end; if raiz and raiz.Anchored then raiz.Anchored = false end
	end)
end
local function marcarSoltoPvP(a)
	local P = CFG.AgarraoPvP
	a:SetAttribute("ImuneAgarraoAte", agora() + P.imune); a:SetAttribute("ControleReduzidoAte", agora() + P.reduz_janela)
	log("PvP: %s imune a agarrao por %.0f s; controle nos %.0f s seguintes dura %.0f%%", a.Name, P.imune, P.reduz_janela, P.reduz * 100)
end

-- solta o alvo (sempre seguro de chamar): volta ao chao no ponto atual, marca liberado
local function soltar(motivo)
	local a = est.alvo; est.alvo = nil
	for _, pl in ipairs(est.avisados or {}) do AVISO:FireClient(pl, "esconder") end; est.avisados = nil   -- some o botao Soltar aliado
	if a and a.Parent then
		local p = centro(a)
		if p and not est.ponto then a:PivotTo(CFrame.new(Vector3.new(p.X, 2.5, p.Z))) end   -- ponto de mordida: ja esta no chao, fica onde esta
		a:SetAttribute("Agarrado", false)
		log("alvo %s solto (%s)", a.Name, motivo)
		if ehPvP(a) then
			marcarSoltoPvP(a)
			local h = a:FindFirstChildOfClass("Humanoid")
			if h and h.Health <= 0 then a:SetAttribute("Refugio", true); log("PvP: %s derrotado -> sai da luta e vai ao refugio (simulado; nao e comido nem levado)", a.Name) end
		end
	end
end

-- P4: coloca o crocodilo num ponto (cf = posicao e direcao); na agua flutua na altura de espreita (se couber), senao apoia no fundo
function M.posicionar(cf)
	if est.poder then M.cancelar("reposicionado") end
	local sup, fundo = medirAgua(cf.Position)
	local y = fundo + C_.pivo
	if sup and sup - fundo >= C_.olhos then y = yEspreita(sup) end
	est.naAgua = sup ~= nil and (sup - fundo) > 1
	BASE = naAltura(cf, y); modelo:PivotTo(BASE)
	T.tocar(est.naAgua and "Crocodilo_Espreita" or "Crocodilo_Repouso", 0.2)
	return string.format("%s prof %.1f", est.naAgua and "agua" or "terra", sup and (sup - fundo) or 0)
end
function M.medir(pos) return medirAgua(pos or modelo:GetPivot().Position) end

function M.cancelar(motivo)
	motivo = motivo or "cancelado"
	if not est.poder then return "nada ativo" end
	log("FIM %s: %s", est.poder, motivo)
	est.gen += 1; limparCons(); soltar(motivo)
	est.pvp = nil; est.limite = nil; est.cavaleiro = nil  -- PvP: fim da pegada
	est.ponto = nil; est.yFix = nil
	T.parar()
	local dy = (modelo:GetPivot().Position - BASE.Position).Magnitude
	moverPivo(BASE, dy > 0.05 and 0.4 or 0)               -- volta a altura normal sem salto
	--                                   -- profundidade/posicao de teste voltam ao normal
	est.poder = nil; est.fase = nil
	modelo:SetAttribute("Submerso", false); modelo:SetAttribute("Movendo", false); modelo:SetAttribute("Giro", false); modelo:SetAttribute("CaudaVarre", nil)
	olharPara(nil)                                        -- O2: devolve o olhar ao cliente
	if modelo:IsDescendantOf(workspace) then T.tocar(est.naAgua and "Crocodilo_Espreita" or "Crocodilo_Repouso", 0.2) end
	return motivo
end

local function iniciar(poder, manterPivo)
	if est.poder then return false end
	if poder == "Agarrao" and est.bocaAbertaAte and os.clock() < est.bocaAbertaAte then   -- PvP: soltou por aliado = 0,6 s sem nova pegada
		log("Agarrao recusado: boca aberta (faltam %.2f s)", est.bocaAbertaAte - os.clock()); return false
	end
	if est.mov then est.mov += 1 end                         -- para uma volta suave pendente
	if not manterPivo and (modelo:GetPivot().Position - BASE.Position).Magnitude > 0.001 then modelo:PivotTo(BASE) end
	est.poder = poder; est.fase = nil; est.gen += 1
	if not manterPivo then est.t0 = os.clock(); M.log = {} end     -- encadeado: o log continua
	log("INICIO %s", poder)
	-- crocodilo removido: solta tudo
	table.insert(est.cons, modelo.AncestryChanged:Connect(function()
		if not modelo:IsDescendantOf(workspace) then M.cancelar("crocodilo_removido") end
	end))
	return est.gen
end
local function vigiaAlvo(g)
	table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
		if est.gen ~= g or not est.alvo then return end
		if not alvoValido(est.alvo) then M.cancelar("alvo_removido_ou_derrotado"); return end
		local mand = osso("Mandibula").TransformedWorldCFrame
		if not est.ponto then
			-- alvo pequeno: acompanha a mandibula no encaixe medido no contato (gira junto no Giro)
			est.alvo:PivotTo(mand * est.rel); return
		end
		-- 19/11 PONTO DE MORDIDA (alvo grande): so o ponto mordido segue os dentes; o corpo fica em pe, na altura do contato,
		-- e vira aos poucos para ficar ATRAS da mordida (arrastado), em vez de girar inteiro com a mandibula
		local ponta = mand * Vector3.new(0, CFG.Agarrao.ponta, 0)
		local cf = est.alvo:GetPivot(); local _, ry = cf:ToOrientation(); local rot = CFrame.Angles(0, ry, 0)
		local loc = -est.ponto * Vector3.new(1, 0, 1)                -- do ponto mordido ao centro do corpo (local)
		local atras = (cf.Position - ponta) * Vector3.new(1, 0, 1)
		if loc.Magnitude > 0.5 and atras.Magnitude > 0.5 then
			local w, t = rot:VectorToWorldSpace(loc).Unit, atras.Unit
			local d = math.atan2(w:Cross(t).Y, w:Dot(t)); local passo = CFG.Agarrao.giro_corpo * dt
			rot = CFrame.Angles(0, math.clamp(d, -passo, passo), 0) * rot
		end
		local pos = ponta - rot:VectorToWorldSpace(est.ponto)
		est.alvo:PivotTo(CFrame.new(pos.X, est.yFix, pos.Z) * rot)
	end))
end

-- ================================================================ Mordida de Agarrao
-- aproximacao (terra: MordidaLateral do lado do alvo; agua: desce a profundidade de teste e da o BoteAquatico; a Mordida
-- basica fica separada) -> contato no evento fecha_boca (alcance medido no servidor da PONTA DOS DENTES ao centro do
-- alvo) -> sustentacao (SegurarPresa / SegurarPresaAgua) -> SoltarPresa (marcador solta libera; cancelamento/remocao soltam na hora)
local function nadarAdiante(g, v0, dur, motivo)       -- P4b: errou o bote = continua nadando e desacelera, sem travar
	local atual
	local function tocarSe(nome) if atual ~= nome then atual = nome; T.tocar(nome, 0.3) end end
	tocarSe("Crocodilo_Nado")
	local t = 0
	while est.gen == g and t < dur do
		local dt = RS.Heartbeat:Wait(); if est.gen ~= g then return end; t += dt
		local cf = modelo:GetPivot()
		local function fundoOk(dir) local s2, f2 = medirAgua(cf.Position + dir * CFG.Submersao.olhar_frente); return s2 and s2 - f2 >= C_.olhos, s2 end
		local okF, s2 = fundoOk(cf.LookVector)
		local v = v0 * math.max(0, 1 - t / dur) ^ 1.5                    -- max(0): base negativa ^1,5 = NaN (jogava o modelo no infinito)
		if not okF then                                                       -- beira a frente: vira para o lado com agua
			local okE = fundoOk((cf * CFrame.Angles(0, math.rad(60), 0)).LookVector)
			cf = cf * CFrame.Angles(0, math.rad((okE and 1 or -1) * 75) * dt, 0); v = v * 0.35
			tocarSe(okE and "Crocodilo_CurvaAquaticaEsquerda" or "Crocodilo_CurvaAquaticaDireita")
		else tocarSe("Crocodilo_Nado") end
		local sAqui = medirAgua(cf.Position) or s2 or cf.Y
		local alvoY = yEspreita(sAqui); local yy = cf.Y + (alvoY - cf.Y) * math.min(1, dt * 3)      -- assenta na espreita sem salto
		cf = naAltura(cf + cf.LookVector * v * dt, yy); modelo:PivotTo(cf); BASE = naAltura(cf, alvoY)
	end
	if est.gen == g then M.cancelar(motivo) end
end
function M.agarrao(alvo, cena, opcoes)
	opcoes = opcoes or {}
	local g = iniciar("Agarrao", opcoes.emboscada); if not g then return "ocupado" end
	if not alvoValido(alvo) then M.cancelar("alvo_invalido"); return "alvo_invalido" end
	seguirOlhar(g, function() return olharAlvo(est.alvo or alvo)() end)   -- O2: olha o alvo do bote e, depois, o preso
	local ov = ehPvP(alvo) and alvo:FindFirstChild("Cavaleiro")
	if ov and ov:IsA("ObjectValue") and ov.Value and ov.Value.Parent then pularCavaleiro(g, alvo, ov.Value) end   -- 19/11: montada
	local clipe
	if cena == "agua" and opcoes.emboscada then
		-- P4b: vem SUBMERSO da Submersao: sobe rapido ate a espreita e continua avancando (impulso que se apaga no bote)
		local cf = modelo:GetPivot(); local sup = medirAgua(cf.Position) or cf.Y
		local yBote = math.max(yEspreita(sup) - CFG.Submersao.bote_abaixo, (select(2, medirAgua(cf.Position)) or -math.huge) + C_.pivo)
		BASE = naAltura(cf, yBote); moverPivo(BASE, CFG.Submersao.subida_bote); clipe = "Crocodilo_BoteAquatico"
		fx("ondulacao", Vector3.new(cf.X, sup, cf.Z) + cf.LookVector * C_.cabeca, 1.3)
		-- investida: avanca ate parar a ~3 da presa (max 9), desacelerando ate o fecha_boca (0,62 s); sobe com o fundo na beira
		local frente = (centro(alvo) - cf.Position); frente = Vector3.new(frente.X, 0, frente.Z):Dot(Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit)
		local L = math.clamp(frente - C_.ponta_bote - CFG.Submersao.parar_antes, 0, CFG.Submersao.investida_max)   -- pela ponta dos dentes
		local ini = modelo:GetPivot()
		task.spawn(function()
			local t, D = 0, 0.6
			while est.gen == g and t < D do
				local dt = RS.Heartbeat:Wait(); if est.gen ~= g then return end; t = math.min(D, t + dt)
				local u = 1 - (1 - t / D) ^ 2                                 -- ease-out
				local alvoXZ = ini.Position + ini.LookVector * (L * u)
				local s2, f2 = medirAgua(alvoXZ); s2 = s2 or sup
				local yy = math.max(modelo:GetPivot().Y, f2 + C_.pivo)          -- nunca abaixo do fundo
				modelo:PivotTo(naAltura(ini.Rotation + alvoXZ, yy)); BASE = naAltura(ini.Rotation + alvoXZ, math.max(yEspreita(s2), f2 + C_.pivo))
				est.yBote = yy
			end
		end)
	elseif cena == "agua" then
		-- espreita: so olhos/narinas/cristas fora (0,85 abaixo do nado de teste), afunda na antecipacao do bote
		moverPivo(BASE * CFrame.new(0, -(est.naAgua and 0 or CFG.Agarrao.profundidade_agua), 0), 0.3); clipe = "Crocodilo_BoteAquatico"
	else
		clipe = (BASE:PointToObjectSpace(centro(alvo)).X < 0) and "Crocodilo_MordidaLateralEsquerda" or "Crocodilo_MordidaLateralDireita"
	end
	log("aproximacao: %s (%s)", clipe:sub(11), cena or "terra")
	local f = T.tocar(clipe, 0.1)
	local resultado = "andamento"
	table.insert(est.cons, f:GetMarkerReachedSignal("fecha_boca"):Connect(function()
		if est.gen ~= g then return end
		local ponta = osso("Mandibula").TransformedWorldCFrame * Vector3.new(0, CFG.Agarrao.ponta, 0)   -- +Y do osso = frente
		local d = (ponta - centro(alvo)).Magnitude
		if d <= CFG.Agarrao.alcance and alvoValido(alvo) then
			local P = CFG.AgarraoPvP
			local imune = alvo:GetAttribute("ImuneAgarraoAte")
			if imune and agora() < imune then                       -- PvP: resistencia a repeticao (8 s depois de solto)
				alvo:FindFirstChildOfClass("Humanoid"):TakeDamage(CFG.Agarrao.dano_contato)
				log("PvP: %s IMUNE ao agarrao (faltam %.1f s): so a mordida, dano %d", alvo.Name, imune - agora(), CFG.Agarrao.dano_contato)
				resultado = "imune"; return
			end
			if ehPvP(alvo) and alvo:GetAttribute("Porte") == "colossal" then   -- PvP colossal: morde um membro, nao prende
				local h = alvo:FindFirstChildOfClass("Humanoid"); h:TakeDamage(CFG.Agarrao.dano_contato)
				local dur = P.colossal_dur * forcaIdade() * fatorControle(alvo)
				local ws0 = h.WalkSpeed; h.WalkSpeed = ws0 * (1 - P.colossal_lentidao)
				alvo:SetAttribute("Lentidao", P.colossal_lentidao); alvo:SetAttribute("SemSaltoVoo", true)
				task.delay(dur, function() if alvo.Parent then h.WalkSpeed = ws0; alvo:SetAttribute("Lentidao", nil); alvo:SetAttribute("SemSaltoVoo", nil) end end)
				log("PvP: %s COLOSSAL -> mordeu um membro: %.0f%% de lentidao por %.2f s, sem saltar/decolar (nao prende)", alvo.Name, P.colossal_lentidao * 100, dur)
				resultado = "membro_colossal"; return
			end
			if ehPvP(alvo) then
				est.pvp = true; est.danoPegada = 0; est.cortado = 0
				local dur = P.duracao * forcaIdade() * fatorControle(alvo)
				est.limite = dur                                 -- segundos que restam, contados pelo dt da simulacao (= tempo das animacoes)
				log("PvP: pegada de %.2f s a partir do contato (agarrao + giro somados; idade %s)", dur, modelo:GetAttribute("Idade") or "Adulto")
				table.insert(est.cons, RS.Heartbeat:Connect(function(dt)   -- solta NO prazo (nao espera o clipe terminar)
					if est.gen ~= g or not est.alvo or not est.limite then return end
					est.limite -= dt; if est.limite > 0 then return end
					log("PvP: prazo da pegada -> solta"); soltar("pvp_prazo"); est.fase = "solto"
					local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
					table.insert(est.cons, fs.Stopped:Connect(function() if est.gen == g then M.cancelar("fim_agarrao") end end))
				end))
			else est.pvp = nil; est.limite = nil end
			est.alvo = alvo; alvo:SetAttribute("Agarrado", true)
			if est.pvp then avisarAliados(alvo) end                -- 19/11: aparece "Soltar aliado" para os aliados
			est.rel = osso("Mandibula").TransformedWorldCFrame:Inverse() * alvo:GetPivot()
			do                                                      -- 19/11: alvo grande = PONTO DE MORDIDA (osso mais perto dos dentes)
				local cfA = alvo:GetPivot(); local tam = alvo:GetExtentsSize()
				est.ponto = nil
				if math.max(tam.X, tam.Y, tam.Z) > CFG.Agarrao.rigido_max then
					local melhor, dm, nome = nil, math.huge, "caixa"
					for _, b in ipairs(alvo:GetDescendants()) do
						if b:IsA("Bone") then local dd = (b.TransformedWorldCFrame.Position - ponta).Magnitude; if dd < dm then melhor, dm, nome = b.TransformedWorldCFrame.Position, dd, b.Name end end
					end
					local lp = cfA:PointToObjectSpace(melhor or ponta)
					if not melhor then local h = tam / 2; lp = Vector3.new(math.clamp(lp.X, -h.X, h.X), math.clamp(lp.Y, -h.Y, h.Y), math.clamp(lp.Z, -h.Z, h.Z)) end
					est.ponto = Vector3.new(lp.X, 0, lp.Z); est.yFix = cfA.Y
					log("PONTO DE MORDIDA: %s (%.1f dos dentes); o corpo (%.0f studs) fica em pe e e arrastado", nome, dm == math.huge and 0 or dm, math.max(tam.X, tam.Z))
				end
			end
			local h = alvo:FindFirstChildOfClass("Humanoid"); h:TakeDamage(CFG.Agarrao.dano_contato)
			log("CONTATO: agarrou %s (distancia %.2f <= %.2f)", alvo.Name, d, CFG.Agarrao.alcance)
			resultado = "acerto"; vigiaAlvo(g)
		else
			log("ERROU: %s a %.2f (alcance %.2f)", alvo.Name, d, CFG.Agarrao.alcance); resultado = "erro_alcance"
		end
	end))
	table.insert(est.cons, f.Stopped:Connect(function()
		if est.gen ~= g then return end
		if est.pvp and not est.alvo then return end           -- PvP: ja soltou no prazo durante a mordida
		if resultado ~= "acerto" then
			if opcoes.emboscada and resultado:sub(1, 4) == "erro" then log("errou: segue nadando"); nadarAdiante(g, CFG.Submersao.velocidade * 0.7, CFG.Submersao.deriva, resultado .. "_seguiu_nadando"); return end
			M.cancelar(resultado); return
		end
		-- 16/11 (P2): sustentacao com clipe proprio (terra SegurarPresa, agua SegurarPresaAgua) no lugar de ArrastarPresa
		local nomeSeg = (cena == "agua") and "Crocodilo_SegurarPresaAgua" or "Crocodilo_SegurarPresa"
		T.tocar(nomeSeg, 0.2); est.fase = "segurando"
		log("SUSTENTACAO: %s", nomeSeg:sub(11))
		local t = 0
		table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
			if est.gen ~= g or not est.alvo or est.fase ~= "segurando" then return end
			if not alvoValido(est.alvo) then M.cancelar("alvo_removido_ou_derrotado"); return end
			t += dt; est.alvo:FindFirstChildOfClass("Humanoid"):TakeDamage(CFG.Agarrao.dano_por_segundo * dt)
			if est.limite then return end                         -- PvP: quem solta e o vigia do prazo (desde o contato)
			if t < CFG.Agarrao.sustentacao then return end
			-- fim normal: o dano para; SoltarPresa abre a boca e o marcador "solta" libera o boneco
			est.fase = "soltando"
			local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
			if cena == "agua" then moverPivo(BASE, 0.8) end        -- sobe a superficie enquanto solta
			log("FIM DA SUSTENTACAO (%.2f s): SoltarPresa", t)
			table.insert(est.cons, fs:GetMarkerReachedSignal("solta"):Connect(function()
				if est.gen ~= g then return end
				soltar("marcador_solta"); est.fase = "solto"
			end))
			table.insert(est.cons, fs.Stopped:Connect(function()
				if est.gen == g then M.cancelar("fim_agarrao") end
			end))
		end))
	end))
	return "iniciado"
end

-- ================================================================ Giro Predatorio
-- RolarDaMorte em laco; cada volta (DidLoop) = efeito de teste (anel de agua) + dano no alvo preso, se houver
local function anelAgua(pos, cor)
	local p = Instance.new("Part"); p.Name = "Efeito_Teste_Croc"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false
	p.Shape = Enum.PartType.Cylinder; p.Material = Enum.Material.Neon; p.Color = cor or Color3.fromRGB(150, 210, 230)
	p.Transparency = 0.35; p.Size = Vector3.new(0.2, 3, 3)
	p.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90)); p.Parent = workspace.Teste_Crocodilo
	local ts = game:GetService("TweenService")
	ts:Create(p, TweenInfo.new(0.8), {Size = Vector3.new(0.2, 16, 16), Transparency = 1}):Play()
	game:GetService("Debris"):AddItem(p, 0.9)
end
function M.giro()
	if not CFG.Giro.ativo then log("Rolar da Morte: removido do kit (usuario 19/11)"); return "removido" end
	local preso = est.poder == "Agarrao" and est.fase == "segurando" and est.alvo or nil
	if est.poder and not preso then return "ocupado" end
	local alvoAntes = preso
	if preso then est.gen += 1; limparCons(); est.poder = nil end   -- encadeia: o alvo continua preso
	local g = iniciar("Giro", preso ~= nil); if not g then return "ocupado" end   -- encadeado: fica na altura da pegada
	est.alvo = alvoAntes; if est.alvo then vigiaAlvo(g); seguirOlhar(g, function() return olharAlvo(est.alvo)() end) end   -- O2
	if est.alvo and est.limite then                         -- PvP: o giro nao renova a pegada (agarrao + giro <= duracao)
		table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
			if est.gen ~= g or not est.limite then return end
			est.limite -= dt
			if est.limite <= 0 then log("PvP: fim do prazo da pegada durante o giro"); M.cancelar("pvp_prazo") end
		end))
	end
	local f = T.tocar("Crocodilo_RolarDaMorte", 0.15); local voltas = 0
	log("GIRO comeca (alvo preso: %s)", est.alvo and est.alvo.Name or "nenhum")
	table.insert(est.cons, f.DidLoop:Connect(function()
		if est.gen ~= g then return end
		voltas += 1
		local c = osso("Coluna1").TransformedWorldCFrame.Position
		anelAgua(Vector3.new(c.X, CFG.AlturaAgua, c.Z))
		if est.alvo and alvoValido(est.alvo) then est.alvo:FindFirstChildOfClass("Humanoid"):TakeDamage(CFG.Giro.dano_por_volta) end
		log("volta %d completa (efeito sincronizado no DidLoop)", voltas)
		if voltas >= CFG.Giro.voltas then M.cancelar("fim_giro") end
	end))
	return "iniciado"
end

-- ================================================================ Submersao (P4, 16/11)
-- AGUA REAL (servidor mede superficie e fundo): espreita com olhos/narinas na superficie -> Mergulho (afunda em 0,5 s ate
-- o topo do corpo ficar abaixo da superficie) -> AproximacaoSubmersa deslocando o crocodilo no MUNDO (velocidade de teste,
-- energia por segundo), sempre conferindo a profundidade a frente -> Emersao adiante, de volta a espreita.
-- Raso demais (prof < topo do corpo + folgas): RECUSA clara (nao afunda atravessando o fundo); fica em espreita de
-- superficie. Sem agua real: recusa. TERRA: variante separada de postura baixa (Deitar -> DescansoDeitado -> Levantar).
-- Efeitos (ondulacao, rastro, bolhas) sao so visuais, no cliente (Crocodilo_FX / atributos Submerso e Movendo).
function M.submersao(meio)
	local g = iniciar("Submersao"); if not g then return "ocupado" end
	local C = CFG.Submersao
	local function seq(passos)
		task.spawn(function()
			for _, p in ipairs(passos) do
				if est.gen ~= g then return end
				p()
			end
			if est.gen == g then M.cancelar("fim_submersao") end
		end)
	end
	if meio == "terra" then
		seq({function() local f = T.tocar("Crocodilo_Deitar", 0.2); log("TERRA: deitar (postura baixa)"); f.Stopped:Wait() end,
			function() T.tocar("Crocodilo_DescansoDeitado", 0.2); log("escondido em cobertura (visivel)"); task.wait(C.tempo_terra) end,
			function() if est.gen ~= g then return end local f = T.tocar("Crocodilo_Levantar", 0.2); log("levanta"); f.Stopped:Wait() end})
		return "iniciado"
	end
	local cf0 = modelo:GetPivot()
	local sup, fundo = medirAgua(cf0.Position)
	if not sup then log("RECUSADA: sem agua real aqui"); fx("recusa", cf0.Position, "Sem água"); M.cancelar("sem_agua"); return "sem_agua" end
	local prof = sup - fundo
	if prof < profMin() then
		log("RECUSADA: raso (profundidade %.1f < %.1f necessaria)", prof, profMin())
		fx("recusa", cf0.Position, string.format("Raso demais: %.1f de %.1f", prof, profMin()))
		seq({function() T.tocar("Crocodilo_Espreita", 0.3); task.wait(1.5) end})     -- provisorio: espreita de superficie
		return "raso_insuficiente"
	end
	local energia = C.energia_teste
	seq({
		function()                                                   -- espreita: olhos e narinas na superficie
			T.tocar("Crocodilo_Espreita", 0.3); moverPivo(naAltura(cf0, yEspreita(sup)), 0.4)
			log("ESPREITA (prof %.1f; superficie %.2f, fundo %.2f)", prof, sup, fundo); task.wait(C.espreita)
		end,
		function()                                                   -- mergulho real
			T.tocar("Crocodilo_Mergulho", 0.2); fx("ondulacao", Vector3.new(cf0.X, sup, cf0.Z), 1.0)
			moverPivo(naAltura(modelo:GetPivot(), ySubmerso(sup)), C.descida)
			task.wait(C.descida * 0.6); modelo:SetAttribute("Superficie", sup); modelo:SetAttribute("Submerso", true)
			log("MERGULHO: topo do corpo %.1f abaixo da superficie", C.folga_topo); task.wait(C.descida * 0.6)
		end,
		function()                                                   -- deslocamento submerso no mundo
			T.tocar("Crocodilo_AproximacaoSubmersa", 0.3, C.vel_clipe); modelo:SetAttribute("Movendo", true)
			local andou, t = 0, 0; local motivo = "distancia"
			while est.gen == g do
				local dt = RS.Heartbeat:Wait(); if est.gen ~= g then break end; t += dt   -- cancelado durante a espera: nao move mais
				local cf = modelo:GetPivot(); local frente = cf.Position + cf.LookVector * C.olhar_frente
				local s2, f2 = medirAgua(frente)
				if not s2 or s2 - f2 < profMin() then motivo = "fundo_acaba_a_frente"; break end
				energia -= C.energia_s * dt
				if energia <= 0 then motivo = "sem_energia"; break end
				local presa = presaAFrente(cf)
				if presa then motivo = "presa_detectada"; est.presa = presa; est.presaDist = select(2, presaAFrente(cf)); olharPara(olharAlvo(presa)()); break end   -- O2: fixa a presa
				local passo = math.min(C.velocidade * dt, C.distancia - andou)
				cf = naAltura(cf + cf.LookVector * passo, ySubmerso(s2)); modelo:PivotTo(cf); andou += passo
				BASE = naAltura(cf, yEspreita(s2))                   -- cancelar aqui = sobe no lugar, sem voltar
				if andou >= C.distancia then break end
			end
			if est.gen ~= g then return end
			modelo:SetAttribute("Movendo", false)
			log("DESLOCAMENTO: %.1f studs em %.2f s (%.1f studs/s), energia %.0f -> %.0f, parou por %s%s", andou, t, andou / math.max(t, 0.01), C.energia_teste, energia, motivo, montado() and " (MONTADO, +" .. C.extra_montado .. " de fundo)" or "")
			if motivo == "presa_detectada" then                   -- emboscada: sobe rapido e da o bote (encadeia o Agarrao)
				local presa = est.presa; est.presa = nil
				modelo:SetAttribute("Submerso", false)
				est.gen += 1; limparCons(); est.poder = nil; est.fase = nil
				log("EMBOSCADA: %s a frente -> bote", presa.Name)
				M.agarrao(presa, "agua", {emboscada = true, vel = C.velocidade, dist = est.presaDist})
				return
			end
		end,
		function()                                                   -- emersao adiante
			local cf = modelo:GetPivot(); local s3 = medirAgua(cf.Position) or sup
			T.tocar("Crocodilo_Emersao", 0.2); moverPivo(naAltura(cf, yEspreita(s3)), C.subida)
			task.wait(C.subida * 0.5); modelo:SetAttribute("Submerso", false)
			fx("ondulacao", Vector3.new(cf.X, s3, cf.Z) + cf.LookVector * 10, 1.0)
			BASE = naAltura(cf, yEspreita(s3))
			log("EMERSAO adiante (%.1f studs do inicio)", (Vector3.new(cf.X, 0, cf.Z) - Vector3.new(cf0.X, 0, cf0.Z)).Magnitude)
			task.wait(C.subida * 0.5 + 0.6)
			est.emergiuEm = os.clock()                            -- abre a janela do Giro de Emboscada
		end})
	return "iniciado"
end

-- ================================================================ Giro Predatorio de Emboscada (P4, 16/11) [PROPOSTA]
-- Ref. secao 4 / 5.8: sai da agua GIRANDO e cai em terra, dano em area, derruba, silencioso. Janela: ate 1,5 s depois de
-- emergir da Submersao (dano cheio + bonus em alvo distraido); em agua rasa sem Submersao: dano 1,2x sem bonus; fora
-- disso: recusa. Clipes: GiroSaida (impulso) -> RolarDaMorte r2 em laco no ar -> GiroPouso (impacto). Servidor decide
-- janela, trajetoria, area, dano, derrubada e limpeza; o cliente so desenha (agua escorrendo, linhas, impacto).
local function chaoEm(pos)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude; p.IgnoreWater = true
	p.FilterDescendantsInstances = {modelo, workspace.Teste_Crocodilo:FindFirstChild("Arena"), workspace.Teste_Crocodilo:FindFirstChild("Cavaleiro_Teste")}
	local r = workspace:Raycast(Vector3.new(pos.X, pos.Y + 80, pos.Z), Vector3.new(0, -300, 0), p)
	return r and r.Position.Y or 0
end
function M.giroEmboscada()
	if est.poder then return "ocupado" end
	local G = CFG.GiroEmboscada
	local cf0 = modelo:GetPivot(); local sup, fundo = medirAgua(cf0.Position)
	local janela = est.emergiuEm and (os.clock() - est.emergiuEm) <= G.janela
	local modo, mult, bonus
	if janela then modo, mult, bonus = "emboscada", G.mult, G.bonus_distraido
	elseif sup and (sup - fundo) < profMin() then modo, mult, bonus = "raso", G.mult_raso, 1.0
	else
		local motivo = sup and "fora_da_janela" or "fora_da_agua"
		fx("recusa", cf0.Position, sup and "Giro: só até 1,5 s após emergir (ou no raso)" or "Giro: precisa sair da água")
		log("GIRO RECUSADO: %s", motivo); return motivo
	end
	local g = iniciar("GiroEmboscada", true)
	if not janela then est.t0 = os.clock(); M.log = {}; log("INICIO GiroEmboscada (raso)") end
	est.emergiuEm = nil
	-- destino: a frente, pousando onde o chao (com a frente do corpo) estiver; nunca abaixo do chao
	local dist = G.distancia; local alvoXZ = cf0.Position + Vector3.new(cf0.LookVector.X, 0, cf0.LookVector.Z).Unit * dist
	local yPouso = math.max(chaoEm(alvoXZ), chaoEm(alvoXZ + cf0.LookVector * C_.cabeca * 0.6) - 0.6) + C_.pivo
	local destino = naAltura(cf0.Rotation + alvoXZ, yPouso)
	do local cen = destino.Position + destino.LookVector * G.centro_frente; olharPara(Vector3.new(cen.X, chaoEm(cen) + 1, cen.Z)) end   -- O2: olha o pouso
	log("GIRO %s (x%.1f%s): de y %.2f ate (%.1f, %.2f, %.1f), %.0f studs", modo, mult, bonus > 1 and ", +50% em distraido" or "", cf0.Y, destino.X, destino.Y, destino.Z, dist)
	task.spawn(function()
		-- antes: agua ondula e escurece, bolhas sobem (silencioso)
		fx("giro_antes", Vector3.new(cf0.X, sup or cf0.Y, cf0.Z), cf0.LookVector)
		local fs = T.tocar("Crocodilo_GiroSaida", 0.15)
		local tImp = 0; local c1 = fs:GetMarkerReachedSignal("impulso"):Connect(function() tImp = os.clock() end)
		local t0 = os.clock(); while est.gen == g and tImp == 0 and os.clock() - t0 < 1 do RS.Heartbeat:Wait() end
		c1:Disconnect(); if est.gen ~= g then return end
		-- voo girando: RolarDaMorte em laco (1 volta por voo), parabola ate o destino
		modelo:SetAttribute("Giro", true); modelo:SetAttribute("Submerso", false)
		BASE = destino                                        -- cancelado no ar = termina no pouso, nao volta para a agua
		T.tocar("Crocodilo_RolarDaMorte", 0.08, 1.2 / G.voo)
		fx("ondulacao", Vector3.new(cf0.X, sup or cf0.Y, cf0.Z), 1.2)
		local ini = modelo:GetPivot(); local t = 0
		while est.gen == g and t < G.voo do
			local dt = RS.Heartbeat:Wait(); if est.gen ~= g then return end; t = math.min(G.voo, t + dt)
			local u = t / G.voo
			local pos = ini.Position:Lerp(destino.Position, u) + Vector3.new(0, 4 * G.altura * u * (1 - u), 0)
			modelo:PivotTo(ini.Rotation + pos)
		end
		if est.gen ~= g then return end
		-- pouso com peso: impacto em area (servidor), derruba; o cliente mostra o impacto
		BASE = destino; est.naAgua = medirAgua(destino.Position) ~= nil
		local fp = T.tocar("Crocodilo_GiroPouso", 0.05)
		local cen = destino.Position + destino.LookVector * G.centro_frente
		fx("giro_pouso", Vector3.new(cen.X, chaoEm(cen), cen.Z), G.raio, est.naAgua)
		local acertos = 0
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if alvoValido(a) and not a:GetAttribute("Agarrado") then
				local d = (centro(a) - cen) * Vector3.new(1, 0, 1)
				if d.Magnitude <= G.raio then
					local b = a:GetAttribute("Distraido") and bonus or 1.0
					local dano = G.dano_base * mult * b
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(dano); acertos += 1
					local orig = a:GetPivot(); a:SetAttribute("Derrubado", true)
					a:PivotTo(orig * CFrame.Angles(math.rad(80), 0, 0) - Vector3.new(0, 1.5, 0))
					local derruba = G.derruba * fatorControle(a)          -- PvP: controle logo depois de solto dura 50%
					if derruba < G.derruba then log("PvP: %s tinha sido solto ha pouco -> derrubada reduzida a %.2f s", a.Name, derruba) end
					task.delay(derruba, function() if a.Parent then a:PivotTo(orig); a:SetAttribute("Derrubado", false) end end)
					log("IMPACTO: %s a %.1f -> dano %.0f%s, derrubado %.2f s", a.Name, d.Magnitude, dano, b > 1 and " (distraido +50%)" or "", derruba)
				end
			end
		end
		if acertos == 0 then log("IMPACTO: ninguem no raio %.0f", G.raio) end
		task.delay(0.6, function() modelo:SetAttribute("Giro", false) end)
		fp.Stopped:Wait()
		if est.gen == g then M.cancelar("fim_giro_emboscada") end
	end)
	return "iniciado"
end

-- ================================================================ Cauda de Mare (P4, 16/11) [PROPOSTA]
-- Agua (CaudaDeMare, boiando) ou terra (CaudaDeMareTerra, patas plantadas). O ACERTO segue a TRAJETORIA REAL da cauda:
-- durante a varredura (0,42-0,75 s do clipe) o servidor amostra os ossos Cauda3..Cauda8 a cada quadro e atinge quem
-- estiver a ate `largura` da linha da cauda (cada boneco uma vez), empurrando no sentido da varredura. Nada e atingido
-- atras/fora do arco percorrido. A cobertura medida (graus do arco da ponta) e comparada com os 360 propostos (ref. 4).
local OSSOS_CAUDA = {"Cauda3", "Cauda4", "Cauda5", "Cauda6", "Cauda7", "Cauda8"}
local function distSeg(p, a, b)
	local ab = b - a; local t = ab.Magnitude > 1e-4 and math.clamp((p - a):Dot(ab) / ab:Dot(ab), 0, 1) or 0
	return (p - (a + ab * t)).Magnitude
end
function M.caudaDeMare()
	local g = iniciar("CaudaDeMare"); if not g then return "ocupado" end
	local K = CFG.Cauda
	local cf0 = modelo:GetPivot(); local sup, fundo = medirAgua(cf0.Position)
	local naAgua = sup ~= nil and (sup - fundo) > 1
	local nivel = naAgua and sup or chaoEm(cf0.Position)
	local f = T.tocar(naAgua and "Crocodilo_CaudaDeMare" or "Crocodilo_CaudaDeMareTerra", 0.1)
	log("CAUDA DE MARE em %s", naAgua and "AGUA (onda maior, empurra mais)" or "TERRA (lama, empurra menos)")
	modelo:SetAttribute("Nivel", nivel); modelo:SetAttribute("CaudaVarre", naAgua and "agua" or "terra")
	local atingidos, angs = {}, {}
	local antPonta
	table.insert(est.cons, RS.Heartbeat:Connect(function()
		if est.gen ~= g then return end
		local tp = f.TimePosition
		if tp < 0.42 or tp > 0.75 then return end
		local pts = {}; for _, n in ipairs(OSSOS_CAUDA) do local b = osso(n); if b then table.insert(pts, b.TransformedWorldCFrame.Position) end end
		local ponta = pts[#pts]; local l = modelo:GetPivot():PointToObjectSpace(ponta)
		table.insert(angs, math.deg(math.atan2(l.X, l.Z)))                   -- 0 = cauda reta para tras
		local dirV = antPonta and (ponta - antPonta) * Vector3.new(1, 0, 1) or Vector3.zero; antPonta = ponta
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if not atingidos[a] and alvoValido(a) and not a:GetAttribute("Agarrado") then
				local c = centro(a); local c2 = Vector3.new(c.X, 0, c.Z); local d = math.huge
				for i = 1, #pts - 1 do d = math.min(d, distSeg(c2, pts[i] * Vector3.new(1, 0, 1), pts[i + 1] * Vector3.new(1, 0, 1))) end
				if d <= K.largura then
					atingidos[a] = true
					local emp = naAgua and K.empurrao_agua or K.empurrao_terra
					local dir = dirV.Magnitude > 0.01 and dirV.Unit or (c2 - Vector3.new(cf0.X, 0, cf0.Z)).Unit
					a:PivotTo(a:GetPivot() + dir * emp)
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(K.dano)
					log("ACERTO na trajetoria: %s a %.1f da cauda (t=%.2f), dano %d, empurrado %.0f", a.Name, d, tp, K.dano, emp)
				end
			end
		end
	end))
	table.insert(est.cons, f:GetMarkerReachedSignal("impacto_cauda"):Connect(function()
		if est.gen ~= g then return end
		local p = osso("Cauda7").TransformedWorldCFrame.Position
		fx("cauda_impacto", Vector3.new(p.X, nivel, p.Z), naAgua and K.onda_agua or K.onda_terra, naAgua)
	end))
	table.insert(est.cons, f.Stopped:Connect(function()
		if est.gen ~= g then return end
		local a0, a1 = angs[1] or 0, angs[#angs] or 0
		local n = 0; for a in pairs(atingidos) do n += 1 end
		log("COBERTURA REAL: ponta de %.0f a %.0f graus = arco de %.0f graus (proposto: %d); atingidos %d", a0, a1, math.abs(a1 - a0), K.proposto_graus, n)
		M.cancelar("fim_cauda")
	end))
	return "iniciado"
end

-- ================================================================ Escamas Grossas (passiva, P4) [PROPOSTA]
-- Ref. secao 4: -15% de dano fisico. Teste: dois golpes fisicos equivalentes, com e sem a passiva, em terra e na agua.
-- O recuo (empurrao do golpe) e o mesmo com e sem a passiva; muda so com o meio (agua empurra mais). Pulso curto nas
-- escamas no ponto do impacto (cliente), sem escudo permanente.
-- PvP (19/11): opcoes.deVitima = golpe da propria presa na cabeca (encurta a pegada); opcoes.pesado = golpe que atordoa/derruba.
-- Golpe de aliado durante a pegada PvP soma dano; >= 8% da vida (ou pesado) solta na hora e deixa a boca aberta 0,6 s.
function M.receberGolpe(dano, ponto, passiva, opcoes)
	opcoes = opcoes or {}
	local E = CFG.Escamas
	local final = passiva and dano * (1 - E.reducao) or dano
	if est.alvo and est.pvp and est.limite then
		local P = CFG.AgarraoPvP
		if opcoes.deVitima then
			local corte = math.min(P.golpe_vitima, P.golpe_vitima_max - est.cortado)
			if corte > 0 then est.cortado += corte; est.limite -= corte end
			log("PvP: a presa golpeou a cabeca -> pegada -%.1f s (total -%.1f de %.1f)", corte, est.cortado, P.golpe_vitima_max)
		else
			est.danoPegada += final
			local limiar = P.soltar_pct * E.vida
			if opcoes.pesado or est.danoPegada >= limiar then
				log("PvP: ALIADO%s SOLTOU a presa (%s; dano somado %.0f de %.0f) -> boca aberta %.1f s", opcoes.de and (" " .. opcoes.de) or "", opcoes.pesado and "golpe pesado" or "dano", est.danoPegada, limiar, P.boca_aberta)
				est.bocaAbertaAte = os.clock() + P.boca_aberta
				M.cancelar("aliado_soltou")
				fx("escamas_pulso", ponto)
			else
				log("PvP: aliado%s golpeou (dano somado %.0f de %.0f)", opcoes.de and (" " .. opcoes.de) or "", est.danoPegada, limiar)
			end
		end
	end
	local cf = modelo:GetPivot(); local sup, fundo = medirAgua(cf.Position); local naAgua = sup ~= nil and (sup - fundo) > 1
	local recuo = naAgua and E.recuo_agua or E.recuo_terra
	local dir = (cf.Position - ponto) * Vector3.new(1, 0, 1); dir = dir.Magnitude > 0.1 and dir.Unit or -cf.LookVector
	local novo = cf + dir * recuo
	if not est.poder then BASE = novo; moverPivo(novo, 0.22) end
	local vida = (modelo:GetAttribute("VidaTeste") or E.vida) - final; modelo:SetAttribute("VidaTeste", vida)
	if passiva then fx("escamas_pulso", ponto) end
	table.insert(M.log, string.format("GOLPE %s em %s: %.0f -> %.0f de dano (%s), recuo %.1f, vida %.0f", passiva and "COM Escamas" or "SEM Escamas", naAgua and "agua" or "terra", dano, final, passiva and "-15%" or "cheio", recuo, vida))
	print("[PoderesTeste] " .. M.log[#M.log])
	return final, recuo
end

-- ================================================================ Soltar aliado (usuario 19/11) [PROPOSTA]
-- Quando o crocodilo agarra a criatura de um jogador (PvP), os aliados dela (o cavaleiro que pulou e quem estiver no
-- atributo "Aliados" da criatura, lista de UserIds) a ate `aviso_raio` recebem a opcao "Soltar aliado" (botao + tecla E).
-- Ao escolher, o SERVIDOR valida (e aliado, a pegada continua) e leva o personagem ate a cabeca do crocodilo andando de
-- verdade (Humanoid:MoveTo); perto, ele vira para a cabeca e golpeia; cada golpe so conta se estiver a ate `soco_alcance`
-- da cabeca no instante do impacto. Os golpes somam como os de qualquer aliado (8% da vida solta). Para quando a criatura
-- e solta, a pegada termina, o jogador morre ou passam `ir_max` s.
local ACP = game:GetService("AnimationClipProvider")
local function animSoco()                                   -- golpe R15 de TESTE (KFS registrado so no Studio)
	if est.animSoco then return est.animSoco end
	local kfs = Instance.new("KeyframeSequence"); kfs.Loop = false; kfs.Priority = Enum.AnimationPriority.Action
	for _, q in ipairs({{0, 0, 0, 0}, {0.14, -35, 75, -12}, {0.24, 100, 5, 20}, {0.36, 90, 10, 15}, {0.55, 0, 0, 0}}) do
		local kf = Instance.new("Keyframe"); kf.Time = q[1]
		local hrp = Instance.new("Pose"); hrp.Name = "HumanoidRootPart"; hrp.Weight = 0; hrp.Parent = kf
		local lt = Instance.new("Pose"); lt.Name = "LowerTorso"; lt.Weight = 0; lt.Parent = hrp
		local ut = Instance.new("Pose"); ut.Name = "UpperTorso"; ut.CFrame = CFrame.Angles(0, math.rad(q[4]), 0); ut.Parent = lt
		local ua = Instance.new("Pose"); ua.Name = "RightUpperArm"; ua.CFrame = CFrame.Angles(math.rad(q[2]), 0, 0); ua.Parent = ut
		local la = Instance.new("Pose"); la.Name = "RightLowerArm"; la.CFrame = CFrame.Angles(math.rad(q[3]), 0, 0); la.Parent = ua
		kf.Parent = kfs
	end
	est.animSoco = Instance.new("Animation"); est.animSoco.AnimationId = ACP:RegisterAnimationClip(kfs)
	return est.animSoco
end
avisarAliados = function(vit)                              -- chamada no contato do agarrao PvP
	local P = CFG.AgarraoPvP; est.avisados = {}
	local ids = "," .. tostring(vit:GetAttribute("Aliados") or "") .. ","
	for _, pl in ipairs(game.Players:GetPlayers()) do
		local ch = pl.Character; local hrp = ch and ch:FindFirstChild("HumanoidRootPart")
		local aliado = (est.cavaleiro ~= nil and ch == est.cavaleiro) or ids:find("," .. pl.UserId .. ",", 1, true) ~= nil
		if hrp and aliado and (hrp.Position - (centro(vit) or hrp.Position)).Magnitude <= P.aviso_raio then
			table.insert(est.avisados, pl); AVISO:FireClient(pl, "mostrar", vit.Name)
			log("SOLTAR ALIADO: opcao mostrada a %s", pl.Name)
		end
	end
end
local function irBater(pl, vit)
	local P = CFG.AgarraoPvP
	local ch = pl.Character; local h = ch and ch:FindFirstChildOfClass("Humanoid"); local hrp = ch and ch:FindFirstChild("HumanoidRootPart")
	if not (h and hrp) then return end
	if hrp.Anchored then hrp.Anchored = false end; h.Sit = false
	local cab = osso("Cabeca"); local tr = h:FindFirstChildOfClass("Animator"):LoadAnimation(animSoco())
	log("SOLTAR ALIADO: %s vai ate a cabeca do crocodilo (%.1f studs)", pl.Name, (hrp.Position - cab.TransformedWorldCFrame.Position).Magnitude)
	local t0, prox = os.clock(), 0
	while est.alvo == vit and h.Health > 0 and os.clock() - t0 < P.ir_max do
		local hp = cab.TransformedWorldCFrame.Position; local plano = Vector3.new(hp.X, hrp.Position.Y, hp.Z)
		if (hrp.Position - hp).Magnitude > P.soco_alcance - 1.5 then
			local lado = hrp.Position - plano; lado = lado.Magnitude > 0.1 and lado.Unit or modelo:GetPivot().RightVector
			h:MoveTo(plano + lado * P.soco_parar)
		elseif os.clock() >= prox then
			prox = os.clock() + P.soco_intervalo
			h:MoveTo(hrp.Position); hrp.CFrame = CFrame.lookAt(hrp.Position, plano)
			tr:Play(0.05, 1, 1.1)
			task.delay(0.22, function()                         -- impacto: o servidor confere o alcance agora
				if est.alvo ~= vit then return end
				local p2 = cab.TransformedWorldCFrame.Position; local d = (hrp.Position - p2).Magnitude
				if d <= P.soco_alcance then log("SOLTAR ALIADO: golpe de %s ACERTOU a %.1f studs", pl.Name, d); M.receberGolpe(P.soco_dano, p2, true, {de = pl.Name})
				else log("SOLTAR ALIADO: golpe de %s fora do alcance (%.1f > %.1f)", pl.Name, d, P.soco_alcance) end
			end)
		end
		task.wait(0.1)
	end
	h:MoveTo(hrp.Position)
	log("SOLTAR ALIADO: %s terminou (%s)", pl.Name, est.alvo == vit and "tempo/queda" or "aliado solto ou pegada acabou")
end
AVISO.OnServerEvent:Connect(function(pl, acao)
	if acao ~= "ir" then return end
	local vit = est.alvo; local ok = false
	for _, p in ipairs(est.avisados or {}) do if p == pl then ok = true end end
	if not (vit and est.pvp and ok) then log("SOLTAR ALIADO recusado para %s (sem pegada PvP ativa ou nao e aliado)", pl.Name); return end
	est.indo = est.indo or {}; if est.indo[pl] then return end
	est.indo[pl] = true
	task.spawn(function() irBater(pl, vit); est.indo[pl] = nil end)
end)

-- ================================================================ Sentido de Vibracao (passiva, usuario 19/11) [PROPOSTA]
-- Na agua (raio 40) ou em terra a ate 10 studs da agua (raio 20), o crocodilo percebe criaturas que SE MOVEM por perto,
-- mesmo sem ve-las (sem cone de visao). So informacao: nao causa dano nem muda os poderes. Parado nao vibra. O terreno
-- solido entre os dois bloqueia (agua nao). O SERVIDOR decide quem foi percebido e manda so ao dono (atributo DonoUserId
-- do crocodilo) as posicoes, para o cliente desenhar uma ondulacao discreta. M.vibracao = ultima leitura (teste/log).
local VIB = RepS:FindFirstChild("Crocodilo_Vibracao") or Instance.new("RemoteEvent"); VIB.Name = "Crocodilo_Vibracao"; VIB.Parent = RepS
M.vibracao = {meio = "fora", n = 0, nomes = {}}
local ultimaPos = {}
local function ondeEsta()                                    -- "agua", "margem" ou "fora" (servidor mede a agua real)
	local p = modelo:GetPivot().Position
	local sup, fundo = medirAgua(p)
	if sup and sup - fundo > 1 then return "agua", sup end
	local V = CFG.Vibracao
	for i = 0, 7 do
		local a = i * math.pi / 4; local s2, f2 = medirAgua(p + Vector3.new(math.cos(a), 0, math.sin(a)) * V.margem)
		if s2 and s2 - f2 > 0.5 then return "margem", s2 end
	end
	return "fora", nil
end
local rpTerreno = RaycastParams.new(); rpTerreno.FilterType = Enum.RaycastFilterType.Include; rpTerreno.IgnoreWater = true
rpTerreno.FilterDescendantsInstances = {workspace.Terrain}
task.spawn(function()
	while modelo.Parent do
		local V = CFG.Vibracao; task.wait(V.intervalo)
		local meio = ondeEsta(); local raio = meio == "agua" and V.raio_agua or (meio == "margem" and V.raio_margem or 0)
		local cab = (osso("Cabeca") and osso("Cabeca").TransformedWorldCFrame.Position) or modelo:GetPivot().Position
		local achados, nomes = {}, {}
		local cands = {}
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do if a:IsA("Model") then table.insert(cands, a) end end
		for _, pl in ipairs(game.Players:GetPlayers()) do if pl.Character then table.insert(cands, pl.Character) end end
		local vistos = {}
		for _, m in ipairs(cands) do
			local h = m:FindFirstChildOfClass("Humanoid"); local c = centro(m)
			if h and h.Health > 0 and c and m ~= modelo then
				vistos[m] = true
				local antes = ultimaPos[m]; ultimaPos[m] = c
				local vel = antes and ((c - antes) * Vector3.new(1, 0, 1)).Magnitude / V.intervalo or 0
				local d = (c - cab).Magnitude
				if raio > 0 and d <= raio and vel >= V.vel_min and vel <= V.vel_max then
					local r = workspace:Raycast(cab, c - cab, rpTerreno)
					if not r then table.insert(achados, c); table.insert(nomes, string.format("%s (%.0f studs, %.1f/s)", m.Name, d, vel)) end
				end
			end
		end
		for m in pairs(ultimaPos) do if not vistos[m] then ultimaPos[m] = nil end end
		local mudou = #nomes ~= M.vibracao.n or meio ~= M.vibracao.meio
		M.vibracao = {meio = meio, n = #nomes, nomes = nomes, raio = raio}
		modelo:SetAttribute("Vibracao", #nomes)
		if mudou and #nomes > 0 then log("VIBRACAO (%s, raio %d): %s", meio, raio, table.concat(nomes, "; ")) end
		local dono = game.Players:GetPlayerByUserId(modelo:GetAttribute("DonoUserId") or 0)
		if dono and #achados > 0 then VIB:FireClient(dono, achados) end
	end
end)

function M.estado() return {poder = est.poder, fase = est.fase, alvo = est.alvo and est.alvo.Name or nil, naAgua = est.naAgua} end
return M

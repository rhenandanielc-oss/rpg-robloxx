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

-- 20/11 HITBOX DE CONTATO (regra passada ao Lobo, adotada aqui): corpo do alvo = capsulas osso->pai (sem cauda/olhos/raiz);
-- sem ossos = caixa das partes visiveis. A distancia de um golpe e da PONTA DOS DENTES (ou da cauda) ate a SUPERFICIE.
local HB = CFG.Hitbox
local cacheCorpo = setmetatable({}, {__mode = "k"})
local function ignorarOsso(n) for _, k in ipairs(HB.ignorarOssos) do if n:find(k) then return true end end return false end
local function corpoDe(m)
	local c = cacheCorpo[m]; if c ~= nil then return c or nil end
	local segs, tem = {}, false
	local _, sz = m:GetBoundingBox(); local r = math.min(sz.X, sz.Y, sz.Z) * HB.raioGenerico
	for _, b in ipairs(m:GetDescendants()) do
		if b:IsA("Bone") then tem = true
			local pai = b.Parent
			if pai and pai:IsA("Bone") and not ignorarOsso(b.Name) and not ignorarOsso(pai.Name) then table.insert(segs, {pai, b, r}) end
		end
	end
	if not tem or #segs == 0 then cacheCorpo[m] = false; return nil end
	cacheCorpo[m] = segs; return segs
end
local function pontoSegm(p, a, b) local ab = b - a; local t = math.clamp((p - a):Dot(ab) / math.max(ab:Dot(ab), 1e-6), 0, 1); return a + ab * t end
local function contatoCorpo(alvo, p)                       -- distancia do ponto p a superficie do corpo do alvo
	local segs = corpoDe(alvo); local md = math.huge
	if segs then
		for _, sg in ipairs(segs) do
			local q = pontoSegm(p, sg[1].TransformedWorldCFrame.Position, sg[2].TransformedWorldCFrame.Position)
			md = math.min(md, (p - q).Magnitude - sg[3])
		end
		return math.max(0, md)
	end
	for _, pt in ipairs(alvo:GetDescendants()) do
		if pt:IsA("BasePart") and pt.Transparency < 1 then
			local l = pt.CFrame:PointToObjectSpace(p); local h = pt.Size / 2
			local q = pt.CFrame:PointToWorldSpace(Vector3.new(math.clamp(l.X, -h.X, h.X), math.clamp(l.Y, -h.Y, h.Y), math.clamp(l.Z, -h.Z, h.Z)))
			md = math.min(md, (p - q).Magnitude)
		end
	end
	return md
end
M.contatoCorpo = contatoCorpo

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
		local d = contatoCorpo(alvo, ponta)                      -- 20/11: dentes ate a SUPERFICIE do corpo (antes: ao centro, alcance 6,5)
		if d <= HB.contatoMordida and alvoValido(alvo) then
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
			log("CONTATO: agarrou %s (dentes a %.2f da superficie <= %.2f)", alvo.Name, d, HB.contatoMordida)
			resultado = "acerto"; vigiaAlvo(g)
		else
			log("ERROU: %s, dentes a %.2f da superficie (contato %.2f)", alvo.Name, d, HB.contatoMordida); resultado = "erro_alcance"
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
		local acertos, derrubados = 0, {}
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if alvoValido(a) and not a:GetAttribute("Agarrado") then
				local ca = centro(a); local d = contatoCorpo(a, Vector3.new(cen.X, ca.Y, cen.Z))   -- 20/11: ate a superficie
				if d <= G.raio then
					local b = a:GetAttribute("Distraido") and bonus or 1.0
					local dano = G.dano_base * mult * b
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(dano); acertos += 1
					log("IMPACTO: %s a %.1f da superficie -> dano %.0f%s", a.Name, d, dano, b > 1 and " (distraido +50%)" or "")
					local r = M.rolarControle(a, "GiroEmboscada")             -- 20/11: queda pelo contrato de porte (Caido/CaidoAte)
					if r.efeito == "queda" then table.insert(derrubados, a) end
				end
			end
		end
		if acertos == 0 then log("IMPACTO: ninguem no raio %.0f", G.raio) end
		task.delay(0.6, function() modelo:SetAttribute("Giro", false) end)
		fp.Stopped:Wait()
		if est.gen == g then M.cancelar("fim_giro_emboscada") end
		-- 20/11: IA decide FINALIZAR / POUPAR / APROVEITAR cada alvo derrubado (uma decisao por queda)
		for _, a in ipairs(derrubados) do
			if M.decidirQueda(a) == "FINALIZAR" then M.finalizar(a); break end
		end
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
				for i = 1, #pts - 1 do                              -- 20/11: a cauda precisa TOCAR a superficie do corpo
					for k = 0, 3 do d = math.min(d, contatoCorpo(a, pts[i]:Lerp(pts[i + 1], k / 3))) end
				end
				if d <= HB.contatoCauda then
					atingidos[a] = true
					local emp = naAgua and K.empurrao_agua or K.empurrao_terra
					local dir = dirV.Magnitude > 0.01 and dirV.Unit or (c2 - Vector3.new(cf0.X, 0, cf0.Z)).Unit
					a:PivotTo(a:GetPivot() + dir * emp)
					a:FindFirstChildOfClass("Humanoid"):TakeDamage(K.dano)
					log("ACERTO na trajetoria: %s, cauda a %.2f da superficie (t=%.2f), dano %d, empurrado %.0f", a.Name, d, tp, K.dano, emp)
					M.rolarControle(a, "CaudaDeMare")
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
	if est.poder == "Finalizacao" and dano > 0 then est.feridoFinal = true end   -- 20/11: ferido durante a finalizacao = solta
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

-- ================================================================ Controle por porte + Finalizacao (20/11) [PROPOSTA]/[A TESTAR]
-- Regras passadas ao Lobo Ancestral (contrato CONTRATO-CONTROLE-PORTE.md), adotadas no crocodilo:
-- * depois de um acerto valido com dano, UMA rolagem no servidor: chance = base x impacto x porte relativo x Forca relativa;
--   lentidao/claudicacao/queda (Caido/CaidoAte, nunca Incapacitado numa queda recuperavel); colossal metade; teto 60%;
--   >= 4 s DE PE entre quedas (do fim do levantar); PvP (criatura de jogador): duracao x0,5, cai pela metade a cada repeticao
--   em 12 s, depois de 2 seguidas imune por duracao + 8 s. O Giro de Emboscada derruba sempre (v6.2), com a duracao do contrato.
-- * finalizacao PROPRIA do crocodilo = MORDIDA ESMAGADORA (usuario 20/11): sibilo anunciado, aproxima andando, prende a
--   cabeca/pescoco do caido e aperta sacudindo; interrompivel o tempo todo (alvo levanta/protegido/removido/ferido = solta,
--   sem dano). Desfecho: selvagem morre; criatura de jogador e RETIRADA (refugio simulado, Vida mantida); humano nunca.
-- * IA: uma decisao por queda (FINALIZAR / POUPAR / APROVEITA), com motivo; crocodilo de dono nao finaliza sozinho.
local CT = CFG.Controle
local function deJogador(m) return (m:GetAttribute("DonoUserId") or 0) ~= 0 or m:GetAttribute("PvP") == true end
local function classePorte(m)
	local ombro, comp, idade, forca
	if m == modelo then comp, idade, forca = CT.porte.comprimento, m:GetAttribute("Idade") or "Adulto", CT.porte.forca
	else ombro, comp, idade, forca = m:GetAttribute("PorteOmbro"), m:GetAttribute("PorteComprimento"), m:GetAttribute("Idade") or "Adulto", m:GetAttribute("Forca") end
	local medida, fonte = ombro, "ombro"
	if not medida and comp then medida, fonte = comp / 2.5, "comprimento/2,5" end
	if not medida then
		local _, sz = m:GetBoundingBox(); medida, fonte = math.max(sz.Y, math.max(sz.X, sz.Z) / 2.5), "estimado pela caixa"
	else medida *= (CT.tamanhoIdade[idade] or 1) end
	local nome, idx = "colossal", 4
	for i, c in ipairs(CT.classes) do if medida < c[2] then nome, idx = c[1], i; break end end
	return {nome = nome, idx = idx, medida = medida, fonte = fonte, forca = (forca or 20) * (CT.forcaIdade[idade] or 1), idade = idade}
end
M.classePorte = classePorte
local function levantar(a)
	if not a.Parent or not a:GetAttribute("Caido") then return end
	local orig = est.origQueda and est.origQueda[a]
	if orig and a:FindFirstChildOfClass("Humanoid") and not a:GetAttribute("Agarrado") then a:PivotTo(orig) end
	a:SetAttribute("Caido", false); a:SetAttribute("CaidoAte", nil); a:SetAttribute("Derrubado", false)
	a:SetAttribute("LevantouEm", agora())
	if est.origQueda then est.origQueda[a] = nil end
	log("CONTROLE: %s levantou", a.Name)
end
M.levantar = levantar
local function aplicarQueda(a, dur)
	est.origQueda = est.origQueda or {}
	local orig = a:GetPivot(); est.origQueda[a] = orig
	a:SetAttribute("Caido", true); a:SetAttribute("CaidoAte", agora() + dur); a:SetAttribute("Derrubado", true)
	local _, sz = a:GetBoundingBox()
	if sz.Y > math.max(sz.X, sz.Z) then a:PivotTo(orig * CFrame.Angles(math.rad(80), 0, 0) - Vector3.new(0, 1.5, 0)) end   -- em pe (boneco): tomba
	task.delay(dur, function() if a.Parent and a:GetAttribute("Caido") and (a:GetAttribute("CaidoAte") or 0) <= agora() + 0.05 then levantar(a) end end)
end
function M.rolarControle(a, tipo, forcar)
	local g = CT.golpes[tipo]
	if not g or not a or not a.Parent then return {efeito = "nenhum", motivo = "golpe sem controle"} end
	if game.Players:GetPlayerFromCharacter(a) then return {efeito = "nenhum", motivo = "humano: regra so de criatura"} end
	local A, B = classePorte(modelo), classePorte(a)
	local dif = math.clamp(A.idx - B.idx, -3, 3)
	local fP = CT.porteRelativo[dif]; local fF = math.clamp(A.forca / math.max(B.forca, 1), CT.forcaMinMax[1], CT.forcaMinMax[2])
	local base = g.impacto * fP * fF
	local cQ = (g.impacto >= CT.queda.impactoMin) and math.min(1, CT.queda.chance * base) or 0
	local cM = (g.impacto >= CT.manca.impactoMin) and math.min(1, CT.manca.chance * base) or 0
	local cL = math.min(1, CT.lento.chance * base)
	local efeito, motivo = "nenhum", "sorteio"
	local r = math.random()
	if g.derrubaSempre or forcar == "queda" or r < cQ then efeito = "queda"
	elseif forcar == "manca" or r < cQ + cM then efeito = "manca"
	elseif forcar == "lento" or r < cQ + cM + cL then efeito = "lento" end
	if efeito == "queda" then                                   -- anti-repeticao: >= 4 s de pe desde o fim do levantar
		local lev = a:GetAttribute("LevantouEm")
		if a:GetAttribute("Caido") then efeito, motivo = "manca", "ja caido"
		elseif lev and agora() - lev < CT.queda.intervaloMin then efeito, motivo = "manca", string.format("so %.1f s de pe (< %.0f)", agora() - lev, CT.queda.intervaloMin) end
	end
	local dur
	if efeito == "queda" then
		dur = (tipo == "GiroEmboscada" and CFG.GiroEmboscada.derruba or 3.0) * (CT.duracaoPorte[B.nome] or 1)
		if deJogador(a) then                                      -- PvP: curto e com resistencia a repeticao
			local P = CT.pvp; local hist = a:GetAttribute("PvPQuedas") or ""; local n, ult = 0, 0
			for t in hist:gmatch("[^,]+") do local x = tonumber(t); if x and agora() - x <= P.janela then n += 1; ult = math.max(ult, x) end end
			local imune = a:GetAttribute("PvPImuneAte")
			if imune and agora() < imune then efeito, motivo, dur = "nenhum", "PvP: imune a queda", nil
			else
				dur = dur * P.fatorDur * (0.5 ^ n)
				a:SetAttribute("PvPQuedas", hist .. "," .. string.format("%.2f", agora()))
				if n + 1 >= P.maxSeguidos then a:SetAttribute("PvPImuneAte", agora() + dur + P.imuneSeg) end
			end
		end
		if dur then aplicarQueda(a, dur) end
	elseif efeito == "manca" or efeito == "lento" then
		local e = CT[efeito]; dur = e.dur * (CT.duracaoPorte[B.nome] or 1)
		a:SetAttribute("LentidaoControle", math.min(0.6, e.fracao)); a:SetAttribute("LentidaoAte", agora() + dur)
		if efeito == "manca" then a:SetAttribute("Mancando", true) end
		task.delay(dur, function() if a.Parent and (a:GetAttribute("LentidaoAte") or 0) <= agora() + 0.05 then
			a:SetAttribute("LentidaoControle", nil); a:SetAttribute("LentidaoAte", nil); a:SetAttribute("Mancando", nil) end end)
	end
	log("CONTROLE %s -> %s: croc %s %.1f (F%.0f) x alvo %s %.1f (%s, F%.0f), dif %+d; chances Q%.0f%% M%.0f%% L%.0f%% -> %s%s%s",
		tipo, a.Name, A.nome, A.medida, A.forca, B.nome, B.medida, B.fonte, B.forca, dif, cQ * 100, cM * 100, cL * 100, efeito,
		dur and string.format(" %.2f s", dur) or "", motivo ~= "sorteio" and (" (" .. motivo .. ")") or "")
	return {efeito = efeito, dur = dur, motivo = motivo}
end

-- IA: uma decisao por queda
function M.decidirQueda(a)
	local F = CFG.Finalizacao; local h = a:FindFirstChildOfClass("Humanoid")
	local dec, motivo = "FINALIZAR", "condicoes ok"
	local vidaCroc = (modelo:GetAttribute("VidaTeste") or CFG.Escamas.vida) / CFG.Escamas.vida
	if (modelo:GetAttribute("DonoUserId") or 0) ~= 0 then dec, motivo = "POUPAR", "crocodilo de dono nao finaliza sozinho"
	elseif game.Players:GetPlayerFromCharacter(a) then dec, motivo = "POUPAR", "humano nunca"
	elseif not h or h.Health / h.MaxHealth > F.vidaAlvoMax then dec, motivo = "APROVEITA", string.format("alvo ainda forte (%.0f%% > %.0f%%)", h and h.Health / h.MaxHealth * 100 or 0, F.vidaAlvoMax * 100)
	elseif vidaCroc < F.vidaPropriaMin then dec, motivo = "POUPAR", string.format("propria vida baixa (%.0f%%)", vidaCroc * 100)
	elseif (centro(a) - modelo:GetPivot().Position).Magnitude > F.abordarAte + C_.cabeca then dec, motivo = "POUPAR", "alvo longe demais"
	else
		for _, o in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if o ~= a and o:GetAttribute("Inimigo") and alvoValido(o) and not o:GetAttribute("Caido") and (centro(o) - modelo:GetPivot().Position).Magnitude < F.ameacaRaio then
				dec, motivo = "POUPAR", "outro inimigo a menos de " .. F.ameacaRaio .. " studs (" .. o.Name .. ")"; break
			end
		end
	end
	a:SetAttribute("DecisaoQueda", dec .. ": " .. motivo)
	log("DECISAO sobre %s caido: %s (%s)", a.Name, dec, motivo)
	return dec, motivo
end

-- MORDIDA ESMAGADORA
local function pontoFinal(a)                               -- osso de cabeca/pescoco do alvo; sem ossos, topo do corpo
	local melhor, nome = nil, nil
	for _, b in ipairs(a:GetDescendants()) do
		if b:IsA("Bone") then for _, k in ipairs(CFG.Finalizacao.ossosAlvo) do if b.Name:find(k) and not b.Name:find("Olho") then melhor, nome = b, b.Name; break end end end
		if melhor then break end
	end
	if melhor then return function() return melhor.TransformedWorldCFrame.Position end, nome end
	return function() local c = centro(a); return c and Vector3.new(c.X, c.Y, c.Z) end, "corpo"
end
function M.finalizar(a, forcar)
	local F = CFG.Finalizacao
	if game.Players:GetPlayerFromCharacter(a) then log("FINALIZACAO recusada: humano nunca"); return "humano" end
	if not alvoValido(a) then return "alvo_invalido" end
	if not a:GetAttribute("Caido") then log("FINALIZACAO recusada: %s de pe", a.Name); return "alvo_de_pe" end
	local h = a:FindFirstChildOfClass("Humanoid")
	if not forcar and h.Health / h.MaxHealth > F.vidaAlvoMax then log("FINALIZACAO recusada: %s ainda forte", a.Name); return "alvo_forte" end
	local g = iniciar("Finalizacao", true); if not g then return "ocupado" end
	est.feridoFinal = false
	local pto, nomePto = pontoFinal(a)
	a:SetAttribute("FinalizacaoDe", modelo.Name); modelo:SetAttribute("EmAtaque", "Finalizacao")
	olharPara(pto())
	local function limpa() if a.Parent then a:SetAttribute("FinalizacaoDe", nil) end; modelo:SetAttribute("EmAtaque", nil) end
	local function cancelar(m) if est.gen == g then log("FINALIZACAO CANCELADA (%s), sem dano", m); limpa(); M.cancelar("finalizacao_" .. m) end end
	local function valida()
		if est.gen ~= g then return false end
		if not alvoValido(a) then cancelar("alvo removido ou morto"); return false end
		if not a:GetAttribute("Caido") then cancelar("alvo levantou"); return false end
		if est.feridoFinal then cancelar("crocodilo ferido"); return false end
		return true
	end
	log("FINALIZACAO: sibilo %.1f s -> Mordida esmagadora em %s (%s)", F.anuncio, a.Name, nomePto)
	local fa = T.tocar("Crocodilo_AmeacaInflada", 0.15)
	task.spawn(function()
		local t = 0
		while t < F.anuncio do t += RS.Heartbeat:Wait(); if not valida() then return end end
		-- aproxima andando ate os dentes tocarem a cabeca/pescoco
		T.tocar("Crocodilo_Andar", 0.2)
		local tAp = 0
		while true do
			local dt = RS.Heartbeat:Wait(); tAp += dt; if not valida() then return end
			local mand = osso("Mandibula").TransformedWorldCFrame; local ponta = mand * Vector3.new(0, CFG.Agarrao.ponta, 0)
			local alvoP = pto(); local dv = (alvoP - ponta) * Vector3.new(1, 0, 1)
			if contatoCorpo(a, ponta) <= F.encostar or dv.Magnitude <= F.encostar then break end
			if tAp > F.abordarMax then cancelar("nao alcancou a tempo"); return end
			-- posiciona o CORPO para a ponta dos dentes chegar ao ponto (anda para a frente ou recua; alvo pode estar sob o pescoco)
			local cf = modelo:GetPivot(); local dir = (alvoP - cf.Position) * Vector3.new(1, 0, 1)
			local look = Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit; local alvoDir = dir.Magnitude > 0.1 and dir.Unit or look
			local ang = math.atan2(look:Cross(alvoDir).Y, look:Dot(alvoDir)); local passoAng = math.clamp(ang, -F.giro * dt, F.giro * dt)
			local nr = CFrame.Angles(0, passoAng, 0) * cf.Rotation
			local dPonta = ((ponta - cf.Position) * Vector3.new(1, 0, 1)).Magnitude
			local desejado = Vector3.new(alvoP.X, cf.Y, alvoP.Z) - alvoDir * dPonta
			local falta = desejado - cf.Position; falta = Vector3.new(falta.X, 0, falta.Z)
			local np = cf.Position + (falta.Magnitude > 0.01 and falta.Unit * math.min(F.vel * dt, falta.Magnitude) or Vector3.zero)
			BASE = CFrame.new(np) * nr; modelo:PivotTo(BASE)
		end
		-- prende e esmaga sacudindo
		T.tocar("Crocodilo_SegurarPresa", 0.12)
		log("FINALIZACAO: prendeu %s pelo %s; aperta sacudindo %.1f s", a.Name, nomePto, F.aperto)
		-- preso na boca nao consegue levantar: a queda dura ate o desfecho (se a finalizacao for interrompida, levanta depois)
		a:SetAttribute("CaidoAte", agora() + F.aperto + 0.6)
		task.delay(F.aperto + 0.6, function() if a.Parent and a:GetAttribute("Caido") and not a:GetAttribute("Incapacitado") and (a:GetAttribute("CaidoAte") or 0) <= agora() + 0.05 then levantar(a) end end)
		local base0 = modelo:GetPivot(); local t2 = 0
		while t2 < F.aperto do
			local dt = RS.Heartbeat:Wait(); t2 += dt; if not valida() then return end
			local s = math.sin(t2 / F.periodo * 2 * math.pi) * math.rad(F.sacudir)
			modelo:PivotTo(base0 * CFrame.Angles(0, s, 0))
		end
		modelo:PivotTo(base0)
		-- desfecho
		if deJogador(a) then
			a:SetAttribute("RetiradaDeCombate", true); a:SetAttribute("Incapacitado", true)
			log("FINALIZACAO: %s (criatura de jogador) RETIRADA da luta -> refugio (simulado; Vida %.0f mantida, sem morte)", a.Name, h.Health)
		else
			h.Health = 0; a:SetAttribute("Estado", "Morto"); a:SetAttribute("Incapacitado", true)
			log("FINALIZACAO: %s (selvagem) morreu (prototipo: sem loot/respawn)", a.Name)
		end
		limpa()
		local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
		fs.Stopped:Wait()
		if est.gen == g then M.cancelar("fim_finalizacao") end
	end)
	return "iniciado"
end

function M.estado() return {poder = est.poder, fase = est.fase, alvo = est.alvo and est.alvo.Name or nil, naAgua = est.naAgua} end
return M

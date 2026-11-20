-- PoderesTeste (ModuleScript em ServerStorage.Crocodilo_Piloto) - PROTOTIPOS [PROPOSTA] dos 4 poderes historicos do
-- Crocodilo Primordial (Mordida de Agarrao, Giro Predatorio, Submersao, Cauda de Mare), SO NA ARENA DE TESTE.
-- Kit oficial, elemento, passiva e regra do agarrao PvP: PENDENTES. Tudo roda no SERVIDOR (alvo, alcance, estado,
-- efeitos e cancelamento); o agarrao so aceita bonecos com o atributo BonecoTeste. Um poder por vez (estado unico).
-- Saida limpa em: fim normal, cancelar(), alvo removido/morto, crocodilo removido. M.log guarda os eventos (evidencia).
local RS = game:GetService("RunService")
local PASTA = game.ServerStorage.Crocodilo_Piloto
local CFG = require(PASTA.ConfigPoderes_Teste)
-- 20/11 KIT OFICIAL (usuario): elemento unico AGUA. Dano das 4 ativas = dano de Agua (marcado no alvo para o sistema de
-- vantagem/fraqueza elemental, que ainda nao existe: so registra). Finalizacao e ataques basicos continuam fisicos.
local function ferir(alvo, valor, poder)
	local h = alvo and alvo:FindFirstChildOfClass("Humanoid"); if not h then return end
	alvo:SetAttribute("UltimoDanoElemento", CFG.Elemento or "Fisico"); alvo:SetAttribute("UltimoDanoPoder", poder)
	h:TakeDamage(valor)
end
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
		if p and not est.ponto and not est.pegada then a:PivotTo(CFrame.new(Vector3.new(p.X, 2.5, p.Z))) end   -- ponto de mordida: ja esta no chao, fica onde esta
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
	est.ponto = nil; est.yFix = nil; est.pegada = nil; est.par = nil
	T.parar()
	local dy = (modelo:GetPivot().Position - BASE.Position).Magnitude
	moverPivo(BASE, dy > 0.05 and 0.4 or 0)               -- volta a altura normal sem salto
	--                                   -- profundidade/posicao de teste voltam ao normal
	est.poder = nil; est.fase = nil
	modelo:SetAttribute("Submerso", false); modelo:SetAttribute("Movendo", false); modelo:SetAttribute("Giro", false); modelo:SetAttribute("NoAr", false); modelo:SetAttribute("CaudaVarre", nil)
	olharPara(nil)                                        -- O2: devolve o olhar ao cliente
	if modelo:IsDescendantOf(workspace) then T.tocar(est.naAgua and "Crocodilo_Espreita" or "Crocodilo_Repouso", 0.2) end
	return motivo
end

local function iniciar(poder, manterPivo)
	if est.poder then return false end
	if est.montadoFase then log("%s recusado: montado (poderes montado ficam para depois, usuario 20/11)", poder); return false end
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
-- ================================================================ PEGADA REAL (20/11) [PROPOSTA]
-- Pedido do usuario: "agarre o alvo na boca, simetricamente na boca, o corpo encaixe certinho; se nao couber, so morde".
-- 1) escolhe a regiao mordivel (EncaixeBoca: secao por raios na colisao da presa); 2) poe a boca na pose da pegada, aberta
-- (regiao baixa = MORDIDA DE LADO, cabeca baixa e girada; senao a normal; na agua a de agua); 3) ajusta o corpo para o
-- CENTRO do vao ficar na regiao (lateral = plano mediano); 4) mede de novo no referencial real; 5) cabe -> fecha ate a
-- espessura (pesos do par _Boca0/_Boca1) e prende a presa ao referencial da boca; nao cabe -> so mordida; fora -> erra.
-- Enquanto segura, revalida (espessura x vao) e registra penetracao (espessura - vao na abertura medida) e deriva.
local E = require(PASTA.EncaixeBoca)
local vigiaAlvo                                            -- (definida logo abaixo)
local OFS_ALFA = 8.01                                      -- calibrado no Studio: par em _Boca0 = -8,01 graus mandibula/cranio
local function alfaAtual()
	local cab = osso("Cabeca").TransformedWorldCFrame; local J = osso("Mandibula").TransformedWorldCFrame.UpVector
	local F, U = cab.UpVector, -cab.LookVector
	return math.deg(math.atan2(-J:Dot(U), J:Dot(F))) + OFS_ALFA
end
local function cfBoca(b, d, alfa) return CFrame.fromMatrix(E.pontoBoca(b, d, alfa), b.R, b.U, -b.F) end
local function tocarPar(base, w, fade)
	T.parar(); local f0, f1 = T.faixa(base .. "_Boca0"), T.faixa(base .. "_Boca1")
	f0:Play(fade or 0.2, math.max(0.001, 1 - w)); f1:Play(fade or 0.2, math.max(0.001, w)); est.par = {f0, f1, base}
	return f1, f0
end
local function pesoPar(w, fade)
	if not est.par then return end
	est.par[1]:AdjustWeight(math.max(0.001, 1 - w), fade or 0.15); est.par[2]:AdjustWeight(math.max(0.001, w), fade or 0.15)
end
local function poseDe(p, agua)
	if agua then return "Crocodilo_SegurarPresaAgua", "Crocodilo_MordidaEsmagadora", "agua" end
	local chao = modelo:GetPivot().Y - C_.pivo
	if p.Y - chao <= CFG.Agarrao.altura_lado then
		local lado = (modelo:GetPivot():PointToObjectSpace(p).X > 0) and "E" or "D"   -- medido em Play: LadoE leva a boca a +X local (convencao giro180y)
		return "Crocodilo_SegurarLado" .. lado, "Crocodilo_EsmagarLado" .. lado, "lado" .. lado
	end
	return "Crocodilo_SegurarPresa", "Crocodilo_MordidaEsmagadora", "normal"
end
-- tenta prender a presa; devolve r com r.modo = "captura" | "mordida" | "erro" e as medidas (para log e teste)
local function pegarEm(g, alvo, agua, maxCorr, alvoR, sim)
	local baseSeg, baseEsm, pose = poseDe(alvoR.p, agua)
	tocarPar(baseSeg, 1, 0.2)                                   -- boca aberta no maximo, cabeca na pose da pegada
	local t = 0; while t < 0.3 do t += RS.Heartbeat:Wait(); if est.gen ~= g then return {modo = "erro", motivo = "cancelado"} end end
	local dEst = sim and sim.dPega or 4.8; local andou = 0; local p0 = modelo:GetPivot().Position
	local pR = alvoR.p
	local subiu = 0                                             -- 20/11: na agua o corpo tambem SOBE ate a presa (bote vindo do fundo)
	for volta = 1, 2 do
		for _ = 1, 15 do                                        -- leva o centro do vao (abertura maxima) ate a regiao
			local Mp = E.pontoBoca(E.boca(modelo), dEst, E.ALFA_MAX); local hz = (pR - Mp) * Vector3.new(1, 0, 1)
			local dy = 0
			if agua then dy = math.clamp((pR - Mp).Y, -1.0, CFG.Agarrao.subir_agua - subiu); dy = math.clamp(dy, -1.0, 1.2) end   -- passos curtos (sem salto)
			if hz.Magnitude < 0.03 and math.abs(dy) < 0.03 then break end
			if dy ~= 0 then subiu += dy; BASE = modelo:GetPivot() + Vector3.new(0, dy, 0); modelo:PivotTo(BASE); est.yBote = BASE.Y end
			local liq = ((modelo:GetPivot().Position + hz - p0) * Vector3.new(1, 0, 1)).Magnitude   -- deslocamento liquido do corpo
			if liq > maxCorr then
				return {modo = "erro", motivo = string.format("fora de alcance: o corpo precisaria se ajustar %.2f (max %.1f)", liq, maxCorr), p = pR, nome = alvoR.nome, pose = pose}
			end
			andou = liq; BASE = modelo:GetPivot() + hz; modelo:PivotTo(BASE); RS.Heartbeat:Wait()
		end
		if volta == 2 then break end
		-- morde o corpo ONDE a boca chega: desliza no plano mediano da boca (eixo R) e centra no corpo ao longo de U
		local b0 = E.boca(modelo); local Mp = E.pontoBoca(b0, dEst, E.ALFA_MAX)
		local pM = pR + b0.R * (Mp - pR):Dot(b0.R)
		local s0 = E.secao(alvo, pM, b0.F, b0.U)
		if s0 then pR = s0.centro end
	end
	local b = E.boca(modelo)
	local r = E.avaliar(alvo, pR, b, CFG.Agarrao.cravar)        -- medida no referencial REAL da boca (pose tocada); r2: dentes cravados
	r.p, r.nome, r.pose, r.baseSeg, r.baseEsm, r.andou, r.subiu = pR, alvoR.nome, pose, baseSeg, baseEsm, andou, subiu
	local dv = pR - E.pontoBoca(b, r.dPega or dEst, E.ALFA_MAX)
	r.lateral, r.altura, r.prof = dv:Dot(b.R), dv:Dot(b.U), dv:Dot(b.F)
	if math.abs(r.lateral) > E.TOL.lateral or math.abs(r.altura) > E.TOL.contato then
		r.modo = "erro"; r.motivo = string.format("a boca nao alcanca a regiao (fora do plano mediano %.2f, fora do vao %.2f)", r.lateral, r.altura); return r
	end
	if not r.cabe then r.modo = "mordida"; return r end
	pesoPar(r.w, 0.12)                                          -- fecha ate os dentes cravarem (espessura - cravar)
	r.modo = "captura"
	return r
end
-- tenta a regiao que cabe; se a boca nao chega nela, tenta a regiao mais perto (que nao cabe = so mordida)
local function pegar(g, alvo, agua, maxCorr, preferir)
	local sim, nao = E.escolher(modelo, alvo, 40, preferir, nil, not agua and (modelo:GetPivot().Y - C_.pivo + CFG.Agarrao.altura_lado) or nil)
	if not (sim or nao) then return {modo = "erro", motivo = "nenhuma regiao ao alcance"} end
	local base0 = modelo:GetPivot()
	local r = sim and pegarEm(g, alvo, agua, maxCorr, sim, sim)
	if (not r or r.modo == "erro") and nao and est.gen == g then
		if r then log("PEGADA: regiao que cabe (%s) fora: %s -> tenta a mais perto (%s)", tostring(sim.nome), r.motivo, nao.nome) end
		BASE = base0; modelo:PivotTo(base0)
		local r2 = pegarEm(g, alvo, agua, maxCorr, nao, nil)
		log("PEGADA (mais perto, %s): %s - %s", nao.nome, r2.modo, r2.motivo or "")
		if r2.modo ~= "erro" or not r then r = r2 end
	end
	return r
end
-- prende a presa no referencial da boca (centro do vao, na abertura de contato) e vigia a pegada
local function fixarPegada(g, alvo, r)
	local b = E.boca(modelo); local cfB = cfBoca(b, r.dPega, r.alfa)
	local tam = alvo:GetExtentsSize(); local grande = math.max(tam.X, tam.Y, tam.Z) > CFG.Agarrao.rigido_max
	est.pegada = {d = r.dPega, alfa = r.alfa, rel = cfB:Inverse() * alvo:GetPivot(), grande = grande, local_ = alvo:GetPivot():PointToObjectSpace(r.p),
		pontoLocal = alvo:GetPivot():PointToObjectSpace(r.p), penMax = -math.huge, derMax = 0, tU = r.tU, d0 = r.d0, d1 = r.d1, base = r.baseSeg, w = r.w,
		pose = r.pose, crava = r.crava, alfaContato = r.alfaContato}
	do                                                             -- r2 arremesso: altura do pivo sobre o chao e rumo da presa em pe
		local pv = alvo:GetPivot(); local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
		rp.FilterDescendantsInstances = {modelo, alvo}
		local hit = workspace:Raycast(pv.Position + Vector3.new(0, 4, 0), Vector3.new(0, -40, 0), rp)
		est.pegada.altChao = pv.Y - (hit and hit.Position.Y or (modelo:GetPivot().Y - C_.pivo))
		local _, ry = pv:ToOrientation(); est.pegada.ry0 = ry
	end
	-- corrige o resto: o ponto agarrado vai exatamente ao centro do vao (sem atravessar: so o desvio residual medido)
	if not grande then est.pegada.rel = cfB:Inverse() * (alvo:GetPivot() + (cfB.Position - r.p)) end
	local acum = 0
	table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
		local pg = est.pegada; if est.gen ~= g or not pg or est.alvo ~= alvo or est.fase == "soltando" then return end
		local b2 = E.boca(modelo); local M2 = E.pontoBoca(b2, pg.d, pg.alfa)
		local pw = alvo:GetPivot() * pg.pontoLocal
		pg.derMax = math.max(pg.derMax, (pw - M2).Magnitude)                       -- deriva do ponto agarrado no vao
		acum += dt; if acum < CFG.Agarrao.revalidar then return end; acum = 0
		local s = E.secao(alvo, pw, b2.F, b2.U); local aMed = alfaAtual()
		if s then
			local fmin = math.huge                                                       -- vao mais apertado na faixa ocupada pelo corpo
			for d = pg.d0 or pg.d, pg.d1 or pg.d, 0.1 do fmin = math.min(fmin, E.folga(aMed, d)) end
			local pen = s.tU - fmin; pg.penMax = math.max(pg.penMax, pen)               -- >0: arcadas apertam o corpo; <0 = folga
			if s.tU > E.folga(E.ALFA_MAX, pg.d) + 0.15 then log("PEGADA: secao %.2f nao cabe mais no vao -> solta", s.tU); M.cancelar("pegada_nao_cabe") end
		end
	end))
	vigiaAlvo(g)
end
local ACP_ = game:GetService("AnimationClipProvider")
local function tocarNaPresa(a, nome, loop, congelarFim)      -- pose da PRESA com os clipes dela (mesmo esqueleto de crocodilo)
	local ac = a:FindFirstChildOfClass("AnimationController"); if not ac then return nil end
	local kfs = PASTA.Animacoes:FindFirstChild(nome); if not kfs then return nil end
	local an = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
	for _, tr in ipairs(an:GetPlayingAnimationTracks()) do tr:Stop(0.25) end
	est.idsPresa = est.idsPresa or {}; est.idsPresa[nome] = est.idsPresa[nome] or ACP_:RegisterAnimationClip(kfs)
	local anim = Instance.new("Animation"); anim.AnimationId = est.idsPresa[nome]
	local tr = an:LoadAnimation(anim); tr.Looped = loop and true or false; tr:Play(0.25)
	if congelarFim then task.delay(math.max(0, kfs:GetKeyframes()[#kfs:GetKeyframes()].Time - 0.05), function() if tr.IsPlaying then tr:AdjustSpeed(0) end end) end
	return tr
end
M.tocarNaPresa = tocarNaPresa
vigiaAlvo = function(g)
	table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
		if est.gen ~= g or not est.alvo then return end
		if not alvoValido(est.alvo) then M.cancelar("alvo_removido_ou_derrotado"); return end
		local mand = osso("Mandibula").TransformedWorldCFrame
		if est.pegada then                                         -- 20/11 PEGADA REAL: preso ao referencial da BOCA (centro do vao)
			local pg = est.pegada; local b = E.boca(modelo); local cfB = cfBoca(b, pg.d, pg.alfa)
			if not pg.grande then est.alvo:PivotTo(cfB * pg.rel); return end
			-- presa grande: o ponto agarrado fica no centro da boca; o corpo fica no chao e vira para tras (arrastado)
			local cf = est.alvo:GetPivot(); local _, ry = cf:ToOrientation(); local rot = CFrame.Angles(0, ry, 0)
			local loc = -pg.local_ * Vector3.new(1, 0, 1); local atras = (cf.Position - cfB.Position) * Vector3.new(1, 0, 1)
			if loc.Magnitude > 0.5 and atras.Magnitude > 0.5 then
				local w, t = rot:VectorToWorldSpace(loc).Unit, atras.Unit
				local dd = math.atan2(w:Cross(t).Y, w:Dot(t)); local passo = CFG.Agarrao.giro_corpo * dt
				rot = CFrame.Angles(0, math.clamp(dd, -passo, passo), 0) * rot
			end
			est.alvo:PivotTo(CFrame.new(cfB.Position - rot:VectorToWorldSpace(pg.local_)) * rot)
			return
		end
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

-- ================================================================ ARREMESSO (20/11 r2) [PROPOSTA]
-- Usuario: "ele deve jogar a criatura presa mais pra longe". Fim da pegada: o crocodilo da uma sacudida DE LADO (corpo e
-- cabeca giram `giro` graus acelerando, a presa ainda presa no vao), solta no pico e a presa voa em arco ~8 studs para
-- o lado/frente, cai (PvE: Caido 1,5 s e levanta; sem dano na queda). PvP: metade da distancia e sem queda.
-- Presa ancorada (bonecos) = arco por script; presa com fisica = velocidade balistica no servidor.
local aplicarQueda                                         -- (definida mais abaixo, no controle por porte)
local function chaoEm(p, ignorar)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ignorar
	local hit = workspace:Raycast(p + Vector3.new(0, 15, 0), Vector3.new(0, -60, 0), rp)
	return hit and hit.Position.Y or (modelo:GetPivot().Y - C_.pivo)
end
local function lancar(a, pg, lado, pvp)
	local A = CFG.Arremesso; local fator = pvp and A.pvp_fator or 1
	local cfC = modelo:GetPivot()
	local dir = ((cfC.RightVector * lado * A.lateral + cfC.LookVector * A.frente) * Vector3.new(1, 0, 1)).Unit
	local ini = a:GetPivot(); local dist, alt, T = A.distancia * fator, A.altura * fator, A.voo * math.sqrt(fator)
	local alvoXZ = ini.Position + dir * dist
	local yFim = chaoEm(alvoXZ, {modelo, a}) + (pg.altChao or 0)
	local fim = CFrame.new(alvoXZ.X, yFim, alvoXZ.Z) * CFrame.Angles(0, (pg.ry0 or 0) - lado * math.rad(35), 0)
	log("ARREMESSO: %s para o lado %s, %.1f studs (arco %.1f, %.2f s)%s", a.Name, lado > 0 and "E" or "D", dist, alt, T, pvp and " [PvP: metade, sem queda]" or "")
	local raiz = a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart
	if raiz and not raiz.Anchored then                         -- presa com fisica: velocidade balistica (servidor e dono da rede no lance)
		local g = workspace.Gravity; local dy = yFim - ini.Y
		pcall(function() raiz:SetNetworkOwner(nil) end)
		raiz.AssemblyLinearVelocity = dir * (dist / T) + Vector3.new(0, (dy + 0.5 * g * T * T) / T, 0)
		task.delay(T, function() if a.Parent and (not pvp or A.pvp_queda) then aplicarQueda(a, A.queda) end end)
		return
	end
	local eixo = dir:Cross(Vector3.yAxis); local cambalhota = pvp and 0 or (math.pi * 2 * lado)
	local rot0 = ini - ini.Position; local rot1 = fim - fim.Position
	task.spawn(function()
		local t = 0
		while t < T do
			t += RS.Heartbeat:Wait(); if not a.Parent then return end
			local u = math.min(1, t / T)
			local p = ini.Position:Lerp(fim.Position, u) + Vector3.new(0, 4 * alt * u * (1 - u), 0)
			a:PivotTo(CFrame.new(p) * CFrame.fromAxisAngle(eixo, cambalhota * u) * rot0:Lerp(rot1, u))
		end
		a:PivotTo(fim)
		log("ARREMESSO: %s caiu a %.1f studs da soltura", a.Name, ((fim.Position - ini.Position) * Vector3.new(1, 0, 1)).Magnitude)
		if not pvp or A.pvp_queda then aplicarQueda(a, A.queda) end
	end)
end
-- r3 (usuario "Fazer os clipes"): clipe ArremessarPresaE/D (par _Boca0/_Boca1 na abertura da pegada) arma e chicoteia a
-- cabeca; o corpo gira so `giro_clipe` graus junto da chicotada; o evento "solta" do clipe solta e lanca a presa.
local function temClipeArr(lado)
	local n = "Crocodilo_ArremessarPresa" .. (lado > 0 and "E" or "D")
	return PASTA.Animacoes:FindFirstChild(n .. "_Boca0") and PASTA.Animacoes:FindFirstChild(n .. "_Boca1") and n
end
local function antecedenciaArr() return temClipeArr(1) and CFG.Arremesso.solta_clipe or CFG.Arremesso.giro_dur end
-- sacudida + soltura + lancamento; devolve true se arremessou (ja soltou a presa), false se so deve soltar como antes;
-- 2o retorno = faixa do clipe de arremesso (quem chama espera ela terminar em vez de tocar SoltarPresa)
local function arremessar(g, cena)
	local A = CFG.Arremesso; local a, pg, pvp = est.alvo, est.pegada, est.pvp
	if not a or not pg or (cena == "agua" and not A.agua) then return false end
	local lado = (pg.pose == "ladoE" and 1) or (pg.pose == "ladoD" and -1) or (math.random() < 0.5 and 1 or -1)
	local clipe = temClipeArr(lado)
	if clipe then
		local f1 = tocarPar(clipe, pg.w or 0.5, 0.15)
		local solto = false
		local con = f1:GetMarkerReachedSignal("solta"):Connect(function() solto = true end)
		est.mov = (est.mov or 0) + 1; local tok = est.mov
		local base = modelo:GetPivot(); local ang = math.rad(A.giro_clipe)
		log("ARREMESSO: clipe %s (arma e chicoteia), corpo gira %.0f graus", clipe, A.giro_clipe)
		local t = 0
		while not solto and t < 1.5 do                         -- corpo acompanha a chicotada (0,30 -> evento solta)
			t += RS.Heartbeat:Wait()
			if est.gen ~= g or est.mov ~= tok or est.alvo ~= a then con:Disconnect(); return est.alvo ~= a end
			local u = math.clamp((f1.TimePosition - 0.30) / math.max(0.05, A.solta_clipe - 0.30), 0, 1)
			modelo:PivotTo(base * CFrame.Angles(0, -lado * ang * u * u, 0))
		end
		con:Disconnect()
		soltar("arremesso"); lancar(a, pg, lado, pvp)
		moverPivo(base, A.volta_dur)
		return true, f1
	end
	est.mov = (est.mov or 0) + 1; local tok = est.mov
	local base = modelo:GetPivot(); local ang = math.rad(A.giro); local t = 0
	while t < A.giro_dur do                                    -- acelera (u^2): a velocidade maxima e no instante da soltura
		t += RS.Heartbeat:Wait()
		if est.gen ~= g or est.mov ~= tok or est.alvo ~= a then return est.alvo ~= a end
		local u = math.min(1, t / A.giro_dur)
		modelo:PivotTo(base * CFrame.Angles(0, -lado * ang * u * u, 0))
	end
	soltar("arremesso")
	lancar(a, pg, lado, pvp)
	moverPivo(base, A.volta_dur)                               -- volta ao rumo enquanto a presa voa
	return true
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
	local pegando = false
	local function aposBote()
		if est.gen ~= g then return end
		if est.pvp and not est.alvo then return end           -- PvP: ja soltou no prazo durante a mordida
		if resultado ~= "acerto" then
			if opcoes.emboscada and resultado:sub(1, 4) == "erro" then log("errou: segue nadando"); nadarAdiante(g, CFG.Submersao.velocidade * 0.7, CFG.Submersao.deriva, resultado .. "_seguiu_nadando"); return end
			M.cancelar(resultado); return
		end
		-- 20/11: sustentacao = o PAR da pose da pegada (normal / de lado / agua) ja tocando na abertura de contato
		est.fase = "segurando"
		log("SUSTENTACAO: %s (abertura %.1f graus, peso %.2f)", est.pegada and est.pegada.base:sub(11) or "?", est.pegada and est.pegada.alfa or -1, est.pegada and est.pegada.w or -1)
		local t = 0
		table.insert(est.cons, RS.Heartbeat:Connect(function(dt)
			if est.gen ~= g or not est.alvo or est.fase ~= "segurando" then return end
			if not alvoValido(est.alvo) then M.cancelar("alvo_removido_ou_derrotado"); return end
			t += dt; ferir(est.alvo, CFG.Agarrao.dano_por_segundo * dt, "MordidaAgarrao")
			if est.limite or est.pvpFim then return end           -- PvP: quem solta e o vigia do prazo (desde o contato)
			-- r2: a sacudida do arremesso comeca `giro_dur` antes do fim, para soltar exatamente na sustentacao
			local arr = est.pegada and (cena ~= "agua" or CFG.Arremesso.agua)
			if t < CFG.Agarrao.sustentacao - (arr and antecedenciaArr() or 0) then return end
			-- fim normal: o dano para; sacudida + arremesso (terra) ou SoltarPresa com o marcador "solta" (agua)
			est.fase = "soltando"
			local pg = est.pegada
			if pg then log("FIM DA PEGADA: penetracao max %.2f (cravar %.2f), deriva max %.3f (espessura %.2f, abertura %.1f, contato %.1f)", pg.penMax, pg.crava or 0, pg.derMax, pg.tU, pg.alfa, pg.alfaContato or pg.alfa) end
			log("FIM DA SUSTENTACAO (%.2f s): %s", t, arr and "sacudida + arremesso" or "SoltarPresa")
			task.spawn(function()
				local jogou, fimClipe = false, nil
				if arr then jogou, fimClipe = arremessar(g, cena) end
				if est.gen ~= g then return end
				if fimClipe then                                   -- r3: o proprio clipe volta ao Repouso
					est.fase = "solto"
					if fimClipe.IsPlaying then table.insert(est.cons, fimClipe.Stopped:Connect(function() if est.gen == g then M.cancelar("fim_agarrao") end end))
					else M.cancelar("fim_agarrao") end
					return
				end
				local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
				if cena == "agua" then moverPivo(BASE, 0.8) end    -- sobe a superficie enquanto solta
				if jogou then est.fase = "solto" else
					table.insert(est.cons, fs:GetMarkerReachedSignal("solta"):Connect(function()
						if est.gen ~= g then return end
						soltar("marcador_solta"); est.fase = "solto"
					end))
				end
				table.insert(est.cons, fs.Stopped:Connect(function()
					if est.gen == g then M.cancelar("fim_agarrao") end
				end))
			end)
		end))
	end
	table.insert(est.cons, f:GetMarkerReachedSignal("fecha_boca"):Connect(function()
		if est.gen ~= g then return end
		if not alvoValido(alvo) then resultado = "alvo_invalido"; return end
		local P = CFG.AgarraoPvP
		local imune = alvo:GetAttribute("ImuneAgarraoAte")
		if imune and agora() < imune then                       -- PvP: resistencia a repeticao (8 s depois de solto)
			ferir(alvo, CFG.Agarrao.dano_contato, "MordidaAgarrao")
			log("PvP: %s IMUNE ao agarrao (faltam %.1f s): so a mordida, dano %d", alvo.Name, imune - agora(), CFG.Agarrao.dano_contato)
			resultado = "imune"; return
		end
		if ehPvP(alvo) and alvo:GetAttribute("Porte") == "colossal" then   -- PvP colossal: morde um membro, nao prende
			local h = alvo:FindFirstChildOfClass("Humanoid"); ferir(alvo, CFG.Agarrao.dano_contato, "MordidaAgarrao")
			local dur = P.colossal_dur * forcaIdade() * fatorControle(alvo)
			local ws0 = h.WalkSpeed; h.WalkSpeed = ws0 * (1 - P.colossal_lentidao)
			alvo:SetAttribute("Lentidao", P.colossal_lentidao); alvo:SetAttribute("SemSaltoVoo", true)
			task.delay(dur, function() if alvo.Parent then h.WalkSpeed = ws0; alvo:SetAttribute("Lentidao", nil); alvo:SetAttribute("SemSaltoVoo", nil) end end)
			log("PvP: %s COLOSSAL -> mordeu um membro: %.0f%% de lentidao por %.2f s, sem saltar/decolar (nao prende)", alvo.Name, P.colossal_lentidao * 100, dur)
			resultado = "membro_colossal"; return
		end
		-- 20/11 PEGADA REAL: regiao que cabe, boca centralizada, fecha ate a espessura; nao cabe = so mordida
		pegando = true
		local r = pegar(g, alvo, cena == "agua", CFG.Agarrao.corrigir_agarrao)
		pegando = false; M.ultimaPegada = r
		if est.gen ~= g then return end
		log("PEGADA %s: regiao %s, pose %s; %s%s", string.upper(r.modo), tostring(r.nome), tostring(r.pose), r.motivo or "",
			r.lateral and string.format(" | desvio lateral %.2f, vao %.2f, corrigiu %.2f, subiu %.2f", r.lateral, r.altura, r.andou or 0, r.subiu or 0) or "")
		if r.modo == "erro" then resultado = "erro_alcance"
		elseif r.modo == "mordida" then
			ferir(alvo, CFG.Agarrao.dano_contato, "MordidaAgarrao")
			log("SO MORDIDA: %s nao cabe na boca (dano %d, sem prender)", alvo.Name, CFG.Agarrao.dano_contato); resultado = "so_mordida"
		else
			if ehPvP(alvo) then
				est.pvp = true; est.danoPegada = 0; est.cortado = 0; est.pvpFim = nil
				local dur = P.duracao * forcaIdade() * fatorControle(alvo)
				est.limite = dur                                 -- segundos que restam, contados pelo dt da simulacao (= tempo das animacoes)
				log("PvP: pegada de %.2f s a partir do contato (agarrao + giro somados; idade %s)", dur, modelo:GetAttribute("Idade") or "Adulto")
				table.insert(est.cons, RS.Heartbeat:Connect(function(dt)   -- solta NO prazo (nao espera o clipe terminar)
					if est.gen ~= g or not est.alvo or not est.limite then return end
					local arr = est.pegada and (cena ~= "agua" or CFG.Arremesso.agua)
					est.limite -= dt; if est.limite > (arr and antecedenciaArr() or 0) then return end
					est.limite = nil; est.pvpFim = true; est.fase = "soltando"
					log("PvP: prazo da pegada -> %s", arr and "sacudida + arremesso curto" or "solta")
					task.spawn(function()
						local jogou, fimClipe = false, nil
						if arr then jogou, fimClipe = arremessar(g, cena) end
						if not jogou and est.gen == g then soltar("pvp_prazo") end
						if est.gen ~= g then return end
						est.fase = "solto"
						if fimClipe then
							if fimClipe.IsPlaying then table.insert(est.cons, fimClipe.Stopped:Connect(function() if est.gen == g then M.cancelar("fim_agarrao") end end))
							else M.cancelar("fim_agarrao") end
							return
						end
						local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
						table.insert(est.cons, fs.Stopped:Connect(function() if est.gen == g then M.cancelar("fim_agarrao") end end))
					end)
				end))
			else est.pvp = nil; est.limite = nil; est.pvpFim = nil end
			est.alvo = alvo; alvo:SetAttribute("Agarrado", true)
			if est.pvp then avisarAliados(alvo) end                -- 19/11: aparece "Soltar aliado" para os aliados
			fixarPegada(g, alvo, r)
			local h = alvo:FindFirstChildOfClass("Humanoid"); ferir(alvo, CFG.Agarrao.dano_contato, "MordidaAgarrao")
			log("CONTATO: prendeu %s pela %s (espessura %.2f, abertura %.1f graus, d %.2f)", alvo.Name, r.nome, r.tU, r.alfa, r.dPega)
			resultado = "acerto"
		end
		if not f.IsPlaying then aposBote() end                  -- o par da pose ja parou o clipe do bote
	end))
	table.insert(est.cons, f.Stopped:Connect(function()
		if pegando then return end                            -- a pegada em curso chama aposBote ao terminar
		aposBote()
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

-- ================================================================ EMBOSCADA (antigo Giro de Emboscada) [OFICIAL 20/11]
-- 20/11 usuario: "tire o giro, deixe somente emboscada, nao quero que o crocodilo gire" -> BOTE SALTANDO: explode para fora
-- da agua com o corpo RETO e a boca aberta, salto curto e baixo, cai com peso e a boca fecha de estalo = MORDIDA em quem
-- estiver na frente da boca (raio a partir da ponta do focinho); derruba pelo contrato de porte. Janela: ate 1,5 s depois
-- de emergir da Submersao (dano cheio + bonus em alvo distraido); em agua rasa sem Submersao: 1,2x sem bonus; fora disso:
-- recusa. Clipes: EmboscadaSaida (impulso) -> EmboscadaVoo (laco, no ar) -> EmboscadaPouso (morde). Servidor decide janela,
-- trajetoria, mordida, dano (Agua), derrubada e limpeza; o cliente so desenha (agua explodindo, escorrendo, respingo).
-- (chaves internas continuam "GiroEmboscada" na config e no contrato de porte, so por compatibilidade)
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
		fx("recusa", cf0.Position, sup and "Emboscada: só até 1,5 s após emergir (ou no raso)" or "Emboscada: precisa sair da água")
		log("EMBOSCADA RECUSADA: %s", motivo); return motivo
	end
	local g = iniciar("Emboscada", true)
	if not janela then est.t0 = os.clock(); M.log = {}; log("INICIO Emboscada (raso)") end
	est.emergiuEm = nil
	-- destino: a frente, pousando onde o chao (com a frente do corpo) estiver; nunca abaixo do chao
	local dist = G.distancia; local alvoXZ = cf0.Position + Vector3.new(cf0.LookVector.X, 0, cf0.LookVector.Z).Unit * dist
	local yPouso = math.max(chaoEm(alvoXZ), chaoEm(alvoXZ + cf0.LookVector * C_.cabeca * 0.6) - 0.6) + C_.pivo
	local destino = naAltura(cf0.Rotation + alvoXZ, yPouso)
	do local cen = destino.Position + destino.LookVector * G.centro_frente; olharPara(Vector3.new(cen.X, chaoEm(cen) + 1, cen.Z)) end   -- O2: olha o pouso
	log("EMBOSCADA %s (x%.1f%s): de y %.2f ate (%.1f, %.2f, %.1f), %.0f studs", modo, mult, bonus > 1 and ", +50% em distraido" or "", cf0.Y, destino.X, destino.Y, destino.Z, dist)
	task.spawn(function()
		-- antes: agua ondula e escurece, bolhas sobem (silencioso)
		fx("giro_antes", Vector3.new(cf0.X, sup or cf0.Y, cf0.Z), cf0.LookVector)
		local fs = T.tocar("Crocodilo_EmboscadaSaida", 0.15)          -- 20/11: sai RETO (sem giro), boca abrindo
		local tImp = 0; local c1 = fs:GetMarkerReachedSignal("impulso"):Connect(function() tImp = os.clock() end)
		local t0 = os.clock(); while est.gen == g and tImp == 0 and os.clock() - t0 < 1 do RS.Heartbeat:Wait() end
		c1:Disconnect(); if est.gen ~= g then return end
		-- 20/11 usuario: SEM GIRO. Voo reto (EmboscadaVoo: corpo reto, boca aberta), arco curto e baixo ate o destino
		modelo:SetAttribute("NoAr", true); modelo:SetAttribute("Submerso", false)
		fx("emb_saida", Vector3.new(cf0.X, sup or cf0.Y, cf0.Z) + cf0.LookVector * C_.cabeca * 0.5, cf0.LookVector, sup ~= nil)
		BASE = destino                                        -- cancelado no ar = termina no pouso, nao volta para a agua
		T.tocar("Crocodilo_EmboscadaVoo", 0.08)
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
		local fp = T.tocar("Crocodilo_EmboscadaPouso", 0.05)   -- boca fecha de estalo no impacto (a mordida)
		local cen = destino.Position + destino.LookVector * G.centro_frente
		fx("giro_pouso", Vector3.new(cen.X, chaoEm(cen), cen.Z), G.raio, est.naAgua)
		local acertos, derrubados = 0, {}
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if alvoValido(a) and not a:GetAttribute("Agarrado") then
				local ca = centro(a); local d = contatoCorpo(a, Vector3.new(cen.X, ca.Y, cen.Z))   -- 20/11: ate a superficie
				if d <= G.raio then
					local b = a:GetAttribute("Distraido") and bonus or 1.0
					local dano = G.dano_base * mult * b
					ferir(a, dano, "Emboscada"); acertos += 1
					log("MORDIDA DA EMBOSCADA: %s a %.1f da superficie -> dano %.0f%s", a.Name, d, dano, b > 1 and " (distraido +50%)" or "")
					local r = M.rolarControle(a, "GiroEmboscada")             -- 20/11: queda pelo contrato de porte (Caido/CaidoAte)
					if r.efeito == "queda" then table.insert(derrubados, a) end
				end
			end
		end
		if acertos == 0 then log("EMBOSCADA: ninguem na mordida (raio %.1f a frente da boca)", G.raio) end
		task.delay(0.6, function() modelo:SetAttribute("NoAr", false) end)
		fp.Stopped:Wait()
		if est.gen == g then M.cancelar("fim_giro_emboscada") end
		-- 20/11: IA decide FINALIZAR / POUPAR / APROVEITAR cada alvo derrubado (uma decisao por queda)
		for _, a in ipairs(derrubados) do
			if M.decidirQueda(a) == "FINALIZAR" then M.finalizar(a); break end
		end
	end)
	return "iniciado"
end

M.emboscada = M.giroEmboscada                                -- 20/11: nome oficial "Emboscada" (sem giro)

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
-- 20/11 ONDA REAL (usuario: "as ondas tem como objetivo causar dano e empurrar"; "Onda real que avanca"): no impacto da
-- cauda sai uma onda em anel a partir da ponta da cauda; a FRENTE da onda cresce ate `onda_agua` (terra: onda de LAMA
-- menor, `onda_terra`) em `onda_dur_*` s. Cada alvo que a frente alcanca (superficie do corpo) e atingido UMA vez: dano
-- de Agua e empurrao para fora do centro, deslizando (nao teletransporta). Quem a cauda ja acertou direto nao leva a onda.
local function empurrarSuave(a, delta, dur)
	local raiz = a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart
	if raiz and not raiz.Anchored then                         -- com fisica: impulso horizontal + um pouco para cima
		raiz.AssemblyLinearVelocity += delta / dur + Vector3.new(0, 6, 0); return
	end
	local ini = a:GetPivot(); local t = 0
	task.spawn(function()
		while t < dur and a.Parent do
			t += RS.Heartbeat:Wait(); local u = math.min(1, t / dur); u = 1 - (1 - u) * (1 - u)   -- desacelera (agua freia)
			if a:GetAttribute("Agarrado") then return end
			a:PivotTo(ini + delta * u)
		end
	end)
end
local function ondaReal(c0, naAgua, jaAtingidos)
	local K = CFG.Cauda
	local R = naAgua and K.onda_agua or K.onda_terra
	local dur = naAgua and K.onda_dur_agua or K.onda_dur_terra
	local dano = naAgua and K.onda_dano_agua or K.onda_dano_terra
	local emp = naAgua and K.onda_empurrao_agua or K.onda_empurrao_terra
	fx("onda", c0, R, dur, naAgua)
	log("ONDA %s: raio %.0f em %.2f s, dano %d, empurra %.0f", naAgua and "DE AGUA" or "DE LAMA", R, dur, dano, emp)
	local t, n = 0, 0
	local con; con = RS.Heartbeat:Connect(function(dt)
		t += dt; local u = math.min(1, t / dur); local r = R * (1 - (1 - u) * (1 - u))   -- rapida no inicio, perde forca
		for _, a in ipairs(workspace.Teste_Crocodilo.Arena:GetChildren()) do
			if not jaAtingidos[a] and alvoValido(a) and not a:GetAttribute("Agarrado") then
				local ca = centro(a)
				if ca then
					local d = contatoCorpo(a, Vector3.new(c0.X, ca.Y, c0.Z))
					if d <= r then
						jaAtingidos[a] = true; n += 1
						local dir = (ca - c0) * Vector3.new(1, 0, 1); dir = dir.Magnitude > 0.05 and dir.Unit or Vector3.new(1, 0, 0)
						local e = emp * (1 - 0.4 * u)                       -- quem e pego mais longe e empurrado menos
						ferir(a, dano, "CaudaDeMare_Onda"); empurrarSuave(a, dir * e, 0.45)
						log("ONDA alcancou %s a %.1f do centro (t=%.2f): dano %d, empurrado %.1f", a.Name, d, t, dano, e)
					end
				end
			end
		end
		if u >= 1 then con:Disconnect(); log("ONDA terminou: %d atingido(s) pela onda", n) end
	end)
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
					ferir(a, K.dano, "CaudaDeMare")
					log("ACERTO na trajetoria: %s, cauda a %.2f da superficie (t=%.2f), dano %d, empurrado %.0f", a.Name, d, tp, K.dano, emp)
					M.rolarControle(a, "CaudaDeMare")
				end
			end
		end
	end))
	table.insert(est.cons, f:GetMarkerReachedSignal("impacto_cauda"):Connect(function()
		if est.gen ~= g then return end
		local p = osso("Cauda7").TransformedWorldCFrame.Position
		ondaReal(Vector3.new(p.X, nivel, p.Z), naAgua, atingidos)   -- 20/11: onda real (dano + empurrao), visual 3D no cliente
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
		for _, pl in ipairs(game.Players:GetPlayers()) do if pl.Character and pl.UserId ~= modelo:GetAttribute("CavaleiroUserId") then table.insert(cands, pl.Character) end end   -- 20/11: o proprio cavaleiro nao conta
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
--   cabeca/pescoco do caido e MEXE A BOCA cravando os dentes (sem girar o corpo); interrompivel o tempo todo (alvo levanta/protegido/removido/ferido = solta,
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
	if not a:GetAttribute("Incapacitado") then
		local tl = tocarNaPresa(a, "Crocodilo_Levantar", false)
		if tl then tl.Stopped:Once(function() if a.Parent and not a:GetAttribute("Caido") and not a:GetAttribute("Incapacitado") then tocarNaPresa(a, "Crocodilo_Repouso", true) end end) end
	end
	log("CONTROLE: %s levantou", a.Name)
end
M.levantar = levantar
aplicarQueda = function(a, dur)                          -- (declarada no ARREMESSO)
	est.origQueda = est.origQueda or {}
	local orig = a:GetPivot(); est.origQueda[a] = orig
	a:SetAttribute("Caido", true); a:SetAttribute("CaidoAte", agora() + dur); a:SetAttribute("Derrubado", true)
	local _, sz = a:GetBoundingBox()
	-- 20/11 encaixe: presa com esqueleto proprio fica CAIDA com o clipe dela (deitada); boneco em pe sem clipes: tomba
	if not tocarNaPresa(a, "Crocodilo_DescansoDeitado", true) and sz.Y > math.max(sz.X, sz.Z) then a:PivotTo(orig * CFrame.Angles(math.rad(80), 0, 0) - Vector3.new(0, 1.5, 0)) end
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
		-- 20/11 ENCAIXE (usuario): escolhe a regiao do caido que CABE (prefere pescoco/cabeca), aproxima ate a boca ficar perto
		-- dela, poe a boca centralizada (de lado se a regiao estiver baixa) e fecha ate a espessura; nao cabe = so mordida
		local sim, nao = E.escolher(modelo, a, 40, F.ossosAlvo, nil, not est.naAgua and (modelo:GetPivot().Y - C_.pivo + CFG.Agarrao.altura_lado) or nil)
		local reg = sim or nao
		if not reg then cancelar("nenhuma regiao mordivel"); return end
		log("FINALIZACAO: regiao %s (%s)", reg.nome, sim and "cabe" or "NAO cabe")
		local yL = not est.naAgua and (modelo:GetPivot().Y - C_.pivo + CFG.Agarrao.altura_lado) or nil
		local offL = E.CENTRO_LOCAL                                -- onde fica o centro do vao na pose que vai usar (normal / de lado)
		if yL and reg.p.Y <= yL then offL = (modelo:GetPivot():PointToObjectSpace(reg.p).X > 0) and E.CENTRO_LADO_E or E.CENTRO_LADO_D end
		local phi = math.atan2(offL.X, -offL.Z)
		local andando
		local function marcha(nome) if andando ~= nome then andando = nome; T.tocar(nome, 0.2) end end
		local tAp = 0
		while true do
			local dt = RS.Heartbeat:Wait(); tAp += dt; if not valida() then return end
			local cf = modelo:GetPivot(); local Mp = cf * offL
			local dir = (reg.p - cf.Position) * Vector3.new(1, 0, 1)
			local look = Vector3.new(cf.LookVector.X, 0, cf.LookVector.Z).Unit
			local alvoDir = dir.Magnitude > 0.1 and CFrame.Angles(0, phi, 0):VectorToWorldSpace(dir.Unit) or look
			local ang = math.atan2(look:Cross(alvoDir).Y, look:Dot(alvoDir))
			local falta = (reg.p - Mp) * Vector3.new(1, 0, 1)
			if falta.Magnitude <= F.encostar + 0.6 and math.abs(ang) < math.rad(8) then break end   -- o resto o pegar corrige
			if tAp > F.abordarMax then cancelar("nao alcancou a tempo"); return end
			local nr = CFrame.Angles(0, math.clamp(ang, -F.giro * dt, F.giro * dt), 0) * cf.Rotation
			local desejado = reg.p - nr:VectorToWorldSpace(offL)
			local fp = (desejado - cf.Position) * Vector3.new(1, 0, 1)
			marcha((fp.Magnitude > 0.05 and fp:Dot(look) < 0) and "Crocodilo_ArrastarPresa" or "Crocodilo_Andar")   -- de re ou para a frente
			local np = cf.Position + (fp.Magnitude > 0.01 and fp.Unit * math.min(F.vel * dt, fp.Magnitude) or Vector3.zero)
			BASE = CFrame.new(np) * nr; modelo:PivotTo(BASE)
		end
		-- preso na boca nao consegue levantar: a queda dura ate o desfecho (se a finalizacao for interrompida, levanta depois)
		a:SetAttribute("CaidoAte", agora() + F.aperto + 1.4)
		task.delay(F.aperto + 1.4, function() if a.Parent and a:GetAttribute("Caido") and not a:GetAttribute("Incapacitado") and (a:GetAttribute("CaidoAte") or 0) <= agora() + 0.05 then levantar(a) end end)
		local r = pegar(g, a, est.naAgua, CFG.Agarrao.corrigir_final, F.ossosAlvo); M.ultimaPegada = r
		if est.gen ~= g then return end
		log("PEGADA %s (finalizacao): regiao %s, pose %s; %s%s", string.upper(r.modo), tostring(r.nome), tostring(r.pose), r.motivo or "",
			r.lateral and string.format(" | desvio lateral %.2f, vao %.2f, corrigiu %.2f, subiu %.2f", r.lateral, r.altura, r.andou or 0, r.subiu or 0) or "")
		if r.modo == "erro" then cancelar(r.motivo or "erro"); return end
		if not valida() then return end
		if r.modo == "mordida" then                                -- nao cabe: so a mordida de contato, sem esmagar
			h:TakeDamage(CFG.Agarrao.dano_contato)
			log("FINALIZACAO: %s nao cabe na boca -> SO MORDIDA (dano %d, sem prender nem esmagar)", r.nome, CFG.Agarrao.dano_contato)
			limpa(); local fs = T.tocar("Crocodilo_SoltarPresa", 0.15); fs.Stopped:Wait()
			if est.gen == g then M.cancelar("finalizacao_so_mordida") end
			return
		end
		est.alvo = a; fixarPegada(g, a, r)
		log("FINALIZACAO: prendeu %s pela %s (espessura %.2f, abertura %.1f graus); crava", a.Name, r.nome, r.tU, r.alfa)
		local t1 = 0; while t1 < 0.15 do t1 += RS.Heartbeat:Wait(); if not valida() then return end end
		-- MORDIDA ESMAGADORA no par da pose (mesma abertura de contato): o corpo fica firme; so a boca/cabeca trabalham
		local fm = tocarPar(r.baseEsm, r.w, 0.12); est.pegada.base = r.baseEsm
		for _, mk in ipairs({"crava1", "crava2"}) do
			table.insert(est.cons, fm:GetMarkerReachedSignal(mk):Connect(function()
				if est.gen ~= g or not est.pegada then return end
				local pg = est.pegada; local b2 = E.boca(modelo); local pw = a:GetPivot() * pg.pontoLocal
				local s = E.secao(a, pw, b2.F, b2.U); local aMed = alfaAtual()
				if s then                                            -- dano so com o corpo de verdade entre as arcadas
					h:TakeDamage(F.danoCrava)
					log("FINALIZACAO: %s - dentes cravam (dano %d; espessura %.2f x vao %.2f a %.1f graus)", mk, F.danoCrava, s.tU, E.folga(aMed, pg.d), aMed)
				else log("FINALIZACAO: %s sem corpo entre as arcadas (sem dano)", mk) end
			end))
		end
		local t2 = 0
		while t2 < F.aperto and fm.IsPlaying do t2 += RS.Heartbeat:Wait(); if not valida() then return end end
		local pg = est.pegada
		if pg then log("FIM DA PEGADA: penetracao max %.2f, deriva max %.3f (espessura %.2f, abertura %.1f)", pg.penMax, pg.derMax, pg.tU, pg.alfa) end
		-- desfecho (para de segurar antes: o corpo fica onde caiu)
		est.alvo = nil; est.ponto = nil; est.pegada = nil
		if deJogador(a) then
			a:SetAttribute("RetiradaDeCombate", true); a:SetAttribute("Incapacitado", true)
			log("FINALIZACAO: %s (criatura de jogador) RETIRADA da luta -> refugio (simulado; Vida %.0f mantida, sem morte)", a.Name, h.Health)
		else
			h.Health = 0; a:SetAttribute("Estado", "Morto"); a:SetAttribute("Incapacitado", true)
			tocarNaPresa(a, "Crocodilo_Morte", false, true)
			log("FINALIZACAO: %s (selvagem) morreu (prototipo: sem loot/respawn)", a.Name)
		end
		limpa()
		local fs = T.tocar("Crocodilo_SoltarPresa", 0.15)
		fs.Stopped:Wait()
		if est.gen == g then M.cancelar("fim_finalizacao") end
	end)
	return "iniciado"
end

-- ================================================================ MONTARIA (20/11, 1a entrega) [PROPOSTA de numeros]
-- Usuario 20/11: botao "Montar [E]" perto da sela (sobe pelo lado em que esta, clipe daquele lado; a mesma tecla desce);
-- controle pela DIRECAO DA CAMERA (WASD/analogico; Shift corre) com o crocodilo virando com peso; na agua NADA NA
-- SUPERFICIE (Submersao montada bloqueada ate decidir o mergulho com cavaleiro); poderes montado ficam para depois.
-- AUTORIDADE DO SERVIDOR: o cliente so manda a intencao (direcao no plano + correr, ~15 Hz); o servidor valida (cavaleiro
-- certo, fase, vetor finito, pacote velho), integra velocidade/giro, acha chao/agua e move o modelo por PivotTo.
-- Cavaleiro: Seat invisivel soldado ao corpo (Assento_Sela, criado na instalacao); subir/descer = clipe do crocodilo +
-- trajetoria do jogador conduzida pelo servidor (HRP ancorada so durante a subida/descida). Um cavaleiro por vez.
local Players_ = game:GetService("Players")
local RepS_ = game:GetService("ReplicatedStorage")
local MC = CFG.Montaria
local mont = {fase = "livre"}                               -- livre | subindo | montado | descendo
local function remotoMont(nome, classe)
	local p = RepS_:FindFirstChild("Crocodilo_Montaria") or Instance.new("Folder"); p.Name = "Crocodilo_Montaria"; p.Parent = RepS_
	local r = p:FindFirstChild(nome) or Instance.new(classe); r.Name = nome; r.Parent = p; return r
end
local function faseMont(f)
	mont.fase = f; est.montadoFase = (f ~= "livre") and f or nil
	modelo:SetAttribute("FaseMontaria", f); modelo:SetAttribute("Montado", f == "montado" or f == "subindo" or f == "descendo")
end
local function chaoMont(pos)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude; p.IgnoreWater = true
	local ign = {modelo, workspace.Teste_Crocodilo:FindFirstChild("Arena"), workspace.Teste_Crocodilo:FindFirstChild("Crocodilo_Sela")}
	for _, pl in ipairs(Players_:GetPlayers()) do if pl.Character then table.insert(ign, pl.Character) end end
	p.FilterDescendantsInstances = ign
	local r = workspace:Raycast(Vector3.new(pos.X, pos.Y + 12, pos.Z), Vector3.new(0, -80, 0), p)
	return r and r.Position.Y
end
local function hrpDe(plr) local c = plr and plr.Character; return c and c:FindFirstChild("HumanoidRootPart"), c and c:FindFirstChildOfClass("Humanoid") end
-- conduz a HRP (ancorada) por uma curva ate o destino, acompanhando o crocodilo (destino em coordenadas do crocodilo)
-- r2 20/11 (usuario: "quero a montaria igual haviamos montado no blender"): o cavaleiro segue o movimento do cavaleiro de
-- TESTE aprovado no Lote 5 (CavaleiroCrocodilo, exportado do Blender): subir/descer = o centro do LowerTorso percorre o
-- caminho do Blender (espaco do pivo do crocodilo), sincronizado com o clipe do crocodilo; o cliente dobra as juntas R15
-- (pe no cotovelo, perna pela garupa, montado de pernas abertas, desce pelo flanco) e, montado, o quadril segue a Coluna2.
local CAV = require(RepS_:WaitForChild("CavaleiroCrocodilo"))
local function cavQuadro(acao, t)                          -- CFrame local (pivo) do LowerTorso no tempo t (interpolado)
	local a = CAV.acoes[acao]; local n = a.n
	local x = math.clamp(t * CAV.fps, 0, n - 1); local i = math.floor(x); local u = x - i; local j = math.min(i + 1, n - 1)
	local function p(k) return Vector3.new(a.lt[3 * k + 1], a.lt[3 * k + 2], a.lt[3 * k + 3]) end
	local r = a.r.LowerTorso
	local function q(k) return CFrame.new(0, 0, 0, r[4 * k + 1], r[4 * k + 2], r[4 * k + 3], r[4 * k + 4]) end
	return CFrame.new(p(i):Lerp(p(j), u)) * q(i):Lerp(q(j), u)
end
local function hrpParaLT(plr, ltWorld)                      -- HRP tal que o LowerTorso (Root sem Transform) caia em ltWorld
	local c = plr.Character; local root = c and c:FindFirstChild("LowerTorso") and c.LowerTorso:FindFirstChild("Root")
	if root and root:IsA("Motor6D") then return ltWorld * root.C1 * root.C0:Inverse() end
	if root and root.ClassName == "AnimationConstraint" and root.Attachment0 and root.Attachment1 then   -- avatar novo (juntas fisicas)
		return ltWorld * root.Attachment1.CFrame * root.Attachment0.CFrame:Inverse()
	end
	return ltWorld * CFrame.new(0, 0.8, 0)                     -- (sem R15: aproximado)
end
local function marcarAcao(acao) modelo:SetAttribute("CavAcao", acao); modelo:SetAttribute("CavT0", workspace:GetServerTimeNow()) end
-- conduz a HRP (ancorada) pelo caminho do Blender; nos primeiros `junta` s mistura a partir de onde o jogador estava
local function seguirCaminho(plr, hrp, acao, tok, junta)
	local dur = CAV.acoes[acao].dur; local t = 0; local de = hrp.CFrame
	while t < dur do
		t += RS.Heartbeat:Wait(); if mont.tok ~= tok or not hrp.Parent then return false end
		local alvo = hrpParaLT(plr, modelo:GetPivot() * cavQuadro(acao, t))
		if junta and t < junta then local u = t / junta; u = u * u * (3 - 2 * u); alvo = de:Lerp(alvo, u) end
		hrp.CFrame = alvo
	end
	return true
end
local function sentarComoBlender(plr, hum, seat)            -- ajusta a solda do assento para a pose sentada do Blender
	local w = seat:FindFirstChild("SeatWeld"); local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
	if not (w and hrp) then return end
	local desejado = hrpParaLT(plr, modelo:GetPivot() * cavQuadro("Sentado", 0))
	w.C1 = CFrame.identity; w.C0 = seat.CFrame:ToObjectSpace(desejado)
end

local function liberarMont(seat)
	mont.plr = nil; mont.dir = nil; faseMont("livre"); modelo:SetAttribute("CavaleiroUserId", nil); modelo:SetAttribute("CavAcao", nil)
	if seat and seat:FindFirstChildOfClass("ProximityPrompt") then seat:FindFirstChildOfClass("ProximityPrompt").Enabled = true end
end
local function desmontar(motivo, imediato)
	if mont.fase ~= "montado" and mont.fase ~= "subindo" then return end
	mont.tok = (mont.tok or 0) + 1; local tok = mont.tok
	local plr, lado = mont.plr, mont.lado or "E"
	local hrp, hum = hrpDe(plr)
	local seat = modelo:FindFirstChild("Assento_Sela")
	local w = seat and seat:FindFirstChild("SeatWeld"); if w then w:Destroy() end
	if hum then hum.Sit = false end
	log("DESMONTAR (%s): %s pelo lado %s", motivo, plr and plr.Name or "?", lado)
	if imediato or not (hrp and hum and hum.Health > 0) then
		if hrp then hrp.Anchored = false end
		liberarMont(seat); T.tocar("Crocodilo_Repouso", 0.2); return
	end
	faseMont("descendo"); mont.v = 0
	local acao = (lado == "E") and "Desmontar" or "DesmontarDireita"
	T.tocar("Crocodilo_" .. acao, 0.15); marcarAcao(acao)
	hrp.Anchored = true
	task.spawn(function()
		seguirCaminho(plr, hrp, acao, tok, 0.15)
		if mont.tok ~= tok then return end
		if hrp.Parent then
			local p = hrp.CFrame; local y = chaoMont(p.Position)
			local _, ry = p:ToOrientation()
			hrp.CFrame = CFrame.new(p.X, (y or (p.Y - 3)) + 3.0, p.Z) * CFrame.Angles(0, ry, 0)   -- em pe no chao real
			hrp.Anchored = false
		end
		liberarMont(seat); T.tocar("Crocodilo_Repouso", 0.25)
		log("DESMONTADO: %s no chao do lado %s (caminho do Blender)", plr.Name, lado)
	end)
end

local function montar(plr)
	if mont.fase ~= "livre" then log("MONTAR recusado (%s): ja ha cavaleiro/fase %s", plr.Name, mont.fase); return end
	if est.poder then log("MONTAR recusado (%s): crocodilo usando %s", plr.Name, est.poder); return end
	if modelo:GetAttribute("Submerso") then log("MONTAR recusado (%s): crocodilo submerso", plr.Name); return end
	local hrp, hum = hrpDe(plr); local seat = modelo:FindFirstChild("Assento_Sela")
	if not (hrp and hum and hum.Health > 0 and seat) then return end
	local d = (hrp.Position - seat.Position).Magnitude
	if d > MC.raio + 2 then log("MONTAR recusado (%s): longe (%.1f)", plr.Name, d); return end
	if hum.Sit or hum.SeatPart then log("MONTAR recusado (%s): ja sentado em outra coisa", plr.Name); return end
	local xl = modelo:GetPivot():PointToObjectSpace(hrp.Position).X
	local lado = (xl < 0) and "E" or "D"                                        -- E = -X local (convencao giro180y medida)
	mont.plr = plr; mont.lado = lado; mont.v = 0; mont.dir = nil; mont.correr = false; mont.tIn = 0
	do local sp, fp = medirAgua(modelo:GetPivot().Position); mont.naAgua = sp ~= nil and (sp - fp) >= C_.olhos end   -- estado inicial (nao toca SaidaAgua ao montar)
	mont.tok = (mont.tok or 0) + 1; local tok = mont.tok
	seat:FindFirstChildOfClass("ProximityPrompt").Enabled = false
	faseMont("subindo"); modelo:SetAttribute("CavaleiroUserId", plr.UserId)
	local acao = (lado == "E") and "Montar" or "MontarDireita"
	log("MONTAR: %s pelo lado %s (x local %.1f, a %.1f da sela) - caminho do Blender %s", plr.Name, lado, xl, d, acao)
	T.tocar("Crocodilo_" .. acao, 0.15); marcarAcao(acao)
	hrp.Anchored = true
	task.spawn(function()
		local ok = seguirCaminho(plr, hrp, acao, tok, MC.junta_inicio)
		if mont.tok ~= tok or not ok then return end
		hrp.Anchored = false
		if not (hum.Parent and hum.Health > 0) then desmontar("morreu_subindo", true); return end
		seat:Sit(hum); mont.sentouEm = os.clock()
		task.wait(); sentarComoBlender(plr, hum, seat)
		faseMont("montado"); marcarAcao("Sentado"); T.tocar("Crocodilo_Repouso", 0.25); mont.anim = "Repouso"
		log("MONTADO: %s na sela (lado %s), pose sentada do Blender", plr.Name, lado)
	end)
end

-- integra a locomocao montada (so com cavaleiro sentado)
local function animMont(nome, vel, fade)
	if mont.anim ~= nome then mont.anim = nome; mont.track = T.tocar("Crocodilo_" .. nome, fade or 0.25, vel or 1)
	elseif mont.track and vel then mont.track:AdjustSpeed(vel) end
end
local function difAngM(a, b) local d = (b - a) % (2 * math.pi); if d > math.pi then d -= 2 * math.pi end; return d end
local function passoMont(dt)
	if mont.fase ~= "montado" then return end
	local plr = mont.plr; local hrp, hum = hrpDe(plr)
	local seat = modelo:FindFirstChild("Assento_Sela")
	if not (hrp and hum and hum.Health > 0) then desmontar("cavaleiro_invalido", true); return end
	if seat and seat.Occupant ~= hum and os.clock() - (mont.sentouEm or 0) > 0.6 then desmontar("saiu_da_sela", false); return end
	local dir = mont.dir
	if os.clock() - (mont.tIn or 0) > MC.timeout then dir = nil end            -- pacote velho = solta o comando
	local cf = modelo:GetPivot(); local pos = cf.Position
	local sup, fundo = medirAgua(pos)
	local naAgua = sup ~= nil and (sup - fundo) >= C_.olhos
	if naAgua ~= mont.naAgua then
		mont.naAgua = naAgua; est.naAgua = naAgua
		log("MONTADO: %s", naAgua and "ENTROU NA AGUA -> nada na superficie" or "SAIU DA AGUA -> anda em terra")
		mont.anim = nil; mont.track = T.tocar(naAgua and "Crocodilo_EntradaAgua" or "Crocodilo_SaidaAgua", 0.2); mont.transAte = os.clock() + (naAgua and 1.2 or 1.4)
	end
	local alvoV = 0
	if dir then alvoV = naAgua and (mont.correr and MC.vel_nado * MC.nado_rapido or MC.vel_nado) or (mont.correr and MC.vel_corrida or MC.vel_andar) end
	local ac = (alvoV > mont.v) and (naAgua and MC.acel_nado or MC.acel) or MC.frear
	mont.v = mont.v + math.clamp(alvoV - mont.v, -ac * dt, ac * dt)
	-- giro com peso
	local _, yaw = cf:ToOrientation(); local giro = 0
	if dir then
		local yawAlvo = math.atan2(-dir.X, -dir.Z)                                 -- LookVector = -Z local
		local d = difAngM(yaw, yawAlvo)
		local taxa = math.rad(naAgua and MC.giro_nado or (mont.v > MC.vel_andar * 1.3 and MC.giro_corrida or (mont.v > 0.3 and MC.giro_andar or MC.giro_parado)))
		giro = math.clamp(d, -taxa * dt, taxa * dt); yaw += giro
	end
	local rot = CFrame.Angles(0, yaw, 0)
	local novo = pos + rot.LookVector * mont.v * dt
	local y
	if naAgua then
		local s2 = select(1, medirAgua(novo)) or sup
		y = yEspreita(s2) + MC.nado_extra
	else
		local ch = chaoMont(novo)
		if not ch or (ch + C_.pivo - pos.Y) > MC.degrau_max then novo = pos; mont.v = 0; ch = chaoMont(pos) end   -- sem chao/parede a frente: para (descer e livre)
		y = (ch or (pos.Y - C_.pivo)) + C_.pivo
		y = pos.Y + math.clamp(y - pos.Y, -MC.subida_s * dt, MC.subida_s * dt)       -- sobe/desce suave no relevo
	end
	BASE = CFrame.new(novo.X, y, novo.Z) * rot; modelo:PivotTo(BASE)
	-- animacao (patas casadas com a velocidade do clipe)
	if mont.transAte and os.clock() < mont.transAte then return end
	if naAgua then
		if mont.v < 0.6 then animMont("NadoParado", 1) else animMont("Nado", math.clamp(mont.v / MC.vel_nado, 0.6, 1.6)) end
	else
		if mont.v < 0.25 then
			if math.abs(giro) > 0.0005 then animMont(giro > 0 and "VirarEsquerda" or "VirarDireita", 1) else animMont("Repouso", 1, 0.35) end
		elseif mont.v <= MC.vel_andar * 1.3 then animMont("Andar", mont.v / MC.vel_andar_clipe)
		else animMont("Corrida", mont.v / MC.vel_corrida_clipe) end
	end
end

function M.montariaIniciar()
	if mont.ligada then return "ja ligada" end
	local seat = modelo:FindFirstChild("Assento_Sela"); if not seat then return "sem Assento_Sela (rodar a instalacao)" end
	mont.ligada = true; faseMont("livre")
	local pr = seat:FindFirstChildOfClass("ProximityPrompt")
	local Cmd, Ent = remotoMont("Comando", "RemoteEvent"), remotoMont("Entrada", "UnreliableRemoteEvent")
	pr.Triggered:Connect(function(plr) montar(plr) end)
	Cmd.OnServerEvent:Connect(function(plr, acao)
		if acao == "desmontar" then
			if plr ~= mont.plr then log("DESMONTAR recusado: %s nao e o cavaleiro", plr.Name); return end
			desmontar("pedido", false)
		end
	end)
	Ent.OnServerEvent:Connect(function(plr, dir, correr)
		if plr ~= mont.plr or mont.fase ~= "montado" then mont.recusados = (mont.recusados or 0) + 1; return end
		if typeof(dir) ~= "Vector3" or dir ~= dir or dir.Magnitude > 1.05 or math.abs(dir.X) == math.huge then mont.recusados = (mont.recusados or 0) + 1; return end
		local p = Vector3.new(dir.X, 0, dir.Z)
		mont.dir = (p.Magnitude > 0.1) and p.Unit or nil; mont.correr = (correr == true); mont.tIn = os.clock()
	end)
	Players_.PlayerRemoving:Connect(function(plr) if plr == mont.plr then desmontar("jogador_saiu", true) end end)
	RS.Heartbeat:Connect(function(dt) if mont.fase == "montado" then passoMont(dt) end end)
	log("MONTARIA ligada (botao Montar na sela, raio %d)", MC.raio)
	return "ok"
end
function M.montariaEstado() return {fase = mont.fase, cavaleiro = mont.plr and mont.plr.Name, lado = mont.lado, v = mont.v, naAgua = mont.naAgua, recusados = mont.recusados or 0} end

function M.estado() return {poder = est.poder, fase = est.fase, alvo = est.alvo and est.alvo.Name or nil, naAgua = est.naAgua} end
return M

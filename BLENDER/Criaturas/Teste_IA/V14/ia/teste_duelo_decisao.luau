-- v2 (11/11, pedido "Duelo Glacial x Sombrio — posicionamento e obstaculos"): POSICAO de ataque verificada antes do golpe
--   (visao, rota livre para corpo+asas, espaco para virar, saida livre do Glacial); ROTAS em volta de obstaculo a partir do
--   ultimo ponto visto (esquerda/direita/por cima, passagem inteira e chegada verificadas, troca so sem progresso); FOLGA
--   das asas na colisao e correcao suave; metricas de visao, abortos, rotas e consultas. v1 = teste_duelo_decisao_v1.luau.
-- teste_duelo_decisao.luau (Studio, PLAY, servidor; enviado inline) — DUELO DE IA Glacial x Sombrio (11/11, pedido
-- "IA dos dragoes — duelo de teste entre Glacial e Sombrio"). So TESTE: nao altera scripts do jogo; tudo que cria fica em
-- workspace._Duelo_Temp e as copias Duelo_* (removidos por _G.DueloLimpar()). Sucessor do teste_duelo_tatico.luau (v11).
-- O QUE MUDA em relacao ao tatico (planos sorteados por pontuacao):
-- * FASES com motivo registrado: AMEACAR -> APROXIMAR -> ATACAR -> RECUPERAR -> REPOSICIONAR, mais ESQUIVAR, RECUAR,
--   PERSEGUIR, INVESTIGAR (ultimo ponto visto) e PATRULHA; compromisso minimo por fase, interrupcao so por ameaca real
--   (golpe mirado em mim), obstaculo ou perda de visao.
-- * GOLPE escolhido pela situacao: distancia, angulo (frente/flanco/costas), linha de visao (raio no terreno e nos
--   obstaculos), diferenca de altura, energia e recarga (Nucleo:podeUsar). Mordida/garra de frente e perto, cauda pelo
--   flanco/costas, sopro com linha livre e distancia util, Correntes/Rajadas no alcance longo, area (Zero Absoluto,
--   Nevasca, Eclipse) so quando a posicao e o kit justificam (Eclipse: so com Marcas no alvo).
-- * DANO REAL do jogo: as copias sao "guardioes derrotaveis" com dono ficticio (DonoUserId = -1, GuardiaoNinho = ninho
--   inexistente, IA_Ativa = false) -> o Nucleo de cada um ve o outro como alvo valido e aplica alcance, cone, linha de visao,
--   Marcas Sombrias, Frostbite e Vida/VidaMax (N.danoGuardiao). Acerto = queda de Vida no alvo durante o golpe. Recargas,
--   alcances e danos = ConfigCombate (NAO_APROVADO). So VidaMax e os parametros de decisao abaixo sao EXPERIMENTAIS.
-- * ESQUIVA com tempo de reacao, checagem de espaco lateral (obstaculo/borda da arena) e intervalo entre esquivas; o golpe
--   ja lancado pode acertar (o acerto e decidido pelo Nucleo no impacto, nao pela esquiva).
-- * COLISAO por capsulas (cabeca -> base da cauda, raio do corpo): sem corpo dentro de corpo, mas permite chegar ao alcance
--   da mordida e ficar de lado para a cauda.
-- Uso: _G.DUELO_CENARIO = "equilibrado" | "altura" | "ferido" (+ _G.DUELO_INVERTER = true troca quem comeca em
-- desvantagem) | "esquiva" | "visao"; _G.DUELO_DUR (s). Resultado em _G.Duelo (log, contagens, checagens).
_G.DueloIniciar = function()   -- (instalado uma vez por Play; cada chamada roda um cenario)
math.randomseed(_G.DUELO_SEMENTE or 7)
local SSS, RS, SS = game:GetService("ServerScriptService"), game:GetService("ReplicatedStorage"), game:GetService("ServerStorage")
local RunService = game:GetService("RunService")
local N = require(SSS.Combate_Dragao.Nucleo)
local Passivas = require(SSS.Combate_Dragao.Passivas)
local CfgC = require(SSS.Combate_Dragao.ConfigCombate)
local Locomotor = require(SSS.IA_Dragao.Locomotor)
local EstadosDragao = require(RS.Comportamento_Dragoes.EstadosDragao)
local Cfg = require(SSS.IA_Dragao.Config)
local Y = Vector3.yAxis
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function unit(v, alt) return v.Magnitude > 1e-3 and v.Unit or (alt or Vector3.zAxis) end
local function nan(v) return v.X ~= v.X or v.Y ~= v.Y or v.Z ~= v.Z or math.abs(v.Y) > 1e5 end
local CEN = _G.DUELO_CENARIO or "equilibrado"; local INV = _G.DUELO_INVERTER == true
-- ===== parametros EXPERIMENTAIS (so deste teste) =====
local X = {VIDA = 320, DUR = _G.DUELO_DUR or 100, CENTRO = Vector3.new(700, 0, 472), ARENA = 230,
	VCRUZ = 34, VRAPIDO = 58, VSUB = 24, VDESCE = 50, ACEL = 38,
	COMPROMISSO = 1.2, RECUP = {0.9, 1.7}, ESQ_INTERVALO = 4.0, RUGIDO_INTERVALO = 20,
	RECUO_VIDA = 0.4, RECUO_MAX = 7, PERSEG_MAX = 10, INVEST_MAX = 6, PATRULHA = 5, VISAO = 320,
	POS_REAVALIA = 1.2, CHEGOU = 18, ROTA_PROGRESSO = 1.5, SUBIDA_MAX = 80, LONGE_RIVAL = 55, CONSULTAS_SEG = 45,
	FOLGA_ASA = 6, EMPURRA_MAX = 60}
-- personalidade: mesma logica, pesos diferentes (Sombrio: flancos/emboscada/Marcas; Glacial: controle de faixa e punicao)
local PERS = {
	Sombrio = {faixa = {55, 100}, flanco = 0.75, reacao = {0.25, 0.45}, voa = 0.55, segura = false, titulo = "Dragao Sombrio", cor = Color3.fromRGB(150, 80, 230)},
	Glacial = {faixa = {110, 165}, flanco = 0.1, reacao = {0.35, 0.6}, voa = 0.2, segura = true, titulo = "Dragao Glacial", cor = Color3.fromRGB(120, 200, 255)},
}
-- dificuldade: so DECISAO (variacao de posicionamento e aproveitamento de abertura); alcance/recarga/acerto iguais
local DIF = {guardiao = {variacao = 1.0, abertura = 0.8}, comum = {variacao = 0.4, abertura = 0.45}}
_G.Duelo = {ativo = true, log = {}, cont = {}, ataques = {}, checa = {sobrepMax = 0, travasVoo = 0, semLOS = 0, repeticoes = {}, folgaAsaMin = math.huge, golpeAtravessa = 0},
	cenario = CEN .. (INV and "_inv" or ""), tvisao = {}, rotas = {}, cons = {Sombrio = 0, Glacial = 0}, dec = {n = 0, soma = 0, max = 0}}
local D = _G.Duelo; D.t0 = os.clock()
local function agora() return os.clock() - D.t0 end
local function log(s) table.insert(D.log, ("%5.1f %s"):format(agora(), s)) end
local function conta(k) D.cont[k] = (D.cont[k] or 0) + 1 end
-- ===== arena, obstaculos e copias =====
local temp = workspace:FindFirstChild("_Duelo_Temp") or Instance.new("Folder"); temp.Name = "_Duelo_Temp"; temp.Parent = workspace
local parque = SS:FindFirstChild("_Duelo_Parque") or Instance.new("Folder"); parque.Name = "_Duelo_Parque"; parque.Parent = SS
local rpT = RaycastParams.new(); rpT.FilterType = Enum.RaycastFilterType.Include
local function chaoY(p) rpT.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("Baseplate")}; local h = workspace:Raycast(Vector3.new(p.X, 600, p.Z), Vector3.new(0, -1200, 0), rpT); return h and h.Position.Y or 0 end
local obst = {}
local function rocha(off, alt, larg)                                  -- coluna de rocha so do teste (visao e parede)
	local b = X.CENTRO + off; local g = chaoY(b)
	local p = Instance.new("Part"); p.Name = "_Duelo_Rocha"; p.Anchored = true; p.Material = Enum.Material.Slate; p.Color = Color3.fromRGB(92, 88, 84)
	p.Size = Vector3.new(larg, alt, larg); p.Position = Vector3.new(b.X, g + alt / 2 - 2, b.Z); p.Parent = temp; table.insert(obst, p)
end
if (CEN ~= "equilibrado" and CEN ~= "estreito" and CEN ~= "porcima") or _G.DUELO_ROCHAS then rocha(Vector3.new(-25, 0, 10), 70, 34); rocha(Vector3.new(110, 0, -70), 55, 28) end
if CEN == "esquiva" then rocha(Vector3.new(-120, 0, 60), 60, 30) end      -- parede junto do Glacial: esquiva sem espaco
local rpV = RaycastParams.new(); rpV.FilterType = Enum.RaycastFilterType.Include
local QUEM = nil                                                            -- dragao que esta decidindo (conta as consultas)
local function contaC() if QUEM then D.cons[QUEM.forma] += 1; QUEM.consJan = (QUEM.consJan or 0) + 1 end end
local function linhaLivre(a, b) contaC(); rpV.FilterDescendantsInstances = {workspace.Terrain, temp}; return workspace:Raycast(a, b - a, rpV) == nil end
local function raio(a, d) contaC(); rpV.FilterDescendantsInstances = {workspace.Terrain, temp}; return workspace:Raycast(a, d, rpV) end
local function esfera(a, r, d) contaC(); rpV.FilterDescendantsInstances = {workspace.Terrain, temp}; return workspace:Spherecast(a, r, d, rpV) end
local function orcamento(F) return (F.consJan or 0) < X.CONSULTAS_SEG end
local function centroEsfera(q, r, noAr) if noAr then return q end; return Vector3.new(q.X, chaoY(q) + r + 3, q.Z) end   -- (v2) esfera nao raspa o chao
local function copia(nome, pos, olhar)
	local o = workspace:FindFirstChild(nome) or parque:FindFirstChild(nome); assert(o, nome)
	local c = o:Clone(); c.Name = "Duelo_" .. nome
	for _, d in ipairs(c:GetDescendants()) do if d:IsA("ProximityPrompt") or d.Name == "VidaDuelo" then d:Destroy() end end
	c:SetAttribute("PastaAnimacoes", nome); c:SetAttribute("Controlador", "TesteDuelo"); c:SetAttribute("IA_Ativa", false)
	c:SetAttribute("DonoUserId", -1); c:SetAttribute("GuardiaoNinho", "_Duelo_NinhoFicticio")   -- alvo valido do Nucleo (dano real)
	c:SetAttribute("VidaMax", X.VIDA); c:SetAttribute("Vida", X.VIDA); c:SetAttribute("Incapacitado", nil)
	local g = chaoY(pos); local alt = o:GetPivot().Position.Y - chaoY(o:GetPivot().Position)
	c:PivotTo(CFrame.lookAt(Vector3.new(pos.X, g + alt, pos.Z), Vector3.new(olhar.X, g + alt, olhar.Z)))
	c.Parent = workspace
	return c
end
for _, m in ipairs(workspace:GetChildren()) do
	if m:IsA("Model") and m:GetAttribute("FormaRegional") and not m.Name:match("^Duelo_") then m.Parent = parque end
end
local pS, pG = X.CENTRO + Vector3.new(0, 0, 85), X.CENTRO - Vector3.new(0, 0, 85)
if CEN == "visao" then pS, pG = X.CENTRO + Vector3.new(-25, 0, 95), X.CENTRO + Vector3.new(-25, 0, -75) end   -- rocha entre os dois
local function parede(cf, tam)
	local q = Instance.new("Part"); q.Name = "_Duelo_Parede"; q.Anchored = true; q.Material = Enum.Material.Slate; q.Color = Color3.fromRGB(92, 88, 84)
	q.Size = tam; q.CFrame = cf; q.Parent = temp; table.insert(obst, q)
end
local g0 = chaoY(X.CENTRO)
if CEN == "estreito" then                        -- corredor de 44 studs (mais estreito que a envergadura) fechado no fundo
	pS, pG = X.CENTRO + Vector3.new(0, 0, 120), X.CENTRO - Vector3.new(0, 0, 110)
	for _, x in ipairs({-32, 32}) do parede(CFrame.new(X.CENTRO.X + x, g0 + 53, X.CENTRO.Z), Vector3.new(20, 110, 130)) end
	parede(CFrame.new(X.CENTRO.X, g0 + 53, X.CENTRO.Z - 55), Vector3.new(84, 110, 20))
elseif CEN == "porcima" then                     -- muro longo e baixo: contornar e longe, passar por cima e curto
	pS, pG = X.CENTRO + Vector3.new(0, 0, 90), X.CENTRO - Vector3.new(0, 0, 70)
	parede(CFrame.new(X.CENTRO.X, g0 + 19, X.CENTRO.Z), Vector3.new(320, 38, 22))
end
if INV and (CEN == "visao" or CEN == "estreito" or CEN == "porcima" or CEN == "equilibrado") then pS, pG = pG, pS end   -- troca os lados iniciais
local cS = copia("Sombrio", pS, X.CENTRO); local cG = copia("Glacial", pG, X.CENTRO)
-- ===== rotulo (vida real + fase/motivo) =====
local function rotulo(F)
	local bg = Instance.new("BillboardGui"); bg.Name = "VidaDuelo"; bg.Size = UDim2.fromOffset(260, 54); bg.StudsOffset = Vector3.new(0, 26, 0)
	bg.AlwaysOnTop = true; bg.Adornee = F.m.PrimaryPart; bg.Parent = F.m.PrimaryPart
	local function txt(y, tam, cor) local t = Instance.new("TextLabel"); t.Position = UDim2.fromOffset(0, y); t.Size = UDim2.new(1, 0, 0, tam + 2); t.BackgroundTransparency = 1
		t.TextColor3 = cor; t.TextStrokeTransparency = 0.3; t.Font = Enum.Font.GothamBold; t.TextSize = tam; t.Parent = bg; return t end
	txt(0, 15, Color3.new(1, 1, 1)).Text = F.P.titulo
	local fundo = Instance.new("Frame"); fundo.Position = UDim2.fromOffset(0, 18); fundo.Size = UDim2.new(1, 0, 0, 10); fundo.BackgroundColor3 = Color3.fromRGB(30, 30, 34); fundo.Parent = bg
	local cheio = Instance.new("Frame"); cheio.Size = UDim2.fromScale(1, 1); cheio.BackgroundColor3 = F.P.cor; cheio.BorderSizePixel = 0; cheio.Parent = fundo
	F.barra, F.rotulo = cheio, txt(31, 13, Color3.fromRGB(255, 225, 140))
end
local function vida(F) return F.m:GetAttribute("Vida") or 0 end
local function lutador(m, forma, dif)
	local E = EstadosDragao.novo(m)
	local F = {m = m, forma = forma, P = PERS[forma], DIF = DIF[dif], E = E, L = Locomotor.novo(m, E, Cfg), N = N.registrar(m),
		vel = Vector3.zero, spd = 0, fase = "INICIO", faseDesde = os.clock(), motivo = "", ultEsq = -99, ultRugido = -99,
		trans = false, ponto = nil, rapido = false, golpes = {}, perdas = {}, ultGolpes = {}, visto = os.clock(), ultimoVisto = nil}
	F.N.energia = CfgC.energiaMax
	F.cabeca = m:FindFirstChild("Cabeca", true); F.cauda = m:FindFirstChild("Cauda3", true) or m:FindFirstChild("tail_3", true)
	F.quadril = m:FindFirstChild("Quadril", true); F.raio = (m:GetAttribute("CorpoRaio") or 8)
	F.asaE = m:FindFirstChild("wing_tip_l", true); F.asaD = m:FindFirstChild("wing_tip_r", true)
	F.meiaEnv = (F.asaE and F.asaD) and (F.asaE.TransformedWorldCFrame.Position - F.asaD.TransformedWorldCFrame.Position).Magnitude / 2 or 24
	F.largura = math.max(F.raio, F.meiaEnv * 0.75) + 4                     -- meia largura para rotas (asas abertas, um pouco recolhidas na curva)
	rotulo(F); return F
end
local S = lutador(cS, "Sombrio", "guardiao"); local G = lutador(cG, "Glacial", "guardiao")
log(("LARGURAS: Sombrio meia envergadura %.0f (rota %.0f) | Glacial meia envergadura %.0f (rota %.0f)"):format(S.meiaEnv, S.largura, G.meiaEnv, G.largura))
S.inimigo, G.inimigo = G, S
local function pos(F) return F.L:pos() end
-- ===== cenarios =====
local fraco = INV and S or G                                                -- quem comeca em desvantagem
if CEN == "ferido" then fraco.m:SetAttribute("Vida", math.floor(X.VIDA * 0.35)); log("CENARIO ferido: " .. fraco.P.titulo .. " comeca com 35% da vida") end
if CEN == "altura" then
	local alto = INV and G or S; alto.alturaInicial = 75
	log("CENARIO altura: " .. alto.P.titulo .. " comeca no ar, 75 studs acima do outro")
end
if CEN == "esquiva" then log("CENARIO esquiva: rocha junto do Glacial (lado esquerdo) para testar esquiva sem espaco") end
if CEN == "visao" then log("CENARIO visao: rocha entre os dois no inicio (sem linha de visao)" .. (INV and " — lados trocados" or "")) end
if CEN == "estreito" then log("CENARIO estreito: corredor de 44 studs fechado no fundo entre os dois (paredes de 110)" .. (INV and " — lados trocados" or "")) end
if CEN == "porcima" then log("CENARIO por cima: muro de 320 x 38 entre os dois (contorno longo, passagem por cima curta)" .. (INV and " — lados trocados" or "")) end
local function atualizarBarra(F) F.barra.Size = UDim2.fromScale(math.clamp(vida(F) / X.VIDA, 0, 1), 1) end
for _, F in ipairs({S, G}) do atualizarBarra(F) end
-- ===== geometria e percepcao =====
local function chao(F, p) return F.L:chaoEm(p) or chaoY(p) end
local function alturaSolo(F) local p = pos(F); return p.Y - (chao(F, p) + F.L.alturaPivo) end
local function centro(F) return F.N:centroCorpo() end
local function boca(F) return F.N:boca() end
local function frenteAng(F, alvoP)                                      -- graus entre a frente e o alvo (no plano)
	local d = plano(alvoP - pos(F)); if d.Magnitude < 1 then return 0 end
	return math.deg(math.acos(math.clamp(F.L:frente():Dot(d.Unit), -1, 1)))
end
local function invisivel(F) local t = F.m:GetAttribute("PassoInvisivel"); return t ~= nil end
local function vePerceber(F)
	local e = F.inimigo
	local ve = not invisivel(e) and (pos(e) - pos(F)).Magnitude < X.VISAO and linhaLivre(centro(F) + Y * 6, centro(e))
	if ve then F.visto = os.clock(); F.ultimoVisto = pos(e) end
	F.ve = ve; return ve
end
-- capsula do corpo (cabeca -> base da cauda), para colisao e para medir sobreposicao
local function capsula(F)
	local a = F.cabeca and F.cabeca.TransformedWorldCFrame.Position or pos(F)
	local b = F.cauda and F.cauda.TransformedWorldCFrame.Position or (pos(F) - F.L:frente() * 30)
	return a, b, F.raio + (F.L.noAr and 6 or 0)
end
local function segSeg(p1, q1, p2, q2)                                   -- pontos mais proximos entre dois segmentos
	local d1, d2, r = q1 - p1, q2 - p2, p1 - p2
	local a, e, f = d1:Dot(d1), d2:Dot(d2), d2:Dot(r)
	local s, t
	if a < 1e-6 and e < 1e-6 then return p1, p2 end
	if a < 1e-6 then s = 0; t = math.clamp(f / e, 0, 1) else
		local c = d1:Dot(r)
		if e < 1e-6 then t = 0; s = math.clamp(-c / a, 0, 1) else
			local b = d1:Dot(d2); local den = a * e - b * b
			s = den > 1e-6 and math.clamp((b * f - c * e) / den, 0, 1) or 0
			t = (b * s + f) / e
			if t < 0 then t = 0; s = math.clamp(-c / a, 0, 1) elseif t > 1 then t = 1; s = math.clamp((b - c) / a, 0, 1) end
		end
	end
	return p1 + d1 * s, p2 + d2 * t
end
-- ===== decolar / pousar =====
local function decolar(F, motivo)
	if F.L.noAr or F.trans or F.N.ocupado then return end
	F.trans = true; conta("decolagens")
	task.spawn(function()
		local ok = F.L:decolar(function() return D.ativo end)
		if ok then F.spd = 18; log(F.P.titulo .. " decola (" .. motivo .. ")") end
		F.trans = false
	end)
end
local function pousar(F, motivo)
	if not F.L.noAr or F.trans or F.N.ocupado then return end
	F.trans = true
	task.spawn(function() F.L:pousar(function() return D.ativo end, true); F.spd = 0; log(F.P.titulo .. " pousa (" .. motivo .. ")"); F.trans = false end)
end
-- ===== motor (do tatico v11, sem o mergulho de teste): voo por direcao continua e corrida com desvio de obstaculo =====
local function aplicarSeguro(F, np)
	if nan(np) or F.L.pitch ~= F.L.pitch then F.L.pitch = 0; return false end
	F.L:_aplicar(np); return true
end
local function desvio(F, p, dir, alcance)                               -- obstaculo a frente: gira a rota para o lado livre
	rpV.FilterDescendantsInstances = {temp}
	if not workspace:Spherecast(p + Y * 10, F.raio + 4, dir * alcance, rpV) then return dir, false end
	for _, a in ipairs({55, -55, 95, -95}) do
		local d2 = CFrame.Angles(0, math.rad(a), 0):VectorToWorldSpace(dir)
		if not workspace:Spherecast(p + Y * 10, F.raio + 4, d2 * alcance, rpV) then return d2, true end
	end
	return dir, true
end
local function voar(F, dt)
	if dt < 1e-4 then return end
	local L = F.L; local p = pos(F); local alvo = F.ponto or p; if nan(alvo) then alvo = p end
	F.pontoSuave = (F.pontoSuave and not nan(F.pontoSuave)) and F.pontoSuave:Lerp(alvo, 1 - math.exp(-dt * 2.2)) or alvo
	alvo = F.pontoSuave
	local dh = plano(alvo - p)
	if os.clock() < (F.esqAte or 0) then dh = F.esqDir * 60 + L:frente() * 30 end
	if F.encarar then dh = plano((F.encararPonto or pos(F.inimigo)) - p) end
	local erro = 0
	if dh.Magnitude > 3 then erro = L:_girarPara(dh.Unit, Cfg.giroVoo * ((F.encarar and F.spd < 12) and 2.2 or (F.rapido and 1.1 or 1.25)), dt) end   -- (v2) pairando, gira no lugar para mirar
	local f = L:frente()
	local vAlvo = ((dh.Magnitude < 14 and not F.rapido) or F.encarar) and 0 or (F.rapido and X.VRAPIDO or X.VCRUZ)
	if os.clock() < (F.esqAte or 0) then vAlvo = X.VRAPIDO end
	vAlvo *= 1 + (F.m:GetAttribute("PassoBonus") or 0)
	if erro > math.rad(60) then vAlvo *= 0.55 end
	F.spd += math.clamp(vAlvo - F.spd, -X.ACEL * dt, X.ACEL * dt)
	local g = chao(F, p + f * 30); local minY = g + L.alturaPivo + 22
	local yAlvo = math.max(alvo.Y, minY)
	rpV.FilterDescendantsInstances = {workspace.Terrain, temp}
	if workspace:Spherecast(p + Y * 18, 22, f * 70, rpV) then yAlvo = math.max(yAlvo, p.Y + 40); F.obstAr = os.clock() end   -- rocha/relevo a frente: sobe
	local dy = math.clamp(yAlvo - p.Y, -X.VDESCE * dt, X.VSUB * dt)
	F.vy = (F.vy or 0) + (dy / dt - (F.vy or 0)) * (1 - math.exp(-dt * 3)); dy = F.vy * dt
	local np = p + f * F.spd * dt + Vector3.new(0, dy, 0)
	local piso = chao(F, np) + L.alturaPivo + 3; if np.Y < piso then np = Vector3.new(np.X, piso, np.Z); F.vy = math.max(F.vy, 0) end
	L.pitch = (L.pitch or 0) + (math.clamp(F.vy / math.max(F.spd, 12) * 0.7, -0.45, 0.45) - (L.pitch or 0)) * (1 - math.exp(-dt * 3.5))
	local quer
	if F.spd < 6 and math.abs(F.vy) < 6 then quer = "Pairar" elseif F.vy < -28 then quer = "Descida" elseif F.vy > 12 then quer = "Subida"
	elseif F.spd > X.VCRUZ + 8 then quer = "Voo_Rapido" else quer = "Voo" end
	local t = os.clock()
	if quer ~= F.querClipe then F.querClipe, F.querDesde = quer, t end
	if L.atual ~= quer and ((L.atual == "Pairar") or (t - F.querDesde >= 0.3 and t - (F.clipeDesde or 0) >= 0.6)) then L:clipe(quer, true, nil, 0.4); F.clipeDesde = t end
	if not aplicarSeguro(F, np) then return end
	F.vel = (np - p) / dt
	if F.spd > 8 and F.vel.Magnitude < 1 then F.parado = (F.parado or 0) + dt else F.parado = 0 end   -- trava em voo
	if (F.parado or 0) > 2.5 then D.checa.travasVoo += 1; F.parado = 0; log("CHECAGEM trava em voo: " .. F.P.titulo) end
end
local function correr(F, dt)
	if dt < 1e-4 then return end
	local L = F.L; local p = pos(F); local alvo = F.ponto or p; if nan(alvo) then alvo = p end
	local dh = plano(alvo - p)
	if os.clock() < (F.esqAte or 0) then dh = F.esqDir * 40 end
	if dh.Magnitude < 6 or F.encarar then
		local dir = unit(plano((F.encararPonto or pos(F.inimigo)) - p)); local erro = L:_girarPara(dir, Cfg.giroParado * 1.4, dt)
		if erro > math.rad(8) then L:clipe((F.lado or 1) > 0 and "Giro_E" or "Giro_D", true); L:_aplicar(p) else L:clipe("Parado", true) end
		F.spd = 0; F.vel = Vector3.zero; return
	end
	local dir, desviou = desvio(F, p, unit(dh), 45); if desviou then F.obstChao = os.clock() end
	local erro = L:_girarPara(dir, Cfg.giroCorrer, dt)
	if erro > math.rad(70) then L:clipe((F.lado or 1) > 0 and "Giro_E" or "Giro_D", true); L:_aplicar(p); F.spd = 0; F.vel = Vector3.zero; return end
	local vel = (F.m:GetAttribute("VelCorrer") or Cfg.correrVel * Cfg.correrRitmo) * (1 + (F.m:GetAttribute("PassoBonus") or 0))
	local np = p + L:frente() * vel * dt
	local g = L:chaoLocal(np); if not g then return end
	L:clipe("Correr", true, Cfg.correrRitmo)
	L.pitch = 0; if not aplicarSeguro(F, Vector3.new(np.X, g + L.alturaPivo, np.Z)) then return end
	F.spd = vel; F.vel = (pos(F) - p) / dt
end
-- ===== fases =====
local function fase(F, n, motivo, dur)
	if F.fase ~= n then
		log(("%s %s -> %s (%s) d=%.0f dy=%.0f vida %d x %d"):format(F.P.titulo, F.fase, n, motivo, (pos(F.inimigo) - pos(F)).Magnitude,
			pos(F.inimigo).Y - pos(F).Y, vida(F), vida(F.inimigo)))
		conta("fase_" .. n); F.faseDesde = os.clock()
	end
	F.fase, F.motivo, F.faseAte = n, motivo, os.clock() + (dur or X.COMPROMISSO)
	F.rotulo.Text = n .. " · " .. motivo
end
local function comprometido(F) return os.clock() < (F.faseAte or 0) end
-- ===== escolha do golpe (situacao, nao sequencia fixa) =====
local function marcasNoInimigo(F) return F.forma == "Sombrio" and Passivas.marcasDe(F.m, F.inimigo.m) or 0 end
local function extraAlvo(F) return (F.inimigo.m:GetAttribute("CorpoRaio") or 8) * 1.6 end   -- = naEsfera do Nucleo (alvo grande)
local function opcoesGolpe(F)
	local e = F.inimigo; local p, pe = pos(F), pos(e)
	local d3 = (pe - p).Magnitude; local dy = pe.Y - p.Y; local ang = frenteAng(F, pe)
	local los = linhaLivre(boca(F), centro(e)); local noAr = F.L.noAr; local eNoAr = e.L.noAr
	local ops = {}
	local function add(h, nota, motivo, precisaMirar) local ok = F.N:podeUsar(h) and os.clock() > ((F.semMira or {})[h] or 0); if ok then table.insert(ops, {h = h, nota = nota, motivo = motivo, mirar = precisaMirar}) end end
	local b = boca(F); local fr = F.L:frente()
	-- basicos: geometria do proprio Nucleo
	if F.N:temHabilidade("Mordida") ~= false and los and ((pe - (b + fr * 6)).Magnitude <= CfgC.basicos.Mordida.raio + extraAlvo(F)) and ang < 35 then
		add("Mordida", 6, "perto e a frente") end
	if not noAr and not eNoAr and math.abs(dy) < 14 and ang < 40 then
		local peE = F.N.peE and F.N.peE.TransformedWorldCFrame.Position or p
		if (pe - (peE + fr * 3)).Magnitude <= CfgC.basicos.Garra.raio + extraAlvo(F) then add("Garra", 5, "colado a frente") end
	end
	if not noAr and not eNoAr and F.quadril then
		local v = plano(pe - F.quadril.TransformedWorldCFrame.Position)
		if v.Magnitude <= CfgC.basicos.Cauda.raio and fr:Dot(unit(v)) < 0.35 then add("Cauda", 7, "inimigo no flanco/costas") end
	end
	local function defH(h) return CfgC.habilidades[F.N:real(h)] end
	local sop = defH("Sopro"); local pe_ = sop and sop.porElemento and (sop.porElemento.Sombra or sop.porElemento.Gelo)
	if _G.DUELO_SOPRO_ANTIGO then
		if pe_ and los and d3 <= pe_.alcance * 0.9 and d3 > 40 then
			add("Sopro", (e.N.ocupado and 7 or 5) + (F.forma == "Glacial" and d3 > 80 and 1 or 0), e.N.ocupado and "linha livre, alvo preso no proprio golpe" or "linha livre e distancia util", ang > pe_.angulo + 4)
		end
	elseif pe_ and los then
		-- (v3, 11/11 "sopro em horas inapropriadas"): o jato so sai 1,05 s depois; preve onde o rival estara, exige que siga no
		-- alcance e perto da frente; prioriza alvo preso/ocupado/recuperando ou quase parado de lado
		local vE = e.vel or Vector3.zero; local futuro = pe + vE * 1.05
		local dirE = unit(pe - p); local lateral = (vE - dirE * vE:Dot(dirE)).Magnitude
		local preso = e.m:GetAttribute("PresoFator") ~= nil or e.N.ocupado or e.fase == "RECUPERAR"
		local angF = frenteAng(F, futuro)
		if d3 > 35 and d3 <= pe_.alcance * 0.75 and (futuro - b).Magnitude <= pe_.alcance * 0.85 and angF <= 60 then
			local nota = 3 + (preso and 3 or 0) + (lateral < 8 and 2 or (lateral > 20 and -3 or 0)) + ((eNoAr and vE.Magnitude > 30) and -2 or 0)
				+ ((noAr and F.spd > 20) and -1.5 or 0)                                          -- (v3b) voando rapido o proprio corpo tira o alvo do cone
			local mot = preso and "alvo preso/ocupado: fica no cone" or (lateral < 8 and ("alvo quase parado na linha (lateral %.0f)"):format(lateral) or ("alvo previsto no cone (lateral %.0f)"):format(lateral))
			add("Sopro", nota, mot, angF > pe_.angulo + 6)
		end
	end
	if F.forma == "Sombrio" then
		local co = defH("Arremetida")
		if co and los and d3 >= 50 and d3 <= co.alcance then add("Arremetida", 6 + (e.L.noAr and 0 or 1) + math.min(2, marcasNoInimigo(F)), "alcance longo, prende o alvo", ang > 25) end
		local ec = defH("Coracao"); local mk = marcasNoInimigo(F)
		if ec and mk >= 2 and d3 <= ec.raio + extraAlvo(F) - 6 then add("Coracao", 5 + mk * 1.5, ("alvo com %d Marcas na area"):format(mk)) end
	else
		local ra = defH("Arremetida")
		if ra and los and d3 >= 80 and d3 <= ra.alcance * 0.95 then add("Arremetida", 6 + (d3 > 120 and 1 or 0), "segura a faixa longa", ang > 30) end
		local za = defH("Tempestade")
		if za and not noAr and d3 <= za.raio + extraAlvo(F) - 8 and (pe.Y - chao(F, pe)) < (za.alturaMaxAr or 45) then
			add("Tempestade", 7, "inimigo entrou na faixa curta (pune a entrada)") end
		local nv = defH("Coracao")
		if nv and d3 <= nv.raio and (e.m:GetAttribute("PresoFator") or e.N.ocupado or vida(F) < vida(e)) then add("Coracao", 5, "alvo preso/ocupado dentro da area grande") end
	end
	-- nao repetir o mesmo golpe 3 vezes seguidas sem motivo
	for _, o in ipairs(ops) do if F.ultGolpes[1] == o.h and F.ultGolpes[2] == o.h then o.nota -= 2.5 end end
	table.sort(ops, function(a, c) return a.nota > c.nota end)
	return ops, los
end
-- ===== registro de golpes: acerto = queda de Vida do alvo durante o golpe (+0,6 s de ticks/zona) =====
local function registrarGolpe(F, h, motivo, los)
	local e = F.inimigo
	local reg = {t = agora(), quem = F.P.titulo, hab = F.N:real(h), motivo = motivo, d = (pos(e) - pos(F)).Magnitude, dy = pos(e).Y - pos(F).Y,
		ang = frenteAng(F, pos(e)), los = los, vida0 = vida(e), esquivou = false, noAr = F.L.noAr}
	if not los then D.checa.semLOS += 1 end
	table.insert(D.ataques, reg); F.golpeAtual = reg
	table.insert(F.ultGolpes, 1, h); F.ultGolpes[3] = nil
	log(("%s USA %s (%s) d=%.0f dy=%.0f ang=%.0f %s"):format(F.P.titulo, reg.hab, motivo, reg.d, reg.dy, reg.ang, F.L.noAr and "no ar" or "no chao"))
	conta("ataque_" .. reg.hab)
	task.spawn(function()
		while D.ativo and (F.N.ocupado or F.m:GetAttribute("EmAtaque")) do task.wait(0.05) end
		task.wait(0.6)
		reg.dano = math.max(0, reg.vida0 - vida(e)); reg.acerto = reg.dano > 0
		if reg.acerto then conta("acertos"); log(("%s ACERTOU %s (-%d) -> %s %d"):format(F.P.titulo, reg.hab, reg.dano, e.P.titulo, vida(e)))
		else conta("evitados"); log(("%s: %s EVITADO (%s)"):format(F.P.titulo, reg.hab, reg.esquivou and "esquiva" or "fora do alcance/cone no impacto")) end
		if F.golpeAtual == reg then F.golpeAtual = nil end
	end)
end
local function atacar(F)
	if F.trans or F.N.ocupado or not F.ve then return false end
	local ops, los = opcoesGolpe(F); local o
	for _, c in ipairs(ops) do if c.nota >= 4 and (not c.mirar or F.naPosicao) then o = c; break end end   -- (v2) mira so na posicao
	if not o then if ops[1] and ops[1].mirar and not F.naPosicao then F.esperaPos = (F.esperaPos or 0) + 1 end; return false end
	if (o.h == "Sopro" or o.h == "Arremetida") and not linhaLivre(boca(F), centro(F.inimigo)) then D.checa.golpeAtravessa += 1; return false end
	if o.mirar then
		F.encarar = true; F.mirandoDesde = F.mirandoDesde or os.clock()
		if os.clock() - F.mirandoDesde < (F.L.noAr and 1.8 or 1.2) then return false end            -- gira para o alvo antes do golpe de cone/linha
		F.mirandoDesde = nil; conta("mira_desistiu"); F.semMira = F.semMira or {}; F.semMira[o.h] = os.clock() + 2; log(("%s desiste de %s: nao ficou de frente a tempo (ang %.0f)"):format(F.P.titulo, F.N:real(o.h), frenteAng(F, pos(F.inimigo))))
		return false
	end
	F.mirandoDesde = nil
	local acompanha = o.h == "Sopro" and not _G.DUELO_SOPRO_ANTIGO
	if acompanha then F.N.segurando = true; F.N.miraDir = unit(centro(F.inimigo) - boca(F)); F.ponto = pos(F); F.rapido = false end   -- (v3b) freia/paira para soprar
	if F.N:usar(o.h, {alvo = F.inimigo.m, direcao = plano(pos(F.inimigo) - pos(F)), segurar = acompanha or nil}) then
		registrarGolpe(F, o.h, o.motivo, los); fase(F, "ATACAR", o.motivo, 0.3)
		if acompanha then
			task.spawn(function()                                                -- (v3b) mira segue o rival a no maximo 50 graus/s
				local def = CfgC.habilidades[F.N:real("Sopro")]; local el = def.porElemento.Sombra or def.porElemento.Gelo
				local t0, dir = os.clock(), F.N.miraDir
				while D.ativo and F.N.ocupado do
					local dt = 0.1; local b = boca(F); local alvo = centro(F.inimigo) + (F.inimigo.vel or Vector3.zero) * 0.2
					local quer = unit(alvo - b); local ang = math.acos(math.clamp(dir:Dot(quer), -1, 1)); local max = math.rad(50) * dt
					dir = ang <= max and quer or dir:Lerp(quer, max / ang).Unit
					F.N.miraDir = dir; F.encarar = true
					local t = os.clock() - t0
					if t > 1.05 + def.emissao then                                     -- passou a emissao base: segue so se ainda vale
						local fora = (alvo - b).Magnitude > el.alcance or not linhaLivre(b, alvo) or math.deg(math.acos(math.clamp(dir:Dot(quer), -1, 1))) > el.angulo
						if fora or t > 1.05 + def.emissao + 1.2 then F.N.segurando = false end
					end
					task.wait(dt)
				end
				F.N.segurando = nil
			end)
		end
		return true
	end
	if acompanha then F.N.segurando = nil; F.N.miraDir = nil end
	return false
end
-- ===== esquiva: golpe forte perceptivel, tempo de reacao, espaco lateral, intervalo =====
local FORTES = {SoproUmbral = true, SoproGlacial = true, Correntes = true, Rajadas = true, Eclipse = true, Nevasca = true, ZeroAbsoluto = true, Mordida = true, Cauda = true}
local function espacoLado(F, lado)
	local p = pos(F) + Y * 8
	rpV.FilterDescendantsInstances = {workspace.Terrain, temp}
	local livre = not workspace:Spherecast(p, F.raio, lado * 55, rpV)
	local dentro = plano(p + lado * 55 - X.CENTRO).Magnitude < X.ARENA
	return livre and dentro
end
for _, F in ipairs({S, G}) do
	F.inimigo.m:GetAttributeChangedSignal("EmAtaque"):Connect(function()
		local hab = F.inimigo.m:GetAttribute("EmAtaque"); if not hab or not D.ativo then return end
		local e = F.inimigo; local habR = e.N:real(hab)
		if not FORTES[habR] and not FORTES[hab] then return end
		local d = pos(F) - pos(e)
		local area = habR == "Eclipse" or habR == "Nevasca" or habR == "ZeroAbsoluto"
		if not area and (plano(d).Magnitude > 240 or e.L:frente():Dot(unit(plano(d))) < 0.75) then return end   -- nao mira em mim
		if area and d.Magnitude > 140 then return end
		local reac = F.P.reacao[1] + math.random() * (F.P.reacao[2] - F.P.reacao[1])
		task.delay(reac, function()
			if not D.ativo or F.N.ocupado or F.trans then log(("%s percebe %s (%.2f s) mas esta ocupado"):format(F.P.titulo, habR, reac)); return end
			if os.clock() - F.ultEsq < X.ESQ_INTERVALO then log(("%s percebe %s mas esquivou ha pouco"):format(F.P.titulo, habR)); return end
			local base = unit(plano(d)):Cross(Y); local lados = math.random() < 0.5 and {base, -base} or {-base, base}
			local lado; for _, l in ipairs(lados) do if espacoLado(F, l) then lado = l; break end end
			if area then lado = unit(plano(d)) end                                   -- area: sai para fora
			if not lado or (F.P.segura and not area and math.random() < 0.35) then
				F.ultEsq = os.clock(); conta("mantem_posicao")
				log(("%s MANTEM POSICAO contra %s (%s, reacao %.2f s)"):format(F.P.titulo, habR, lado and "faixa de controle" or "sem espaco lateral", reac)); return
			end
			F.ultEsq = os.clock(); F.esqAte = os.clock() + (F.L.noAr and 0.8 or 1.0); F.esqDir = lado; conta("esquivas")
			if e.golpeAtual then e.golpeAtual.esquivou = true end
			fase(F, "ESQUIVAR", habR .. " mirado em mim", 1.0)
			log(("%s ESQUIVA de %s (reacao %.2f s, %s)"):format(F.P.titulo, habR, reac, F.L.noAr and "guinada no ar" or "corre de lado"))
		end)
	end)
	F.vidaAnt = vida(F)
	F.m:GetAttributeChangedSignal("Vida"):Connect(function()
		atualizarBarra(F); local v = vida(F); local perda = (F.vidaAnt or v) - v; F.vidaAnt = v
		if perda > 0 then table.insert(F.perdas, {os.clock(), perda}); if os.clock() - (F.ultGolpeT or -9) >= 1.0 then table.insert(F.golpes, os.clock()); F.ultGolpeT = os.clock() end end
	end)
end
-- ===== pontos de cada fase =====
local function pontoFaixa(F, ideal, orbita)
	local e = pos(F.inimigo); local fora = unit(plano(pos(F) - e))
	local dir = CFrame.Angles(0, math.rad(orbita or 0), 0):VectorToWorldSpace(fora)
	local p = e + dir * ideal
	if plano(p - X.CENTRO).Magnitude > X.ARENA then p = X.CENTRO + unit(plano(p - X.CENTRO)) * X.ARENA * 0.9 end
	return Vector3.new(p.X, F.L.noAr and math.max(e.Y + 15, chao(F, p) + F.L.alturaPivo + 25) or p.Y, p.Z)
end
local function pontoFlanco(F)
	local e = pos(F.inimigo); local fe = F.inimigo.L:frente()
	F.lado = F.lado or (math.random() < 0.5 and 1 or -1)
	local p = e + fe:Cross(Y) * 70 * F.lado - fe * 30
	return Vector3.new(p.X, F.L.noAr and e.Y + 10 or p.Y, p.Z)
end
-- ===== (v2) POSICAO DE ATAQUE: candidatos em volta do rival, verificados antes de armar o golpe =====
local function alturaPonto(F, q, pe)
	if F.L.noAr then return math.max(pe.Y + 10, chaoY(q) + F.L.alturaPivo + 25) end
	return chaoY(q) + F.L.alturaPivo
end
local function escolherPosicao(F)
	local e = F.inimigo; local p, pe = pos(F), pos(e)
	local fe = unit(plano(e.L:frente())); local base = unit(plano(p - pe))
	local ideal, angs, ref
	if F.forma == "Sombrio" then                                                   -- flanco utilizavel, fora do cone da frente do rival
		ideal = F.N:podeUsar("Arremetida") and 110 or (F.N:podeUsar("Sopro") and 72 or 48)
		angs = {70, -70, 110, -110, 150, -150}; ref = fe
	else                                                                            -- faixa de controle com saida livre
		ideal = (F.P.faixa[1] + F.P.faixa[2]) / 2; angs = {0, 25, -25, 50, -50}; ref = base
	end
	local melhor
	for _, a in ipairs(angs) do
		if not orcamento(F) then break end
		local dirA = CFrame.Angles(0, math.rad(a), 0):VectorToWorldSpace(ref)
		local q = pe + dirA * ideal
		if plano(q - X.CENTRO).Magnitude > X.ARENA then continue end
		q = Vector3.new(q.X, alturaPonto(F, q, pe), q.Z)
		if not linhaLivre(q + Y * 6, centro(e)) then continue end                           -- sem visao dali
		do local r = F.largura * 0.8; local a0, a1 = centroEsfera(p, r, F.L.noAr), centroEsfera(q, r, F.L.noAr); if esfera(a0, r, a1 - a0) then continue end end   -- rota bloqueada para corpo+asas
		local nota = -(q - p).Magnitude / 40
		local livres = 0
		for _, l in ipairs({dirA:Cross(Y), -dirA:Cross(Y)}) do if not raio(q + Y * 10, l * (F.largura + 12)) then livres += 1 end end
		if livres < 2 then nota -= 3 end                                              -- pouco espaco para virar
		if F.forma == "Sombrio" then nota += (1 - fe:Dot(dirA)) * 1.5
		else nota += raio(q + Y * 10, dirA * 60) and -2 or 2 end                      -- Glacial: saida livre atras dele
		if (q - pe).Magnitude < F.largura + e.largura then nota -= 4 end                -- colado demais (asas)
		if not melhor or nota > melhor.nota then melhor = {q = q, nota = nota, a = a, ideal = ideal} end
	end
	return melhor
end
-- ===== (v2) ROTAS em volta do obstaculo, a partir do ultimo ponto visto =====
local function caixaParte(part, p, dir, lat)
	local cf, sz = part.CFrame, part.Size; local sMin, sMax, aMin, aMax, topo = math.huge, -math.huge, math.huge, -math.huge, -math.huge
	for _, dx in ipairs({-1, 1}) do for _, dy_ in ipairs({-1, 1}) do for _, dz in ipairs({-1, 1}) do
		local c = cf:PointToWorldSpace(Vector3.new(dx * sz.X / 2, dy_ * sz.Y / 2, dz * sz.Z / 2)); local v = c - p
		sMin = math.min(sMin, v:Dot(lat)); sMax = math.max(sMax, v:Dot(lat)); aMin = math.min(aMin, v:Dot(dir)); aMax = math.max(aMax, v:Dot(dir)); topo = math.max(topo, c.Y)
	end end end
	return sMin, sMax, aMin, aMax, topo
end
local function planejarRota(F, excluir)
	local p = pos(F); local alvo = F.ultimoVisto; if not alvo then return nil end
	local dir = unit(plano(alvo - p)); local lat = dir:Cross(Y)                       -- lat = direita de quem olha para o alvo
	local h = raio(p + Y * 12, (alvo + Y * 12) - (p + Y * 12))
	if not h then return {tipo = "direto", pontos = {alvo}, motivo = "linha livre ate o ultimo ponto visto", custo = (alvo - p).Magnitude} end
	local part = h.Instance
	local sMin, sMax, aMin, aMax, topo
	if part:IsA("BasePart") and part ~= workspace.Terrain then
		-- (v2f) obstaculo composto: junta as pecas do teste encostadas (folga < 12) num bloco so
		local bloco, fila = {[part] = true}, {part}
		while #fila > 0 do
			local a = table.remove(fila)
			for _, o in ipairs(obst) do
				if not bloco[o] then
					local da = (o.Position - a.Position); local lim = (o.Size + a.Size) / 2 + Vector3.new(12, 12, 12)
					if math.abs(da.X) < lim.X and math.abs(da.Y) < lim.Y and math.abs(da.Z) < lim.Z then bloco[o] = true; table.insert(fila, o) end
				end
			end
		end
		sMin, sMax, aMin, aMax, topo = math.huge, -math.huge, math.huge, -math.huge, -math.huge
		for o in pairs(bloco) do local s1, s2, a1, a2, t1 = caixaParte(o, p, dir, lat); sMin = math.min(sMin, s1); sMax = math.max(sMax, s2); aMin = math.min(aMin, a1); aMax = math.max(aMax, a2); topo = math.max(topo, t1) end
	else local a0 = (h.Position - p):Dot(dir); sMin, sMax, aMin, aMax, topo = -40, 40, a0, a0 + 40, h.Position.Y + 30 end
	local W = F.largura + 8; local ops = {}
	local function chegada(q) return (q - alvo).Magnitude >= X.LONGE_RIVAL and linhaLivre(q + Y * 8, alvo + Y * 8) end
	for _, lado in ipairs({{"direita", 1}, {"esquerda", -1}}) do
		if excluir[lado[1]] then continue end
		local off = lado[2] > 0 and (sMax + W) or (sMin - W)
		-- (v2b) 3 pontos: sai para o lado ANTES do obstaculo, passa rente a ele na folga W e chega depois dele
		local w0 = p + dir * math.max(0, aMin - W) + lat * off
		local w1 = p + dir * (aMax + W) + lat * off
		local w2 = w1 + dir * 10
		local yy = F.L.noAr and p.Y or chaoY(w1) + F.L.alturaPivo
		w0 = Vector3.new(w0.X, yy, w0.Z); w1 = Vector3.new(w1.X, yy, w1.Z); w2 = Vector3.new(w2.X, yy, w2.Z)
		local r = W - 4; local a0, b0, a1 = centroEsfera(p, r, F.L.noAr), centroEsfera(w0, r, F.L.noAr), centroEsfera(w1, r, F.L.noAr)
		local livre = not esfera(a0, r, b0 - a0) and not esfera(b0, r, a1 - b0)
		-- (v2c) chegada = primeiro ponto do contorno que ja recupera a visao, fora do alcance imediato do rival
		local pts, chega = {}, nil
		for _, q in ipairs({w0, w0:Lerp(w1, 0.5), w1, w2}) do table.insert(pts, q); if chegada(q) then chega = q; break end end
		local ok = livre and chega ~= nil and plano(chega - X.CENTRO).Magnitude < X.ARENA + 40
		if ok then
			local custo, ant = 0, p; for _, q in ipairs(pts) do custo += (q - ant).Magnitude; ant = q end
			-- (v2e) desempate sem lado fixo: lado para onde o rival se movia; Sombrio prefere o lado com outra cobertura; sorteio
			local vl = (F.inimigo.vel or Vector3.zero):Dot(lat) * lado[2]
			local bias = (vl > 2 and -20 or (vl < -2 and 20 or 0))
			if F.forma == "Sombrio" then for _, o in ipairs(obst) do if o ~= part and (plano(o.Position - pts[#pts])).Magnitude < 90 then bias -= 10 end end end
			custo += bias + math.random() * 8
			table.insert(ops, {tipo = lado[1], pontos = pts, custo = custo,
			motivo = ("contorno pela %s: passagem de %.0f studs livre, chega com visao a %.0f do rival (%d pontos; desempate %+.0f)"):format(lado[1], 2 * W, (chega - alvo).Magnitude, #pts, bias)}) end
		if not ok then table.insert(ops, {tipo = lado[1], falhou = livre and "chegada sem visao/colada no rival" or "passagem estreita para corpo+asas"}) end
	end
	local podeVoar = F.forma == "Sombrio" or F.L.noAr
	if podeVoar and not excluir.cima then
		local wy = topo + F.raio + 18
		if wy <= p.Y + X.SUBIDA_MAX or F.L.noAr then
			local w1 = Vector3.new(0, wy, 0) + plano(p + dir * (aMin - 10)); local w2 = Vector3.new(0, wy, 0) + plano(p + dir * (aMax + W))
			local livre = not esfera(p + Y * 10, F.raio + 6, (w1 - p)) and not esfera(w1, F.largura, (w2 - w1))
			if livre and chegada(w2) then table.insert(ops, {tipo = "cima", pontos = {w1, w2}, custo = (w1 - p).Magnitude + (w2 - w1).Magnitude + (F.L.noAr and 20 or 60),
				motivo = ("por cima: topo %.0f, folga %.0f acima, chega com visao"):format(topo - chaoY(p), wy - topo)}) else table.insert(ops, {tipo = "cima", falhou = livre and "chegada sem visao" or "sem folga para subir/passar"}) end
		else table.insert(ops, {tipo = "cima", falhou = ("obstaculo alto demais (%.0f > subida maxima)"):format(topo - p.Y)}) end
	end
	local melhor; local falhas = {}
	for _, o in ipairs(ops) do if o.falhou then table.insert(falhas, o.tipo .. ": " .. o.falhou) elseif not melhor or o.custo < melhor.custo then melhor = o end end
	local direto = (alvo - p).Magnitude
	if F.P.segura and (not melhor or melhor.tipo == "cima" or melhor.custo > direto * 2.2) then        -- Glacial: vigia a saida em vez de volta longa
		local recuo = (aMin < W + 10) and (p - dir * (W + 10 - aMin)) or p
		return {tipo = "vigiar", pontos = {Vector3.new(recuo.X, p.Y, recuo.Z)}, custo = 0, falhas = falhas,
			motivo = "vigia a saida do obstaculo, sem ficar prensado (" .. (melhor and ("contorno " .. melhor.tipo .. " longo") or "sem contorno seguro") .. ")"}
	end
	if melhor then melhor.falhas = falhas end
	return melhor or {tipo = "abrir", pontos = {p - dir * 60}, custo = 60, falhas = falhas, motivo = "nenhuma rota segura: abre espaco"}
end
local function seguirRota(F)
	local R = F.rota; local p = pos(F)
	if R.tipo == "vigiar" then F.ponto = R.pontos[1]; if plano(R.pontos[1] - p).Magnitude < 10 then F.encarar = true; F.encararPonto = F.ultimoVisto end; return end
	local wp = R.pontos[R.i]
	if R.tipo == "cima" and not F.L.noAr then decolar(F, "rota por cima do obstaculo") end
	F.ponto = wp; F.rapido = false
	local dd = (R.tipo == "cima" or F.L.noAr) and (wp - p).Magnitude or plano(wp - p).Magnitude
	if R.chegou then F.ponto = F.ultimoVisto; return end                         -- (v2d) chegou e o rival saiu dali: segue ao ultimo ponto visto
	if dd < X.CHEGOU then
		if R.i < #R.pontos then R.i += 1; R.melhor = math.huge
		else R.chegou = true; log(("%s chegou ao fim da rota %s sem visao (rival se moveu): segue ao ultimo ponto visto"):format(F.P.titulo, R.tipo)); return end
	end
	if os.clock() - R.tCheck >= X.ROTA_PROGRESSO then                                -- sem progresso -> alternativa
		if dd > R.melhor - 4 and not F.trans then
			R.tentadas[R.tipo] = true; conta("troca_rota")
			local nova = planejarRota(F, R.tentadas)
			log(("%s ROTA %s parou de avancar (%.0f do ponto) -> %s (%s)"):format(F.P.titulo, R.tipo, dd, nova and nova.tipo or "nenhuma", nova and nova.motivo or "-"))
			if nova then nova.i, nova.tCheck, nova.melhor, nova.tentadas, nova.t0 = 1, os.clock(), math.huge, R.tentadas, R.t0; F.rota = nova
				table.insert(D.rotas, {quem = F.P.titulo, tipo = nova.tipo, motivo = "troca: " .. nova.motivo}) end
			return
		end
		R.melhor = math.min(R.melhor, dd); R.tCheck = os.clock()
	end
end
-- ===== cerebro =====
local function decidir(F)
	local e = F.inimigo; local p, pe = pos(F), pos(e)
	local d = (pe - p).Magnitude; local hpF, hpE = vida(F) / X.VIDA, vida(e) / X.VIDA
	local ve = vePerceber(F)
	F.encarar = false; F.encararPonto = nil
	-- interrupcoes (ameaca real/perda de visao/vida baixa) — respeitam o golpe em andamento
	if F.N.ocupado then F.encarar = true; if F.m:GetAttribute("EmAtaque") == "Sopro" then F.ponto = pos(F) end; return end                            -- (v3) durante o golpe segue virado para o rival
	local recentes, perdido = 0, 0; for _, t in ipairs(F.golpes) do if os.clock() - t < 6 then recentes += 1 end end
	for _, x in ipairs(F.perdas) do if os.clock() - x[1] < 6 then perdido += x[2] end end
	if F.fase ~= "RECUAR" and F.fase ~= "ESQUIVAR" and (os.clock() - (F.ultRecuo or -99) > 14) and ((hpF < X.RECUO_VIDA and hpE > hpF) or recentes >= 3 or perdido >= X.VIDA * 0.25) then
		F.ultRecuo = os.clock(); F.recuoT0 = os.clock(); conta("recuos")
		fase(F, "RECUAR", hpF < X.RECUO_VIDA and ("ferido %d%%"):format(hpF * 100) or (recentes >= 3 and "pressionado (3 golpes em 6 s)" or ("perdeu %d de vida em 6 s"):format(perdido)), 2.5)
		if not F.L.noAr and ((F.P.segura and d < 60) or (not F.P.segura and math.random() < 0.6 + F.P.voa * 0.4)) then decolar(F, "recuar") end
	end
	if F.fase == "ESQUIVAR" and comprometido(F) then return end
	if F.fase == "RECUAR" then
		local fora = unit(plano(p - pe))
		F.rapido = true; F.ponto = p + fora * 120 + Y * (F.L.noAr and 30 or 0)
		if plano(F.ponto - X.CENTRO).Magnitude > X.ARENA then F.ponto = X.CENTRO + fora:Cross(Y) * X.ARENA * 0.8 + Y * F.ponto.Y end
		if F.forma == "Sombrio" and F.N:podeUsar("Tempestade") and d < 120 then F.N:usar("Tempestade", {direcao = fora}); log("Dragao Sombrio usa Passo Sombrio para sair da pressao"); conta("ataque_PassoSombrio") end
		local abertura = e.N.ocupado or e.fase == "RECUPERAR" or (e.fase == "PERSEGUIR" and not e.ve)
		if os.clock() - F.recuoT0 > X.RECUO_MAX or (d > 170 and os.clock() - F.recuoT0 > 3) then
			fase(F, "REPOSICIONAR", "fim do recuo (limite/distancia segura)", 1.5)
		elseif abertura and math.random() < F.DIF.abertura * 0.1 and os.clock() - F.recuoT0 > 2 then
			fase(F, "APROXIMAR", "abertura: inimigo ocupado/recuperando", 1.0)
		end
		return
	end
	-- perseguicao: o outro recua e eu ainda o vejo
	if e.fase == "RECUAR" and F.fase ~= "PERSEGUIR" and F.fase ~= "INVESTIGAR" and hpF > 0.3 and ve then
		F.persegT0 = os.clock(); conta("perseguicoes"); fase(F, "PERSEGUIR", "rival recuando, ainda visivel", 1.5)
		if e.L.noAr and not F.L.noAr then decolar(F, "perseguir no ar") end
	end
	if F.fase == "PERSEGUIR" then
		if not ve then fase(F, "INVESTIGAR", "perdeu a visao (ultimo ponto visto)", 1.0); F.investT0 = os.clock(); F.perdeuT = os.clock(); F.rota = nil; conta("investigacoes")
		elseif os.clock() - F.persegT0 > X.PERSEG_MAX then fase(F, "REPOSICIONAR", "limite da perseguicao", 1.5); conta("persegLimite")
		elseif e.fase ~= "RECUAR" then fase(F, "APROXIMAR", "rival parou de recuar", 1.0)
		else F.rapido = true; F.ponto = pe + (e.vel or Vector3.zero) * 0.8 + unit(plano(p - pe)) * 60 + Y * (e.L.noAr and 8 or 0); atacar(F) end
		return
	end
	if not ve and F.fase ~= "INVESTIGAR" and F.fase ~= "PATRULHA" and F.fase ~= "INICIO" and os.clock() - F.visto > 0.8 then
		F.investT0 = os.clock(); F.perdeuT = os.clock(); F.rota = nil; conta("investigacoes"); fase(F, "INVESTIGAR", invisivel(e) and "rival sumiu (Passo Sombrio)" or (d > X.VISAO and "rival fora do alcance de visao" or "rival atras de obstaculo"), 1.0)
	end
	if F.fase == "INVESTIGAR" then
		if ve then
			local tv = os.clock() - (F.perdeuT or F.investT0); table.insert(D.tvisao, {quem = F.P.titulo, t = tv, rota = F.rota and F.rota.tipo or "sem rota"})
			log(("%s RECUPERA A VISAO em %.1f s (rota %s)"):format(F.P.titulo, tv, F.rota and F.rota.tipo or "nenhuma")); F.rota = nil
			fase(F, "APROXIMAR", "reencontrou o rival", 1.0)
		elseif os.clock() - F.investT0 > X.INVEST_MAX then
			log(("%s encerra a busca pelo limite (%.0f s, rota %s)"):format(F.P.titulo, X.INVEST_MAX, F.rota and F.rota.tipo or "nenhuma")); F.rota = nil
			fase(F, "PATRULHA", "busca sem reencontro (limite)", X.PATRULHA); conta("abandonos"); F.patrT0 = os.clock()
			do local v0 = plano(p - X.CENTRO); F.patrA0 = math.atan2(v0.Z, v0.X) end
		else
			if not F.rota and F.ultimoVisto and orcamento(F) then
				F.rota = planejarRota(F, {})
				if F.rota then F.rota.i, F.rota.tCheck, F.rota.melhor, F.rota.tentadas, F.rota.t0 = 1, os.clock(), math.huge, {}, os.clock()
					table.insert(D.rotas, {quem = F.P.titulo, tipo = F.rota.tipo, motivo = F.rota.motivo}); conta("rota_" .. F.rota.tipo)
					log(("%s ROTA %s: %s%s"):format(F.P.titulo, F.rota.tipo, F.rota.motivo, (#(F.rota.falhas or {}) > 0) and (" | descartadas: " .. table.concat(F.rota.falhas, "; ")) or "")) end
			end
			if F.rota then seguirRota(F) else F.rapido = false; F.ponto = F.ultimoVisto or p end
		end
		return
	end
	if F.fase == "PATRULHA" then
		if ve then fase(F, "AMEACAR", "rival de volta a vista", 1.2)
		else local sent = F.forma == "Sombrio" and 1 or -1; local a = (F.patrA0 or 0) + sent * (os.clock() - F.patrT0) * 0.5   -- (v2f) sentidos opostos
			F.ponto = X.CENTRO + Vector3.new(math.cos(a), 0, math.sin(a)) * 150 + Y * p.Y; F.rapido = false end
		return
	end
	-- ciclo principal: AMEACAR -> APROXIMAR -> ATACAR -> RECUPERAR -> REPOSICIONAR
	if F.fase == "ATACAR" then
		local r = X.RECUP[1] + math.random() * (X.RECUP[2] - X.RECUP[1]); fase(F, "RECUPERAR", ("pos-golpe %.1f s"):format(r), r); return
	end
	if F.fase == "RECUPERAR" then
		F.encarar = true; F.ponto = p
		if not comprometido(F) then fase(F, "REPOSICIONAR", F.forma == "Sombrio" and "muda o angulo" or "volta para a faixa", 1.4 + math.random() * F.DIF.variacao) end
		return
	end
	if F.fase == "AMEACAR" or F.fase == "INICIO" then
		F.encarar = true; F.ponto = p
		if F.fase == "INICIO" or (os.clock() - F.ultRugido > X.RUGIDO_INTERVALO and d > 70 and d < 200 and not F.L.noAr and F.N:podeUsar("Rugido")) then
			if F.N:podeUsar("Rugido") and not F.L.noAr then F.N:usar("Rugido", {}); F.ultRugido = os.clock(); conta("rugidos"); log(F.P.titulo .. " RUGE (intimida)") end
			fase(F, "AMEACAR", F.fase == "INICIO" and "encontro: intimida antes de lutar" or "rival voltou a vista", 1.6); return
		end
		if not comprometido(F) then fase(F, "APROXIMAR", "fim da ameaca", 1.0) end
		return
	end
	-- APROXIMAR / REPOSICIONAR: personalidade decide o ponto; ataca quando a situacao permite
	if F.fase == "REPOSICIONAR" and not comprometido(F) then fase(F, "APROXIMAR", "posicao refeita", 1.0) end
	local faixa = F.P.faixa
	local dy = pe.Y - p.Y
	if F.fase == "REPOSICIONAR" then
		if F.forma == "Sombrio" then
			F.lado = -(F.lado or 1); F.ponto = pontoFlanco(F); F.rapido = true
			if F.N:podeUsar("Tempestade") and math.random() < 0.25 * F.DIF.variacao and d > 70 then F.N:usar("Tempestade", {direcao = plano(F.ponto - p)}); log("Dragao Sombrio some no Passo Sombrio para trocar de angulo"); conta("ataque_PassoSombrio") end
			if not F.L.noAr and math.random() < F.P.voa * 0.5 then decolar(F, "trocar de angulo pelo ar") end
		else
			F.ponto = pontoFaixa(F, (faixa[1] + faixa[2]) / 2, 15 * (F.lado or 1)); F.rapido = d < faixa[1] - 20
			if F.L.noAr and not e.L.noAr and alturaSolo(F) > 10 then pousar(F, "controla o espaco no chao") end
		end
	else -- APROXIMAR
		if F.forma == "Sombrio" then
			F.ponto = (F.P.flanco > math.random() and d < 200) and pontoFlanco(F) or pontoFaixa(F, faixa[1], 10 * (F.lado or 1)); F.rapido = d > 140
		else
			if d < faixa[1] - 10 then F.ponto = pontoFaixa(F, faixa[2], 0); F.rapido = true          -- rival entrou: abre a faixa (ou pune)
			elseif d > faixa[2] + 20 then F.ponto = pontoFaixa(F, faixa[2], 0) else F.ponto = p; F.encarar = true end   -- segura a rota
		end
	end
	-- (v2) posicao de ataque verificada: substitui o ponto acima quando ha visao (e orcamento de consultas)
	F.naPosicao = false
	if ve then
		local reav = not F.posAlvo or os.clock() > (F.posReavalia or 0)
		if reav and orcamento(F) then
			local nv = escolherPosicao(F); F.posReavalia = os.clock() + X.POS_REAVALIA
			if nv and (not F.posAlvo or (nv.q - F.posAlvo.q).Magnitude > 25) then
				conta("posicoes"); log(("%s POSICAO: %s a %.0f do rival, angulo %d (nota %.1f)"):format(F.P.titulo, F.forma == "Sombrio" and "flanco" or "faixa com saida", nv.ideal, nv.a, nv.nota)) end
			F.posAlvo = nv or F.posAlvo
		end
		local seguraFaixa = F.P.segura and d >= faixa[1] - 10 and d <= faixa[2] + 20
		if seguraFaixa and not raio(p + Y * 10, unit(plano(p - pe)) * 50) then F.ponto = p; F.encarar = true; F.naPosicao = true
		elseif F.posAlvo then
			F.ponto = F.posAlvo.q; F.rapido = (F.posAlvo.q - p).Magnitude > 60
			if plano(F.posAlvo.q - p).Magnitude < X.CHEGOU then F.naPosicao = true; F.encarar = true end
		end
	end
	-- voo coerente com a situacao
	if not F.L.noAr and dy > 30 and e.L.noAr and (not F.P.segura or (dy > 60 and d < 80)) and os.clock() - (F.dyAltoDesde or os.clock()) > (F.P.segura and 2.5 or 1.0) then decolar(F, "rival no alto (" .. math.floor(dy) .. " studs)") end
	if dy > 30 and e.L.noAr then F.dyAltoDesde = F.dyAltoDesde or os.clock() else F.dyAltoDesde = nil end
	if F.L.noAr and F.P.segura and alturaSolo(F) > 10 and (F.fase == "APROXIMAR" or F.fase == "REPOSICIONAR") and not (e.L.noAr and dy > 60 and d < 80) then pousar(F, "volta ao chao para segurar o espaco") end
	if not F.L.noAr and F.forma == "Sombrio" and d > 150 and math.random() < 0.02 then decolar(F, "aproxima pelo ar (distancia longa)") end
	if F.L.noAr and F.forma == "Sombrio" and not e.L.noAr and d < 90 and alturaSolo(F) > 10 and math.random() < 0.03 then pousar(F, "desce para o golpe de perto") end
	atacar(F)
end
-- ===== motor + colisao por capsulas a cada quadro =====
D.perf = {n = 0, soma = 0, max = 0}
local conMotor = RunService.Heartbeat:Connect(function(dt)
	if not D.ativo then return end
	local t0 = os.clock()
	for _, F in ipairs({S, G}) do
		if F.m.Parent and not F.trans and not F.m:GetAttribute("Incapacitado") then
			local ok, err = pcall(function() if F.L.noAr then voar(F, dt) else correr(F, dt) end end)
			if not ok and not D.erroMotor then D.erroMotor = true; log("ERRO motor " .. F.P.titulo .. ": " .. tostring(err)) end
		end
	end
	local a1, b1, r1 = capsula(S); local a2, b2, r2 = capsula(G)
	local c1, c2 = segSeg(a1, b1, a2, b2); local v = c2 - c1; local dist = v.Magnitude; local falta = r1 + r2 - dist
	-- (v2) asas: segmento ponta a ponta (raio 3) contra o corpo e as asas do outro; folga minima registrada
	local function asa(F) return F.asaE and F.asaE.TransformedWorldCFrame.Position, F.asaD and F.asaD.TransformedWorldCFrame.Position end
	local eS1, eS2 = asa(S); local eG1, eG2 = asa(G); local faltaAsa, vAsa = 0, v
	if eS1 and eG1 then
		for _, par in ipairs({{eS1, eS2, a2, b2, r2}, {a1, b1, eG1, eG2, r1}, {eS1, eS2, eG1, eG2, 3}}) do
			local x1, x2 = segSeg(par[1], par[2], par[3], par[4]); local dd = (x2 - x1).Magnitude - par[5] - 3
			D.checa.folgaAsaMin = math.min(D.checa.folgaAsaMin, dd)
			if X.FOLGA_ASA - dd > faltaAsa then faltaAsa = X.FOLGA_ASA - dd; vAsa = x2 - x1 end
		end
	end
	local quer = math.max(falta, faltaAsa)
	if quer > 0 then
		local u = (S.L.noAr and G.L.noAr) and unit(falta >= faltaAsa and v or vAsa, Vector3.xAxis) or unit(plano(falta >= faltaAsa and v or vAsa), Vector3.xAxis)
		if falta > 0 then D.checa.sobrepMax = math.max(D.checa.sobrepMax, falta) end
		local passo = math.min(quer / 2, X.EMPURRA_MAX * dt * (falta > 0 and 2 or 1))   -- (v2) correcao suave (sem salto)
		local kS, kG = (S.trans and 0 or (G.trans and 2 or 1)), (G.trans and 0 or (S.trans and 2 or 1))
		if kS > 0 and not S.m:GetAttribute("CorpoElevado") then aplicarSeguro(S, pos(S) - u * passo * kS) end
		if kG > 0 and not G.m:GetAttribute("CorpoElevado") then aplicarSeguro(G, pos(G) + u * passo * kG) end
	end
	D.minCorpo = math.min(D.minCorpo or math.huge, dist - r1 - r2)
	local dt_ = os.clock() - t0; D.perf.n += 1; D.perf.soma += dt_; D.perf.max = math.max(D.perf.max, dt_)
end)
-- repeticao de clipes (ataques/reacoes): mesmo clipe nao-locomocao tocando > 6 vezes em 20 s
local LOCO = {Parado = 1, Correr = 1, Voo = 1, Voo_Rapido = 1, Pairar = 1, Subida = 1, Descida = 1, Giro_E = 1, Giro_D = 1, Andar = 1, Planeio = 1, Decolagem = 1, Pouso = 1}
for _, F in ipairs({S, G}) do
	local an = F.m:FindFirstChildWhichIsA("Animator", true); local hist = {}
	if an then an.AnimationPlayed:Connect(function(t)
		local n = t.Name; if LOCO[n] then return end
		hist[n] = hist[n] or {}; table.insert(hist[n], os.clock())
		local c = 0; for _, x in ipairs(hist[n]) do if os.clock() - x < 20 then c += 1 end end
		if c > 6 then D.checa.repeticoes[F.P.titulo .. ":" .. n] = c end
	end) end
end
-- ===== inicio: posicoes, provocacao explicita e cerebros =====
for _, F in ipairs({S, G}) do F.L:virarPara(pos(F.inimigo), function() return true end) end
for _, F in ipairs({S, G}) do
	if F.alturaInicial then
		F.L.noAr = true; F.m:SetAttribute("NoAr", true); F.L:_aplicar(pos(F) + Y * F.alturaInicial); F.L:clipe("Pairar", true); F.spd = 0
	end
end
task.spawn(function()
	log(("PROVOCACAO (teste): %s invade o territorio de %s; a partir daqui as decisoes sao da IA"):format((INV and G or S).P.titulo, (INV and S or G).P.titulo))
	for _, F in ipairs({S, G}) do F.ultimoVisto = pos(F.inimigo) end              -- (v2) a provocacao revela onde o rival entrou
	local function cerebro(F)
		while D.ativo and not F.m:GetAttribute("Incapacitado") and not F.inimigo.m:GetAttribute("Incapacitado") do
			local t0 = os.clock(); QUEM = F
			if os.clock() - (F.janT0 or 0) >= 1 then F.janT0 = os.clock(); F.consJan = 0 end
			local ok, err = pcall(decidir, F); QUEM = nil
			local dtc = os.clock() - t0; D.dec.n += 1; D.dec.soma += dtc; D.dec.max = math.max(D.dec.max, dtc)
			if not ok then log("ERRO " .. F.P.titulo .. ": " .. tostring(err)); task.wait(0.4) end
			task.wait(0.1)
		end
	end
	task.spawn(cerebro, S); task.wait(0.3); task.spawn(cerebro, G)
end)
task.spawn(function()
	local fim = os.clock() + X.DUR
	while D.ativo and not S.m:GetAttribute("Incapacitado") and not G.m:GetAttribute("Incapacitado") and os.clock() < fim do task.wait(0.2) end
	local venc = vida(S) >= vida(G) and S or G; local perd = venc == S and G or S
	local c = {}; for k, v in pairs(D.cont) do table.insert(c, k .. "=" .. v) end; table.sort(c)
	local rep = {}; for k, v in pairs(D.checa.repeticoes) do table.insert(rep, k .. "=" .. v) end
	log(("FIM (%s): %s %s (%d x %d) | menor folga entre corpos %.1f | sobreposicao corrigida max %.1f | travas voo %d | golpes sem visao %d | repeticoes [%s] | motor medio %.2f ms max %.2f ms"):format(
		D.cenario, venc.P.titulo, perd.m:GetAttribute("Incapacitado") and "vence (rival incapacitado)" or "a frente no tempo", vida(S), vida(G), D.minCorpo or -1, D.checa.sobrepMax,
		D.checa.travasVoo, D.checa.semLOS, table.concat(rep, ","), D.perf.soma / math.max(1, D.perf.n) * 1000, D.perf.max * 1000))
	log("CONTAGENS " .. table.concat(c, " "))
	local tv = {}; for _, x in ipairs(D.tvisao) do table.insert(tv, ("%s %.1fs(%s)"):format(x.quem:sub(8, 14), x.t, x.rota)) end
	local dur = os.clock() - D.t0
	local ns_, na_, dn_ = 0, 0, 0; for _, a in ipairs(D.ataques) do if a.hab == "SoproUmbral" or a.hab == "SoproGlacial" then ns_ += 1; if a.acerto then na_ += 1; dn_ += a.dano or 0 end end end
	log(("SOPROS (%s): usados %d, acertaram %d, dano total %d | cone do Sombrio %d graus"):format(_G.DUELO_SOPRO_ANTIGO and "decisao antiga" or "decisao v3", ns_, na_, dn_, CfgC.habilidades.SoproUmbral.porElemento.Sombra.angulo))
	log(("V2: visao recuperada [%s] | iniciados %d abortados %d | folga minima das asas %.1f | golpes barrados por obstaculo %d | consultas/s Sombrio %.1f Glacial %.1f | decisao media %.3f ms max %.2f ms"):format(
		table.concat(tv, ", "), #D.ataques, D.cont.mira_desistiu or 0, D.checa.folgaAsaMin, D.checa.golpeAtravessa, D.cons.Sombrio / dur, D.cons.Glacial / dur, D.dec.soma / math.max(1, D.dec.n) * 1000, D.dec.max * 1000))
	D.ativo = false; task.wait(0.3); conMotor:Disconnect()
	pcall(function()
		for _, F in ipairs({S, G}) do F.rotulo.Text = (F == venc) and "FIM: a frente" or "FIM"; if F.L.noAr then F.L:pousar(function() return true end, true) end; F.L:soltar(); F.E:Mudar("Idle") end
	end)
	D.fim = true
end)
-- limpeza (chamar ao terminar a sessao de teste)
_G.DueloLimpar = function()
	D.ativo = false
	for _, m in ipairs(workspace:GetChildren()) do if m.Name:match("^Duelo_") then m:Destroy() end end
	local t = workspace:FindFirstChild("_Duelo_Temp"); if t then t:Destroy() end
	local pq = SS:FindFirstChild("_Duelo_Parque"); if pq then for _, m in ipairs(pq:GetChildren()) do m.Parent = workspace end; pq:Destroy() end
	return "limpo"
end
return "duelo de decisao iniciado: " .. D.cenario
end
return "instalado: _G.DueloIniciar()"

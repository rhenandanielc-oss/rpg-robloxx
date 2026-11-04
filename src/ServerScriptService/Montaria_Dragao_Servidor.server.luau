-- Montaria_Dragao_Servidor (Script, ServerScriptService) — montaria do Dragao das Montanhas, AUTORIDADE DO SERVIDOR.
-- O cliente so manda INTENCAO (acelerar/virar/subir, direcao da camera, botoes); o servidor integra o movimento com
-- velocidades e curvas configuradas (sem teleporte/velocidade forjada), valida dono, estagio, missao de voo, estado,
-- espaco para decolar/pousar e desmontar, e anima com os clipes aprovados (Locomotor/EstadosDragao reaproveitados).
-- Um unico controlador por dragao (atributo Controlador); guardiao selvagem de ninho nunca e montavel.
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local SSS = game:GetService("ServerScriptService")
local RunService = game:GetService("RunService")

local pasta = RS:WaitForChild("Montaria_Dragoes")
local Cfg = require(pasta:WaitForChild("ConfigMontaria"))
local Locomotor = require(SSS:WaitForChild("IA_Dragao"):WaitForChild("Locomotor"))
local EstadosDragao = require(RS:WaitForChild("Comportamento_Dragoes"):WaitForChild("EstadosDragao"))

local function remoto(nome, classe)
	local r = pasta:FindFirstChild(nome) or Instance.new(classe); r.Name = nome; r.Parent = pasta; return r
end
local Comando = remoto("Comando", "RemoteEvent")                 -- cliente -> servidor: montar/desmontar/decolar/pousar/planar
local Entrada = remoto("Entrada", "UnreliableRemoteEvent")       -- cliente -> servidor: intencao de movimento (~15 Hz)
local Aviso = remoto("Aviso", "RemoteEvent")                     -- servidor -> cliente: acao bloqueada e motivo

-- o Locomotor usa estes campos (rampa em dy/dx e teto livre para voo)
local cfgLoc = {inclinacaoMax = 0.6, tetoMinVoo = Cfg.tetoDecolagem, giroParado = Cfg.giroParado}
local Y = Vector3.yAxis
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function yawDe(v) return math.atan2(v.X, v.Z) end
local function difAng(a, b) local d = (b - a) % (2 * math.pi); if d > math.pi then d -= 2 * math.pi end; return d end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end

local montarias = {}                                              -- [modelo] = M
local cavaleiros = {}                                             -- [player] = M
local estados, locos = {}, {}

local function avisar(plr, txt) if plr and plr.Parent then Aviso:FireClient(plr, txt) end end

-- autorizacao TEMPORARIA de voo para desenvolvimento: so servidor (ServerStorage nao replica), so no Studio, so para
-- UserIds listados, nunca no place de producao. Nao altera VooDesbloqueado nem a missao oficial.
local function vooDev(plr)
	local mod = game:GetService("ServerStorage"):FindFirstChild("ConfigDev_Montaria"); if not mod then return false end
	local ok, c = pcall(require, mod); if not ok or type(c) ~= "table" or c.ativo ~= true then return false end
	if not RunService:IsStudio() then return false end
	if table.find(c.placeIdsProducao or {}, game.PlaceId) then return false end
	return table.find(c.userIds or {}, plr.UserId) ~= nil
end

-- ===== sela ======================================================================================================
-- pose de REPOUSO do osso (cadeia de Bone.CFrame): WorldPosition no servidor ja inclui a animacao (ex.: abaixado)
local function repouso(b)
	local cf = b.CFrame; local p = b.Parent
	while p and p:IsA("Bone") do cf = p.CFrame * cf; p = p.Parent end
	return (p and p:IsA("BasePart") and p.CFrame or CFrame.new()) * cf
end
-- altura/avanco da sela por dragao (atributos AssentoAcima/AssentoFrente sobrepoem a config; portes diferentes)
local function acima(m) return m:GetAttribute("AssentoAcima") or Cfg.assento.acima end
local function assentoCF(m)
	local b = osso(m, Cfg.assento.osso); local root = m.PrimaryPart
	local p = repouso(b).Position
	local f = plano((repouso(osso(m, "Cabeca")).Position - repouso(osso(m, "Quadril")).Position)).Unit
	local centro = root.Position + plano(p - root.Position):Dot(f) * f                  -- na linha do dorso
	local pos = Vector3.new(centro.X, p.Y + acima(m), centro.Z) + f * (m:GetAttribute("AssentoFrente") or Cfg.assento.frente)
	return CFrame.lookAt(pos, pos + f)
end
local function prepararAssento(m)
	local root = m.PrimaryPart
	local a = root:FindFirstChild("Assento") or Instance.new("Attachment")
	a.Name = "Assento"; a.Parent = root; a.WorldCFrame = assentoCF(m)
	local pp = a:FindFirstChild("Montar") or Instance.new("ProximityPrompt")
	pp.Name = "Montar"; pp.ActionText = "Montar"; pp.ObjectText = m:GetAttribute("NomeExibicao") or "Dragao das Montanhas"; pp.HoldDuration = 0.3
	pp.MaxActivationDistance = Cfg.distMontar; pp.RequiresLineOfSight = false; pp.KeyboardKeyCode = Enum.KeyCode.E
	pp.GamepadKeyCode = Enum.KeyCode.ButtonX; pp.Parent = a
	return a, pp
end

-- ===== validacao =================================================================================================
local function podeMontar(plr, m)
	if typeof(m) ~= "Instance" or not m:IsA("Model") or not m:IsDescendantOf(workspace) or not m:GetAttribute("FormaRegional") then return false, "montaria invalida" end
	if m:GetAttribute("GuardiaoNinho") then return false, "Guardiao selvagem de ninho nao pode ser montado" end
	if m:GetAttribute("DonoUserId") ~= plr.UserId then return false, "Este dragao nao e seu" end
	local est = Cfg.estagios[m:GetAttribute("Estagio") or ""]
	if not est or not est[1] then return false, "Estagio de crescimento nao permite montaria" end
	if m:GetAttribute("Estagio") == "PreAdulto" and not Cfg.formasGrandes[m:GetAttribute("FormaRegional")] then return false, "Especie pequena demais para montaria" end
	if m:GetAttribute("Incapacitado") then return false, "O dragao esta incapacitado" end
	if m:GetAttribute("NoAr") then return false, "O dragao precisa estar no chao" end
	if m:GetAttribute("EmAtaque") then return false, "O dragao esta atacando" end
	if montarias[m] or m:GetAttribute("Controlador") then return false, "Montaria ocupada" end
	if cavaleiros[plr] then return false, "Voce ja esta montado" end
	local ch = plr.Character; local hrp = ch and ch:FindFirstChild("HumanoidRootPart"); local hum = ch and ch:FindFirstChildOfClass("Humanoid")
	if not (hrp and hum and hum.Health > 0) then return false, "personagem indisponivel" end
	if (hrp.Position - assentoCF(m).Position).Magnitude > Cfg.distMontar + 4 then return false, "Chegue mais perto" end
	return true, ch, hrp, hum
end

-- ===== animacao: espera clipe (com limite) =======================================================================
local function esperarTrilha(E, nome)
	local t = E:_trilha(nome); local lim = os.clock() + 4
	while t.Length <= 0 and os.clock() < lim do task.wait(0.05) end
	task.wait(math.max(0.2, t.Length / math.max(t.Speed, 0.01) - 0.3))
end
-- move o personagem em arco (servidor, ancorado durante a transicao)
local function arco(hrp, de, ate, dur, altura)
	local t0 = os.clock()
	while os.clock() - t0 < dur do
		RunService.Heartbeat:Wait()
		local k = math.min((os.clock() - t0) / dur, 1); local e = k * k * (3 - 2 * k)
		hrp.CFrame = de:Lerp(ate, e) + Y * math.sin(k * math.pi) * altura
	end
	hrp.CFrame = ate
end

-- ===== montar / desmontar ========================================================================================
local function aplicar(M, pos)
	local L = M.L
	local pf = M.m:GetAttribute("PresoFator")                               -- PATCH_CORRENTES_AR: preso pelas Correntes da Noite
	if pf then local atual = L:pos(); pos = atual + (pos - atual) * math.clamp(pf, 0, 1) end
	local giro = CFrame.Angles(0, L.psi, 0)
	local dir = giro:VectorToWorldSpace(L.f0); local direita = dir:Cross(Y).Unit
	M.m:PivotTo(CFrame.new(pos) * CFrame.fromAxisAngle(dir, M.roll) * CFrame.fromAxisAngle(direita, L.pitch) * giro * L.R0)
end

local soltar
local function montar(plr, m)
	local ok, ch, hrp, hum = podeMontar(plr, m)
	if not ok then avisar(plr, ch); return end
	m:SetAttribute("Controlador", "Montaria"); m:SetAttribute("Montaria_Transicao", true); m:SetAttribute("Cavaleiro", plr.UserId)
	m:SetAttribute("VooDev", vooDev(plr) or nil)                                                   -- so exibicao no HUD
	local E = estados[m] or EstadosDragao.novo(m); estados[m] = E
	local L = locos[m] or Locomotor.novo(m, E, cfgLoc); locos[m] = L
	L.noAr = false
	local M = {m = m, plr = plr, ch = ch, hrp = hrp, hum = hum, L = L, E = E, modo = "transicao", vel = 0, vy = 0, roll = 0,
		ent = {f = 0, t = 0, up = 0, correr = false}, ultEnt = 0, planar = false, conns = {}, clipeAte = 0}
	montarias[m] = M; cavaleiros[plr] = M
	local a, pp = prepararAssento(m); pp.Enabled = false
	-- 1) o dragao se abaixa (Montaria_Abaixar -> Aguardar)
	E:Mudar("MontariaEspera"); esperarTrilha(E, "Montaria_Abaixar")
	if montarias[m] ~= M then return end
	-- 2) o cavaleiro sobe em arco ate a sela e senta
	local sela = assentoCF(m) * CFrame.new(0, -acima(m) * 0.25, 0)          -- dragao abaixado: sela mais baixa
	hrp.Anchored = true; hum.Sit = false
	arco(hrp, hrp.CFrame, sela, 0.9, 8)
	local w = Instance.new("Weld"); w.Name = "SelaWeld"; w.Part0 = m.PrimaryPart; w.Part1 = hrp
	w.C0 = m.PrimaryPart.CFrame:ToObjectSpace(assentoCF(m)); w.Parent = hrp; M.weld = w
	M.pulo = {hum.JumpPower, hum.JumpHeight}; hum.JumpPower = 0; hum.JumpHeight = 0
	hrp.Anchored = false; hum.Sit = true
	local ov = Instance.new("ObjectValue"); ov.Name = "MontariaAtual"; ov.Value = m; ov.Parent = plr; M.ov = ov
	table.insert(M.conns, hum.Died:Connect(function() soltar(M, "morte") end))
	table.insert(M.conns, plr.CharacterRemoving:Connect(function() soltar(M, "personagem") end))
	table.insert(M.conns, hum:GetPropertyChangedSignal("Sit"):Connect(function() if M.weld and M.weld.Parent and not hum.Sit then hum.Sit = true end end))
	-- 3) levanta e libera o controle
	E:Mudar("Idle"); esperarTrilha(E, "Montaria_Levantar")
	if montarias[m] ~= M then return end
	L.atual = nil; M.modo = "chao"; m:SetAttribute("Montaria_Transicao", nil); m:SetAttribute("MontariaModo", "chao")
end

local function localDesmontar(M)
	local m = M.m; local root = m.PrimaryPart
	local ex = {m}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(ex, p.Character) end end
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = ex
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ex
	local f = M.L:frente(); local dir = f:Cross(Y).Unit
	for _, off in ipairs({-dir * 26, dir * 26, -f * 40, -dir * 34 - f * 10, dir * 34 - f * 10, f * 40}) do
		local p = root.Position + off
		local h = workspace:Raycast(p + Y * 40, -Y * 90, rp)
		if h and h.Normal.Y > 0.6 then
			local alvo = h.Position + Y * 3.2
			if #workspace:GetPartBoundsInBox(CFrame.new(alvo), Vector3.new(4, 5, 4), op) == 0 then return CFrame.lookAt(alvo, alvo + f) end
		end
	end
	return nil
end
-- desmontagem pedida pelo jogador: so no chao, parado e fora de transicao/ataque
local function desmontar(M)
	if M.modo ~= "chao" then avisar(M.plr, "Desmontar so com o dragao no chao"); return end
	if math.abs(M.vel) > 3 then avisar(M.plr, "Pare o dragao antes de desmontar"); return end
	if M.m:GetAttribute("EmAtaque") then avisar(M.plr, "Aguarde o ataque terminar"); return end
	local destino = localDesmontar(M); if not destino then avisar(M.plr, "Sem espaco seguro para desmontar aqui"); return end
	M.modo = "transicao"; M.m:SetAttribute("Montaria_Transicao", true)
	M.E:Mudar("MontariaEspera"); esperarTrilha(M.E, "Montaria_Abaixar")
	local hrp = M.hrp
	if M.weld then M.weld:Destroy(); M.weld = nil end
	if hrp and hrp.Parent then hrp.Anchored = true; M.hum.Sit = false; arco(hrp, hrp.CFrame, destino, 0.7, 6); hrp.Anchored = false end
	soltar(M, "desmontou")
end

-- encerra a montaria (pedido, morte, desconexao). No ar, o dragao plana e pousa sozinho antes de liberar.
local pousarAuto
soltar = function(M, motivo)
	if M.encerrando then return end
	M.encerrando = true
	for _, c in ipairs(M.conns) do c:Disconnect() end
	if M.weld then M.weld:Destroy(); M.weld = nil end
	local hum = M.hum
	if hum and hum.Parent then
		if M.pulo then hum.JumpPower, hum.JumpHeight = M.pulo[1], M.pulo[2] end
		hum.Sit = false
		if M.hrp and M.hrp.Parent then M.hrp.Anchored = false end
	end
	if M.ov then M.ov:Destroy() end
	cavaleiros[M.plr] = nil
	local m = M.m
	task.spawn(function()
		if m.Parent and M.modo ~= "chao" and M.modo ~= "transicao" then pousarAuto(M) end          -- nunca larga no ar
		if not m.Parent then montarias[m] = nil; return end
		m:SetAttribute("Cavaleiro", nil); m:SetAttribute("MontariaModo", nil); m:SetAttribute("Montaria_Transicao", nil); m:SetAttribute("VooDev", nil)
		m:SetAttribute("NoAr", false); M.L.noAr = false
		M.E:Mudar("Idle")
		montarias[m] = nil; m:SetAttribute("Controlador", nil)
		local a = m.PrimaryPart:FindFirstChild("Assento"); if a and a:FindFirstChild("Montar") then a.Montar.Enabled = true end
	end)
end

-- ===== entrada ===================================================================================================
local function entrada(M)
	if os.clock() - M.ultEnt > Cfg.entradaTimeout then return {f = 0, t = 0, up = 0, correr = false} end
	return M.ent
end
Entrada.OnServerEvent:Connect(function(plr, d)
	local M = cavaleiros[plr]; if not M or typeof(d) ~= "table" then return end
	if os.clock() - M.ultEnt < 1 / (Cfg.entradaHz * 2.5) then return end                          -- anti-spam
	local function n(v, a, b) v = tonumber(v); if not v or v ~= v then return 0 end; return math.clamp(v, a, b) end
	M.ent = {f = n(d.f, -1, 1), t = n(d.t, -1, 1), up = n(d.up, -1, 1), correr = d.c == true,
		cy = (tonumber(d.cy) and d.cy == d.cy) and d.cy or nil, cp = n(d.cp, -1.2, 1.2)}
	M.ultEnt = os.clock()
end)

-- ===== PATCH_ARREMETIDA_5S (02/11): bonus de velocidade da Arremetida DENTRO deste controlador ==================
-- O Nucleo marca ArremetidaFim (tempo do servidor) e ArremetidaImpacto; aqui a velocidade-alvo sobe, a aceleracao parte da
-- velocidade atual, o jogador segue dirigindo e as colisoes/relevo deste controlador continuam valendo. No fim, a
-- desaceleracao normal do controlador traz a velocidade de volta (sem parada brusca, sem ganho permanente).
local ARR = require(game:GetService("ServerScriptService"):WaitForChild("Combate_Dragao"):WaitForChild("ConfigCombate")).habilidades.Arremetida
local function arremetendo(m) return (m:GetAttribute("ArremetidaFim") or 0) > workspace:GetServerTimeNow() end
local function impactoArremetida(M)
	local t = M.m:GetAttribute("ArremetidaImpacto")
	if t and t ~= M.ultImpactoArr then M.ultImpactoArr = t; M.vel *= ARR.freioImpacto end   -- peso da colisao
end

-- ===== chao ======================================================================================================
local function clipe(M, nome, ritmo, segurar)
	if os.clock() < M.clipeAte and not segurar then
		if ritmo and M.L.trilha and M.L.atual == nome then M.L.trilha:AdjustSpeed(ritmo) end
		return
	end
	M.L:clipe(nome, true, ritmo); if segurar then M.clipeAte = os.clock() + segurar end
end
local function passoChao(M, dt)
	local m, L = M.m, M.L
	local e = entrada(M)
	local ataque = m:GetAttribute("EmAtaque")
	-- um so controlador por vez: durante a investida e a elevacao da Tempestade quem move o corpo e o combate
	local arr = arremetendo(m); impactoArremetida(M)                     -- PATCH_ARREMETIDA_5S
	if m:GetAttribute("CorpoElevado") then M.vel = 0; return end
	local fixo = ataque == "Ruptura" or ataque == "Coracao" or ataque == "Tempestade" or ataque == "Garra" or ataque == "Cauda"
		or (ataque == "Mordida" and not m:GetAttribute("MordidaEmMovimento"))   -- PATCH_MORDIDA_MOVIMENTO (03/11)
		or ataque == "Rajadas" or ataque == "ZeroAbsoluto" or ataque == "Nevasca"            -- PATCH_KIT_GELO
		or ataque == "Correntes"                                                            -- PATCH_CORRENTES_NOITE (Sombrio)
		or ataque == "Eclipse"                                                              -- PATCH_ECLIPSE_DRACONICO (Sombrio)
		or m:GetAttribute("Incapacitado")
	local alvo = 0
	if arr and not fixo then alvo = ARR.velChao                           -- investida: corre para frente; A/D e camera dirigem
	elseif not fixo then
		if e.f > 0.1 then alvo = (e.correr and (m:GetAttribute("VelCorrer") or Cfg.correrVel) or (m:GetAttribute("VelAndar") or Cfg.andarVel)) * math.min(e.f, 1)
			* (1 + (m:GetAttribute("RastroBonus") or 0))                                -- PATCH_RASTRO_BREU (03/11): passiva do Sombrio
		elseif e.f < -0.1 then alvo = -Cfg.recuarVel end
	end
	local a = math.abs(alvo) > math.abs(M.vel) and (arr and ARR.acelChao or Cfg.acelChao) or Cfg.freioChao
	M.vel += math.clamp(alvo - M.vel, -a * dt, a * dt)
	if alvo <= 0 and M.vel > Cfg.frenagemMin and not M.freando and not ataque then
		M.freando = true; M.L:clipe("Correr_Frenagem", false); M.clipeAte = os.clock() + 0.9
	end
	if M.vel < 2 then M.freando = false end
	-- giro: A/D; andando para frente sem A/D, segue a direcao da camera (gradual)
	local giro = M.vel > Cfg.andarVel + 1 and Cfg.giroCorrer or Cfg.giroAndar
	local yawRate = 0
	if not fixo then
		if math.abs(e.t) > 0.1 then
			yawRate = -e.t * math.rad(math.abs(M.vel) < 0.5 and Cfg.giroParado or giro)
		elseif e.f > 0.1 and e.cy then
			local alvoPsi = e.cy - yawDe(L.f0)
			yawRate = math.clamp(difAng(L.psi, alvoPsi) * 2.5, -math.rad(giro), math.rad(giro))
		end
	end
	L.psi += yawRate * dt
	local p = L:pos(); local f = L:frente()
	-- obstaculo: testado pela INTENCAO (sentido pedido) e pelo rumo ATUAL, mesmo parado. Antes so era retestado com
	-- vel > 0,3, mas o bloqueio zerava vel a cada quadro: o dragao ficava travado para sempre (causa da montaria travada).
	local sentido = alvo > 0 and 1 or alvo < 0 and -1 or 0
	if sentido ~= 0 and (os.clock() - (M.ultTeste or 0) > 0.15 or sentido ~= M.sentidoTestado) then
		M.ultTeste = os.clock(); M.sentidoTestado = sentido
		local ok, motivo = L:podePassar(f * sentido)
		M.bloqueado = not ok
		if not ok and os.clock() - (M.ultAvisoBloq or 0) > 2.5 then
			M.ultAvisoBloq = os.clock(); avisar(M.plr, "Caminho bloqueado (" .. tostring(motivo) .. "): vire para outro lado")
		end
	elseif sentido == 0 then M.bloqueado = false end
	if M.bloqueado and M.vel * sentido > 0 then M.vel = 0 end
	local np = p + f * M.vel * dt
	local g = L:chaoLocal(np)
	if not g then M.vel = 0; np = p; g = L:chaoLocal(p) or (p.Y - L.alturaPivo) end
	local gF = L:chaoLocal(np + f * 20) or g; local gT = L:chaoLocal(np - f * 20) or g
	L.pitch = -math.clamp(math.atan2(gF - gT, 40), math.rad(-14), math.rad(14))
	M.roll += (0 - M.roll) * math.min(1, 4 * dt)
	aplicar(M, Vector3.new(np.X, g + L.alturaPivo, np.Z))
	if math.floor(math.abs(M.vel)) ~= m:GetAttribute("Velocidade") then m:SetAttribute("Velocidade", math.floor(math.abs(M.vel))) end   -- PATCH_SOPRO_MOVIMENTO
	-- ataque que deixa andar (Sopro): as patas seguem o passo (Andar/Correr), o clipe do ataque so mexe pescoco/cabeca
	if ataque and fixo then return end
	if M.freando then return end
	if math.abs(M.vel) < 0.4 then
		if math.abs(yawRate) > 0.05 then clipe(M, yawRate > 0 and "Giro_E" or "Giro_D") else clipe(M, "Parado") end
	elseif M.vel > (m:GetAttribute("VelAndar") or Cfg.andarVel) + 2 then clipe(M, "Correr", M.vel / (m:GetAttribute("RitmoCorrerBase") or Cfg.ritmoCorrerBase))
	else clipe(M, "Andar", M.vel / (m:GetAttribute("RitmoAndarBase") or Cfg.ritmoAndarBase)) end
end

-- ===== ar: misturador de animacoes (clipes do afk.ai adaptados) ====================================================
-- Todas as trilhas de voo tocam juntas em laco; so os PESOS mudam, a partir de velocidade, curva, subida/descida,
-- planeio e mergulho. Base (Core): Voo/Pairar/Planeio/Curvas/Mergulho. Camadas (Action, so pescoco/cabeca/torax):
-- olhar para cima/baixo/esquerda/direita. Sem troca instantanea de pose: AdjustWeight com fade.
-- Subida_AFK/Descida_AFK so existem em rigs que os tem (apelidos do Silverwing); no V14 sao ignorados
local MIX_BASE = {"Voo_AFK", "Pairar_AFK", "Planeio_AFK", "Curva_Aerea_E_AFK", "Curva_Aerea_D_AFK", "Mergulho_AFK", "Subida_AFK", "Descida_AFK"}
local MIX_CAMADA = {"Olhar_Cima_AFK", "Olhar_Baixo_AFK", "Olhar_E_AFK", "Olhar_D_AFK"}
local function temMix(M) return M.E:_kfs("Voo_AFK") ~= nil end          -- V14 ou apelido (Silverwing)
local function iniciarMix(M)
	if not temMix(M) then return end
	if M.mix and M.mix.ativo then return end
	M.mix = M.mix or {t = {}, w = {}}
	if M.E.atual then M.E.atual:Stop(0.45); M.E.atual = nil end; M.L.atual = nil
	for _, n in ipairs(MIX_BASE) do
		if not (M.mix.t[n] or M.E:_kfs(n)) then continue end
		local t = M.mix.t[n] or M.E:_trilha(n); t.Priority = Enum.AnimationPriority.Core; t.Looped = true
		M.mix.t[n] = t; t:Play(0.45, n == "Voo_AFK" and 1 or 0.001); M.mix.w[n] = n == "Voo_AFK" and 1 or 0
	end
	for _, n in ipairs(MIX_CAMADA) do
		local ok, t = pcall(function() return M.mix.t[n] or M.E:_trilha(n) end)
		if ok and t then t.Priority = Enum.AnimationPriority.Action; t.Looped = true; M.mix.t[n] = t; t:Play(0.3, 0.001); M.mix.w[n] = 0 end
	end
	M.mix.ativo = true
end
local function pararMix(M, fade)
	if not (M.mix and M.mix.ativo) then return end
	for _, t in pairs(M.mix.t) do t:Stop(fade or 0.4) end
	M.mix.ativo = false
end
local function pesos(M, w)
	local soma = 0; for _, n in ipairs(MIX_BASE) do soma += (w[n] or 0) end
	for n, t in pairs(M.mix.t) do
		local alvo = w[n] or 0
		if table.find(MIX_BASE, n) and soma > 0 then alvo /= soma end             -- base sempre soma 1 (sem "buraco" de pose)
		alvo = math.max(alvo, 0.001)
		if math.abs(alvo - (M.mix.w[n] or 0)) > 0.025 then t:AdjustWeight(alvo, 0.25); M.mix.w[n] = alvo end
	end
end

-- ===== ar: MORDIDA AEREA (teste; so dragoes com VooLivre e clipe "Mordida_Aerea") =================================
-- Linha do tempo casada com o clipe (1,0 s): preparo 0-0.28 (freia, alinha com a camera) | disparo 0.28-0.62
-- (avanco real em alta velocidade na direcao da camera; para antes de parede) | mordida 0.40-0.66 (hitbox SO na
-- cabeca/boca, cada alvo 1x: dano + empurrao) | recuperacao: devolve o controle do voo. Alvos: NPCs com Humanoid
-- (jogadores ficam de fora ate haver regra de PvP). O cliente so pede; tudo e validado aqui.
local function iniciarMordida(M)
	local m = M.m; local MA = Cfg.mordidaAerea
	if M.modo ~= "voo" or not m:GetAttribute("VooLivre") then avisar(M.plr, "Mordida aerea: so em voo"); return end
	if m:GetAttribute("EmAtaque") or M.mordida then return end
	local agora = workspace:GetServerTimeNow()
	if (m:GetAttribute("RecargaFim_MordidaAerea") or 0) > agora then return end
	if not M.E:_kfs("Mordida_Aerea") then return end
	m:SetAttribute("RecargaFim_MordidaAerea", agora + MA.recarga); m:SetAttribute("RecargaDur_MordidaAerea", MA.recarga)
	m:SetAttribute("EmAtaque", "MordidaAerea")
	M.planar = false
	M.mordida = {t0 = os.clock(), atingidos = {}, velIni = M.vel}
	local t = M.E:_trilha("Mordida_Aerea"); t.Priority = Enum.AnimationPriority.Action; t.Looped = false
	t:Play(0.08); M.mordida.trilha = t
end
local function mordidaAcertos(M, dir)
	local m = M.m; local MA = Cfg.mordidaAerea
	local cab = osso(m, "Cabeca"); if not cab then return end
	local centro = cab.TransformedWorldCFrame.Position + dir * MA.avancoHitbox
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = {m, M.ch}
	for _, parte in ipairs(workspace:GetPartBoundsInRadius(centro, MA.raioHitbox, op)) do
		local alvo = parte:FindFirstAncestorWhichIsA("Model")
		local hum = alvo and alvo:FindFirstChildOfClass("Humanoid")
		if alvo and alvo:GetAttribute("GuardiaoNinho") and not hum then
			if not M.mordida.atingidos[alvo] then
				M.mordida.atingidos[alvo] = true
				local okN, Nc = pcall(require, game:GetService("ServerScriptService").Combate_Dragao.Nucleo)
				if okN and Nc.ferir(m, alvo, MA.dano, nil, "MordidaAerea", "moderado") then           -- aplica Burning (passiva)
					m:SetAttribute("MordidaAcertou", workspace:GetServerTimeNow()); M.vel *= MA.freioImpacto
				end
			end
		elseif hum and hum.Health > 0 and not M.mordida.atingidos[alvo] and not Players:GetPlayerFromCharacter(alvo) then
			M.mordida.atingidos[alvo] = true
			local okN, Nc = pcall(require, game:GetService("ServerScriptService").Combate_Dragao.Nucleo)
			if okN then Nc.ferir(m, alvo, MA.dano, nil, "MordidaAerea", "moderado") else hum:TakeDamage(MA.dano) end   -- + Burning
			local r = alvo:FindFirstChild("HumanoidRootPart") or alvo.PrimaryPart
			if r and not r.Anchored then r.AssemblyLinearVelocity += dir * MA.empurrao + Y * MA.empurrao * 0.35 end
			m:SetAttribute("MordidaAcertou", workspace:GetServerTimeNow())          -- cliente: tranco de camera
			M.vel *= MA.freioImpacto                                                     -- peso do impacto
		end
	end
end
-- chamada dentro do passoVooLivre; devolve true enquanto o ataque controla a velocidade/trajetoria
local function passoMordida(M, dt, e)
	local md = M.mordida; if not md then return false end
	local MA = Cfg.mordidaAerea; local t = os.clock() - md.t0
	if t >= MA.duracao then
		M.mordida = nil; M.m:SetAttribute("EmAtaque", nil)
		M.vel = math.min(M.vel, Cfg.vooRapidoVel)                                  -- recupera: segue voando, sem travar
		return false
	end
	local cp = math.clamp(e.cp or 0, -math.rad(MA.gamaMaxDescida), math.rad(MA.gamaMaxSubida))
	if t < MA.disparo then                                                          -- preparo: freia e mira
		M.vel += (math.max(md.velIni * 0.55, 10) - M.vel) * math.min(1, 6 * dt)
		M.gama += (cp - M.gama) * math.min(1, 8 * dt); md.gama = M.gama
	elseif t < MA.fimDisparo and not md.parou then                                   -- disparo (trajetoria travada na mira)
		M.gama = md.gama or M.gama
		if M.parede then md.parou = true; M.vel = math.min(M.vel, 20)
		else M.vel += (MA.velocidade - M.vel) * math.min(1, 14 * dt) end
	else                                                                             -- recuperacao
		M.vel += (math.max(md.velIni, Cfg.vooVel * 0.7) - M.vel) * math.min(1, 3 * dt)
	end
	if t >= MA.inicioMordida and t <= MA.fimMordida then
		mordidaAcertos(M, (M.L:frente() * math.cos(M.gama) + Y * math.sin(M.gama)).Unit)
	end
	return true
end

-- ===== ar: VOO LIVRE (atributo VooLivre no modelo; teste do Dragao Glacial) =======================================
-- Camera = direcao (com W o pitch da camera vira subida/descida). W acelera; S NAO faz nada no ar; sem W desacelera
-- ate PARAR no ar (voo estacionario, batidas de sustentacao); Espaco/Ctrl sobem/descem parado. Pouso automatico:
-- perto do chao, devagar e com intencao de descer (passagem rapida rente ao chao nao pousa). Sem atributo: controle antigo.
local function passoVooLivre(M, dt)
	local m, L = M.m, M.L
	local e = entrada(M)
	local ataque = m:GetAttribute("EmAtaque")
	if not (M.mix and M.mix.ativo) then iniciarMix(M) end
	local V, VL = Cfg.voo, Cfg.vooLivre
	local arr = arremetendo(m); impactoArremetida(M)                                -- PATCH_ARREMETIDA_5S
	local f = arr and 1 or math.max(e.f, 0)                                           -- S sem funcao no ar; investida = empuxo pleno
	local wNovo = f > 0.1 and (M.fAnt or 0) <= 0.1; local upNovo = (e.up or 0) > 0.5 and (M.upAnt or 0) <= 0.5
	M.fAnt, M.upAnt = f, e.up or 0
	if m:GetAttribute("Incapacitado") then M.planar = true
	elseif M.planar and (wNovo or upNovo) and os.clock() - (M.planarDesde or 0) > 0.5 then M.planar = false end
	local mover = math.clamp(M.vel / VL.velPlena, 0, 1)                               -- 0 parado .. 1 voo pleno
	-- trajetoria: com W segue o pitch da camera; sem W a altitude e mantida
	local cp = e.cp or 0; if math.abs(cp) < math.rad(V.zonaMorta) then cp = 0 end
	local gAlvo = f > 0.1 and math.clamp(cp * V.ganhoPitch, -math.rad(V.gamaMaxDescida), math.rad(V.gamaMaxSubida)) or 0
	-- E/Q tem PRIORIDADE sobre o pitch da camera (sem disputa): com W, sobe/desce avancando; sem W, o vertical do hover
	if f > 0.1 and math.abs(e.up or 0) > 0.3 then gAlvo = (e.up > 0 and 1 or -1) * math.rad(VL.gamaEQ or 35) end
	if M.planar then
		gAlvo = math.min(gAlvo, M.vel > 30 and math.rad(22) or -math.rad(V.planeioGama))
		if (e.up or 0) < -0.3 then gAlvo = math.min(gAlvo, -math.rad(16)) end                 -- Ctrl no planeio: desce para pousar
	else gAlvo *= math.max(mover, 0.35) end
	M.gama = M.gama or 0
	M.gama += math.clamp(gAlvo - M.gama, -math.rad(V.gamaTaxa) * dt, math.rad(V.gamaTaxa) * dt)
	-- velocidade: W leva ao alvo; sem W freia suave ate zero; subir custa e mergulhar ganha (moderado)
	local alvoVel = arr and ARR.velAr or f > 0.1 and (e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * f * (1 + (m:GetAttribute("RastroBonus") or 0)) or 0   -- PATCH_RASTRO_BREU
	local acel
	local mergulhando = M.gama < -math.rad(V.mergulhoInicio)
	if M.planar then acel = -Cfg.planeioPerda
	elseif alvoVel > M.vel then acel = arr and ARR.acelAr or Cfg.acelVoo
	elseif mergulhando and f > 0.1 then acel = 0                                        -- mergulho com W: a gravidade acelera
	else acel = -VL.desacel end
	if M.planar or f > 0.1 then acel -= V.gravidade * math.sin(M.gama) * (M.planar and 1 or 0.5) end
	if passoMordida(M, dt, e) then acel = 0 end                                       -- ataque controla a velocidade
	M.vel = math.clamp(M.vel + acel * dt, M.planar and Cfg.planeioMin or 0, math.max(V.mergulhoVel, Cfg.mordidaAerea.velocidade, arr and ARR.velAr or 0))
	-- vertical no estacionario (Espaco/Ctrl)
	local vyH = 0
	if not M.planar and (e.up or 0) ~= 0 and f <= 0.1 then vyH = (e.up > 0 and e.up * VL.vSubidaParado or e.up * VL.vDescidaParado) * (1 - mover * 0.6) end
	M.vyH = (M.vyH or 0) + (vyH - (M.vyH or 0)) * math.min(1, 4 * dt)
	-- rumo: segue o yaw da camera (parado tambem gira, mais devagar no ar que no chao)
	local k = math.clamp((M.vel - Cfg.vooVel) / (Cfg.vooRapidoVel - Cfg.vooVel), 0, 1)
	local lento = math.clamp((V.velGiroLento - M.vel) / V.velGiroLento, 0, 1)
	local maxGiro = math.rad(Cfg.giroVoo + (Cfg.giroVooRapido - Cfg.giroVoo) * k + (V.giroLento - Cfg.giroVoo) * lento)
	local yawAlvo = -e.t * maxGiro
	if e.cy then yawAlvo += difAng(L.psi, e.cy - yawDe(L.f0)) * V.ganhoYaw end
	yawAlvo = math.clamp(yawAlvo, -maxGiro, maxGiro)
	M.yawRate = M.yawRate or 0
	M.yawRate += math.clamp(yawAlvo - M.yawRate, -math.rad(V.acelGiro) * dt, math.rad(V.acelGiro) * dt)
	L.psi += M.yawRate * dt
	M.roll += (-(M.yawRate / maxGiro) * math.rad(Cfg.inclinacaoMax) * mover - M.roll) * math.min(1, Cfg.suavRoll * dt)
	-- relevo / obstaculos (tamanhos do corpo por atributo: CorpoAltura/CorpoRaio)
	local p = L:pos(); local fr = L:frente()
	local hC, rC = m:GetAttribute("CorpoAltura") or 34, m:GetAttribute("CorpoRaio") or 22
	if os.clock() - (M.ultTeste or 0) > 0.15 then
		M.ultTeste = os.clock()
		local g = L:chaoEm(p); if g then M.ultimoChao = g end; g = g or M.ultimoChao
		M.chaoY = g; M.minY = g and (g + L.alturaPivo + (m:GetAttribute("FolgaChao") or Cfg.folgaChao)) or nil
		M.parede = M.vel > 4 and workspace:Spherecast(p + Y * hC, rC, fr * math.max(rC * 1.4, M.vel * 1.2), L.params) ~= nil
		M.teto = workspace:Raycast(p + Y * hC, Y * rC * 1.2, L.params) ~= nil
	end
	if M.parede then M.gama = math.max(M.gama, math.rad(30)); M.vel = math.min(M.vel, 20) end
	if M.teto and (M.gama > 0 or M.vyH > 0) then M.gama = math.min(M.gama, 0); M.vyH = math.min(M.vyH, 0) end
	local vy = M.vel * math.sin(M.gama) + M.vyH
	local np = p + fr * (M.vel * math.cos(M.gama) * dt) + Y * (vy * dt)
	-- pouso automatico: candidato aqui; o laco valida o local (localPouso) e pousa
	local alturaLivre = M.chaoY and (p.Y - (M.chaoY + L.alturaPivo)) or math.huge
	-- intencao: descendo devagar; ou Ctrl segurado (pedido explicito: aceita velocidade maior). Rente ao chao em W
	-- rapido, sem Ctrl, e passagem: nao pousa
	local ctrl = (e.up or 0) < -0.3
	local intencao = (M.vel < VL.velMaxPouso and vy < -1.5) or (ctrl and M.vel < VL.velMaxPouso * 1.4)
	M.candidatoPouso = (not ataque) and alturaLivre < (m:GetAttribute("AlturaPouso") or VL.alturaPouso) and intencao
	if M.minY and np.Y < M.minY then
		np = Vector3.new(np.X, M.minY, np.Z); if M.gama < 0 then M.gama *= 0.5 end; if M.vyH < 0 then M.vyH = 0 end
	end
	-- em aplicar(), pitch POSITIVO ergue o focinho (giro em torno de frente x Y): subida = nariz para cima
	L.pitch += (math.clamp(M.gama * V.narizSegue * math.max(mover, 0.3), -math.rad(V.pitchMax or 40), math.rad(V.pitchMax or 40)) - L.pitch) * math.min(1, (V.pitchResp or 4) * dt)
	aplicar(M, np)
	m:SetAttribute("Velocidade", math.floor(M.vel))
	-- pesos das animacoes (base soma 1)
	M.planSuave = (M.planSuave or 0) + ((M.planar and 1 or 0) - (M.planSuave or 0)) * math.min(1, 3 * dt)
	local gd = math.deg(M.gama)
	local mergulho = math.clamp((-gd - V.mergulhoInicio) / 18, 0, 1)
	local curva = math.clamp(math.abs(M.yawRate) / maxGiro, 0, 1) * mover
	local pairar = math.clamp((VL.velPairar - M.vel) / VL.velPairar, 0, 1)
	local resto = 1 - mergulho
	local pl, ba = resto * M.planSuave, resto * (1 - M.planSuave)
	local sub = math.clamp(gd / 16, 0, 1) * (1 - pairar)
	local des = math.clamp(-gd / 12, 0, 1) * (1 - pairar)
	local ativo = ba * (1 - pairar) * (1 - curva * 0.35)
	local esq = M.yawRate > 0
	local w = {Mergulho_AFK = mergulho, Planeio_AFK = pl * (1 - curva), Pairar_AFK = ba * pairar,
		Voo_AFK = ativo * (1 - sub) * (1 - des), Subida_AFK = ativo * sub, Descida_AFK = ativo * des}
	w[esq and "Curva_Aerea_E_AFK" or "Curva_Aerea_D_AFK"] = pl * curva + ba * (1 - pairar) * curva * 0.35
	-- PATCH_MIX_VERTICAL (02/11): parado no ar subindo (E) ou descendo (Q): Subida/Descida entram sobre o Pairar
	if m:GetAttribute("MixVerticalParado") and M.vyH ~= 0 then
		local hp = ba * pairar
		local sv = math.clamp(M.vyH / math.max(1, VL.vSubidaParado), 0, 1) * 0.7
		local dv = math.clamp(-M.vyH / math.max(1, VL.vDescidaParado), 0, 1) * 0.7
		w.Pairar_AFK = hp * (1 - sv - dv); w.Subida_AFK += hp * sv; w.Descida_AFK += hp * dv
	end
	pesos(M, w)
	local ritmo = 0.9 + 0.45 * k + (gd > 8 and 0.25 or 0) + (f > 0.1 and 0.1 or 0)
	if math.abs(ritmo - (M.ritmoVoo or 1)) > 0.05 then
		for _, n in ipairs({"Voo_AFK", "Subida_AFK"}) do if M.mix.t[n] then M.mix.t[n]:AdjustSpeed(ritmo) end end
		M.ritmoVoo = ritmo
	end
	m:SetAttribute("VooEstado", mergulho > 0.5 and "mergulho" or M.planar and "planeio" or pairar > 0.7 and "parado" or gd > 8 and "subida" or gd < -8 and "descida" or "voo")
end

-- ===== ar: controlador guiado pela camera ==========================================================================
-- Rumo e inclinacao da trajetoria seguem a CAMERA (yaw/pitch enviados pelo cliente, limitados no servidor);
-- W acelera, S desacelera ate a velocidade minima de sustentacao, sem nada mantem a velocidade. Curvas progressivas
-- (taxa e aceleracao de giro limitadas), inclinacao do corpo pela curva, nariz acompanha a trajetoria.
local function passoVoo(M, dt)
	local m, L = M.m, M.L
	local e = entrada(M)
	local ataque = m:GetAttribute("EmAtaque")
	local arr = arremetendo(m); impactoArremetida(M)                                         -- PATCH_ARREMETIDA_5S (bonus abaixo)
	if m:GetAttribute("CorpoElevado") then M.vel = 0; M.vyH = 0; return end                   -- PATCH_KIT_GELO: Nevasca no ar (o Nucleo move)
	if m:GetAttribute("VooLivre") and temMix(M) then return passoVooLivre(M, dt) end
	if m:GetAttribute("Incapacitado") then M.planar = true end                                   -- incapacitado: plana e desce
	if temMix(M) then
		if not (M.mix and M.mix.ativo) then iniciarMix(M) end
		local V = Cfg.voo
		-- W/Espaco APERTADOS de novo (borda, nao "segurado") voltam a bater asas: ligar o planeio com W ainda no ultimo
		-- pacote nao o desliga na hora
		local wNovo = e.f > 0.1 and (M.fAnt or 0) <= 0.1; local upNovo = (e.up or 0) > 0.5 and (M.upAnt or 0) <= 0.5
		M.fAnt, M.upAnt = e.f, e.up or 0
		if M.planar and (wNovo or upNovo) and os.clock() - (M.planarDesde or 0) > 0.5 and not m:GetAttribute("Incapacitado") then M.planar = false end
		-- inclinacao desejada da trajetoria (gama) pela camera; zona morta = voo horizontal estavel
		local cp = e.cp or 0
		if math.abs(cp) < math.rad(V.zonaMorta) then cp = 0 end
		local gAlvo = math.clamp(cp * V.ganhoPitch + (e.up or 0) * math.rad(15), -math.rad(V.gamaMaxDescida), math.rad(V.gamaMaxSubida))
		-- planeio nao sustenta subida; com velocidade sobrando (saida de mergulho) troca velocidade por altura
		if M.planar then gAlvo = math.min(gAlvo, M.vel > 30 and math.rad(22) or -math.rad(V.planeioGama)) end
		M.gama = M.gama or 0
		M.gama += math.clamp(gAlvo - M.gama, -math.rad(V.gamaTaxa) * dt, math.rad(V.gamaTaxa) * dt)
		-- velocidade: empuxo (W/S) + gravidade na trajetoria (sobe perde, mergulha ganha) + sustentacao minima
		local acel = 0
		if arr then acel += (M.vel < ARR.velAr and ARR.acelAr or 0); M.planar = false
		elseif not M.planar then
			if e.f > 0.1 then acel += Cfg.acelVoo * e.f * (M.vel < Cfg.vooRapidoVel and 1 or 0)
			elseif e.f < -0.1 then acel -= Cfg.freioVoo * -e.f end
		else acel -= Cfg.planeioPerda end
		acel -= V.gravidade * math.sin(M.gama)
		if M.vel > Cfg.vooRapidoVel and M.gama > -math.rad(20) and not arr then acel -= V.arrastoExcesso * (M.vel - Cfg.vooRapidoVel) end
		M.vel = math.clamp(M.vel + acel * dt, M.planar and Cfg.planeioMin or Cfg.vooMin, arr and math.max(V.mergulhoVel, ARR.velAr) or V.mergulhoVel)
		-- rumo: segue o yaw da camera; taxa e aceleracao de giro limitadas (sem giro instantaneo / oscilacao)
		local k = math.clamp((M.vel - Cfg.vooVel) / (Cfg.vooRapidoVel - Cfg.vooVel), 0, 1)
		local lento = math.clamp((V.velGiroLento - M.vel) / V.velGiroLento, 0, 1)
		local maxGiro = math.rad(Cfg.giroVoo + (Cfg.giroVooRapido - Cfg.giroVoo) * k + (V.giroLento - Cfg.giroVoo) * lento)
		local yawAlvo = -e.t * maxGiro
		if e.cy then yawAlvo += difAng(L.psi, e.cy - yawDe(L.f0)) * V.ganhoYaw end
		yawAlvo = math.clamp(yawAlvo, -maxGiro, maxGiro)
		M.yawRate = M.yawRate or 0
		M.yawRate += math.clamp(yawAlvo - M.yawRate, -math.rad(V.acelGiro) * dt, math.rad(V.acelGiro) * dt)
		L.psi += M.yawRate * dt
		local rollAlvo = -(M.yawRate / maxGiro) * math.rad(Cfg.inclinacaoMax)
		M.roll += (rollAlvo - M.roll) * math.min(1, Cfg.suavRoll * dt)
		-- deslocamento e relevo
		M.vy = M.vel * math.sin(M.gama)
		local p = L:pos(); local f = L:frente()
		if os.clock() - (M.ultTeste or 0) > 0.2 then
			M.ultTeste = os.clock()
			local g = L:chaoEm(p)
			if g then M.ultimoChao = g end                                              -- fora do mapa (sem chao): vale o ultimo chao
			g = g or M.ultimoChao
			M.minY = g and (g + L.alturaPivo + Cfg.folgaChao) or nil
			M.parede = workspace:Spherecast(p + Y * 34, 22, f * math.max(30, M.vel * 1.2), L.params) ~= nil
			M.teto = workspace:Raycast(p + Y * 30, Y * 26, L.params) ~= nil
		end
		if M.parede then M.gama = math.max(M.gama, math.rad(30)); M.vel = math.min(M.vel, 20) end   -- assistencia: arremete sobre o obstaculo
		if M.teto and M.gama > 0 then M.gama = 0 end
		local np = p + f * (M.vel * math.cos(M.gama) * dt) + Y * (M.vel * math.sin(M.gama) * dt)
		if M.minY and np.Y < M.minY then
			np = Vector3.new(np.X, M.minY, np.Z); if M.gama < 0 then M.gama *= 0.5 end            -- rente ao chao: nivela
		end
		local pitchAlvo = math.clamp(-M.gama * V.narizSegue, -math.rad(40), math.rad(40))
		L.pitch += (pitchAlvo - L.pitch) * math.min(1, 4 * dt)
		aplicar(M, np)
		m:SetAttribute("Velocidade", math.floor(M.vel))
		-- pesos das animacoes
		M.planSuave = (M.planSuave or 0) + ((M.planar and 1 or 0) - (M.planSuave or 0)) * math.min(1, 3 * dt)
		local gd = math.deg(M.gama)
		local mergulho = math.clamp((-gd - V.mergulhoInicio) / 18, 0, 1)
		local curva = math.clamp(math.abs(M.yawRate) / maxGiro, 0, 1)
		local pairar = math.clamp((V.velPairar - M.vel) / 10, 0, 1)
		local resto = 1 - mergulho
		local pl, ba = resto * M.planSuave, resto * (1 - M.planSuave)
		local esq = M.yawRate > 0
		local w = {Mergulho_AFK = mergulho, Planeio_AFK = pl * (1 - curva),
			Voo_AFK = ba * (1 - pairar) * (1 - curva * 0.35), Pairar_AFK = ba * pairar * (1 - curva * 0.35)}
		local wc = pl * curva + ba * curva * 0.35
		w[esq and "Curva_Aerea_E_AFK" or "Curva_Aerea_D_AFK"] = wc
		if not ataque then                                                             -- camadas de orientacao da cabeca
			w.Olhar_Cima_AFK = math.clamp(gd / 30, 0, 1) * 0.8; w.Olhar_Baixo_AFK = math.clamp(-gd / 30, 0, 1) * 0.8
			w.Olhar_E_AFK = esq and curva * 0.75 or 0; w.Olhar_D_AFK = (not esq) and curva * 0.75 or 0
		end
		pesos(M, w)
		local tv = M.mix.t.Voo_AFK                                                    -- batidas mais fortes/rapidas subindo e acelerando
		local ritmo = 0.9 + 0.45 * k + (gd > 8 and 0.25 or 0) + (e.f > 0.1 and 0.1 or 0)
		if math.abs(ritmo - (M.ritmoVoo or 1)) > 0.05 then tv:AdjustSpeed(ritmo); M.ritmoVoo = ritmo end
		m:SetAttribute("VooEstado", mergulho > 0.5 and "mergulho" or M.planar and "planeio" or gd > 8 and "subida" or gd < -8 and "descida" or "voo")
		return
	end
	-- velocidade
	if M.planar then
		M.vel = math.max(Cfg.planeioMin, M.vel - Cfg.planeioPerda * dt)
	else
		local alvo = e.f > 0.1 and (e.correr and Cfg.vooRapidoVel or Cfg.vooVel) * e.f or Cfg.vooMin
		local a = alvo > M.vel and Cfg.acelVoo or Cfg.freioVoo
		M.vel += math.clamp(alvo - M.vel, -a * dt, a * dt)
	end
	-- rumo: segue a camera quando acelera; A/D somam. Taxa limitada (curvas largas para o porte do dragao)
	local k = math.clamp((M.vel - Cfg.vooVel) / (Cfg.vooRapidoVel - Cfg.vooVel), 0, 1)
	local maxGiro = math.rad(Cfg.giroVoo + (Cfg.giroVooRapido - Cfg.giroVoo) * k)
	local yawRate = -e.t * maxGiro
	if e.f > 0.1 and e.cy then yawRate += difAng(L.psi, e.cy - yawDe(L.f0)) * 1.8 end
	yawRate = math.clamp(yawRate, -maxGiro, maxGiro)
	L.psi += yawRate * dt
	local rollAlvo = -(yawRate / maxGiro) * math.rad(Cfg.inclinacaoMax)
	M.roll += (rollAlvo - M.roll) * math.min(1, Cfg.suavRoll * dt)
	-- vertical
	local vyAlvo
	if M.planar then
		if e.up > 0.5 and not m:GetAttribute("Incapacitado") then M.planar = false end           -- bater asas de novo sai do planeio
		vyAlvo = -Cfg.planeioQueda
	else
		vyAlvo = (e.up > 0 and e.up * Cfg.vSubida or e.up * Cfg.vDescida) + (e.f > 0.1 and math.sin(e.cp or 0) * M.vel * Cfg.pitchCamera or 0)
	end
	vyAlvo = math.clamp(vyAlvo, -Cfg.vDescida, Cfg.vSubida)
	M.vy += math.clamp(vyAlvo - M.vy, -40 * dt, 40 * dt)
	-- relevo e obstaculos
	local p = L:pos(); local f = L:frente()
	if os.clock() - (M.ultTeste or 0) > 0.2 then
		M.ultTeste = os.clock()
		local g = L:chaoEm(p); M.minY = g and (g + L.alturaPivo + Cfg.folgaChao) or nil
		M.parede = workspace:Spherecast(p + Y * 34, 22, f * math.max(30, M.vel * 1.4), L.params) ~= nil
		M.teto = workspace:Raycast(p + Y * 30, Y * 26, L.params) ~= nil
	end
	if M.parede then M.vel = math.min(M.vel, 6); M.vy = math.max(M.vy, Cfg.vSubida * 0.7) end
	if M.teto and M.vy > 0 then M.vy = 0 end
	local np = p + f * M.vel * dt + Y * M.vy * dt
	if M.minY and np.Y < M.minY then np = Vector3.new(np.X, M.minY, np.Z); if M.vy < 0 then M.vy = 0 end end
	L.pitch = math.clamp(-math.atan2(M.vy, math.max(M.vel, 10)) * 0.6, math.rad(-20), math.rad(20))
	aplicar(M, np)
	m:SetAttribute("Velocidade", math.floor(M.vel))
	if ataque then return end
	if M.planar then clipe(M, "Planeio")
	elseif math.abs(yawRate) > maxGiro * 0.6 then clipe(M, yawRate > 0 and "Curva_Aerea_E" or "Curva_Aerea_D", nil, 0.4)
	elseif M.vy > 8 then clipe(M, "Subida", nil, 0.4)
	elseif M.vy < -10 then clipe(M, "Descida", nil, 0.4)
	elseif e.correr and e.f > 0.1 then clipe(M, "Voo_Rapido")
	else clipe(M, "Voo") end
end

-- ===== decolar / pousar ==========================================================================================
local function decolar(M)
	local m, L = M.m, M.L
	if M.modo ~= "chao" then return end
	if m:GetAttribute("EmAtaque") then avisar(M.plr, "Aguarde o ataque terminar"); return end
	local est = Cfg.estagios[m:GetAttribute("Estagio") or ""]
	if not (est and est[2]) then avisar(M.plr, "Este estagio ainda nao voa montado"); return end
	if m:GetAttribute("VooDesbloqueado") ~= true and not vooDev(M.plr) then avisar(M.plr, "Voo montado bloqueado: conclua a missao de voo"); return end
	if not L:ceuLivre() then avisar(M.plr, "Sem espaco acima para decolar"); return end
	M.modo = "decolando"; m:SetAttribute("Montaria_Transicao", true); m:SetAttribute("MontariaModo", "decolando")
	M.clipeAte = 0
	local t = L:clipe("Decolagem", false, nil, 0.25)
	local lim = os.clock() + 4; while t.Length <= 0 and os.clock() < lim do task.wait(0.05) end
	local dur = math.max(t.Length, 0.8); local t0 = os.clock()
	while os.clock() - t0 < dur - 0.2 and montarias[m] == M do                                  -- impulso: frente + subida progressiva
		local dt = RunService.Heartbeat:Wait()
		local k = (os.clock() - t0) / dur
		M.vel = math.max(M.vel * (1 - dt), 3)
		aplicar(M, L:pos() + L:frente() * M.vel * dt + Y * (k > 0.4 and 9 * dt or 0))
	end
	if montarias[m] ~= M or M.encerrando then return end
	L.noAr = true; m:SetAttribute("NoAr", true)
	M.vel = math.max(M.vel, 18); M.vy = 8; M.gama = math.rad(12); M.yawRate = 0; M.planar = false; M.clipeAte = 0
	if m:GetAttribute("VooLivre") then M.vel = math.max(M.vel * 0.5, 10); M.vyH = 6 end          -- sai do chao subindo, sem disparar
	M.modo = "voo"; m:SetAttribute("Montaria_Transicao", nil); m:SetAttribute("MontariaModo", "voo")
	iniciarMix(M)                                                                       -- decolagem -> voo com fade
end

-- local de pouso: chao firme, pouco inclinado, sem obstaculo no caminho vertical (arvore/rocha/parede)
local function localPouso(M)
	local L = M.L; local p = L:pos()
	local h = workspace:Raycast(p + Y * 5, -Y * Cfg.pousoAlcance, L.params)
	if not h then return nil, "Alto demais para pousar" end
	if h.Normal.Y < Cfg.pousoInclinacaoMin then return nil, "Terreno inclinado demais para pousar" end
	local s = workspace:Spherecast(p + Y * 10, M.m:GetAttribute("CorpoRaio") or 14, -Y * (p.Y - h.Position.Y + 2), L.params)
	if s and s.Position.Y > h.Position.Y + 5 then return nil, "Local de pouso obstruido" end
	return h.Position.Y
end
local function descerEPousar(M, g)
	local m, L = M.m, M.L
	M.modo = "pousando"; m:SetAttribute("Montaria_Transicao", true); m:SetAttribute("MontariaModo", "pousando")
	pararMix(M, 0.5); M.gama = 0; m:SetAttribute("VooEstado", nil)                   -- voo -> descida de pouso com fade
	while m.Parent do
		local dt = RunService.Heartbeat:Wait()
		local p = L:pos(); local alvoY = g + L.alturaPivo
		M.vel = math.max(0, M.vel - 14 * dt); M.roll *= (1 - math.min(1, 3 * dt)); L.pitch *= (1 - math.min(1, 3 * dt))
		if p.Y - alvoY <= Cfg.alturaMinPouso then break end
		L:clipe("Descida", true)
		local np = p + L:frente() * M.vel * dt
		local g2 = L:chaoLocal(np); if g2 then g = g2; alvoY = g + L.alturaPivo end
		aplicar(M, Vector3.new(np.X, math.max(alvoY, p.Y - Cfg.vPouso * dt), np.Z))
	end
	if not m.Parent then return end
	M.roll, L.pitch = 0, 0
	aplicar(M, Vector3.new(L:pos().X, g + L.alturaPivo, L:pos().Z))
	local t = L:clipe("Pouso", false, nil, 0.2)
	local lim = os.clock() + 4; while t.Length <= 0 and os.clock() < lim do task.wait(0.05) end
	task.wait(math.max(0.3, t.Length - 0.25))
	L.noAr = false; m:SetAttribute("NoAr", false); m:SetAttribute("Velocidade", 0)
	M.vel, M.vy, M.planar = 0, 0, false; M.clipeAte = 0; L.atual = nil
	M.modo = "chao"; m:SetAttribute("Montaria_Transicao", nil); m:SetAttribute("MontariaModo", "chao")
end
local function pousar(M)
	if M.modo ~= "voo" then return end
	local g, motivo = localPouso(M); if not g then avisar(M.plr, motivo); return end
	descerEPousar(M, g)
end
-- pouso automatico (desconexao/morte/incapacitacao): plana ate achar chao valido
pousarAuto = function(M)
	M.planar = true
	local lim = os.clock() + 30
	while M.m.Parent and os.clock() < lim do
		local g = localPouso(M)
		if g then descerEPousar(M, g); return end
		passoVoo(M, RunService.Heartbeat:Wait())
	end
end

RunService.Heartbeat:Connect(function(dt)
	for m, M in pairs(montarias) do
		if not m.Parent then montarias[m] = nil
		elseif not M.encerrando then
			if M.modo == "chao" then passoChao(M, dt)
			elseif M.modo == "voo" then
				passoVoo(M, dt)
				if M.candidatoPouso and M.modo == "voo" then                                   -- pouso automatico (VooLivre)
					M.candidatoPouso = false
					local g = localPouso(M)
					if g then M.modo = "pousando"; task.spawn(descerEPousar, M, g) end
				end
				if m:GetAttribute("Incapacitado") and localPouso(M) then task.spawn(descerEPousar, M, (localPouso(M))) end
			end
		end
	end
end)

Comando.OnServerEvent:Connect(function(plr, acao, m)
	if acao == "montar" then task.spawn(montar, plr, m); return end
	local M = cavaleiros[plr]; if not M or M.encerrando then return end
	if acao == "desmontar" then task.spawn(desmontar, M)
	elseif acao == "decolar" then task.spawn(decolar, M)
	elseif acao == "pousar" then task.spawn(pousar, M)
	elseif acao == "planar" then if M.modo == "voo" then M.planar = not M.planar; M.planarDesde = os.clock() end
	elseif acao == "mordida" then iniciarMordida(M) end
end)
Players.PlayerRemoving:Connect(function(plr) local M = cavaleiros[plr]; if M then soltar(M, "desconexao") end end)

-- prompts de montaria nos dragoes com dono (guardioes nao recebem)
local function registrar(m)
	if not (m:IsA("Model") and m:GetAttribute("FormaRegional") and m:GetAttribute("DonoUserId") and not m:GetAttribute("GuardiaoNinho")) then return end
	if not m.PrimaryPart then return end
	local _, pp = prepararAssento(m)
	if not pp:GetAttribute("Ligado") then
		pp:SetAttribute("Ligado", true)
		pp.Triggered:Connect(function(plr) task.spawn(montar, plr, m) end)
	end
end
local function observar(m)
	if not (m:IsA("Model") and m:GetAttribute("FormaRegional")) then return end
	registrar(m)
	m:GetAttributeChangedSignal("DonoUserId"):Connect(function() registrar(m) end)   -- posse pode chegar depois (salvamento)
end
for _, m in ipairs(workspace:GetChildren()) do observar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(observar, m) end)

-- depuracao (somente servidor)
local dbg = game:GetService("ServerStorage"):FindFirstChild("Montaria_Debug") or Instance.new("BindableFunction")
dbg.Name = "Montaria_Debug"; dbg.Parent = game:GetService("ServerStorage")
dbg.OnInvoke = function(cmd, plr, a)
	if cmd == "montar" then return podeMontar(plr, a) end
	local M = plr and cavaleiros[plr]
	if cmd == "info" then
		if not M then return "sem montaria" end
		return ("modo=%s vel=%.1f vy=%.1f roll=%.0f psi=%.0f planar=%s pos=%s"):format(M.modo, M.vel, M.vy, math.deg(M.roll), math.deg(M.L.psi), tostring(M.planar), tostring(M.m:GetPivot().Position))
	end
	if cmd == "entrada" and M then M.ent = a; M.ultEnt = os.clock() + 9999; return "ok" end   -- teste: entrada fixa
	if cmd == "soltarEntrada" and M then M.ultEnt = 0; return "ok" end
	if cmd == "estado" and M then
		local e = entrada(M)
		return ("f=%s cp=%s cy=%s gama=%.1f yawRate=%.1f teto=%s parede=%s minY=%s y=%.1f"):format(tostring(e.f), tostring(e.cp), tostring(e.cy),
			math.deg(M.gama or 0), math.deg(M.yawRate or 0), tostring(M.teto), tostring(M.parede), tostring(M.minY and math.floor(M.minY)), M.m:GetPivot().Position.Y)
	end
	if cmd == "simularDesconexao" and M then soltar(M, "desconexao"); return "ok" end         -- mesmo caminho do PlayerRemoving
	if cmd == "acao" and M then
		if a == "desmontar" then desmontar(M) elseif a == "decolar" then decolar(M) elseif a == "pousar" then pousar(M) elseif a == "planar" then M.planar = not M.planar
		elseif a == "mordida" then iniciarMordida(M) end
		return M.modo
	end
end

-- montarias SOLTAS (nunca montadas desde o inicio do servidor): nenhum clipe tocava, o dragao ficava na pose de
-- repouso e a camada MovimentoVivo do cliente acumulava giros na cabeca (usuario 31/10: "mexe a cabeca igual louco
-- quando parado"). Toca o Idle como depois de desmontar. Guardioes de ninho sao da IA (IA_Dragao_Servidor).
local function idleSolta(m)
	if not m:IsA("Model") or not m:GetAttribute("FormaRegional") or m:GetAttribute("GuardiaoNinho") then return end
	if montarias[m] or m:GetAttribute("Controlador") or not m:FindFirstChildOfClass("AnimationController") then return end   -- o Animator so nasce no EstadosDragao.novo
	local E = estados[m] or EstadosDragao.novo(m); estados[m] = E
	E:Mudar("Idle")
end
for _, m in ipairs(workspace:GetChildren()) do task.spawn(idleSolta, m) end
workspace.ChildAdded:Connect(function(m) task.defer(idleSolta, m) end)

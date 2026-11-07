-- AnimCavaleiro (ModuleScript, ReplicatedStorage.Montaria_Dragoes) — animacao do CAVALEIRO (R15) ao montar no dragao (06/11,
-- pedido do usuario: "faca a animacao de uma pessoa montando"). Substitui o deslize em arco do Montaria_Dragao_Servidor:
-- o jogador agacha ao lado do flanco, salta esticando os bracos, agarra a sela e se puxa, passa a perna por cima do dorso e
-- senta; depois fica numa pose de montado (pernas abertas sobre o dorso) em loop, no lugar do Sit padrao (pernas juntas).
-- As poses sao montadas aqui como KeyframeSequence (sem asset). KeyframeSequence so toca no Studio; no jogo publicado a
-- trajetoria continua e a pose fica a do Sit ate os clipes serem publicados como Animation (mesmo caso dos dragoes).
-- Convencao R15 (Transform do Motor6D, graus): quadril/ombro +X = membro para a frente; joelho -X = dobra;
-- tornozelo -X = ponta do pe para baixo; tronco/cabeca -X = inclina para a frente; Z = abre para o lado (direita +, esquerda -).
local M = {}
local KSP = game:GetService("KeyframeSequenceProvider")
local RunService = game:GetService("RunService")
local DUR = 1.45                                                  -- duracao da subida (s)
M.DUR = DUR
local ARVORE = {HumanoidRootPart = {LowerTorso = {UpperTorso = {Head = {}, LeftUpperArm = {LeftLowerArm = {LeftHand = {}}},
	RightUpperArm = {RightLowerArm = {RightHand = {}}}}, LeftUpperLeg = {LeftLowerLeg = {LeftFoot = {}}},
	RightUpperLeg = {RightLowerLeg = {RightFoot = {}}}}}}
local function simetrico(t)                                       -- "UpperArm" = {x, z} vale para os dois lados (z espelhado)
	local r = {}
	for k, v in pairs(t) do
		if k:sub(1, 4) == "Left" or k:sub(1, 5) == "Right" or k == "LowerTorso" or k == "UpperTorso" or k == "Head" then r[k] = v
		else r["Right" .. k] = {v[1], v[2] or 0, v[3] or 0}; r["Left" .. k] = {v[1], -(v[2] or 0), -(v[3] or 0)} end
	end
	return r
end
-- {x, z, y} em graus por articulacao; LowerTorso pode ter p = deslocamento (studs)
local SENTADO = simetrico({LowerTorso = {0}, UpperTorso = {-10}, Head = {4}, UpperArm = {50, -6}, LowerArm = {38}, Hand = {-10},
	UpperLeg = {72, 40}, LowerLeg = {-78}, Foot = {14}})
local KF = {
	{0.00, {}},
	{0.30, simetrico({LowerTorso = {-15, p = Vector3.new(0, -0.6, 0)}, UpperTorso = {-18}, Head = {18}, UpperArm = {-35, 8}, LowerArm = {22},
		UpperLeg = {62}, LowerLeg = {-95}, Foot = {35}})},                                    -- agacha olhando a sela
	{0.55, simetrico({LowerTorso = {4, p = Vector3.new(0, 0.3, 0)}, UpperTorso = {6}, Head = {22}, UpperArm = {165, 10}, LowerArm = {8},
		UpperLeg = {12}, LowerLeg = {-22}, Foot = {-28}})},                                    -- salta esticando os bracos
	{0.85, simetrico({LowerTorso = {-10}, UpperTorso = {-26}, Head = {10}, UpperArm = {100, 4}, LowerArm = {78}, Hand = {-15},
		RightUpperLeg = {88, 36}, RightLowerLeg = {-72}, RightFoot = {10}, LeftUpperLeg = {22, -6}, LeftLowerLeg = {-42}, LeftFoot = {-22}})},  -- puxa, perna direita sobe
	{1.15, simetrico({LowerTorso = {-20}, UpperTorso = {-26}, Head = {6}, UpperArm = {70, -4}, LowerArm = {52},
		RightUpperLeg = {70, 56}, RightLowerLeg = {-58}, RightFoot = {12}, LeftUpperLeg = {52, -26}, LeftLowerLeg = {-72}, LeftFoot = {6}})},  -- passa a perna
	{DUR, SENTADO},                                                                            -- senta
}
local function cfDe(v)
	if not v then return CFrame.identity end
	return CFrame.new(v.p or Vector3.zero) * CFrame.Angles(math.rad(v[1] or 0), math.rad(v[3] or 0), math.rad(v[2] or 0))
end
local function poseArvore(no, nome, angs)
	local p = Instance.new("Pose"); p.Name = nome; p.CFrame = cfDe(angs[nome]); p.Weight = 1
	p.EasingStyle = Enum.PoseEasingStyle.Cubic; p.EasingDirection = Enum.PoseEasingDirection.InOut
	for filho, sub in pairs(no) do poseArvore(sub, filho, angs).Parent = p end
	return p
end
local function sequencia(nome, chaves, loop)
	local ks = Instance.new("KeyframeSequence"); ks.Name = nome; ks.Loop = loop or false
	ks.Priority = Enum.AnimationPriority.Action4
	for _, c in ipairs(chaves) do
		local k = Instance.new("Keyframe"); k.Time = c[1]
		poseArvore(ARVORE.HumanoidRootPart, "HumanoidRootPart", c[2]).Parent = k
		k.Parent = ks
	end
	return ks
end
local cache = {}
local function animacao(nome)
	if cache[nome] ~= nil then return cache[nome] or nil end
	local ok, id = pcall(function()
		local ks
		if nome == "Montar" then ks = sequencia("Cavaleiro_Montar", KF)
		else                                                       -- montado: respiracao leve, sem mexer as pernas
			local resp = table.clone(SENTADO); resp.UpperTorso = {-12}; resp.Head = {6}
			ks = sequencia("Cavaleiro_Montado", {{0, SENTADO}, {1.3, resp}, {2.6, SENTADO}}, true)
		end
		return KSP:RegisterKeyframeSequence(ks)
	end)
	if not ok then warn("AnimCavaleiro: KeyframeSequence indisponivel (" .. tostring(id) .. ")"); cache[nome] = false; return nil end
	local a = Instance.new("Animation"); a.AnimationId = id; cache[nome] = a; return a
end
local function tocar(hum, nome)
	local an = hum and hum:FindFirstChildOfClass("Animator"); local a = animacao(nome)
	if not (an and a) then return nil end
	local ok, t = pcall(function() return an:LoadAnimation(a) end)
	if not ok then return nil end
	t.Priority = Enum.AnimationPriority.Action4; t:Play(0.15); return t
end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function suave(k) return k * k * (3 - 2 * k) end
-- sobe do lugar atual (hrp.CFrame) ate a sela (CFrame final do HRP), pulando pelo lado em que o jogador esta
-- (v3, 06/11: a entrada da FRENTE usa este pulo; a direcao e a do jogador ate a sela, nao mais so as laterais)
function M.subir(hrp, hum, sela)
	local de = hrp.CFrame
	local dir = plano(de.Position - sela.Position); if dir.Magnitude < 0.1 then dir = -sela.LookVector end
	local side = dir.Unit; local up = Vector3.yAxis
	local flanco = sela.Position + side * 2.4 + up * 0.4                                    -- ao lado da sela, maos nas alcas
	local P = {de.Position, de.Position, de.Position:Lerp(flanco, 0.55) + up * 1.2, flanco, sela.Position + side * 1.0 + up * 0.9, sela.Position}
	local olhar = plano(-side).Magnitude > 0.01 and CFrame.lookAt(Vector3.zero, plano(-side)) or de.Rotation   -- de frente para o dragao
	local R = {de.Rotation, olhar, olhar, olhar, olhar:Lerp(sela.Rotation, 0.6), sela.Rotation}   -- vira para o dragao ao agachar
	local T = {}; for i, c in ipairs(KF) do T[i] = c[1] end
	local trilha = tocar(hum, "Montar")
	local t0 = os.clock()
	while true do
		local t = os.clock() - t0; if t >= DUR then break end
		local i = 1; while i < #T - 1 and t > T[i + 1] do i += 1 end
		local k = suave(math.clamp((t - T[i]) / (T[i + 1] - T[i]), 0, 1))
		hrp.CFrame = CFrame.new(P[i]:Lerp(P[i + 1], k)) * R[i]:Lerp(R[i + 1], k)
		RunService.Heartbeat:Wait()
	end
	hrp.CFrame = sela
	if trilha then task.delay(0.2, function() trilha:Stop(0.25) end) end
	return tocar(hum, "Montado")                                                           -- devolve a trilha da pose montada
end

-- ===== v2 (06/11, usuario: "para o jogador montar, a animacao deve abrir a asa ao montar (como uma rampa)") =========
-- O dragao abre a asa do lado do cavaleiro ate o chao (clipes *_Rampa_E/D); o cavaleiro anda ate a ponta da asa, sobe
-- pela borda dela (punho -> cotovelo -> ombro) e, no ombro, passa a perna e senta.
local VEL_RAMPA = 11                                                                       -- studs/s andando na asa
local ANDAR = {                                                                            -- passada subindo (0,8 s, laco)
	{0.0, simetrico({LowerTorso = {-8}, UpperTorso = {-14}, Head = {10}, RightUpperArm = {-28}, LeftUpperArm = {28}, LowerArm = {20},
		RightUpperLeg = {34}, RightLowerLeg = {-14}, LeftUpperLeg = {-18}, LeftLowerLeg = {-30}, Foot = {6}})},
	{0.2, simetrico({LowerTorso = {-8, p = Vector3.new(0, 0.15, 0)}, UpperTorso = {-14}, Head = {10}, UpperArm = {0}, LowerArm = {24},
		RightUpperLeg = {8}, RightLowerLeg = {-20}, LeftUpperLeg = {40}, LeftLowerLeg = {-70}, Foot = {10}})},
	{0.4, simetrico({LowerTorso = {-8}, UpperTorso = {-14}, Head = {10}, RightUpperArm = {28}, LeftUpperArm = {-28}, LowerArm = {20},
		RightUpperLeg = {-18}, RightLowerLeg = {-30}, LeftUpperLeg = {34}, LeftLowerLeg = {-14}, Foot = {6}})},
	{0.6, simetrico({LowerTorso = {-8, p = Vector3.new(0, 0.15, 0)}, UpperTorso = {-14}, Head = {10}, UpperArm = {0}, LowerArm = {24},
		RightUpperLeg = {40}, RightLowerLeg = {-70}, LeftUpperLeg = {8}, LeftLowerLeg = {-20}, Foot = {10}})},
	{0.8, nil},
}
ANDAR[5][2] = ANDAR[1][2]
M.ANDAR = ANDAR
local SENTAR = {                                                                           -- do ombro para a sela (0,8 s)
	{0.0, simetrico({LowerTorso = {-8}, UpperTorso = {-14}, Head = {10}, UpperArm = {30}, LowerArm = {30}, UpperLeg = {10}, LowerLeg = {-20}})},
	{0.35, simetrico({LowerTorso = {-20}, UpperTorso = {-26}, Head = {6}, UpperArm = {70, -4}, LowerArm = {52},
		RightUpperLeg = {70, 56}, RightLowerLeg = {-58}, RightFoot = {12}, LeftUpperLeg = {52, -26}, LeftLowerLeg = {-72}, LeftFoot = {6}})},
	{0.8, SENTADO},
}
M.SENTAR = SENTAR
local function animV2(nome)
	if cache[nome] ~= nil then return cache[nome] or nil end
	local ok, id = pcall(function()
		local ks = nome == "Andar" and sequencia("Cavaleiro_Andar_Rampa", ANDAR, true) or sequencia("Cavaleiro_Sentar", SENTAR)
		return KSP:RegisterKeyframeSequence(ks)
	end)
	if not ok then cache[nome] = false; return nil end
	local a = Instance.new("Animation"); a.AnimationId = id; cache[nome] = a; return a
end
local function tocarV2(hum, nome)
	local an = hum and hum:FindFirstChildOfClass("Animator"); local a = animV2(nome)
	if not (an and a) then return nil end
	local ok, t = pcall(function() return an:LoadAnimation(a) end)
	if not ok then return nil end
	t.Priority = Enum.AnimationPriority.Action4; t:Play(0.15); return t
end
-- ===== v3 (06/11, usuario: "Prefiro a animacao de pulo. E por tras pulando pela cauda. Deve ser disponivel montar
-- somente por tras e na frente das asas"): a rampa saiu do servidor. Entrada TRAS: pula na cauda deitada (o dragao esta
-- no Abaixado), corre por ela ate o quadril e senta na sela por tras. pos(nomeOsso) devolve a posicao ANIMADA do osso.
function M.caminhoCauda(pos)
	local up = Vector3.yAxis * 3.0; local out = {}
	for _, n in ipairs({"tail_5", "tail_4", "Cauda3", "tail_2", "Quadril"}) do
		local p = pos(n); if not p then return nil end
		table.insert(out, p + up)
	end
	return out
end
local PULO = {KF[1], KF[2], KF[3], {0.75, ANDAR[1][2]}}                                    -- agacha, salta, cai andando
local function animPulo()
	if cache.Pulo ~= nil then return cache.Pulo or nil end
	local ok, id = pcall(function() return KSP:RegisterKeyframeSequence(sequencia("Cavaleiro_Pular", PULO)) end)
	if not ok then cache.Pulo = false; return nil end
	local a = Instance.new("Animation"); a.AnimationId = id; cache.Pulo = a; return a
end
function M.subirCauda(hrp, hum, sela, pts)
	local up = Vector3.yAxis
	local alvo = pts[1]
	local chaoAlvo = Vector3.new(alvo.X, hrp.Position.Y, alvo.Z)
	local ate = plano(chaoAlvo - hrp.Position)
	if ate.Magnitude > 4.5 then                                                            -- longe: anda pelo chao ate perto da cauda
		local a0 = hrp.Position; local b0 = chaoAlvo - ate.Unit * 3.5; local d0 = (b0 - a0).Magnitude / VEL_RAMPA
		local rot0 = CFrame.lookAt(Vector3.zero, ate.Unit); local andar0 = tocarV2(hum, "Andar"); local t1 = os.clock()
		while os.clock() - t1 < d0 do
			local k = (os.clock() - t1) / d0; hrp.CFrame = CFrame.new(a0:Lerp(b0, k)) * hrp.CFrame.Rotation:Lerp(rot0, math.min(1, k * 4))
			RunService.Heartbeat:Wait()
		end
		if andar0 then andar0:Stop(0.15) end
	end
	local an = hum and hum:FindFirstChildOfClass("Animator"); local ap = animPulo(); local pulo
	if an and ap then local ok, t = pcall(function() return an:LoadAnimation(ap) end); if ok then pulo = t; t.Priority = Enum.AnimationPriority.Action4; t:Play(0.15) end end
	local de = hrp.CFrame
	local olhar = plano(alvo - de.Position).Magnitude > 0.05 and CFrame.lookAt(Vector3.zero, plano(alvo - de.Position)) or de.Rotation
	local t0 = os.clock()
	while os.clock() - t0 < 0.75 do                                                        -- agacha (0-0,30) e salta na cauda
		local t = os.clock() - t0
		if t < 0.30 then hrp.CFrame = CFrame.new(de.Position) * de.Rotation:Lerp(olhar, suave(t / 0.30))
		else local k = suave(math.min(1, (t - 0.30) / 0.40)); hrp.CFrame = CFrame.new(de.Position:Lerp(alvo, k) + up * math.sin(math.pi * k) * 2.2) * olhar end
		RunService.Heartbeat:Wait()
	end
	if pulo then pulo:Stop(0.2) end
	local P = {alvo}; for i = 2, #pts do table.insert(P, pts[i]) end
	local fwd = plano(sela.LookVector).Unit
	table.insert(P, sela.Position - fwd * 1.2 + up * 0.9)                                  -- atras da sela
	local andar = tocarV2(hum, "Andar")
	for i = 1, #P - 2 do                                                                   -- corre pela cauda ate o quadril
		local a, b = P[i], P[i + 1]; local d = (b - a).Magnitude; local dur = math.max(0.15, d / VEL_RAMPA)
		local dirP = plano(b - a); local rot = dirP.Magnitude > 0.05 and CFrame.lookAt(Vector3.zero, dirP) or hrp.CFrame.Rotation
		local t0 = os.clock()
		while os.clock() - t0 < dur do
			local k = (os.clock() - t0) / dur
			hrp.CFrame = CFrame.new(a:Lerp(b, k)) * hrp.CFrame.Rotation:Lerp(rot, math.min(1, k * 4))
			RunService.Heartbeat:Wait()
		end
	end
	if andar then andar:Stop(0.2) end
	local sentar = tocarV2(hum, "Sentar")                                                  -- passa a perna e senta
	local de, meio = CFrame.new(P[#P - 1]) * hrp.CFrame.Rotation, CFrame.new(P[#P]) * hrp.CFrame.Rotation:Lerp(sela.Rotation, 0.6)
	local t0 = os.clock()
	while os.clock() - t0 < 0.8 do
		local k = (os.clock() - t0) / 0.8
		hrp.CFrame = (k < 0.45 and de:Lerp(meio, suave(k / 0.45)) or meio:Lerp(sela, suave((k - 0.45) / 0.55)))
		RunService.Heartbeat:Wait()
	end
	hrp.CFrame = sela
	if sentar then task.delay(0.15, function() sentar:Stop(0.25) end) end
	return tocar(hum, "Montado")
end
return M

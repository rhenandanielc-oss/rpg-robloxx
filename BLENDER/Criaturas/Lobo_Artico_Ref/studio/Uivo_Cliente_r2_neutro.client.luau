-- Uivo_Cliente (Script com RunContext = Client, Workspace.Teste_LoboArtico) - Uivo do Lobo Artico, E3 (visual + som NEUTROS).
-- Aprovado pelo usuario 16/11/2026 ("Aprovar e ir a E3"). So cosmetico: le os atributos que o servidor (Uivo_Servidor) grava
-- e nunca decide nada. Neutro = sem cor de elemento (o elemento do Artico esta PENDENTE): branco/cinza frio, sem gelo/raio/fogo.
--  * Som: uivo unico (Pro Sound Effects, biblioteca do Roblox) saindo da ponta da Cabeca; comeca no fim do Uivar (inicio da
--    nota longa) e some ao cortar a fase.
--  * Respiracao visivel: nevoa branca curta saindo da boca durante a nota longa (Uivando 0-3,67 s) - vapor de ar frio.
--  * Pulso da Marca: luz branca suave no ombro E enquanto o efeito do Uivo estiver ativo (UivoAtivoFim), apaga no fim.
-- Pontos medidos no Edit (repouso, 16/11): boca = Cabeca + (0, 1.66, -0.31); nariz = Cabeca + (0, 1.565, 0);
-- marca = Escapula_E + (-0.57, 0.72, 0.13).
-- r2 (16/11, apos captura da r1): nevoa virou bola grande acima da cabeca e a luz (alcance 7, brilho 1,4) estourava o
-- pelo do corpo todo -> nevoa fina (0,12->0,75, mais transparente, vida 0,55-0,9 s) e luz so no ombro (alcance 3,5, brilho 0,7).
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
-- (o Uivo_Servidor deixa o lobo Persistent; o laco abaixo cobre o atraso ate o modelo chegar)
local function osso(n) return lobo:FindFirstChild(n, true) end
-- com StreamingEnabled o modelo pode chegar depois do script: espera os ossos (sem limite; checa 4x por segundo)
local cab, esc = osso("Cabeca"), osso("Escapula_E")
while not (cab and esc) do task.wait(0.25); cab, esc = osso("Cabeca"), osso("Escapula_E") end

local SOM_ID = "rbxassetid://9120790529"     -- "Wolf Howl Two Versions 1 (SFX)" - Pro Sound Effects (3,5 s)

-- pontos (Bone filho so no cliente; sem peso, nao deforma a malha)
local function ponto(pai, nome, pos)
	local b = pai:FindFirstChild(nome) or Instance.new("Bone")
	b.Name = nome; b.CFrame = CFrame.new(pos); b.Parent = pai
	return b
end
local pBoca = ponto(cab, "FX_Boca", Vector3.new(0, 1.66, -0.31))
local pNariz = ponto(cab, "FX_Nariz", Vector3.new(0, 1.565, 0))
local pMarca = ponto(esc, "FX_Marca", Vector3.new(-0.57, 0.72, 0.13))

local som = pNariz:FindFirstChild("Som_Uivo") or Instance.new("Sound")
som.Name = "Som_Uivo"; som.SoundId = SOM_ID; som.Volume = 0.8
som.RollOffMode = Enum.RollOffMode.InverseTapered; som.RollOffMinDistance = 12; som.RollOffMaxDistance = 220
som.Parent = pNariz

local nevoa = pBoca:FindFirstChild("Nevoa_Uivo") or Instance.new("ParticleEmitter")
nevoa.Name = "Nevoa_Uivo"
nevoa.Texture = "rbxasset://textures/particles/smoke_main.dds"
nevoa.Color = ColorSequence.new(Color3.fromRGB(235, 240, 245))
nevoa.LightEmission = 0; nevoa.LightInfluence = 1
nevoa.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.12), NumberSequenceKeypoint.new(1, 0.75)})
nevoa.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.72), NumberSequenceKeypoint.new(0.4, 0.85), NumberSequenceKeypoint.new(1, 1)})
nevoa.Lifetime = NumberRange.new(0.55, 0.9); nevoa.Rate = 0
nevoa.Speed = NumberRange.new(3, 4.2); nevoa.SpreadAngle = Vector2.new(8, 8)
nevoa.Drag = 1.6; nevoa.Acceleration = Vector3.new(0, 0.3, 0)
nevoa.Rotation = NumberRange.new(0, 360); nevoa.RotSpeed = NumberRange.new(-30, 30)
nevoa.EmissionDirection = Enum.NormalId.Top     -- +Y do osso da Cabeca = para o nariz
nevoa.Parent = pBoca

local luz = pMarca:FindFirstChild("Luz_Marca") or Instance.new("PointLight")
luz.Name = "Luz_Marca"; luz.Color = Color3.fromRGB(240, 244, 255); luz.Range = 3.5; luz.Brightness = 0; luz.Shadows = false
luz.Parent = pMarca

local function agora() return workspace:GetServerTimeNow() end
local faseAtual = ""
local fadeSom
local function pararSom(t)
	if not som.IsPlaying then return end
	if fadeSom then fadeSom:Cancel() end
	fadeSom = TweenService:Create(som, TweenInfo.new(t), {Volume = 0}); fadeSom:Play()
	fadeSom.Completed:Once(function(st) if st == Enum.PlaybackState.Completed then som:Stop(); som.Volume = 0.8 end end)
end

local function aoMudarFase()
	local f = lobo:GetAttribute("UivoFase") or ""
	if f == faseAtual then return end
	faseAtual = f
	if f == "Uivando" then
		-- comeca no ponto da fase em que o cliente esta (atraso de rede)
		local atraso = math.clamp(agora() - (lobo:GetAttribute("UivoFaseT") or agora()), 0, 1)
		if fadeSom then fadeSom:Cancel() end
		som.Volume = 0.8; som.TimePosition = atraso; som:Play()
		nevoa.Rate = 22
		task.delay(math.max(0, 3.2 - atraso), function() if faseAtual == "Uivando" then nevoa.Rate = 6 end end)
	elseif f == "PararUivar" then
		nevoa.Rate = 0; pararSom(0.5)
	else                                  -- "" (fim normal ou interrompido) ou "Uivar"
		nevoa.Rate = 0
		if f == "" then pararSom(0.25) end
	end
end
lobo:GetAttributeChangedSignal("UivoFase"):Connect(aoMudarFase)
aoMudarFase()

-- pulso da Marca enquanto o efeito estiver ativo (1 batida por segundo, fade nos ultimos 0,8 s)
RunService.RenderStepped:Connect(function()
	local fim = lobo:GetAttribute("UivoAtivoFim") or 0
	local resta = fim - agora()
	if resta <= 0 or (lobo:GetAttribute("MultVelocidade") or 1) <= 1 then
		if luz.Brightness ~= 0 then luz.Brightness = 0 end
		return
	end
	local pulso = 0.55 + 0.45 * math.sin(agora() * math.pi * 2)       -- 1 Hz
	local env = math.clamp(resta / 0.8, 0, 1) * math.clamp((6 - resta) / 0.3, 0, 1)
	luz.Brightness = 0.7 * pulso * env
end)

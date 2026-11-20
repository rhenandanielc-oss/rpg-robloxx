-- MontariaCrocodilo_Cliente (LocalScript em StarterPlayer.StarterPlayerScripts do place de TESTE Crocodilo-testes) - 20/11
-- 1a entrega da montaria (usuario: botao Montar [E], controle pela direcao da camera, Shift corre, nada na superficie).
-- So VISUAL e INTENCAO: (1) a sela (Model separado, soldada ao corpo) tem os PROPRIOS ossos com os mesmos nomes do
-- crocodilo; a cada quadro cada osso da sela copia o osso animado do crocodilo (mesmo metodo da sela do Urso: ossos de
-- mesmo nome no MESMO Model fariam a pele do crocodilo usar os da sela). (2) Se o jogador local e o cavaleiro, manda ao
-- servidor a direcao pedida (Humanoid.MoveDirection, ja relativa a camera) e se quer correr, ~15 Hz; E/botao = descer.
-- O servidor decide tudo (velocidade, giro, chao, agua, montar/descer). Celular: botoes Correr (alterna) e Descer.
local Players = game:GetService("Players"); local RS = game:GetService("RunService"); local UIS = game:GetService("UserInputService")
local lp = Players.LocalPlayer
local lab = workspace:WaitForChild("Teste_Crocodilo")
local croc = lab:WaitForChild("Crocodilo_Primordial")
local pasta = game:GetService("ReplicatedStorage"):WaitForChild("Crocodilo_Montaria", 30)
local Cmd, Ent = pasta and pasta:WaitForChild("Comando", 10), pasta and pasta:WaitForChild("Entrada", 10)

-- (1) sela segue os ossos do crocodilo ------------------------------------------------------------------------------
local selaM = lab:WaitForChild("Crocodilo_Sela", 30)
local sela = selaM and selaM:FindFirstChildWhichIsA("MeshPart")
local par = {}
-- os ossos podem chegar ao cliente DEPOIS do script comecar: monta os pares (e acha a Coluna2) ate encontrar
local coluna2
local function montarPares()
	if #par > 0 and coluna2 then return true end
	local oc = {}
	for _, d in ipairs(croc:GetDescendants()) do if d:IsA("Bone") then oc[d.Name] = d end end
	coluna2 = oc.Coluna2
	if sela and #par == 0 then
		local function coletar(inst) for _, c in ipairs(inst:GetChildren()) do if c:IsA("Bone") then
			local u = oc[c.Name]; if u then table.insert(par, {b = c, u = u, rel = u.WorldCFrame:Inverse() * c.WorldCFrame}) end
			coletar(c) end end end
		coletar(sela)                                               -- ordem: pai antes do filho
	end
	return #par > 0 and coluna2 ~= nil
end
local tentar = 0
RS:BindToRenderStep("SelaCrocodilo", Enum.RenderPriority.Last.Value + 1, function(dt)
	if #par == 0 or not coluna2 then tentar += dt; if tentar < 0.5 then return end; tentar = 0; montarPares() end
	for _, p in ipairs(par) do
		local desejado = p.u.TransformedWorldCFrame * p.rel
		local pai = p.b.Parent:IsA("Bone") and p.b.Parent.TransformedWorldCFrame or p.b.Parent.CFrame
		p.b.Transform = (pai * p.b.CFrame):Inverse() * desejado
	end
end)

-- (1b) r2 20/11 "igual ao Blender": pose do cavaleiro (TODOS os clientes, para quem estiver montando/montado) ---------------
-- CavaleiroCrocodilo traz, por quadro, a rotacao delta de cada parte R15 (eixos do crocodilo). Depois do Animator, cada
-- Motor6D recebe Transform = C0^-1 * Pai^-1 * Filho * C1 (so rotacao) para as partes ficarem como no Blender. Montado
-- ("Sentado"), o LowerTorso segue a Coluna2 do crocodilo (o Root ganha o desvio da coluna), como o cavaleiro no Blender.
local CAV = game:GetService("ReplicatedStorage"):WaitForChild("CavaleiroCrocodilo", 30)
CAV = CAV and require(CAV)
local function quat(arr, k) return CFrame.new(0, 0, 0, arr[4 * k + 1], arr[4 * k + 2], arr[4 * k + 3], arr[4 * k + 4]) end
local function rotParte(a, parte, t)
	local r = a.r[parte]; if not r then return nil end
	local x = math.clamp(t * CAV.fps, 0, a.n - 1); local i = math.floor(x); local j = math.min(i + 1, a.n - 1)
	return quat(r, i):Lerp(quat(r, j), x - i)
end
local function ltLocal(a, t)
	local x = math.clamp(t * CAV.fps, 0, a.n - 1); local i = math.floor(x); local j = math.min(i + 1, a.n - 1); local u = x - i
	local function p(k) return Vector3.new(a.lt[3 * k + 1], a.lt[3 * k + 2], a.lt[3 * k + 3]) end
	return CFrame.new(p(i):Lerp(p(j), u)) * rotParte(a, "LowerTorso", t)
end
local juntas = {}                                                   -- [character] = lista {parte, motor} (pai antes do filho)
local ORDEM = {"LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm", "RightLowerArm", "RightHand",
	"LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg", "RightFoot"}
local function juntasDe(ch)
	if juntas[ch] then return juntas[ch] end
	local l = {}
	for _, nm in ipairs(ORDEM) do
		local part = ch:FindFirstChild(nm)
		if part then for _, m in ipairs(part:GetChildren()) do
			-- avatar classico = Motor6D (Part0/Part1, C0/C1); avatar novo = AnimationConstraint (Attachment0/Attachment1)
			if m:IsA("Motor6D") and m.Part1 == part then table.insert(l, {nm, m, m.Part0, m.C0, m.C1}); break end
			if m.ClassName == "AnimationConstraint" and m.Attachment1 and m.Attachment1.Parent == part and m.Attachment0 then
				table.insert(l, {nm, m, m.Attachment0.Parent, m.Attachment0.CFrame, m.Attachment1.CFrame}); break end
		end end
	end
	juntas[ch] = l; ch.AncestryChanged:Connect(function() if not ch.Parent then juntas[ch] = nil end end)
	return l
end
-- a pose animada da Coluna2 so esta atualizada na renderizacao (no PreSimulation ainda vale o repouso): guarda o desvio
-- (animada x repouso, em coordenadas do crocodilo) aqui e usa no proximo quadro (1 quadro de atraso, imperceptivel)
local colunaDesvioLocal
RS.RenderStepped:Connect(function()
	if coluna2 then local piv = croc:GetPivot(); colunaDesvioLocal = piv:Inverse() * (coluna2.TransformedWorldCFrame * coluna2.WorldCFrame:Inverse()) * piv end
end)
local colunaDesvio
-- PreSimulation: DEPOIS das animacoes do avatar (Animate/Animator) e antes da fisica; no RenderStepped o Animator sobrescrevia
RS.PreSimulation:Connect(function()
	if not CAV then return end
	local uid = croc:GetAttribute("CavaleiroUserId"); local acao = croc:GetAttribute("CavAcao")
	if not uid or not acao or not CAV.acoes[acao] then return end
	local pl = Players:GetPlayerByUserId(uid); local ch = pl and pl.Character
	local hrp = ch and ch:FindFirstChild("HumanoidRootPart"); if not hrp or not ch:FindFirstChild("LowerTorso") then return end
	local a = CAV.acoes[acao]
	local t = (acao == "Sentado") and 0 or (workspace:GetServerTimeNow() - (croc:GetAttribute("CavT0") or 0))
	local piv = croc:GetPivot(); local R = piv - piv.Position
	colunaDesvio = colunaDesvioLocal and (piv * colunaDesvioLocal * piv:Inverse()) or nil
	local desvio = CFrame.identity                                  -- montado: desvio da Coluna2 (animada x repouso)
	if acao == "Sentado" and colunaDesvio then desvio = colunaDesvio end
	local mundo = {}                                                -- rotacao desejada de cada parte no mundo
	for _, nm in ipairs(ORDEM) do local q = rotParte(a, nm, t); if q then mundo[nm] = (desvio - desvio.Position) * R * q end end
	mundo.HumanoidRootPart = hrp.CFrame - hrp.CFrame.Position
	for _, jm in ipairs(juntasDe(ch)) do
		local nm, m, part0, C0, C1 = jm[1], jm[2], jm[3], jm[4], jm[5]
		local filho = mundo[nm]
		if filho then
			if nm == "LowerTorso" then
				if acao == "Sentado" then                               -- o quadril segue a coluna (posicao + rotacao)
					-- sentado, o Humanoid zera o Root a cada quadro: o cavaleiro inteiro segue a coluna pela SOLDA do assento
					-- (so neste cliente, visual; o servidor continua dono da regra)
					local lt = desvio * (piv * ltLocal(a, 0))
					local seat = croc:FindFirstChild("Assento_Sela"); local w = seat and seat:FindFirstChild("SeatWeld")
					if w and w.Part1 == hrp then w.C0 = seat.CFrame:Inverse() * (lt * C1 * C0:Inverse()); w.C1 = CFrame.identity end
					m.Transform = CFrame.identity
				else
					local paiR = mundo.HumanoidRootPart
					m.Transform = (C0 - C0.Position):Inverse() * paiR:Inverse() * filho * (C1 - C1.Position)
				end
			else
				local pai = part0 and mundo[part0.Name]
				if pai then m.Transform = (C0 - C0.Position):Inverse() * pai:Inverse() * filho * (C1 - C1.Position) end
			end
		end
	end
end)

-- (2) cavaleiro: intencao -> servidor -------------------------------------------------------------------------------
local CELULAR = UIS.TouchEnabled and not UIS.KeyboardEnabled
local correrToque = false
local gui
local function souCavaleiro() return croc:GetAttribute("CavaleiroUserId") == lp.UserId end
local function montado() return souCavaleiro() and croc:GetAttribute("FaseMontaria") == "montado" end
local function hud(on)
	if on and not gui then
		gui = Instance.new("ScreenGui"); gui.Name = "HUD_MontariaCrocodilo"; gui.ResetOnSpawn = false
		local dica = Instance.new("TextLabel"); dica.Name = "Dica"; dica.Size = UDim2.new(0, 420, 0, 28); dica.Position = UDim2.new(0.5, -210, 1, -96)
		dica.BackgroundTransparency = 0.45; dica.BackgroundColor3 = Color3.new(0, 0, 0); dica.TextColor3 = Color3.new(1, 1, 1)
		dica.Font = Enum.Font.GothamMedium; dica.TextSize = 16; dica.Text = CELULAR and "Analógico: mover  •  Correr  •  Descer" or "WASD: mover  •  Shift: correr  •  E: descer"
		Instance.new("UICorner", dica).CornerRadius = UDim.new(0, 8); dica.Parent = gui
		if CELULAR then
			local function botao(txt, x, fn)
				local b = Instance.new("TextButton"); b.Size = UDim2.new(0, 96, 0, 56); b.Position = UDim2.new(1, x, 1, -190)
				b.BackgroundColor3 = Color3.fromRGB(30, 40, 34); b.BackgroundTransparency = 0.2; b.TextColor3 = Color3.new(1, 1, 1)
				b.Font = Enum.Font.GothamBold; b.TextSize = 18; b.Text = txt; Instance.new("UICorner", b).CornerRadius = UDim.new(0, 12)
				b.Activated:Connect(function() fn(b) end); b.Parent = gui
			end
			botao("Correr", -220, function(b) correrToque = not correrToque; b.BackgroundColor3 = correrToque and Color3.fromRGB(60, 110, 70) or Color3.fromRGB(30, 40, 34) end)
			botao("Descer", -112, function() if Cmd then Cmd:FireServer("desmontar") end end)
		end
		gui.Parent = lp:WaitForChild("PlayerGui")
	elseif not on and gui then gui:Destroy(); gui = nil; correrToque = false end
end
UIS.InputBegan:Connect(function(io, gp)
	if gp then return end
	if io.KeyCode == Enum.KeyCode.E and souCavaleiro() and Cmd then Cmd:FireServer("desmontar") end
end)
-- direcao pelo teclado relativa a camera (quando o Humanoid sentado nao da MoveDirection, ex.: place sem PlayerModule)
local K = Enum.KeyCode
local function dirTeclado()
	local f = (UIS:IsKeyDown(K.W) and 1 or 0) - (UIS:IsKeyDown(K.S) and 1 or 0)
	local r = (UIS:IsKeyDown(K.D) and 1 or 0) - (UIS:IsKeyDown(K.A) and 1 or 0)
	if f == 0 and r == 0 then return nil end
	local cam = workspace.CurrentCamera.CFrame
	local lk = Vector3.new(cam.LookVector.X, 0, cam.LookVector.Z); local rt = Vector3.new(cam.RightVector.X, 0, cam.RightVector.Z)
	if lk.Magnitude < 0.01 then return nil end
	local v = lk.Unit * f + rt.Unit * r; return v.Magnitude > 0.01 and v.Unit or nil
end
local acc = 0
RS.Heartbeat:Connect(function(dt)
	local on = montado(); hud(on)
	local hum = lp.Character and lp.Character:FindFirstChildOfClass("Humanoid")
	if hum then hum:SetStateEnabled(Enum.HumanoidStateType.Jumping, not souCavaleiro()) end   -- montado: pular nao derruba
	if not on or not Ent then return end
	acc += dt; if acc < 1 / 15 then return end; acc = 0
	local dir = hum and hum.MoveDirection or Vector3.zero
	if dir.Magnitude < 0.1 then dir = dirTeclado() or Vector3.zero end
	local correr = correrToque or UIS:IsKeyDown(Enum.KeyCode.LeftShift) or UIS:IsKeyDown(Enum.KeyCode.RightShift)
	local td = lp:GetAttribute("TESTE_MontariaDir")                    -- SO TESTE (ensaio automatico no Studio): direcao e correr
	if typeof(td) == "Vector3" then dir = td; correr = lp:GetAttribute("TESTE_MontariaCorrer") == true end
	Ent:FireServer(dir, correr)
end)

-- patch_trava_alvo.luau (Studio, Edit) — trava de alvo da montaria (todas as formas) (04/11).
-- Gerado por sombrio/gerar_patch_trava_alvo.py com as MESMAS trocas do src/. Tudo-ou-nada; backup unico
-- ServerStorage.Backup_Trava_Alvo_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local novos = {}
do local s = game.StarterPlayer.StarterPlayerScripts.Montaria_Cliente; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_TRAVA_ALVO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[local m = nil                                                        -- dragao montado
]==], [==[local m = nil                                                        -- dragao montado
local trava, travar, soltarTrava, avisoTrava, travaAtual             -- PATCH_TRAVA_ALVO: definidos no bloco da trava (mais abaixo)
]==])
  src = troca(src, [==[function dirMira()
	local alvo = pontoMira(); local v = alvo - bocaPos()
]==], [==[-- ===== PATCH_TRAVA_ALVO (04/11): ALVO DINAMICO (C / clique do meio / R3) =========================================
-- Trava no jogador/criatura mais perto do cursor (ou do centro da tela sem mouse). Com alvo travado, dirMira aponta
-- da boca ao alvo, e o pedido leva o alvo (o servidor valida). Solta: mesma tecla, alvo morto/sumiu/longe, desmontar.
local TRAVA = {alcance = 320, quebra = 400, raioTela = 0.35, cor = Color3.fromRGB(255, 95, 95)}
trava = nil                                                          -- {alvo, raiz, hl, bb, txt} (declarado no topo)
local function raizAlvo(md) return md and (md:FindFirstChild("HumanoidRootPart") or md.PrimaryPart) end
local function alvoVivo(md)
	if not (md and md.Parent and md:IsDescendantOf(workspace)) then return false end
	local h = md:FindFirstChildOfClass("Humanoid"); if h then return h.Health > 0 end
	return not md:GetAttribute("Incapacitado")
end
avisoTrava = function(txt)
	toast.Text = txt; toast.TextTransparency = 0; toast.TextStrokeTransparency = 0.5
	TweenService:Create(toast, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In, 0, false, 1.2), {TextTransparency = 1, TextStrokeTransparency = 1}):Play()
end
soltarTrava = function()
	if not trava then return end
	if trava.hl then trava.hl:Destroy() end; if trava.bb then trava.bb:Destroy() end
	trava = nil
end
local function candidatosTrava()
	local l, vistos = {}, {}
	local function por(md)
		if vistos[md] or md == m or md == lp.Character or not md:IsA("Model") then return end
		vistos[md] = true
		if md:GetAttribute("DonoUserId") == lp.UserId then return end           -- nunca os proprios dragoes
		if raizAlvo(md) and alvoVivo(md) then table.insert(l, md) end
	end
	for _, d in ipairs(workspace:GetDescendants()) do if d:IsA("Humanoid") and d.Parent then por(d.Parent) end end
	for _, md in ipairs(workspace:GetChildren()) do if md:IsA("Model") and (md:GetAttribute("FormaRegional") or md:GetAttribute("GuardiaoNinho")) then por(md) end end
	return l
end
travar = function()
	local cam = workspace.CurrentCamera; local vp = cam.ViewportSize
	local ml = UIS:GetMouseLocation()                                  -- cursor fora da tela (ou sem mouse): centro da tela
	local foco = (UIS.MouseEnabled and ml.X >= 0 and ml.Y >= 0 and ml.X <= vp.X and ml.Y <= vp.Y) and ml or Vector2.new(vp.X / 2, vp.Y / 2)
	local origem = m and m:GetPivot().Position or cam.CFrame.Position
	local melhor, nota = nil, math.huge
	for _, md in ipairs(candidatosTrava()) do
		local r = raizAlvo(md)
		if (r.Position - origem).Magnitude <= TRAVA.alcance then
			local p, naTela = cam:WorldToViewportPoint(r.Position)
			if naTela and p.Z > 0 then
				local d = (Vector2.new(p.X, p.Y) - foco).Magnitude / math.min(vp.X, vp.Y)
				if d <= TRAVA.raioTela and d < nota then melhor, nota = md, d end
			end
		end
	end
	if not melhor then avisoTrava("Nenhum alvo perto da mira"); return end
	soltarTrava()
	local r = raizAlvo(melhor)
	local hl = Instance.new("Highlight"); hl.Name = "TravaAlvo"; hl.Adornee = melhor; hl.FillTransparency = 1; hl.OutlineColor = TRAVA.cor
	hl.OutlineTransparency = 0.15; hl.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop; hl.Parent = lp.PlayerGui
	local bb = Instance.new("BillboardGui"); bb.Name = "TravaAlvo"; bb.Adornee = r; bb.AlwaysOnTop = true; bb.Size = UDim2.fromOffset(60, 78)
	bb.StudsOffsetWorldSpace = Vector3.new(0, 0, 0); bb.LightInfluence = 0; bb.Parent = lp.PlayerGui
	local anel = Instance.new("Frame"); anel.AnchorPoint = Vector2.new(0.5, 0); anel.Position = UDim2.new(0.5, 0, 0, 0); anel.Size = UDim2.fromOffset(46, 46)
	anel.BackgroundTransparency = 1; anel.Parent = bb
	local cr = Instance.new("UICorner"); cr.CornerRadius = UDim.new(0.5, 0); cr.Parent = anel
	local st = Instance.new("UIStroke"); st.Color = TRAVA.cor; st.Thickness = 3; st.Parent = anel
	local txt = Instance.new("TextLabel"); txt.BackgroundTransparency = 1; txt.Position = UDim2.new(0, 0, 0, 50); txt.Size = UDim2.new(1, 0, 0, 22)
	txt.Font = Enum.Font.GothamBold; txt.TextSize = 14; txt.TextColor3 = TRAVA.cor; txt.TextStrokeTransparency = 0.4; txt.Text = ""; txt.Parent = bb
	trava = {alvo = melhor, raiz = r, hl = hl, bb = bb, txt = txt, anel = anel}
	avisoTrava("Alvo travado: " .. melhor.Name)
end
travaAtual = function()                                              -- alvo travado ainda valido? (solta sozinho se nao)
	if not trava then return nil end
	local r = raizAlvo(trava.alvo)
	if not (m and r and alvoVivo(trava.alvo)) or (r.Position - m:GetPivot().Position).Magnitude > TRAVA.quebra then soltarTrava(); return nil end
	trava.raiz = r; return trava
end
RunService.RenderStepped:Connect(function()
	local t = travaAtual(); if not t then return end
	local d = (t.raiz.Position - m:GetPivot().Position).Magnitude
	t.txt.Text = ("%d m"):format(math.floor(d + 0.5)); t.anel.Rotation = (os.clock() * 90) % 360
end)
function dirMira()
	local t = travaAtual()                                             -- PATCH_TRAVA_ALVO: alvo travado comanda a mira
	if t then local v = t.raiz.Position - bocaPos(); if v.Magnitude > 1 then return v.Unit end end
	local alvo = pontoMira(); local v = alvo - bocaPos()
]==])
  src = troca(src, [==[elseif m:GetAttribute("MontariaModo") == "chao" and Pedido then Pedido:FireServer(m, "usar", "Mordida", workspace.CurrentCamera.CFrame.LookVector) end]==], [==[elseif m:GetAttribute("MontariaModo") == "chao" and Pedido then Pedido:FireServer(m, "usar", "Mordida", travaAtual() and dirMira() or workspace.CurrentCamera.CFrame.LookVector, trava and trava.alvo) end]==])
  src = troca(src, [==[					Pedido:FireServer(m, "usar", "Garra", workspace.CurrentCamera.CFrame.LookVector)]==], [==[					Pedido:FireServer(m, "usar", "Garra", travaAtual() and dirMira() or workspace.CurrentCamera.CFrame.LookVector, trava and trava.alvo)]==])
  src = troca(src, [==[			if st == Enum.UserInputState.Begin and m and Pedido then Pedido:FireServer(m, "usar", "Rugido", workspace.CurrentCamera.CFrame.LookVector) end]==], [==[			if st == Enum.UserInputState.Begin and m and Pedido then Pedido:FireServer(m, "usar", "Rugido", travaAtual() and dirMira() or workspace.CurrentCamera.CFrame.LookVector) end]==])
  src = troca(src, [==[				Pedido:FireServer(m, "usar", h[1], dirMira())                     -- direcao da BOCA ate o ponto do cursor]==], [==[				Pedido:FireServer(m, "usar", h[1], dirMira(), travaAtual() and trava.alvo or nil)   -- direcao da BOCA ate o cursor/alvo travado]==])
  src = troca(src, [==[	acao("Mont_Pousar", function(st) if st == Enum.UserInputState.Begin then Comando:FireServer("pousar") end; return Enum.ContextActionResult.Sink end, C.pousar, "Pousar")
]==], [==[	acao("Mont_Pousar", function(st) if st == Enum.UserInputState.Begin then Comando:FireServer("pousar") end; return Enum.ContextActionResult.Sink end, C.pousar, "Pousar")
	if C.travar then acao("Mont_Trava", function(st) if st == Enum.UserInputState.Begin then if trava then soltarTrava(); avisoTrava("Alvo solto") else travar() end end; return Enum.ContextActionResult.Sink end, C.travar, "Alvo") end   -- PATCH_TRAVA_ALVO
]==])
  src = troca(src, [==[	for _, n in ipairs({"Mont_Subir", "Mont_Descer", "Mont_Correr", "Mont_Planar", "Mont_Pousar", "Mont_Desmontar", "Mont_Elemento", "Mont_Mordida", "Mont_Garra", "Mont_Rugido"}) do CAS:UnbindAction(n) end]==], [==[	for _, n in ipairs({"Mont_Subir", "Mont_Descer", "Mont_Correr", "Mont_Planar", "Mont_Pousar", "Mont_Desmontar", "Mont_Elemento", "Mont_Mordida", "Mont_Garra", "Mont_Rugido", "Mont_Trava"}) do CAS:UnbindAction(n) end
	soltarTrava()                                                       -- PATCH_TRAVA_ALVO]==])
  src = troca(src, [==[	if C.dicaForma and C.dicaForma[fr] then dica.Text ..= C.dicaForma[fr] end
]==], [==[	if C.dicaForma and C.dicaForma[fr] then dica.Text ..= C.dicaForma[fr] end
	if C.travar then dica.Text ..= " | C / clique do meio: travar alvo" end   -- PATCH_TRAVA_ALVO
]==])
  assert(loadstring(src), "Montaria_Cliente.client.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ReplicatedStorage.Montaria_Dragoes.ConfigMontaria; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_TRAVA_ALVO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[		elemento = {Enum.KeyCode.Z, Enum.KeyCode.DPadUp},                  -- so liga em forma com MAIS de um elemento (nenhuma hoje)
]==], [==[		elemento = {Enum.KeyCode.Z, Enum.KeyCode.DPadUp},                  -- so liga em forma com MAIS de um elemento (nenhuma hoje)
		travar = {Enum.KeyCode.C, Enum.UserInputType.MouseButton3, Enum.KeyCode.ButtonR3},   -- PATCH_TRAVA_ALVO: alvo dinamico (liga/solta)
]==])
  assert(loadstring(src), "ConfigMontaria.luau nao compila"); table.insert(novos, {s, src}) end
do local s = game.ServerScriptService.Combate_Dragao_Servidor; local src = s.Source:gsub("\r\n", "\n")
  if src:find("PATCH_TRAVA_ALVO", 1, true) then return "scripts ja aplicados" end
  src = troca(src, [==[Pedido.OnServerEvent:Connect(function(plr, m, acao, arg, dir)
]==], [==[Pedido.OnServerEvent:Connect(function(plr, m, acao, arg, dir, alvo)
]==])
  src = troca(src, [==[		local usou = c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil, segurar = arg == "Sopro"})
]==], [==[		-- PATCH_TRAVA_ALVO (04/11): alvo travado pelo cavaleiro so vale se for alvo VALIDO deste dragao e estiver no alcance
		local alvoOk
		if typeof(alvo) == "Instance" and alvo:IsA("Model") and alvo:IsDescendantOf(workspace) then
			local rr = alvo:FindFirstChild("HumanoidRootPart") or alvo.PrimaryPart
			if rr and (rr.Position - m:GetPivot().Position).Magnitude <= 420 then
				for _, a in ipairs(c:alvosValidos()) do if a == alvo then alvoOk = alvo; break end end
			end
		end
		local usou = c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil, segurar = arg == "Sopro", alvo = alvoOk})
]==])
  assert(loadstring(src), "Combate_Dragao_Servidor.server.luau nao compila"); table.insert(novos, {s, src}) end
if not SS:FindFirstChild("Backup_Trava_Alvo_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Trava_Alvo_2026-11-04"; for _, x in ipairs(novos) do x[1]:Clone().Parent = f end; f.Parent = SS end
for _, x in ipairs(novos) do x[1].Source = x[2] end
return "aplicado: Montaria_Cliente + ConfigMontaria + Combate_Dragao_Servidor (" .. #novos .. "); backup ServerStorage.Backup_Trava_Alvo_2026-11-04"

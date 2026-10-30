-- patch_mira_camera.luau (Studio, Edit) — ATUALIZACAO OFICIAL de camera, mouse livre, mira dos poderes e controles E/Q.
-- Tudo-ou-nada: as trocas sao feitas numa copia; so grava se todas acharem o trecho original. Originais em
-- ServerStorage.Backup_Scripts_MiraCamera.
local SSS, RS, SP = game:GetService("ServerScriptService"), game:GetService("ReplicatedStorage"), game:GetService("StarterPlayer")
local log, copia, ordem = {}, {}, {}
local function trocar(script, velho, novo, rotulo)
	if not copia[script] then copia[script] = script.Source; table.insert(ordem, script) end
	local src = copia[script]
	local a, b = src:find(velho, 1, true)
	assert(a, "NADA FOI ALTERADO - trecho nao encontrado em " .. script:GetFullName() .. ": " .. rotulo)
	copia[script] = src:sub(1, a - 1) .. novo .. src:sub(b + 1)
	table.insert(log, script.Name .. ": " .. rotulo)
end
local CM = RS.Montaria_Dragoes.ConfigMontaria
local MC = SP.StarterPlayerScripts.Montaria_Cliente
local MS = SSS.Montaria_Dragao_Servidor
local CS = SSS.Combate_Dragao_Servidor
local N = SSS.Combate_Dragao.Nucleo
local VFX = RS.Combate_Dragoes.VFXCombate
local MV = SP.StarterPlayerScripts.MovimentoVivo_Cliente

-- 1) teclas E/Q (subir/descer no ar) + sopro continuo (config)
trocar(CM, [[		pousar = {Enum.KeyCode.F, Enum.KeyCode.ButtonB},]],
[[		pousar = {Enum.KeyCode.F, Enum.KeyCode.ButtonB},
		subirAr = {Enum.KeyCode.E}, descerAr = {Enum.KeyCode.Q},          -- (29/10) E sobe / Q desce (prioridade sobre a camera)]], "teclas E/Q")

-- 2) servidor de voo: com E/Q segurado, E/Q decidem a vertical (com W: sobe/desce avancando 35 graus; sem W: no lugar)
trocar(MS, [[	local gAlvo = f > 0.1 and math.clamp(cp * V.ganhoPitch, -math.rad(V.gamaMaxDescida), math.rad(V.gamaMaxSubida)) or 0]],
[[	local gAlvo = f > 0.1 and math.clamp(cp * V.ganhoPitch, -math.rad(V.gamaMaxDescida), math.rad(V.gamaMaxSubida)) or 0
	-- E/Q tem PRIORIDADE sobre o pitch da camera (sem disputa): com W, sobe/desce avancando; sem W, o vertical do hover
	if f > 0.1 and math.abs(e.up or 0) > 0.3 then gAlvo = (e.up > 0 and 1 or -1) * math.rad(VL.gamaEQ or 35) end]], "prioridade E/Q")
trocar(MS, [[	if not M.planar and (e.up or 0) ~= 0 then vyH = (e.up > 0 and e.up * VL.vSubidaParado or e.up * VL.vDescidaParado) * (1 - mover * 0.6) end]],
[[	if not M.planar and (e.up or 0) ~= 0 and f <= 0.1 then vyH = (e.up > 0 and e.up * VL.vSubidaParado or e.up * VL.vDescidaParado) * (1 - mover * 0.6) end]], "vertical so sem W")
trocar(CM, [[vSubidaParado = 10, vDescidaParado = 12,]], [[vSubidaParado = 16, vDescidaParado = 16, gamaEQ = 35,]], "subida/descida no lugar mais fortes")

-- 3) cliente: E/Q, mouse livre, camera so com botao direito, mira pelo cursor, reticula, sopro segurado
trocar(MC, [[	end, C.decolar, "Voar")
	acao("Mont_Descer", function(st) seg.descer = st == Enum.UserInputState.Begin; return Enum.ContextActionResult.Sink end, C.descer, "Descer")]],
[[	end, {table.unpack(C.decolar), table.unpack(C.subirAr or {})}, "Voar")
	acao("Mont_Descer", function(st) seg.descer = st == Enum.UserInputState.Begin; return Enum.ContextActionResult.Sink end, {table.unpack(C.descer), table.unpack(C.descerAr or {})}, "Descer")]], "E/Q no subir/descer")
trocar(MC, [[	for _, h in ipairs(C.habilidades) do
		acao("Mont_" .. h[1], function(st)
			if st == Enum.UserInputState.Begin and m and Pedido then Pedido:FireServer(m, "usar", h[1], workspace.CurrentCamera.CFrame.LookVector) end
			return Enum.ContextActionResult.Sink
		end, {h[2], h[3]}, h[1])
	end]],
[[	for _, h in ipairs(C.habilidades) do
		acao("Mont_" .. h[1], function(st)
			if not (m and Pedido) then return Enum.ContextActionResult.Sink end
			if st == Enum.UserInputState.Begin then
				Pedido:FireServer(m, "usar", h[1], dirMira())                     -- direcao da BOCA ate o ponto do cursor
				if h[1] == "Sopro" then soproSegurado = true end
			elseif st == Enum.UserInputState.End and h[1] == "Sopro" and soproSegurado then
				soproSegurado = false; Pedido:FireServer(m, "soltar")
			end
			return Enum.ContextActionResult.Sink
		end, {h[2], h[3]}, h[1])
	end]], "habilidades miram pelo cursor; sopro segurado")
trocar(MC, [[local orbita, mouseLivre = false, false]],
[[local orbita, mouseLivre = false, false
-- ===== mira pelo cursor (mouse livre) =============================================================================
-- O cursor NAO fica preso: aponta os poderes. Raio da camera pelo ponto do cursor (ignora o proprio dragao, o
-- cavaleiro e os efeitos); a direcao final sai da BOCA ate esse ponto (o servidor valida o cone do pescoco).
local rpMira = RaycastParams.new(); rpMira.FilterType = Enum.RaycastFilterType.Exclude
function pontoMira()
	local cam = workspace.CurrentCamera
	local p = UIS:GetMouseLocation()
	local raio = cam:ViewportPointToRay(p.X, p.Y)
	local ex = {}
	if m then table.insert(ex, m) end
	if lp.Character then table.insert(ex, lp.Character) end
	if alvoCam then table.insert(ex, alvoCam) end
	local fx = workspace:FindFirstChild("VFX_Temporarios"); if fx then table.insert(ex, fx) end
	rpMira.FilterDescendantsInstances = ex
	local h = workspace:Raycast(raio.Origin, raio.Direction * 700, rpMira)
	return h and h.Position or (raio.Origin + raio.Direction * 400), h
end
local function bocaPos()
	if not m then return Vector3.zero end
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == "mouth_upper_tip" then return d.TransformedWorldCFrame.Position end end
	return m:GetPivot().Position
end
function dirMira()
	local alvo = pontoMira(); local v = alvo - bocaPos()
	return v.Magnitude > 1 and v.Unit or workspace.CurrentCamera.CFrame.LookVector
end]], "mira pelo cursor")
trocar(MC, [[	UIS.MouseBehavior = mouseLivre and Enum.MouseBehavior.Default or Enum.MouseBehavior.LockCenter
	UIS.MouseIconEnabled = mouseLivre
	if not mouseLivre then
		local d = UIS:GetMouseDelta()
		local sens = 0.0042 * UserSettings():GetService("UserGameSettings").MouseSensitivity
		orb.yaw -= d.X * sens; orb.pitch -= d.Y * sens
	end]],
[[	-- MOUSE LIVRE (oficial 29/10): o cursor fica solto para mirar; a camera so gira com o BOTAO DIREITO segurado.
	-- Sem girar, a camera volta suave para tras do dragao (nada de curva involuntaria a cada movimento do mouse).
	local orbitando = UIS:IsMouseButtonPressed(Enum.UserInputType.MouseButton2)
	UIS.MouseBehavior = orbitando and Enum.MouseBehavior.LockCurrentPosition or Enum.MouseBehavior.Default
	UIS.MouseIconEnabled = false                                              -- a reticula pequena faz o papel do cursor
	if orbitando then
		local d = UIS:GetMouseDelta()
		local sens = 0.0042 * UserSettings():GetService("UserGameSettings").MouseSensitivity
		orb.yaw -= d.X * sens; orb.pitch -= d.Y * sens
	elseif (m:GetAttribute("Velocidade") or 0) > 2 or m:GetAttribute("NoAr") then
		local lv = m:GetPivot().LookVector
		local alvoYaw = math.atan2(-lv.X, -lv.Z)
		local dif = (alvoYaw - orb.yaw + math.pi) % (2 * math.pi) - math.pi
		orb.yaw += dif * math.min(1, 2.2 * dt)
	end
	orbAtivo = orbitando]], "mouse livre + camera no botao direito")
trocar(MC, [[local orb = {yaw = 0, pitch = -0.28, dist = 70, zoom = nil}]],
[[local orb = {yaw = 0, pitch = -0.28, dist = 70, zoom = nil}
local orbAtivo = false]], "estado da orbita")
trocar(MC, [[		local cy, cp = cyCp()
		Entrada:FireServer({f = -mv.Z, t = mv.X, up = (seg.subir and 1 or 0) - (seg.descer and 1 or 0), c = seg.correr, cy = cy, cp = cp})]],
[[		local cy, cp = cyCp()
		-- a camera so comanda o rumo/pitch do voo enquanto o jogador a GIRA (botao direito ou analogico direito);
		-- fora disso o dragao segue reto/A-D e o cursor serve so para mirar
		local stick = false
		for _, st in ipairs(UIS:GetGamepadState(Enum.UserInputType.Gamepad1)) do if st.KeyCode == Enum.KeyCode.Thumbstick2 and st.Position.Magnitude > 0.15 then stick = true end end
		if not (orbAtivo or stick or not UIS.MouseEnabled) then cy, cp = nil, 0 end
		Entrada:FireServer({f = -mv.Z, t = mv.X, up = (seg.subir and 1 or 0) - (seg.descer and 1 or 0), c = seg.correr, cy = cy, cp = cp})
		local dm = dirMira(); m:SetAttribute("MiraLocal", dm)                   -- cabeca do dragao olha a mira (MovimentoVivo)
		if soproSegurado and Pedido then Pedido:FireServer(m, "mira", nil, dm) end]], "rumo so com camera girando; mira enviada")
trocar(MC, [[	gui.Enabled = false; m = nil]],
[[	gui.Enabled = false; if reticula then reticula.Visible = false end; soproSegurado = false; m = nil]], "esconde reticula ao sair")
trocar(MC, [[	gui.Enabled = true
	ligarAcoes()]],
[[	gui.Enabled = true; if reticula then reticula.Visible = UIS.MouseEnabled end
	ligarAcoes()]], "mostra reticula ao montar")
trocar(MC, [[local function entrar(dragao)]],
[[-- reticula pequena e discreta no cursor: branca; vermelha sobre um alvo com Humanoid (nao garante acerto)
local reticula = Instance.new("Frame"); reticula.Name = "Reticula"; reticula.Size = UDim2.fromOffset(14, 14); reticula.AnchorPoint = Vector2.new(0.5, 0.5)
reticula.BackgroundTransparency = 1; reticula.Visible = false; reticula.ZIndex = 50; reticula.Parent = gui
local anelR = Instance.new("UIStroke"); anelR.Thickness = 1.6; anelR.Color = Color3.fromRGB(240, 240, 240); anelR.Transparency = 0.15; anelR.Parent = reticula
Instance.new("UICorner", reticula).CornerRadius = UDim.new(1, 0)
local pontoR = Instance.new("Frame"); pontoR.Size = UDim2.fromOffset(2, 2); pontoR.AnchorPoint = Vector2.new(0.5, 0.5); pontoR.Position = UDim2.fromScale(0.5, 0.5)
pontoR.BackgroundColor3 = Color3.fromRGB(240, 240, 240); pontoR.BorderSizePixel = 0; pontoR.Parent = reticula
RunService.RenderStepped:Connect(function()
	if not (m and reticula.Visible) then return end
	local p = UIS:GetMouseLocation(); local ins = game:GetService("GuiService"):GetGuiInset()
	reticula.Position = UDim2.fromOffset(p.X - ins.X, p.Y - ins.Y)
	local _, h = pontoMira()
	local alvo = h and h.Instance and h.Instance:FindFirstAncestorWhichIsA("Model")
	local valido = alvo and alvo:FindFirstChildOfClass("Humanoid") ~= nil
	anelR.Color = valido and Color3.fromRGB(255, 90, 80) or Color3.fromRGB(240, 240, 240); pontoR.BackgroundColor3 = anelR.Color
end)
local function entrar(dragao)]], "reticula")
trocar(MC, [[local alvoCam, camAntes]], [[local alvoCam, camAntes
local soproSegurado = false                                           -- sopro com a tecla segurada (mira viva)]], "estado do sopro segurado")
trocar(MC, [["Mouse: direcao | W acelera (no ar: sobe/desce para onde a camera olha) | solte W: para no ar | Espaco: decolar / subir parado | Ctrl: descer (perto do chao pousa sozinho)]],
[["Botao direito: girar a camera (o dragao segue) | Cursor: mira | W acelera | solte W: para no ar | E sobe / Q desce | Espaco: decolar | segure 1: sopro continuo (mira no cursor)]], "dica")

-- 4) camera: zoom 12-25-45 no Silverwing (montaria)
for _, n in ipairs({"Silverwing", "Silverwing_Guardiao"}) do
	local mm = workspace:FindFirstChild(n)
	if mm then mm:SetAttribute("Camera_distMin", 12); mm:SetAttribute("Camera_distancia", 25); mm:SetAttribute("Camera_distMax", 45) end
end
table.insert(log, "camera Silverwing: min 12, padrao 25, max 45")

-- 5) servidor de combate: mira viva e soltar o sopro (com limite proprio de frequencia)
trocar(CS, [[	if m:GetAttribute("DonoUserId") ~= plr.UserId then return end
	if m:GetAttribute("EmAtaque") == "MordidaAerea" then return end]],
[[	if m:GetAttribute("DonoUserId") ~= plr.UserId then return end
	local c0 = N.registro[m]
	if acao == "mira" then                                                -- direcao da mira (so usada pelo sopro segurado)
		if typeof(dir) == "Vector3" and dir.Magnitude > 0.5 and dir.Magnitude < 2 and os.clock() - (c0.miraT or 0) > 0.05 then c0.miraDir = dir.Unit; c0.miraT = os.clock() end
		return
	end
	if acao == "soltar" then c0.segurando = false; return end
	if m:GetAttribute("EmAtaque") == "MordidaAerea" then return end]], "mira/soltar")
trocar(CS, [[		c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil})]],
[[		if arg == "Sopro" and not c.ocupado then c.segurando = true; c.miraDir = typeof(dir) == "Vector3" and dir.Unit or nil end
		c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil, segurar = arg == "Sopro"})]], "sopro segurado")
trocar(N, [[		local pulsos = 0
		while os.clock() < fim do
			local b, f = self:boca()]],
[[		local pulsos = 0
		-- SOPRO CONTINUO (oficial 29/10): segurando a tecla, segue enquanto houver energia (ate emissaoMax); a mira do
		-- cursor atualiza a direcao dentro do cone do pescoco; alem da emissao base consome energia por segundo
		local t0, ultMira = os.clock(), 0
		while true do
			local agora = os.clock()
			local segue = op.segurar and self.segurando ~= false and agora - t0 < (def.emissaoMax or 6) and self.energia > 0
			if agora >= fim and not segue then break end
			if op.segurar and self.segurando == false and agora - t0 > 0.5 then break end
			if agora > fim then self.energia = math.max(0, self.energia - (def.energiaSeg or 8) * def.tick); self.m:SetAttribute("Energia", self.energia) end
			if op.segurar and self.miraDir then
				local d = self.miraDir; local pd = plano(d)
				if pd.Magnitude > 0.1 and pd.Unit:Dot(self:frente()) > 0.25 and math.abs(d.Y) < 0.85 then
					local novo = self:boca() + d * e.alcance
					if not alvoPos or (novo - alvoPos).Magnitude > 3 then
						alvoPos = novo
						if agora - ultMira > 0.12 then ultMira = agora; FX:FireAllClients({d = self.m, hab = "Sopro", fase = "mira", el = el, alvoPos = alvoPos}) end
					end
				end
			end
			local b, f = self:boca()]], "sopro continuo com mira")
trocar(N, [[	if loop then loop:Stop(0.15) end
	FX:FireAllClients({d = self.m, hab = "Sopro", fase = "fim", el = el})]],
[[	if loop then loop:Stop(0.15) end
	self.segurando = nil; self.miraDir = nil
	FX:FireAllClients({d = self.m, hab = "Sopro", fase = "fim", el = el})]], "fim do sopro limpa a mira")
trocar(game.ServerScriptService.Combate_Dragao.ConfigCombate, [[		Sopro = {recarga = 9, energia = 25, emissao = 1.8, tick = 0.3, elemental = true,]],
[[		Sopro = {recarga = 9, energia = 25, emissao = 1.8, tick = 0.3, elemental = true,
			emissaoMax = 6, energiaSeg = 8,                       -- segurado: ate 6 s, 8 de energia/s alem dos 1,8 s (EXPERIMENTAL)]], "config sopro continuo")

-- 6) efeitos: o jato segue a mira viva e dura enquanto o sopro estiver ativo
trocar(VFX, [[		elseif d.fase == "emissao" then
			if d.forma ~= "projetil" then ligarSopro(m, el, true, f, d.alvoPos, d.alcance) end]],
[[		elseif d.fase == "mira" then                                         -- sopro segurado: nova direcao validada pelo servidor
			miraSopro[m] = d.alvoPos; local s = emissoresSopro(m, el); s.alvo = d.alvoPos
		elseif d.fase == "emissao" then
			miraSopro[m] = d.alvoPos; soproAtivo[m] = (soproAtivo[m] or 0) + 1
			if d.forma ~= "projetil" then ligarSopro(m, el, true, f, d.alvoPos, d.alcance) end]], "fase mira")
trocar(VFX, [[					local fim = os.clock() + (d.duracao or 1.8)
					local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
					while os.clock() < fim and m.Parent do
						local b, dr = bocaDe(m); if d.alvoPos then dr = (d.alvoPos - b).Unit end]],
[[					local tok = soproAtivo[m]; local lim = os.clock() + 8
					local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
					while soproAtivo[m] == tok and os.clock() < lim and m.Parent do
						local b, dr = bocaDe(m); local ap = miraSopro[m] or d.alvoPos; if ap then dr = (ap - b).Unit end]], "impacto segue a mira")
trocar(VFX, [[		elseif d.fase == "fim" then ligarSopro(m, el, false, f); if el == "Fogo" then brilhoCorpo(m, 0.8, 0.9) end end]],
[[		elseif d.fase == "fim" then soproAtivo[m] = (soproAtivo[m] or 0) + 1; miraSopro[m] = nil; ligarSopro(m, el, false, f); if el == "Fogo" then brilhoCorpo(m, 0.8, 0.9) end end]], "fim encerra laços")
trocar(VFX, [[local function ligarSopro(m, el, ligado, fator, alvo, alcance)]],
[[local miraSopro, soproAtivo = {}, {}                                  -- mira viva e ficha do sopro em curso, por dragao
local function ligarSopro(m, el, ligado, fator, alvo, alcance)]], "estado do sopro")

-- 7) cabeca olha a MIRA do cavaleiro (antes: a direcao da camera)
trocar(MV, [[	if cav and eu and cav == eu.UserId then alvoDir = cam.CFrame.LookVector]],
[[	if cav and eu and cav == eu.UserId then alvoDir = m:GetAttribute("MiraLocal") or cam.CFrame.LookVector]], "cabeca segue a mira")

local bk = game:GetService("ServerStorage"):FindFirstChild("Backup_Scripts_MiraCamera") or Instance.new("Folder")
bk.Name = "Backup_Scripts_MiraCamera"; bk.Parent = game:GetService("ServerStorage")
for _, s in ipairs(ordem) do
	local v = bk:FindFirstChild(s.Name) or Instance.new("StringValue"); v.Name = s.Name; v.Value = s.Source; v.Parent = bk
	s.Source = copia[s]
end
return table.concat(log, "\n")

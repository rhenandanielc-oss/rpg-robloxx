-- IA_FaunaFloresta/Cena - cena ISOLADA do piloto em Workspace.Teste_FaunaFloresta (y=2600). Dados + construtor.
-- Tudo aqui e de teste: chao maior, marcas de referencia a cada 20 studs, 3 poleiros (A, B e o seguro C) e rotas aereas
-- explicitas. construir() so cria/atualiza objetos dentro da pasta da cena; desfazer() remove o que construir() criou.
local S = {}

S.Y = 2600
S.area = { centro = Vector3.new(0, 2600, 300), tamanho = Vector3.new(260, 40, 220) }
S.casas = {
	Cervo = { pos = Vector3.new(-50, 2600, 330), dir = Vector3.new(1, 0, 0) },
	Javali = { pos = Vector3.new(30, 2600, 345), dir = Vector3.new(-1, 0, 0) },
}
-- poleiros: base no chao, altura do tronco; o topo (pivo da coruja) = base + altura + 0.4
S.poleiros = {
	A = { base = Vector3.new(55, 2600, 255), altura = 10, dir = Vector3.new(-1, 0, 0) },
	B = { base = Vector3.new(-35, 2600, 255), altura = 10, dir = Vector3.new(1, 0, 0) },
	C = { base = Vector3.new(100, 2600, 390), altura = 16, dir = Vector3.new(-1, 0, 0), seguro = true },
}
S.corujaInicio = "A"
local function topo(n) local p = S.poleiros[n]; return p.base + Vector3.new(0, p.altura + 0.4, 0) end
S.topo = topo
-- rotas aereas explicitas (pontos do pivo da coruja); o ultimo ponto define a direcao do pouso
S.rotas = {
	A_B = { Vector3.new(45, 2616, 262), Vector3.new(10, 2618, 266), Vector3.new(-12, 2614, 260) },
	B_A = { Vector3.new(-25, 2616, 248), Vector3.new(10, 2618, 244), Vector3.new(32, 2614, 250) },
	A_C = { Vector3.new(58, 2618, 272), Vector3.new(78, 2621, 330), Vector3.new(90, 2620, 362) },
	B_C = { Vector3.new(-28, 2618, 272), Vector3.new(25, 2621, 330), Vector3.new(78, 2620, 372) },
	C_A = { Vector3.new(92, 2621, 370), Vector3.new(72, 2620, 300), Vector3.new(62, 2615, 278) },
	C_B = { Vector3.new(88, 2621, 372), Vector3.new(20, 2620, 320), Vector3.new(-25, 2615, 278) },
}

function S.construir(pasta)
	local cena = pasta:FindFirstChild("Cena_IA") or Instance.new("Folder")
	cena.Name = "Cena_IA"; cena.Parent = pasta
	cena:ClearAllChildren()
	local chao = pasta:FindFirstChild("Chao")
	if chao then
		if not chao:GetAttribute("TamanhoOriginal") then chao:SetAttribute("TamanhoOriginal", chao.Size) end
		chao.Size = Vector3.new(S.area.tamanho.X, 1, S.area.tamanho.Z)
		chao.CFrame = CFrame.new(S.area.centro - Vector3.new(0, 0.5, 0))
	end
	-- marcas de referencia (nao colidem nem bloqueiam raycast)
	for x = -120, 120, 20 do
		local m = Instance.new("Part"); m.Name = "Marca_X" .. x; m.Anchored = true; m.CanCollide = false; m.CanQuery = false; m.CanTouch = false
		m.Size = Vector3.new(0.4, 0.06, S.area.tamanho.Z - 4); m.Material = Enum.Material.SmoothPlastic
		m.Color = x == 0 and Color3.fromRGB(230, 200, 60) or Color3.fromRGB(235, 235, 235); m.Transparency = 0.3
		m.CFrame = CFrame.new(x, S.Y + 0.03, S.area.centro.Z); m.Parent = cena
	end
	for nome, p in pairs(S.poleiros) do
		local mdl = Instance.new("Model"); mdl.Name = "Poleiro_" .. nome
		local tronco = Instance.new("Part"); tronco.Name = "Tronco"; tronco.Anchored = true; tronco.Shape = Enum.PartType.Cylinder
		tronco.Size = Vector3.new(p.altura, 1.4, 1.4); tronco.CFrame = CFrame.new(p.base + Vector3.new(0, p.altura / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
		tronco.Material = Enum.Material.Wood; tronco.Color = Color3.fromRGB(92, 66, 44); tronco.Parent = mdl
		local t = Instance.new("Part"); t.Name = "Topo"; t.Anchored = true; t.Size = Vector3.new(2.4, 0.4, 2.4)
		t.CFrame = CFrame.new(p.base + Vector3.new(0, p.altura + 0.2, 0)); t.Material = Enum.Material.Wood
		t.Color = Color3.fromRGB(110, 80, 52); t.Parent = mdl
		local bb = Instance.new("BillboardGui"); bb.Size = UDim2.fromOffset(60, 24); bb.StudsOffsetWorldSpace = Vector3.new(0, 1.5, 0)
		bb.AlwaysOnTop = true; local l = Instance.new("TextLabel"); l.Size = UDim2.fromScale(1, 1); l.BackgroundTransparency = 1
		l.TextColor3 = p.seguro and Color3.fromRGB(120, 255, 120) or Color3.new(1, 1, 0.6); l.TextScaled = true
		l.Text = nome .. (p.seguro and " seguro" or ""); l.Parent = bb; bb.Parent = t
		mdl.PrimaryPart = t; mdl.Parent = cena
	end
	return cena
end

function S.desfazer(pasta)
	local cena = pasta:FindFirstChild("Cena_IA"); if cena then cena:Destroy() end
	local chao = pasta:FindFirstChild("Chao")
	if chao and chao:GetAttribute("TamanhoOriginal") then
		chao.Size = chao:GetAttribute("TamanhoOriginal"); chao.CFrame = CFrame.new(Vector3.new(0, S.Y - 0.5, 300))
		chao:SetAttribute("TamanhoOriginal", nil)
	end
end

-- coloca os 3 animais nas posicoes iniciais (casa / poleiro A)
function S.posicionar(pasta)
	for esp, c in pairs(S.casas) do
		local m = pasta:FindFirstChild(esp .. "_Teste")
		if m then m:PivotTo(CFrame.lookAt(c.pos, c.pos + c.dir)) end
	end
	local cj = pasta:FindFirstChild("Coruja_Teste")
	if cj then local t = topo(S.corujaInicio); cj:PivotTo(CFrame.lookAt(t, t + S.poleiros[S.corujaInicio].dir)) end
end

return S

-- Monta o Laboratorio_IA no place de TESTE (rodar no modo Edit pela linha de comando do Studio ou Studio MCP).
-- Relevo: pico (ninho no topo ~y186), caverna com tunel e camara (ninho no piso), lago, coluna-poleiro, rochas;
-- POIs (Agua, Comida, Observacao, Poleiro); invasores de teste com tag "Invasor_Teste". Nao usar no mapa oficial.
local T = workspace.Terrain
local PICO, CAV = Vector3.new(500, 0, 900), Vector3.new(160, 0, 1250)
for y = 0, 176, 8 do T:FillCylinder(CFrame.new(PICO + Vector3.new(0, y + 4, 0)), 8, math.max(46, 170 * (1 - y / 200)), Enum.Material.Rock); if y % 32 == 0 then task.wait() end end
T:FillCylinder(CFrame.new(PICO + Vector3.new(0, 182, 0)), 4, 46, Enum.Material.Slate)
for y = 0, 128, 8 do T:FillCylinder(CFrame.new(CAV + Vector3.new(0, y + 4, 0)), 8, 150 * (1 - y / 170), Enum.Material.Basalt); if y % 32 == 0 then task.wait() end end
T:FillBlock(CFrame.new(CAV + Vector3.new(0, 36, -110)), Vector3.new(84, 68, 160), Enum.Material.Air)
T:FillBall(CAV + Vector3.new(0, 30, 0), 62, Enum.Material.Air)
T:FillBlock(CFrame.new(CAV + Vector3.new(0, 1, 0)), Vector3.new(200, 2, 300), Enum.Material.Ground)
T:FillCylinder(CFrame.new(Vector3.new(860, 3, 560)), 6, 70, Enum.Material.Water)
T:FillCylinder(CFrame.new(Vector3.new(300, 45, 560)), 90, 26, Enum.Material.Rock)
for _, p in ipairs({Vector3.new(760, 8, 960), Vector3.new(260, 8, 780), Vector3.new(640, 8, 600)}) do T:FillBall(p, 16, Enum.Material.Rock) end
task.wait()
local lab = workspace:FindFirstChild("Laboratorio_IA") or Instance.new("Folder"); lab.Name = "Laboratorio_IA"; lab.Parent = workspace; lab:ClearAllChildren()
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {lab}
local function chao(x, z, topo) local r = workspace:Raycast(Vector3.new(x, topo or 600, z), Vector3.new(0, -800, 0), rp); return r and r.Position.Y or 0 end
local function ninho(nome, pos, extra)
	local m = Instance.new("Model"); m.Name = nome
	local base = Instance.new("Part"); base.Name = "Base"; base.Shape = Enum.PartType.Cylinder; base.Size = Vector3.new(2, 22, 22)
	base.CFrame = CFrame.new(pos + Vector3.new(0, 1, 0)) * CFrame.Angles(0, 0, math.rad(90)); base.Anchored = true
	base.Material = Enum.Material.Wood; base.Color = Color3.fromRGB(90, 62, 40); base.Parent = m
	local ovo = Instance.new("Part"); ovo.Name = "Ovo"; ovo.Shape = Enum.PartType.Ball; ovo.Size = Vector3.new(5, 5, 5)
	ovo.Position = pos + Vector3.new(0, 4.5, 0); ovo.Anchored = true; ovo.Material = Enum.Material.Basalt; ovo.Color = Color3.fromRGB(70, 30, 20)
	ovo:SetAttribute("Estado", "Presente"); ovo.Parent = m; m.PrimaryPart = base
	m:SetAttribute("FormaRegional", "Montanhas"); m:SetAttribute("Ativo", true); m:SetAttribute("NinhoId", nome)
	for k, v in pairs(extra or {}) do m:SetAttribute(k, v) end
	m.Parent = lab
end
ninho("Ninho_Pico", Vector3.new(500, chao(500, 900), 900))
ninho("Ninho_Caverna", Vector3.new(160, chao(160, 1250, 40), 1250), {Entrada = Vector3.new(160, chao(160, 1000), 1000)})
local pois = Instance.new("Folder"); pois.Name = "POIs"; pois.Parent = lab
local cores = {Agua = Color3.new(0.2, 0.5, 1), Comida = Color3.new(0.6, 0.2, 0.1), Observacao = Color3.new(1, 1, 0.3), Poleiro = Color3.new(0.6, 0.6, 0.6)}
local function poi(tipo, x, z, nome)
	local p = Instance.new("Part"); p.Name = nome or tipo; p.Size = Vector3.new(4, 4, 4); p.Anchored = true; p.CanCollide = false
	p.Transparency = 0.4; p.Color = cores[tipo]; p.Position = Vector3.new(x, chao(x, z) + 2, z); p:SetAttribute("Tipo", tipo); p.Parent = pois; return p
end
poi("Agua", 860, 480, "Agua_Margem")
local c = poi("Comida", 760, 1060, "Carcaca_Teste"); c.Size = Vector3.new(10, 4, 6); c.Transparency = 0; c.CanCollide = true
poi("Observacao", 760, 960); poi("Observacao", 260, 780); poi("Observacao", 640, 600); poi("Observacao", 300, 950)
poi("Poleiro", 300, 560, "Poleiro_Coluna")
for _, n in ipairs({"Invasor_A", "Invasor_B"}) do
	local m = Instance.new("Model"); m.Name = n
	local p = Instance.new("Part"); p.Name = "HumanoidRootPart"; p.Size = Vector3.new(2, 5, 2); p.Anchored = true; p.CanCollide = false
	p.Color = Color3.new(0.2, 0.9, 0.3); p.Position = Vector3.new(-900, 3, -900); p.Parent = m; m.PrimaryPart = p
	m.Parent = lab; game:GetService("CollectionService"):AddTag(m, "Invasor_Teste")
end
return "Laboratorio_IA montado"

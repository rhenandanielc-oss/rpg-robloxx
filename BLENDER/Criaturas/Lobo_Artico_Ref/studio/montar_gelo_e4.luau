-- montar_gelo_e4.luau (Studio, Edit, place Teste-animacoes) - E4 dos efeitos de gelo (17/11/2026).
-- Leva o import do GLB boreal/export/CR_LoboArtico_GeloFX_E4.glb (Import 3D do usuario) para LoboArtico_LOW.FX_Boreal:
--   * Espinho_01..08 (cristais r8l) -> trocam os do r6 (mesmo contrato: OssoEspinho, OffsetOsso, BaseLocal, TamanhoCheio, Altura)
--   * Casca_Gelo (pele nos ossos do lobo pelo NOME) -> FX_Boreal, Glass, invisivel ate o voo do Cometa
--   * Molde_Coroa_1..3, Molde_Lasca_1..2, Molde_Crosta -> FX_Boreal.Moldes (o cliente clona no pouso)
-- Backup: o FX_Boreal anterior vai inteiro para ServerStorage.LoboArtico_Backups.FX_Boreal_r6 (uma vez).
-- Base dos espinhos: Blender (x, y, z) -> Roblox (-x, z, y) a partir do pivo do lobo (conferido com o r6).
-- 17/11: o Import 3D nomeia as pecas pela MALHA (Casca_Gelo_E2, Placa_Gelo_E3) e o modelo vem como "Scene"
local imp
for _, c in ipairs(workspace:GetChildren()) do if c:IsA("Model") and c:FindFirstChild("Molde_Coroa_1") then imp = c end end
assert(imp, "import E4 nao encontrado (modelo com Molde_Coroa_1 no Workspace)")
imp.Name = "Import_GeloFX_E4"
for velho, novo in pairs({Casca_Gelo_E2 = "Casca_Gelo", Placa_Gelo_E3 = "Molde_Crosta"}) do
	local m = imp:FindFirstChild(velho); if m then m.Name = novo end
end
local lobo = workspace.Teste_LoboArtico.LoboArtico_LOW
local wb, ib = {}, {}
for _, d in ipairs(lobo:GetDescendants()) do if d:IsA("Bone") then d.Transform = CFrame.identity; wb[d.Name] = d end end
for _, d in ipairs(imp:GetDescendants()) do if d:IsA("Bone") then ib[d.Name] = d end end
local soma, n, giro = Vector3.zero, 0, 0
for nome, b in pairs(ib) do if wb[nome] then
	soma += wb[nome].TransformedWorldCFrame.Position - b.TransformedWorldCFrame.Position; n += 1
	giro = math.max(giro, (wb[nome].TransformedWorldCFrame.LookVector - b.TransformedWorldCFrame.LookVector).Magnitude)
end end
assert(n > 10, "poucos ossos em comum: " .. n)
local T = soma / n
local piv = lobo:GetPivot()
local pasta = lobo:FindFirstChild("FX_Boreal") or Instance.new("Folder"); pasta.Name = "FX_Boreal"; pasta.Parent = lobo
local bk = game.ServerStorage:FindFirstChild("LoboArtico_Backups") or Instance.new("Folder"); bk.Name = "LoboArtico_Backups"; bk.Parent = game.ServerStorage
if not bk:FindFirstChild("FX_Boreal_r6") then local c = pasta:Clone(); c.Name = "FX_Boreal_r6"; c.Parent = bk end
pasta:SetAttribute("Fonte", "boreal/export/CR_LoboArtico_GeloFX_E4.glb (Import 3D do usuario, 17/11) + montar_gelo_e4.luau")
local ESP = {
	{"Espinho_01", "Pescoco2", Vector3.new(-0.0000, 6.7730, -3.6163), Vector3.new(-0.0000, 0.4560, 0.8900), 1.350},
	{"Espinho_02", "Pescoco1", Vector3.new(0.0151, 6.4446, -2.8536), Vector3.new(-0.0752, 0.5003, 0.8626), 1.118},
	{"Espinho_03", "Pescoco1", Vector3.new(-0.0193, 6.0610, -2.1098), Vector3.new(0.1077, 0.5377, 0.8362), 0.995},
	{"Espinho_04", "Coluna3", Vector3.new(0.0083, 5.7471, -1.3698), Vector3.new(-0.0559, 0.4795, 0.8757), 0.824},
	{"Espinho_05", "Coluna2", Vector3.new(0.0026, 5.5405, -0.6334), Vector3.new(-0.0207, 0.4608, 0.8872), 0.710},
	{"Espinho_06", "Coluna2", Vector3.new(-0.0092, 5.4883, 0.1147), Vector3.new(0.0919, 0.5210, 0.8486), 0.559},
	{"Espinho_07", "Coluna1", Vector3.new(0.0080, 5.4738, 0.8522), Vector3.new(-0.1000, 0.5259, 0.8446), 0.446},
	{"Espinho_08", "Quadril", Vector3.new(-0.0020, 5.3589, 1.5505), Vector3.new(0.0357, 0.4638, 0.8852), 0.310},
}
for _, c in ipairs(imp:GetDescendants()) do
	if c:IsA("WeldConstraint") or c:IsA("JointInstance") or c:IsA("Constraint") then c:Destroy() end
end
for _, c in ipairs(imp:GetDescendants()) do if c:IsA("BasePart") then c.Anchored = true end end
local function limpar(p)
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Massless = true; p.CastShadow = false
	p.Transparency = 1
	for _, c in ipairs(p:GetChildren()) do if c:IsA("SurfaceAppearance") then c:Destroy() end end
end
local r = {}
for _, e in ipairs(ESP) do
	local m = imp:FindFirstChild(e[1], true)
	if m then
		local velho = pasta:FindFirstChild(e[1]); if velho then velho:Destroy() end
		m.CFrame = m.CFrame + T
		limpar(m); m.Material = Enum.Material.Glass; m.Color = Color3.fromRGB(190, 230, 255); m.Reflectance = 0.15
		local base = piv * e[3]
		local osso = wb[e[2]]
		m:SetAttribute("OssoEspinho", e[2])
		m:SetAttribute("OffsetOsso", osso.TransformedWorldCFrame:ToObjectSpace(m.CFrame))
		m:SetAttribute("BaseLocal", m.CFrame:PointToObjectSpace(base))
		m:SetAttribute("TamanhoCheio", m.Size)
		m:SetAttribute("Altura", e[5])
		m.Parent = pasta
		table.insert(r, string.format("%s osso=%s base->centro=%.2f tam=%.2f", e[1], e[2], (m.Position - base).Magnitude, m.Size.Magnitude))
	else table.insert(r, e[1] .. " FALTA") end
end
local casca = imp:FindFirstChild("Casca_Gelo", true)
if casca then
	local velho = pasta:FindFirstChild("Casca_Gelo"); if velho then velho:Destroy() end
	casca.CFrame = casca.CFrame + T
	limpar(casca); casca.Material = Enum.Material.Glass; casca.Color = Color3.fromRGB(175, 225, 255); casca.Reflectance = 0.2
	casca.Parent = pasta
	table.insert(r, "Casca_Gelo ok tam=" .. tostring(casca.Size))
end
local moldes = pasta:FindFirstChild("Moldes") or Instance.new("Folder"); moldes.Name = "Moldes"; moldes.Parent = pasta
for _, nome in ipairs({"Molde_Coroa_1", "Molde_Coroa_2", "Molde_Coroa_3", "Molde_Lasca_1", "Molde_Lasca_2", "Molde_Crosta"}) do
	local m = imp:FindFirstChild(nome, true)
	if m then
		local velho = moldes:FindFirstChild(nome); if velho then velho:Destroy() end
		limpar(m); m.Material = nome == "Molde_Crosta" and Enum.Material.Ice or Enum.Material.Glass
		m.Color = Color3.fromRGB(190, 232, 255); m.Reflectance = 0.15
		m.CFrame = CFrame.new(0, -300, 0)     -- guardado longe (acima do FallenPartsDestroyHeight); o cliente clona
		m.Parent = moldes
		table.insert(r, nome .. " tam=" .. tostring(m.Size))
	else table.insert(r, nome .. " FALTA") end
end
local NL = string.char(10)
return string.format("T=(%.3f,%.3f,%.3f) n=%d giroMax=%.4f", T.X, T.Y, T.Z, n, giro) .. NL .. table.concat(r, NL)

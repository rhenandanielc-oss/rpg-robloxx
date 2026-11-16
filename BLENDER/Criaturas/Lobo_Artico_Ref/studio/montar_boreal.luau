-- montar_boreal.luau (Studio, Edit, place Teste-animacoes) - Uivo Boreal: leva linhas e espinhos do import r6 para o lobo.
-- Gerado por boreal/ a partir de boreal/export/boreal_fx_r6.json. O import (Workspace.Import_BorealFX_r6) e o lobo em
-- REPOUSO diferem so por translacao (30 ossos, desvio 0,0001, sem giro; medido 16/11).
-- Linhas_*: MeshPart com pele -> vao para LoboArtico_LOW.FX_Boreal (a pele liga nos ossos do lobo pelo NOME), Neon,
-- invisiveis ate o Uivo. Espinho_*: rigidos -> FX_Boreal, ancorados e invisiveis; atributos OssoEspinho, OffsetOsso
-- (CFrame da peca no espaco do osso em repouso), BaseLocal (base no espaco da peca) e TamanhoCheio. O cliente prende
-- cada um ao osso e faz crescer/recolher a partir da base.
local imp = workspace:FindFirstChild("Import_BorealFX_r6")
assert(imp, "import r6 nao encontrado")
local lobo = workspace.Teste_LoboArtico.LoboArtico_LOW
local wb, ib = {}, {}
for _, d in ipairs(lobo:GetDescendants()) do if d:IsA("Bone") then d.Transform = CFrame.identity; wb[d.Name] = d end end
for _, d in ipairs(imp:GetDescendants()) do if d:IsA("Bone") then ib[d.Name] = d end end
local soma, n = Vector3.zero, 0
for nome, b in pairs(ib) do if wb[nome] then soma += wb[nome].TransformedWorldCFrame.Position - b.TransformedWorldCFrame.Position; n += 1 end end
local T = soma / n
local piv = lobo:GetPivot()
local pasta = lobo:FindFirstChild("FX_Boreal") or Instance.new("Folder")
pasta.Name = "FX_Boreal"; pasta.Parent = lobo
pasta:SetAttribute("Fonte", "boreal/export/CR_LoboArtico_BorealFX_r6.glb (Import 3D do usuario, 16/11) + montar_boreal.luau")
local ESP = {
	{"Espinho_01", "Coluna3", Vector3.new(-0.1058, 5.9701, -1.5296), Vector3.new(0.5064, -0.0714, 0.8593), 0.950},
	{"Espinho_02", "Coluna2", Vector3.new(0.0483, 5.6223, -0.9774), Vector3.new(-0.2660, 0.4224, 0.8665), 0.826},
	{"Espinho_03", "Coluna2", Vector3.new(0.0163, 5.4708, -0.3648), Vector3.new(-0.1012, 0.8448, 0.5254), 0.733},
	{"Espinho_04", "Coluna2", Vector3.new(-0.0079, 5.4424, 0.1978), Vector3.new(0.0549, 0.8618, 0.5043), 0.650},
	{"Espinho_05", "Coluna1", Vector3.new(-0.0258, 5.4237, 0.7542), Vector3.new(0.2047, 0.8280, 0.5220), 0.573},
	{"Espinho_06", "Coluna1", Vector3.new(0.0166, 5.4121, 1.2949), Vector3.new(-0.1515, 0.7136, 0.6839), 0.499},
	{"Espinho_07", "Quadril", Vector3.new(-0.0231, 5.2348, 1.8521), Vector3.new(0.2453, 0.6488, 0.7204), 0.428},
	{"Espinho_08", "Quadril", Vector3.new(-0.0137, 4.9827, 2.4118), Vector3.new(0.1736, 0.6553, 0.7352), 0.360},
}
-- 16/11: o Import 3D solda todas as pecas: mover uma arrastava as outras -> tira as soldas ANTES de mover
for _, c in ipairs(imp:GetDescendants()) do
	if c:IsA("WeldConstraint") or c:IsA("JointInstance") or c:IsA("Constraint") then c:Destroy() end
end
for _, c in ipairs(imp:GetDescendants()) do if c:IsA("BasePart") then c.Anchored = true end end
local function limpar(p)
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Massless = true; p.CastShadow = false
	p.Transparency = 1
end
local r = {}
for _, nome in ipairs({"Linhas_1", "Linhas_2", "Linhas_3", "Linhas_4", "Linhas_6"}) do
	local m = imp:FindFirstChild(nome, true)
	if m then
		local velho = pasta:FindFirstChild(nome); if velho then velho:Destroy() end
		m.CFrame = m.CFrame + T
		limpar(m); m.Material = Enum.Material.Neon; m.Color = Color3.fromRGB(120, 200, 255)
		m.DoubleSided = true          -- as fitas sairam do Blender com a face para dentro (r6); sem isto nao aparecem
		for _, c in ipairs(m:GetChildren()) do if c:IsA("SurfaceAppearance") then c:Destroy() end end
		m.Parent = pasta
		table.insert(r, nome .. " ok")
	end
end
for _, e in ipairs(ESP) do
	local m = imp:FindFirstChild(e[1], true)
	if m then
		local velho = pasta:FindFirstChild(e[1]); if velho then velho:Destroy() end
		m.CFrame = m.CFrame + T
		limpar(m); m.Material = Enum.Material.Glass; m.Color = Color3.fromRGB(190, 230, 255); m.Reflectance = 0.15
		for _, c in ipairs(m:GetChildren()) do if c:IsA("SurfaceAppearance") then c:Destroy() end end
		local base = piv * e[3]
		local osso = wb[e[2]]
		m:SetAttribute("OssoEspinho", e[2])
		m:SetAttribute("OffsetOsso", osso.TransformedWorldCFrame:ToObjectSpace(m.CFrame))
		m:SetAttribute("BaseLocal", m.CFrame:PointToObjectSpace(base))
		m:SetAttribute("TamanhoCheio", m.Size)
		m:SetAttribute("Altura", e[5])
		m.Parent = pasta
		table.insert(r, string.format("%s osso=%s base->centro=%.2f", e[1], e[2], (m.Position - base).Magnitude))
	end
end
local NL = string.char(10)
return string.format("T=(%.3f,%.3f,%.3f) n=%d", T.X, T.Y, T.Z, n) .. NL .. table.concat(r, NL)

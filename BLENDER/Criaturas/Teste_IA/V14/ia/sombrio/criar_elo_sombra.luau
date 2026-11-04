-- criar_elo_sombra.luau (Studio, Edit) — cria/recria ReplicatedStorage.Combate_Dragoes.Elo_Sombra: o elo das Correntes
-- da Noite (VFXSombra v4, 04/11). Anel alongado COM FURO feito por CSG (estadio externo - estadio interno), eixo longo Y,
-- plano XY, espessura Z. Medidas = ELO do VFXSombra (comp 1,1 / larg 0,6 / fio 0,17). Sem colisao/consulta/sombra.
-- Reexecutavel: substitui o elo anterior (nao mexe em mais nada).
local comp, larg, fio = 1.1, 0.6, 0.17
local pasta = game:GetService("ReplicatedStorage"):WaitForChild("Combate_Dragoes")
local tmp = Instance.new("Folder"); tmp.Name = "_tmp_elo"; tmp.Parent = workspace
local function bloco(sz, cf, forma)
	local p = Instance.new("Part"); p.Anchored = true; p.Size = sz; p.CFrame = cf; p.Shape = forma or Enum.PartType.Block; p.Parent = tmp; return p
end
local DISCO = CFrame.Angles(0, math.rad(90), 0)                       -- cilindro do Roblox tem eixo X: gira para Z
local function estadio(w, t, folga)
	local reto = comp - larg                                          -- trecho reto entre as duas pontas redondas
	local partes = {bloco(Vector3.new(w, reto, t + folga), CFrame.new())}
	for _, sy in ipairs({-1, 1}) do table.insert(partes, bloco(Vector3.new(t + folga, w, w), CFrame.new(0, sy * reto / 2, 0) * DISCO, Enum.PartType.Cylinder)) end
	return partes
end
local ok, res = pcall(function()
	local fora = estadio(larg, fio, 0)
	local dentro = estadio(larg - 2 * fio, fio, 0.4)
	local cheio = fora[1]:UnionAsync({fora[2], fora[3]})
	cheio.Parent = tmp
	local buraco = dentro[1]:UnionAsync({dentro[2], dentro[3]})
	buraco.Parent = tmp
	local elo = cheio:SubtractAsync({buraco})
	return elo
end)
if not ok then tmp:Destroy(); error("CSG falhou: " .. tostring(res)) end
local elo = res
elo.Name = "Elo_Sombra"; elo.UsePartColor = true; elo.Color = Color3.fromRGB(20, 13, 28); elo.Material = Enum.Material.Metal
elo.Anchored = true; elo.CanCollide = false; elo.CanQuery = false; elo.CanTouch = false; elo.CastShadow = false
elo.CollisionFidelity = Enum.CollisionFidelity.Box; elo.RenderFidelity = Enum.RenderFidelity.Automatic; elo.SmoothingAngle = 30
elo:SetAttribute("Origem", "sombrio/criar_elo_sombra.luau (04/11)")
local velho = pasta:FindFirstChild("Elo_Sombra"); if velho then velho:Destroy() end
elo.CFrame = CFrame.new(); elo.Parent = pasta
tmp:Destroy()
return ("Elo_Sombra criado: tamanho %s"):format(tostring(elo.Size))

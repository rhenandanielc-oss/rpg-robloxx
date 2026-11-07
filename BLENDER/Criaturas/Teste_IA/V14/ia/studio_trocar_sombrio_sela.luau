-- studio_trocar_sombrio_sela.luau (Studio, modo Edit, DEPOIS do Import 3D de dragao_sombra/final/SB_Dragao_Sombrio_v6.glb)
-- (06/11) igual ao studio_trocar_sombrio_boca.luau, agora com a SELA (sela/sela_dragao.py): as pecas Silverwing_Sela* (o
-- importador pode separar por material) vem so com cor, sem textura. Guarda os antigos como <nome>_antesSela_<data>.
-- (05/11) Boca interna do Sombrio (boca_interior_sombrio.py): troca a MALHA de workspace.Sombrio e workspace.Sombrio_Guardiao
-- pela v5 (Corpo/Asas/Detalhes + nova Silverwing_Boca), mantendo TODOS os atributos, tags, pivo e a relacao pivo -> pes de
-- cada um. Os antigos vao para ServerStorage.Dragoes_Retirados (<nome>_antesBoca_<data>); o importado tambem (recuperavel).
-- Tudo-ou-nada: valida tudo antes de mexer em qualquer coisa.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage"); local CS = game:GetService("CollectionService")
local RENOMEIA = {["Silverwing"] = "Silverwing_Corpo", ["Silverwing.001"] = "Silverwing_Asas", ["Silverwing.002"] = "Silverwing_Detalhes"}
local importado
for _, m in ipairs(workspace:GetChildren()) do
	-- (05/11) o Silverwing (Fogo) tambem tem Silverwing_Boca: a importacao e a que ainda nao tem FormaRegional
	if m:IsA("Model") and m:FindFirstChild("Silverwing_Boca") and m:GetAttribute("FormaRegional") == nil then
		assert(not importado, "mais de uma importacao v5 no Workspace: deixe so uma")
		importado = m
	end
end
assert(importado, "importacao do SB_Dragao_Sombrio_v5.glb nao encontrada no Workspace (Import 3D primeiro)")
for _, d in ipairs(importado:GetDescendants()) do
	if d:IsA("MeshPart") and RENOMEIA[d.Name] then d.Name = RENOMEIA[d.Name] end
	if d:IsA("Bone") then assert(d.Name ~= "head" and d.Name ~= "mouth_lower", "GLB com nomes do Blender: reexporte com exportar_sombrio.py") end
end
local PECAS = {"Silverwing_Corpo", "Silverwing_Asas", "Silverwing_Detalhes", "Silverwing_Boca"}
local nSela = 0
for _, d in ipairs(importado:GetDescendants()) do if d:IsA("MeshPart") and d.Name:find("^Silverwing_Sela") then nSela += 1 end end
assert(nSela > 0, "importacao sem Silverwing_Sela (use o SB_Dragao_Sombrio_v6.glb)")
for _, n in ipairs(PECAS) do
	local p = importado:FindFirstChild(n, true); assert(p and p:IsA("MeshPart"), "falta MeshPart " .. n .. " na importacao")
	local sa = p:FindFirstChildOfClass("SurfaceAppearance")
	if not sa and n == "Silverwing_Boca" and p.TextureID ~= "" then   -- so cor (sem rugosidade): o importador poe em TextureID
		sa = Instance.new("SurfaceAppearance"); sa.ColorMap = p.TextureID; sa.Parent = p
	end
	assert(sa and sa.ColorMap ~= "", n .. " sem SurfaceAppearance com cor")
end
local alvos = {}
for _, n in ipairs({"Sombrio", "Sombrio_Guardiao"}) do
	local v = workspace:FindFirstChild(n); assert(v and v.PrimaryPart, "workspace." .. n .. " nao encontrado")
	for _, c in ipairs(v:GetChildren()) do assert(not c.Name:find("^Silverwing_Sela"), n .. " ja tem a sela (troca ja aplicada)") end
	table.insert(alvos, v)
end
local function pes(mod)
	local y = math.huge
	for _, b in ipairs(mod:GetDescendants()) do if b:IsA("Bone") and b.Name:find("toes_tip") then y = math.min(y, b.WorldPosition.Y) end end
	assert(y < math.huge, "sem ossos toes_tip em " .. mod.Name); return y
end
local guard = SS:FindFirstChild("Dragoes_Retirados") or Instance.new("Folder"); guard.Name = "Dragoes_Retirados"; guard.Parent = SS
local data = os.date("!%Y%m%d_%H%M%S"); local res = {}
for _, velho in ipairs(alvos) do
	local m = importado:Clone()
	m:ScaleTo(velho:GetScale())
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then d.Anchored = true end
		if d:IsA("MeshPart") then
			d.DoubleSided = true
			local ant = velho:FindFirstChild(d.Name)                    -- mesmas regras de colisao/sombra da peca antiga
			if ant and ant:IsA("BasePart") then
				d.CanCollide, d.CanQuery, d.CanTouch, d.CastShadow, d.CollisionGroup = ant.CanCollide, ant.CanQuery, ant.CanTouch, ant.CastShadow, ant.CollisionGroup
			elseif d.Name:find("^Silverwing_Sela") then
				d.CanCollide, d.CanQuery, d.CanTouch, d.CastShadow = false, false, false, true   -- sela: nao colide, faz sombra
			elseif d.Name == "Silverwing_Boca" then
				d.CanCollide, d.CanQuery, d.CanTouch, d.CastShadow = false, false, false, false   -- interior: nao colide nem projeta sombra
			end
		end
	end
	local rp = m:FindFirstChild("RootPart")
	if rp then rp.CanCollide = false; rp.CanQuery = false; rp.CanTouch = false; rp.CastShadow = false end
	m.ModelStreamingMode = velho.ModelStreamingMode
	for k, v in pairs(velho:GetAttributes()) do if not k:find("^RBX_") then m:SetAttribute(k, v) end end
	m:SetAttribute("Versao", "Sombrio v11 (06/11: sela + arreio, base comum; cores provisorias do tema Sombra)")
	-- com a sela o topo do assento fica ~3,1 studs acima do osso Coluna2: o cavaleiro (HRP) vai a 3,6 (antes 1,8 = dentro da sela)
	m:SetAttribute("AssentoAcima", 3.6)
	for _, t in ipairs(CS:GetTags(velho)) do CS:AddTag(m, t) end
	for _, c in ipairs(velho:GetChildren()) do                         -- extras que a importacao nao traz (prompts, scripts...)
		if not c:IsA("BasePart") and c.Name ~= "InitialPoses" and not m:FindFirstChild(c.Name) then c:Clone().Parent = m end
	end
	-- pivo -> pes igual ao do antigo (montaria e IA movem por PivotTo contando com essa altura)
	local acima = velho:GetPivot().Position.Y - pes(velho)
	local prim = m.PrimaryPart; assert(prim, "importacao sem PrimaryPart")
	prim.PivotOffset = CFrame.new(0, (pes(m) + acima) - prim.Position.Y, 0)
	m:PivotTo(velho:GetPivot())
	local nome = velho.Name
	velho.Name = nome .. "_antesSela_" .. data; velho.Parent = guard
	m.Name = nome; m.Parent = workspace
	table.insert(res, ("%s em %s (pes %.2f abaixo do pivo)"):format(nome, tostring(m:GetPivot().Position), acima))
end
importado.Name = "Sombrio_Importado_v6_" .. data; importado.Parent = guard
return "trocado: " .. table.concat(res, " | ")

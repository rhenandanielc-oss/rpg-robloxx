-- montar_idades_v1.luau (EDIT, Teste-animacoes, 19/11/2026) - guarda as malhas por idade do Lobo Artico para a troca no jogo.
-- Antes: o usuario importa (Import 3D) os GLB de idades_v1/export/: CR_LoboArtico_Filhote / _Jovem / _PreAdulto / _Anciao.
-- Faz, sem apagar nada do lobo atual:
--   1) ServerStorage.LoboArtico_Idades.Adulto = copia das MeshParts LOW_* do lobo atual + CFrame de repouso de cada osso;
--   2) para cada import achado no Workspace: MeshParts renomeadas pelo papel (Import 3D usa o nome da MALHA), SurfaceAppearance
--      igual ao Adulto (MetalnessMap vazio = sem pelo cromado; mascara/tinta de emissao do Uivo copiadas), mesmas propriedades
--      fisicas do Adulto; tabela de ossos (nome -> CFrame local) num atributo; o import vai para LoboArtico_Idades.<Idade>.
-- Retorna um resumo. Rodar de novo e seguro (substitui so a pasta da idade).
local SS = game:GetService("ServerStorage")
local HS = game:GetService("HttpService")
local lobo = workspace.Teste_LoboArtico.LoboArtico_LOW
local raiz = lobo:FindFirstChild("RootPart")
local pasta = SS:FindFirstChild("LoboArtico_Idades") or Instance.new("Folder"); pasta.Name = "LoboArtico_Idades"; pasta.Parent = SS
local PAPEIS = {"LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"}
local out = {}

local function ossos(m)
	local rp = m:FindFirstChild("RootPart") or m.PrimaryPart
	local t = {}
	for _, b in ipairs(rp:GetDescendants()) do if b:IsA("Bone") then t[b.Name] = {b.CFrame:GetComponents()} end end
	return t, rp
end
local function partes(m)
	local t = {}
	for _, p in ipairs(m:GetDescendants()) do if p:IsA("MeshPart") then table.insert(t, p) end end
	return t
end

-- 1) Adulto (o lobo atual)
local adulto = pasta:FindFirstChild("Adulto")
if not adulto then
	adulto = Instance.new("Model"); adulto.Name = "Adulto"
	local tb, rp = ossos(lobo)
	for _, n in ipairs(PAPEIS) do
		local p = lobo:FindFirstChild(n)
		if p then local c = p:Clone(); c:SetAttribute("Rel", HS:JSONEncode({rp.CFrame:ToObjectSpace(p.CFrame):GetComponents()})); c.Parent = adulto end
	end
	adulto:SetAttribute("Ossos", HS:JSONEncode(tb)); adulto.Parent = pasta
	table.insert(out, "Adulto guardado (" .. #adulto:GetChildren() .. " partes)")
end
local saAdulto = lobo.LOW_Corpo:FindFirstChildOfClass("SurfaceAppearance")
local saCabA = lobo.LOW_Cabeca:FindFirstChildOfClass("SurfaceAppearance")

-- 2) imports
for _, idade in ipairs({"Filhote", "Jovem", "PreAdulto", "Anciao"}) do
	local imp = workspace:FindFirstChild("CR_LoboArtico_" .. idade)
	if not imp then table.insert(out, idade .. ": import nao achado"); continue end
	local tb, rp = ossos(imp)
	local m = Instance.new("Model"); m.Name = idade
	local ps = partes(imp)
	-- papel pelo numero de triangulos/vertices nao e exposto: usa o nome (malha) e, se nao bater, o tamanho relativo
	for _, p in ipairs(ps) do
		local nome
		for _, n in ipairs(PAPEIS) do if p.Name:find(n:sub(5), 1, true) then nome = n end end
		if nome then
			local ref = lobo:FindFirstChild(nome)
			local c = p:Clone(); c.Name = nome
			if ref then
				c.Anchored = ref.Anchored; c.CanCollide = ref.CanCollide; c.CanTouch = ref.CanTouch; c.CanQuery = ref.CanQuery
				c.Massless = ref.Massless; c.CastShadow = ref.CastShadow
				pcall(function() c.CollisionFidelity = ref.CollisionFidelity end)
			end
			local sa = c:FindFirstChildOfClass("SurfaceAppearance")
			local saRef = (nome == "LOW_Corpo" and saAdulto) or (nome == "LOW_Cabeca" and saCabA) or nil
			if sa then
				sa:SetAttribute("MetalnessMap_Importado", sa.MetalnessMap); sa.MetalnessMap = ""
				if saRef then
					for _, prop in ipairs({"EmissiveMaskContent", "EmissiveTint", "EmissiveStrength", "AlphaMode"}) do
						pcall(function() sa[prop] = saRef[prop] end)
					end
				end
			end
			c:SetAttribute("Rel", HS:JSONEncode({rp.CFrame:ToObjectSpace(p.CFrame):GetComponents()}))
			c.Parent = m
		end
	end
	m:SetAttribute("Ossos", HS:JSONEncode(tb))
	local velho = pasta:FindFirstChild(idade); if velho then velho:Destroy() end
	m.Parent = pasta
	imp.Parent = SS                                   -- o import original fica guardado (nada apagado)
	imp.Name = "Import_" .. imp.Name
	local nomes = {}; for _, c in ipairs(m:GetChildren()) do table.insert(nomes, c.Name) end
	table.insert(out, idade .. ": " .. #ps .. " MeshParts -> [" .. table.concat(nomes, ",") .. "], " .. (function() local k = 0; for _ in pairs(tb) do k += 1 end; return k end)() .. " ossos")
end
return table.concat(out, "\n")

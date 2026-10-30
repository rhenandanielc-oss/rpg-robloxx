-- studio_trocar_silverwing.luau (rodar no Studio, modo Edit, DEPOIS do Import 3D do Silverwing_Glacial_v2.glb)
-- Troca o Silverwing/Guardiao pela importacao nova (pesos corrigidos + animacoes proprias), preservando posicao,
-- escala (17,5), atributos e nomes de ossos usados pelos sistemas. Versao anterior vai para ServerStorage (recuperavel).
local SS, RS = game:GetService("ServerStorage"), game:GetService("ReplicatedStorage")
local MAPA = {head = "Cabeca", hips = "Quadril", spine_1 = "Coluna2", mouth_lower = "Mandibula", spine_4 = "Pescoco4",
	spine_2 = "Pescoco2", tail_3 = "Cauda3", wing_2_l = "AsaE_2", wing_2_r = "AsaD_2"}
local novo = workspace:FindFirstChild("Scene")
assert(novo and novo:FindFirstChildWhichIsA("MeshPart"), "importacao 'Scene' nao encontrada no Workspace")
-- pode haver varias pastas "Scene" (importacoes anteriores): usa a que tem o clipe mais novo (Mordida_Aerea)
-- Drake5 (30/10): os clipes ja chegam pela ponte JSON (V14\montar_kfs_json.luau); a importacao traz so 4 clipes de
-- previa. Se nao houver o pacote completo (com Silverwing_Mordida_Aerea), troca SO o modelo e mantem os clipes atuais.
local saves
local animsaves = SS:FindFirstChild("RBX_ANIMSAVES")
for _, f in ipairs(animsaves and animsaves:GetChildren() or {}) do if f.Name == "Scene" and f:FindFirstChild("Silverwing_Mordida_Aerea") then saves = f end end
local guard = SS:FindFirstChild("Dragoes_Retirados") or Instance.new("Folder"); guard.Name = "Dragoes_Retirados"; guard.Parent = SS
local log = {}
-- 1) animacoes: as antigas (molde) vao para a subpasta Antigas_M2M; as novas entram com ossos renomeados
local pasta = RS.Animacoes_Silverwing
if saves then
local antigas = pasta:FindFirstChild("Antigas_M2M") or Instance.new("Folder"); antigas.Name = "Antigas_M2M"; antigas.Parent = pasta
local anteriores = pasta:FindFirstChild("Anteriores") or Instance.new("Folder"); anteriores.Name = "Anteriores"; anteriores.Parent = pasta
for _, k in ipairs(pasta:GetChildren()) do
	if k:IsA("KeyframeSequence") then
		local velho = anteriores:FindFirstChild(k.Name); if velho then velho:Destroy() end     -- guarda so a ultima versao
		k.Parent = anteriores
	end
end
local n = 0
for _, k in ipairs(saves:GetChildren()) do
	if k:IsA("KeyframeSequence") then
		local c = k:Clone()
		for _, p in ipairs(c:GetDescendants()) do if p:IsA("Pose") and MAPA[p.Name] then p.Name = MAPA[p.Name] end end
		c.Loop = not (c.Name:find("Decolagem") or c.Name:find("Pouso") or c.Name:find("Parada") or c.Name:find("Abaixar") or c.Name:find("Levantar") or c.Name:find("Mordida"))
		c.Parent = pasta; n += 1
	end
end
table.insert(log, "animacoes novas: " .. n)
else
	table.insert(log, "animacoes: mantidas (ponte JSON); importacao sem pacote completo de clipes")
end
-- 2) modelos: novo herda posicao/atributos; o anterior vai para ServerStorage
local function preparar(m)
	m:ScaleTo(17.5)
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("Bone") and MAPA[d.Name] then d.Name = MAPA[d.Name] end
		if d:IsA("BasePart") then d.Anchored = true end
	end
	local mp = m:FindFirstChildWhichIsA("MeshPart"); mp.Name = "Silverwing_Malha"
	-- o Roblox so desenha a frente das faces; a malha do Meshy tem trechos com a normal para dentro (base da cauda,
	-- membranas) que sumiam ("cauda faltando um pedaco"). DoubleSided desenha os dois lados.
	mp.DoubleSided = true
end
local function trocar(nomeAntigo, base)
	local velho = workspace:FindFirstChild(nomeAntigo); if not velho then return end
	local m = base:Clone(); preparar(m); m.Name = nomeAntigo
	for k, v in pairs(velho:GetAttributes()) do if not k:find("^RBX_") then m:SetAttribute(k, v) end end
	m:SetAttribute("DonoUserId", nil); m:SetAttribute("Controlador", nil); m:SetAttribute("Cavaleiro", nil)
	m:SetAttribute("Versao", "Drake5 (asas 1,5x com dobra propria no chao, corrida pesada, voo mais vivo, clipes de comportamento da IA)")
	if velho:GetAttribute("DonoUserId") then m:SetAttribute("DonoUserId", velho:GetAttribute("DonoUserId")) end
	-- mesma base apoiada no chao e mesmo rumo
	local cfV, szV = velho:GetBoundingBox()
	m:PivotTo(velho:GetPivot())
	local cfN, szN = m:GetBoundingBox()
	m:PivotTo(m:GetPivot() + Vector3.new(0, (cfV.Position.Y - szV.Y / 2) - (cfN.Position.Y - szN.Y / 2), 0))
	local ant = guard:FindFirstChild(nomeAntigo .. "_anterior"); if ant then ant:Destroy() end   -- 1 versao recuperavel
	velho.Name = nomeAntigo .. "_anterior"; velho.Parent = guard
	m.Parent = workspace
	table.insert(log, nomeAntigo .. " trocado; antigo em ServerStorage.Dragoes_Retirados." .. velho.Name)
end
trocar("Silverwing", novo)
trocar("Silverwing_Guardiao", novo)
novo:Destroy()
if saves then saves.Name = "Scene_usada" end                          -- a proxima importacao nao confunde com esta
local aux = workspace:FindFirstChild("AuxScene"); if aux and #aux:GetChildren() == 0 then aux:Destroy() end
return table.concat(log, "\n")

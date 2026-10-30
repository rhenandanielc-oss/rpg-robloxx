-- studio_trocar_cr.luau (Studio, modo Edit, DEPOIS do Import 3D de CR_Dragao_Roblox.glb): troca os dois Silverwing
-- (montaria e guardiao) pelo CR_Dragao. Mesmo esqueleto/nomes de ossos => IA, combate, montaria e sons continuam.
-- Seguranca: backup UNICO de todos os clipes atuais (ServerStorage.Backup_Clipes_Silverwing_Drake4) e dos modelos
-- (ServerStorage.Dragoes_Retirados, com sufixo de data; nada antigo e apagado). O importado deve se chamar "Scene".
local SS, RS = game:GetService("ServerStorage"), game:GetService("ReplicatedStorage")
local MAPA = {head = "Cabeca", hips = "Quadril", spine_1 = "Coluna2", mouth_lower = "Mandibula", spine_4 = "Pescoco4",
	spine_2 = "Pescoco2", tail_3 = "Cauda3", wing_2_l = "AsaE_2", wing_2_r = "AsaD_2"}
local novo
for _, m in ipairs(workspace:GetChildren()) do
	if m.Name == "Scene" and m:FindFirstChild("Silverwing_Corpo", true) then novo = m end
end
assert(novo, "importacao 'Scene' com Silverwing_Corpo nao encontrada no Workspace")
local log = {}
-- 1) backup unico dos clipes atuais (KeyframeSequences do Silverwing Drake4)
local pasta = RS.Animacoes_Silverwing
if not SS:FindFirstChild("Backup_Clipes_Silverwing_Drake4") then
	local b = Instance.new("Folder"); b.Name = "Backup_Clipes_Silverwing_Drake4"
	local n = 0
	for _, k in ipairs(pasta:GetChildren()) do if k:IsA("KeyframeSequence") then k:Clone().Parent = b; n += 1 end end
	b.Parent = SS; table.insert(log, "backup de " .. n .. " clipes em ServerStorage.Backup_Clipes_Silverwing_Drake4")
end
-- 2) modelos
local guard = SS:FindFirstChild("Dragoes_Retirados") or Instance.new("Folder"); guard.Name = "Dragoes_Retirados"; guard.Parent = SS
local function preparar(m)
	m:ScaleTo(17.5)
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("Bone") and MAPA[d.Name] then d.Name = MAPA[d.Name] end
		if d:IsA("BasePart") then d.Anchored = true end
		if d:IsA("MeshPart") then d.DoubleSided = true end      -- membranas sem espessura e interior da boca
	end
end
local carimbo = os.date("!%Y%m%d_%H%M%S")
local function trocar(nomeAntigo)
	local velho = workspace:FindFirstChild(nomeAntigo); if not velho then return end
	local m = novo:Clone(); preparar(m); m.Name = nomeAntigo
	for k, v in pairs(velho:GetAttributes()) do if not k:find("^RBX_") then m:SetAttribute(k, v) end end
	m:SetAttribute("Versao", "CR_Dragao v1 (Meshy texto + rosto refinado: olho, boca real, dobra das asas)")
	local cfV, szV = velho:GetBoundingBox()
	m:PivotTo(velho:GetPivot())
	local cfN, szN = m:GetBoundingBox()
	m:PivotTo(m:GetPivot() + Vector3.new(0, (cfV.Position.Y - szV.Y / 2) - (cfN.Position.Y - szN.Y / 2), 0))
	velho.Name = nomeAntigo .. "_Drake4_" .. carimbo; velho.Parent = guard
	m.Parent = workspace
	table.insert(log, nomeAntigo .. " trocado; anterior em ServerStorage.Dragoes_Retirados." .. velho.Name)
end
trocar("Silverwing")
trocar("Silverwing_Guardiao")
novo:Destroy()
return table.concat(log, "\n")

-- criar_treino_sol.luau (Edit, Cerbero-testes, 26/11): bonecos de treino do Sol Infernal + parede + RemoteEvents.
-- Cerbero em (0,0,60) olhando para -Z. Bonecos: parado a ~38 studs, andando de lado, e um atras de uma parede.
local RS = game:GetService("ReplicatedStorage")
local pasta = RS:FindFirstChild("SolInfernal") or Instance.new("Folder")
pasta.Name = "SolInfernal"; pasta.Parent = RS
for _, n in ipairs({"Pedido", "Explodiu", "Queima"}) do
	if not pasta:FindFirstChild(n) then local r = Instance.new("RemoteEvent"); r.Name = n; r.Parent = pasta end
end
local velho = workspace:FindFirstChild("Treino_SolInfernal"); if velho then velho:Destroy() end
local treino = Instance.new("Folder"); treino.Name = "Treino_SolInfernal"
treino:SetAttribute("LevarJogador", true)
local function boneco(nome, pos, cor)
	local m = Instance.new("Model"); m.Name = nome
	local raiz = Instance.new("Part"); raiz.Name = "HumanoidRootPart"; raiz.Size = Vector3.new(4, 6, 2)
	raiz.Anchored = true; raiz.Color = cor; raiz.Material = Enum.Material.SmoothPlastic; raiz.CFrame = CFrame.new(pos + Vector3.new(0, 3, 0)); raiz.Parent = m
	local cab = Instance.new("Part"); cab.Name = "Head"; cab.Size = Vector3.new(2, 2, 2); cab.Anchored = true; cab.Color = cor
	cab.CFrame = CFrame.new(pos + Vector3.new(0, 7, 0)); cab.Parent = m
	local h = Instance.new("Humanoid"); h.MaxHealth = 200; h.Health = 200; h.RequiresNeck = false
	h.HealthDisplayDistance = 200; h.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.Viewer; h.Parent = m
	m.PrimaryPart = raiz; m.Parent = treino
	return m
end
boneco("Boneco_Parado", Vector3.new(0, 0, 22), Color3.fromRGB(200, 200, 210))
boneco("Boneco_Andando", Vector3.new(0, 0, 30), Color3.fromRGB(120, 170, 230))
local atras = boneco("Boneco_AtrasParede", Vector3.new(-30, 0, 26), Color3.fromRGB(230, 200, 120))
boneco("Boneco_Vizinho", Vector3.new(7, 0, 18), Color3.fromRGB(170, 220, 160))   -- perto do parado: recebe so a explosao
-- parede entre a boca do Cerbero e o boneco de tras
-- origem da bola depois de o Cerbero virar para o boneco de tras: RootPart (0,0,60) + 22 studs na direcao + 18 de altura
local alvo = atras:GetPivot().Position
local dirC = Vector3.new(alvo.X, 0, alvo.Z - 60).Unit
local boca = Vector3.new(0, 18, 60) + dirC * 22
local meio = boca:Lerp(alvo, 0.5)
local dir = Vector3.new(alvo.X - boca.X, 0, alvo.Z - boca.Z).Unit
local parede = Instance.new("Part"); parede.Name = "Parede_Teste"; parede.Anchored = true
parede.Size = Vector3.new(18, 22, 2); parede.Color = Color3.fromRGB(90, 85, 80); parede.Material = Enum.Material.Slate
parede.CFrame = CFrame.lookAt(Vector3.new(meio.X, 11, meio.Z), Vector3.new(meio.X, 11, meio.Z) + dir)
parede.Parent = treino
treino.Parent = workspace
return "treino ok"

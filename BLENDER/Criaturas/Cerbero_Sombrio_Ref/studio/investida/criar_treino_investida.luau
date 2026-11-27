-- criar_treino_investida.luau (Edit, Cerbero-testes, 26/11): faixas de teste da Investida + RemoteEvents.
-- Cada faixa comeca em z = 60 (Cerbero olhando para -Z) e o alvo fica em z = 22. Bonecos com 300 de vida.
-- Portes pela ALTURA (cernelha do Cerbero 13,72; limite pequeno 6,86): pequeno 6,4 | medio 13,0 | grande 19,2.
local RS = game:GetService("ReplicatedStorage")
local pasta = RS:FindFirstChild("InvestidaSombria") or Instance.new("Folder")
pasta.Name = "InvestidaSombria"; pasta.Parent = RS
for _, n in ipairs({"Pedido", "Direcao", "Efeito"}) do
	if not pasta:FindFirstChild(n) then local r = Instance.new("RemoteEvent"); r.Name = n; r.Parent = pasta end
end
local velho = workspace:FindFirstChild("Treino_Investida"); if velho then velho:Destroy() end
local treino = Instance.new("Folder"); treino.Name = "Treino_Investida"
treino:SetAttribute("Faixas", "Pequeno x=80 | Medio x=110 | Grande x=140 | Parede x=170 | Rastro x=200, boneco espera em x=215 (inicio z=60, olhando -Z)")
local function boneco(nome, pos, tam, cor)
	local m = Instance.new("Model"); m.Name = nome
	local raiz = Instance.new("Part"); raiz.Name = "HumanoidRootPart"; raiz.Size = tam
	raiz.Anchored = true; raiz.Color = cor; raiz.Material = Enum.Material.SmoothPlastic
	raiz.CFrame = CFrame.new(pos + Vector3.new(0, tam.Y / 2 - 0.6, 0)); raiz.Parent = m
	local cab = Instance.new("Part"); cab.Name = "Head"; cab.Size = Vector3.new(1.2, 1.2, 1.2); cab.Anchored = true; cab.Color = cor
	cab.CFrame = CFrame.new(pos + Vector3.new(0, tam.Y - 1.4, 0)); cab.Parent = m   -- dentro da caixa: altura do modelo = tam.Y
	local h = Instance.new("Humanoid"); h.MaxHealth = 300; h.Health = 300; h.RequiresNeck = false; h.WalkSpeed = 16
	h.HealthDisplayDistance = 250; h.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.Viewer; h.Parent = m
	m.PrimaryPart = raiz; m.Parent = treino
	return m
end
boneco("Alvo_Pequeno", Vector3.new(80, 0, 22), Vector3.new(8, 6.4, 3.6), Color3.fromRGB(200, 200, 210))
boneco("Alvo_Medio", Vector3.new(110, 0, 22), Vector3.new(9, 13, 10), Color3.fromRGB(120, 170, 230))
boneco("Alvo_Grande", Vector3.new(140, 0, 22), Vector3.new(10, 19.2, 14), Color3.fromRGB(230, 200, 120))
local parede = Instance.new("Part"); parede.Name = "Parede_Investida"; parede.Anchored = true
parede.Size = Vector3.new(20, 18, 2); parede.Color = Color3.fromRGB(90, 85, 80); parede.Material = Enum.Material.Slate
parede.CFrame = CFrame.new(170, 9, 32); parede.Parent = treino
boneco("Boneco_CruzaRastro", Vector3.new(215, 0, 40), Vector3.new(3, 6, 2), Color3.fromRGB(170, 220, 160))
treino.Parent = workspace
return "treino da investida ok"

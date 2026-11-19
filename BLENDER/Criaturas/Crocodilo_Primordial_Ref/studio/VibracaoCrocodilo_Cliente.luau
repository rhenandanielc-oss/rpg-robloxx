-- VibracaoCrocodilo_Cliente (LocalScript em StarterPlayerScripts) - 19/11 [PROPOSTA], so o place de teste do Crocodilo.
-- Passiva Sentido de Vibracao: o SERVIDOR decide quem o crocodilo percebeu e manda as posicoes so ao dono. Aqui so se
-- desenha uma ondulacao discreta (anel fino que abre e some) no chao/agua onde a criatura se mexe. Nada de dano/estado.
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local Rem = RS:WaitForChild("Crocodilo_Vibracao")
local pasta = Instance.new("Folder"); pasta.Name = "Vibracao_Local"; pasta.Parent = workspace

local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain}
local function nivel(p)                                     -- superficie da agua ou chao abaixo do ponto
	local r = workspace:Raycast(p + Vector3.new(0, 6, 0), Vector3.new(0, -40, 0), rp)
	return r and r.Position.Y or (p.Y - 2.5)
end
local function anel(pos)
	local a = Instance.new("Part"); a.Name = "Ondulacao"; a.Anchored = true; a.CanCollide = false; a.CanQuery = false; a.CanTouch = false
	a.CastShadow = false; a.Shape = Enum.PartType.Cylinder; a.Material = Enum.Material.Neon
	a.Color = Color3.fromRGB(170, 215, 225); a.Transparency = 0.55; a.Size = Vector3.new(0.05, 1.5, 1.5)
	a.CFrame = CFrame.new(pos.X, nivel(pos) + 0.08, pos.Z) * CFrame.Angles(0, 0, math.rad(90)); a.Parent = pasta
	TS:Create(a, TweenInfo.new(0.9, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.new(0.05, 7, 7), Transparency = 1}):Play()
	game:GetService("Debris"):AddItem(a, 1)
end
local ultimo = {}
Rem.OnClientEvent:Connect(function(posicoes)
	local agora = os.clock()
	for i, p in ipairs(posicoes) do
		local k = math.floor(p.X / 4) .. ":" .. math.floor(p.Z / 4)   -- no maximo 1 anel a cada 0,5 s por lugar
		if not ultimo[k] or agora - ultimo[k] > 0.5 then ultimo[k] = agora; anel(p) end
	end
end)

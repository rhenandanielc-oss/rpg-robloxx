-- OndulacaoAgua_Cliente (LocalScript) — vida selvagem, 11/11/2026, TESTE (NAO_APROVADO).
-- Ondulacao pequena na agua quando o FOCINHO de um dragao que esta bebendo (atributo EstadoIA = "Drink", definido pelo
-- IA_Dragao.Cerebro) toca a superficie. O evento nasce do contato real (raio do focinho ate a agua do Terrain), nao de um
-- tempo fixo: fica sincronizado com o gole do clipe Beber em qualquer margem.
-- Custo: so dragoes a ate DIST da camera, checagem a cada 0,1 s, no maximo MAX_ANEIS aneis vivos (PC e celular).
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local DIST, TOQUE, SOLTA, INTERVALO, MAX_ANEIS = 250, 1.2, 1.8, 0.35, 12   -- TOQUE/SOLTA: altura da ponta do osso (a malha da boca fica ~1 abaixo dela)
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.IgnoreWater = false
local vivos, ultimo, perto = 0, {}, {}
local function anel(pos, atraso, tamFinal)
	if vivos >= MAX_ANEIS then return end
	vivos += 1
	task.delay(atraso, function()
		local p = Instance.new("Part"); p.Name = "OndulacaoAgua"; p.Shape = Enum.PartType.Cylinder; p.Anchored = true
		p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Material = Enum.Material.SmoothPlastic; p.Color = Color3.fromRGB(225, 240, 255); p.Transparency = 0.45
		p.Size = Vector3.new(0.08, 1.5, 1.5); p.CFrame = CFrame.new(pos + Vector3.new(0, 0.06, 0)) * CFrame.Angles(0, 0, math.rad(90))
		p.Parent = workspace.CurrentCamera
		local tw = TweenService:Create(p, TweenInfo.new(1.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.new(0.08, tamFinal, tamFinal), Transparency = 1})
		tw.Completed:Connect(function() p:Destroy(); vivos -= 1 end); tw:Play()
	end)
end
local acc = 0
RunService.Heartbeat:Connect(function(dt)
	acc += dt; if acc < 0.1 then return end; acc = 0
	local cam = workspace.CurrentCamera; if not cam then return end
	local cp = cam.CFrame.Position
	rp.FilterDescendantsInstances = {workspace.Terrain}
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("EstadoIA") == "Drink" and m.PrimaryPart and (m.PrimaryPart.Position - cp).Magnitude < DIST then
			local b = m:FindFirstChild("mouth_upper_tip", true) or m:FindFirstChild("Cabeca", true)
			if b and b:IsA("Bone") then
				local bp = b.TransformedWorldCFrame.Position
				local h = workspace:Raycast(bp + Vector3.new(0, 4, 0), Vector3.new(0, -16, 0), rp)
				local agua = h and h.Material == Enum.Material.Water; local alt = h and (bp.Y - h.Position.Y) or 99
				if agua and alt < TOQUE and not perto[m] and os.clock() - (ultimo[m] or 0) > INTERVALO then
					ultimo[m] = os.clock(); perto[m] = true; anel(h.Position, 0, 12); anel(h.Position, 0.25, 8)
				elseif not agua or alt > SOLTA then perto[m] = nil end
			end
		else perto[m] = nil end
	end
end)

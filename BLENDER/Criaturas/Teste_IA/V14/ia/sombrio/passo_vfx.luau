-- ===== PASSO SOMBRIO (04/11): o dragao se desfaz em breu e reaparece adiante ==========================================
-- sumir: o corpo (e o cavaleiro) some aos poucos (LocalTransparencyModifier, so no cliente), estouro de breu na saida e
-- um rastro de fumaca escura ao longo do caminho; surgir: estouro na chegada e o corpo volta aos poucos. Sem luz.
local function partesVisiveis(m)
	local l = {}
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then table.insert(l, d) end end
	for _, p in ipairs(Players:GetPlayers()) do                         -- quem esta montado some junto
		local ch = p.Character; local hum = ch and ch:FindFirstChildOfClass("Humanoid")
		local sela = hum and hum.SeatPart
		local montado = ch and (sela and sela:IsDescendantOf(m) or (ch:GetAttribute("MontadoEm") == m.Name))
		if not montado and ch and ch:FindFirstChild("HumanoidRootPart") then
			for _, w in ipairs(ch.HumanoidRootPart:GetJoints()) do local o = w.Part0 == ch.HumanoidRootPart and w.Part1 or w.Part0; if o and o:IsDescendantOf(m) then montado = true end end
		end
		if montado then for _, d in ipairs(ch:GetDescendants()) do if d:IsA("BasePart") or d:IsA("Decal") then table.insert(l, d) end end end
	end
	return l
end
local function desvanecer(lista, de, ate, dur)
	local t0 = os.clock(); local c
	c = RunService.RenderStepped:Connect(function()
		local k = math.min(1, (os.clock() - t0) / dur); local v = de + (ate - de) * (k * k * (3 - 2 * k))
		for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = v end end
		if k >= 1 then c:Disconnect() end
	end)
end
local function estouroBreu(pos, f, escala)
	if f <= 0 then return end
	local a = ancora(pos); Debris:AddItem(a, 2.2)
	emissor(a, flipFumaca({Color = seq({PRETO, BREU, C3(55, 20, 95)}), LightEmission = 0.05, LightInfluence = 0.5, Size = ns(0, 4 * escala, 1, 14 * escala),
		Transparency = ns(0, 0.35, 0.5, 0.55, 1, 1), Lifetime = NumberRange.new(0.7, 1.1), Speed = NumberRange.new(14, 26), Drag = 3,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60), SpreadAngle = Vector2.new(180, 180), Rate = 0})):Emit(math.max(6, math.floor(26 * f)))
	emissor(a, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = seq({PRETO, C3(90, 35, 160)}), LightEmission = 0.1,
		LightInfluence = 0.4, Size = ns(0, 0.8 * escala, 1, 0.2), Squash = ns(0, 1.2, 1, 0.6), Transparency = ns(0, 0.4, 1, 1),
		Lifetime = NumberRange.new(0.35, 0.55), Speed = NumberRange.new(40, 70), Drag = 4, SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.max(4, math.floor(18 * f)))
end
local function passoEvento(m, d, f)
	local escala = math.clamp((m:GetAttribute("CorpoRaio") or 8) / 8, 0.5, 2)
	if d.fase == "sumir" then
		local lista = partesVisiveis(m); local dur = d.tempo or 0.3
		desvanecer(lista, 0, 1, dur)
		task.delay(dur + 0.05, function() for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = 1 end end end)
		estouroBreu(d.de, f, escala)
		if f > 0 and d.de and d.ate then                                 -- rastro de breu pelo caminho (sombra que corre)
			local v = d.ate - d.de; local n = math.clamp(math.floor(v.Magnitude / 6), 2, 16)
			for i = 1, n do
				task.delay(dur * 0.6 + (i / n) * 0.14, function()
					local a = ancora(d.de + v * (i / n)); Debris:AddItem(a, 1.6)
					emissor(a, flipFumaca({Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 5 * escala, 1, 9 * escala),
						Transparency = ns(0, 0.45, 0.4, 0.6, 1, 1), Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(1, 4), Drag = 2,
						Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30), SpreadAngle = Vector2.new(180, 180), Rate = 0})):Emit(3)
				end)
			end
		end
	elseif d.fase == "surgir" then
		estouroBreu(d.pos, f, escala)
		local lista = partesVisiveis(m)
		desvanecer(lista, 1, 0, d.tempo or 0.35)
		task.delay((d.tempo or 0.35) + 0.1, function() for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = 0 end end end)
	end
end


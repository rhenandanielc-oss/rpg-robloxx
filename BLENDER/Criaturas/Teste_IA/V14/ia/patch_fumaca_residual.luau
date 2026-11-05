-- patch_fumaca_residual.luau (Studio, Edit) — fumaca residual ao fim do sopro, todos os dragoes (05/11).
-- Gerado por sombrio/gerar_patch_fumaca_residual.py. Backup unico ServerStorage.Backup_Fumaca_Residual_2026-11-05.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage"); local V = game:GetService("ReplicatedStorage").Combate_Dragoes.VFXCombate
local src = V.Source:gsub("\r\n", "\n")
if src:find("PATCH_FUMACA_RESIDUAL", 1, true) then return "ja aplicado" end
do local a, b = [======[-- ===== despacho ==================================================================================================
]======], [======[-- ===== fumaca residual ao fim do sopro (PATCH_FUMACA_RESIDUAL, 05/11) ===========================================
-- Depois que o jato para, um resto do elemento escapa da boca e das duas narinas por ~2,5 s, diminuindo aos poucos
-- (vale para todos os dragoes; os ossos sao os do esqueleto comum). So cosmetico, no cliente; pesa pouco (3 emissores).
local RESIDUO = {
	Sombra = {cor = {C3(34, 24, 46), C3(12, 9, 18)}, luzI = 0.55, sobe = 1.1, alfa = 0.5, tex = FB.fumaca},
	Fogo = {cor = {C3(96, 86, 80), C3(52, 49, 48)}, luzI = 1, sobe = 2.2, alfa = 0.55, tex = FB.fumaca, brasa = C3(255, 150, 60)},
	Gelo = {cor = {C3(236, 246, 255), C3(196, 220, 240)}, luzI = 0.8, sobe = -0.9, alfa = 0.62, tex = TEX.fumaca, cristal = C3(200, 235, 255)},
	Neutro = {cor = {C3(200, 205, 212), C3(150, 156, 165)}, luzI = 1, sobe = 1.2, alfa = 0.65, tex = TEX.fumaca},
}
local residuoTok = {}
local function fumacaResidual(m, el, f)
	local R = RESIDUO[el] or RESIDUO.Neutro
	local cab, up, lo = osso(m, "Cabeca"), osso(m, "mouth_upper_tip"), osso(m, "mouth_lower_tip")
	if not (cab and up) then return end
	residuoTok[m] = (residuoTok[m] or 0) + 1; local tok = residuoTok[m]
	local k = math.clamp((up.TransformedWorldCFrame.Position - cab.TransformedWorldCFrame.Position).Magnitude / 2.5, 0.4, 4)  -- tamanho da cabeca
	local function pontos()
		local pc, pu = cab.TransformedWorldCFrame.Position, up.TransformedWorldCFrame.Position
		local pl = lo and lo.TransformedWorldCFrame.Position or pu
		local dir = (pu - pc).Unit; local dir2 = Vector3.new(dir.X, 0, dir.Z); local dirH = dir2.Magnitude > 0.05 and dir2.Unit or dir
		local rt = dirH:Cross(Vector3.yAxis).Unit
		local boca = pu:Lerp(pl, 0.5) - dir * 0.15 * k
		local nar = pu - dir * 0.3 * k + Vector3.yAxis * 0.2 * k              -- narinas: no alto do focinho, um pouco atras da ponta
		return boca, nar + rt * 0.14 * k, nar - rt * 0.14 * k, dir
	end
	local b, n1, n2, dir = pontos()
	local ancs = {ancora(b), ancora(n1), ancora(n2)}
	local base = {Color = seq(R.cor), LightEmission = 0, LightInfluence = R.luzI, Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-35, 35),
		Acceleration = Vector3.new(0, R.sobe, 0), Drag = 1.6, EmissionDirection = Enum.NormalId.Front}
	local function fumaca(a, tam, taxa, vel, abre)
		local t = table.clone(base)
		t.Size = ns(0, 0.18 * tam * k, 0.4, 0.7 * tam * k, 1, 1.5 * tam * k); t.Transparency = ns(0, 1, 0.12, R.alfa, 0.6, R.alfa + 0.15, 1, 1)
		t.Lifetime = NumberRange.new(1.1, 1.9); t.Speed = NumberRange.new(vel * 0.5 * k, vel * k); t.SpreadAngle = Vector2.new(abre, abre); t.Rate = taxa * f
		if R.tex == FB.fumaca then flip(t, FB.fumaca) else t.Texture = R.tex end
		return emissor(a, t)
	end
	local es = {fumaca(ancs[1], 1, 16, 1.6, 22), fumaca(ancs[2], 0.55, 9, 1.1, 10), fumaca(ancs[3], 0.55, 9, 1.1, 10)}
	if R.brasa then                                                        -- Fogo: brasas soltas que sobem e apagam
		table.insert(es, emissor(ancs[1], {Texture = TEX.faisca, Color = seq({C3(255, 220, 140), R.brasa, C3(120, 30, 10)}), LightEmission = 1,
			Size = ns(0, 0.07 * k, 1, 0), Transparency = ns(0, 0, 0.8, 0.3, 1, 1), Lifetime = NumberRange.new(0.6, 1.2), Speed = NumberRange.new(0.6 * k, 1.6 * k),
			Acceleration = Vector3.new(0, 2.5, 0), SpreadAngle = Vector2.new(35, 35), EmissionDirection = Enum.NormalId.Front, Rate = 7 * f}))
		luz(ancs[1], R.brasa, 0.7, 6 * k, 1.2)
	elseif R.cristal then                                                  -- Gelo: cintilas finas de geada caindo
		table.insert(es, emissor(ancs[1], {Texture = TEX.faisca, Color = ColorSequence.new(R.cristal), LightEmission = 0.6, Size = ns(0, 0.05 * k, 1, 0),
			Transparency = ns(0, 0.2, 1, 1), Lifetime = NumberRange.new(0.7, 1.2), Speed = NumberRange.new(0.3 * k, 0.9 * k), Acceleration = Vector3.new(0, -1.5, 0),
			SpreadAngle = Vector2.new(40, 40), EmissionDirection = Enum.NormalId.Front, Rate = 6 * f}))
	end
	for _, e in ipairs(es) do TweenService:Create(e, TweenInfo.new(2.4, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Rate = 0}):Play() end
	local fim = os.clock() + 2.6
	local con; con = RunService.Heartbeat:Connect(function()               -- acompanha a cabeca (o dragao continua se mexendo)
		if os.clock() > fim or residuoTok[m] ~= tok or not m.Parent then
			con:Disconnect(); for _, e in ipairs(es) do e.Rate = 0 end
			task.delay(2.2, function() for _, a in ipairs(ancs) do a:Destroy() end end); return
		end
		local p1, p2, p3, dr = pontos()
		ancs[1].WorldCFrame = CFrame.lookAt(p1, p1 + dr - Vector3.yAxis * 0.25)
		ancs[2].WorldCFrame = CFrame.lookAt(p2, p2 + dr - Vector3.yAxis * 0.6)  -- o ar das narinas sai para a frente e para baixo
		ancs[3].WorldCFrame = CFrame.lookAt(p3, p3 + dr - Vector3.yAxis * 0.6)
	end)
end

-- ===== despacho ==================================================================================================
]======]
	local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora 1")
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1) end
do local a, b = [======[	local f = fatorLOD(m:GetPivot().Position); local el = d.el or semEl; local P = PERFIL[el] or PERFIL.Neutro
]======], [======[	local f = fatorLOD(m:GetPivot().Position); local el = d.el or semEl; local P = PERFIL[el] or PERFIL.Neutro
	if d.hab == "Sopro" and d.fase == "fim" and f > 0 then task.spawn(fumacaResidual, m, el, f) end   -- PATCH_FUMACA_RESIDUAL
]======]
	local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora 2")
	src = src:sub(1, i - 1) .. b .. src:sub(j + 1) end
assert(loadstring(src), "VFXCombate nao compila")
if not SS:FindFirstChild("Backup_Fumaca_Residual_2026-11-05") then local f = Instance.new("Folder"); f.Name = "Backup_Fumaca_Residual_2026-11-05"; V:Clone().Parent = f; f.Parent = SS end
V.Source = src
local _, n = src:gsub("\n", "")
return "aplicado: VFXCombate " .. #src .. " bytes / " .. n .. " linhas"

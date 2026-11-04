-- RastroBreu_Cliente (LocalScript) — EFEITO VISUAL da passiva Rastro do Breu (Dragao Sombrio). So cosmetico: quem
-- decide o impulso e o servidor (RastroBreu_Servidor publica RastroModo / RastroCarga no modelo).
-- LINHAS negras com borda violeta: fracas enquanto o impulso carrega, fortes com o impulso ativo. Sem particulas, sem
-- luz dinamica, sem mexer em anatomia/rig. LOD por distancia da camera.
-- v2 (03/11): a v1 ligava ossos distantes e virava placas largas sobre a asa (reprovado na revisao do proprio teste).
-- v3 (04/11, "linha mais reta e maior"): Trails em pontos suavizados -> retas e longas, mas soltas da asa.
-- v4 (04/11, "mais parecido que sai da asa"): cada linha e um FEIXE (Beam) que NASCE colado no osso da ponta da asa /
-- das penas / da cauda (Attachment no proprio osso: acompanha a batida) e termina num ponto de cauda no mundo que segue
-- a ponta com atraso (ARRASTO): reta, mais longa com mais velocidade (~ vel / ARRASTO), afinando e sumindo para tras.
-- Nucleo preto estreito + halo violeta largo e transparente. Pontos: 3 por asa (ponta + penas 2 e 4) e a cauda.
-- Valores artisticos NAO_APROVADO (prototipo para revisao do usuario).
local RunService = game:GetService("RunService")
local cam = workspace.CurrentCamera
local FORMAS = {Sombrio = true}
local LOD = 350                                         -- studs: alem disto as linhas ficam desligadas
local ARRASTO = 1.6                                     -- 1/s: menor = linha mais longa (comprimento ~ velocidade / ARRASTO)
local COMP_MAX = 34                                     -- studs: teto do comprimento
local PRETO, VIOLETA = Color3.fromRGB(6, 0, 12), Color3.fromRGB(165, 60, 255)
local LARG = {nucleo = {0.55, 0.05}, halo = {1.7, 0.2}}  -- largura na asa -> na ponta de tras
local PONTOS = {"wing_tip_l", "wing_tip_r", "wing_feather_2_tip_l", "wing_feather_2_tip_r", "wing_feather_4_tip_l", "wing_feather_4_tip_r", "tail_tip"}
local registrados = {}                                  -- [modelo] = {feixes, pontos}
local function registrar(m)
	if registrados[m] or not FORMAS[m:GetAttribute("FormaRegional") or ""] or not m.PrimaryPart then return end
	local B = {}; for _, b in ipairs(m:GetDescendants()) do if b:IsA("Bone") then B[b.Name] = b end end
	local feixes, pontos = {}, {}
	local pasta = Instance.new("Folder"); pasta.Name = "RastroBreu_VFX"
	for _, nome in ipairs(PONTOS) do
		local o = B[nome]
		if o then
			local a0 = Instance.new("Attachment"); a0.Name = "Rastro_Raiz"; a0.Parent = o                 -- colado no osso
			local a1 = Instance.new("Attachment"); a1.Name = "Rastro_" .. nome .. "_Cauda"; a1.Parent = workspace.Terrain
			local pt = {osso = o, a0 = a0, a1 = a1}
			for _, c in ipairs({{"nucleo", PRETO, 0, 1}, {"halo", VIOLETA, 0.8, 0.2}}) do
				local b = Instance.new("Beam"); b.Name = nome .. "_" .. c[1]; b.Attachment0 = a0; b.Attachment1 = a1
				b.Color = ColorSequence.new(c[2]); b.LightEmission = c[3]; b.LightInfluence = c[4]; b.FaceCamera = true; b.Segments = 1
				b.Width0, b.Width1 = LARG[c[1]][1], LARG[c[1]][2]; b.Enabled = false; b:SetAttribute("Halo", c[1] == "halo")
				b.Parent = pasta; table.insert(feixes, b)
			end
			table.insert(pontos, pt)
		end
	end
	pasta.Parent = m.PrimaryPart
	registrados[m] = {feixes = feixes, pontos = pontos}
	m.AncestryChanged:Connect(function()
		if not m:IsDescendantOf(workspace) then registrados[m] = nil; for _, pt in ipairs(pontos) do pt.a1:Destroy() end end
	end)
end
local function transp(base) return NumberSequence.new({NumberSequenceKeypoint.new(0, base), NumberSequenceKeypoint.new(0.6, base + (1 - base) * 0.45), NumberSequenceKeypoint.new(1, 1)}) end
local ultNivel = {}
RunService.RenderStepped:Connect(function(dt)
	for _, m in ipairs(workspace:GetChildren()) do if m:IsA("Model") and not registrados[m] and FORMAS[m:GetAttribute("FormaRegional") or ""] then registrar(m) end end
	local k = 1 - math.exp(-ARRASTO * math.min(dt, 0.1))
	for m, R in pairs(registrados) do
		local nivel = 0
		local root = m.PrimaryPart
		if root and (root.Position - cam.CFrame.Position).Magnitude < LOD then
			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end
		end
		for _, pt in ipairs(R.pontos) do                                -- a cauda de cada linha persegue a ponta do osso
			local p = pt.osso.TransformedWorldCFrame.Position
			if nivel == 0 or not pt.q then pt.q = p
			else
				pt.q = pt.q:Lerp(p, k)
				local v = pt.q - p; if v.Magnitude > COMP_MAX then pt.q = p + v.Unit * COMP_MAX end
			end
			pt.a1.WorldPosition = pt.q
		end
		if nivel ~= ultNivel[m] then
			ultNivel[m] = nivel
			for _, b in ipairs(R.feixes) do
				local halo = b:GetAttribute("Halo")
				b.Enabled = nivel > 0
				if nivel == 2 then b.Transparency = transp(halo and 0.5 or 0.05)
				elseif nivel == 1 then b.Transparency = transp(halo and 0.88 or 0.7) end
			end
		end
	end
end)

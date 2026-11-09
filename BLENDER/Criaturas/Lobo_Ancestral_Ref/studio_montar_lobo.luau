-- studio_montar_lobo.luau (Studio, modo Edit, PLACE DE TESTE ISOLADO): monta os KeyframeSequences do Lobo Ancestral a
-- partir dos JSON exportados pelo Blender (anim_lobo.py), servidos em http://127.0.0.1:8766/ (pasta
-- BLENDER/Criaturas/Lobo_Ancestral_Ref/clipes). Pose.CFrame = matrix_basis do Blender (mesma convencao dos dragoes).
-- A arvore de Poses vem de um clipe que o Import 3D ja criou (molde); sem molde, e montada pela hierarquia dos Bones.
-- Marcadores (Contato, UivoInicio...) viram KeyframeMarker. Destino: <modelo>.AnimSaves_Lobo (nao publica nada).
local H = game:GetService("HttpService")
local URL = "http://127.0.0.1:8766/"
local NOME_MODELO = "Lobo_Ancestral"
local modelo = workspace:FindFirstChild(NOME_MODELO, true)
assert(modelo and modelo:IsA("Model"), "modelo " .. NOME_MODELO .. " nao encontrado no Workspace")
local destino = modelo:FindFirstChild("AnimSaves_Lobo") or Instance.new("Folder")
destino.Name = "AnimSaves_Lobo"; destino.Parent = modelo

local function molde()
	for _, d in ipairs(game:GetDescendants()) do
		if d:IsA("KeyframeSequence") and d.Parent ~= destino and #d:GetKeyframes() > 0 then
			local kf = d:GetKeyframes()[1]
			for _, p in ipairs(kf:GetDescendants()) do
				if p:IsA("Pose") and p.Name == "Pelve" then return kf end
			end
		end
	end
end
local function arvoreDosBones()
	local raizes = {}
	local function copiar(inst, pai)
		for _, c in ipairs(inst:GetChildren()) do
			if c:IsA("Bone") then
				local p = Instance.new("Pose"); p.Name = c.Name; p.Parent = pai; copiar(c, p)
			end
		end
	end
	for _, mp in ipairs(modelo:GetDescendants()) do
		if mp:IsA("BasePart") then
			local tem = false
			for _, c in ipairs(mp:GetChildren()) do if c:IsA("Bone") then tem = true end end
			if tem then
				local r = Instance.new("Pose"); r.Name = mp.Name; copiar(mp, r); table.insert(raizes, r)
			end
		end
	end
	return raizes
end
local MOLDE = molde()
local function base()
	local out = {}
	if MOLDE then for _, c in ipairs(MOLDE:GetChildren()) do table.insert(out, c:Clone()) end
	else out = arvoreDosBones() end
	return out
end

local function montar(nome)
	local js = H:JSONDecode(H:GetAsync(URL .. "LoboAncestral_" .. nome .. ".json"))
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = js.nome; kfs.Loop = js.loop
	kfs.Priority = js.loop and Enum.AnimationPriority.Movement or Enum.AnimationPriority.Action
	kfs:SetAttribute("Velocidade", js.velocidade); kfs:SetAttribute("RotacaoRaizGraus", js.rotacao_raiz_graus or 0)
	local arv = base()
	for i = 0, js.quadros - 1 do
		local kf = Instance.new("Keyframe"); kf.Time = i / js.fps
		for _, raiz in ipairs(arv) do
			local r = raiz:Clone()
			for _, p in ipairs(r:GetDescendants()) do
				local d = p:IsA("Pose") and js.ossos[p.Name]
				if d then
					local o = i * 7
					p.CFrame = CFrame.new(d[o + 5], d[o + 6], d[o + 7], d[o + 1], d[o + 2], d[o + 3], d[o + 4])
				end
			end
			r.Parent = kf
		end
		for _, m in ipairs(js.marcadores or {}) do
			if math.abs(m.t - kf.Time) < 0.5 / js.fps then
				local mk = Instance.new("KeyframeMarker"); mk.Name = m.nome; mk.Value = m.nome; mk.Parent = kf
			end
		end
		kf.Parent = kfs
		if i % 30 == 29 then task.wait() end
	end
	local velho = destino:FindFirstChild(js.nome)
	if velho then velho:Destroy() end
	kfs.Parent = destino
	return js.quadros
end

local CLIPES = {"Repouso", "Observar", "Andar", "Trote", "Corrida", "Partida", "Freada", "VirarE", "VirarD",
	"Sentar", "Sentado", "LevantarSentado", "Deitar", "Deitado", "Descanso", "Adormecer", "Despertar", "LevantarDeitado",
	"Salto", "Uivo", "Rosnar", "Mordida", "Garra", "Impacto"}
local rel = {}
for _, n in ipairs(CLIPES) do
	local ok, q = pcall(montar, n)
	table.insert(rel, n .. "=" .. (ok and tostring(q) or ("ERRO " .. tostring(q))))
	task.wait()
end
return "molde=" .. tostring(MOLDE and MOLDE:GetFullName() or "bones") .. " | " .. table.concat(rel, ", ")

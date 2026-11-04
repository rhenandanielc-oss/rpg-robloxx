-- SUBSTITUIDO no piloto de 04/11/2026 (nao usado): o place principal tem HttpEnabled=false. Ver studio/AdaptadorUrso.luau e studio/TestePlayUrso.luau.
-- montar_kfs_urso.luau (Studio, modo Edit) - ADAPTADOR PROPRIO DO URSO SILVESTRE v2 (nao altera a ponte compartilhada
-- V14/montar_kfs_json.luau). Monta KeyframeSequences a partir dos JSON do Blender (rig/clipes/Urso_<clipe>.json),
-- servidos em http://127.0.0.1:8767/ (servidor local do urso; a 8766 e da ponte dos dragoes).
-- Diferenca da ponte: NAO usa clipe molde de outra criatura. A arvore de Poses e montada a partir da hierarquia de
-- Bones do PROPRIO urso importado (modelo em workspace.Teste_Urso_v2). Cada quadro: Pose.CFrame = matrix_basis do
-- Blender (quaternion xyzw + translacao), a mesma convencao conferida na ponte dos dragoes.
-- Destino: ReplicatedStorage.Animacoes_Urso_v2 (pasta so do urso). Nada e publicado.
local H = game:GetService("HttpService")
local BASE = "http://127.0.0.1:8767/"
local modelo = workspace:FindFirstChild("Teste_Urso_v2") and workspace.Teste_Urso_v2:FindFirstChildWhichIsA("Model")
assert(modelo, "modelo do urso nao encontrado em workspace.Teste_Urso_v2")
local pasta = game.ReplicatedStorage:FindFirstChild("Animacoes_Urso_v2") or Instance.new("Folder")
pasta.Name = "Animacoes_Urso_v2"; pasta.Parent = game.ReplicatedStorage

-- arvore: Pose(parte que contem a Raiz) > Pose(Raiz) > ... seguindo Bone.Parent; a parte raiz e confirmada no M0
local raizBone = modelo:FindFirstChild("Raiz", true)
assert(raizBone and raizBone:IsA("Bone"), "osso Raiz nao encontrado")
local parte = raizBone:FindFirstAncestorWhichIsA("BasePart")
local function poseDe(inst)
	local p = Instance.new("Pose"); p.Name = inst.Name; p.Weight = 1
	for _, c in ipairs(inst:GetChildren()) do
		if c:IsA("Bone") then poseDe(c).Parent = p end
	end
	return p
end
local function arvore()
	local topo = Instance.new("Pose"); topo.Name = parte.Name; topo.Weight = 0
	poseDe(raizBone).Parent = topo
	return topo
end

local function montar(nome)
	local js = H:JSONDecode(H:GetAsync(BASE .. nome .. ".json"))
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = js.nome; kfs.Loop = js.loop
	kfs.Priority = (nome == "Urso_Repouso") and Enum.AnimationPriority.Idle
		or (nome == "Urso_Andar") and Enum.AnimationPriority.Movement or Enum.AnimationPriority.Action
	local faltam = {}
	for i = 0, js.quadros - 1 do
		local kf = Instance.new("Keyframe"); kf.Time = i / js.fps
		local t = arvore()
		for _, p in ipairs(t:GetDescendants()) do
			local d = js.ossos[p.Name]
			if d then
				local o = i * 7
				p.CFrame = CFrame.new(d[o + 5], d[o + 6], d[o + 7], d[o + 1], d[o + 2], d[o + 3], d[o + 4])
			elseif i == 0 then table.insert(faltam, p.Name) end
		end
		t.Parent = kf; kf.Parent = kfs
	end
	local velho = pasta:FindFirstChild(js.nome); if velho then velho:Destroy() end
	kfs.Parent = pasta
	print("KFS_URSO", js.nome, js.quadros, "quadros", "loop", js.loop, "poses sem dado:", table.concat(faltam, ","))
	return kfs
end

for _, n in ipairs({"Urso_Repouso", "Urso_Andar", "Urso_Rugir"}) do montar(n) end

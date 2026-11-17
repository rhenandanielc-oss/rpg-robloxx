-- montar_kfs_lobo_v43.luau: igual a v42, le studio/json_v43 = golpes PARCIAIS do ataque basico (anim_v43).
-- Parcial: so os ossos do JSON recebem Pose com Weight 1; ossos que so ligam a raiz aos animados entram com Weight 0 e
-- CFrame identidade (caminho, como o topo); ossos fora do caminho nao entram -> a locomocao continua neles.
-- Prioridade Action2 (acima das faixas Action do kit e do Uivo). Marcador "Contato" num KeyframeMarker.
-- montar_kfs_lobo_v42.luau: igual a v41 r2, le studio/json_v42 (5 clipes do kit, anim_v42; matrizes do mesmo rig v41)
-- montar_kfs_lobo_v41.luau (Studio, modo Edit, place Teste-animacoes) - Lobo Artico anim_v41, 15/11/2026 (r2)
-- Monta KeyframeSequences a 30 fps a partir dos JSON do Blender (studio/json_v41/, servidos em http://127.0.0.1:8766/).
-- Convencao MEDIDA neste import (Import 3D de 15/11), osso a osso, com a orientacao COMPLETA (conferir_giro_v41.luau):
--   osso_Roblox = osso_Blender * M_osso, M_osso = (G * B_repouso)^-1 * W_repouso  (180 graus; eixo varia por osso)
--   => Transform = M^-1 * basis_Blender * M   (deducao: W = G*B_pai*L*basis*M e W_repouso = W_pai_repouso*C)
-- G = Blender armature -> Roblox (x,y,z)->(-x,z,y) na origem do pivo. Arvore: RootPart > Raiz > ... (o Animator ignora a
-- Pose do topo, por isso o Raiz precisa de um pai; os clipes do importador tinham o Raiz no topo e um giro errado).
-- r1 (descartada): usava K = Pose_importador(q0)*basis(q0)^-1 + giro no Quadril; as pontas batiam, mas os ossos giravam 180
-- em torno do proprio eixo (malha torcida no Play). Os clipes do importador (RBX_ANIMSAVES) ficam intactos.
-- Uso: local M = loadstring(GetAsync(".../montar_kfs_lobo_v41.luau"))(); M.montar({"Repouso", "Andar"})
local H = game:GetService("HttpService")
local BASE = "http://127.0.0.1:8766/json_v43/"
local LACOS = {CometaVoo = 1, AvalancheCorrida = 1}
local MOVIMENTO = {Andar = 1, Trote = 1, Corrida = 1, Arrancada = 1, Frenagem = 1, VirarEsquerda = 1, VirarDireita = 1,
	AndarParaTrote = 1, TroteParaAndar = 1, TroteParaCorrida = 1, CorridaParaTrote = 1}
local low = workspace.Teste_LoboArtico.LoboArtico_LOW
local pasta = game.ReplicatedStorage:FindFirstChild("Animacoes_LoboArtico")
if not pasta then
	pasta = Instance.new("Folder"); pasta.Name = "Animacoes_LoboArtico"; pasta.Parent = game.ReplicatedStorage
end
pasta:SetAttribute("Fonte_v41", "BLENDER/Criaturas/Lobo_Artico_Ref/anim_v41 (aprovada 12/11) -> studio/json_v41 -> montar_kfs_lobo_v41.luau r2, 30 fps")

local function cfm(m) return CFrame.new(m[1][4], m[2][4], m[3][4], m[1][1], m[1][2], m[1][3], m[2][1], m[2][2], m[2][3], m[3][1], m[3][2], m[3][3]) end
local MZ = H:JSONDecode(H:GetAsync(BASE .. "matrizes_v41.json"))
local ossos = {}
for _, b in ipairs(low:GetDescendants()) do if b:IsA("Bone") then ossos[b.Name] = b end end
for _, b in pairs(ossos) do b.Transform = CFrame.identity end
local G = CFrame.fromMatrix(low:GetPivot().Position, Vector3.new(-1, 0, 0), Vector3.new(0, 0, 1), Vector3.new(0, 1, 0))
local M, Mi = {}, {}
for n, b in pairs(ossos) do
	local m = (G * cfm(MZ.rest[n])):Inverse() * b.TransformedWorldCFrame
	M[n] = m.Rotation; Mi[n] = m.Rotation:Inverse()      -- translacao medida = 0,000
end
local raiz = ossos.Raiz
local topoNome = raiz.Parent.Name                         -- "RootPart"

local function montar1(nome)
	local js = H:JSONDecode(H:GetAsync(BASE .. "LoboArtico_" .. nome .. ".json"))
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = "LoboArtico_" .. nome
	kfs.Loop = LACOS[nome] ~= nil
	kfs.Priority = Enum.AnimationPriority.Action2
	kfs:SetAttribute("Quadros", js.quadros); kfs:SetAttribute("Fps", js.fps); kfs:SetAttribute("Montador", "r2 conjugado por osso")
	for i = 0, js.quadros - 1 do
		local kf = Instance.new("Keyframe"); kf.Time = i / js.fps
		local o = i * 7
		local function temAnimado(bone)
			if js.ossos[bone.Name] then return true end
			for _, c in ipairs(bone:GetChildren()) do if c:IsA("Bone") and temAnimado(c) then return true end end
			return false
		end
		local function rec(bone, parent)
			if not temAnimado(bone) then return end
			local d = js.ossos[bone.Name]
			local p = Instance.new("Pose"); p.Name = bone.Name
			if d then
				p.Weight = 1
				local J = CFrame.new(d[o + 5], d[o + 6], d[o + 7], d[o + 1], d[o + 2], d[o + 3], d[o + 4])
				p.CFrame = Mi[bone.Name] * J * M[bone.Name]
			else p.Weight = 0; p.CFrame = CFrame.identity end
			p.Parent = parent
			for _, c in ipairs(bone:GetChildren()) do if c:IsA("Bone") then rec(c, p) end end
		end
		local topo = Instance.new("Pose"); topo.Name = topoNome; topo.Weight = 0; topo.Parent = kf
		rec(raiz, topo)
		kf.Parent = kfs
	end
	for nomeM, t in pairs(js.marcadores_s or {}) do
		local kfm = Instance.new("KeyframeMarker"); kfm.Name = nomeM
		local alvo, dm = nil, math.huge
		for _, k in ipairs(kfs:GetChildren()) do if k:IsA("Keyframe") and math.abs(k.Time - t) < dm then alvo, dm = k, math.abs(k.Time - t) end end
		if alvo then alvo:AddMarker(kfm) end
	end
	kfs:SetAttribute("Parcial", true)
	local velho = pasta:FindFirstChild(kfs.Name); if velho then velho:Destroy() end
	kfs.Parent = pasta
	return string.format("%s q=%d loop=%s pri=%s desc=%d", kfs.Name, js.quadros, tostring(kfs.Loop), kfs.Priority.Name, #kfs:GetDescendants())
end

return {montar = function(lista)
	local r = {}
	for _, n in ipairs(lista) do table.insert(r, montar1(n)); task.wait() end
	return table.concat(r, "\n")
end}

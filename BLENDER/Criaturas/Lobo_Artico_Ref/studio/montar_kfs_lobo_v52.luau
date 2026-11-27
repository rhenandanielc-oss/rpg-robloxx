-- v52: le studio/json_v52 (16 CURVAS DO ANDAR com apoio corrigido + PartidaCurva E/D v51 + ParadaAndar; prioridade Movement; lacos AndarCurva*/AndarCurvaFechada*)
-- v49: le studio/json_v49 (32 CURVAS DE TROTE E CORRIDA, anim_v49; lacos TroteCurva*/CorridaCurva*; prioridade Movement)
-- v48: le studio/json_v48 (PARTIDA/PARADA do Andar, anim_v48; prioridade Movement)
-- v47: le studio/json_v47 (4 VIRADAS DE COMBATE, anim_v47b; prioridade Movement)
-- v46b: le studio/json_v46b (16 clipes de CURVA ANDANDO, anim_v46c; lacos AndarCurva*/AndarCurvaFechada*; prioridade Movement)
-- v45r3: le studio/json_v45r3 (clipes de ameaca r3, mais agressivos)
-- montar_kfs_lobo_v45.luau: igual a v44, le studio/json_v45 (AmeacaEntrar/Ameaca laco/AmeacaSair/InvestidaAviso, anim_v45; prioridade Action)
-- montar_kfs_lobo_v44.luau: igual a v42, le studio/json_v44 (viradas curtas VirarCurtoEsquerda/Direita, anim_v44b; mesmas matrizes do rig v41)
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
local BASE = "http://127.0.0.1:8766/json_v52/"
local LACOS = {}
for _, g in ipairs({"Trote", "Corrida"}) do for _, l in ipairs({"Esquerda", "Direita"}) do LACOS[g .. "Curva" .. l] = 1; LACOS[g .. "CurvaFechada" .. l] = 1 end end
for _, l in ipairs({"Esquerda", "Direita"}) do LACOS["AndarCurva" .. l] = 1; LACOS["AndarCurvaFechada" .. l] = 1 end   -- v52
local MOVIMENTO = {Andar = 1, Trote = 1, Corrida = 1, Arrancada = 1, Frenagem = 1, VirarEsquerda = 1, VirarDireita = 1, VirarCurtoEsquerda = 1, VirarCurtoDireita = 1,
	AndarParaTrote = 1, TroteParaAndar = 1, TroteParaCorrida = 1, CorridaParaTrote = 1}
for _, l in ipairs({"Esquerda", "Direita"}) do for _, a in ipairs({"AndarCurva", "AndarCurvaFechada", "AndarParaCurva", "CurvaParaAndar", "CurvaParaFechada", "FechadaParaCurva", "CurvaBreve", "CurvaCurta", "VirarCombate45", "VirarCombate90", "VirarCombate180", "PartidaCurva"}) do MOVIMENTO[a .. l] = 1 end end
MOVIMENTO.PartidaAndar = 1; MOVIMENTO.ParadaAndar = 1
for _, g in ipairs({"Trote", "Corrida"}) do for _, l in ipairs({"Esquerda", "Direita"}) do for _, a in ipairs({"Curva", "CurvaFechada", "ParaCurva", "CurvaParaReto", "CurvaParaFechada", "FechadaParaCurva", "CurvaBreve", "CurvaCurta"}) do MOVIMENTO[g .. a .. l] = 1 end end end
for _, l in ipairs({""}) do for _, a in ipairs({}) do MOVIMENTO[a .. l] = 1 end end
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
	kfs.Priority = (nome == "Repouso") and Enum.AnimationPriority.Idle or MOVIMENTO[nome] and Enum.AnimationPriority.Movement or Enum.AnimationPriority.Action
	kfs:SetAttribute("Quadros", js.quadros); kfs:SetAttribute("Fps", js.fps); kfs:SetAttribute("Montador", "r2 conjugado por osso")
	for i = 0, js.quadros - 1 do
		local kf = Instance.new("Keyframe"); kf.Time = i / js.fps
		local o = i * 7
		local function rec(bone, parent)
			local d = js.ossos[bone.Name]
			local p = Instance.new("Pose"); p.Name = bone.Name; p.Weight = 1
			local J = CFrame.new(d[o + 5], d[o + 6], d[o + 7], d[o + 1], d[o + 2], d[o + 3], d[o + 4])
			p.CFrame = Mi[bone.Name] * J * M[bone.Name]
			p.Parent = parent
			for _, c in ipairs(bone:GetChildren()) do if c:IsA("Bone") then rec(c, p) end end
		end
		local topo = Instance.new("Pose"); topo.Name = topoNome; topo.Weight = 0; topo.Parent = kf
		rec(raiz, topo)
		kf.Parent = kfs
	end
	local velho = pasta:FindFirstChild(kfs.Name); if velho then velho:Destroy() end
	kfs.Parent = pasta
	return string.format("%s q=%d loop=%s pri=%s desc=%d", kfs.Name, js.quadros, tostring(kfs.Loop), kfs.Priority.Name, #kfs:GetDescendants())
end

return {montar = function(lista)
	local r = {}
	for _, n in ipairs(lista) do table.insert(r, montar1(n)); task.wait() end
	return table.concat(r, "\n")
end}

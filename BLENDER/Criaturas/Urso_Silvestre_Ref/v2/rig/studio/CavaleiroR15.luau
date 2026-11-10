-- CavaleiroR15 (ModuleScript em ServerStorage.Urso_v2_Piloto.Montaria) - montaria do urso, TESTE (09/11/2026).
-- Converte o cavaleiro de teste do Blender (Dados_Clipes.Cav_*: rotacao de cada PARTE do R15 no espaco da RootPart do urso,
-- e posicao do LowerTorso) em KeyframeSequence para um R15 real. Funciona com Motor6D (C0/C1) e com AnimationConstraint
-- (Attachment0/1): Transform = (Part0 * A0)^-1 * (Part1 * A1). A HumanoidRootPart do cavaleiro fica na RootPart do urso
-- (identidade); o caminho inteiro do quadril vai na junta Root. As demais juntas so giram (sem translacao).
-- As proporcoes do manequim do Blender sao aproximadas do R15: pequenas diferencas de contato sao esperadas.
local PASTA = game.ServerStorage.Urso_v2_Piloto
local A = require(PASTA.AdaptadorUrso)
local M = {}

local function juntas(rig)                         -- {parte1 = {pai, f0, f1}} para Motor6D e AnimationConstraint
	local J = {}
	for _, d in rig:GetDescendants() do
		if d:IsA("Motor6D") and d.Part0 and d.Part1 then
			J[d.Part1.Name] = {pai = d.Part0.Name, f0 = d.C0, f1 = d.C1, j = d}
		elseif d.ClassName == "AnimationConstraint" and d.Attachment0 and d.Attachment1 then
			J[d.Attachment1.Parent.Name] = {pai = d.Attachment0.Parent.Name, f0 = d.Attachment0.CFrame, f1 = d.Attachment1.CFrame, j = d}
		end
	end
	return J
end
M.juntas = juntas

local function parte(c, nome, i)                     -- CFrame da parte (rotacao; posicao so no LowerTorso)
	local o = c.ossos[nome]; if not o then return nil end
	local k = i + 1
	return CFrame.new(o[5][k], o[6][k], o[7][k], o[1][k], o[2][k], o[3][k], o[4][k])
end

-- transforms de todas as juntas no quadro i: {parte1 = CFrame}
function M.quadro(c, J, i)
	local T = {}
	for p1, j in J do
		local b = parte(c, p1, i)
		if b then
			if j.pai == "HumanoidRootPart" then
				T[p1] = j.f0:Inverse() * b * j.f1                                           -- HRP = identidade
			else
				local a = parte(c, j.pai, i)
				if a then T[p1] = (j.f0.Rotation:Inverse() * a.Rotation:Inverse() * b.Rotation * j.f1.Rotation).Rotation end
			end
		end
	end
	return T
end

function M.montar(rig, nome, prioridade)
	local c = A.clipe(nome); local J = juntas(rig)
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = nome; kfs.Loop = c.loop; kfs.Priority = prioridade or Enum.AnimationPriority.Action
	for i = 0, c.quadros - 1 do
		local kf = Instance.new("Keyframe"); kf.Time = i / c.fps
		local T = M.quadro(c, J, i); local poses = {}
		local function pose(nomeP)
			if poses[nomeP] then return poses[nomeP] end
			local p = Instance.new("Pose"); p.Name = nomeP; p.CFrame = T[nomeP] or CFrame.identity; poses[nomeP] = p
			local j = J[nomeP]
			if j then p.Parent = pose(j.pai) else p.Weight = 0; p.Parent = kf end
			return p
		end
		for p1 in J do pose(p1) end
		kf.Parent = kfs
	end
	if c.quadros == 1 then                         -- pose unica (Sentado): fecha com um 2o keyframe igual
		local kf2 = kfs:GetChildren()[1]:Clone(); kf2.Time = 1 / c.fps; kf2.Parent = kfs
	end
	return kfs
end

-- aplica um quadro direto nas juntas (conferencia no Edit, sem tocar animacao)
function M.aplicar(rig, nome, i)
	local c = A.clipe(nome); local J = juntas(rig); local T = M.quadro(c, J, i)
	for p1, j in J do j.j.Transform = T[p1] or CFrame.identity end
end
return M

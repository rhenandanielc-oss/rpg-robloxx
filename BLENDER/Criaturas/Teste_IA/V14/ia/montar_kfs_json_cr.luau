-- montar_kfs_json_cr.luau (clipes do CR_Dragao, pasta anim_json_cr) (Studio, modo Edit): monta KeyframeSequences a partir dos JSON exportados do Blender
-- (meshy\exportar_clipes_json.py), servidos em http://127.0.0.1:8766/anim_json_cr/. Dispensa a importacao 3D manual.
-- A arvore de Poses (hierarquia dos ossos, DRV_root/root) vem de um clipe ja importado (molde); cada quadro recebe
-- Pose.CFrame = matrix_basis do Blender (conferido igual ao do importador). A versao anterior de cada clipe vai para
-- Animacoes_Silverwing.Anteriores (1 recuperavel).
local H = game:GetService("HttpService")
local pasta = game.ReplicatedStorage.Animacoes_Silverwing
local anteriores = pasta:FindFirstChild("Anteriores") or Instance.new("Folder"); anteriores.Name = "Anteriores"; anteriores.Parent = pasta
local MOLDE = pasta:FindFirstChild("Silverwing_Ataque_Garra_E")
assert(MOLDE, "clipe molde nao encontrado")
-- ATENCAO: o keyframe importado tem DUAS raizes irmas — DRV_root (vazia) e root (com os 98 ossos). Copiar so a
-- primeira gerava clipes sem ossos (o Animator tocava e nada se mexia).
local function arvoreMolde()
	local kf = MOLDE:GetKeyframes()[1]
	local raizes = {}
	for _, c in ipairs(kf:GetChildren()) do table.insert(raizes, c:Clone()) end
	return raizes
end
local PARCIAL = {Silverwing_Sopro_Inicio = "Pescoco2", Silverwing_Sopro_Loop = "Pescoco2", Silverwing_Sopro_Fim = "Pescoco2"}
local function pesoParcial(kfs, raizViva)
	for _, kf in ipairs(kfs:GetKeyframes()) do
		for _, p in ipairs(kf:GetDescendants()) do
			if p:IsA("Pose") then
				local vivo = p.Name == raizViva or p:FindFirstAncestor(raizViva) ~= nil
				p.Weight = vivo and 1 or 0
			end
		end
	end
end
local function montar(nome, destino)
	local js = H:JSONDecode(H:GetAsync("http://127.0.0.1:8766/anim_json_cr/" .. nome .. ".json"))
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = js.nome; kfs.Loop = js.loop
	local velho = pasta:FindFirstChild(js.nome)
	kfs.Priority = velho and velho.Priority or Enum.AnimationPriority.Action
	local base = arvoreMolde()
	for i = 0, js.quadros - 1 do
		local kf = Instance.new("Keyframe"); kf.Time = i / js.fps
		for _, raiz in ipairs(base) do
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
		kf.Parent = kfs
	end
	-- clipes de CORPO SUPERIOR (o dragao pode andar enquanto tocam): so o pescoco/cabeca/boca tem peso; o resto fica
	-- com peso 0 e as patas/tronco/asas/cauda seguem o clipe de locomocao por baixo (usuario 31/10: soprar andando)
	if PARCIAL[js.nome] then pesoParcial(kfs, PARCIAL[js.nome]) end
	if destino == "teste" then return kfs end
	if velho then
		local ant = anteriores:FindFirstChild(js.nome); if ant then ant:Destroy() end
		velho.Parent = anteriores
	end
	kfs.Parent = pasta
	return kfs
end
return montar

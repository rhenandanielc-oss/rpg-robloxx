-- montar_kfs_json_sombrio.luau (clipes do DRAGAO SOMBRIO; copia do montar_kfs_json_glacial.luau) (pasta anim_json_sombrio) (Studio, modo Edit): monta
-- KeyframeSequences "Sombrio_*" a partir dos JSON exportados do Blender (meshy\exportar_clipes_json.py com
-- PREFIXO_SAIDA=Sombrio_), servidos em http://127.0.0.1:8766/anim_json_sombrio/. Derivado de montar_kfs_json_cr.luau.
-- Os clipes vao para ReplicatedStorage.Animacoes_Sombrio (pasta propria): os "Silverwing_*" do dragao de fogo nao
-- sao tocados. A arvore de Poses vem do molde do Silverwing (mesmo esqueleto e mesmos nomes de osso do jogo).
-- A versao anterior de cada clipe vai para Animacoes_Sombrio.Anteriores (1 recuperavel).
-- Sem clipes de habilidade (Sopro, Arremetida, Tempestade, Ruptura, Coracao): o kit de gelo ainda esta PENDENTE.
local H = game:GetService("HttpService")
local RS = game:GetService("ReplicatedStorage")
local pasta = RS:FindFirstChild("Animacoes_Sombrio")
if not pasta then pasta = Instance.new("Folder"); pasta.Name = "Animacoes_Sombrio"; pasta.Parent = RS end
local anteriores = pasta:FindFirstChild("Anteriores") or Instance.new("Folder"); anteriores.Name = "Anteriores"; anteriores.Parent = pasta
local MOLDE = RS.Animacoes_Silverwing:FindFirstChild("Silverwing_Ataque_Garra_E")
assert(MOLDE, "clipe molde nao encontrado")
-- o keyframe importado tem DUAS raizes irmas (DRV_root vazia e root com os ossos): copiar as duas
local function arvoreMolde()
	local kf = MOLDE:GetKeyframes()[1]
	local raizes = {}
	for _, c in ipairs(kf:GetChildren()) do table.insert(raizes, c:Clone()) end
	return raizes
end
local function montar(nome, destino)
	local js = H:JSONDecode(H:GetAsync("http://127.0.0.1:8766/anim_json_sombrio/" .. nome .. ".json"))
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = js.nome; kfs.Loop = js.loop
	local velho = pasta:FindFirstChild(js.nome)
	local doFogo = RS.Animacoes_Silverwing:FindFirstChild((js.nome:gsub("^Sombrio_", "Silverwing_")))
	kfs.Priority = (velho and velho.Priority) or (doFogo and doFogo.Priority) or Enum.AnimationPriority.Action
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
	if destino == "teste" then return kfs end
	if velho then
		local ant = anteriores:FindFirstChild(js.nome); if ant then ant:Destroy() end
		velho.Parent = anteriores
	end
	kfs.Parent = pasta
	return kfs
end
return montar

-- AdaptadorLobo (ModuleScript em ReplicatedStorage.LoboAncestral) - ADAPTADOR PROPRIO DO LOBO ANCESTRAL (15/11/2026).
-- Nao usa pontes compartilhadas nem clipes de outras criaturas. Dados: StringValues em ReplicatedStorage.LoboAncestral.Dados
-- (studio/empacotar_lobo.py + rojo build -> LoboAncestral_Dados.rbxm, inserido pelo usuario). Nada e publicado:
-- os KeyframeSequences sao montados em Play e registrados com AnimationClipProvider:RegisterAnimationClip (id temporario).
-- Canais 1..7 = qx qy qz qw tx ty tz = matrix_basis do Blender (local ao osso).
-- Convencao do Import 3D novo (desde 10/11): cada osso = osso do Blender girado 180 graus no Y -> q(-x,y,-z,w), t(-x,y,-z).
local M = {}
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {}
for i = 1, #A do IDX[string.byte(A, i)] = i - 1 end
local PASTA = script.Parent
local PADRAO = {0, 0, 0, 1, 0, 0, 0}

local function dec(s, n)
	local out, acc, z, sh = table.create(n), 0, 0, 0
	for i = 1, #s do
		local c = IDX[string.byte(s, i)]
		z += bit32.lshift(bit32.band(c, 31), sh); sh += 5
		if c < 32 then
			local d = (z % 2 == 1) and -((z + 1) // 2) or (z // 2)
			acc += d; table.insert(out, acc / 10000); z = 0; sh = 0
		end
	end
	return out
end

local cache = {}
-- 18/11 (pedido do usuario: atacar ANDANDO para o PvP): clipes PARCIAIS derivados dos aprovados, sem mexer nos dados.
-- So os ossos listados recebem pose; os demais ficam com peso 0 e continuam com a marcha (Andar/Corrida) por baixo.
local CABECA = {"Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "OrelhaE", "OrelhaD", "PeloBochechaE", "PeloBochechaD", "PalpebraE",
	"PalpebraD", "JubaE", "JubaD", "PeloJubaE1", "PeloJubaE2", "PeloJubaD1", "PeloJubaD2", "PeloNuca1", "PeloNuca2", "JubaPeito"}
local PATA_D = {"EscapulaD", "BracoD", "AntebracoD", "CarpoD", "MaoD", "DedosD", "PeloCotoveloD"}   -- a Garra golpeia com a direita
local function conjunto(...) local s = {} for _, l in ipairs({...}) do for _, b in ipairs(l) do s[b] = true end end return s end
M.PARCIAIS = {Mordida_Andando = {base = "Mordida", ossos = conjunto(CABECA)}, Garra_Andando = {base = "Garra", ossos = conjunto(CABECA, PATA_D)}}
function M.clipe(nome)
	if cache[nome] then return cache[nome] end
	local pc = M.PARCIAIS[nome]
	if pc then
		local b = M.clipe(pc.base); local c = table.clone(b); c.nome = nome; c.parcial = pc.ossos
		cache[nome] = c; return c
	end
	local L = string.split(PASTA.Dados[nome].Value, "\n")
	local h = string.split(L[1], "|")
	local c = {nome = h[1], fps = tonumber(h[2]), loop = h[3] == "1", quadros = tonumber(h[4]), ossos = {}, marcadores = {}}
	for _, b in ipairs(string.split(h[5], ",")) do
		c.ossos[b] = {}
		for k = 1, 7 do c.ossos[b][k] = table.create(c.quadros, PADRAO[k]) end
	end
	local i0 = 2
	while L[i0] and string.sub(L[i0], 1, 1) == "#" do
		local tipo, resto = string.match(L[i0], "^#(%a)|(.*)$")
		if tipo == "M" and resto ~= "" then
			for _, par in ipairs(string.split(resto, ",")) do
				local nm, t = string.match(par, "^(.-)=(.*)$"); table.insert(c.marcadores, {nome = nm, t = tonumber(t)})
			end
		elseif tipo == "V" then
			local p = string.split(resto, "|"); c.velocidade = tonumber(p[1]); c.rotacaoRaiz = tonumber(p[2]); c.fonte = p[3]
		end
		i0 += 1
	end
	for i = i0, #L do
		local p = string.split(L[i], "|")
		local b, k, v = p[1], tonumber(p[2]), p[3]
		if string.sub(v, 1, 1) == "S" then c.ossos[b][k] = table.create(c.quadros, tonumber(string.sub(v, 2)))
		else c.ossos[b][k] = dec(string.sub(v, 2), c.quadros) end
	end
	cache[nome] = c
	return c
end

function M.nomes()
	local r = {}
	for _, v in ipairs(PASTA.Dados:GetChildren()) do
		if v:IsA("StringValue") and string.sub(v.Name, 1, 7) ~= "Perfil_" then table.insert(r, v.Name) end
	end
	table.sort(r); return r
end

-- deteccao: no import novo o Raiz em repouso tem RightVector.X = -1 (antigo +1)
function M.convencaoNova(modelo)
	local raiz = modelo:FindFirstChild("Raiz", true)
	return raiz ~= nil and raiz:IsA("Bone") and raiz.CFrame.RightVector.X < 0
end

M.forcarConvencao = nil -- true/false fixa a convencao depois de medida (nil = deteccao automatica)
local function convencao(modelo) if M.forcarConvencao ~= nil then return M.forcarConvencao end return M.convencaoNova(modelo) end
function M.cframe(c, osso, i, nova)
	local ch = c.ossos[osso]; if not ch then return nil end
	local j = i + 1
	if nova then return CFrame.new(-ch[5][j], ch[6][j], -ch[7][j], -ch[1][j], ch[2][j], -ch[3][j], ch[4][j]) end
	return CFrame.new(ch[5][j], ch[6][j], ch[7][j], ch[1][j], ch[2][j], ch[3][j], ch[4][j])
end

function M.arvore(modelo)
	local raiz = modelo:FindFirstChild("Raiz", true)
	assert(raiz and raiz:IsA("Bone"), "osso Raiz nao encontrado")
	local parte = raiz.Parent
	assert(parte:IsA("BasePart"), "Raiz nao esta direto numa parte")
	local function poseDe(inst)
		local p = Instance.new("Pose"); p.Name = inst.Name; p.Weight = 1
		for _, f in ipairs(inst:GetChildren()) do if f:IsA("Bone") then poseDe(f).Parent = p end end
		return p
	end
	local topo = Instance.new("Pose"); topo.Name = parte.Name; topo.Weight = 0
	poseDe(raiz).Parent = topo
	return topo, parte
end

local PRIORIDADE = {Repouso = "Idle", Sentado = "Idle", Deitado = "Idle", Descanso = "Idle", DormirEnrolado = "Idle",
	Farejar = "Idle", Andar = "Movement", Trote = "Movement", Corrida = "Movement", Espreita = "Movement", FarejarAndando = "Movement"}

-- monta o KeyframeSequence (fora do DataModel) com marcadores; loop ganha o quadro de fechamento (= quadro 0)
function M.montar(modelo, nome)
	local c = M.clipe(nome)
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = "Lobo_" .. c.nome; kfs.Loop = c.loop
	kfs.Priority = Enum.AnimationPriority[PRIORIDADE[c.nome] or "Action"]
	kfs:SetAttribute("Fonte", c.fonte); kfs:SetAttribute("Velocidade", c.velocidade or 0)
	local nova = convencao(modelo)
	local faltam, n = {}, 0
	local ultimo = c.loop and c.quadros or c.quadros - 1
	local kfs_por_t = {}
	for i = 0, ultimo do
		local kf = Instance.new("Keyframe"); kf.Time = i / c.fps
		local t = M.arvore(modelo)
		for _, p in ipairs(t:GetDescendants()) do
			local cf = M.cframe(c, p.Name, i % c.quadros, nova)
			if c.parcial and not c.parcial[p.Name] then p.Weight = 0                -- parcial: osso fica com a marcha
			elseif cf then p.CFrame = cf; n += 1 elseif i == 0 then table.insert(faltam, p.Name) end
		end
		t.Parent = kf; kf.Parent = kfs; kfs_por_t[i] = kf
	end
	for _, m in ipairs(c.marcadores) do
		local i = math.clamp(math.floor(m.t * c.fps + 0.5), 0, ultimo)
		local mk = Instance.new("KeyframeMarker"); mk.Name = m.nome; mk.Value = string.format("%.3f", m.t)
		kfs_por_t[i]:AddMarker(mk)
	end
	return kfs, faltam, n
end

-- aplica um quadro direto nos Bones (para conferir a conversao em Edit, por calculo)
function M.aplicarQuadro(modelo, nome, i)
	local c = M.clipe(nome); local nova = convencao(modelo)
	for _, b in ipairs(modelo:GetDescendants()) do
		if b:IsA("Bone") then b.Transform = M.cframe(c, b.Name, i, nova) or CFrame.identity end
	end
end
function M.zerar(modelo)
	for _, b in ipairs(modelo:GetDescendants()) do if b:IsA("Bone") then b.Transform = CFrame.identity end end
end
return M

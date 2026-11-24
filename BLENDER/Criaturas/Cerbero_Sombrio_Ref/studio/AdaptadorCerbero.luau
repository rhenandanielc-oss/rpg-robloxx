-- AdaptadorCerbero (ModuleScript em ServerStorage.Cerbero_Piloto) - PROPRIO DO CERBERO SOMBRIO (piloto).
-- Nao usa a ponte compartilhada dos dragoes (V14/montar_kfs_json.luau) nem clipe molde de outra criatura; segue o
-- formato do AdaptadorUrso. Dados: StringValues em Cerbero_Piloto.Dados_Clipes (studio/empacotar_clipes_cerbero.py).
-- Canais 1..7 = qx qy qz qw tx ty tz = matrix_basis do Blender (local ao osso) -> Pose.CFrame / Bone.Transform.
local M = {}
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {}
for i = 1, #A do IDX[string.byte(A, i)] = i - 1 end
local PASTA = game.ServerStorage:WaitForChild("Cerbero_Piloto")
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
function M.clipe(nome)
	if cache[nome] then return cache[nome] end
	local txt = PASTA.Dados_Clipes[nome].Value
	local L = string.split(txt, "\n")
	local h = string.split(L[1], "|")
	local c = {nome = h[1], fps = tonumber(h[2]), loop = h[3] == "1", quadros = tonumber(h[4]), ossos = {}, eventos = {}}
	for _, b in ipairs(string.split(h[5], ",")) do
		c.ossos[b] = {}
		for k = 1, 7 do c.ossos[b][k] = table.create(c.quadros, PADRAO[k]) end
	end
	for i = 2, #L do
		local p = string.split(L[i], "|")
		local b, k, v = p[1], tonumber(p[2]), p[3]
		if string.sub(v, 1, 1) == "S" then
			c.ossos[b][k] = table.create(c.quadros, tonumber(string.sub(v, 2)))
		else
			c.ossos[b][k] = dec(string.sub(v, 2), c.quadros)
		end
	end
	local ev = PASTA.Dados_Clipes:FindFirstChild("Eventos_" .. nome)
	if ev then
		for _, par in ipairs(string.split(ev.Value, ";")) do
			local kv = string.split(par, "="); c.eventos[kv[1]] = tonumber(kv[2])
		end
	end
	cache[nome] = c
	return c
end

-- CONVENCAO DOS OSSOS: imports do Roblox a partir de 10/11/2026 chegam com cada osso = osso do Blender girado 180 graus
-- no proprio Y (medido no urso e nos dragoes). Nesse caso: q (x,y,z,w) -> (-x, y, -z, w) e t -> (-x, y, -z).
-- O modelo guarda a decisao no atributo "Convencao" ("giro180y" ou "bruta"), definido depois de MEDIR (pose conhecida).
function M.convencaoNova(modelo)
	local a = modelo:GetAttribute("Convencao")
	if a ~= nil then return a == "giro180y" end
	local raiz = modelo:FindFirstChild("Raiz", true)
	return raiz ~= nil and raiz:IsA("Bone") and raiz.CFrame.RightVector.X < 0
end

function M.cframe(c, osso, i, nova)                 -- i = 0..quadros-1
	local ch = c.ossos[osso]; if not ch then return nil end
	local j = i + 1
	if nova then return CFrame.new(-ch[5][j], ch[6][j], -ch[7][j], -ch[1][j], ch[2][j], -ch[3][j], ch[4][j]) end
	return CFrame.new(ch[5][j], ch[6][j], ch[7][j], ch[1][j], ch[2][j], ch[3][j], ch[4][j])
end

-- arvore de Poses a partir da hierarquia REAL de Bones do Cerbero importado: Pose(parte com a Raiz) > Pose(Raiz) > ...
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
	return topo
end

function M.montar(modelo, nome, prioridade)
	local c = M.clipe(nome)
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = c.nome; kfs.Loop = c.loop
	kfs.Priority = prioridade or Enum.AnimationPriority.Action
	local faltam, n = {}, 0
	local nova = M.convencaoNova(modelo)
	-- laco: o JSON nao repete o quadro final (quadros = duracao*fps); o Roblox fecha o laco no ultimo keyframe, entao
	-- entra um keyframe em quadros/fps igual ao quadro 0 (duracao certa e sem salto na volta)
	local ultimo = c.loop and c.quadros or c.quadros - 1
	local kfsPorQuadro = {}
	for i = 0, ultimo do
		local kf = Instance.new("Keyframe"); kf.Time = i / c.fps
		local t = M.arvore(modelo)
		for _, p in ipairs(t:GetDescendants()) do
			local cf = M.cframe(c, p.Name, i % c.quadros, nova)
			if cf then p.CFrame = cf; n += 1 elseif i == 0 then table.insert(faltam, p.Name) end
		end
		-- O1 (17/11): osso que o clipe NAO grava nao entra na pose (senao o Animator o prende no repouso: clipe de
		-- corpo travaria os olhos e o Piscar travaria o corpo). Ancestral sem dado fica so de caminho (Weight 0).
		local function poda(p)
			local temFilho = false
			for _, f in ipairs(p:GetChildren()) do if f:IsA("Pose") and poda(f) then temFilho = true end end
			local tem = c.ossos[p.Name] ~= nil
			if not tem then p.Weight = 0 end
			if not tem and not temFilho and p ~= t then p:Destroy(); return false end
			return tem or temFilho
		end
		poda(t)
		t.Parent = kf; kf.Parent = kfs; kfsPorQuadro[i] = kf
	end
	for evn, tev in pairs(c.eventos) do                 -- eventos de sincronizacao -> KeyframeMarker no quadro mais perto
		local q = math.clamp(math.floor(tev * c.fps + 0.5), 0, ultimo)
		local mk = Instance.new("KeyframeMarker"); mk.Name = evn; mk.Value = string.format("%.3f", tev)
		kfsPorQuadro[q]:AddMarker(mk)
	end
	return kfs, faltam, n
end

-- aplica um quadro direto nos Bones (Bone.Transform): conferencia de pose conhecida do Blender
function M.aplicarQuadro(modelo, nome, i, nova)
	local c = M.clipe(nome); if nova == nil then nova = M.convencaoNova(modelo) end
	for _, b in ipairs(modelo:GetDescendants()) do
		if b:IsA("Bone") then b.Transform = M.cframe(c, b.Name, i, nova) or CFrame.identity end
	end
end
function M.zerar(modelo)
	for _, b in ipairs(modelo:GetDescendants()) do if b:IsA("Bone") then b.Transform = CFrame.identity end end
end
return M

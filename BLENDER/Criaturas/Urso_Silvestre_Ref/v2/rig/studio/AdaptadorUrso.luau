-- AdaptadorUrso (ModuleScript em ServerStorage.Urso_v2_Piloto) - ADAPTADOR PROPRIO DO URSO SILVESTRE v2.
-- Nao altera nem usa a ponte compartilhada (V14/montar_kfs_json.luau), nem clipe molde de outra criatura.
-- Dados: StringValues em ServerStorage.Urso_v2_Piloto.Dados_Clipes, gerados por studio/empacotar_clipes.py a partir
-- de rig/clipes/Urso_<clipe>.json (o place tem HttpEnabled=false; a configuracao nao foi alterada).
-- Cada canal: S<valor> constante ou E<deltas> (inteiros x1e4, delta, zigzag, base64 5 bits + continuacao).
-- Canais 1..7 = qx qy qz qw tx ty tz = matrix_basis do Blender (local ao osso) -> Pose.CFrame / Bone.Transform.
local M = {}
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local IDX = {}
for i = 1, #A do IDX[string.byte(A, i)] = i - 1 end
local PASTA = game.ServerStorage:WaitForChild("Urso_v2_Piloto")

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
	local c = {nome = h[1], fps = tonumber(h[2]), loop = h[3] == "1", quadros = tonumber(h[4]), ossos = {}}
	-- formato compacto (lote 2, 04/11): o cabecalho lista os ossos e os canais constantes iguais ao padrao
	-- (quaternion identidade, translacao zero) sao omitidos; aqui eles sao preenchidos
	local PADRAO = {0, 0, 0, 1, 0, 0, 0}
	if h[5] then
		for _, b in ipairs(string.split(h[5], ",")) do
			c.ossos[b] = {}
			for k = 1, 7 do c.ossos[b][k] = table.create(c.quadros, PADRAO[k]) end
		end
	end
	for i = 2, #L do
		local p = string.split(L[i], "|")
		local b, k, v = p[1], tonumber(p[2]), p[3]
		c.ossos[b] = c.ossos[b] or {}
		if string.sub(v, 1, 1) == "S" then
			local x = tonumber(string.sub(v, 2)); local t = table.create(c.quadros, x); c.ossos[b][k] = t
		else
			c.ossos[b][k] = dec(string.sub(v, 2), c.quadros)
		end
	end
	cache[nome] = c
	return c
end

-- CONVENCAO DOS OSSOS (10/11/2026): o Import 3D do Roblox mudou desde 04/11. O mesmo GLB importado hoje chega com cada
-- osso = antigo * giro de 180 graus no Y do proprio osso (medido: 180,0 em todos os 31 ossos; a sela v3 importada hoje
-- bate com o urso de hoje em 0,03). Os clipes (matrix_basis do Blender) foram validados no import ANTIGO (04/11); num
-- import NOVO o canal local precisa ser conjugado por Ry(180): q (x,y,z,w) -> (-x, y, -z, w) e t (x,y,z) -> (-x, y, -z).
-- Deteccao pelo Raiz em repouso (local a parte): antigo RightVector.X = +1, novo = -1.
function M.convencaoNova(modelo)
	local raiz = modelo:FindFirstChild("Raiz", true)
	return raiz ~= nil and raiz:IsA("Bone") and raiz.CFrame.RightVector.X < 0
end

function M.cframe(c, osso, i, nova)                 -- i = 0..quadros-1; nova = modelo importado na convencao nova
	local ch = c.ossos[osso]; if not ch then return nil end
	local j = i + 1
	if nova then return CFrame.new(-ch[5][j], ch[6][j], -ch[7][j], -ch[1][j], ch[2][j], -ch[3][j], ch[4][j]) end
	return CFrame.new(ch[5][j], ch[6][j], ch[7][j], ch[1][j], ch[2][j], ch[3][j], ch[4][j])
end

-- checagem dos dados: quantidade de quadros por canal e soma de cada canal (comparada com o Python)
function M.somas(nome)
	local c = M.clipe(nome); local r = {}
	for b, ch in pairs(c.ossos) do
		for k = 1, 7 do
			assert(#ch[k] == c.quadros, nome .. " " .. b .. " canal " .. k .. " com " .. #ch[k] .. " quadros")
			local s = 0; for _, x in ipairs(ch[k]) do s += x end; r[b .. "|" .. k] = s
		end
	end
	return r
end

-- arvore de Poses a partir da hierarquia REAL de Bones do urso importado: Pose(parte que contem a Raiz) > Pose(Raiz) > ...
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
	local kfs = Instance.new("KeyframeSequence"); kfs.Name = c.nome; kfs.Loop = c.loop; kfs.Priority = prioridade
	local faltam, n = {}, 0
	local nova = M.convencaoNova(modelo)
	-- loop: os JSON do urso NAO repetem o quadro final (quadros = duracao*fps); o Roblox fecha o loop no ultimo
	-- keyframe, entao acrescenta-se um keyframe em quadros/fps igual ao quadro 0 (duracao certa e sem salto na volta)
	local ultimo = c.loop and c.quadros or c.quadros - 1
	for i = 0, ultimo do
		local kf = Instance.new("Keyframe"); kf.Time = i / c.fps
		local t = M.arvore(modelo)
		for _, p in ipairs(t:GetDescendants()) do
			local cf = M.cframe(c, p.Name, i % c.quadros, nova)
			if cf then p.CFrame = cf; n += 1 elseif i == 0 then table.insert(faltam, p.Name) end
		end
		t.Parent = kf; kf.Parent = kfs
	end
	return kfs, faltam, n
end

-- aplica um quadro direto nos Bones (Bone.Transform), para conferir a conversao com poses conhecidas do Blender
function M.aplicarQuadro(modelo, nome, i)
	local c = M.clipe(nome); local nova = M.convencaoNova(modelo)
	for _, b in ipairs(modelo:GetDescendants()) do
		if b:IsA("Bone") then b.Transform = M.cframe(c, b.Name, i, nova) or CFrame.identity end
	end
end
function M.zerar(modelo)
	for _, b in ipairs(modelo:GetDescendants()) do if b:IsA("Bone") then b.Transform = CFrame.identity end end
end
return M

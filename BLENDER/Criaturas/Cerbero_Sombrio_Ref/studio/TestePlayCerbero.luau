-- TestePlayCerbero (ModuleScript em ServerStorage.Cerbero_Piloto) - toca os clipes do Cerbero no PLAY, SEM publicar:
-- AnimationClipProvider:RegisterAnimationClip(kfs) gera um id temporario valido so no Studio.
-- verificar(nome): toca o clipe no Animator do Cerbero de teste e, em instantes amostrados, compara o Bone.Transform
-- tocado com o quadro esperado do AdaptadorCerbero (erro angular e de posicao) - prova de que o clipe foi reproduzido.
local ACP = game:GetService("AnimationClipProvider")
local M = {}
local PASTA = game.ServerStorage.Cerbero_Piloto
local AD = require(PASTA.AdaptadorCerbero)
local modelo = workspace:WaitForChild("Teste_Cerbero"):WaitForChild("Cerbero_Sombrio")
local estado = {ids = {}, faixas = {}, atual = nil}

local function animator()
	local ac = modelo:FindFirstChildOfClass("AnimationController")
	local an = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator")
	an.Parent = ac
	return an
end
M.animator = animator

function M.faixa(nome)
	if estado.faixas[nome] then return estado.faixas[nome] end
	local kfs = PASTA.Animacoes:FindFirstChild(nome)
	assert(kfs, "clipe nao montado: " .. nome)
	estado.ids[nome] = estado.ids[nome] or ACP:RegisterAnimationClip(kfs)
	local a = Instance.new("Animation"); a.AnimationId = estado.ids[nome]
	estado.faixas[nome] = animator():LoadAnimation(a)
	return estado.faixas[nome]
end

function M.parar()
	for _, f in pairs(estado.faixas) do if f.IsPlaying then f:Stop(0) end end
	estado.atual = nil
end

function M.tocar(nome, misturar, vel)
	M.parar()
	local f = M.faixa(nome)
	f:Play(misturar or 0, 1, vel or 1)
	estado.atual = f
	return f
end

-- compara o osso tocado com o esperado nos instantes amostrados (pausando a faixa no tempo exato)
local OSSOS = {"Pelve", "Coluna2", "PescocoC2", "CabecaC", "MandibulaC", "CabecaE", "CabecaD", "BracoE", "AntebracoD", "CoxaE", "PeD", "Cauda3"}
function M.verificar(nome, amostras)
	local c = AD.clipe(nome); local nova = AD.convencaoNova(modelo)
	local f = M.tocar(nome); f:AdjustSpeed(0)
	local dur = (c.loop and c.quadros or c.quadros - 1) / c.fps
	amostras = amostras or 5
	local piorAng, piorPos = 0, 0
	for k = 0, amostras - 1 do
		local q = math.floor((c.quadros - 1) * k / math.max(1, amostras - 1) + 0.5)
		local tp = q / c.fps
		if not c.loop and k == amostras - 1 then tp -= 0.004 end    -- no fim exato a faixa termina e solta a pose
		f.TimePosition = tp
		task.wait(0.2)                                          -- 0,05 s nao bastava: o Animator ainda mostrava o instante anterior
		for _, nb in ipairs(OSSOS) do
			local b = modelo:FindFirstChild(nb, true)
			local esp = AD.cframe(c, nb, q, nova)
			if b and esp then
				local d = esp:Inverse() * b.Transform
				local _, ang = d:ToAxisAngle()
				piorAng = math.max(piorAng, math.deg(math.abs(ang))); piorPos = math.max(piorPos, d.Position.Magnitude)
			end
		end
	end
	M.parar()
	return {nome = nome, tocou = true, comprimento = f.Length, esperado = dur, piorAng = piorAng, piorPos = piorPos}
end
return M

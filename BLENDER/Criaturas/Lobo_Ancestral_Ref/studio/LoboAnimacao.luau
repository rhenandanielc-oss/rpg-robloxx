-- LoboAnimacao (ModuleScript em ReplicatedStorage.LoboAncestral) - controlador de animacoes do Lobo Ancestral (15/11/2026).
-- Fonte: BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/LoboAnimacao.luau. So em Play: monta o KeyframeSequence pelo
-- AdaptadorLobo e registra com AnimationClipProvider (id temporario; nada e publicado). O KFS e montado uma vez por clipe
-- (todos os lobos usam o mesmo esqueleto) e as faixas sao carregadas por modelo.
local ACP = game:GetService("AnimationClipProvider")
local Ad = require(script.Parent:WaitForChild("AdaptadorLobo"))
Ad.forcarConvencao = true          -- medido 15/11 no Testes-loboancestral: convencao nova erro 0,002 stud (antiga 2,0)
local M = {}
local ids, kfsCache = {}, {}
local LOCOMOCAO = {Repouso = true, Andar = true, Trote = true, Corrida = true, Espreita = true, FarejarAndando = true,
	Sentado = true, Deitado = true, Descanso = true, DormirEnrolado = true, Farejar = true}

function M.id(modelo, nome)
	if not ids[nome] then
		local kfs = Ad.montar(modelo, nome)
		kfsCache[nome] = kfs
		ids[nome] = ACP:RegisterAnimationClip(kfs)
	end
	return ids[nome]
end
function M.clipe(nome) return Ad.clipe(nome) end
function M.nomes() return Ad.nomes() end

-- pre-carrega (um clipe por quadro, para nao travar)
function M.preCarregar(modelo, lista)
	for _, n in ipairs(lista or Ad.nomes()) do M.id(modelo, n); task.wait() end
end

function M.preparar(modelo)
	local ac = modelo:FindFirstChildOfClass("AnimationController")
	local an = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
	local C = {modelo = modelo, animator = an, faixas = {}, base = nil, acao = nil}
	function C.faixa(nome)
		local f = C.faixas[nome]
		if not f then
			local a = Instance.new("Animation"); a.AnimationId = M.id(modelo, nome)
			f = an:LoadAnimation(a); C.faixas[nome] = f
		end
		return f
	end
	-- base = laco de locomocao/repouso (troca com fade); acao = clipe unico por cima (prioridade Action)
	function C.base(nome, fade, vel)
		local f = C.faixa(nome)
		if C.baseNome ~= nome then
			if C.baseNome and C.faixas[C.baseNome] then C.faixas[C.baseNome]:Stop(fade or 0.25) end
			f:Play(fade or 0.25); C.baseNome = nome
		end
		f:AdjustSpeed(vel or 1)
		return f
	end
	function C.acao(nome, fade, vel)
		if C.acaoNome and C.faixas[C.acaoNome] and C.faixas[C.acaoNome].IsPlaying then C.faixas[C.acaoNome]:Stop(fade or 0.15) end
		local f = C.faixa(nome); f:Play(fade or 0.15); f:AdjustSpeed(vel or 1); C.acaoNome = nome
		return f
	end
	function C.pararTudo(fade)
		for _, f in pairs(C.faixas) do f:Stop(fade or 0.2) end
		C.baseNome, C.acaoNome = nil, nil
	end
	return C
end
M.LOCOMOCAO = LOCOMOCAO
return M

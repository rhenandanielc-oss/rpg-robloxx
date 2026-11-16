--!nonstrict
-- TestePlay_LoboArtico (roda no CLIENTE do Play via execute_luau, em task.spawn; nada fica instalado no place; 15/11/2026)
-- Animacao, deslocamento e medidas sao locais do cliente (o que a camera mostra).
-- Toca as 34 acoes (anim_v41, ReplicatedStorage.Animacoes_LoboArtico) numa linha do tempo propria: cada passo fixa
-- TimePosition (velocidade 0), entao as emendas entram no quadro exato e o deslocamento (Movimento_LoboArtico) fica em fase.
-- Mede por acao: altura minima de cada pata, deslize horizontal das patas apoiadas, focinho/queixo na agua e no alimento.
-- Resultado: atributo "Resultado_TestePlay" da pasta (atualizado a cada acao) + print "LOBO_TESTE".
-- Antes de rodar: no servidor, LoboArtico_LOW.ModelStreamingMode = Persistent e o personagem perto da area (streaming).
-- Nunca esperar o fim numa chamada longa do execute_luau (a conexao cai); consultar o atributo "Etapa" em chamadas curtas.
local pasta = workspace:WaitForChild("Teste_LoboArtico")
local RS = game:GetService("RunService")
local KSP = game:GetService("KeyframeSequenceProvider")

local lobo = pasta:WaitForChild("LoboArtico_LOW")
local an = lobo.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", lobo.AnimationController)
local lib = game.ReplicatedStorage:WaitForChild("Animacoes_LoboArtico")
local MOV = require(game.ReplicatedStorage.Animacoes_LoboArtico:WaitForChild("Movimento_LoboArtico"))
local CHAO = 1500
local escala = pasta:GetAttribute("Escala") or 1     -- 1 = tempo real; o servidor do Studio roda ~15 fps

local tracks = {}
local function track(n)
	if not tracks[n] then
		local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(lib["LoboArtico_" .. n])
		local tr = an:LoadAnimation(a)
		local t0 = os.clock(); while tr.Length == 0 and os.clock() - t0 < 3 do task.wait() end
		tracks[n] = tr
	end
	return tracks[n]
end

-- deslocamento do clipe no tempo local t (s): CFrame no espaco do modelo
local function mover(n, t, len)
	local c = MOV.Curvas[n]
	if c then
		local f = math.clamp(t * MOV.Fps, 0, #c - 1); local i = math.floor(f); local a = f - i
		local p, q = c[i + 1], c[math.min(i + 2, #c)]
		local dx, dz, g = p[1] + (q[1] - p[1]) * a, p[2] + (q[2] - p[2]) * a, p[3] + (q[3] - p[3]) * a
		return CFrame.new(dx, 0, dz) * CFrame.Angles(0, g, 0)
	end
	local v = MOV.Velocidade[n]
	if v then return CFrame.new(0, 0, -v * t) end
	return CFrame.identity
end

local PATAS = {Dedos_E = 0.46152, Dedos_D = 0.48715, DedosPe_E = 0.48285, DedosPe_D = 0.40998}
-- a ponta do osso dos dedos fica ~0,12 acima do chao no repouso: "apoio" = ate 0,04 acima disso (inclui o rolamento antes
-- de a pata subir; a medida rigorosa de deslize foi feita no Edit, com apoio = ate 0,01 do ponto mais baixo de cada pata)
local LIM_APOIO = 0.12 + 0.04
local ossos = {}
for n in pairs(PATAS) do ossos[n] = lobo:FindFirstChild(n, true) end
local mand, cab = lobo:FindFirstChild("Mandibula", true), lobo:FindFirstChild("Cabeca", true)
local function ponta(b, l) return (b.TransformedWorldCFrame * CFrame.new(0, l, 0)).Position end

local linhas = {}
local function registrar(s) table.insert(linhas, s); print("LOBO_TESTE", s); pasta:SetAttribute("Resultado_TestePlay", table.concat(linhas, "
")) end

-- toca um segmento: clipe n por dur segundos (laco: repete); devolve o pivo final
local function tocar(n, dur, opc)
	opc = opc or {}
	local tr = track(n); local len = tr.Length
	dur = dur or len
	local base = lobo:GetPivot()
	for _, o in pairs(tracks) do if o ~= tr and o.IsPlaying then o:Stop(opc.fade or 0) end end
	if not tr.IsPlaying then tr:Play(opc.fade or 0, 1, 0) end
	tr:AdjustSpeed(0)
	local med = {min = {}, deslize = {}, apoio = {}, inicio = {}, focinhoMin = math.huge, queixoMin = math.huge, passos = 0}
	for k in pairs(PATAS) do med.min[k] = math.huge; med.deslize[k] = 0 end
	local t, real0 = 0, os.clock()
	while t < dur do
		local dt = RS.PreAnimation:Wait() * escala          -- antes do passo de animacao: fixa tempo e posicao
		t = math.min(t + dt, dur)
		local tl = tr.Looped and (t % len) or math.min(t, len - 1e-3)
		tr.TimePosition = tl
		local cf
		if MOV.Velocidade[n] then cf = mover(n, t, len) else cf = mover(n, math.min(t, len), len) end
		lobo:PivotTo(base * cf)
		RS.PreSimulation:Wait()                              -- depois do passo de animacao: mede a pose aplicada
		med.passos += 1
		for k, l in pairs(PATAS) do
			local p = ponta(ossos[k], l); local h = p.Y - CHAO
			med.min[k] = math.min(med.min[k], h)
			if h < LIM_APOIO then
				if med.apoio[k] then med.deslize[k] = math.max(med.deslize[k], (Vector3.new(p.X, 0, p.Z) - med.inicio[k]).Magnitude)
				else med.apoio[k] = true; med.inicio[k] = Vector3.new(p.X, 0, p.Z) end
			else med.apoio[k] = false end
		end
		local pm = ponta(mand, 1.08703); local pc = ponta(cab, 1.56518)
		med.queixoMin = math.min(med.queixoMin, pm.Y - CHAO); med.focinhoMin = math.min(med.focinhoMin, pc.Y - CHAO)
		med.ultimoQueixo = pm; med.ultimoFocinho = pc
	end
	local s = string.format("%s dur=%.2f len=%.3f real=%.1fs passos=%d minPatas[DE=%.3f DD=%.3f TE=%.3f TD=%.3f] deslizeApoio[DE=%.3f DD=%.3f TE=%.3f TD=%.3f] queixoMin=%.3f focinhoMin=%.3f",
		n, dur, len, os.clock() - real0, med.passos, med.min.Dedos_E, med.min.Dedos_D, med.min.DedosPe_E, med.min.DedosPe_D,
		med.deslize.Dedos_E, med.deslize.Dedos_D, med.deslize.DedosPe_E, med.deslize.DedosPe_D, med.queixoMin, med.focinhoMin)
	if opc.extra then s ..= " " .. opc.extra(med) end
	registrar(s)
	pasta:SetAttribute("Etapa", n)
	return med
end

local function ir(cf) lobo:PivotTo(cf) end
local function ciclos(n, k) return track(n).Length * k end

-- ===== Roteiro =====
local roteiro = pasta:GetAttribute("Roteiro") or "tudo"
local LARGADA = CFrame.new(-640, CHAO, -530)                      -- frente -Z, pista temporaria ate z=-1000
local POCA_Z = -592                                               -- borda sul da poca (agua de -608 a -592, x -584..-568)

if roteiro == "tudo" or roteiro == "locomocao" then
	pasta:SetAttribute("Bloco", "locomocao")
	ir(LARGADA)
	tocar("Repouso", 2)
	tocar("Andar", ciclos("Andar", 2)); tocar("AndarParaTrote"); tocar("Trote", ciclos("Trote", 3)); tocar("TroteParaCorrida")
	tocar("Corrida", ciclos("Corrida", 4)); tocar("CorridaParaTrote"); tocar("Trote", ciclos("Trote", 2)); tocar("TroteParaAndar")
	tocar("Andar", ciclos("Andar", 2)); tocar("Repouso", 1.5, {fade = 0.3})
	tocar("Arrancada"); tocar("Corrida", ciclos("Corrida", 2)); tocar("Frenagem"); tocar("Repouso", 1)
	tocar("VirarEsquerda"); tocar("Repouso", 0.5); tocar("VirarDireita"); tocar("Repouso", 1)
end
if roteiro == "tudo" or roteiro == "descanso" then
	pasta:SetAttribute("Bloco", "descanso")
	ir(CFrame.new(-620, CHAO, -560))
	tocar("Repouso", 1)
	tocar("Deitar"); tocar("Descanso", 3); tocar("Adormecer"); tocar("Dormindo", 4); tocar("Despertar"); tocar("Descanso", 2)
	tocar("LevantarDeitado"); tocar("Repouso", 1)
	tocar("Sentar"); tocar("Sentado", 3); tocar("LevantarSentado"); tocar("Repouso", 1)
end
if roteiro == "tudo" or roteiro == "vida" then
	pasta:SetAttribute("Bloco", "vida")
	ir(CFrame.new(-620, CHAO, -560))
	tocar("Farejar"); tocar("Farejando", 4); tocar("PararFarejar"); tocar("Repouso", 1)
	-- comer: alimento de ensaio sob a boca (Comendo: queixo 0,20-0,47 acima do chao, 3,65-4,28 a frente da Raiz)
	local raiz = lobo:FindFirstChild("Raiz", true).WorldPosition
	local comida = pasta:FindFirstChild("Comida_Ensaio")
	if comida then comida.Size = Vector3.new(1.4, 0.2, 1.0); comida.CFrame = CFrame.new(raiz.X, CHAO + 0.1, raiz.Z - 4.0) end
	local topo = CHAO + 0.2
	tocar("Comer"); tocar("Comendo", 5, {extra = function(m) return string.format("queixo-topoAlimento=%.3f", m.queixoMin + CHAO - topo) end}); tocar("PararComer"); tocar("Repouso", 1)
	-- beber: patas na margem sul, queixo sobre a agua (pivo = Raiz + 0,708 atras)
	ir(CFrame.new(-576, CHAO, POCA_Z + 3.92 + 0.708))
	tocar("Repouso", 1)
	tocar("Beber"); tocar("Bebendo", 3, {extra = function(m)
		local q, f = m.ultimoQueixo, m.ultimoFocinho
		local naAgua = q.X > -584 and q.X < -568 and q.Z > -608 and q.Z < -592
		return string.format("queixoNaAgua=%s queixoZ=%.2f focinhoY-agua=%.3f", tostring(naAgua), q.Z, f.Y - CHAO)
	end}); tocar("PararBeber"); tocar("Repouso", 1)
	ir(CFrame.new(-620, CHAO, -560))
	tocar("Uivar"); tocar("Uivando", 5); tocar("PararUivar"); tocar("Repouso", 1)
	tocar("Sacudir"); tocar("Repouso", 2)
end
for _, o in pairs(tracks) do o:Stop(0) end
local v = pasta:FindFirstChild("Resultado_TestePlay") or Instance.new("StringValue")
v.Name = "Resultado_TestePlay"; v.Value = table.concat(linhas, "\n"); v.Parent = pasta
pasta:SetAttribute("Etapa", "FIM")

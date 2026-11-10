-- teste_golpe_colossal.luau - rodar no PLAY, datamodel SERVER (execute_luau). Monta o cenario TEMPORARIO do teste
-- (bonecos, parede, plataforma alta: tudo some ao parar o Play) e roda a bateria em task.spawn; resultado em _G.URSO_GC.
-- Antes: no CLIENTE, require(ReplicatedStorage.Urso_v2_Lab.EfeitosUrso_Cliente).iniciar(ReplicatedStorage.Urso_v2_Lab)
-- (o servidor cria os RemoteEvents ao ser carregado). Parametros = LABORATORIO.
local S = require(game.ServerStorage.Urso_v2_Piloto.Poderes.PoderesUrso_Servidor)
local urso = workspace.Teste_Urso_v2.Urso_Silvestre_v2_Piloto
local CS = game:GetService("CollectionService")
local cen = Instance.new("Folder"); cen.Name = "CenarioTesteGC"; cen.Parent = workspace
local piv = urso:GetPivot(); local P0 = piv.Position                     -- chao da plataforma = P0.Y
local function rel(x, y, z) return piv:PointToWorldSpace(Vector3.new(x, y, z)) end   -- frente do urso = -Z local
local function boneco(nome, pos)
	local m = Instance.new("Model"); m.Name = nome
	local r = Instance.new("Part"); r.Name = "HumanoidRootPart"; r.Size = Vector3.new(2, 2, 1); r.Anchored = true; r.CanCollide = false
	r.Transparency = 0.3; r.Color = Color3.fromRGB(200, 60, 60); r.CFrame = CFrame.new(pos + Vector3.new(0, 3, 0)); r.Parent = m
	local t = Instance.new("Part"); t.Name = "Torso"; t.Size = Vector3.new(2, 2, 1); t.Anchored = true; t.CFrame = r.CFrame; t.Parent = m
	local hd = Instance.new("Part"); hd.Name = "Head"; hd.Size = Vector3.new(1.2, 1.2, 1.2); hd.Anchored = true; hd.CFrame = r.CFrame + Vector3.new(0, 1.6, 0); hd.Parent = m
	local h = Instance.new("Humanoid"); h.HipHeight = 2; h.MaxHealth = 100; h.Health = 100; h.Parent = m
	m.PrimaryPart = r; m:SetAttribute("AlvoTesteUrso", true); m.Parent = cen; CS:AddTag(m, "AlvoTesteUrso")
	return m
end
local function parte(nome, cf, tam)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.Size = tam; p.CFrame = cf; p.Color = Color3.fromRGB(90, 90, 100); p.Parent = cen; return p
end
-- impacto esperado ~2,3 studs a frente do pivo (meio das patas dianteiras): alvos medidos a partir dele
local B = {
	perto = boneco("Alvo_Perto_8", rel(0, 0, -10)),           -- dentro do raio (~8 do impacto)
	longe = boneco("Alvo_Longe_20", rel(0, 0, -22)),          -- fora do raio (~20)
	parede = boneco("Alvo_AtrasParede", rel(9, 0, -2.3)),     -- dentro do raio mas atras de parede
	alto = boneco("Alvo_Plataforma_6", rel(-9, 6, -2.3)),     -- dentro do raio horizontal, 6 studs acima
	e1 = boneco("Alvo_Grupo_E", rel(5, 0, -6)), d1 = boneco("Alvo_Grupo_D", rel(-5, 0, -6)),
}
parte("Parede", CFrame.new(rel(5.5, 4, -2.3)), Vector3.new(1, 8, 6))
parte("PlataformaAlta", CFrame.new(rel(-9, 5.5, -2.3)), Vector3.new(6, 1, 6))     -- topo em +6
local function vidas() local v = {}; for k, m in pairs(B) do v[k] = m.Humanoid.Health end; return v end
local function curar() for _, m in pairs(B) do m.Humanoid.Health = 100; m:SetAttribute("UltimoAtaqueUrso", nil) end end
local function esperarFim() local t0 = os.clock(); repeat task.wait(0.05) until (os.clock() - t0 > 8) or not (S.log[#S.log] and S.log[#S.log].ev == "inicio") ; task.wait(1.4) end
_G.URSO_GC = {fase = "rodando"}
task.spawn(function()
	local R = {}; local L = S.LAB.GolpeColossal; local rec0 = L.recarga
	urso:SetAttribute("EnergiaLab", 100)
	local plr = game.Players:GetPlayers()[1]; urso:SetAttribute("DonoUserId", plr and plr.UserId or nil)
	-- 1) golpe normal (1x): acerto/erro, alcance, parede, altura, varios alvos, dano unico por modelo
	curar(); local n0 = #S.log; local t0 = os.clock()
	local ok, id = S.golpeColossal(urso, "teste1")
	repeat task.wait() until (#S.log > n0 + 1) or os.clock() - t0 > 6
	task.wait(0.3)
	local imp; for i = n0 + 1, #S.log do if S.log[i].ev == "impacto" then imp = S.log[i] end end
	R.normal = {aceito = ok, impacto_tp = imp and imp.tp, tempo_real = imp and (os.clock() - t0 - 0.3), ponto = imp and tostring(imp.pos),
		feridos = imp and imp.feridos, motivos = imp and imp.motivos, vidas = vidas()}
	task.wait(1.6)
	-- 2) spam: 10 pedidos no mesmo quadro (recarga zerada) + pedido depois do fim dentro da recarga
	L.recarga = 3; curar(); task.wait(0.2)
	local aceitos, recusas = 0, {}
	for i = 1, 10 do local a, por = S.golpeColossal(urso, "spam" .. i); if a then aceitos += 1 else recusas[por] = (recusas[por] or 0) + 1 end end
	task.wait(2.6)
	local a2, por2 = S.golpeColossal(urso, "dentro_recarga")
	R.spam = {aceitos = aceitos, recusas = recusas, depois_do_fim = a2 and "aceito" or por2, vidas = vidas()}
	-- 3) interrupcao antes do contato: sem dano e sem efeito
	task.wait(3.2); curar(); n0 = #S.log
	S.golpeColossal(urso, "interromper"); task.wait(0.6); S.interromper(urso); task.wait(1.0)
	local evs = {}; for i = n0 + 1, #S.log do table.insert(evs, S.log[i].ev) end
	R.interrupcao = {eventos = evs, vidas = vidas()}
	-- 4) lento (1/3): contato no mesmo tempo de CLIPE, dano 1x, tempo real ~3x
	task.wait(3.2); curar(); n0 = #S.log; t0 = os.clock()
	local okL = S.golpeColossal(urso, "lento")
	local f = nil; for _, tr in ipairs(urso:FindFirstChildOfClass("AnimationController").Animator:GetPlayingAnimationTracks()) do if tr.Animation and tr.Speed > 0 and tr.Priority == Enum.AnimationPriority.Action2 then f = tr end end
	if f then f:AdjustSpeed(1 / 3) end
	repeat task.wait() until os.clock() - t0 > 8 or (S.log[#S.log] and S.log[#S.log].ev == "impacto" and #S.log > n0)
	local impL = S.log[#S.log]
	R.lento = {aceito = okL, impacto_tp = impL.tp, velocidade = impL.velocidade, tempo_real = os.clock() - t0, feridos = impL.feridos, vidas = vidas()}
	task.wait(5.5)
	-- 5) energia insuficiente e urso incapacitado
	urso:SetAttribute("EnergiaLab", 5); local aE, pE = S.golpeColossal(urso, "sem_energia"); urso:SetAttribute("EnergiaLab", 100)
	urso:SetAttribute("Incapacitado", true); local aI, pI = S.golpeColossal(urso, "incapacitado"); urso:SetAttribute("Incapacitado", nil)
	R.recusas = {energia = aE and "aceito" or pE, incapacitado = aI and "aceito" or pI}
	L.recarga = rec0
	_G.URSO_GC = {fase = "fim", R = R}
end)
return "bateria iniciada"

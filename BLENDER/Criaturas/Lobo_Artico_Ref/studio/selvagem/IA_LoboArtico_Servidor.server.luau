-- IA_LoboArtico_Servidor (Script, ServerScriptService) - alcateias selvagens do Lobo Artico na Tundra + ovo na toca. r4 20/11/2026 (LOBO SOLITARIO, LOCAL nao instalado: decisao do usuario 20/11 = um lobo por territorio/toca;
-- spawn idempotente + migracao dos grupos da r3 com backup dos excedentes. Copia: IA_LoboArtico_Servidor_r3.) r3 (alvo da coleta por UserId + motivo; copia da r2: IA_LoboArtico_Servidor_r2). r2 19/11/2026 (3 alcateias).
-- Usuario 19/11: "prossiga com a ida, ninhos, spawn no habitat, IA selvagem" e "o lobo ja tem cavernas para esconder seus
-- ovos e dormir la" -> ovo escondido no Abrigo_Filhotes da toca de cada alcateia; a alcateia dorme no Descanso_Toca.
-- Habitat (ja existente, M5.1): Workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico.<Alcateia>.
-- Regras OFICIAIS usadas (urso-silvestre.md / lobo-artico.md): ovo reaparece em 30-60 min; o primeiro jogador a terminar
-- a coleta leva; coleta validada no servidor; guardioes adultos selvagens nao sao capturaveis.
-- [PROPOSTA]: 3 lobos por alcateia (Lider Adulto, Guardiao Pre-adulto, Membro Adulto), 1 ovo por toca, coleta de 4 s
-- segurando a 10 studs, visual do ovo provisorio (sem modelo de ovo do lobo ainda). Nenhum item e entregue: dispara
-- ServerStorage.IA_LoboArtico_Eventos.OvoColetado(jogador, alcateia) para o sistema de inventario futuro (igual ao Urso).
-- Liga/desliga: workspace:SetAttribute("IA_LoboArtico_Ativa", false) desliga as IAs; Alcateias ativas em CFG.
local Players = game:GetService("Players")
local SS = game:GetService("ServerStorage")
local CFG = {
	alcateias = {"Alcateia_Floresta", "Alcateia_Macico", "Alcateia_Campos"},   -- r2: as 3 alcateias do habitat (piloto Floresta testado 19/11)
	membros = {{"Solitario", "Adulto"}},                                        -- r4: um lobo por territorio (era Lider/Guardiao/Membro)
	sistema = "LoboArtico_Selvagem",                                            -- r4: marca dos NPCs deste sistema (migracao segura)
	ovo = {seguraSeg = 4, dist = 10, reaparecerMin = {30, 60}},
}
local modelo = SS:WaitForChild("LoboArtico_Selvagem_Modelo")
local habitats = workspace:WaitForChild("Tundra_Congelada"):WaitForChild("Habitats"):WaitForChild("Ecologia_Fauna"):WaitForChild("Lobo_Artico")
local raizIA = workspace:FindFirstChild("Criaturas_IA") or Instance.new("Folder"); raizIA.Name = "Criaturas_IA"; raizIA.Parent = workspace
local raizLobos = raizIA:FindFirstChild("Lobos_Articos") or Instance.new("Folder"); raizLobos.Name = "Lobos_Articos"; raizLobos.Parent = raizIA
local eventos = SS:FindFirstChild("IA_LoboArtico_Eventos") or Instance.new("Folder"); eventos.Name = "IA_LoboArtico_Eventos"; eventos.Parent = SS
local function evento(n) local e = eventos:FindFirstChild(n) or Instance.new("BindableEvent"); e.Name = n; e.Parent = eventos; return e end
local evColetado, evReapareceu = evento("OvoColetado"), evento("OvoReapareceu")
if workspace:GetAttribute("IA_LoboArtico_Ativa") == nil then workspace:SetAttribute("IA_LoboArtico_Ativa", true) end

local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
local function chao(p)
	rp.FilterDescendantsInstances = {habitats, raizIA}
	local r = workspace:Raycast(p + Vector3.new(0, 3, 0), Vector3.new(0, -30, 0), rp)
	return r and r.Position or p
end

-- ovo na toca ------------------------------------------------------------------------------------------------------------
local function criarOvo(hab, pastaAlc)
	local abrigo = hab:FindFirstChild("Abrigo_Filhotes", true); if not abrigo then return end
	local base = chao(abrigo.Position)
	local ovo = Instance.new("Part"); ovo.Name = "Ovo_LoboArtico"; ovo.Anchored = true; ovo.CanCollide = false; ovo.CanQuery = false; ovo.CanTouch = false
	ovo.Size = Vector3.new(1.3, 1.3, 1.3); ovo.Material = Enum.Material.SmoothPlastic; ovo.Color = Color3.fromRGB(226, 232, 240)
	local me = Instance.new("SpecialMesh"); me.MeshType = Enum.MeshType.Sphere; me.Scale = Vector3.new(1, 1.35, 1); me.Parent = ovo
	ovo.CFrame = CFrame.new(base + Vector3.new(0, 0.85, 0)) * CFrame.Angles(math.rad(12), math.random() * 6.28, 0)
	ovo:SetAttribute("Provisorio", "visual de ovo [PROPOSTA]; modelo do ovo do Lobo Artico pendente")
	local pr = Instance.new("ProximityPrompt"); pr.ActionText = "Pegar o ovo"; pr.ObjectText = "Ovo de Lobo Artico"
	pr.HoldDuration = CFG.ovo.seguraSeg; pr.MaxActivationDistance = CFG.ovo.dist; pr.RequiresLineOfSight = false; pr.Parent = ovo
	ovo.Parent = pastaAlc
	local geracao, coletado = 0, false
	-- r3: alvo por UserId com motivo "coleta" (oficial: a coleta e SEMPRE percebida -> Defesa imediata, sem aviso)
	local function alvoColeta(j, seg)
		pastaAlc:SetAttribute("AlvoId", j.UserId); pastaAlc:SetAttribute("AlvoMotivo", "coleta"); pastaAlc:SetAttribute("AlvoAte", os.clock() + seg)
		pastaAlc:SetAttribute("Tensao", "Defesa"); pastaAlc:SetAttribute("TensaoId", j.UserId); pastaAlc:SetAttribute("Motivo", "coleta do ovo")
	end
	pr.PromptButtonHoldBegan:Connect(function(j) alvoColeta(j, 20) end)   -- quem comeca a pegar o ovo vira alvo da alcateia
	pr.Triggered:Connect(function(j)
		if coletado then return end
		local r = j.Character and j.Character:FindFirstChild("HumanoidRootPart")
		local h = j.Character and j.Character:FindFirstChildOfClass("Humanoid")
		if not (r and h and h.Health > 0) or (r.Position - ovo.Position).Magnitude > CFG.ovo.dist + 2 then return end
		coletado = true; geracao += 1; local g = geracao                -- trava antes de qualquer espera
		ovo.Transparency = 1; pr.Enabled = false
		ovo:SetAttribute("ColetadoPor", j.UserId); ovo:SetAttribute("ColetadoEm", os.time())
		alvoColeta(j, 20)
		evColetado:Fire(j, pastaAlc.Name)
		local seg = ovo:GetAttribute("ReaparecerTesteSeg") or (60 * (CFG.ovo.reaparecerMin[1] + math.random() * (CFG.ovo.reaparecerMin[2] - CFG.ovo.reaparecerMin[1])))
		ovo:SetAttribute("ReapareceEm", os.time() + math.floor(seg))
		task.delay(seg, function()
			if g ~= geracao then return end
			coletado = false; ovo.Transparency = 0; pr.Enabled = true; ovo:SetAttribute("ColetadoPor", nil)
			evReapareceu:Fire(pastaAlc.Name)
		end)
	end)
end

-- alcateias (r4: um lobo por territorio, idempotente) ----------------------------------------------------------------------
-- Regras: (1) so mexe em pastas MARCADAS por este sistema (atributo SistemaIA) ou criadas por ele (nome da alcateia dentro de
-- Criaturas_IA.Lobos_Articos); outras criaturas, o lobo de ensaio e os habitats nao sao tocados. (2) Se a alcateia ja tem
-- lobos (reinicio do script, grupo da r3), mantem UM (prefere Solitario, depois Lider) e move os EXCEDENTES para
-- ServerStorage.LoboArtico_Backups.Excedentes_Solitario (desligados), sem destruir. (3) Rodar de novo nao duplica nada.
local backups = SS:FindFirstChild("LoboArtico_Backups") or Instance.new("Folder"); backups.Name = "LoboArtico_Backups"; backups.Parent = SS
local function guardarExcedente(f, nomeAlc)
	local dst = backups:FindFirstChild("Excedentes_Solitario") or Instance.new("Folder"); dst.Name = "Excedentes_Solitario"; dst.Parent = backups
	for _, d in ipairs(f:GetDescendants()) do if d:IsA("BaseScript") then d.Disabled = true end end
	f:SetAttribute("RetiradoDe", nomeAlc); f:SetAttribute("RetiradoEm", os.time()); f.Name = nomeAlc .. "_" .. f.Name
	f.Parent = dst
end
local function lobosDe(pastaAlc)
	local l = {}
	for _, f in ipairs(pastaAlc:GetChildren()) do
		if f:FindFirstChild("LoboArtico_LOW") and (f:GetAttribute("SistemaIA") == CFG.sistema or f:GetAttribute("AlcateiaPasta") == pastaAlc.Name) then table.insert(l, f) end
	end
	return l
end
local PREF = {Solitario = 0, Lider = 1, Membro = 2, Guardiao = 3}
for _, nomeAlc in ipairs(CFG.alcateias) do
	local hab = habitats:FindFirstChild(nomeAlc)
	if not hab then warn("[IA_LoboArtico] habitat nao achado: " .. nomeAlc); continue end
	local pastaAlc = raizLobos:FindFirstChild(nomeAlc)
	if not pastaAlc then pastaAlc = Instance.new("Folder"); pastaAlc.Name = nomeAlc; pastaAlc.Parent = raizLobos end
	pastaAlc:SetAttribute("Id", hab:GetAttribute("Id")); pastaAlc:SetAttribute("SistemaIA", CFG.sistema); pastaAlc:SetAttribute("Modo", "Solitario")
	-- ovo: refaz (as conexoes do prompt morrem com o script antigo); o estado de coleta segue no atributo ReapareceEm
	local ovoVelho = pastaAlc:FindFirstChild("Ovo_LoboArtico"); local reaparece = ovoVelho and ovoVelho:GetAttribute("ReapareceEm")
	if ovoVelho then ovoVelho:Destroy() end
	criarOvo(hab, pastaAlc)
	local ovo = pastaAlc:FindFirstChild("Ovo_LoboArtico")
	if ovo and reaparece and reaparece > os.time() then                    -- continua coletado ate a hora de reaparecer
		ovo:SetAttribute("ReapareceEm", reaparece)
		local pr = ovo:FindFirstChildOfClass("ProximityPrompt"); ovo.Transparency = 1; if pr then pr.Enabled = false end
		task.delay(reaparece - os.time(), function() if ovo.Parent then ovo.Transparency = 0; if pr then pr.Enabled = true end end end)
	end
	-- migracao: mantem um, guarda os excedentes
	local atuais = lobosDe(pastaAlc)
	table.sort(atuais, function(a, b) return (PREF[a:GetAttribute("Papel") or ""] or 9) < (PREF[b:GetAttribute("Papel") or ""] or 9) end)
	for k = #CFG.membros + 1, #atuais do guardarExcedente(atuais[k], nomeAlc) end
	local mantidos = math.min(#atuais, #CFG.membros)
	for k = 1, mantidos do                                                   -- o mantido vira Solitario (a IA r4 le o papel no inicio)
		local f = atuais[k]
		if f:GetAttribute("Papel") ~= CFG.membros[k][1] then
			local ia = f:FindFirstChild("IA_LoboArtico")
			f:SetAttribute("Papel", CFG.membros[k][1]); f:SetAttribute("SistemaIA", CFG.sistema)
			if ia then ia.Disabled = true; ia.Disabled = false end              -- reinicia so a IA para ler o papel novo
		end
	end
	local descanso = chao((hab:FindFirstChild("Descanso_Toca", true) or hab:FindFirstChild("Entrada_Toca", true)).Position)
	for i = mantidos + 1, #CFG.membros do
		local m = CFG.membros[i]
		local p = modelo:Clone(); p.Name = "Lobo_" .. i .. "_" .. m[1]
		p:SetAttribute("Alcateia", hab:GetAttribute("Id")); p:SetAttribute("AlcateiaPasta", nomeAlc); p:SetAttribute("Papel", m[1]); p:SetAttribute("SistemaIA", CFG.sistema)
		local l = p:FindFirstChild("LoboArtico_LOW")
		l:SetAttribute("Selvagem", true); l:SetAttribute("Criatura", true); l:SetAttribute("Especie", "LoboArtico")
		l:SetAttribute("Alcateia", hab:GetAttribute("Id")); l:SetAttribute("Idade", m[2])
		local ang = (i - 1) * 2.1
		l:PivotTo(CFrame.new(chao(descanso + Vector3.new(math.cos(ang) * 5, 0, math.sin(ang) * 5))) * CFrame.Angles(0, ang, 0))
		p.Parent = pastaAlc
	end
	print(string.format("[IA_LoboArtico] %s: %d lobo(s) (mantidos %d, excedentes guardados %d) + ovo", nomeAlc, #lobosDe(pastaAlc), mantidos, math.max(0, #atuais - #CFG.membros)))
end
script:SetAttribute("Versao", "r4 20/11 (lobo solitario, idempotente; alcateias " .. table.concat(CFG.alcateias, ",") .. ")")

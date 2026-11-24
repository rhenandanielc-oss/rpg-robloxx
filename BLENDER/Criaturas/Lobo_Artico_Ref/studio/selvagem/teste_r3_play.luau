-- Banco de ensaio da IA r3 (SO durante o Play, contexto Server). Cria _G.R3T com:
--   R3T.alc = pasta da alcateia; R3T.rodar(nomeCenario) dispara o roteiro (task.spawn) e grava amostras a cada 0,1 s;
--   R3T.res[nome] = {amostras..., resumo}; R3T.painel(true/false) liga os rotulos de diagnostico (BillboardGui) dos lobos.
-- Nada disto e salvo no place: tudo some ao parar o Play.
local Players = game:GetService("Players")
local R = _G.R3T or {}; _G.R3T = R
local raiz = workspace.Criaturas_IA.Lobos_Articos
R.alcNome = R.alcNome or "Alcateia_Floresta"
R.alc = raiz:FindFirstChild(R.alcNome)
local hab = workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico:FindFirstChild(R.alcNome)
local function P(n) local p = hab:FindFirstChild(n, true); return p and p.Position end
R.abrigo, R.entrada, R.descanso = P("Abrigo_Filhotes"), P("Entrada_Toca"), P("Descanso_Toca")
R.res = R.res or {}
local function jog() local j = Players:GetPlayers()[1]; return j, j and j.Character end
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
local function chao(p)
	rp.FilterDescendantsInstances = {raiz, (select(2, jog()))}
	local r = workspace:Raycast(p + Vector3.new(0, 40, 0), Vector3.new(0, -120, 0), rp)
	return r and r.Position or p
end
function R.lobos()
	local l = {}
	for _, f in ipairs(R.alc:GetChildren()) do local o = f:FindFirstChild("LoboArtico_LOW"); if o then table.insert(l, {pasta = f, lobo = o}) end end
	return l
end
function R.medir()                                                   -- uma amostra
	local _, c = jog(); local r = c and c:FindFirstChild("HumanoidRootPart"); local h = c and c:FindFirstChildOfClass("Humanoid")
	local s = {t = os.clock(), tensao = R.alc:GetAttribute("Tensao"), motivo = R.alc:GetAttribute("Motivo"), vida = h and h.Health, lobos = {}}
	if r then s.dAbr = (r.Position - R.entrada).Magnitude end         -- r3b: distancia ate a ENTRADA da toca (fora dela)
	for _, m in ipairs(R.lobos()) do
		local e = m.lobo:GetAttribute("Escala") or 1; local pv = m.lobo:GetPivot()
		local fr = plano(pv.LookVector).Unit; local foc = pv.Position + fr * 6.2 * e
		local x = {papel = m.pasta:GetAttribute("Papel"), est = m.pasta:GetAttribute("IA_Estado"), cont = m.pasta:GetAttribute("IA_Contato")}
		if r then
			x.dF = plano(r.Position - foc).Magnitude
			local rel = plano(r.Position - pv.Position); local al = rel:Dot(fr); local la = math.abs(rel:Dot(Vector3.new(-fr.Z, 0, fr.X)))
			x.dentro = al > -0.8 * e and al < 6.0 * e and la < 1.3 * e
		end
		table.insert(s.lobos, x)
	end
	return s
end
function R.ir(alvo, vel)                                              -- anda ate alvo (Humanoid:MoveTo), espera chegar
	local _, c = jog(); local h = c:FindFirstChildOfClass("Humanoid"); h.WalkSpeed = vel or 8
	local p = chao(alvo); local t0 = os.clock()
	repeat h:MoveTo(p); task.wait(0.25) until (plano(c.HumanoidRootPart.Position - p)).Magnitude < 2 or os.clock() - t0 > 30
end
function R.pos(p) local _, c = jog(); c:PivotTo(CFrame.new(chao(p) + Vector3.new(0, 3, 0))); c.HumanoidRootPart.AssemblyLinearVelocity = Vector3.zero end
function R.resetar()                                                  -- estado limpo entre cenarios (so o Play)
	for _, k in ipairs({"AlvoId", "AlvoMotivo", "AlvoAte", "AlvoJogador", "Tensao", "TensaoId", "TensaoPos", "Motivo", "AvisoDesde", "InvestigarPos", "InvestigarAte"}) do R.alc:SetAttribute(k, nil) end
	local _, c = jog(); local h = c:FindFirstChildOfClass("Humanoid"); h.MaxHealth = 1e6; h.Health = 1e6
end
-- direcao "para fora" da toca, a partir da entrada (a rota de aproximacao natural)
function R.fora() local d = plano(R.entrada - R.descanso); return d.Magnitude > 0.1 and d.Unit or Vector3.new(1, 0, 0) end
function R.ponto(dist) return R.entrada + R.fora() * dist end        -- a `dist` studs da entrada, para fora da toca
local ROTEIROS = {}
ROTEIROS["aproxima_e_para"] = function() R.pos(R.ponto(75)); task.wait(3); R.ir(R.ponto(30), 6); task.wait(14) end
ROTEIROS["recua"] = function() R.pos(R.ponto(75)); task.wait(3); R.ir(R.ponto(28), 6); task.wait(3); R.ir(R.ponto(75), 10); task.wait(10) end
ROTEIROS["insiste"] = function() R.pos(R.ponto(75)); task.wait(3); R.ir(R.ponto(28), 6); task.wait(3); R.ir(R.ponto(12), 4); task.wait(10) end
ROTEIROS["zona_critica"] = function() R.pos(R.ponto(75)); task.wait(3); R.ir(R.ponto(18), 6); task.wait(12) end
ROTEIROS["coleta"] = function()
	R.pos(R.ponto(75)); task.wait(2)
	local j = jog()                                                      -- o servidor nao segura o prompt: grava o mesmo que o spawner r3
	R.alc:SetAttribute("AlvoId", j.UserId); R.alc:SetAttribute("AlvoMotivo", "coleta"); R.alc:SetAttribute("AlvoAte", os.clock() + 20)
	R.alc:SetAttribute("Tensao", "Defesa"); R.alc:SetAttribute("TensaoId", j.UserId); R.alc:SetAttribute("Motivo", "coleta do ovo (simulada)")
	task.wait(12); R.ir(R.ponto(110), 16); task.wait(12)
end
ROTEIROS["dano_sem_autoria"] = function()
	R.pos(R.ponto(40)); task.wait(4)
	local l = R.lobos()[1]; local fn = l.pasta:FindFirstChild("ReceberDano")
	if fn then fn:Invoke(5, "Fisico") end; task.wait(10)
end
ROTEIROS["dano_validado"] = function()
	R.pos(R.ponto(55)); task.wait(4)
	local l = R.lobos()[1]; local fn = l.pasta:FindFirstChild("ReceberDano")
	if fn then fn:Invoke(5, "Fisico", (jog())) end; task.wait(10); R.ir(R.ponto(130), 16); task.wait(14)
end
ROTEIROS["morre"] = function()
	R.pos(R.ponto(20)); task.wait(1)
	local j, c = jog(); R.alc:SetAttribute("AlvoId", j.UserId); R.alc:SetAttribute("AlvoMotivo", "dano"); R.alc:SetAttribute("AlvoAte", os.clock() + 20)
	R.alc:SetAttribute("Tensao", "Defesa"); task.wait(6); c:FindFirstChildOfClass("Humanoid").Health = 0; task.wait(12)
end
function R.rodar(nome)
	R.resetar()
	local r = {nome = nome, amostras = {}, fim = false}; R.res[nome] = r
	local vivo = true
	task.spawn(function() while vivo do table.insert(r.amostras, R.medir()); task.wait(0.1) end end)
	task.spawn(function()
		local ok, err = pcall(ROTEIROS[nome]); vivo = false; r.fim = true; r.erro = (not ok) and tostring(err) or nil
	end)
	return "rodando " .. nome
end
function R.resumo(nome)                                               -- transicoes + menores distancias + tempo dentro
	local r = R.res[nome]; if not r then return "sem " .. nome end
	local out, ant, t0 = {}, nil, r.amostras[1] and r.amostras[1].t or 0
	local dmin, dentro, primeiraDef, primeiraAm = math.huge, 0, nil, nil
	for _, s in ipairs(r.amostras) do
		local k = tostring(s.tensao) .. " | " .. tostring(s.motivo)
		if k ~= ant then table.insert(out, string.format("%5.1fs %s (dAbr %.0f)", s.t - t0, k, s.dAbr or -1)); ant = k end
		if s.tensao == "Ameaca" and not primeiraAm then primeiraAm = s.t end
		if s.tensao == "Defesa" and not primeiraDef then primeiraDef = s.t end
		for _, x in ipairs(s.lobos) do
			if x.dF and not primeiraDef then dmin = math.min(dmin, x.dF) end
			if x.dentro then dentro += 0.1 / #s.lobos end
		end
	end
	table.insert(out, string.format("aviso antes da defesa: %s s | menor focinho->jogador antes da defesa: %.1f | dentro do corpo ~%.1f s | fim=%s %s",
		(primeiraAm and primeiraDef) and string.format("%.1f", primeiraDef - primeiraAm) or "-", dmin, dentro, tostring(r.fim), r.erro or ""))
	return table.concat(out, "\n")
end
function R.painel(on)                                                 -- rotulos de diagnostico (video com estado)
	for _, m in ipairs(R.lobos()) do
		local b = m.lobo:FindFirstChild("R3_Painel")
		if not on then if b then b:Destroy() end
		elseif not b then
			b = Instance.new("BillboardGui"); b.Name = "R3_Painel"; b.Size = UDim2.fromOffset(230, 46); b.StudsOffset = Vector3.new(0, 9, 0); b.AlwaysOnTop = true
			b.Adornee = m.lobo.PrimaryPart or m.lobo:FindFirstChildWhichIsA("BasePart", true)
			local t = Instance.new("TextLabel"); t.Size = UDim2.fromScale(1, 1); t.BackgroundTransparency = 0.35; t.BackgroundColor3 = Color3.new(0, 0, 0)
			t.TextColor3 = Color3.new(1, 1, 1); t.TextScaled = true; t.Font = Enum.Font.Code; t.Parent = b; b.Parent = m.lobo
			task.spawn(function()
				while b.Parent do
					local s = m.pasta
					t.Text = string.format("%s: %s\n%s | dF %s", s:GetAttribute("Papel") or "?", tostring(s:GetAttribute("IA_Estado")), tostring(s:GetAttribute("IA_Contato") or s:GetAttribute("IA_Sinal") or ""), tostring(s:GetAttribute("IA_DistFocinho") or "-"))
					local cor = ({Atencao = Color3.fromRGB(224, 179, 65), Ameacar = Color3.fromRGB(224, 123, 41), Defender = Color3.fromRGB(200, 55, 45)})[s:GetAttribute("IA_Estado") or ""]
					t.BackgroundColor3 = cor or Color3.new(0, 0, 0)
					task.wait(0.15)
				end
			end)
		end
	end
	return "painel " .. tostring(on)
end
return string.format("R3T pronto: %s abrigo %s entrada %s", R.alcNome, tostring(R.abrigo), tostring(R.entrada))

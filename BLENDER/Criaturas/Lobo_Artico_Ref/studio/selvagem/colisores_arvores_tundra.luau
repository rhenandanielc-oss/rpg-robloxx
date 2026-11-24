-- Colisores de TRONCO das arvores da Tundra (usuario 20/11/2026: "como ele entrou dentro da arvore, consegue arrumar as arvores";
-- escolha: "Troncos solidos na Tundra"). As malhas das arvores tem CanCollide/CanQuery = false (lobo e jogador atravessavam).
-- Em vez de dar colisao as malhas (copa e galhos ficariam solidos; varias arvores sao malha unica), cria em cada arvore de
-- Workspace.Tundra_Congelada.Vegetacao_Arvores um cilindro INVISIVEL "Colisor_Tronco" (CanCollide/CanQuery, sem toque/sombra),
-- dentro do proprio modelo (o LOD_Distancia do cliente leva junto). Eixo e raio medidos por raios horizontais em 16 direcoes a
-- 1,2 stud do chao (mediana das distancias) contra as malhas da arvore (CanQuery ligado so durante a medida e devolvido). Reversivel: apagar os
-- "Colisor_Tronco" (atributo CriadoPor). Uso (Studio, Edit): require/loadstring e chamar M.rodar(limite, so_relatorio).
local M = {}
local va = workspace.Tundra_Congelada.Vegetacao_Arvores
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include
local ALT, N, H_COL = 1.2, 16, 10                                            -- r2: 1,2 do chao (a 2,5 pegava galhos baixos)
local function arvores()
	local l = {}
	for _, m in ipairs(va:GetDescendants()) do if m:IsA("Model") and not m:FindFirstChildWhichIsA("Model") then table.insert(l, m) end end
	return l
end
local function medir(m)
	local partes = {}
	for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") and p.Name ~= "Colisor_Tronco" then table.insert(partes, {p, p.CanQuery}); p.CanQuery = true end end
	local lista = {}; for _, x in ipairs(partes) do table.insert(lista, x[1]) end
	rp.FilterDescendantsInstances = lista
	local cf, sz = m:GetBoundingBox(); local c = cf.Position; local baseY = c.Y - sz.Y / 2
	local tr = m:FindFirstChild("Trunk"); if tr then c = Vector3.new(tr.Position.X, c.Y, tr.Position.Z) end
	-- r3: o centro do modelo nao e o eixo do tronco; 3 passadas: mira os raios no centro estimado e recalcula
	local cen, pts = Vector3.new(c.X, baseY + ALT, c.Z), nil
	for passada = 1, 3 do
		local busca = passada == 1 and (math.max(sz.X, sz.Z) / 2 + 2) or 6
		pts = {}
		for k = 0, N - 1 do
			local a = k * 2 * math.pi / N; local d = Vector3.new(math.cos(a), 0, math.sin(a))
			local o = Vector3.new(cen.X, baseY + ALT, cen.Z) + d * busca
			local h = workspace:Raycast(o, -d * busca, rp)                      -- ate o centro estimado (nao atravessa para o outro lado)
			if h then table.insert(pts, h.Position) end
		end
		if #pts < 3 then break end
		local s = Vector3.zero; for _, p in ipairs(pts) do s += p end
		cen = s / #pts
	end
	for _, x in ipairs(partes) do x[1].CanQuery = x[2] end
	if not pts or #pts < 3 then return nil end
	local ds = {}
	for _, p in ipairs(pts) do table.insert(ds, (Vector3.new(p.X, 0, p.Z) - Vector3.new(cen.X, 0, cen.Z)).Magnitude) end
	table.sort(ds); local r = ds[math.ceil(#ds / 2)]                         -- r2: mediana (galho solto nao infla o raio)
	return Vector3.new(cen.X, baseY, cen.Z), math.clamp(r, 0.35, 3.0), #pts
end
function M.rodar(limite, soRelatorio)
	local l = arvores(); local feitos, sem, ja = 0, 0, 0; local raios = {}
	for i, m in ipairs(l) do
		if limite and feitos >= limite then break end
		if m:FindFirstChild("Colisor_Tronco") then ja += 1
		else
			local base, r, n = medir(m)
			if not base then sem += 1
			else
				table.insert(raios, r)
				if not soRelatorio then
					local p = Instance.new("Part"); p.Name = "Colisor_Tronco"; p.Shape = Enum.PartType.Cylinder; p.Anchored = true
					p.Size = Vector3.new(H_COL, r * 2, r * 2)                               -- cilindro: eixo em X
					p.CFrame = CFrame.new(base + Vector3.new(0, H_COL / 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
					p.Transparency = 1; p.CanCollide = true; p.CanQuery = true; p.CanTouch = false; p.CastShadow = false
					p:SetAttribute("CriadoPor", "Lobo Artico 20/11 (colisor de tronco)"); p.Parent = m
				end
				feitos += 1
			end
		end
		if i % 80 == 0 then task.wait() end
	end
	table.sort(raios)
	local med = #raios > 0 and raios[math.ceil(#raios / 2)] or 0
	return string.format("arvores %d | colisores %s %d | ja tinham %d | sem medida %d | raio min %.2f mediana %.2f max %.2f",
		#l, soRelatorio and "(simulado)" or "criados", feitos, ja, sem, raios[1] or 0, med, raios[#raios] or 0)
end
-- r4: arvores sem colisor (betulas de varios troncos, pinheiros/abetos com o tronco longe do centro): um colisor POR PECA que nao
-- e copa, medida so contra aquela peca, centrada nela
function M.rodarFaltando()
	local feitos, arvs, semNada = 0, 0, 0
	for i, m in ipairs(arvores()) do
		if not m:FindFirstChild("Colisor_Tronco") then
			arvs += 1; local criou = false
			for _, p in ipairs(m:GetChildren()) do
				if p:IsA("BasePart") and not p.Name:find("Copa") and p.Name ~= "Colisor_Tronco" then
					local q = p.CanQuery; p.CanQuery = true; rp.FilterDescendantsInstances = {p}
					local cf, sz = m:GetBoundingBox(); local baseY = cf.Position.Y - sz.Y / 2
					local gp = RaycastParams.new(); gp.FilterType = Enum.RaycastFilterType.Include; gp.FilterDescendantsInstances = {workspace.Terrain}
					local g = workspace:Raycast(Vector3.new(p.Position.X, cf.Position.Y + sz.Y, p.Position.Z), Vector3.new(0, -sz.Y * 3, 0), gp)
					if g then baseY = g.Position.Y end                                -- r4b: chao real (raizes enterradas abaixo da caixa)
					local cen, pts = Vector3.new(p.Position.X, baseY + ALT, p.Position.Z), nil
					for passada = 1, 3 do
						local busca = passada == 1 and (math.max(p.Size.X, p.Size.Z) / 2 + 2) or 4
						pts = {}
						for k = 0, N - 1 do
							local a = k * 2 * math.pi / N; local d = Vector3.new(math.cos(a), 0, math.sin(a))
							local h = workspace:Raycast(Vector3.new(cen.X, baseY + ALT, cen.Z) + d * busca, -d * busca, rp)
							if h then table.insert(pts, h.Position) end
						end
						if #pts < 3 then break end
						local s_ = Vector3.zero; for _, x in ipairs(pts) do s_ += x end; cen = s_ / #pts
					end
					p.CanQuery = q
					if pts and #pts >= 3 then
						local ds = {}; for _, x in ipairs(pts) do table.insert(ds, (Vector3.new(x.X, 0, x.Z) - Vector3.new(cen.X, 0, cen.Z)).Magnitude) end
						table.sort(ds); local r = math.clamp(ds[math.ceil(#ds / 2)], 0.3, 3.0)
						local c = Instance.new("Part"); c.Name = "Colisor_Tronco"; c.Shape = Enum.PartType.Cylinder; c.Anchored = true
						c.Size = Vector3.new(H_COL, r * 2, r * 2); c.CFrame = CFrame.new(Vector3.new(cen.X, baseY + H_COL / 2, cen.Z)) * CFrame.Angles(0, 0, math.rad(90))
						c.Transparency = 1; c.CanCollide = true; c.CanQuery = true; c.CanTouch = false; c.CastShadow = false
						c:SetAttribute("CriadoPor", "Lobo Artico 20/11 (colisor de tronco, por peca)"); c.Parent = m
						feitos += 1; criou = true
					end
				end
			end
			if not criou then semNada += 1 end
		end
		if i % 80 == 0 then task.wait() end
	end
	return string.format("arvores que faltavam %d | colisores por peca %d | ainda sem colisor %d", arvs, feitos, semNada)
end
-- r5: VARREDURA EM GRADE para as que ainda faltam (betulas de varios troncos com a malha inteira numa peca): linhas de raios
-- em X e em Z, a cada 0,5 stud, a 1,5 stud do CHAO REAL (Terrain sob a arvore); pontos agrupados (< 2,5 studs) = um tronco;
-- um colisor por grupo (centro = media, raio = metade da maior extensao, 0,3..3).
function M.rodarVarredura()
	local feitos, arvs, semNada = 0, 0, 0
	local gp = RaycastParams.new(); gp.FilterType = Enum.RaycastFilterType.Include; gp.FilterDescendantsInstances = {workspace.Terrain}
	for i, m in ipairs(arvores()) do
		if not m:FindFirstChild("Colisor_Tronco") then
			arvs += 1
			local partes = {}; for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") then table.insert(partes, {p, p.CanQuery}); p.CanQuery = true end end
			local lista = {}; for _, x in ipairs(partes) do table.insert(lista, x[1]) end
			rp.FilterDescendantsInstances = lista
			local cf, sz = m:GetBoundingBox(); local c = cf.Position
			local g = workspace:Raycast(Vector3.new(c.X, c.Y + sz.Y, c.Z), Vector3.new(0, -sz.Y * 3, 0), gp)
			local y = (g and g.Position.Y or (c.Y - sz.Y / 2)) + 1.5
			local hx, hz = sz.X / 2 + 1, sz.Z / 2 + 1
			local pts = {}
			for z = -hz, hz, 0.5 do
				local h = workspace:Raycast(Vector3.new(c.X - hx, y, c.Z + z), Vector3.new(2 * hx, 0, 0), rp); if h then table.insert(pts, h.Position) end
				local h2 = workspace:Raycast(Vector3.new(c.X + hx, y, c.Z + z), Vector3.new(-2 * hx, 0, 0), rp); if h2 then table.insert(pts, h2.Position) end
			end
			for x = -hx, hx, 0.5 do
				local h = workspace:Raycast(Vector3.new(c.X + x, y, c.Z - hz), Vector3.new(0, 0, 2 * hz), rp); if h then table.insert(pts, h.Position) end
				local h2 = workspace:Raycast(Vector3.new(c.X + x, y, c.Z + hz), Vector3.new(0, 0, -2 * hz), rp); if h2 then table.insert(pts, h2.Position) end
			end
			for _, x in ipairs(partes) do x[1].CanQuery = x[2] end
			local grupos = {}
			for _, p in ipairs(pts) do
				local achou
				for _, gr in ipairs(grupos) do if (Vector3.new(p.X, 0, p.Z) - Vector3.new(gr.c.X, 0, gr.c.Z)).Magnitude < 2.5 then achou = gr; break end end
				if achou then table.insert(achou.p, p); local s_ = Vector3.zero; for _, q in ipairs(achou.p) do s_ += q end; achou.c = s_ / #achou.p
				else table.insert(grupos, {c = p, p = {p}}) end
			end
			local criou = false
			for _, gr in ipairs(grupos) do
				if #gr.p >= 3 then
					local mx = 0; for _, q in ipairs(gr.p) do mx = math.max(mx, (Vector3.new(q.X, 0, q.Z) - Vector3.new(gr.c.X, 0, gr.c.Z)).Magnitude) end
					local r = math.clamp(mx, 0.3, 3.0); local baseY = y - 1.5
					local col = Instance.new("Part"); col.Name = "Colisor_Tronco"; col.Shape = Enum.PartType.Cylinder; col.Anchored = true
					col.Size = Vector3.new(H_COL, r * 2, r * 2); col.CFrame = CFrame.new(Vector3.new(gr.c.X, baseY + H_COL / 2, gr.c.Z)) * CFrame.Angles(0, 0, math.rad(90))
					col.Transparency = 1; col.CanCollide = true; col.CanQuery = true; col.CanTouch = false; col.CastShadow = false
					col:SetAttribute("CriadoPor", "Lobo Artico 20/11 (colisor de tronco, varredura)"); col.Parent = m
					feitos += 1; criou = true
				end
			end
			if not criou then semNada += 1 end
		end
		if i % 40 == 0 then task.wait() end
	end
	return string.format("arvores que faltavam %d | colisores por varredura %d | ainda sem colisor %d", arvs, feitos, semNada)
end
function M.desfazer()
	local n = 0
	for _, p in ipairs(va:GetDescendants()) do if p.Name == "Colisor_Tronco" and p:GetAttribute("CriadoPor") then p:Destroy(); n += 1 end end
	return "removidos " .. n
end
return M

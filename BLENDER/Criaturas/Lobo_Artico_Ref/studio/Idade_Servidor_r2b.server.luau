-- r2 19/11: malha propria por idade (copia da r1: Idade_Servidor_r1.server.luau).
-- Idade_Servidor (Script, Workspace.Teste_LoboArtico) - ESTAGIOS DE IDADE do Lobo Artico (ensaio, 18/11/2026).
-- Usuario 18/11: "Prossiga com todos os passos de uma vez e depois eu avalio."
-- Fonte: ESTATISTICAS_POR_IDADE.md v5.2 (16/11) [PROPOSTA][A TESTAR]: multiplicadores sobre o Adulto, iguais para todas
-- as criaturas; o SERVIDOR calcula tudo a partir do estagio (o cliente so mostra).
-- So o Adulto tem modelo: os outros estagios usam o MESMO modelo em escala (Model:ScaleTo). Modelos proprios de
-- Filhote/Jovem/Pre-adulto/Anciao e o ovo continuam [PENDENTE] (decisao conjunta das criaturas, usuario 10/11).
-- Grava no lobo: Escala, VidaMax/Vida (proporcional), MultDano, MultDefesa, MultForca, BonusVel_Idade, TetoEsquiva,
-- EnergiaMax, RegenEnergia e Ativas (liberacao por idade, sugestao [A CONFIRMAR] do documento).
-- Troca no ensaio: atributo Idade do lobo ("Filhote", "Jovem", "PreAdulto", "Adulto", "Anciao"). No jogo a idade
-- vem dos dados salvos da criatura (DataStore) - nao implementado aqui.
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")

local ADULTO = {vida = 400, energia = 100, regen = 5, teto = 0.35}
local IDADES = {      -- tamanho, vida, dano, defesa, forca, velocidade, teto de esquiva, energia max, regen (sobre o Adulto)
	Filhote   = {esc = 0.40, vida = 0.30, dano = 0.30, def = 0.40, forca = 0.30, vel = 1.15, esq = 1.20, en = 60,  reg = 0.70},
	Jovem     = {esc = 0.65, vida = 0.50, dano = 0.55, def = 0.65, forca = 0.55, vel = 1.10, esq = 1.10, en = 75,  reg = 0.85},
	PreAdulto = {esc = 0.85, vida = 0.75, dano = 0.80, def = 0.85, forca = 0.80, vel = 1.05, esq = 1.05, en = 90,  reg = 0.95},
	Adulto    = {esc = 1.00, vida = 1.00, dano = 1.00, def = 1.00, forca = 1.00, vel = 1.00, esq = 1.00, en = 100, reg = 1.00},
	Anciao    = {esc = 1.10, vida = 1.15, dano = 1.10, def = 1.20, forca = 1.10, vel = 0.90, esq = 0.80, en = 100, reg = 1.00},
}
-- Liberacao [A CONFIRMAR]: documento = Filhote so basico+passivas; Jovem 1 ativa; Pre-adulto 2; Adulto/Anciao 3.
-- Ordem [PROPOSTA deste ensaio]: Uivo (autobuff, sem dano) -> Avalanche (curto alcance) -> Cometa (longo alcance).
local ATIVAS = {Filhote = "", Jovem = "Uivo", PreAdulto = "Uivo,Avalanche", Adulto = "Uivo,Avalanche,Cometa", Anciao = "Uivo,Avalanche,Cometa"}

local escalaBase = lobo:GetScale()            -- escala do Adulto no place (normalmente 1)
-- r2 (19/11, visual por idade APROVADO: "Aprovar e seguir"): cada idade tem malha propria (exportar_idades_v1.py ->
-- Import 3D -> montar_idades_v1.luau -> ServerStorage.LoboArtico_Idades.<Idade>). A troca acontece na escala do Adulto:
-- as MeshParts LOW_* sao substituidas por copias da idade (mesma posicao relativa a RootPart) e cada osso recebe o CFrame
-- de repouso daquela malha; os clipes continuam os mesmos (orientacoes de repouso iguais; so comprimentos mudam).
-- Sem a pasta (ou sem a idade) fica a malha atual e so a escala muda, como na r1.
local HS = game:GetService("HttpService")
local estoque = game:GetService("ServerStorage"):FindFirstChild("LoboArtico_Idades")
local PAPEIS = {"LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"}
local malhaAtual = "Adulto"
local function trocarMalha(nome)
	if not estoque then return "sem estoque" end
	local src = estoque:FindFirstChild(nome)
	if not src then return "sem malha " .. nome end
	if src.Name == malhaAtual then return "ja " .. nome end
	local rp = lobo:FindFirstChild("RootPart")
	local ok, tb = pcall(function() return HS:JSONDecode(src:GetAttribute("Ossos")) end)
	if not (rp and ok and tb) then return "dados invalidos" end
	for _, n in ipairs(PAPEIS) do local p = lobo:FindFirstChild(n); if p then p:Destroy() end end
	for _, p in ipairs(src:GetChildren()) do
		if p:IsA("MeshPart") then
			local c = p:Clone(); local r = HS:JSONDecode(c:GetAttribute("Rel"))
			local rel = CFrame.new(table.unpack(r))
			c.CFrame = rp.CFrame * rel
			-- r2b: cada MeshPart pendura na RootPart por um Motor6D; o do clone apontava para a RootPart do import guardado
			-- (a peca caia no vazio). Religa na RootPart deste lobo com a mesma posicao relativa.
			local m6 = c:FindFirstChildOfClass("Motor6D")
			if not m6 then m6 = Instance.new("Motor6D"); m6.Name = c.Name .. "Motor6D"; m6.Parent = c end
			m6.Part0 = rp; m6.Part1 = c; m6.C0 = rel; m6.C1 = CFrame.identity
			c.Parent = lobo
		end
	end
	for _, b in ipairs(rp:GetDescendants()) do
		if b:IsA("Bone") and tb[b.Name] then b.CFrame = CFrame.new(table.unpack(tb[b.Name])) end
	end
	malhaAtual = src.Name
	lobo:SetAttribute("MalhaIdade", malhaAtual)
	return "malha " .. malhaAtual
end
local function aplicar()
	local nome = lobo:GetAttribute("Idade")
	if not IDADES[nome] then nome = "Adulto"; lobo:SetAttribute("Idade", nome); return end   -- AttributeChanged chama de novo
	if lobo:GetAttribute("PoderAtivo") then                                                -- nao troca no meio de um poder
		task.delay(0.5, aplicar); return
	end
	local I = IDADES[nome]
	local pv = lobo:GetPivot()
	lobo:ScaleTo(escalaBase)                                                             -- r2: troca a malha na escala do Adulto
	local troca = trocarMalha(nome)
	lobo:ScaleTo(escalaBase * I.esc)
	lobo:PivotTo(pv)                                                                     -- pivo nas patas: fica no chao
	local vMaxAnt = lobo:GetAttribute("VidaMax") or ADULTO.vida
	local fracao = math.clamp((lobo:GetAttribute("Vida") or vMaxAnt) / math.max(vMaxAnt, 1), 0, 1)
	local vMax = math.floor(ADULTO.vida * I.vida + 0.5)
	lobo:SetAttribute("Escala", I.esc)
	lobo:SetAttribute("VidaMax", vMax); lobo:SetAttribute("Vida", math.floor(vMax * fracao + 0.5))
	lobo:SetAttribute("MultDano", I.dano); lobo:SetAttribute("MultDefesa", I.def); lobo:SetAttribute("MultForca", I.forca)
	lobo:SetAttribute("BonusVel_Idade", I.vel - 1)
	lobo:SetAttribute("TetoEsquiva", math.min(0.35, ADULTO.teto * I.esq))
	lobo:SetAttribute("EnergiaMax", I.en); lobo:SetAttribute("RegenEnergia", ADULTO.regen * I.reg)
	lobo:SetAttribute("Ativas", ATIVAS[nome])
	pasta:SetAttribute("Idade_Troca", troca)
	pasta:SetAttribute("Idade_Ultima", string.format("%s escala %.2f vida %d dano %.1f vel %.2f teto %.0f%% energia %d (+%.1f/s) ativas [%s]",
		nome, I.esc, vMax, 10 * I.dano, I.vel, 100 * math.min(0.35, ADULTO.teto * I.esq), I.en, ADULTO.regen * I.reg, ATIVAS[nome]))
end
lobo:GetAttributeChangedSignal("Idade"):Connect(aplicar)
if not lobo:GetAttribute("Idade") then lobo:SetAttribute("Idade", "Adulto") else aplicar() end
task.defer(aplicar)
pasta:SetAttribute("Idade_Versao", "r2b 19/11 (malha propria por idade; Motor6D religado) | r1 18/11 (5 idades por escala do modelo Adulto; numeros ESTATISTICAS_POR_IDADE v5.2 [A TESTAR])")

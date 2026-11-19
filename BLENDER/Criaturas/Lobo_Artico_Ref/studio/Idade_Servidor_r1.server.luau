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
local function aplicar()
	local nome = lobo:GetAttribute("Idade")
	if not IDADES[nome] then nome = "Adulto"; lobo:SetAttribute("Idade", nome); return end   -- AttributeChanged chama de novo
	if lobo:GetAttribute("PoderAtivo") then                                                -- nao troca no meio de um poder
		task.delay(0.5, aplicar); return
	end
	local I = IDADES[nome]
	local pv = lobo:GetPivot()
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
	pasta:SetAttribute("Idade_Ultima", string.format("%s escala %.2f vida %d dano %.1f vel %.2f teto %.0f%% energia %d (+%.1f/s) ativas [%s]",
		nome, I.esc, vMax, 10 * I.dano, I.vel, 100 * math.min(0.35, ADULTO.teto * I.esq), I.en, ADULTO.regen * I.reg, ATIVAS[nome]))
end
lobo:GetAttributeChangedSignal("Idade"):Connect(aplicar)
if not lobo:GetAttribute("Idade") then lobo:SetAttribute("Idade", "Adulto") else aplicar() end
task.defer(aplicar)
pasta:SetAttribute("Idade_Versao", "r1 18/11 (5 idades por escala do modelo Adulto; numeros ESTATISTICAS_POR_IDADE v5.2 [A TESTAR])")

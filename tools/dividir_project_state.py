"""Divide PROJECT-STATE.md (grande demais para ler de uma vez) em notas por tema em DOCS/estado/, sem perder texto:
cada secao '## ' vai inteira para a nota do seu tema; PROJECT-STATE.md vira indice com links (Obsidian + Markdown).
Uso: python -I dividir_project_state.py <repo>"""
import os, re, sys
repo = sys.argv[1]; arq = os.path.join(repo, "PROJECT-STATE.md")
linhas = open(arq, encoding="utf-8").read().split("\n")
cab, secoes, atual = [], [], None
for l in linhas:
    if l.startswith("## "):
        atual = [l]; secoes.append(atual)
    elif atual is None: cab.append(l)
    else: atual.append(l)
META = ("Próxima tarefa autorizada", "Registro de execução", "Como atualizar após trabalho real")
MUNDO = ((r"M2\.1", "mundo-floresta", "Mundo: Floresta Ancestral (M2.1, protótipo e árvores)"),
         (r"(OPERAÇÃO M2 |OPERAÇÃO M2-|MONTANHAS)", "mundo-montanhas", "Mundo: Montanhas Altas (M2, V3, V4)"),
         (r"(ATMOSFERA|CORREÇÕES V6|V7|V8|V9)", "mundo-floresta-montanhas-v5-v9", "Mundo: correções Floresta × Montanhas (V5–V9)"),
         (r"M3", "mundo-pantano", "Mundo: Pântano Nebuloso (M3)"),
         (r"M4", "mundo-planicies", "Mundo: Planícies Douradas (M4)"),
         (r"M5", "mundo-tundra", "Mundo: Tundra Congelada (M5)"),
         (r"(M6|OPERAÇÃO M6)", "mundo-deserto-grutas", "Mundo: Deserto de Cristal e grutas (M6)"),
         (r"M7", "mundo-costas", "Mundo: Costas Selvagens e oceano (M7)"),
         (r"(M8|OPERAÇÃO M8)", "mundo-corrompidas-auditoria", "Mundo: Terras Corrompidas e auditoria dos 8 biomas (M8)"),
         (r"OPERAÇÃO M9", "mundo-ilhas", "Mundo: Ilhas flutuantes (M9)"),
         (r"(TAMANHO DO PLACE|AUDITORIA DE ERROS)", "mundo-auditorias", "Mundo: tamanho do place e auditoria de bugs"))
def tema(titulo, idx):
    t = titulo[3:]
    if t.startswith(META): return None
    if idx < 5: return ("fundacao", "Fundação: estado inicial do Studio, M1")
    for padrao, nome, desc in MUNDO:
        if re.match(padrao, t): return (nome, desc)
    if re.match(r"(OPERAÇÃO C1|OPERAÇÃO CREATURE|CRIATURAS|OPERAÇÃO CRIATURAS|Lobo|Master Prompt|Produção autônoma)", t):
        return ("criaturas-gerais", "Criaturas oficiais: blockouts, lobos, produção V5")
    if t.startswith("2026-10-30") or t.startswith("F) "):
        return ("dragao-2026-10-30", "Dragão: Drake5, IA selvagem integrada, derrota/voo, dragão novo, limpeza")
    if re.match(r"(IA selvagem|Combate elemental|Atualização oficial do Dragão|Correção crítica)", t):
        return ("dragao-ia-combate-montaria", "Dragão: IA, combate elemental e montaria (até 29/10)")
    return ("dragao-modelos-animacao", "Dragão: testes de IA 3D, V12–V14, Silverwing, animações (até 29/10)")
notas, meta = {}, []
for i, s in enumerate(secoes):
    tm = tema(s[0], i)
    if tm is None: meta.append(s); continue
    notas.setdefault(tm, []).append(s)
dest = os.path.join(repo, "DOCS", "estado"); os.makedirs(dest, exist_ok=True)
indice = cab[:]
indice += ["## Notas de estado por sistema (DOCS/estado/)", "",
           "O histórico completo foi dividido por tema em 2026-10-30 (o arquivo único passou de 480 KB). Novas entradas vão",
           "na nota do sistema; aqui fica só o índice. Abrir a pasta do repositório como cofre no Obsidian mostra os links.", ""]
total = 0
for (nome, desc), secs in notas.items():
    corpo = ["# " + desc, "", "Voltar ao índice: [[PROJECT-STATE]]", ""]
    for s in secs: corpo += s
    open(os.path.join(dest, nome + ".md"), "w", encoding="utf-8", newline="\n").write("\n".join(corpo) + "\n")
    total += sum(len(s) for s in secs)
    indice += ["### [[%s]] — %s" % (nome, desc), "Arquivo: [DOCS/estado/%s.md](DOCS/estado/%s.md)" % (nome, nome), ""]
    indice += ["- " + s[0][3:] for s in secs] + [""]
for s in meta: indice += s
open(arq, "w", encoding="utf-8", newline="\n").write("\n".join(indice).rstrip() + "\n")
print("secoes:", len(secoes), "em notas:", sum(len(v) for v in notas.values()), "meta no indice:", len(meta),
      "linhas movidas:", total, "de", len(linhas))

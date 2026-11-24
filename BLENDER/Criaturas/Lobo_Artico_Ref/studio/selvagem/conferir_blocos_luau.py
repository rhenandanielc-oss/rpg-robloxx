"""Conferencia estatica simples de scripts Luau (19/11/2026): blocos abertos x fechados, ignorando strings e comentarios.
Nao substitui o compilador do Roblox (loadstring no Studio); so pega bloco sem 'end' e 'end' sobrando.
Uso: python conferir_blocos_luau.py arquivo.luau [...]"""
import re, sys
def limpar(s):
    s = re.sub(r"--\[(=*)\[.*?\]\1\]", "", s, flags=re.S)          # comentario longo
    s = re.sub(r"\[(=*)\[.*?\]\1\]", '""', s, flags=re.S)          # string longa
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if s.startswith("--", i):
            j = s.find("\n", i); i = n if j < 0 else j; continue
        if c in "\"'`":
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == "\\" else 1
            out.append('""'); i = j + 1; continue
        out.append(c); i += 1
    return "".join(out)
for f in sys.argv[1:]:
    s = limpar(open(f, encoding="utf-8").read())
    toks = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", s)
    pilha = 0; menor = 0
    for t in toks:
        if t in ("function", "if", "do", "repeat"): pilha += 1     # for/while abrem pelo 'do'
        elif t in ("end", "until"): pilha -= 1; menor = min(menor, pilha)
    print("%-55s saldo=%d %s" % (f, pilha, "OK" if pilha == 0 and menor >= 0 else "PROBLEMA"))

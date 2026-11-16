"""Gera Crocodilo_Piloto.rbxmx (XML do Roblox) com a pasta do piloto: Dados_Clipes (StringValues dos 49 clipes +
Eventos_*) e o ModuleScript AdaptadorCrocodilo. Inserir no Studio: ServerStorage > botao direito > Insert from File.
Evita colar centenas de KB de dados no execute_luau. Uso: python gerar_rbxmx.py <dir_clipes> <saida.rbxmx>"""
import sys, os, re, subprocess, tempfile, glob
from xml.sax.saxutils import escape
aqui = os.path.dirname(os.path.abspath(__file__))
clipes, saida = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, os.path.join(aqui, "empacotar_clipes_croc.py"), clipes, tmp, "100000000"], check=True, capture_output=True)
lua = open(glob.glob(os.path.join(tmp, "envio_*.luau"))[0], encoding="utf-8").read()
valores = re.findall(r'v = Instance\.new\("StringValue"\); v\.Name = "([^"]+)"; v\.Value = (?:\[==\[(.*?)\]==\]|"([^"]*)"); v\.Parent = dados', lua, re.S)
ref = [0]
def item(classe, nome, props):
    ref[0] += 1
    p = '<string name="Name">%s</string>' % escape(nome) + props
    return '<Item class="%s" referent="RBX%d"><Properties>%s</Properties>' % (classe, ref[0], p)
partes = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" version="4">', item("Folder", "Crocodilo_Piloto", "")]
fonte = open(os.path.join(aqui, "AdaptadorCrocodilo.luau"), encoding="utf-8").read()
partes.append(item("ModuleScript", "AdaptadorCrocodilo", '<ProtectedString name="Source"><![CDATA[%s]]></ProtectedString>' % fonte) + "</Item>")
partes.append(item("Folder", "Dados_Clipes", ""))
for nome, longo, curto in valores:
    partes.append(item("StringValue", nome, '<string name="Value">%s</string>' % escape(longo or curto)) + "</Item>")
partes.append("</Item></Item></roblox>")
open(saida, "w", encoding="utf-8", newline="\n").write("".join(partes))
print("RBXMX_OK", saida, os.path.getsize(saida), "bytes;", len(valores), "StringValues")

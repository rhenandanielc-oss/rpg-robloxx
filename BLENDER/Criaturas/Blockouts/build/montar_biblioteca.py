"""Monta CR_Blockouts_Biblioteca.blend: copia (append) cada blockout de <Especie>/<Especie>_blockout.blend para
CREATURES/BLOCKOUTS/<Especie>, lado a lado em X na mesma escala, cada um com seu humano de 5,2 studs em REF/Escala.
Os arquivos por especie continuam sendo as versoes de trabalho (os scripts build_*.py os regeneram)."""
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blockout_lib import RAIZ, cena_nova, colecao, salvar

ORDEM = ["Leao_Solar", "Lobo_Ancestral", "Lobo_Artico", "Urso_Silvestre", "Bufalo_Colossal", "Cerbero_Sombrio",
         "Crocodilo_Primordial", "Basilisco", "Lagarto_Cristalino", "Escorpiao_Colossal", "Serpente_Marinha",
         "Leviata_Jovem", "Wyvern", "Dragao_das_Montanhas", "Dragao_Glacial", "Dragao_Sombrio"]

SUF = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "_blockout"
SAIDA = "CR_Criaturas_Final_Biblioteca.blend" if SUF == "_final" else "CR_Blockouts_Biblioteca.blend"
cena_nova()
ref = bpy.data.collections.new("REF_Escala"); bpy.context.scene.collection.children.link(ref)
x = 0.0
rel = []
for esp in ORDEM:
    src = os.path.join(RAIZ, esp, esp + SUF + ".blend")
    with bpy.data.libraries.load(src, link=False) as (a, b):
        b.objects = list(a.objects)
    obs = [o for o in b.objects if o is not None]
    larg = max((max((o.matrix_world @ v.co).x for v in o.data.vertices) - min((o.matrix_world @ v.co).x for v in o.data.vertices))
               for o in obs if o.type == "MESH" and not o.name.startswith("REF_"))
    obs = [o for o in obs if o.parent is None or o.parent not in obs]   # move so as raizes (rig leva as malhas)
    todos = [o for o in b.objects if o is not None]
    x += larg / 2 + 8
    col = colecao(esp)
    n = 0
    for o in todos:
        if o in obs: o.location.x += x
        if o.name.startswith("REF_"):
            o.name = "REF_Humano_" + esp
            ref.objects.link(o)
        else:
            col.objects.link(o); n += 1
    rel.append((esp, round(x, 1), n))
    x += larg / 2 + 8
salvar(os.path.join(RAIZ, SAIDA))
for r in rel:
    print("BIBLIOTECA", r)
print("TOTAL_OBJETOS", sum(r[2] for r in rel), "COLECOES", len(bpy.data.collections["BLOCKOUTS"].children))


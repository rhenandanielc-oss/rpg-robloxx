"""Folha de revisao das animacoes novas: para cada clipe, quadros em 0, 1/3, 2/3 em vistas lado / frente / 3-4,
EEVEE com textura e chao. Uso: blender -b arq.blend -P render_clipes.py -- saida_dir clipe1,clipe2|todos"""
import bpy, sys, os
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; quais = None if len(args) < 2 or args[1] == "todos" else args[1].split(",")
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 480, 360
cam = bpy.data.objects["cam_rev"]; sc.camera = cam
NOVOS = ["Parado", "Andar", "Correr", "Parada", "Abaixar", "Abaixado", "Levantar", "Voo", "Pairar", "Subida", "Descida",
         "Planeio", "Curva_E", "Curva_D", "Mergulho", "Decolagem", "Pouso", "Mordida_Aerea"]
RAIO = float(os.environ.get("RAIO_CAM", "1"))           # >1 afasta a camera (asas maiores)
for nome in (quais or NOVOS):
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    qs = [f0, f0 + (f1 - f0) // 3, f0 + 2 * (f1 - f0) // 3]
    if nome == "Mordida_Aerea": qs = [f0 + int((f1 - f0) * k) for k in (0.25, 0.48, 0.6)]   # preparo / boca aberta / mordida
    for i, f in enumerate(qs):
        sc.frame_set(f)
        c = Vector((-0.02, -0.1, 0.3))
        for vista, d, r in (("lado", (1, 0, 0.08), 1.7), ("frente", (0, -1, 0.15), 1.7), ("34", (0.9, -0.8, 0.6), 1.9),
                            ("baixo", (1, 0.15, -0.12), 1.5), ("tras", (0.25, 1, 0.35), 2.2)):
            cam.location = c + Vector(d).normalized() * r * RAIO
            if vista == "baixo": cam.location.z = 0.06
            cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(out, "%s_%d_%s.png" % (nome, i, vista)); bpy.ops.render.render(write_still=True)
A.animation_data.action = None
print("RENDER_OK")

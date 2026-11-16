"""Captura a area do viewport do Studio por PrintWindow (le a janela mesmo coberta, sem foco nem teclado) ate existir o
arquivo PARAR na pasta de saida. Salva JPG recortados (f00000.jpg...). Uso: python capturar.py HWND PASTA [qps]"""
import sys, os, time, ctypes
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "review", "teaser_anuncio", "scripts"))
import pw
hwnd, pasta = int(sys.argv[1]), sys.argv[2]; qps = float(sys.argv[3]) if len(sys.argv) > 3 else 24
os.makedirs(pasta, exist_ok=True)
CORTE = (176, 170, 1560, 944)
n = 0; t0 = time.time()
while not os.path.exists(os.path.join(pasta, "PARAR")):
    t = time.time()
    ok, im = pw.grab(hwnd)
    if ok: im.crop(CORTE).save(os.path.join(pasta, "f%05d.jpg" % n), quality=92); n += 1
    dt = 1.0 / qps - (time.time() - t)
    if dt > 0: time.sleep(dt)
print("capturados", n, "em", round(time.time() - t0, 1), "s")

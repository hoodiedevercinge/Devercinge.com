# -*- coding: utf-8 -*-
"""Rend une page de montage image par image et en fait un mp4 muet.

Les pixels vont directement dans ffmpeg : 915 PNG poses sur le disque ne
serviraient a rien. macro_block_size=1 garde le cadrage exact 1080x1920
qu'attend Instagram, sinon imageio elargit a 1088.

    python3 rendu.py                      # montage.html -> muet.mp4
    python3 rendu.py etape.html           # etape.html   -> etape-muet.mp4
    python3 rendu.py etape.html paysage   # 1920x1080    -> etape-paysage-muet.mp4

Si Chromium n'est pas la ou playwright l'attend, donnez son chemin :

    CHROMIUM=/opt/pw-browsers/chromium python3 rendu.py
"""
import io, os, sys, time
import numpy as np, imageio_ffmpeg
from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
FPS = 30
CHROMIUM = os.environ.get('CHROMIUM')
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'montage.html'
PAYSAGE = len(sys.argv) > 2 and sys.argv[2] == 'paysage'
LARGEUR, HAUTEUR = (1920, 1080) if PAYSAGE else (1080, 1920)
SORTIE = ('muet.mp4' if PAGE == 'montage.html'
          else os.path.splitext(PAGE)[0] + ('-paysage' if PAYSAGE else '') + '-muet.mp4')

with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': CHROMIUM} if CHROMIUM else {}))
    pg = b.new_page(viewport={'width': LARGEUR, 'height': HAUTEUR})
    fautes = []
    pg.on('pageerror', lambda e: fautes.append(str(e)))
    pg.goto('file://' + os.path.join(ICI, PAGE) + ('?paysage' if PAYSAGE else ''))
    pg.wait_for_timeout(900)

    duree = pg.evaluate('window.__duree')
    n = int(round(duree * FPS))
    flux = imageio_ffmpeg.write_frames(
        os.path.join(ICI, SORTIE), (LARGEUR, HAUTEUR), fps=FPS,
        codec='libx264', quality=None, macro_block_size=1,
        output_params=['-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p'])
    flux.send(None)

    t0 = time.time()
    for k in range(n):
        pg.evaluate('t => window.__render(t)', k / FPS)
        img = Image.open(io.BytesIO(pg.screenshot(type='png'))).convert('RGB')
        flux.send(np.asarray(img))
        if k % 120 == 0:
            print('  %4d/%d  %.0fs' % (k, n, time.time() - t0), flush=True)
    flux.close()
    b.close()

if fautes:
    raise SystemExit('la page a leve des erreurs : %s' % fautes)
print('%s : %d images, %.1f s' % (SORTIE, n, duree))

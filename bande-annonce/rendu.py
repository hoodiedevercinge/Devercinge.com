# -*- coding: utf-8 -*-
"""Rend montage.html image par image et en fait un mp4 muet.

Les pixels vont directement dans ffmpeg : 915 PNG poses sur le disque ne
serviraient a rien. macro_block_size=1 garde le cadrage exact 1080x1920
qu'attend Instagram, sinon imageio elargit a 1088.

    python3 rendu.py          # -> muet.mp4

Si Chromium n'est pas la ou playwright l'attend, donnez son chemin :

    CHROMIUM=/opt/pw-browsers/chromium python3 rendu.py
"""
import io, os, time
import numpy as np, imageio_ffmpeg
from PIL import Image
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
FPS = 30
CHROMIUM = os.environ.get('CHROMIUM')

with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': CHROMIUM} if CHROMIUM else {}))
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    fautes = []
    pg.on('pageerror', lambda e: fautes.append(str(e)))
    pg.goto('file://' + os.path.join(ICI, 'montage.html'))
    pg.wait_for_timeout(900)

    duree = pg.evaluate('window.__duree')
    n = int(round(duree * FPS))
    flux = imageio_ffmpeg.write_frames(
        os.path.join(ICI, 'muet.mp4'), (1080, 1920), fps=FPS,
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
print('muet.mp4 : %d images, %.1f s' % (n, duree))

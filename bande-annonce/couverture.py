# -*- coding: utf-8 -*-
"""Enregistre une image d'une page de montage, pour servir de couverture.

Sur la grille d'un profil Instagram, un Reel est represente par sa couverture :
c'est elle, et non la video, qui montre le numero d'episode.

    python3 couverture.py banniere.html "reel&episode=1" 7.6 couverture-episode-1.png

Le temps est celui de la video ou la composition est complete.
"""
import os, sys
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
page, fmt, t, sortie = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
taille = (1920, 1080) if fmt.startswith('paysage') else (1080, 1920)
chromium = os.environ.get('CHROMIUM')

with sync_playwright() as p:
    b = p.chromium.launch(**({'executable_path': chromium} if chromium else {}))
    pg = b.new_page(viewport={'width': taille[0], 'height': taille[1]})
    pg.goto('file://' + os.path.join(ICI, page) + '?' + fmt)
    pg.wait_for_timeout(900)
    pg.evaluate('t => window.__render(t)', t)
    pg.wait_for_timeout(150)
    pg.screenshot(path=os.path.join(ICI, sortie))
    b.close()
print(sortie)

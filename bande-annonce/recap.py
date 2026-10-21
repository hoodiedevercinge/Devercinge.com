# -*- coding: utf-8 -*-
"""Produit la bande-annonce recap : portrait et paysage, avec le son.

    python3 recap.py

    devercinge-recap.mp4            portrait, 1080x1920
    devercinge-recap-paysage.mp4    paysage, 1920x1080

Les photos des villes sont facultatives : tout fichier recap-photos/<slug>.jpg
(.jpeg, .png, .webp) apparait en fond sombre pendant que le cycliste traverse la
ville. Les slugs sont dans la liste LIEUX de recap.html. Si Chromium n'est pas la
ou playwright l'attend : CHROMIUM=/opt/pw-browsers/chromium python3 recap.py
"""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
import imageio_ffmpeg

ICI = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()


def lancer(*cmd):
    r = subprocess.run(cmd, cwd=ICI, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(' '.join(cmd) + '\n' + (r.stderr or r.stdout)[-800:])


def rendre(paysage):
    muet = os.path.join(ICI, 'recap-paysage-muet.mp4' if paysage else 'recap-muet.mp4')
    sortie = os.path.join(ICI, 'devercinge-recap-paysage.mp4' if paysage else 'devercinge-recap.mp4')
    lancer(sys.executable, 'rendu.py', 'recap.html', 'paysage' if paysage else '')
    lancer(FF, '-y', '-loglevel', 'error', '-i', muet, '-i', 'habillage-recap.wav',
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', sortie)
    os.remove(muet)
    return sortie


t0 = time.time()
lancer(sys.executable, 'son-recap.py')
print('son pret', flush=True)
with ThreadPoolExecutor(2) as pool:
    for f in pool.map(rendre, (False, True)):
        print('%-32s pret (%.0f s)' % (os.path.basename(f), time.time() - t0), flush=True)
os.remove(os.path.join(ICI, 'habillage-recap.wav'))

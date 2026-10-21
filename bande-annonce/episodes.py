# -*- coding: utf-8 -*-
"""Produit d'un coup une serie de videos numerotees, avec leur image.

    python3 episodes.py                  # Reels verticaux, episodes 1 a 25
    python3 episodes.py 1 8              # seulement les episodes 1 a 8
    python3 episodes.py paysage          # version paysage, episodes 1 a 25
    python3 episodes.py 1 8 paysage

Vertical, dans `episodes/` :
    devercinge-episode-NN-reel.mp4      le Reel (1080x1920, 12 s, avec son)
    couverture-episode-NN.png           la couverture a choisir a l'import

Paysage, dans `episodes-paysage/` :
    devercinge-episode-NN-paysage.mp4   l'animation (1920x1080, 12 s, avec son) :
                                        le mot « Episode » s'ecrit, puis le numero se pose
    image-episode-NN.png                la meme composition, fixe, pour une publication

Les rendus tournent en parallele (un par coeur, au plus quatre). Le son est le
meme pour tous : une seule synthese. Si Chromium n'est pas la ou playwright
l'attend : CHROMIUM=/opt/pw-browsers/chromium python3 episodes.py
"""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import imageio_ffmpeg

ICI = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
PAYSAGE = 'paysage' in sys.argv[1:]
nombres = [a for a in sys.argv[1:] if a.isdigit()]
debut, fin = (int(nombres[0]), int(nombres[1])) if len(nombres) > 1 else (1, 25)
FORMAT = 'paysage' if PAYSAGE else 'reel'
SORTIE = os.path.join(ICI, 'episodes-paysage' if PAYSAGE else 'episodes')
os.makedirs(SORTIE, exist_ok=True)


def lancer(*cmd):
    r = subprocess.run(cmd, cwd=ICI, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(' '.join(cmd) + '\n' + r.stderr[-800:])


def episode(n):
    nn = '%02d' % n
    fmt = '%s&episode=%d' % (FORMAT, n)
    muet = os.path.join(ICI, 'banniere-%s-episode-%d-muet.mp4' % (FORMAT, n))
    reel = os.path.join(SORTIE, 'devercinge-episode-%s-%s.mp4' % (nn, FORMAT))
    lancer(sys.executable, 'rendu.py', 'banniere.html', fmt)
    lancer(FF, '-y', '-loglevel', 'error', '-i', muet, '-i', 'habillage-banniere.wav',
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', reel)
    os.remove(muet)
    image = ('image-episode-%s.png' if PAYSAGE else 'couverture-episode-%s.png') % nn
    lancer(sys.executable, 'couverture.py', 'banniere.html', fmt, '7.6',
           os.path.join(os.path.basename(SORTIE), image))
    return n


t0 = time.time()
lancer(sys.executable, 'son-banniere.py')
travailleurs = min(4, os.cpu_count() or 1)
faits = []
with ThreadPoolExecutor(travailleurs) as pool:
    futurs = {pool.submit(episode, n): n for n in range(debut, fin + 1)}
    for f in as_completed(futurs):
        n = futurs[f]
        try:
            faits.append(f.result())
            print('episode %2d pret   (%2d/%d, %.0f s)' % (n, len(faits), fin - debut + 1, time.time() - t0), flush=True)
        except Exception as e:
            print('episode %2d ECHEC : %s' % (n, e), flush=True)
os.remove(os.path.join(ICI, 'habillage-banniere.wav'))
print('%d episodes sur %d, en %.0f s' % (len(faits), fin - debut + 1, time.time() - t0))

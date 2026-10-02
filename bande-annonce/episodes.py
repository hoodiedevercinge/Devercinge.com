# -*- coding: utf-8 -*-
"""Produit d'un coup une serie de Reels numerotes, avec leur couverture.

    python3 episodes.py              # les episodes 1 a 25
    python3 episodes.py 1 8          # seulement les episodes 1 a 8

Pour chaque numero N, dans le dossier `episodes/` :
    devercinge-episode-NN-reel.mp4      le Reel (1080x1920, 12 s, avec son)
    couverture-episode-NN.png           la couverture a choisir a l'import

Les rendus tournent en parallele (un par coeur, au plus quatre). Le son est le
meme pour tous : une seule synthese. Si Chromium n'est pas la ou playwright
l'attend : CHROMIUM=/opt/pw-browsers/chromium python3 episodes.py
"""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import imageio_ffmpeg

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, 'episodes')
FF = imageio_ffmpeg.get_ffmpeg_exe()
debut, fin = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, 25)
os.makedirs(SORTIE, exist_ok=True)


def lancer(*cmd):
    r = subprocess.run(cmd, cwd=ICI, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(' '.join(cmd) + '\n' + r.stderr[-800:])


def episode(n):
    nn = '%02d' % n
    muet = os.path.join(ICI, 'banniere-reel-episode-%d-muet.mp4' % n)
    reel = os.path.join(SORTIE, 'devercinge-episode-%s-reel.mp4' % nn)
    lancer(sys.executable, 'rendu.py', 'banniere.html', 'reel&episode=%d' % n)
    lancer(FF, '-y', '-loglevel', 'error', '-i', muet, '-i', 'habillage-banniere.wav',
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', reel)
    os.remove(muet)
    lancer(sys.executable, 'couverture.py', 'banniere.html', 'reel&episode=%d' % n,
           '7.6', os.path.join('episodes', 'couverture-episode-%s.png' % nn))
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

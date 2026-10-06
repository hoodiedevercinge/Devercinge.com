# -*- coding: utf-8 -*-
"""Produit les videos d'une ou plusieurs etapes : portrait et paysage, avec le son.

    python3 etapes.py beziers argeliers la-redorte

Pour chaque etape NOM (une entree du bloc #etapes de etape.html) :
    devercinge-etape-NOM.mp4            portrait, 1080x1920
    devercinge-etape-NOM-paysage.mp4    paysage, 1920x1080

Le son est synthetise une fois par etape (son-etape.py), les rendus tournent en
parallele (jusqu'a quatre). Si Chromium n'est pas la ou playwright l'attend :
CHROMIUM=/opt/pw-browsers/chromium python3 etapes.py ...
"""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import imageio_ffmpeg

ICI = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
noms = [a for a in sys.argv[1:] if not a.startswith('-')]
if not noms:
    raise SystemExit(__doc__)


def lancer(*cmd):
    r = subprocess.run(cmd, cwd=ICI, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(' '.join(cmd) + '\n' + (r.stderr or r.stdout)[-800:])


def rendre(nom, paysage):
    fmt = ('paysage&' if paysage else '') + 'etape=' + nom
    muet = os.path.join(ICI, 'etape-%s-muet.mp4' % (('paysage-etape-' if paysage else 'etape-') + nom))
    sortie = os.path.join(ICI, 'devercinge-etape-%s%s.mp4' % (nom, '-paysage' if paysage else ''))
    lancer(sys.executable, 'rendu.py', 'etape.html', fmt)
    lancer(FF, '-y', '-loglevel', 'error', '-i', muet, '-i', 'habillage-etape-%s.wav' % nom,
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', sortie)
    os.remove(muet)
    return sortie


t0 = time.time()
for nom in noms:                       # le son d'abord : les deux formats le partagent
    lancer(sys.executable, 'son-etape.py', nom)
    print('son %s pret' % nom, flush=True)
faits = []
with ThreadPoolExecutor(min(4, os.cpu_count() or 1)) as pool:
    futurs = {pool.submit(rendre, n, p): (n, p) for n in noms for p in (False, True)}
    for f in as_completed(futurs):
        n, p = futurs[f]
        try:
            faits.append(f.result())
            print('%-34s pret (%.0f s)' % (os.path.basename(f.result()), time.time() - t0), flush=True)
        except Exception as e:
            print('%s %s ECHEC : %s' % (n, 'paysage' if p else 'portrait', e), flush=True)
for nom in noms:
    w = os.path.join(ICI, 'habillage-etape-%s.wav' % nom)
    if os.path.exists(w): os.remove(w)
print('%d videos sur %d, en %.0f s' % (len(faits), 2 * len(noms), time.time() - t0))

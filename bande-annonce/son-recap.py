# -*- coding: utf-8 -*-
"""Habillage sonore de la bande-annonce recap, synthetise de zero.

    python3 son-recap.py             # -> habillage-recap.wav

Comme son-etape.py, il lit les reperes de temps dans la page (window.__reperes
de recap.html) : une cloche par lieu traverse, qui monte avec le voyage, un
souffle quand la carte recule, puis la vitrine et la chute comme les etapes.
Si Chromium n'est pas la ou playwright l'attend : CHROMIUM=/opt/pw-browsers/chromium
"""
import wave, os, sys
import numpy as np
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
SR = 44100
SORTIE = 'habillage-recap.wav'


def lire_reperes():
    chromium = os.environ.get('CHROMIUM')
    with sync_playwright() as p:
        b = p.chromium.launch(**({'executable_path': chromium} if chromium else {}))
        pg = b.new_page()
        pg.goto('file://' + os.path.join(ICI, 'recap.html'))
        pg.wait_for_timeout(600)
        r = pg.evaluate('window.__reperes')
        b.close()
    return r


R = lire_reperes()
DUREE = R['duree']
LIEUX = R['lieux']                       # l'instant d'arrivee dans chaque lieu
ZOOM = R['zoom']                         # la carte recule
T_KM, T_VILLES = R['km'], R['villes']
T_PIECE0, T_PIECE_PAS = R['piece0'], R['pas']
T_COLLECTION, T_CHUTE, T_URL = R['collection'], R['chute'], R['url']

N = int(SR * DUREE)
t = np.arange(N) / SR
piste = np.zeros(N)


# ----------------------------------------------------------- outils
def poser(sig, depart):
    i = int(depart * SR)
    if i >= N:
        return
    fin = min(N, i + len(sig))
    piste[i:fin] += sig[:fin - i]


def enveloppe(n, attaque, chute):
    e = np.exp(-np.arange(n) / (chute * SR))
    a = int(attaque * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def cloche(freq, duree, chute, gain=1.0):
    """Partiels inharmoniques : le timbre d'une cloche, pas d'un sinus."""
    n = int(duree * SR)
    x = np.arange(n) / SR
    partiels = [(1.0, 1.0), (2.01, 0.42), (2.97, 0.26), (4.23, 0.14), (5.42, 0.08)]
    s = sum(a * np.sin(2 * np.pi * freq * m * x) * np.exp(-x / (chute / m ** 0.6))
            for m, a in partiels)
    return gain * s * enveloppe(n, 0.004, chute)


def souffle(duree, gain=1.0, montant=True):
    n = int(duree * SR)
    b = np.random.default_rng(7).normal(0, 1, n)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    coupe = env if montant else env[::-1]
    y = np.zeros(n); z = 0.0
    for i in range(n):
        a = 0.02 + 0.22 * coupe[i]
        z += a * (b[i] - z)
        y[i] = z
    y /= (np.abs(y).max() + 1e-9)
    return gain * y * env



# ---------------------------------------------------------------- nappe
nappe = np.zeros(N)
for freq, amp in [(55.0, 0.55), (82.41, 0.30), (110.0, 0.34),
                  (130.81, 0.20), (164.81, 0.16), (220.0, 0.09)]:
    for detune in (-0.13, 0.0, 0.13):
        lfo = 1 + 0.05 * np.sin(2 * np.pi * (0.045 + 0.02 * amp) * t + freq)
        nappe += amp * lfo * np.sin(2 * np.pi * (freq + detune) * t)
air = np.random.default_rng(11).normal(0, 1, N)
z = 0.0; filtre = np.zeros(N)
for i in range(N):
    z += 0.0016 * (air[i] - z)
    filtre[i] = z
nappe += 9.0 * filtre

points = [(0.0, 0.0), (1.4, 0.30), (LIEUX[0], 0.26), (LIEUX[-1], 0.40), (ZOOM[1], 0.44),
          (T_KM, 0.38), (T_PIECE0, 0.28), (T_COLLECTION, 0.38),
          (T_CHUTE + 0.4, 0.52), (T_CHUTE + 1.4, 0.34), (DUREE, 0.0)]
courbe = np.interp(t, [x for x, _ in points], [y for _, y in points])
piste += nappe / (np.abs(nappe).max() + 1e-9) * courbe * 2.2

# ------------------------------------------------- 1. l'en-tete
poser(souffle(1.8, 0.28), 0.15)
poser(cloche(220.0, 2.6, 1.1, 0.26), 1.35)
poser(cloche(329.63, 2.2, 0.9, 0.12), 1.45)

# ------------- 2. une cloche par lieu : la gamme pentatonique monte avec le voyage
# La, do, re, mi, sol sur trois octaves : quinze notes pour vingt-deux lieux.
pentatonique = [0, 3, 5, 7, 10]
demitons = [pentatonique[k % 5] + 12 * (k // 5) for k in range(15)]
n = len(LIEUX)
for i, q in enumerate(LIEUX):
    dernier = (i == n - 1)
    degre = round(i * (len(demitons) - 1) / (n - 1))
    f = 220.0 * 2 ** (demitons[degre] / 12)
    poser(cloche(f, 2.6 if dernier else 1.3, 1.0 if dernier else 0.4,
                 0.30 if dernier else 0.14), q)
# Nice et Carcassonne sonnent double : le depart et l'arrivee
poser(cloche(110.0, 3.0, 1.3, 0.17), LIEUX[0])
poser(cloche(110.0 * 2 ** (demitons[-1] / 12), 3.4, 1.5, 0.17), LIEUX[-1])

# ------------------------------------------ 3. la carte recule
poser(souffle(2.6, 0.24), ZOOM[0])

# -------------------------- 4. les kilometres, puis les villes : deux cloches
poser(cloche(523.25, 2.4, 0.9, 0.16), T_KM + 0.05)
poser(cloche(783.99, 2.6, 1.0, 0.12), T_KM + 0.12)
poser(cloche(659.25, 2.0, 0.7, 0.10), T_VILLES + 0.05)

# ------------------------------- 5. la vitrine, une note par piece levee
poser(souffle(1.2, 0.20, montant=False), T_PIECE0 - 0.7)
for i, f in enumerate([440.00, 523.25, 587.33, 659.25, 783.99]):
    poser(cloche(f, 2.4, 0.85, 0.22 - i * 0.012), T_PIECE0 + i * T_PIECE_PAS)
poser(cloche(329.63, 2.6, 1.0, 0.16), T_COLLECTION + 0.3)

# ------------------------------------------------- 6. la chute
poser(souffle(1.4, 0.24, montant=False), T_CHUTE - 0.9)
poser(cloche(220.0, 3.4, 1.7, 0.40), T_CHUTE + 0.35)
poser(cloche(329.63, 3.2, 1.5, 0.22), T_CHUTE + 0.45)
poser(cloche(440.0, 3.0, 1.3, 0.11), T_CHUTE + 0.55)
poser(cloche(659.25, 2.2, 0.9, 0.07), T_URL + 0.15)   # sur l'adresse du site

# ------------------------------------------------- finition
fd = int(0.3 * SR)
piste[:fd] *= np.linspace(0, 1, fd)
piste[-int(1.1 * SR):] *= np.linspace(1, 0, int(1.1 * SR))
piste = np.tanh(piste * 0.85)
piste *= 10 ** (-1.5 / 20) / (np.abs(piste).max() + 1e-9)

pcm = (np.stack([piste, piste], axis=1) * 32767).astype(np.int16)
with wave.open(os.path.join(ICI, SORTIE), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())

print('%s  %.1f s  crete %.1f dBFS  rms %.1f dBFS'
      % (SORTIE, DUREE, 20 * np.log10(np.abs(piste).max()),
         20 * np.log10(np.sqrt(np.mean(piste ** 2)))))
print('%d lieux, de %.2f s a %.2f s | carte qui recule %.2f s | vitrine %.2f s | chute %.2f s'
      % (len(LIEUX), LIEUX[0], LIEUX[-1], ZOOM[0], T_PIECE0, T_CHUTE))

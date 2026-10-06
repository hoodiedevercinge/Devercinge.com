# -*- coding: utf-8 -*-
"""Habillage sonore de la video d'etape, synthetise de zero.

    python3 son-etape.py              # etape de Montpellier -> habillage-etape.wav
    python3 son-etape.py meze         # etape de Meze        -> habillage-etape-meze.wav

Les reperes de temps ne sont ni recopies ni devines : le script ouvre
etape.html dans Chromium et lit `window.__reperes`, l'objet que la page
construit pour se peindre elle-meme. Deplacer une scene dans la page deplace la
note avec elle, et le son ne peut pas se desynchroniser de l'image. Si Chromium
n'est pas la ou playwright l'attend : CHROMIUM=/opt/pw-browsers/chromium
"""
import wave, os, sys
import numpy as np
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
SR = 44100
NOM_ETAPE = sys.argv[1] if len(sys.argv) > 1 else 'montpellier'
SORTIE = 'habillage-etape.wav' if NOM_ETAPE == 'montpellier' else 'habillage-etape-%s.wav' % NOM_ETAPE


def lire_reperes():
    chromium = os.environ.get('CHROMIUM')
    with sync_playwright() as p:
        b = p.chromium.launch(**({'executable_path': chromium} if chromium else {}))
        pg = b.new_page()
        pg.goto('file://' + os.path.join(ICI, 'etape.html') + '?etape=' + NOM_ETAPE)
        pg.wait_for_timeout(600)
        r = pg.evaluate('window.__reperes')
        b.close()
    return r


R = lire_reperes()
DUREE = R['duree']
T_TRACE1 = R['trace'][1]
quand = R['validations']                 # l'instant ou le trait atteint chaque point
T_LIGNES = R['lignes']                   # le nom, le decompte, les kilometres
T_PLUS = R['plus']                       # l'augmentation et « depuis ... » (None si l'etape n'en a pas)
T_RESTE = R['reste']
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

points = [(0.0, 0.0), (1.4, 0.30), (2.4, 0.26), (T_TRACE1, 0.46), (T_TRACE1 + 1.0, 0.30),
          (8.6, 0.26), (T_LIGNES[2] + 0.7, 0.38)]
if T_PLUS:
    points.append((T_PLUS[1] + 0.7, 0.38))
points += [(T_RESTE[1], 0.34), (T_PIECE0, 0.28), (T_COLLECTION, 0.38),
           (T_CHUTE + 0.4, 0.52), (T_CHUTE + 1.4, 0.34), (DUREE, 0.0)]
courbe = np.interp(t, [x for x, _ in points], [y for _, y in points])
piste += nappe / (np.abs(nappe).max() + 1e-9) * courbe * 2.2

# ------------------------------------------------- 1. l'en-tete
poser(souffle(1.8, 0.28), 0.15)
poser(cloche(220.0, 2.6, 1.1, 0.26), 1.35)
poser(cloche(329.63, 2.2, 0.9, 0.12), 1.45)

# ------------------- 2. une note par ville validee, de plus en plus haut
gamme = [329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99, 880.00,
         987.77, 1046.50, 1174.66]
for i, q in enumerate(quand):
    dernier = (i == len(quand) - 1)
    poser(cloche(gamme[i], 2.6 if dernier else 1.5, 1.0 if dernier else 0.45,
                 0.30 if dernier else 0.15), q)
# l'etape du jour sonne double
poser(cloche(gamme[len(quand) - 1] / 2, 3.0, 1.3, 0.17), quand[-1])

# ------------------------------------------- 3. le monument se dessine
poser(souffle(1.6, 0.18), 8.5)

# ------------------------------------------- 4. les trois lignes de texte
for k, (q, f) in enumerate(zip(T_LIGNES, (523.25, 659.25, 783.99))):
    poser(cloche(f, 2.0, 0.7, 0.12 - k * 0.015), q + 0.05)

# --------------- 4 bis. l'augmentation des kilometres : une quinte qui monte
if T_PLUS:
    poser(cloche(659.25, 2.2, 0.8, 0.14), T_PLUS[0] + 0.05)
    poser(cloche(987.77, 2.2, 0.8, 0.09), T_PLUS[0] + 0.12)
    poser(cloche(523.25, 1.8, 0.6, 0.09), T_PLUS[1] + 0.05)

# ------------------------- 5. le reste a parcourir : deux cloches, la seconde plus haute
poser(cloche(440.00, 2.0, 0.7, 0.13), T_RESTE[0] + 0.05)
poser(cloche(587.33, 2.6, 0.9, 0.16), T_RESTE[1] + 0.05)
poser(cloche(880.00, 2.2, 0.8, 0.07), T_RESTE[1] + 0.12)

# ------------------------------- 6. la vitrine, une note par piece levee
poser(souffle(1.2, 0.20, montant=False), T_PIECE0 - 0.7)
for i, f in enumerate([440.00, 523.25, 587.33, 659.25, 783.99]):
    poser(cloche(f, 2.4, 0.85, 0.22 - i * 0.012), T_PIECE0 + i * T_PIECE_PAS)
poser(cloche(329.63, 2.6, 1.0, 0.16), T_COLLECTION + 0.3)

# ------------------------------------------------- 7. la chute
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
print('villes validees a : ' + ', '.join('%.2f s' % q for q in quand))
print('lignes de chiffres a : ' + ', '.join('%.2f s' % q for q in T_LIGNES))
if T_PLUS: print('augmentation a : ' + ', '.join('%.2f s' % q for q in T_PLUS))
print('reste a parcourir a : ' + ', '.join('%.2f s' % q for q in T_RESTE))
print('vitrine a %.2f s (pas %.2f) | collection %.2f | chute %.2f | adresse %.2f'
      % (T_PIECE0, T_PIECE_PAS, T_COLLECTION, T_CHUTE, T_URL))

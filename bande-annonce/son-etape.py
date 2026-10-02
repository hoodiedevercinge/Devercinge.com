# -*- coding: utf-8 -*-
"""Habillage sonore de la video d'etape, synthetise de zero.

Les reperes de temps sont calcules a partir de etape.html -- l'indice de la
ville atteinte y est lu, et les instants de validation sont recalcules avec
la meme projection que la page. Changer d'etape ne demande donc de toucher
qu'a un seul fichier.
"""
import math, re, wave, os
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SR = 44100
DUREE = 15.0
N = int(SR * DUREE)
t = np.arange(N) / SR
piste = np.zeros(N)


# ------------------------------------------------- ce que dit la page
page = open(os.path.join(ICI, 'etape.html'), encoding='utf-8').read()
ATTEINTE = int(re.search(r'const ATTEINTE = (\d+)', page).group(1))
T_TRACE0, T_TRACE1 = (float(x) for x in
                      re.search(r'T_TRACE0 = ([\d.]+), T_TRACE1 = ([\d.]+)', page).groups())

VILLES = [(43.7102, 7.2620), (43.2965, 5.3698), (43.6108, 3.8767), (43.1836, 3.0036),
          (43.6047, 1.4442), (44.8378, -0.5792), (46.1591, -1.1578), (47.2199, -1.5582),
          (47.4784, -0.5632), (48.1173, -1.6778), (48.6493, -2.0257)]

# Meme projection que la page : la longueur parcourue se mesure a l'ecran,
# pas sur le terrain, sinon les notes tomberaient a cote du trait.
merc = lambda la: math.log(math.tan(math.pi / 4 + la * math.pi / 360))
bx = [lo * math.pi / 180 for la, lo in VILLES]
by = [merc(la) for la, lo in VILLES]
P = list(zip(bx, by))
cum = [0.0]
for i in range(1, ATTEINTE + 1):
    cum.append(cum[-1] + math.hypot(P[i][0] - P[i-1][0], P[i][1] - P[i-1][1]))
quand = [T_TRACE0 + (c / cum[-1]) * (T_TRACE1 - T_TRACE0) for c in cum] if cum[-1] else [T_TRACE0]


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

courbe = np.interp(t,
    [0.0, 1.4,  2.4,  T_TRACE1, T_TRACE1 + 1.0, 8.6,  11.6, 12.9, 13.6, 15.0],
    [0.0, 0.30, 0.26, 0.46,     0.30,           0.26, 0.34, 0.50, 0.34, 0.0])
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
for k, (q, f) in enumerate(zip((10.35, 10.95, 11.35), (523.25, 659.25, 783.99))):
    poser(cloche(f, 1.8, 0.6, 0.11 - k * 0.015), q)

# ------------------------------------------------- 5. la chute
poser(souffle(1.4, 0.24, montant=False), 12.3)
poser(cloche(220.0, 3.4, 1.7, 0.40), 12.80)
poser(cloche(329.63, 3.2, 1.5, 0.22), 12.90)
poser(cloche(440.0, 3.0, 1.3, 0.11), 13.00)
poser(cloche(659.25, 2.2, 0.9, 0.07), 13.85)   # sur l'adresse du site

# ------------------------------------------------- finition
fd = int(0.3 * SR)
piste[:fd] *= np.linspace(0, 1, fd)
piste[-int(1.1 * SR):] *= np.linspace(1, 0, int(1.1 * SR))
piste = np.tanh(piste * 0.85)
piste *= 10 ** (-1.5 / 20) / (np.abs(piste).max() + 1e-9)

pcm = (np.stack([piste, piste], axis=1) * 32767).astype(np.int16)
with wave.open(os.path.join(ICI, 'habillage-etape.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())

print('habillage-etape.wav  %.1f s  crete %.1f dBFS  rms %.1f dBFS'
      % (DUREE, 20 * np.log10(np.abs(piste).max()),
         20 * np.log10(np.sqrt(np.mean(piste ** 2)))))
print('villes validees a : ' + ', '.join('%.2f s' % q for q in quand))

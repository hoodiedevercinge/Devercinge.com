# -*- coding: utf-8 -*-
"""Habillage sonore de la story Devercinge, synthetise de zero.

Tout est genere par calcul : aucune source exterieure, donc rien a
crediter ni a licencier. Les reperes de temps suivent ceux du montage
dans story-v3.html.
"""
import numpy as np, wave, struct

SR = 44100
DUREE = 30.5
N = int(SR * DUREE)
t = np.arange(N) / SR
piste = np.zeros(N)


def poser(sig, depart):
    """Ajoute un son a un instant donne, en rognant ce qui depasse."""
    i = int(depart * SR)
    if i >= N:
        return
    fin = min(N, i + len(sig))
    piste[i:fin] += sig[:fin - i]


def enveloppe(n, attaque, chute):
    """Attaque lineaire puis decroissance exponentielle."""
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
    """Bruit filtre en va-et-vient : la respiration entre deux plans."""
    n = int(duree * SR)
    b = np.random.default_rng(7).normal(0, 1, n)
    # passe-bas a un pole, dont la coupure suit l'enveloppe
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    coupe = env if montant else env[::-1]
    y = np.zeros(n); z = 0.0
    for i in range(n):
        a = 0.02 + 0.22 * coupe[i]
        z += a * (b[i] - z)
        y[i] = z
    y /= (np.abs(y).max() + 1e-9)
    return gain * y * env


def pas(gain=1.0):
    """Un pas : une frappe grave et un frottement bref."""
    n = int(0.26 * SR)
    x = np.arange(n) / SR
    f = 92 * np.exp(-x * 26) + 48          # la hauteur chute vite
    corps = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.055)
    gr = np.random.default_rng(3).normal(0, 1, n) * np.exp(-x / 0.012) * 0.30
    return gain * (corps + gr)


# ---------------------------------------------------------------- nappe
# Un la mineur tenu, legerement desaccorde, qui respire sous tout le film.
nappe = np.zeros(N)
for freq, amp in [(55.0, 0.55), (82.41, 0.30), (110.0, 0.34),
                  (130.81, 0.20), (164.81, 0.16), (220.0, 0.09)]:
    for detune in (-0.13, 0.0, 0.13):
        lfo = 1 + 0.05 * np.sin(2 * np.pi * (0.045 + 0.02 * amp) * t + freq)
        nappe += amp * lfo * np.sin(2 * np.pi * (freq + detune) * t)
# souffle d'air tres discret par-dessus
air = np.random.default_rng(11).normal(0, 1, N)
z = 0.0; filtre = np.zeros(N)
for i in range(N):
    z += 0.0016 * (air[i] - z)
    filtre[i] = z
nappe += 9.0 * filtre

# le volume de la nappe suit la dramaturgie
courbe = np.interp(t,
    [0.0, 2.0,  4.6,  5.0,  9.6,  10.2, 15.6, 16.4, 18.4, 26.0, 28.1, 29.2, 30.5],
    [0.0, 0.34, 0.30, 0.22, 0.24, 0.26, 0.38, 0.30, 0.26, 0.30, 0.52, 0.34, 0.0])
piste += nappe / (np.abs(nappe).max() + 1e-9) * courbe * 2.2

# ------------------------------------------------------- 1. le logo
poser(souffle(2.2, 0.30), 0.2)
poser(cloche(220.0, 3.4, 1.5, 0.34), 1.85)
poser(cloche(329.63, 3.0, 1.2, 0.16), 1.95)

# ------------------------------- 2. les cinq fenetres, une par note
poser(souffle(1.0, 0.20, montant=False), 4.4)
for i, f in enumerate([440.00, 523.25, 587.33, 659.25, 783.99]):
    poser(cloche(f, 2.6, 0.95, 0.30 - i * 0.012), 4.95 + i * 0.38)

# ------------------------- 3. la carte : une note par ville atteinte
# Les reperes sont ceux de story-v4.html : premiere halte a 10,2 s,
# puis une ville toutes les HALTE + JAMBE = 0,56 s.
poser(souffle(1.1, 0.22), 9.6)
CARTE_T0, PAS_VILLE = 10.2, 0.56
gamme = [220.00, 261.63, 293.66, 329.63, 392.00, 440.00,
         523.25, 587.33, 659.25, 783.99, 880.00]
for i, f in enumerate(gamme):
    dernier = (i == len(gamme) - 1)
    poser(cloche(f, 2.4 if dernier else 1.6, 1.0 if dernier else 0.5,
                 0.26 if dernier else 0.115), CARTE_T0 + i * PAS_VILLE)
poser(cloche(440.0, 2.6, 1.1, 0.13), CARTE_T0 + 10 * PAS_VILLE)   # l'arrivee sonne double


# ------------------------------ 4. le defile des monuments, 8,8 s
poser(souffle(1.0, 0.20), 18.3)
pas_a, pas_b = pas(0.26), pas(0.20)
k, temps_pas = 0, 18.75
while temps_pas < 27.4:
    poser(pas_a if k % 2 == 0 else pas_b, temps_pas)
    k += 1
    temps_pas += 0.545

# Un timbre tres doux quand chaque monument passe au centre. Le defile est
# amorti aux deux bouts : on inverse le lissage pour tomber juste.
def quand_monument(i):
    y = i / 10.0
    x = 0.5 - np.sin(np.arcsin(1 - 2 * y) / 3)      # inverse de x*x*(3-2x)
    return 18.7 + x * 8.8

for i in range(11):
    poser(cloche(gamme[i], 1.8, 0.55, 0.075), quand_monument(i))


# ------------------------------------------------- 5. la chute
poser(souffle(1.6, 0.26, montant=False), 27.8)
poser(cloche(220.0, 3.8, 1.9, 0.42), 28.35)
poser(cloche(329.63, 3.6, 1.6, 0.24), 28.45)
poser(cloche(440.0, 3.4, 1.4, 0.12), 28.55)
poser(cloche(659.25, 2.6, 1.0, 0.07), 29.45)   # sur l'adresse du site

# ------------------------------------------------- finition
# fondu d'entree et de sortie pour eviter tout claquement
fd = int(0.35 * SR)
piste[:fd] *= np.linspace(0, 1, fd)
piste[-int(1.2 * SR):] *= np.linspace(1, 0, int(1.2 * SR))

# limitation douce puis marge de 1,5 dB sous le maximum
piste = np.tanh(piste * 0.85)
piste *= 10 ** (-1.5 / 20) / (np.abs(piste).max() + 1e-9)

stereo = np.stack([piste, piste], axis=1)
pcm = (stereo * 32767).astype(np.int16)
with wave.open('habillage.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())

crete = 20 * np.log10(np.abs(piste).max())
rms = 20 * np.log10(np.sqrt(np.mean(piste ** 2)))
print("habillage.wav  %.1f s  crete %.1f dBFS  rms %.1f dBFS" % (DUREE, crete, rms))

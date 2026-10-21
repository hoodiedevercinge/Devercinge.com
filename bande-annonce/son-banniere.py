# -*- coding: utf-8 -*-
"""Habillage sonore de la banniere, synthetise de zero, qui boucle sans couture.

Un Reel se rejoue en boucle : si le son n'est pas periodique, on entend un
claquement a chaque tour. Trois precautions :
  * la nappe n'utilise que des frequences a nombre entier de periodes dans la
    boucle, donc elle revient a la meme phase ;
  * ses variations de volume sont des cosinus de periode DUREE ;
  * les cloches sont posees « en cercle » : la queue d'une cloche qui depasse la
    fin de la boucle revient par le debut au lieu d'etre coupee.
Les reperes de temps sont lus dans banniere.html.
"""
import math, re, wave, os
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
SR = 44100
page = open(os.path.join(ICI, 'banniere.html'), encoding='utf-8').read()
DUREE = float(re.search(r'const DUREE = ([\d.]+)', page).group(1))
T_DEBUT, T_FIN = (float(x) for x in re.search(r'T_DEBUT = ([\d.]+), T_FIN = ([\d.]+)', page).groups())
VILLES = [(float(a), float(b)) for a, b in re.findall(r'\[(-?[\d.]+),\s*(-?[\d.]+)\]',
          re.search(r'const VILLES = \[(.*?)\];', page, re.S).group(1))]
N = int(round(SR * DUREE))
t = np.arange(N) / SR
piste = np.zeros(N)

# Meme projection que la page : les notes tombent quand le trait atteint la ville.
merc = lambda la: math.log(math.tan(math.pi / 4 + la * math.pi / 360))
P = [(lo * math.pi / 180, merc(la)) for la, lo in VILLES]
cum = [0.0]
for i in range(1, len(P)):
    cum.append(cum[-1] + math.hypot(P[i][0] - P[i-1][0], P[i][1] - P[i-1][1]))
quand = [T_DEBUT + (c / cum[-1]) * (T_FIN - T_DEBUT) for c in cum]


def poser(sig, depart):
    """Pose un son a `depart`, et rabat ce qui depasse la fin sur le debut."""
    i = int(depart * SR) % N
    for k in range(0, len(sig), N):          # une queue plus longue que la boucle
        morceau = sig[k:k + N]
        fin = i + len(morceau)
        if fin <= N:
            piste[i:fin] += morceau
        else:
            piste[i:] += morceau[:N - i]
            piste[:fin - N] += morceau[N - i:]


def cloche(freq, duree, chute, gain=1.0):
    n = int(duree * SR)
    x = np.arange(n) / SR
    partiels = [(1.0, 1.0), (2.01, 0.42), (2.97, 0.26), (4.23, 0.14), (5.42, 0.08)]
    s = sum(a * np.sin(2 * np.pi * freq * m * x) * np.exp(-x / (chute / m ** 0.6))
            for m, a in partiels)
    e = np.exp(-np.arange(n) / (chute * SR))
    a = int(0.004 * SR)
    e[:a] *= np.linspace(0, 1, a)
    return gain * s * e


# ------------------------------------------------ nappe, periodique par construction
nappe = np.zeros(N)
for f, amp in [(55.0, 0.55), (82.5, 0.30), (110.0, 0.34), (165.0, 0.20),
               (220.0, 0.16), (330.0, 0.07)]:
    assert abs(f * DUREE - round(f * DUREE)) < 1e-9, 'frequence hors boucle'
    # la phase n'est pas nulle : un attaque franche a t=0 s'entendrait au raccord
    nappe += amp * np.sin(2 * np.pi * f * t + f)
# le volume respire une fois par boucle
respire = 1 + 0.18 * np.cos(2 * np.pi * (t - T_FIN) / DUREE)
piste += nappe / (np.abs(nappe).max() + 1e-9) * 0.34 * respire * 2.0

# ------------------------------------------------ une note par ville atteinte
gamme = [329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99, 880.00,
         987.77, 1046.50, 1174.66]
for i, q in enumerate(quand):
    dernier = (i == len(quand) - 1)
    poser(cloche(gamme[i], 2.6 if dernier else 1.5, 1.0 if dernier else 0.45,
                 0.30 if dernier else 0.15), q)
poser(cloche(gamme[-1] / 2, 3.0, 1.3, 0.17), quand[-1])     # l'arrivee sonne double
poser(cloche(220.0, 3.0, 1.2, 0.14), 0.0)                    # et le depart pose la note de base

# ------------------------------------------------ finition (aucun fondu : on boucle)
piste = np.tanh(piste * 0.85)
piste *= 10 ** (-4.5 / 20) / (np.abs(piste).max() + 1e-9)   # un fond sonore, pas une piste de tete

pcm = (np.stack([piste, piste], axis=1) * 32767).astype(np.int16)
with wave.open(os.path.join(ICI, 'habillage-banniere.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())

# Le raccord : le saut entre le dernier echantillon et le premier doit etre du
# meme ordre que le saut entre deux echantillons voisins, pas plus.
pas = np.abs(np.diff(piste))
raccord = abs(piste[0] - piste[-1])
print('habillage-banniere.wav  %.1f s  crete %.1f dBFS  rms %.1f dBFS'
      % (DUREE, 20 * np.log10(np.abs(piste).max()), 20 * np.log10(np.sqrt(np.mean(piste ** 2)))))
print('raccord : saut %.5f  (saut voisin typique %.5f, maximal %.5f)'
      % (raccord, np.median(pas), pas.max()))

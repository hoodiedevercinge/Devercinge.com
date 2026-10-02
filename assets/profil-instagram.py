# -*- coding: utf-8 -*-
"""Fabrique le logo de profil Instagram : casque et mot « devercinge » blancs
sur un degrade diagonal violet -> vert, 1080x1080.

    python3 profil-instagram.py                    # -> instagram-profil.png
    python3 profil-instagram.py --vivacite 0.8     # un fond plus vif (voir plus bas)
    python3 profil-instagram.py --sortie essai.png

Sources : logo-mark.png (le casque, a transparence) et wordmark-devercinge.png
(le mot, blanc a transparence). Rien d'autre : le fond est calcule.

Trois reglages, aux valeurs retenues :

  VIVACITE  part du chemin entre l'ancien ton (sampled sur la carte de visite) et
            les couleurs du site (#9b6bff, #3ddc84). 0 = l'ancien fond terne ;
            1 = les couleurs du site. 0,45 est le choix retenu : le blanc garde
            un contraste de 3,5 au minimum sous le logo (WCAG demande 3 pour un
            grand element graphique). A 0,8 il tombe a 2,4 : le blanc se noie
            dans la zone pastel du milieu du degrade.
  CASQUE    1,20 : le casque est 20 % plus grand qu'a l'origine (414 -> 497 px).
  MOT       1,10 : le mot grandit un peu moins, pour garder l'equilibre.

Le degrade est interpole dans OKLab, pas en RGB : interpoler du violet vers du
vert en RGB passe par un gris-bleu boueux ; OKLab garde la couleur vive.

Le logo doit rester dans le cercle que montre Instagram : le script le verifie
et refuse de produire une image dont le logo approche le bord a moins de 40 px.
"""
import argparse, os
import numpy as np
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
N = 1080
VIVACITE, CASQUE, MOT = 0.45, 1.20, 1.10
HAUTEUR_ORIGINE, ECART_ORIGINE = 414, 59     # mesures sur l'ancienne image

VIOLET_ANCIEN, VERT_ANCIEN = np.array([99, 78, 162.]), np.array([42, 113, 81.])
VIOLET_SITE, VERT_SITE = np.array([155, 107, 255.]), np.array([61, 220, 132.])

M1 = np.array([[.4122214708, .5363325363, .0514459929],
               [.2119034982, .6806995451, .1073969566],
               [.0883024619, .2817188376, .6299787005]])
M2 = np.array([[.2104542553, .7936177850, -.0040720468],
               [1.9779984951, -2.4285922050, .4505937099],
               [.0259040371, .7827717662, -.8086757660]])


def vers_lineaire(c):
    c = c / 255.
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def vers_srgb(c):
    c = np.clip(c, 0, 1)
    return 255 * np.where(c <= .0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - .055)


def en_oklab(rgb):
    return np.cbrt(vers_lineaire(np.asarray(rgb, float)) @ M1.T) @ M2.T


def depuis_oklab(lab):
    return vers_srgb(((lab @ np.linalg.inv(M2).T) ** 3) @ np.linalg.inv(M1).T)


def fond(vivacite):
    c0 = VIOLET_ANCIEN + vivacite * (VIOLET_SITE - VIOLET_ANCIEN)
    c1 = VERT_ANCIEN + vivacite * (VERT_SITE - VERT_ANCIEN)
    yy, xx = np.mgrid[0:N, 0:N]
    t = ((xx + yy) / (2 * (N - 1)))[..., None]
    return depuis_oklab(en_oklab(c0) + t * (en_oklab(c1) - en_oklab(c0)))


def composer(vivacite):
    logo = Image.open(os.path.join(ICI, 'logo-mark.png')).convert('RGBA')
    logo = logo.crop(logo.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    mot = Image.open(os.path.join(ICI, 'wordmark-devercinge.png')).convert('RGBA')

    hh = round(HAUTEUR_ORIGINE * CASQUE)
    hw = round(logo.width * hh / logo.height)
    casque = logo.resize((hw, hh), Image.LANCZOS)
    mw, mh = round(mot.width * MOT), round(mot.height * MOT)
    mot = mot.resize((mw, mh), Image.LANCZOS)
    ecart = round(ECART_ORIGINE * CASQUE)
    haut = round((N - (hh + ecart + mh - 12)) / 2)      # 12 px de marge transparente autour du mot

    img = Image.fromarray(fond(vivacite).round().astype(np.uint8), 'RGB').convert('RGBA')
    for el, pos in ((casque, ((N - hw) // 2, haut)), (mot, ((N - mw) // 2, haut + hh + ecart - 6))):
        blanc = Image.new('RGBA', el.size, (255, 255, 255, 0))      # blanc pur : seule la forme compte
        blanc.putalpha(el.getchannel('A'))
        img.alpha_composite(blanc, pos)
    return img.convert('RGB')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--vivacite', type=float, default=VIVACITE)
    p.add_argument('--sortie', default=os.path.join(ICI, 'instagram-profil.png'))
    a = p.parse_args()
    img = composer(a.vivacite)
    px = np.argwhere(np.asarray(img).astype(int).min(axis=2) > 235)
    marge = N / 2 - np.hypot(px[:, 0] - N / 2, px[:, 1] - N / 2).max()
    if marge < 40:
        raise SystemExit('le logo approche le bord du cercle a %.0f px (minimum 40)' % marge)
    img.save(a.sortie)
    print('%s : %dx%d, vivacite %.2f, le logo reste a %.0f px du bord du cercle' % (a.sortie, N, N, a.vivacite, marge))

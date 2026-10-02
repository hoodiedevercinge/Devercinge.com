# Les videos

Deux films, meme fabrique : 1080x1920 pour Instagram. Tout est fabrique ici : le
montage est une page web rendue image par image, le son est synthetise par
calcul. Aucune source exterieure, donc rien a crediter ni a licencier.

| fichier | role |
|---|---|
| `montage.html` | le film. `window.__render(t)` peint l'instant `t`, `window.__duree` donne la longueur. Deterministe : la meme seconde donne toujours la meme image. |
| `monuments.js` | les onze monuments au trait, un par ville, dans une boite de 200x200 posee sur une ligne de sol a y=200. |
| `son.py` | l'habillage sonore. Nappe, cloches inharmoniques, souffles et pas, tout en numpy. |
| `etape.html` | la video d'etape : une ville validee en cours de route. |
| `son-etape.py` | son habillage sonore. |
| `rendu.py` | pousse les images d'une page dans ffmpeg. |
| `devercinge-bande-annonce.mp4` | la bande-annonce. |
| `devercinge-etape-montpellier.mp4` | l'etape de Montpellier. |

## Refaire le film

```sh
python3 son.py      # -> habillage.wav
python3 rendu.py    # -> muet.mp4  (environ 3 minutes)
ffmpeg -y -i muet.mp4 -i habillage.wav \
       -c:v copy -c:a aac -b:a 192k -shortest devercinge-bande-annonce.mp4
```

Il faut `playwright` (avec Chromium installe via `playwright install`),
`pillow`, `numpy` et `imageio-ffmpeg`. Si Chromium est ailleurs, passez son
chemin : `CHROMIUM=/opt/pw-browsers/chromium python3 rendu.py`.

## Refaire une video d'etape

Une seule ligne a changer, en haut du script de `etape.html` :

```js
const ATTEINTE = 2;     // indice de la derniere ville franchie (0 = Nice)
const KM_FAITS = 322;   // kilometres parcourus -- a remplacer par le releve GPS
```

`ATTEINTE` suit l'ordre du trace : 0 Nice, 1 Marseille, 2 Montpellier,
3 Narbonne, 4 Toulouse, 5 Bordeaux, 6 La Rochelle, 7 Nantes, 8 Angers,
9 Rennes, 10 Saint-Malo. Le monument, le nom, le decompte des villes et les
kilometres en toutes lettres suivent tout seuls.

```sh
python3 son-etape.py            # -> habillage-etape.wav
python3 rendu.py etape.html     # -> etape-muet.mp4
ffmpeg -y -i etape-muet.mp4 -i habillage-etape.wav \
       -c:v copy -c:a aac -b:a 192k -shortest devercinge-etape-<ville>.mp4
```

`son-etape.py` lit dans `etape.html` tout ce qui porte une date : `ATTEINTE`,
`DUREE`, les bornes du trace, les trois lignes du bloc de chiffres, le depart
de la vitrine et son pas, l'entree du mot et celle de la chute. Plus une seule
date n'y est ecrite en dur. Il recalcule ensuite les instants de validation avec
la meme projection que la page. Contrairement a la bande-annonce, l'image et
le son d'une etape ne peuvent donc pas se desynchroniser : deplacer une scene
dans la page deplace la note avec elle.

## Les cinq temps de la bande-annonce

| | |
|---|---|
| 0 -> 4,8 s | le logo, « Deux createurs » |
| 4,6 -> 9,9 s | les cinq pieces qui se levent une par une |
| 9,8 -> 18,6 s | le trace se dessine, ville apres ville |
| 18,4 -> 28,3 s | les onze monuments defilent |
| 28,2 -> 30,5 s | le logo, « Un seul reve », devercinge.com |

## Les quatre temps de la video d'etape

| | |
|---|---|
| 0 -> 8,1 s | la carte : le trait vert progresse, chaque ville franchie recoit sa coche |
| 8,1 -> 15,2 s | le monument de l'etape se dessine, puis le nom, le decompte et les kilometres |
| 15,0 -> 19,8 s | la vitrine : les cinq pieces se levent une a une, « Cinq pieces » |
| 19,7 -> 22,5 s | le logo, « La route continue », devercinge.com |

Le bloc de chiffres garde volontairement la pose : une fois les trois lignes
installees, rien ne bouge pendant plus de deux secondes. Mesure sur la page,
image par image, le temps ou chaque ligne est pleinement opaque : le nom de
la ville 3,6 s, le decompte 2,9 s, les kilometres 2,2 s. La derniere ligne
est celle qui arrive, c'est donc elle qui commande la duree de la scene --
la raccourcir la rend illisible avant les autres.

Le vert dit ce qui est fait, le gris ce qui reste, et Saint-Malo garde son
cercle violet de but.

La vitrine reprend les images de `assets/products/` dans l'ordre ou
`boutique.html` les presente : la vitrine du film et celle du site montrent
la meme chose. Une piece ajoutee ou retiree la-bas se reporte dans le tableau
`PIECES` en haut du script -- et le mot « Cinq pieces » avec, puisqu'il est
ecrit a la main lui.

## Deux choses a savoir avant d'y toucher

**Les reperes de temps de la bande-annonce sont ecrits deux fois**, dans
`montage.html` et dans `son.py`. Deplacer une scene sans reporter la meme valeur dans l'autre
fichier desynchronise l'image et le son. Les constantes qui comptent sont
`CARTE_T0`, `HALTE` et `JAMBE` cote image, et la table `courbe` cote son.

**Les villes ne sont pas nommees sur la carte**, seulement Nice et
Saint-Malo, comme sur `aventure.html` au repos. Un relais de tous les noms
avait ete essaye : chaque nom ne tenait que trois dixiemes de seconde, donc
illisible, et le defile des monuments les nomme deja un par un.

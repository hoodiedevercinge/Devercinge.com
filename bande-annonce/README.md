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
| `banniere.html` | la banniere : une boucle de 12 s, en 16:9 par defaut et en Reel avec `?reel`. |
| `son-banniere.py` | le son du Reel, qui boucle lui aussi sans couture. |
| `rendu.py` | pousse les images d'une page dans ffmpeg. |
| `devercinge-bande-annonce.mp4` | la bande-annonce. |
| `devercinge-etape-montpellier.mp4` | l'etape de Montpellier, en portrait (1080x1920). |
| `devercinge-etape-montpellier-paysage.mp4` | la meme, en paysage (1920x1080). |
| `devercinge-banniere.mp4` | la banniere, 1920x1080, 12 s, sans son, faite pour boucler. |
| `devercinge-banniere-reel.mp4` | la banniere pour Instagram, 1080x1920, 12 s, avec son, en boucle. |
| `devercinge-episode-1-reel.mp4` | la meme avec « Episode 1 » en grand au centre. |
| `couverture-episode-1.png` | l'image de couverture du Reel, celle que montre la grille du profil. |
| `couverture.py` | enregistre une image d'une page de montage. |

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
const KM_TOTAL = 1408;  // longueur du parcours ; le reste s'en deduit
```

`ATTEINTE` suit l'ordre du trace : 0 Nice, 1 Marseille, 2 Montpellier,
3 Narbonne, 4 Toulouse, 5 Bordeaux, 6 La Rochelle, 7 Nantes, 8 Angers,
9 Rennes, 10 Saint-Malo. Le monument, le nom, le decompte des villes et les
kilometres en toutes lettres suivent tout seuls.

```sh
python3 son-etape.py                  # -> habillage-etape.wav
python3 rendu.py etape.html           # -> etape-muet.mp4          (portrait)
python3 rendu.py etape.html paysage   # -> etape-paysage-muet.mp4  (paysage)
ffmpeg -y -i etape-muet.mp4 -i habillage-etape.wav \
       -c:v copy -c:a aac -b:a 192k -shortest devercinge-etape-<ville>.mp4
ffmpeg -y -i etape-paysage-muet.mp4 -i habillage-etape.wav \
       -c:v copy -c:a aac -b:a 192k -shortest devercinge-etape-<ville>-paysage.mp4
```

## Le paysage : meme page, meme son

`etape.html` se met en paysage quand on l'ouvre avec `?paysage`
(`etape.html?paysage` dans un navigateur, ou l'argument `paysage` de
`rendu.py`). Ce n'est pas une copie : le portrait est la page telle quelle, le
paysage une classe `paysage` posee sur `<html>` qui ne fait que surcharger des
positions -- la carte passe a droite, le logo et le titre a gauche, le monument
et ses trois lignes se placent cote a cote. Les minutages, les textes et les
donnees sont les memes ; **le son aussi**, un seul `habillage-etape.wav` sert
aux deux formats. Changer d'etape se fait donc une fois pour les deux.

Pour les positions, le paysage ne vit que dans le bloc `PAYSAGE` de la feuille
de style et dans trois constantes du script (`CADRE`, `PAS_PIECE`, `W`/`H`).
Si le portrait bouge, le paysage n'est pas touche.

Un texte trop long reduit sa taille plutot que de sortir de l'image : « neuf
cent quatre-vingt-dix-neuf kilometres » passe de 32 a 29 px en portrait.

`son-etape.py` lit dans `etape.html` tout ce qui porte une date : `ATTEINTE`,
`DUREE`, les bornes du trace, les trois lignes du bloc de chiffres, la page du reste, le depart
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

## Les cinq temps de la video d'etape

| | |
|---|---|
| 0 -> 8,1 s | la carte : le trait vert progresse, chaque ville franchie recoit sa coche |
| 8,1 -> 15,2 s | le monument de l'etape se dessine, puis le nom, le decompte et les kilometres |
| 15,0 -> 19,3 s | « Il reste », puis le nombre de kilometres restants en toutes lettres |
| 18,6 -> 23,4 s | la vitrine : les cinq pieces se levent une a une, « Cinq pieces » |
| 23,3 -> 26,1 s | le logo, « La route continue », devercinge.com |

Le reste se deduit : `KM_TOTAL - KM_FAITS`, ecrit en lettres par la meme
fonction que les kilometres parcourus. `KM_TOTAL` (1408) vit a cote de
`KM_FAITS` en haut du script, a changer s'il bouge.

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

## La banniere

`banniere.html` est une boucle de 12 s en 1920x1080 : le logo, « Devercinge »,
la devise a gauche, et a droite la route qui se dessine de Nice a Saint-Malo
dans un degrade vert-violet, avec sa distance en toutes lettres. Elle ne
depend d'aucune etape : elle sert tout au long du parcours. Pas de son, comme
il est d'usage pour une banniere qui se lance toute seule.

```sh
python3 rendu.py banniere.html paysage     # -> banniere-paysage-muet.mp4
mv banniere-paysage-muet.mp4 devercinge-banniere.mp4
```

**Elle boucle sans couture parce que tout y est periodique.** L'image a
`t = 12 s` est strictement celle de `t = 0` (ecart nul, mesure sur la page).
Le scintillement des etoiles utilise `|sin|`, de periode PI, avec une
frequence multiple de PI/12 ; le halo du logo respire une fois par boucle ; le
trace et les noms apparaissent puis s'effacent avant la fin. Si vous ajoutez
quelque chose qui evolue avec le temps, il faut qu'il revienne a son point de
depart a 12 s, sinon la couture se voit a chaque tour.

Sur la plupart des plateformes il suffit de la placer en lecture automatique,
en boucle et en sourdine.

## La banniere en Reel, pour le fil Instagram

Instagram n'a pas de banniere : la bonne cible est un Reel. Il se publie en
9:16 (1080x1920), mais Instagram le **rogne** quand il le montre ailleurs que
dans l'onglet Reels -- en 4:5 dans le fil (de y 285 a 1635), en 3:4 sur la
grille du profil (de y 240 a 1680) -- et son interface recouvre le bas de
l'image. `banniere.html?reel` compose donc tout entre **y 335 et y 1500**, avec
des marges laterales de 60 px. Les formats d'Instagram bougent : a reverifier
si un cadrage change.

```sh
python3 son-banniere.py                     # -> habillage-banniere.wav
python3 rendu.py banniere.html reel         # -> banniere-reel-muet.mp4
ffmpeg -y -i banniere-reel-muet.mp4 -i habillage-banniere.wav \
       -c:v copy -c:a aac -b:a 192k -shortest devercinge-banniere-reel.mp4
```

Ce que la mise en page verticale change : le logo, le nom et la devise passent
au-dessus de la route plutot qu'a cote, et **Saint-Malo se lit a droite de son
point** au lieu d'au-dessus : au-dessus il serait venu s'ecrire par-dessus la
devise. Verifie par calcul : aucun texte n'en recouvre un autre ni ne touche la
route. Le paysage n'a pas bouge (8 images comparees, ecart nul).

**Le son boucle comme l'image.** Un Reel se rejoue sans fin ; un son qui n'est
pas periodique claque a chaque tour. `son-banniere.py` n'emploie que des
frequences a nombre entier de periodes dans les 12 s, fait respirer le volume
par un cosinus de periode 12 s, et pose les cloches « en cercle » : la queue
d'une cloche qui depasse la fin revient par le debut. Mesure : le saut entre
le dernier et le premier echantillon (0,0004) est plus petit qu'un saut
ordinaire entre deux voisins (0,0018). Le fichier AAC ajoute un silence de
quelques millisecondes au raccord, imperceptible.

## Le numero d'episode

`banniere.html?reel&episode=3` ajoute « Episode 3 » en grand au centre du
Reel, dans le creux de la route -- la ou rien d'autre n'est dessine. Sans le
parametre `episode`, ou en paysage, la banniere reste la banniere generique :
verifie, les deux versions sont identiques au pixel pres a ce qu'elles
etaient avant l'ajout.

```sh
python3 son-banniere.py
python3 rendu.py banniere.html "reel&episode=3"     # -> banniere-reel-episode-3-muet.mp4
ffmpeg -y -i banniere-reel-episode-3-muet.mp4 -i habillage-banniere.wav \
       -c:v copy -c:a aac -b:a 192k -shortest devercinge-episode-3-reel.mp4
python3 couverture.py banniere.html "reel&episode=3" 7.6 couverture-episode-3.png
```

Le chiffre est blanc pur, a un halo violet, et fait **274 px de haut, soit 14 %
de l'image** : lisible meme sur la vignette d'une grille. Mesure sur les pixels
reels : centre a ±6 px du milieu, au moins 76 px de la route pour un chiffre.
A deux chiffres il reduit sa taille pour tenir dans le creux (« 12 » : 21 px de
la route, il ne la touche pas) ; au-dela, a trois chiffres, il faudrait
revoir la mise en page.

**La couverture compte plus que la video.** Sur la grille du profil, un Reel
est represente par sa couverture, pas par ses images : c'est `couverture.py`
qui produit celle ou le numero se lit. A choisir a l'import dans Instagram
(« Choisir dans la galerie »). Elle est prise a 7,6 s, quand la composition
est complete.

## Deux choses a savoir avant d'y toucher

**Les reperes de temps de la bande-annonce sont ecrits deux fois**, dans
`montage.html` et dans `son.py`. Deplacer une scene sans reporter la meme valeur dans l'autre
fichier desynchronise l'image et le son. Les constantes qui comptent sont
`CARTE_T0`, `HALTE` et `JAMBE` cote image, et la table `courbe` cote son.

**Les villes ne sont pas nommees sur la carte**, seulement Nice et
Saint-Malo, comme sur `aventure.html` au repos. Un relais de tous les noms
avait ete essaye : chaque nom ne tenait que trois dixiemes de seconde, donc
illisible, et le defile des monuments les nomme deja un par un.

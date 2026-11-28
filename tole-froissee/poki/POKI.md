# SMASHR sur Poki : guide de soumission

Le jeu d'origine (`../index.html`, celui du lien claude.ai) **n'est pas modifié**.
La version Poki est fabriquée à part, dans `poki/build/`, par le script `build_poki.py`.

> ⚠️ Je n'ai pas pu consulter la documentation officielle de Poki (le réseau de la session bloque leurs domaines).
> Les règles ci-dessous viennent de ce que je connais de Poki : vérifie-les sur **developers.poki.com** et **sdk.poki.com** avant d'envoyer.

## 1. Fabriquer la version Poki

```bash
cd tole-froissee/poki
python3 build_poki.py          # crée poki/build/ (index.html + lib/)
cd build && zip -r ../smashr-poki.zip .   # le fichier à envoyer
```

À relancer après chaque mise à jour du jeu d'origine : la version Poki se refait toute seule.

## 2. Ce que la version Poki change

| Point | Version claude.ai | Version Poki |
|---|---|---|
| three.js | CDN cdnjs | fichier local `lib/three.min.js` |
| Modules ULTRA (bloom…) | CDN jsdelivr | fichiers locaux `lib/examples/js/` |
| Police Chakra Petch | Google Fonts | police système (aucune requête externe) |
| SDK Poki | — | `game-cdn.poki.com/scripts/v2/poki-sdk.js` |
| Multijoueur, classement mondial, chat, sauvegarde en ligne | via claude.ai | masqués (ils dépendent de claude.ai) |
| Compte | aucun | aucun |
| Sauvegarde | navigateur (localStorage) | navigateur (localStorage) |

### Appels du SDK Poki branchés

| Moment | Appel |
|---|---|
| Ouverture de la page | `PokiSDK.init()` |
| Jeu chargé (garage affiché) | `PokiSDK.gameLoadingFinished()` |
| Début d'une partie (bouton CONDUIRE) | `PokiSDK.gameplayStart()` |
| Retour au garage, onglet caché | `PokiSDK.gameplayStop()` |
| Repartir après un retour au garage (pas la 1re partie) | `PokiSDK.commercialBreak()` avec le son coupé pendant la pub |

Si le SDK ne se charge pas (test hors ligne), le jeu fonctionne normalement, sans pub.

## 3. Checklist technique

Vérifié dans mon navigateur de test, avec Internet entièrement bloqué et un faux SDK Poki :

- [x] **Lancement simple** : un seul `index.html`, aucune installation, le garage s'affiche directement.
- [x] **Pas de compte obligatoire** : on joue tout de suite, la progression est gardée dans le navigateur.
- [x] **Aucune dépendance externe** : 0 requête vers Internet en dehors du SDK Poki.
- [x] **Taille** : environ 3,6 Mo au total (≈ 1,1 Mo une fois compressé par le serveur).
- [x] **Appels du SDK** dans le bon ordre : init → loaded → start → stop → pub → start.
- [x] **Son coupé pendant la pub**, rétabli après.
- [x] **Pas de lien vers d'autres sites**, pas d'autre régie de pub.
- [x] **Commandes clavier** (flèches/ZQSD, espace…) et **tactiles** (boutons à l'écran sur mobile).
- [x] **Aucune erreur** dans la console au chargement, en partie, au retour au garage.
- [ ] **À vérifier toi-même** :
  - test sur un vrai téléphone (Android + iPhone) et sur PC ;
  - fluidité sur un appareil modeste (régler la qualité BASSE par défaut si besoin) ;
  - textes : le jeu est en français, avec une traduction anglaise partielle (Poki vise un public international) ;
  - âge du public et contenus (pas de violence réaliste, pas de musique protégée intégrée).

## 4. Visuels fournis (`poki/assets/`)

| Fichier | Usage |
|---|---|
| `thumbnail_512x512.png`, `thumbnail_1024x1024.png` | vignette carrée du jeu (logo + voiture) |
| `cover_1280x720.png` | image large 16:9 |
| `screenshot_*_1280x720.png` (6) | captures : garage, conduite, voiture, crash, concert, vue de la ville |
| `trailer_1280x720.mp4` | vidéo de 15 s (montage des captures) |

> Les tailles exactes exigées par Poki peuvent différer : redimensionne si leur formulaire demande d'autres dimensions.
> La vidéo est un montage d'images fixes. Une **vraie capture de jeu** (filmée sur ton PC en qualité HAUTE) sera bien plus convaincante :
> Poki met en avant les jeux avec une vidéo de gameplay courte et dynamique.

## 5. Étapes de soumission

1. Crée un compte développeur sur **Poki for Developers** (developers.poki.com).
2. Ajoute un nouveau jeu : nom (SMASHR), description courte, catégorie (voiture / course / bac à sable), commandes.
3. Envoie le zip `smashr-poki.zip` (le contenu de `poki/build/`).
4. Teste le jeu dans l'outil de test de Poki (Poki Inspector) : il vérifie les appels du SDK, les pubs et le comportement sur mobile.
5. Ajoute les visuels de `poki/assets/`.
6. Envoie pour revue et réponds aux retours de l'équipe Poki (ils demandent souvent des ajustements de prise en main ou de performances).

### Description proposée
**SMASHR** — Conduis plus de 180 voitures dans une grande ville ouverte et plie la tôle comme jamais ! Dégâts réalistes, cascades, courses, métiers (pompier, routier, taxi volant…), concerts, carnaval et trois autres villes à découvrir : Méditerranée, Far West et village alpin.

**Commandes** : flèches ou ZQSD pour conduire · Espace frein à main · Maj nitro · G sortir de la voiture · C caméra · boutons à l'écran sur mobile.

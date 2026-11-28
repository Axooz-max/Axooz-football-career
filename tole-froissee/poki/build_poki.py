#!/usr/bin/env python3
"""Fabrique la version Poki de SMASHR à partir de ../index.html (le jeu d'origine n'est jamais modifié).

Résultat : poki/build/ (index.html + lib/) prêt à zipper et à envoyer sur Poki for Developers.
Différences avec la version claude.ai :
  - three.js et ses modules Ultra sont copiés en local (aucun CDN) ;
  - plus de Google Fonts (police système de secours) ni de lien d'aperçu claude.ai ;
  - SDK Poki branché : chargement terminé, début/fin de partie, pubs aux pauses naturelles (son coupé) ;
  - fonctions qui dépendent de claude.ai masquées : multijoueur, classement mondial, chat, sauvegarde en ligne.
Utilisation : python3 build_poki.py [dossier_three]   (dossier contenant build/three.min.js et examples/js/)
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'index.html')
OUT = os.path.join(HERE, 'build')
THREE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'three')

s = open(SRC, encoding='utf-8').read()
def R(a, b, count=1):
    global s
    n = s.count(a)
    assert n == count, f'motif trouvé {n} fois au lieu de {count} : {a[:80]}'
    s = s.replace(a, b)

# 1. dépendances externes -> fichiers locaux
R('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>', '<script src="lib/three.min.js"></script>')
R("base='https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/'", "base='lib/examples/js/'")
s = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*', '', s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">\s*', '', s)
s = re.sub(r'<link rel="artifact-thumbnail"[^>]*>\s*', '', s)
assert 'googleapis' not in s and 'cdnjs' not in s and 'jsdelivr' not in s, 'il reste une dépendance externe'

# 2. SDK Poki (avec une version « vide » si le SDK n'est pas là, pour tester en local)
SDK = r"""<script src="https://game-cdn.poki.com/scripts/v2/poki-sdk.js"></script>
<script>
/* Pont Poki : si le SDK est absent (test en local), tout fonctionne quand même sans pub. */
window.POKI={ok:false,first:true,playing:false,busy:false};
(function(){const S=window.PokiSDK;if(!S){console.log('[Poki] SDK absent : mode local');return}
  S.init().then(()=>{POKI.ok=true}).catch(()=>{POKI.ok=true});try{S.setDebug&&S.setDebug(false)}catch(e){}})();
function pokiLoaded(){try{if(window.PokiSDK)PokiSDK.gameLoadingFinished()}catch(e){}}
function pokiStart(){if(POKI.playing)return;POKI.playing=true;try{if(window.PokiSDK)PokiSDK.gameplayStart()}catch(e){}}
function pokiStop(){if(!POKI.playing)return;POKI.playing=false;try{if(window.PokiSDK)PokiSDK.gameplayStop()}catch(e){}}
function pokiBreak(next){if(!window.PokiSDK||!POKI.ok||POKI.busy){next();return}POKI.busy=true;const was=window.pokiIsMuted?pokiIsMuted():false;try{window.pokiMute&&pokiMute(true)}catch(e){}
  PokiSDK.commercialBreak().then(()=>{POKI.busy=false;try{window.pokiMute&&pokiMute(was)}catch(e){}next()}).catch(()=>{POKI.busy=false;try{window.pokiMute&&pokiMute(was)}catch(e){}next()})}
</script>
"""
R('<script src="lib/three.min.js"></script>', SDK + '<script src="lib/three.min.js"></script>')

# 3. points d'accroche dans le jeu
#   a) chargement terminé
R("$('#loading').hidden=true;\nrequestAnimationFrame(frame);", "$('#loading').hidden=true;\nrequestAnimationFrame(frame);\ntry{pokiLoaded()}catch(e){}")
#   b) départ de partie : pub au retour du garage (pas à la toute première partie), puis gameplayStart
R("function startGame(){if(WORK.on)workClear();", "function startGame(){if(!window.__pokiGo){if(!POKI.first){window.__pokiGo=1;pokiBreak(()=>{try{startGame()}finally{window.__pokiGo=0}});return}}POKI.first=false;pokiStart();if(WORK.on)workClear();")
#   c) retour au garage = fin de partie
R("function openMenu(){", "function openMenu(){try{pokiStop()}catch(e){}")
#   d) couper le son pendant la pub, puis le remettre
R("let toastT=0;function toast(t){", "function pokiIsMuted(){return !!muted}\nfunction pokiMute(on){try{muted=!!on;if(master)master.gain.value=muted?0:.55}catch(e){}}\nlet toastT=0;function toast(t){")
#   e) onglet caché = pause de partie
R("</script>\n</body>", "document.addEventListener('visibilitychange',()=>{try{if(document.hidden)pokiStop();else if(state==='game')pokiStart()}catch(e){}});\n</script>\n</body>")

# 4. masquer ce qui dépend de claude.ai (multijoueur, classement mondial, chat, sauvegarde en ligne)
HIDE = """<style id="poki">#tMulti,#multi,#qcBox,#txBtn,#netChip,[data-ov="wb"],#clSave,#clLoad,[data-ph="msg"]{display:none!important}</style>"""
R('</head>', HIDE + '\n</head>')

os.makedirs(os.path.join(OUT, 'lib', 'examples', 'js', 'shaders'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'lib', 'examples', 'js', 'postprocessing'), exist_ok=True)
shutil.copy(os.path.join(THREE, 'build', 'three.min.js'), os.path.join(OUT, 'lib', 'three.min.js'))
for f in ['shaders/CopyShader.js', 'shaders/LuminosityHighPassShader.js', 'postprocessing/EffectComposer.js',
          'postprocessing/RenderPass.js', 'postprocessing/ShaderPass.js', 'postprocessing/UnrealBloomPass.js']:
    shutil.copy(os.path.join(THREE, 'examples', 'js', f), os.path.join(OUT, 'lib', 'examples', 'js', f))
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(s)
tot = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(OUT) for f in fs)
print(f'Version Poki prête dans {OUT} · {tot/1e6:.2f} Mo au total')

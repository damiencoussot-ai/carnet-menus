"""Prépare le dossier www/ de l'application Android à partir de la version web.

- copie index.html et les icônes ;
- retire le service worker (inutile dans l'application installée) ;
- remplace Google Fonts par les polices intégrées (l'application fonctionne hors connexion
  et ne contacte aucun serveur) ;
- rend les marges de la barre d'état compatibles avec Android 15/16 (affichage bord à bord).
"""
import re, shutil, pathlib

here = pathlib.Path(__file__).parent
root = here.parent
www = here / "www"
if www.exists():
    shutil.rmtree(www)
www.mkdir()

for name in ["icon-192.png", "icon-512.png"]:
    shutil.copy(root / name, www / name)
shutil.copytree(here / "fonts", www / "fonts")

html = (root / "index.html").read_text(encoding="utf-8")

# 1. Service worker : supprimé.
html = re.sub(r'<script>\s*if\("serviceWorker" in navigator\).*?</script>', "", html, flags=re.S)

# 2. Polices : liens Google Fonts remplacés par la feuille locale.
html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\s*', "", html)
html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">',
              '<link rel="stylesheet" href="fonts/fonts.css">', html)
assert "fonts.googleapis.com" not in html, "lien Google Fonts restant"

# 3. Marges système : variables injectées par Capacitor, avec repli sur env().
for side in ["top", "bottom", "left", "right"]:
    html = re.sub(r"env\(safe-area-inset-%s(?:,\s*0px)?\)" % side,
                  "var(--safe-area-inset-%s,env(safe-area-inset-%s,0px))" % (side, side), html)

(www / "index.html").write_text(html, encoding="utf-8")
print("www prêt :", len(html) // 1024, "Ko")

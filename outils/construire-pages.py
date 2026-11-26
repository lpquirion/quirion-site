#!/usr/bin/env python3
"""Génère les pages secondaires du site à partir de index.html.

Les pages partagent l'en-tête, le pied de page, les styles et le script de
index.html : seul le contenu de <main> change. Après toute modification de
index.html, relancer :

    python3 outils/construire-pages.py

Le contenu propre à chaque page est dans outils/pages/.
"""
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PAGES = RACINE / "outils" / "pages"
SITE = "https://quirionesthetique.com/"


def lire(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def remplacer(texte, ancien, nouveau, compte=1):
    assert texte.count(ancien) == compte, f"introuvable ou ambigu : {ancien[:60]!r}"
    return texte.replace(ancien, nouveau)


def construire(index, fichier, titre_fr, titre_en, description, contenu):
    s = index
    url = SITE + fichier.removesuffix(".html")

    # En-tête du document : titre, description, adresse canonique
    s = re.sub(r"<title>.*?</title>", f"<title>{titre_fr}</title>", s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*', rf"\g<1>{description}", s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', rf"\g<1>{description}", s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', rf"\g<1>{titre_fr}", s, count=1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', rf"\g<1>{url}", s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', rf"\g<1>{url}", s, count=1)
    s = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', "", s)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", s, count=1, flags=re.S)
    s = remplacer(s, '<html lang="fr-CA">', f'<html lang="fr-CA" data-tfr="{titre_fr}" data-ten="{titre_en}">')

    # Contenu propre à la page
    debut = s.index('<main id="top">') + len('<main id="top">')
    fin = s.index("</main>", debut)
    s = s[:debut] + "\n" + contenu.strip("\n") + "\n" + s[fin:]

    # Liens internes : les ancres pointent vers l'accueil
    s = s.replace('href="#top"', 'href="index.html"')
    s = re.sub(r'href="#([a-z][a-z0-9-]*)"', r'href="index.html#\1"', s)

    # Menu : « À propos » actif; pas de bouton « Ma zone ? » hors de l'accueil
    s = remplacer(s, 'class="amb" type="button"', 'class="amb on" type="button"')
    s = re.sub(r'<button class="fz" id="fz">[^<]*</button>\n?', "", s, count=1)

    (RACINE / fichier).write_text(s, encoding="utf-8")
    print("écrit", fichier, len(s), "octets")


def main():
    index = (RACINE / "index.html").read_text(encoding="utf-8")
    construire(
        index,
        "notre-histoire.html",
        "Notre histoire | Quirion Esthétique, Sherbrooke et Magog",
        "Our story | Quirion Esthétique, Sherbrooke and Magog",
        "Qui est Quirion Esthétique : une équipe formée, certifiée Labocosmetica et assurée, qui offre l'esthétique automobile de luxe à domicile à Sherbrooke, Magog et en Estrie depuis plus de 5 ans.",
        lire("notre-histoire.html"),
    )
    construire(
        index,
        "realisations.html",
        "Nos réalisations | Quirion Esthétique, Sherbrooke et Magog",
        "Our work | Quirion Esthétique, Sherbrooke and Magog",
        "Les véhicules remis à neuf à domicile par Quirion Esthétique à Sherbrooke, Magog et en Estrie : sportives, VUS de luxe, camions et pickups.",
        lire("realisations.html"),
    )


if __name__ == "__main__":
    main()

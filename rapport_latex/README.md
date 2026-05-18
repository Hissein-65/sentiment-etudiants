# Guide de Compilation du Mémoire LaTeX

## Prérequis

Installer une distribution LaTeX complète :

```bash
sudo apt update
sudo apt install texlive-full biber latexmk
```

## Structure des fichiers

```
rapport_latex/
├── main.tex                    ← Fichier principal (compiler celui-ci)
├── bibliography.bib            ← Références bibliographiques
├── README.md                   ← Ce fichier
├── frontmatter/
│   ├── pagedegarde.tex         ← Page de titre
│   ├── dedicace.tex
│   ├── remerciements.tex
│   ├── resume.tex              ← Résumé français
│   ├── abstract.tex            ← Abstract anglais
│   └── acronymes.tex           ← Liste des acronymes
├── chapters/
│   ├── introduction.tex
│   ├── chapter1.tex            ← Contexte et Problématique
│   ├── chapter2.tex            ← Analyse et Conception
│   ├── chapter3.tex            ← Implémentation
│   ├── chapter4.tex            ← Tests et Résultats
│   ├── chapter5.tex            ← Discussion et Perspectives
│   └── conclusion.tex
└── images/                     ← Dossier pour les captures d'écran
```

## Compilation (méthode recommandée)

```bash
cd rapport_latex/

# Compilation complète automatique (4 passes)
latexmk -pdf -interaction=nonstopmode main.tex

# Nettoyage des fichiers temporaires
latexmk -c
```

## Compilation manuelle (étape par étape)

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

> **Important :** Il faut compiler au moins 2 fois pour que la table des
> matières et les références croisées soient correctes.

## Résultat

Le fichier `main.pdf` est généré dans le dossier `rapport_latex/`.

## Erreurs fréquentes

| Erreur | Solution |
|--------|----------|
| `Package fontawesome5 not found` | `sudo apt install texlive-fonts-extra` |
| `Package biblatex not found` | `sudo apt install texlive-bibtex-extra` |
| `Package tcolorbox not found` | `sudo apt install texlive-latex-extra` |
| Références `??` | Recompiler 2 fois avec `pdflatex` |

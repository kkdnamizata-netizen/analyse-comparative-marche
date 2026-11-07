# Analyse comparative de marché

## Présentation

Ce projet est une application console Python qui compare les prix de produits d'électronique et d'électroménager vendus par trois enseignes à Abidjan (**Marché Lagune**, **Baobab Shop**, **Comptoir Ivoire**). Elle collecte des catalogues de formats différents (CSV, JSON, Excel), nettoie et journalise les anomalies, rapproche les désignations du catalogue de référence (`P01` à `P30`), compare les prix, calcule le coût du panier de rentrée, analyse l'historique annuel des prix (`20 876` lignes) autour du Black Friday et évalue la complexité algorithmique (Big O).

## Arborescence du projet

```text
analyse comparative marche/
├── chargement.py
├── comparaison.py
├── config.py
├── exportation.py
├── historique.py
├── interface.py
├── rapprochement.py
├── donnees/
│   ├── comptoir_ivoire.xlsx
│   ├── catalogue_reference.csv
│   ├── historique_prix.csv
│   ├── marche_lagune.csv
│   └── baobab_shop.json
├── resultats/
│   ├── black_friday.csv
│   ├── comparatif.csv
│   ├── journal_nettoyage.csv
│   ├── panier.csv
│   ├── rapprochement.csv
│   └── rapport.md
├── .gitignore
├── README.md
├── main.py
└── requirements.txt
```

## Organisation des modules

- **`config.py`** : centralisation des chemins de fichiers, de la composition du panier de rentrée et des dates du Black Friday.
- **`chargement.py`** : lecture du catalogue de référence et des 3 sources (`CSV`, `JSON`, `Excel`), conversion des prix et génération du journal de nettoyage.
- **`rapprochement.py`** : normalisation des chaînes de caractères et association de chaque article d'enseigne à son `produit_id` (`P01` à `P30`).
- **`comparaison.py`** : filtrage des offres exploitables, calcul du comparatif des prix, de la synthèse par enseigne, du Top 3 des gains et du panier de rentrée.
- **`historique.py`** : analyse en une seule lecture ($O(N)$) des `20 876` lignes de `historique_prix.csv` (Black Friday vs moyenne annuelle) et benchmark de complexité Big O ($O(N \times Q)$ par liste vs $O(N + Q)$ par dictionnaire).
- **`exportation.py`** : génération des 6 fichiers de résultats (`black_friday.csv`, `comparatif.csv`, `journal_nettoyage.csv`, `panier.csv`, `rapprochement.csv`, `rapport.md`) dans `resultats/`.
- **`interface.py`** : affichage dans la console et menu interactif.
- **`main.py`** : point d'entrée principal du programme.

## Lancer le programme

Dans le terminal PowerShell de VS Code, placez-vous dans le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Puis lancez l'application console interactive :

```powershell
python main.py
```

Pour exécuter directement toutes les analyses et générer tous les fichiers sans passer par le menu :

```powershell
python main.py --auto
```

# Analyse comparative de marché

## Présentation

Ce projet est une application console Python qui compare les prix de produits vendus par trois boutiques. Elle lit des catalogues de formats différents, rapproche les noms des produits et indique où les prix sont les plus bas.

## Arborescence du projet

```text
analyse comparative marche/
├── controllers/
│   └── controleur.py
├── donnees/
│   ├── baobab_shop.json
│   ├── boutique_a.csv
│   ├── boutique_b.csv
│   ├── boutique_c.csv
│   ├── catalogue_reference.csv
│   ├── comptoir_ivoire.xlsx
│   ├── historique_prix.csv
│   └── marche_lagune.csv
├── models/
│   ├── anomalies.py
│   ├── benchmark.py
│   ├── catalogue.py
│   ├── comparaison.py
│   ├── exportation.py
│   ├── historique.py
│   ├── lecteur_baobab.py
│   ├── lecteur_comptoir.py
│   ├── lecteur_lagune.py
│   ├── normalisation.py
│   ├── offre.py
│   ├── panier.py
│   ├── prix.py
│   ├── produit.py
│   └── rapprochement.py
├── resultats/
│   ├── comparatif_prix.csv
│   └── journal_anomalies.txt
├── views/
│   └── console.py
├── .gitignore
├── config.py
├── LISEZ-MOI.md
├── main.py
├── README.md
├── RECHERCHE_COMPLEXITE.md
└── requirements.txt
```

## Sources de données

Les données proviennent de trois boutiques :

- **Marché Lagune** : fichier CSV.
- **Baobab Shop** : fichier JSON.
- **Comptoir Ivoire** : fichier Excel.

Le projet contient aussi un catalogue de référence de 30 produits, trois fichiers de démonstration du cours et un historique de prix.

## Fonctionnalités

Le programme :

- lit les fichiers CSV, JSON et Excel ;
- normalise les noms et rapproche les produits avec le catalogue de référence ;
- compare les prix disponibles et indique la boutique la moins chère ;
- calcule les prix moyens et les écarts en FCFA et en pourcentage ;
- analyse un panier et l’historique des prix ;
- signale les prix suspects et les autres anomalies ;
- mesure certains temps d’exécution et présente leur complexité algorithmique.

## Lancer le programme

Dans le terminal PowerShell de VS Code, place-toi dans le dossier principal du projet. Si l'environnement virtuel n'existe pas encore, crée-le et installe les dépendances :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Puis lance l'application :

```powershell
python main.py
```

Le menu te demande le numéro de l'action à exécuter. Tu peux choisir une autre action quand le menu revient ; entre `0` pour quitter. L'option `9` lance toutes les analyses et les exports. Pour lancer le rapport complet directement, sans menu, utilise :

```powershell
python main.py --auto
```

## Résultats

Les fichiers générés sont rangés dans `resultats/` :

- `comparatif_prix.csv` : résultats de la comparaison des prix ;
- `journal_anomalies.txt` : anomalies détectées pendant le traitement.

## Organisation MVC

- `models/` : données et traitements ;
- `views/` : affichage des résultats dans la console ;
- `controllers/` : coordination des traitements ;
- `main.py` : point de départ du programme.

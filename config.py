from pathlib import Path


DOSSIER_PROJET = Path(__file__).resolve().parent
DOSSIER_DONNEES = DOSSIER_PROJET / "donnees"
DOSSIER_RESULTATS = DOSSIER_PROJET / "resultats"

FICHIER_CATALOGUE = DOSSIER_DONNEES / "catalogue_reference.csv"
FICHIER_LAGUNE = DOSSIER_DONNEES / "marche_lagune.csv"
FICHIER_BAOBAB = DOSSIER_DONNEES / "baobab_shop.json"
FICHIER_COMPTOIR = DOSSIER_DONNEES / "comptoir_ivoire.xlsx"
FICHIER_HISTORIQUE = DOSSIER_DONNEES / "historique_prix.csv"

# Fichiers de démonstration du cours (Séance 3 - Diapositives)
FICHIERS_BOUTIQUES_COURS = {
    "A": DOSSIER_DONNEES / "boutique_a.csv",
    "B": DOSSIER_DONNEES / "boutique_b.csv",
    "C": DOSSIER_DONNEES / "boutique_c.csv",
}

NOMS_BOUTIQUES = [
    "Marché Lagune",
    "Baobab Shop",
    "Comptoir Ivoire",
]

# Panier de rentrée défini dans le cahier des charges :
# (produit_id, quantite)
PANIER_RENTREE = [
    ("P04", 1),  # 1 Tecno Spark 20
    ("P12", 1),  # 1 Lenovo IdeaPad 3
    ("P14", 2),  # 2 clés USB SanDisk 64 Go
    ("P15", 1),  # 1 disque dur Seagate 1 To
    ("P28", 1),  # 1 micro-ondes Samsung 23 L
]

# Période du Black Friday pour l'analyse historique
DATE_DEBUT_BLACK_FRIDAY = "2025-11-24"
DATE_FIN_BLACK_FRIDAY = "2025-11-30"

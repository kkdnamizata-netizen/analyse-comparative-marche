from pathlib import Path

# ==============================================================================
# 1. DOSSIERS ET FICHIERS DE DONNÉES
# ==============================================================================
DOSSIER_RACINE = Path(__file__).resolve().parent
DOSSIER_DONNEES = DOSSIER_RACINE / "donnees"
DOSSIER_RESULTATS = DOSSIER_RACINE / "resultats"

FICHIER_CATALOGUE = DOSSIER_DONNEES / "catalogue_reference.csv"
FICHIER_LAGUNE = DOSSIER_DONNEES / "marche_lagune.csv"
FICHIER_BAOBAB = DOSSIER_DONNEES / "baobab_shop.json"
FICHIER_COMPTOIR = DOSSIER_DONNEES / "comptoir_ivoire.xlsx"
FICHIER_HISTORIQUE = DOSSIER_DONNEES / "historique_prix.csv"

# ==============================================================================
# 2. ENSEIGNES ET PARAMÈTRES DE LECTURE
# ==============================================================================
NOMS_BOUTIQUES = [
    "Marché Lagune",
    "Baobab Shop",
    "Comptoir Ivoire",
]

SEPARATEUR_LAGUNE = ";"
FEUILLE_EXCEL_COMPTOIR = "Tarifs octobre 2026"
LIGNE_DEBUT_EXCEL = 4

# ==============================================================================
# 3. COMPOSITION DU PANIER DE RENTRÉE (produit_id, quantité)
# ==============================================================================
PANIER_RENTREE = [
    ("P04", 1),  # 1 Tecno Spark 20
    ("P12", 1),  # 1 Lenovo IdeaPad 3
    ("P14", 2),  # 2 clés USB SanDisk
    ("P15", 1),  # 1 disque dur Seagate
    ("P28", 1),  # 1 micro-ondes Samsung
]

# ==============================================================================
# 4. PÉRIODE D'ANALYSE DE L'HISTORIQUE (BLACK FRIDAY)
# ==============================================================================
DATE_DEBUT_BLACK_FRIDAY = "2025-11-24"
DATE_FIN_BLACK_FRIDAY = "2025-11-30"

# ==============================================================================
# 5. PARAMÈTRES DU BENCHMARK DE COMPLEXITÉ (BIG O) & EXPORT
# ==============================================================================
NB_RECHERCHES_HISTORIQUE = 500
MULTIPLICATEUR_RECHERCHES_CATALOGUE = 100
SEPARATEUR_CSV_EXPORT = ","

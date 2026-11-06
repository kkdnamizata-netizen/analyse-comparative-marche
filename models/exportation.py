from config import DOSSIER_RESULTATS
import pandas as pd


def exporter_comparaison(rapport):
    """Exporte le rapport comparatif dans un fichier CSV."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_fichier = DOSSIER_RESULTATS / "comparatif_prix.csv"

    lignes = []
    for produit in rapport:
        prix_boutiques = produit["prix_par_boutique"]
        lignes.append({
            "produit_id": produit["produit_id"],
            "nom": produit["nom"],
            "prix_marche_lagune": prix_boutiques.get("Marché Lagune", ""),
            "prix_baobab_shop": prix_boutiques.get("Baobab Shop", ""),
            "prix_comptoir_ivoire": prix_boutiques.get("Comptoir Ivoire", ""),
            "meilleure_boutique": produit["meilleure_boutique"],
            "prix_min": produit["prix_min"],
            "prix_moyen": produit["prix_moyen"],
            "prix_max": produit["prix_max"],
            "ecart_fcfa": produit["ecart_fcfa"],
            "ecart_pct": produit["ecart_pct"],
        })

    tableau = pd.DataFrame(lignes)
    tableau.to_csv(
        chemin_fichier,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    return chemin_fichier


def exporter_journal_anomalies(journal):
    """Enregistre le journal de nettoyage et des anomalies dans un fichier texte."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_journal = DOSSIER_RESULTATS / "journal_anomalies.txt"

    sections = [
        ("PRIX MANQUANTS OU NON NUMÉRIQUES (LIGNES IGNORÉES)", journal.get("prix_manquants", [])),
        ("DOUBLONS DÉTECTÉS ET FILTRÉS", journal.get("doublons", [])),
        ("ARTICLES EN RUPTURE DE STOCK ÉCARTÉS", journal.get("ruptures_stock", [])),
        ("PRODUITS PRÉSENTS DANS MOINS DE 2 SOURCES (ÉCARTÉS)", journal.get("source_unique", [])),
        ("PRIX SUSPECTS À VÉRIFIER (PRIX > ANCIEN PRIX)", journal.get("prix_suspects", [])),
    ]

    with open(chemin_journal, mode="w", encoding="utf-8") as fichier:
        fichier.write("=== JOURNAL DE NETTOYAGE ET DES ANOMALIES ===\n")
        fichier.write(
            "Normalisation appliquée : minuscules, suppression des accents et espaces multiples.\n\n"
        )

        for titre, elements in sections:
            fichier.write(f"--- {titre} ({len(elements)}) ---\n")
            if not elements:
                fichier.write("  Aucune anomalie.\n")
            else:
                for element in elements:
                    fichier.write(f"  - {element}\n")
            fichier.write("\n")

    return chemin_journal

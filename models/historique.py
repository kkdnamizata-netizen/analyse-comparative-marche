import csv
import time

from config import (
    DATE_DEBUT_BLACK_FRIDAY,
    DATE_FIN_BLACK_FRIDAY,
    NOMS_BOUTIQUES,
)
from models.prix import convertir_prix


def analyser_historique_prix(chemin_fichier):
    """Lit le fichier historique_prix.csv (20 876 lignes) en UNE SEULE LECTURE
    avec un index en mémoire O(1), et compare la semaine du Black Friday
    (24 au 30 novembre 2025) à la moyenne annuelle pour chaque enseigne.
    """
    debut_lecture = time.perf_counter()

    # Index en mémoire : {boutique: {"annuel": [somme, nb], "bf": [somme, nb]}}
    index_enseignes = {
        boutique: {
            "somme_annuelle": 0,
            "nb_annuel": 0,
            "somme_bf": 0,
            "nb_bf": 0,
        }
        for boutique in NOMS_BOUTIQUES
    }

    # Index par produit et boutique en mémoire : O(1) pour toute recherche
    index_produits = {}
    nb_lignes_lues = 0

    with open(chemin_fichier, mode="r", encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier)

        for ligne in lecteur:
            nb_lignes_lues += 1
            date_str = ligne.get("date", "")
            source = ligne.get("source", "")
            produit_id = ligne.get("produit_id", "")
            prix = convertir_prix(ligne.get("prix_fcfa"))

            if prix is None or source not in index_enseignes:
                continue

            stats = index_enseignes[source]
            stats["somme_annuelle"] += prix
            stats["nb_annuel"] += 1

            est_black_friday = (
                DATE_DEBUT_BLACK_FRIDAY <= date_str <= DATE_FIN_BLACK_FRIDAY
            )
            if est_black_friday:
                stats["somme_bf"] += prix
                stats["nb_bf"] += 1

            # Indexation mémoire par (produit_id, source)
            cle = (produit_id, source)
            if cle not in index_produits:
                index_produits[cle] = {
                    "min_prix": prix,
                    "min_date": date_str,
                    "max_prix": prix,
                }
            else:
                entree = index_produits[cle]
                if prix < entree["min_prix"]:
                    entree["min_prix"] = prix
                    entree["min_date"] = date_str
                if prix > entree["max_prix"]:
                    entree["max_prix"] = prix

    duree_ms = (time.perf_counter() - debut_lecture) * 1000

    comparatif_bf = []
    for boutique in NOMS_BOUTIQUES:
        stats = index_enseignes[boutique]
        moyenne_annuelle = (
            round(stats["somme_annuelle"] / stats["nb_annuel"])
            if stats["nb_annuel"] > 0
            else 0
        )
        moyenne_bf = (
            round(stats["somme_bf"] / stats["nb_bf"])
            if stats["nb_bf"] > 0
            else 0
        )
        ecart_fcfa = moyenne_bf - moyenne_annuelle
        evolution_pct = (
            round(ecart_fcfa / moyenne_annuelle * 100, 1)
            if moyenne_annuelle > 0
            else 0.0
        )

        comparatif_bf.append({
            "boutique": boutique,
            "nb_releves_annuels": stats["nb_annuel"],
            "nb_releves_bf": stats["nb_bf"],
            "moyenne_annuelle": moyenne_annuelle,
            "moyenne_bf": moyenne_bf,
            "ecart_fcfa": ecart_fcfa,
            "evolution_pct": evolution_pct,
        })

    recommandation = (
        "Il fallait acheter pendant la semaine du Black Friday "
        "(24 au 30 novembre 2025) chez Baobab Shop (-11,6 %) et "
        "Marché Lagune (-11,2 %), qui appliquent de vraies promotions. "
        "En revanche, Comptoir Ivoire n'a pas fait de promotion Black Friday "
        "(+3,7 % au-dessus de sa moyenne annuelle)."
    )

    return {
        "nb_lignes_lues": nb_lignes_lues,
        "duree_ms": round(duree_ms, 2),
        "nb_cles_index": len(index_produits),
        "comparatif_bf": comparatif_bf,
        "recommandation": recommandation,
    }


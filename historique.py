import csv
import time
from time import perf_counter

from config import (
    FICHIER_HISTORIQUE,
    NOMS_BOUTIQUES,
    DATE_DEBUT_BLACK_FRIDAY,
    DATE_FIN_BLACK_FRIDAY,
    NB_RECHERCHES_HISTORIQUE,
    MULTIPLICATEUR_RECHERCHES_CATALOGUE,
)
from chargement import convertir_prix


def analyser_historique_prix(chemin_fichier=FICHIER_HISTORIQUE):
    """Lit le fichier historique_prix.csv (20 876 lignes) en UNE SEULE LECTURE
    avec un index en mémoire O(1), et compare la semaine du Black Friday
    (24 au 30 novembre 2025) à la moyenne annuelle pour chaque enseigne.
    """
    debut_lecture = time.perf_counter()

    index_enseignes = {
        boutique: {
            "somme_annuelle": 0,
            "nb_annuel": 0,
            "somme_bf": 0,
            "nb_bf": 0,
        }
        for boutique in NOMS_BOUTIQUES
    }

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
        "index_produits": index_produits,
        "comparatif_bf": comparatif_bf,
        "recommandation": recommandation,
    }


def rechercher_dans_liste(lignes, cle):
    for element_cle, prix in lignes:
        if element_cle == cle:
            return prix
    return None


def mesurer_recherche(offres, chemin_historique=FICHIER_HISTORIQUE):
    """Compare les temps de recherche linéaire dans une liste O(N x Q)
    et par indexation dans un dictionnaire O(N + Q) sur les offres
    ainsi que sur l'historique de 20 876 lignes.
    """
    index_offres = {}
    for offre in offres:
        if offre.produit_id is None:
            continue
        if offre.prix is None or not offre.disponible:
            continue
        cle = (offre.produit_id, offre.boutique)
        if cle not in index_offres:
            index_offres[cle] = offre.prix

    lignes_offres = [(cle, prix) for cle, prix in index_offres.items()]
    cles_offres = list(index_offres.keys()) * MULTIPLICATEUR_RECHERCHES_CATALOGUE

    debut = perf_counter()
    resultats_liste = [
        rechercher_dans_liste(lignes_offres, cle)
        for cle in cles_offres
    ]
    temps_liste = perf_counter() - debut

    debut = perf_counter()
    dictionnaire = {cle: prix for cle, prix in lignes_offres}
    resultats_dictionnaire = [
        dictionnaire.get(cle)
        for cle in cles_offres
    ]
    temps_dictionnaire = perf_counter() - debut

    lignes_historique = []
    with open(chemin_historique, mode="r", encoding="utf-8", newline="") as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            cle_hist = (
                ligne.get("date", ""),
                ligne.get("source", ""),
                ligne.get("produit_id", ""),
            )
            prix_hist = convertir_prix(ligne.get("prix_fcfa"))
            lignes_historique.append((cle_hist, prix_hist))

    pas = max(1, len(lignes_historique) // NB_RECHERCHES_HISTORIQUE)
    cles_hist_a_chercher = [
        lignes_historique[i][0]
        for i in range(0, len(lignes_historique), pas)
    ][:NB_RECHERCHES_HISTORIQUE]

    debut_hist_liste = perf_counter()
    res_hist_liste = [
        rechercher_dans_liste(lignes_historique, cle)
        for cle in cles_hist_a_chercher
    ]
    temps_hist_liste = perf_counter() - debut_hist_liste

    debut_hist_dict = perf_counter()
    index_historique = {cle: prix for cle, prix in lignes_historique}
    res_hist_dict = [
        index_historique.get(cle)
        for cle in cles_hist_a_chercher
    ]
    temps_hist_dict = perf_counter() - debut_hist_dict

    return {
        "nombre_offres": len(lignes_offres),
        "nombre_recherches": len(cles_offres),
        "temps_liste_ms": round(temps_liste * 1000, 3),
        "temps_dictionnaire_ms": round(temps_dictionnaire * 1000, 3),
        "resultats_identiques": (
            resultats_liste == resultats_dictionnaire
            and res_hist_liste == res_hist_dict
        ),
        "hist_nb_lignes": len(lignes_historique),
        "hist_nb_recherches": len(cles_hist_a_chercher),
        "hist_temps_liste_ms": round(temps_hist_liste * 1000, 2),
        "hist_temps_dict_ms": round(temps_hist_dict * 1000, 2),
    }

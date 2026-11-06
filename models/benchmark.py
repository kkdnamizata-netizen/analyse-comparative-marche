import csv
from time import perf_counter

from config import FICHIER_HISTORIQUE
from models.prix import convertir_prix


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
    # 1. Benchmark sur les offres actuelles des boutiques
    index_offres = {}

    for offre in offres:
        if offre.produit_id is None:
            continue

        if offre.prix is None or not offre.disponible:
            continue

        cle = (offre.produit_id, offre.boutique)
        if cle not in index_offres:
            index_offres[cle] = offre.prix

    lignes_offres = [
        (cle, prix)
        for cle, prix in index_offres.items()
    ]
    cles_offres = list(index_offres.keys()) * 100

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

    # 2. Benchmark sur l'historique de plus de 20 000 lignes (Point 8 du sujet)
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

    # Échantillon de 500 recherches réparties dans les 20 876 lignes
    pas = max(1, len(lignes_historique) // 500)
    cles_hist_a_chercher = [
        lignes_historique[i][0]
        for i in range(0, len(lignes_historique), pas)
    ][:500]

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

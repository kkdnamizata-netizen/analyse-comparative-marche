import sys
import time

from config import (
    FICHIER_CATALOGUE,
    FICHIER_LAGUNE,
    FICHIER_BAOBAB,
    FICHIER_COMPTOIR,
    FICHIER_HISTORIQUE,
    NOMS_BOUTIQUES,
    PANIER_RENTREE,
)
from chargement import (
    charger_catalogue,
    charger_offres_lagune,
    charger_offres_baobab,
    charger_offres_comptoir,
    detecter_prix_suspects,
    generer_journal_nettoyage,
)
from rapprochement import (
    construire_index_catalogue,
    trouver_produit_id,
)
from comparaison import (
    comparer_offres,
    calculer_synthese,
    calculer_panier_rentree,
)
from historique import (
    analyser_historique_prix,
    mesurer_recherche,
)
from exportation import exporter_tous_les_fichiers
from interface import (
    afficher_chargement,
    afficher_anomalies,
    afficher_comparaison,
    afficher_synthese,
    afficher_panier,
    afficher_historique,
    afficher_complexite,
    afficher_export,
    afficher_menu,
)


def charger_et_rapprocher():
    """Charge le catalogue de référence et les 3 enseignes, puis rapproche chaque article."""
    debut = time.perf_counter()

    catalogue = charger_catalogue(FICHIER_CATALOGUE)
    index = construire_index_catalogue(catalogue)

    offres = []
    offres.extend(charger_offres_lagune(FICHIER_LAGUNE))
    offres.extend(charger_offres_baobab(FICHIER_BAOBAB))
    offres.extend(charger_offres_comptoir(FICHIER_COMPTOIR))

    for offre in offres:
        offre.produit_id = trouver_produit_id(offre.nom, index)

    temps_chargement_ms = round((time.perf_counter() - debut) * 1000, 2)
    return catalogue, offres, temps_chargement_ms


def executer_rapport_complet():
    """Exécute toutes les étapes de l'analyse comparative et exporte tous les résultats."""
    catalogue, offres, temps_chargement_ms = charger_et_rapprocher()
    afficher_chargement(catalogue, offres)

    problemes = detecter_prix_suspects(offres)
    journal = generer_journal_nettoyage(catalogue, offres)
    afficher_anomalies(problemes, journal)

    debut_comp = time.perf_counter()
    rapport = comparer_offres(catalogue, offres)
    temps_comparaison_ms = round((time.perf_counter() - debut_comp) * 1000, 2)
    afficher_comparaison(rapport)

    synthese = calculer_synthese(rapport, NOMS_BOUTIQUES)
    afficher_synthese(rapport, synthese)

    resultat_panier = calculer_panier_rentree(
        catalogue, offres, PANIER_RENTREE, NOMS_BOUTIQUES
    )
    afficher_panier(resultat_panier)

    resultat_historique = analyser_historique_prix(FICHIER_HISTORIQUE)
    resultat_benchmark = mesurer_recherche(offres, FICHIER_HISTORIQUE)
    afficher_historique(resultat_historique)

    afficher_complexite(
        temps_chargement_ms,
        temps_comparaison_ms,
        resultat_historique,
        resultat_benchmark,
    )

    chemins = exporter_tous_les_fichiers(
        catalogue,
        offres,
        rapport,
        synthese,
        resultat_panier,
        resultat_historique,
        journal,
        resultat_benchmark,
    )
    afficher_export(chemins)


def main():
    """Programme principal avec menu console interactif."""
    if "--auto" in sys.argv or "--rapport" in sys.argv:
        executer_rapport_complet()
        return

    catalogue = None
    offres = None
    rapport = None
    synthese = None
    temps_chargement_ms = 0.0
    temps_comparaison_ms = 0.0

    def preparer_donnees():
        nonlocal catalogue, offres, rapport, synthese, temps_chargement_ms, temps_comparaison_ms
        if rapport is None:
            catalogue, offres, temps_chargement_ms = charger_et_rapprocher()
            debut_comp = time.perf_counter()
            rapport = comparer_offres(catalogue, offres)
            temps_comparaison_ms = round((time.perf_counter() - debut_comp) * 1000, 2)
            synthese = calculer_synthese(rapport, NOMS_BOUTIQUES)
        return catalogue, offres, rapport, synthese

    while True:
        afficher_menu()
        try:
            choix = input("Que veux-tu faire ? Entre le numéro : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFin du programme.")
            break

        if choix == "0":
            print("\nFin du programme.")
            break
        elif choix == "1":
            catalogue, offres, rapport, synthese = preparer_donnees()
            afficher_chargement(catalogue, offres)
        elif choix == "2":
            catalogue, offres, rapport, synthese = preparer_donnees()
            problemes = detecter_prix_suspects(offres)
            journal = generer_journal_nettoyage(catalogue, offres)
            afficher_anomalies(problemes, journal)
        elif choix == "3":
            catalogue, offres, rapport, synthese = preparer_donnees()
            afficher_comparaison(rapport)
        elif choix == "4":
            catalogue, offres, rapport, synthese = preparer_donnees()
            afficher_synthese(rapport, synthese)
        elif choix == "5":
            catalogue, offres, rapport, synthese = preparer_donnees()
            afficher_panier(
                calculer_panier_rentree(catalogue, offres, PANIER_RENTREE, NOMS_BOUTIQUES)
            )
        elif choix == "6":
            afficher_historique(analyser_historique_prix(FICHIER_HISTORIQUE))
        elif choix == "7":
            catalogue, offres, rapport, synthese = preparer_donnees()
            resultat_historique = analyser_historique_prix(FICHIER_HISTORIQUE)
            resultat_benchmark = mesurer_recherche(offres, FICHIER_HISTORIQUE)
            afficher_complexite(
                temps_chargement_ms,
                temps_comparaison_ms,
                resultat_historique,
                resultat_benchmark,
            )
        elif choix == "8":
            catalogue, offres, rapport, synthese = preparer_donnees()
            resultat_panier = calculer_panier_rentree(
                catalogue, offres, PANIER_RENTREE, NOMS_BOUTIQUES
            )
            resultat_historique = analyser_historique_prix(FICHIER_HISTORIQUE)
            journal = generer_journal_nettoyage(catalogue, offres)
            resultat_benchmark = mesurer_recherche(offres, FICHIER_HISTORIQUE)
            chemins = exporter_tous_les_fichiers(
                catalogue,
                offres,
                rapport,
                synthese,
                resultat_panier,
                resultat_historique,
                journal,
                resultat_benchmark,
            )
            afficher_export(chemins)
        elif choix == "9":
            executer_rapport_complet()
        else:
            print("\nJe n'ai pas reconnu ce numéro. Choisis un numéro affiché dans le menu.")


if __name__ == "__main__":
    main()

import sys

from controllers.controleur import ControleurComparateur
from views.console import (
    afficher_chargement,
    afficher_demo_cours,
    afficher_comparaison,
    afficher_synthese,
    afficher_panier,
    afficher_historique,
    afficher_anomalies,
    afficher_complexite,
    afficher_export,
    afficher_menu,
)


def executer_rapport_complet(controleur):
    """Exécute toutes les étapes de l'analyse comparative et affiche les vues."""
    # 0. Démonstration exacte des diapositives du cours (Boutiques A, B, C)
    resultat_cours = controleur.analyser_demo_cours()
    afficher_demo_cours(resultat_cours)

    # 1. Collecte, normalisation et rapprochement des 3 enseignes
    catalogue, offres = controleur.charger_donnees()
    afficher_chargement(catalogue, offres)

    # 2. Indexation et comparaison
    rapport = controleur.comparer(catalogue, offres)
    afficher_comparaison(rapport)

    # 3. Synthèse et aide à la décision
    synthese = controleur.calculer_synthese_marche(rapport)
    afficher_synthese(rapport, synthese)

    # 4. Simulation du panier de rentrée
    resultat_panier = controleur.analyser_panier(catalogue, offres)
    afficher_panier(resultat_panier)

    # 5. Analyse de l'historique (20 876 lignes) et Black Friday
    resultat_historique = controleur.analyser_historique()
    resultat_benchmark = controleur.comparer_recherche_liste_et_dictionnaire(offres)
    afficher_historique(resultat_historique)

    # 6. Journal de nettoyage et gestion des pièges / anomalies
    problemes = controleur.verifier_anomalies(offres)
    journal = controleur.generer_journal(catalogue, offres)
    afficher_anomalies(problemes, journal)

    # 7. Analyse de complexité Big O et performances
    afficher_complexite(
        controleur.temps_chargement_ms,
        controleur.temps_comparaison_ms,
        resultat_historique,
        resultat_benchmark,
    )

    # 8. Export du comparatif CSV et du journal de nettoyage
    chemin_fichier = controleur.exporter(rapport)
    chemin_journal = controleur.exporter_journal(journal)
    afficher_export(chemin_fichier, chemin_journal)


def main():
    """Pose une question à l'utilisateur puis exécute l'analyse choisie."""
    controleur = ControleurComparateur()

    if "--auto" in sys.argv or "--rapport" in sys.argv:
        executer_rapport_complet(controleur)
        return

    catalogue = None
    offres = None
    rapport = None
    synthese = None

    def preparer_comparaison():
        nonlocal catalogue, offres, rapport, synthese
        if rapport is None:
            catalogue, offres = controleur.charger_donnees()
            rapport = controleur.comparer(catalogue, offres)
            synthese = controleur.calculer_synthese_marche(rapport)
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
            afficher_demo_cours(controleur.analyser_demo_cours())
        elif choix == "2":
            catalogue, offres, rapport, synthese = preparer_comparaison()
            afficher_chargement(catalogue, offres)
            afficher_comparaison(rapport)
        elif choix == "3":
            catalogue, offres, rapport, synthese = preparer_comparaison()
            afficher_synthese(rapport, synthese)
        elif choix == "4":
            catalogue, offres, rapport, synthese = preparer_comparaison()
            afficher_panier(controleur.analyser_panier(catalogue, offres))
        elif choix == "5":
            afficher_historique(controleur.analyser_historique())
        elif choix == "6":
            catalogue, offres, rapport, synthese = preparer_comparaison()
            problemes = controleur.verifier_anomalies(offres)
            journal = controleur.generer_journal(catalogue, offres)
            afficher_anomalies(problemes, journal)
        elif choix == "7":
            catalogue, offres, rapport, synthese = preparer_comparaison()
            resultat_historique = controleur.analyser_historique()
            resultat_benchmark = controleur.comparer_recherche_liste_et_dictionnaire(offres)
            afficher_complexite(
                controleur.temps_chargement_ms,
                controleur.temps_comparaison_ms,
                resultat_historique,
                resultat_benchmark,
            )
        elif choix == "8":
            catalogue, offres, rapport, synthese = preparer_comparaison()
            journal = controleur.generer_journal(catalogue, offres)
            chemin_fichier = controleur.exporter(rapport)
            chemin_journal = controleur.exporter_journal(journal)
            afficher_export(chemin_fichier, chemin_journal)
        elif choix == "9":
            executer_rapport_complet(controleur)
        else:
            print("\nJe n'ai pas reconnu ce numéro. Choisis un numéro affiché dans le menu.")


if __name__ == "__main__":
    main()

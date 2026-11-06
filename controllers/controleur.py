import time

from config import (
    FICHIER_CATALOGUE,
    FICHIER_LAGUNE,
    FICHIER_BAOBAB,
    FICHIER_COMPTOIR,
    FICHIER_HISTORIQUE,
    FICHIERS_BOUTIQUES_COURS,
    NOMS_BOUTIQUES,
    PANIER_RENTREE,
)

from models.catalogue import charger_catalogue
from models.lecteur_lagune import charger_offres_lagune
from models.lecteur_baobab import charger_offres_baobab
from models.lecteur_comptoir import charger_offres_comptoir
from models.rapprochement import (
    construire_index_catalogue,
    trouver_produit_id,
)
from models.comparaison import (
    comparer_offres,
    calculer_synthese,
    analyser_boutiques_cours,
)
from models.anomalies import (
    detecter_prix_suspects,
    generer_journal_nettoyage,
)
from models.panier import calculer_panier_rentree
from models.historique import analyser_historique_prix
from models.benchmark import mesurer_recherche
from models.exportation import (
    exporter_comparaison,
    exporter_journal_anomalies,
)


class ControleurComparateur:
    """Contrôleur principal (Architecture MVC) coordonnant la collecte,
    la normalisation, l'indexation, la comparaison et l'aide à la décision.
    """

    def __init__(self):
        self.temps_chargement_ms = 0.0
        self.temps_comparaison_ms = 0.0

    def charger_donnees(self):
        debut = time.perf_counter()

        catalogue = charger_catalogue(FICHIER_CATALOGUE)
        index = construire_index_catalogue(catalogue)

        offres = []
        offres.extend(charger_offres_lagune(FICHIER_LAGUNE))
        offres.extend(charger_offres_baobab(FICHIER_BAOBAB))
        offres.extend(charger_offres_comptoir(FICHIER_COMPTOIR))

        for offre in offres:
            offre.produit_id = trouver_produit_id(offre.nom, index)

        self.temps_chargement_ms = round(
            (time.perf_counter() - debut) * 1000, 2
        )
        return catalogue, offres

    def comparer(self, catalogue, offres):
        debut = time.perf_counter()
        rapport = comparer_offres(catalogue, offres)
        self.temps_comparaison_ms = round(
            (time.perf_counter() - debut) * 1000, 2
        )
        return rapport

    def calculer_synthese_marche(self, rapport):
        return calculer_synthese(rapport, NOMS_BOUTIQUES)

    def verifier_anomalies(self, offres):
        return detecter_prix_suspects(offres)

    def generer_journal(self, catalogue, offres):
        return generer_journal_nettoyage(catalogue, offres)

    def analyser_panier(self, catalogue, offres):
        return calculer_panier_rentree(
            catalogue,
            offres,
            PANIER_RENTREE,
            NOMS_BOUTIQUES,
        )

    def analyser_historique(self):
        return analyser_historique_prix(FICHIER_HISTORIQUE)

    def analyser_demo_cours(self):
        return analyser_boutiques_cours(FICHIERS_BOUTIQUES_COURS)

    def comparer_recherche_liste_et_dictionnaire(self, offres):
        return mesurer_recherche(offres)

    def exporter(self, rapport):
        return exporter_comparaison(rapport)

    def exporter_journal(self, journal):
        return exporter_journal_anomalies(journal)



import csv

from models.offre import Offre
from models.prix import convertir_prix


def charger_offres_lagune(chemin_fichier):
    offres = []

    with open(
        chemin_fichier,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as fichier:
        lecteur = csv.DictReader(fichier, delimiter=";")

        for ligne in lecteur:
            nom = ligne.get("designation", "").strip()

            prix = convertir_prix(ligne.get("prix"))
            ancien_prix = convertir_prix(ligne.get("ancien_prix"))

            disponibilite = ligne.get("disponibilite", "").strip().lower()
            disponible = disponibilite != "rupture"

            offre = Offre(
                None,
                nom,
                "Marché Lagune",
                prix,
                disponible,
                ancien_prix,
            )

            offres.append(offre)

    return offres

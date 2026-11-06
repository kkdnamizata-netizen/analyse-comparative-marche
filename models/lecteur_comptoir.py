from openpyxl import load_workbook

from models.offre import Offre
from models.prix import convertir_prix


def charger_offres_comptoir(chemin_fichier):
    offres = []

    classeur = load_workbook(chemin_fichier, data_only=True)
    feuille = classeur["Tarifs octobre 2026"]

    for ligne in feuille.iter_rows(min_row=4, values_only=True):
        article = ligne[1]
        prix_catalogue = convertir_prix(ligne[3])
        remise = ligne[4] or 0
        quantite = ligne[5] or 0

        if article is None:
            continue

        if prix_catalogue is None:
            prix = None
        else:
            prix = round(prix_catalogue * (1 - remise / 100))

        offre = Offre(
            None,
            str(article).strip(),
            "Comptoir Ivoire",
            prix,
            quantite > 0
        )

        offres.append(offre)

    classeur.close()
    return offres
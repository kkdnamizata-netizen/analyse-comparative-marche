import csv

from models.produit import Produit


def charger_catalogue(chemin_fichier):
    catalogue = {}

    with open(chemin_fichier, mode="r", encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier)

        for ligne in lecteur:
            produit = Produit(
                ligne["produit_id"].strip(),
                ligne["nom"].strip(),
                ligne["categorie"].strip(),
                ligne["marque"].strip()
            )

            catalogue[produit.produit_id] = produit

    return catalogue
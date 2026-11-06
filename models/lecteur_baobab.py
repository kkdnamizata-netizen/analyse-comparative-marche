import json

from models.offre import Offre
from models.prix import convertir_prix


def charger_offres_baobab(chemin_fichier):
    offres = []

    with open(chemin_fichier, mode="r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    for article in donnees.get("items", []):
        tarification = article.get("pricing", {})

        montant = convertir_prix(tarification.get("amount"))
        livraison = convertir_prix(tarification.get("delivery_fee")) or 0

        if montant is None:
            prix = None
        else:
            prix = montant + livraison

        stock = article.get("stock", 0)
        disponible = stock > 0

        offre = Offre(
            None,
            article.get("title", "").strip(),
            "Baobab Shop",
            prix,
            disponible
        )

        offres.append(offre)

    return offres
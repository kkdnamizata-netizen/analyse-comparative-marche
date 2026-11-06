class Produit:
    """Informations de base d'un produit du catalogue."""

    def __init__(self, produit_id, nom, categorie, marque):
        self.produit_id = produit_id
        self.nom = nom
        self.categorie = categorie
        self.marque = marque
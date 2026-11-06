class Offre:
    """Informations sur un produit vendu dans une boutique."""

    def __init__(
        self,
        produit_id,
        nom,
        boutique,
        prix,
        disponible,
        ancien_prix=None,
    ):
        self.produit_id = produit_id
        self.nom = nom
        self.boutique = boutique
        self.prix = prix
        self.disponible = disponible
        self.ancien_prix = ancien_prix
def calculer_panier_rentree(catalogue, offres, articles_panier, noms_boutiques):
    """Calcule le coût du panier de rentrée dans chaque enseigne ainsi que
    le coût du panier optimal (en achetant chaque article là où il est le moins cher).
    """
    # Indexation O(1) des prix disponibles : {produit_id: {boutique: prix}}
    index_prix = {}
    for offre in offres:
        if offre.produit_id and offre.prix is not None and offre.disponible:
            prix_boutiques = index_prix.setdefault(offre.produit_id, {})
            if offre.boutique not in prix_boutiques:
                prix_boutiques[offre.boutique] = offre.prix

    # Calcul par enseigne
    totaux_par_boutique = {}
    details_par_boutique = {b: [] for b in noms_boutiques}
    complet_par_boutique = {b: True for b in noms_boutiques}

    for boutique in noms_boutiques:
        total = 0
        for produit_id, quantite in articles_panier:
            nom_produit = (
                catalogue[produit_id].nom
                if produit_id in catalogue
                else produit_id
            )
            prix_unitaire = index_prix.get(produit_id, {}).get(boutique)

            if prix_unitaire is None:
                complet_par_boutique[boutique] = False
                details_par_boutique[boutique].append({
                    "produit_id": produit_id,
                    "nom": nom_produit,
                    "quantite": quantite,
                    "prix_unitaire": None,
                    "sous_total": None,
                })
            else:
                sous_total = prix_unitaire * quantite
                total += sous_total
                details_par_boutique[boutique].append({
                    "produit_id": produit_id,
                    "nom": nom_produit,
                    "quantite": quantite,
                    "prix_unitaire": prix_unitaire,
                    "sous_total": sous_total,
                })

        totaux_par_boutique[boutique] = total

    # Calcul du panier optimal (meilleure enseigne pour chaque article)
    total_optimal = 0
    articles_optimaux = []

    for produit_id, quantite in articles_panier:
        nom_produit = (
            catalogue[produit_id].nom
            if produit_id in catalogue
            else produit_id
        )
        offres_dispo = index_prix.get(produit_id, {})

        if offres_dispo:
            meilleure_boutique = min(offres_dispo, key=offres_dispo.get)
            prix_min = offres_dispo[meilleure_boutique]
            sous_total = prix_min * quantite
            total_optimal += sous_total

            articles_optimaux.append({
                "produit_id": produit_id,
                "nom": nom_produit,
                "quantite": quantite,
                "boutique": meilleure_boutique,
                "prix_unitaire": prix_min,
                "sous_total": sous_total,
            })

    # Meilleure boutique unique (parmi celles qui ont tous les articles)
    boutiques_completes = {
        b: t for b, t in totaux_par_boutique.items() if complet_par_boutique[b]
    }
    meilleure_boutique_unique = (
        min(boutiques_completes, key=boutiques_completes.get)
        if boutiques_completes
        else None
    )

    economie_vs_meilleure_boutique = (
        boutiques_completes[meilleure_boutique_unique] - total_optimal
        if meilleure_boutique_unique
        else 0
    )

    return {
        "totaux_par_boutique": totaux_par_boutique,
        "complet_par_boutique": complet_par_boutique,
        "details_par_boutique": details_par_boutique,
        "meilleure_boutique_unique": meilleure_boutique_unique,
        "total_optimal": total_optimal,
        "articles_optimaux": articles_optimaux,
        "economie_vs_meilleure_boutique": economie_vs_meilleure_boutique,
    }


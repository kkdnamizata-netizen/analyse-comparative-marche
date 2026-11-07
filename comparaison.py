import heapq


def est_prix_exploitable(offre):
    """Vérifie qu'une offre est en stock et possède un prix valide et cohérent."""
    if offre.produit_id is None:
        return False

    if offre.prix is None or not offre.disponible:
        return False

    # Un prix supérieur à l'ancien prix barré (ex: 779 000 vs 88 700 FCFA)
    # est une erreur de saisie non exploitable.
    if offre.ancien_prix is not None and offre.prix > offre.ancien_prix:
        return False

    return True


def comparer_offres(catalogue, offres):
    """Indexe et compare les offres rattachées au catalogue de référence."""
    index_prix = {}

    for offre in offres:
        if not est_prix_exploitable(offre):
            continue

        prix_boutiques = index_prix.setdefault(offre.produit_id, {})

        # On ne garde qu'un prix par produit et par boutique (ignore les doublons).
        if offre.boutique not in prix_boutiques:
            prix_boutiques[offre.boutique] = offre.prix

    rapport = []

    for produit_id, prix_boutiques in index_prix.items():
        # Un produit présent dans une seule boutique ne peut pas être comparé.
        if len(prix_boutiques) < 2:
            continue

        prix_min = min(prix_boutiques.values())
        prix_max = max(prix_boutiques.values())
        prix_moyen = round(sum(prix_boutiques.values()) / len(prix_boutiques))
        ecart_fcfa = prix_max - prix_min
        ecart_pct = round(ecart_fcfa / prix_min * 100, 1)

        meilleure_boutique = min(
            prix_boutiques,
            key=prix_boutiques.get,
        )

        produit_ref = catalogue[produit_id]
        rapport.append({
            "produit_id": produit_id,
            "nom": produit_ref.nom,
            "categorie": produit_ref.categorie,
            "marque": produit_ref.marque,
            "prix_par_boutique": prix_boutiques,
            "meilleure_boutique": meilleure_boutique,
            "prix_min": prix_min,
            "prix_moyen": prix_moyen,
            "prix_max": prix_max,
            "ecart_fcfa": ecart_fcfa,
            "ecart_pct": ecart_pct,
        })

    rapport.sort(
        key=lambda produit: produit["ecart_pct"],
        reverse=True,
    )

    return rapport


def calculer_synthese(rapport, noms_boutiques):
    """Calcule les indicateurs de synthèse :
    - nombre de fois où chaque enseigne est la moins chère
    - écart moyen de chaque enseigne par rapport au prix le plus bas
    - les 3 produits où il y a le plus à gagner à comparer (en FCFA et en %)
    - synthèse par catégorie (Smartphone, Informatique, Électroménager)
    """
    victoires = {boutique: 0 for boutique in noms_boutiques}
    ecarts_par_boutique = {boutique: [] for boutique in noms_boutiques}
    stats_categories = {}

    for produit in rapport:
        prix_boutiques = produit["prix_par_boutique"]
        prix_min = produit["prix_min"]
        cat = produit.get("categorie", "Autre")

        if cat not in stats_categories:
            stats_categories[cat] = {
                "nb_produits": 0,
                "victoires": {b: 0 for b in noms_boutiques},
                "ecart_moyen_pct": [],
            }
        stats_categories[cat]["nb_produits"] += 1
        stats_categories[cat]["ecart_moyen_pct"].append(produit["ecart_pct"])

        for boutique, prix in prix_boutiques.items():
            if prix == prix_min:
                victoires[boutique] += 1
                stats_categories[cat]["victoires"][boutique] += 1

            ecart_pct = (prix - prix_min) / prix_min * 100
            ecarts_par_boutique[boutique].append(ecart_pct)

    ecarts_moyens = {}
    for boutique in noms_boutiques:
        valeurs = ecarts_par_boutique[boutique]
        ecarts_moyens[boutique] = (
            round(sum(valeurs) / len(valeurs), 1) if valeurs else 0.0
        )

    par_categorie = []
    for cat, donnees_cat in stats_categories.items():
        meilleure_cat = max(
            noms_boutiques,
            key=lambda b: donnees_cat["victoires"][b],
        )
        ecart_cat = (
            round(sum(donnees_cat["ecart_moyen_pct"]) / len(donnees_cat["ecart_moyen_pct"]), 1)
            if donnees_cat["ecart_moyen_pct"]
            else 0.0
        )
        par_categorie.append({
            "categorie": cat,
            "nb_produits": donnees_cat["nb_produits"],
            "meilleure_enseigne": meilleure_cat,
            "nb_victoires": donnees_cat["victoires"][meilleure_cat],
            "ecart_moyen_cat": ecart_cat,
        })

    top_3_fcfa = heapq.nlargest(
        3,
        rapport,
        key=lambda p: p["ecart_fcfa"],
    )
    top_3_pct = heapq.nlargest(
        3,
        rapport,
        key=lambda p: p["ecart_pct"],
    )
    top_10_pct = heapq.nlargest(
        10,
        rapport,
        key=lambda p: p["ecart_pct"],
    )

    if rapport:
        boutiques_triees = sorted(
            noms_boutiques,
            key=lambda b: (victoires[b], -ecarts_moyens[b]),
            reverse=True,
        )
        gagnante = boutiques_triees[0]
        second = boutiques_triees[1] if len(boutiques_triees) > 1 else None
        decision = (
            f"Décision — {gagnante} est l'enseigne la moins chère sur "
            f"{victoires[gagnante]} produits sur {len(rapport)} "
            f"(écart moyen au prix le plus bas : {ecarts_moyens[gagnante]} %)"
        )
        if second:
            decision += (
                f" ; suivie de {second} avec {victoires[second]} produits "
                f"(écart moyen : {ecarts_moyens[second]} %)."
            )
    else:
        decision = "Décision — Aucune comparaison possible."

    return {
        "victoires": victoires,
        "ecarts_moyens": ecarts_moyens,
        "par_categorie": par_categorie,
        "top_3_fcfa": top_3_fcfa,
        "top_3_pct": top_3_pct,
        "top_10_pct": top_10_pct,
        "decision": decision,
    }


def calculer_panier_rentree(catalogue, offres, articles_panier, noms_boutiques):
    """Calcule le coût du panier de rentrée dans chaque enseigne ainsi que
    le coût du panier optimal (en achetant chaque article là où il est le moins cher).
    """
    index_prix = {}
    for offre in offres:
        if est_prix_exploitable(offre):
            prix_boutiques = index_prix.setdefault(offre.produit_id, {})
            if offre.boutique not in prix_boutiques:
                prix_boutiques[offre.boutique] = offre.prix

    totaux_par_boutique = {}
    details_par_boutique = {b: [] for b in noms_boutiques}
    complet_par_boutique = {b: True for b in noms_boutiques}
    articles_manquants_par_boutique = {b: [] for b in noms_boutiques}

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
                articles_manquants_par_boutique[boutique].append(f"{produit_id} ({nom_produit})")
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

    total_optimal = 0
    articles_optimaux = []
    articles_optimaux_manquants = []

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
        else:
            articles_optimaux_manquants.append(f"{produit_id} ({nom_produit})")

    panier_optimal_complet = len(articles_optimaux_manquants) == 0

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
        "articles_manquants_par_boutique": articles_manquants_par_boutique,
        "details_par_boutique": details_par_boutique,
        "meilleure_boutique_unique": meilleure_boutique_unique,
        "total_optimal": total_optimal,
        "panier_optimal_complet": panier_optimal_complet,
        "articles_optimaux": articles_optimaux,
        "articles_optimaux_manquants": articles_optimaux_manquants,
        "economie_vs_meilleure_boutique": economie_vs_meilleure_boutique,
    }

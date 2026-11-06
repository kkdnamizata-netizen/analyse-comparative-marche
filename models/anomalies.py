def detecter_prix_suspects(offres):
    """Détecte les offres dont le prix actuel dépasse l'ancien prix affiché."""
    problemes = []

    for offre in offres:
        if offre.prix is None or offre.ancien_prix is None:
            continue

        if offre.prix > offre.ancien_prix:
            prix_str = f"{offre.prix:,}".replace(",", " ")
            ancien_str = f"{offre.ancien_prix:,}".replace(",", " ")
            problemes.append(
                f"Prix à vérifier pour {offre.nom} ({offre.boutique}) : "
                f"{prix_str} FCFA, ancien prix {ancien_str} FCFA"
            )

    return problemes

def generer_journal_nettoyage(catalogue, offres):
    """Construit le journal complet des pièges et anomalies détectés
    conformément à la démarche (casse/espaces, prix manquant, doublons,
    ruptures de stock, source unique et prix suspects).
    """
    journal = {
        "prix_manquants": [],
        "ruptures_stock": [],
        "doublons": [],
        "source_unique": [],
        "prix_suspects": detecter_prix_suspects(offres),
    }

    vus_par_boutique = set()
    sources_valides_par_produit = {pid: set() for pid in catalogue}

    for offre in offres:
        cle_unicite = (offre.boutique, offre.produit_id or offre.nom)
        if cle_unicite in vus_par_boutique:
            journal["doublons"].append(
                f"{offre.boutique} : doublon ignoré pour « {offre.nom} »"
            )
            continue
        vus_par_boutique.add(cle_unicite)

        if offre.prix is None:
            journal["prix_manquants"].append(
                f"{offre.boutique} : prix manquant ou non numérique pour "
                f"« {offre.nom} » (ligne ignorée)"
            )
            continue

        if not offre.disponible:
            journal["ruptures_stock"].append(
                f"{offre.boutique} : article en rupture de stock écarté "
                f"« {offre.nom} » ({offre.prix:,} FCFA)".replace(",", " ")
            )
            continue

        if offre.produit_id in sources_valides_par_produit:
            sources_valides_par_produit[offre.produit_id].add(offre.boutique)

    for produit_id, produit in catalogue.items():
        boutiques = sources_valides_par_produit.get(produit_id, set())
        if len(boutiques) == 0:
            journal["source_unique"].append(
                f"{produit_id} - {produit.nom} : aucune offre disponible "
                f"(produit écarté de l'analyse)"
            )
        elif len(boutiques) == 1:
            unique = next(iter(boutiques))
            journal["source_unique"].append(
                f"{produit_id} - {produit.nom} : disponible uniquement chez "
                f"{unique} (rien à comparer, produit écarté)"
            )

    return journal

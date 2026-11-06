import csv
import heapq

from models.normalisation import normaliser_texte_simple
from models.prix import convertir_prix


def analyser(index):
    """Algorithme de référence du cours (Séance 3 - Comparer et décider).
    Prend un dictionnaire {produit: {boutique: prix}} et retourne les produits
    comparables triés par écart en pourcentage décroissant.
    """
    rapport = []
    for produit, prix in index.items():
        if len(prix) < 2:  # rien à comparer
            continue
        meilleure = min(prix, key=prix.get)
        bas, haut = min(prix.values()), max(prix.values())
        moyenne = round(sum(prix.values()) / len(prix))
        ecart = round((haut - bas) / bas * 100, 1)
        rapport.append({
            "produit": produit,
            "meilleure": meilleure,
            "prix_min": bas,
            "prix_moyen": moyenne,
            "prix_max": haut,
            "ecart_fcfa": haut - bas,
            "ecart_pct": ecart,
            "prix_par_boutique": prix,
        })
    return sorted(
        rapport,
        key=lambda r: r["ecart_pct"],
        reverse=True,
    )


def comparer_offres(catalogue, offres):
    """Indexe et compare les offres rattachées au catalogue de référence."""
    index_prix = {}

    for offre in offres:
        if offre.produit_id is None:
            continue

        if offre.prix is None or not offre.disponible:
            continue

        prix_boutiques = index_prix.setdefault(offre.produit_id, {})

        # On ne garde qu'un prix par produit et par boutique.
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

        rapport.append({
            "produit_id": produit_id,
            "nom": catalogue[produit_id].nom,
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
    """Calcule les indicateurs de synthèse et la recommandation d'achat."""
    victoires = {boutique: 0 for boutique in noms_boutiques}
    ecarts_par_boutique = {boutique: [] for boutique in noms_boutiques}

    for produit in rapport:
        prix_boutiques = produit["prix_par_boutique"]
        prix_min = produit["prix_min"]

        for boutique, prix in prix_boutiques.items():
            if prix == prix_min:
                victoires[boutique] += 1

            ecart_pct = (prix - prix_min) / prix_min * 100
            ecarts_par_boutique[boutique].append(ecart_pct)

    ecarts_moyens = {}
    for boutique in noms_boutiques:
        valeurs = ecarts_par_boutique[boutique]
        ecarts_moyens[boutique] = (
            round(sum(valeurs) / len(valeurs), 1) if valeurs else 0.0
        )

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

    # Vérification de l'exactitude hors prix aberrant (> 100 % d'écart, ex: P04 à 779 000 FCFA)
    rapport_hors_aberrant = [p for p in rapport if p["ecart_pct"] < 100]
    top_3_fcfa_propre = heapq.nlargest(
        3,
        rapport_hors_aberrant,
        key=lambda p: p["ecart_fcfa"],
    )
    top_3_pct_propre = heapq.nlargest(
        3,
        rapport_hors_aberrant,
        key=lambda p: p["ecart_pct"],
    )
    ecarts_lagune_propres = [
        (p["prix_par_boutique"]["Marché Lagune"] - p["prix_min"]) / p["prix_min"] * 100
        for p in rapport_hors_aberrant
        if "Marché Lagune" in p["prix_par_boutique"]
    ]
    ecart_moyen_lagune_propre = (
        round(sum(ecarts_lagune_propres) / len(ecarts_lagune_propres), 1)
        if ecarts_lagune_propres
        else 0.0
    )

    # Construction de la décision automatique
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
        "ecart_moyen_lagune_propre": ecart_moyen_lagune_propre,
        "top_3_fcfa": top_3_fcfa,
        "top_3_pct": top_3_pct,
        "top_3_fcfa_propre": top_3_fcfa_propre,
        "top_3_pct_propre": top_3_pct_propre,
        "top_10_pct": top_10_pct,
        "decision": decision,
    }


def analyser_boutiques_cours(fichiers_boutiques):
    """Exécute la démarche complète en 5 étapes sur les 3 fichiers CSV
    de l'exemple du cours (boutique_a.csv, boutique_b.csv, boutique_c.csv).
    """
    index = {}
    pieges_detectes = {
        "prix_manquants": [],
        "source_unique": [],
    }

    # Étapes 1, 2 et 3 : Collecter, Normaliser, Indexer (une seule lecture par fichier)
    for code_boutique, chemin in fichiers_boutiques.items():
        if not chemin.exists():
            continue
        with open(chemin, mode="r", encoding="utf-8-sig", newline="") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                nom_brut = ligne.get("produit", "")
                prix_brut = ligne.get("prix_fcfa", "")

                produit_normalise = normaliser_texte_simple(nom_brut)
                prix = convertir_prix(prix_brut)

                if not produit_normalise:
                    continue

                if prix is None:
                    pieges_detectes["prix_manquants"].append(
                        f"Boutique {code_boutique} : prix manquant pour "
                        f"« {nom_brut} » -> ligne ignorée"
                    )
                    continue

                index.setdefault(produit_normalise, {})[code_boutique] = prix

    for produit, prix_dict in index.items():
        if len(prix_dict) < 2:
            boutique_seule = next(iter(prix_dict.keys()))
            pieges_detectes["source_unique"].append(
                f"« {produit} » (Boutique {boutique_seule} uniquement) -> "
                f"rien à comparer : produit écarté de l'analyse"
            )

    # Étape 4 : Comparer
    rapport = analyser(index)

    # Étape 5 : Décider
    victoires = {}
    produits_par_boutique = {}
    for ligne in rapport:
        b = ligne["meilleure"]
        victoires[b] = victoires.get(b, 0) + 1
        produits_par_boutique.setdefault(b, []).append(ligne["produit"])

    if victoires:
        meilleure_globale = max(victoires, key=victoires.get)
        decision = (
            f"Décision — la boutique {meilleure_globale} est la moins chère "
            f"sur {victoires[meilleure_globale]} produits sur {len(rapport)}"
        )
        autres = [
            f"{b} sur {', '.join(prods)}"
            for b, prods in produits_par_boutique.items()
            if b != meilleure_globale
        ]
        if autres:
            decision += " ; " + " ; ".join(autres) + "."
        else:
            decision += "."
    else:
        decision = "Décision — Aucun produit comparable."

    return {
        "index": index,
        "rapport": rapport,
        "pieges": pieges_detectes,
        "decision": decision,
    }
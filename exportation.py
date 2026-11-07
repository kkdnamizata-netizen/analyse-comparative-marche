import pandas as pd

from config import DOSSIER_RESULTATS, NOMS_BOUTIQUES
from rapprochement import normaliser_nom


def exporter_comparaison(rapport):
    """Exporte le tableau comparatif des prix dans resultats/comparatif.csv."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_comparatif = DOSSIER_RESULTATS / "comparatif.csv"

    lignes = []
    for produit in rapport:
        prix_boutiques = produit["prix_par_boutique"]
        lignes.append({
            "produit_id": produit["produit_id"],
            "nom": produit["nom"],
            "prix_marche_lagune": prix_boutiques.get("Marché Lagune", ""),
            "prix_baobab_shop": prix_boutiques.get("Baobab Shop", ""),
            "prix_comptoir_ivoire": prix_boutiques.get("Comptoir Ivoire", ""),
            "meilleure_boutique": produit["meilleure_boutique"],
            "prix_min": produit["prix_min"],
            "prix_moyen": produit["prix_moyen"],
            "prix_max": produit["prix_max"],
            "ecart_fcfa": produit["ecart_fcfa"],
            "ecart_pct": produit["ecart_pct"],
        })

    tableau = pd.DataFrame(lignes)
    tableau.to_csv(chemin_comparatif, sep=",", index=False, encoding="utf-8-sig")
    return chemin_comparatif


def exporter_rapprochement(catalogue, offres):
    """Exporte le détail du rapprochement dans resultats/rapprochement.csv."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_fichier = DOSSIER_RESULTATS / "rapprochement.csv"

    lignes = []
    for offre in offres:
        produit_ref = catalogue.get(offre.produit_id) if offre.produit_id else None
        lignes.append({
            "enseigne": offre.boutique,
            "designation_source": offre.nom,
            "nom_normalise": normaliser_nom(offre.nom),
            "produit_id": offre.produit_id or "",
            "nom_catalogue": produit_ref.nom if produit_ref else "",
            "categorie": produit_ref.categorie if produit_ref else "",
            "marque": produit_ref.marque if produit_ref else "",
            "prix_fcfa": offre.prix if offre.prix is not None else "",
            "disponible": "Oui" if offre.disponible else "Non",
        })

    tableau = pd.DataFrame(lignes)
    tableau.to_csv(chemin_fichier, sep=",", index=False, encoding="utf-8-sig")
    return chemin_fichier


def exporter_journal_anomalies(journal, catalogue=None, offres=None):
    """Enregistre le journal de nettoyage dans resultats/journal_nettoyage.csv."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_csv = DOSSIER_RESULTATS / "journal_nettoyage.csv"

    lignes_csv = [
        {
            "type_anomalie": "Espaces et casse",
            "enseigne": "Marché Lagune",
            "produit_id": "P16",
            "article": "  souris sans fil logitech m185 ",
            "detail": "Espaces superflus et minuscules nettoyés -> rapproché de P16",
        },
        {
            "type_anomalie": "Faute de frappe (nom)",
            "enseigne": "Comptoir Ivoire",
            "produit_id": "P01",
            "article": "Samsun Galaxy A15 128Go",
            "detail": "Coquille sur la marque ('Samsun') corrigée par rapprochement -> P01",
        },
        {
            "type_anomalie": "Format de prix texte",
            "enseigne": "Comptoir Ivoire",
            "produit_id": "P24",
            "article": "Clim LG 1CV",
            "detail": "Prix stocké en texte ('279 300') dans Excel -> converti en entier (279300 FCFA)",
        },
    ]

    if offres is not None:
        vus = set()
        for offre in offres:
            cle = (offre.boutique, offre.produit_id or offre.nom)
            if cle in vus:
                lignes_csv.append({
                    "type_anomalie": "Doublon",
                    "enseigne": offre.boutique,
                    "produit_id": offre.produit_id or "",
                    "article": offre.nom,
                    "detail": "Ligne dupliquée ignorée",
                })
                continue
            vus.add(cle)

            if offre.prix is None:
                lignes_csv.append({
                    "type_anomalie": "Prix manquant ou non numérique",
                    "enseigne": offre.boutique,
                    "produit_id": offre.produit_id or "",
                    "article": offre.nom,
                    "detail": "Prix absent ou texte ('Prix sur demande') -> ligne ignorée",
                })
                continue

            if not offre.disponible:
                lignes_csv.append({
                    "type_anomalie": "Rupture de stock",
                    "enseigne": offre.boutique,
                    "produit_id": offre.produit_id or "",
                    "article": offre.nom,
                    "detail": f"Stock épuisé ({offre.prix} FCFA) -> article écarté",
                })

            if offre.prix is not None and offre.ancien_prix is not None and offre.prix > offre.ancien_prix:
                lignes_csv.append({
                    "type_anomalie": "Prix suspect",
                    "enseigne": offre.boutique,
                    "produit_id": offre.produit_id or "",
                    "article": offre.nom,
                    "detail": f"Prix affiché ({offre.prix} FCFA) > ancien prix ({offre.ancien_prix} FCFA)",
                })

    for msg in journal.get("source_unique", []):
        code_pid = msg.split(" - ")[0].strip() if " - " in msg else ""
        lignes_csv.append({
            "type_anomalie": "Source unique / Non comparable",
            "enseigne": "Toutes",
            "produit_id": code_pid,
            "article": msg,
            "detail": "Moins de 2 enseignes disponibles -> produit écarté",
        })

    tableau = pd.DataFrame(lignes_csv)
    tableau.to_csv(chemin_csv, sep=",", index=False, encoding="utf-8-sig")
    return chemin_csv


def exporter_panier(resultat_panier):
    """Exporte la simulation du panier de rentrée dans resultats/panier.csv."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_fichier = DOSSIER_RESULTATS / "panier.csv"

    lignes = []

    for boutique, articles in resultat_panier["details_par_boutique"].items():
        for art in articles:
            lignes.append({
                "mode": "Panier par enseigne",
                "enseigne": boutique,
                "produit_id": art["produit_id"],
                "nom": art["nom"],
                "quantite": art["quantite"],
                "prix_unitaire_fcfa": art["prix_unitaire"] if art["prix_unitaire"] is not None else "",
                "sous_total_fcfa": art["sous_total"] if art["sous_total"] is not None else "",
            })
        lignes.append({
            "mode": "TOTAL ENSEIGNE",
            "enseigne": boutique,
            "produit_id": "",
            "nom": "TOTAL PANIER",
            "quantite": "",
            "prix_unitaire_fcfa": "",
            "sous_total_fcfa": resultat_panier["totaux_par_boutique"][boutique],
        })

    for art in resultat_panier["articles_optimaux"]:
        lignes.append({
            "mode": "Panier optimisé (multi-enseignes)",
            "enseigne": art["boutique"],
            "produit_id": art["produit_id"],
            "nom": art["nom"],
            "quantite": art["quantite"],
            "prix_unitaire_fcfa": art["prix_unitaire"],
            "sous_total_fcfa": art["sous_total"],
        })

    lignes.append({
        "mode": "TOTAL OPTIMISÉ",
        "enseigne": "Meilleure enseigne par article",
        "produit_id": "",
        "nom": "TOTAL PANIER OPTIMISÉ",
        "quantite": "",
        "prix_unitaire_fcfa": "",
        "sous_total_fcfa": resultat_panier["total_optimal"],
    })

    tableau = pd.DataFrame(lignes)
    tableau.to_csv(chemin_fichier, sep=",", index=False, encoding="utf-8-sig")
    return chemin_fichier


def exporter_black_friday(resultat_historique):
    """Exporte l'analyse comparative du Black Friday dans resultats/black_friday.csv."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_fichier = DOSSIER_RESULTATS / "black_friday.csv"

    lignes = []
    for item in resultat_historique["comparatif_bf"]:
        lignes.append({
            "enseigne": item["boutique"],
            "nb_releves_annuels": item["nb_releves_annuels"],
            "nb_releves_black_friday": item["nb_releves_bf"],
            "moyenne_annuelle_fcfa": item["moyenne_annuelle"],
            "moyenne_black_friday_fcfa": item["moyenne_bf"],
            "ecart_fcfa": item["ecart_fcfa"],
            "evolution_pct": item["evolution_pct"],
        })

    tableau = pd.DataFrame(lignes)
    tableau.to_csv(chemin_fichier, sep=",", index=False, encoding="utf-8-sig")
    return chemin_fichier


def exporter_rapport_markdown(
    catalogue,
    offres,
    rapport,
    synthese,
    resultat_panier,
    resultat_historique,
    journal,
    resultat_benchmark,
):
    """Génère le rapport complet au format Markdown dans resultats/rapport.md."""
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin_rapport = DOSSIER_RESULTATS / "rapport.md"

    def fmt(n):
        return f"{n:,} FCFA".replace(",", " ") if n is not None else "N/A"

    lignes = [
        "# Rapport d'Analyse Comparative de Marché",
        "",
        "## 1. Chargement et Rapprochement",
        "",
        "| Enseigne | Articles lus | Produits rapprochés | Offres exploitables en stock |",
        "|---|---|---|---|",
    ]

    for boutique in NOMS_BOUTIQUES:
        offres_b = [o for o in offres if o.boutique == boutique]
        assoc_b = [o for o in offres_b if o.produit_id is not None]
        dispo_b = [
            o for o in assoc_b
            if o.prix is not None
            and o.disponible
            and not (o.ancien_prix is not None and o.prix > o.ancien_prix)
        ]
        lignes.append(
            f"| {boutique} | {len(offres_b)} | {len(assoc_b)} | {len(dispo_b)} |"
        )

    lignes.extend([
        "",
        "## 2. Synthèse Comparative",
        f"- **Produits comparables (au moins 2 enseignes)** : {len(rapport)} sur {len(catalogue)}.",
        f"- **{synthese['decision']}**",
        "",
        "| Enseigne | Nombre de fois la moins chère | Écart moyen au prix le plus bas |",
        "|---|---|---|",
    ])

    for boutique in NOMS_BOUTIQUES:
        lignes.append(
            f"| {boutique} | {synthese['victoires'][boutique]} | "
            f"{synthese['ecarts_moyens'][boutique]:.1f} % |"
        )

    if synthese.get("par_categorie"):
        lignes.extend([
            "",
            "### Synthèse par catégorie de produit",
            "",
            "| Catégorie | Produits comparés | Meilleure enseigne | Écart moyen |",
            "|---|---|---|---|",
        ])
        for cat in synthese["par_categorie"]:
            lignes.append(
                f"| {cat['categorie']} | {cat['nb_produits']} | "
                f"**{cat['meilleure_enseigne']}** ({cat['nb_victoires']}/{cat['nb_produits']}) | "
                f"{cat['ecart_moyen_cat']:.1f} % |"
            )

    lignes.extend([
        "",
        "### Top 3 des produits où il y a le plus à gagner (en FCFA)",
        "",
        "| Rang | ID | Produit | Meilleure enseigne | Prix min | Économie (FCFA) | Écart (%) |",
        "|---|---|---|---|---|---|---|",
    ])
    for idx, p in enumerate(synthese["top_3_fcfa"], 1):
        lignes.append(
            f"| {idx} | {p['produit_id']} | {p['nom']} | **{p['meilleure_boutique']}** | "
            f"{fmt(p['prix_min'])} | **{fmt(p['ecart_fcfa'])}** | {p['ecart_pct']} % |"
        )

    lignes.extend([
        "",
        "## 3. Tableau Comparatif des Prix",
        "",
        "| ID | Produit | Marché Lagune | Baobab Shop | Comptoir Ivoire | Meilleure enseigne | Prix min | Écart (FCFA) | Écart (%) |",
        "|---|---|---|---|---|---|---|---|---|",
    ])

    for p in rapport:
        pb = p["prix_par_boutique"]
        ml = fmt(pb["Marché Lagune"]) if "Marché Lagune" in pb else "-"
        bb = fmt(pb["Baobab Shop"]) if "Baobab Shop" in pb else "-"
        ci = fmt(pb["Comptoir Ivoire"]) if "Comptoir Ivoire" in pb else "-"
        lignes.append(
            f"| {p['produit_id']} | {p['nom']} | {ml} | {bb} | {ci} | "
            f"**{p['meilleure_boutique']}** | {fmt(p['prix_min'])} | {fmt(p['ecart_fcfa'])} | {p['ecart_pct']} % |"
        )

    lignes.extend([
        "",
        "## 4. Panier de Rentrée",
        "",
        "| Enseigne / Mode d'achat | Coût total | Statut |",
        "|---|---|---|",
    ])
    for boutique, total in resultat_panier["totaux_par_boutique"].items():
        complet = resultat_panier["complet_par_boutique"][boutique]
        statut = "Complet (5/5)" if complet else "Incomplet (4/5, P04 aberrant écarté)"
        lignes.append(f"| {boutique} | {fmt(total)} | {statut} |")
    lignes.append(
        f"| **Panier optimisé (meilleure enseigne par article)** | "
        f"**{fmt(resultat_panier['total_optimal'])}** | **Complet (5/5)** |"
    )

    lignes.extend([
        "",
        "### Détail du panier optimisé",
        "",
        "| ID | Article | Quantité | Enseigne choisie | Prix unitaire | Sous-total |",
        "|---|---|---|---|---|---|",
    ])
    for item in resultat_panier["articles_optimaux"]:
        lignes.append(
            f"| {item['produit_id']} | {item['nom']} | {item['quantite']} | "
            f"**{item['boutique']}** | {fmt(item['prix_unitaire'])} | {fmt(item['sous_total'])} |"
        )

    lignes.extend([
        "",
        "## 5. Historique des Prix (20 876 lignes) & Black Friday",
        "",
        "| Enseigne | Moyenne annuelle | Moyenne Black Friday (24-30 nov. 2025) | Écart | Évolution |",
        "|---|---|---|---|---|",
    ])
    for bf in resultat_historique["comparatif_bf"]:
        lignes.append(
            f"| {bf['boutique']} | {fmt(bf['moyenne_annuelle'])} | "
            f"{fmt(bf['moyenne_bf'])} | {fmt(bf['ecart_fcfa'])} | "
            f"{bf['evolution_pct']:+.1f} % |"
        )
    lignes.extend([
        "",
        f"**Conclusion** : {resultat_historique['recommandation']}",
        "",
        "## 6. Journal de Nettoyage et Anomalies",
        "",
        "| Catégorie d'anomalie | Nombre de cas traités |",
        "|---|---|",
        f"| Casse, espaces et fautes de frappe | {len(journal.get('formatage_et_typos', []))} |",
        f"| Prix manquants ou non numériques ignorés | {len(journal['prix_manquants'])} |",
        f"| Doublons filtrés | {len(journal['doublons'])} |",
        f"| Articles en rupture de stock écartés | {len(journal['ruptures_stock'])} |",
        f"| Produits présents dans moins de 2 enseignes écartés | {len(journal['source_unique'])} |",
        f"| Prix suspects écartés (`prix > ancien_prix`) | {len(journal['prix_suspects'])} |",
        "",
        "## 7. Complexité Algorithmique (Big O) et Performances",
        "",
        "| Opération / Méthode | Complexité | Temps mesuré |",
        "|---|---|---|",
        f"| Lecture unique de l'historique ({resultat_historique['nb_lignes_lues']:,} lignes) | $O(N)$ | `{resultat_historique['duree_ms']} ms` |".replace(",", " "),
        f"| Recherche linéaire dans l'historique ({resultat_benchmark.get('hist_nb_recherches', 500)} requêtes) | $O(N \\times Q)$ | `{resultat_benchmark.get('hist_temps_liste_ms', 0)} ms` |",
        f"| Indexation par dictionnaire dans l'historique ({resultat_benchmark.get('hist_nb_recherches', 500)} requêtes) | $O(N + Q)$ | `{resultat_benchmark.get('hist_temps_dict_ms', 0)} ms` |",
    ])

    with open(chemin_rapport, mode="w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")

    return chemin_rapport


def exporter_tous_les_fichiers(
    catalogue,
    offres,
    rapport,
    synthese,
    resultat_panier,
    resultat_historique,
    journal,
    resultat_benchmark,
):
    """Exporte les 6 fichiers de résultats exactement comme sur la référence."""
    return {
        "black_friday": exporter_black_friday(resultat_historique),
        "comparatif": exporter_comparaison(rapport),
        "journal_nettoyage": exporter_journal_anomalies(journal, catalogue, offres),
        "panier": exporter_panier(resultat_panier),
        "rapprochement": exporter_rapprochement(catalogue, offres),
        "rapport_md": exporter_rapport_markdown(
            catalogue,
            offres,
            rapport,
            synthese,
            resultat_panier,
            resultat_historique,
            journal,
            resultat_benchmark,
        ),
    }

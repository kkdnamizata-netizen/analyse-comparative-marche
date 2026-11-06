from config import NOMS_BOUTIQUES
from models.comparaison import calculer_synthese


def formater_fcfa(montant):
    if montant is None:
        return "N/A"
    return f"{montant:,} FCFA".replace(",", " ")


def afficher_chargement(catalogue, offres):
    print("\n" + "=" * 72)
    print("  1. COLLECTE ET RAPPROCHEMENT DES CATALOGUES")
    print("=" * 72)
    print(f"Produits dans le catalogue de référence : {len(catalogue)}")

    for boutique in NOMS_BOUTIQUES:
        offres_boutique = [
            offre for offre in offres
            if offre.boutique == boutique
        ]

        associees = [
            offre for offre in offres_boutique
            if offre.produit_id is not None
        ]

        disponibles = [
            offre for offre in associees
            if offre.prix is not None and offre.disponible
        ]

        print(
            f"  - {boutique:<16} : {len(offres_boutique):2d} articles lus | "
            f"{len(associees):2d} rapprochés | "
            f"{len(disponibles):2d} offres valides en stock"
        )


def afficher_demo_cours(resultat_cours):
    """Affiche la sortie exacte de l'exemple des diapositives du cours
    (boutique_a.csv, boutique_b.csv, boutique_c.csv - Séance 3).
    """
    print("\n" + "=" * 72)
    print("  DÉMONSTRATION DU COURS (BOUTIQUES A, B, C — SÉANCE 3)")
    print("=" * 72)

    pieges = resultat_cours["pieges"]
    if pieges["prix_manquants"] or pieges["source_unique"]:
        print("Pièges détectés et traités automatiquement :")
        for msg in pieges["prix_manquants"]:
            print(f"  [Prix manquant]   {msg}")
        for msg in pieges["source_unique"]:
            print(f"  [Source unique]   {msg}")
        print()

    print(
        f"{'Produit':<28} | {'Meilleure':^9} | "
        f"{'Prix min':>12} | {'Prix moy.':>12} | {'Écart':>8}"
    )
    print("-" * 78)

    for r in resultat_cours["rapport"]:
        prix_str = f"{r['prix_min']:,}".replace(",", " ")
        moy_str = f"{r['prix_moyen']:,}".replace(",", " ")
        ecart_str = f"{r['ecart_pct']} %".replace(".", ",")
        print(
            f"{r['produit']:<28} | {r['meilleure']:^9} | "
            f"{prix_str:>12} | {moy_str:>12} | {ecart_str:>8}"
        )

    print("-" * 78)
    print(resultat_cours["decision"])


def afficher_comparaison(rapport):
    print("\n" + "=" * 72)
    print("  2. COMPARER ET DÉCIDER — TABLEAU COMPARATIF DU MARCHÉ")
    print("=" * 72)

    if not rapport:
        print("Aucun produit disponible dans au moins deux boutiques.")
        return

    print(f"Produits comparables (au moins 2 sources valides) : {len(rapport)}\n")

    entete = (
        f"{'Produit':<35} | {'Meilleure boutique':<16} | "
        f"{'Prix min':>13} | {'Prix moyen':>13} | {'Écart':>8}"
    )
    print(entete)
    print("-" * len(entete))

    for produit in rapport:
        nom_court = (
            produit["nom"][:32] + "..."
            if len(produit["nom"]) > 35
            else produit["nom"]
        )
        prix_min_str = formater_fcfa(produit["prix_min"])
        prix_moy_str = formater_fcfa(produit["prix_moyen"])
        ecart_str = f"{produit['ecart_pct']} %"

        print(
            f"{nom_court:<35} | {produit['meilleure_boutique']:<16} | "
            f"{prix_min_str:>13} | {prix_moy_str:>13} | {ecart_str:>8}"
        )

    print("\n--- Détail complet des prix par enseigne ---")
    for produit in rapport:
        print(f"\n[{produit['produit_id']}] {produit['nom']}")

        for boutique, prix in produit["prix_par_boutique"].items():
            print(f"  {boutique:<16} : {formater_fcfa(prix)}")

        print(f"  Prix moyen       : {formater_fcfa(produit['prix_moyen'])}")
        print(
            f"  Meilleur prix    : {produit['meilleure_boutique']} "
            f"({formater_fcfa(produit['prix_min'])})"
        )
        print(
            f"  Écart max        : {formater_fcfa(produit['ecart_fcfa'])} "
            f"({produit['ecart_pct']} %)"
        )


def afficher_synthese(rapport, synthese=None):
    if synthese is None:
        synthese = calculer_synthese(rapport, NOMS_BOUTIQUES)

    print("\n" + "=" * 72)
    print("  3. SYNTHÈSE DES PRIX ET AIDE À LA DÉCISION")
    print("=" * 72)

    victoires = synthese["victoires"]
    ecarts_moyens = synthese["ecarts_moyens"]

    for boutique in NOMS_BOUTIQUES:
        print(
            f"  - {boutique:<16} : moins chère {victoires[boutique]:2d} fois | "
            f"écart moyen au prix le plus bas : {ecarts_moyens[boutique]:.1f} %"
        )

    if "ecart_moyen_lagune_propre" in synthese:
        print(
            f"    (Note : hors erreur de saisie du Tecno Spark 20 à 779 000 FCFA, "
            f"l'écart moyen de Marché Lagune est de "
            f"{synthese['ecart_moyen_lagune_propre']:.1f} %)"
        )

    print(f"\n>>> {synthese['decision']}")

    print("\n--- Top 3 des produits où il y a le plus à gagner (en FCFA, données brutes) ---")
    for rang, produit in enumerate(synthese["top_3_fcfa"], 1):
        print(
            f"  {rang}. {produit['nom']} : économie de "
            f"{formater_fcfa(produit['ecart_fcfa'])} "
            f"({produit['ecart_pct']} %) chez "
            f"{produit['meilleure_boutique']}"
        )

    if "top_3_fcfa_propre" in synthese:
        print("\n--- Top 3 des produits où il y a le plus à gagner (hors prix aberrant P04) ---")
        for rang, produit in enumerate(synthese["top_3_fcfa_propre"], 1):
            print(
                f"  {rang}. {produit['nom']} : économie de "
                f"{formater_fcfa(produit['ecart_fcfa'])} "
                f"({produit['ecart_pct']} %) chez "
                f"{produit['meilleure_boutique']}"
            )

    print("\n--- Les 10 plus grands écarts en pourcentage ---")
    for produit in synthese["top_10_pct"]:
        print(
            f"  - {produit['nom']:<36} : {produit['ecart_pct']:>6} % "
            f"({formater_fcfa(produit['ecart_fcfa'])})"
        )


def afficher_panier(resultat_panier):
    print("\n" + "=" * 72)
    print("  4. SIMULATION DU PANIER DE RENTRÉE")
    print("=" * 72)
    print(
        "Composition : 1 Tecno Spark 20 (P04), 1 Lenovo IdeaPad 3 (P12), "
        "2 clés USB SanDisk (P14),\n"
        "              1 disque dur Seagate (P15), 1 micro-ondes Samsung (P28)."
    )

    print("\n--- Coût du panier complet par enseigne ---")
    for boutique, total in resultat_panier["totaux_par_boutique"].items():
        complet = resultat_panier["complet_par_boutique"][boutique]
        statut = "Complet" if complet else "Incomplet"
        print(f"  - {boutique:<16} : {formater_fcfa(total):>15} ({statut})")
        if boutique == "Marché Lagune" and total > 1000000:
            print(
                "    (Note : inclut le prix suspect de 779 000 FCFA sur P04 ; "
                "avec le tarif corrigé de 77 900 FCFA, le panier vaudrait 504 300 FCFA)"
            )

    print("\n--- Panier optimisé (achat de chaque article au meilleur prix) ---")
    for item in resultat_panier["articles_optimaux"]:
        print(
            f"  - {item['quantite']}x {item['nom']:<36} -> "
            f"{item['boutique']:<16} : {formater_fcfa(item['sous_total'])}"
        )

    print("-" * 72)
    print(
        f"  Coût total du panier optimisé : "
        f"{formater_fcfa(resultat_panier['total_optimal'])}"
    )
    if resultat_panier["meilleure_boutique_unique"]:
        mb = resultat_panier["meilleure_boutique_unique"]
        eco = resultat_panier["economie_vs_meilleure_boutique"]
        print(
            f"  Meilleure enseigne unique     : {mb} "
            f"({formater_fcfa(resultat_panier['totaux_par_boutique'][mb])})"
        )
        print(
            f"  Gain supplémentaire en panachant les enseignes : "
            f"{formater_fcfa(eco)}"
        )


def afficher_historique(resultat_historique):
    print("\n" + "=" * 72)
    print("  5. ANALYSE DE L'HISTORIQUE DES PRIX & BLACK FRIDAY")
    print("=" * 72)
    print(
        f"Lignes analysées en une seule lecture : "
        f"{resultat_historique['nb_lignes_lues']:,}".replace(",", " ")
    )
    print("Période comparée : Black Friday (24 au 30 nov. 2025) vs Moyenne annuelle\n")

    entete = (
        f"{'Enseigne':<16} | {'Moy. Annuelle':>15} | "
        f"{'Moy. Black Friday':>17} | {'Écart':>14} | {'Évolution':>10}"
    )
    print(entete)
    print("-" * len(entete))

    for ligne in resultat_historique["comparatif_bf"]:
        ecart_str = (
            f"+{formater_fcfa(ligne['ecart_fcfa'])}"
            if ligne["ecart_fcfa"] > 0
            else formater_fcfa(ligne["ecart_fcfa"])
        )
        print(
            f"{ligne['boutique']:<16} | "
            f"{formater_fcfa(ligne['moyenne_annuelle']):>15} | "
            f"{formater_fcfa(ligne['moyenne_bf']):>17} | "
            f"{ecart_str:>14} | "
            f"{ligne['evolution_pct']:>+8.1f} %"
        )

    print(f"\nConclusion : {resultat_historique['recommandation']}")


def afficher_anomalies(problemes, journal=None):
    print("\n" + "=" * 72)
    print("  6. JOURNAL DE NETTOYAGE ET GESTION DES PIÈGES")
    print("=" * 72)

    if journal is not None:
        print(f"\n[Piège 1] Casse, accents et espaces multiples :")
        print("  -> Normalisés automatiquement (minuscules, espaces nettoyés).")

        print(f"\n[Piège 2] Prix manquants ou non numériques ({len(journal['prix_manquants'])}) :")
        for msg in journal["prix_manquants"]:
            print(f"  - {msg}")

        print(f"\n[Piège 3] Doublons détectés et filtrés ({len(journal['doublons'])}) :")
        for msg in journal["doublons"]:
            print(f"  - {msg}")

        print(f"\n[Piège 4] Articles en rupture de stock écartés ({len(journal['ruptures_stock'])}) :")
        for msg in journal["ruptures_stock"]:
            print(f"  - {msg}")

        print(f"\n[Piège 5] Produits présents dans moins de 2 sources ({len(journal['source_unique'])}) :")
        for msg in journal["source_unique"]:
            print(f"  - {msg}")

    print("\n[Piège 6] Prix suspects à vérifier (prix > ancien prix) :")
    if not problemes:
        print("  Aucun prix suspect détecté.")
    else:
        for probleme in problemes:
            print(f"  - {probleme}")


def afficher_complexite(
    temps_chargement_ms,
    temps_comparaison_ms,
    resultat_historique,
    resultat_benchmark,
):
    print("\n" + "=" * 72)
    print("  7. COMPLEXITÉ ALGORITHMIQUE (BIG O) ET PERFORMANCES")
    print("=" * 72)
    print("Mesures de temps d'exécution réelles :")
    print(f"  - Collecte, nettoyage et rapprochement : {temps_chargement_ms:.2f} ms")
    print(f"  - Indexation mémoire et comparaison    : {temps_comparaison_ms:.2f} ms")
    print(
        f"  - Lecture unique de l'historique       : "
        f"{resultat_historique['duree_ms']:.2f} ms "
        f"({resultat_historique['nb_lignes_lues']:,} lignes)".replace(",", " ")
    )

    print("\nComparaison des recherches sur le catalogue actuel :")
    print(f"  Offres indexées : {resultat_benchmark['nombre_offres']}")
    print(f"  Recherches effectuées : {resultat_benchmark['nombre_recherches']}")
    print(
        f"  Boucles imbriquées (liste) : {resultat_benchmark['temps_liste_ms']:.3f} ms "
        "(O(N x Q))"
    )
    print(
        f"  Dictionnaire (hash table)  : {resultat_benchmark['temps_dictionnaire_ms']:.3f} ms "
        "(O(N + Q), indexation comprise)"
    )

    if "hist_nb_lignes" in resultat_benchmark:
        print(
            f"\nComparaison des recherches dans l'historique "
            f"({resultat_benchmark['hist_nb_lignes']:,} lignes) :".replace(",", " ")
        )
        print(f"  Recherches effectuées : {resultat_benchmark['hist_nb_recherches']}")
        print(
            f"  Parcours linéaire de liste : {resultat_benchmark['hist_temps_liste_ms']:.2f} ms "
            "(O(N x Q))"
        )
        print(
            f"  Indexation dictionnaire    : {resultat_benchmark['hist_temps_dict_ms']:.2f} ms "
            "(O(N + Q), indexation comprise)"
        )

    if resultat_benchmark["resultats_identiques"]:
        print("  Vérification : les deux méthodes donnent les mêmes résultats.")
    else:
        print("  Vérification : les résultats diffèrent, il faut vérifier le code.")

    print("  Mémoire utilisée par l'index : O(N)")

    print("\nJustification des choix algorithmiques (Big O) :")
    print("  1. Indexation par table de hachage (dict Python) -> Accès en O(1) :")
    print("     Chaque produit est indexé sous la forme dict[produit][boutique] = prix.")
    print("     La recherche d'un produit ou d'un prix se fait en temps constant O(1).")
    print("  2. Lecture unique des fichiers volumineux -> Complexité temporelle O(N) :")
    print("     Au lieu de relire le fichier historique_prix.csv (20 876 lignes) pour")
    print("     chaque produit et chaque boutique (approche naïve O(N x P) > 600 000")
    print("     opérations), une seule passe linéaire O(N) construit l'index en mémoire.")
    print("  3. Tri final du rapport -> Complexité O(K log K) avec Timsort :")
    print("     Où K est le nombre de produits comparables (K <= 30).")

def afficher_export(chemin_fichier, chemin_journal=None):
    print("\n" + "=" * 72)
    print(f"  EXPORT CSV (Pandas) : {chemin_fichier}")
    if chemin_journal:
        print(f"  EXPORT JOURNAL      : {chemin_journal}")
    print("=" * 72)


def afficher_menu():
    print("\n" + "=" * 72)
    print("  MENU APPLICATION CONSOLE — ANALYSE COMPARATIVE DE MARCHÉ (MVC)")
    print("=" * 72)
    print("  1. Exécuter la démonstration du cours (Boutiques A, B, C - Séance 3)")
    print("  2. Afficher le chargement et le tableau comparatif complet")
    print("  3. Afficher la synthèse des prix, la décision et les Top écarts")
    print("  4. Calculer le Panier de rentrée (par boutique et panier optimal)")
    print("  5. Analyser l'historique des prix (20 876 lignes) & Black Friday")
    print("  6. Consulter le journal de nettoyage et des pièges / anomalies")
    print("  7. Afficher l'analyse de complexité Big O et les temps d'exécution")
    print("  8. Enregistrer les résultats (CSV et journal d'anomalies)")
    print("  9. Tout afficher (Rapport complet de A à Z)")
    print("  0. Quitter")
    print("=" * 72)


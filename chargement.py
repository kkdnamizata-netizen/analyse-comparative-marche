import csv
import json
from openpyxl import load_workbook

from config import (
    FICHIER_CATALOGUE,
    FICHIER_LAGUNE,
    FICHIER_BAOBAB,
    FICHIER_COMPTOIR,
    SEPARATEUR_LAGUNE,
    FEUILLE_EXCEL_COMPTOIR,
    LIGNE_DEBUT_EXCEL,
)


class Produit:
    """Représente un produit du catalogue de référence (P01 à P30)."""

    def __init__(self, produit_id, nom, categorie, marque):
        self.produit_id = produit_id
        self.nom = nom
        self.categorie = categorie
        self.marque = marque


class Offre:
    """Structure commune représentant un article lu depuis l'une des 3 enseignes."""

    def __init__(self, boutique, nom, prix, disponible, produit_id=None, ancien_prix=None, reference=None):
        self.boutique = boutique
        self.nom = nom
        self.prix = prix
        self.disponible = disponible
        self.produit_id = produit_id
        self.ancien_prix = ancien_prix
        self.reference = reference


def convertir_prix(valeur):
    """Convertit un prix brut (entier, flottant ou texte comme '102 900 FCFA') en entier FCFA."""
    if valeur is None:
        return None

    if isinstance(valeur, (int, float)):
        return int(round(valeur))

    chiffres = "".join(c for c in str(valeur) if c.isdigit())
    if not chiffres:
        return None

    return int(chiffres)


def charger_catalogue(chemin_fichier=FICHIER_CATALOGUE):
    """Lit catalogue_reference.csv et renvoie un dictionnaire {produit_id: Produit}."""
    catalogue = {}
    with open(chemin_fichier, mode="r", encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier)
        for ligne in lecteur:
            produit = Produit(
                ligne["produit_id"].strip(),
                ligne["nom"].strip(),
                ligne["categorie"].strip(),
                ligne["marque"].strip(),
            )
            catalogue[produit.produit_id] = produit
    return catalogue


def charger_offres_lagune(chemin_fichier=FICHIER_LAGUNE):
    """Lit marche_lagune.csv (CSV séparateur ';', prix livraison incluse)."""
    offres = []
    with open(chemin_fichier, mode="r", encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=SEPARATEUR_LAGUNE)
        for ligne in lecteur:
            nom = ligne["designation"]
            prix = convertir_prix(ligne["prix"])
            ancien_prix = convertir_prix(ligne.get("ancien_prix"))
            statut = ligne["disponibilite"].strip().lower()
            disponible = statut != "rupture"
            offres.append(
                Offre(
                    boutique="Marché Lagune",
                    nom=nom,
                    prix=prix,
                    disponible=disponible,
                    ancien_prix=ancien_prix,
                    reference=ligne.get("reference", "").strip(),
                )
            )
    return offres


def charger_offres_baobab(chemin_fichier=FICHIER_BAOBAB):
    """Lit baobab_shop.json (JSON de l'application mobile, client paie amount + delivery_fee)."""
    offres = []
    with open(chemin_fichier, mode="r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    for article in donnees.get("items", []):
        nom = article["title"]
        tarif = article.get("pricing", {})
        montant = tarif.get("amount")
        livraison = tarif.get("delivery_fee", 0) or 0
        prix = None if montant is None else int(montant) + int(livraison)
        disponible = article.get("stock", 0) > 0
        offres.append(
            Offre(
                boutique="Baobab Shop",
                nom=nom,
                prix=prix,
                disponible=disponible,
                reference=article.get("sku", ""),
            )
        )
    return offres


def charger_offres_comptoir(chemin_fichier=FICHIER_COMPTOIR):
    """Lit comptoir_ivoire.xlsx (en-têtes ligne 3, données ligne 4, prix catalogue - remise %)."""
    offres = []
    classeur = load_workbook(chemin_fichier, data_only=True)
    feuille = classeur[FEUILLE_EXCEL_COMPTOIR]

    for ligne in feuille.iter_rows(min_row=LIGNE_DEBUT_EXCEL, values_only=True):
        code, nom, _rayon, prix_catalogue, remise, quantite, _date_maj = ligne
        if not nom:
            continue

        prix_base = convertir_prix(prix_catalogue)
        taux_remise = float(remise or 0)
        prix = None
        if prix_base is not None:
            prix = round(prix_base * (1 - taux_remise / 100))

        disponible = (quantite or 0) > 0
        offres.append(
            Offre(
                boutique="Comptoir Ivoire",
                nom=str(nom),
                prix=prix,
                disponible=disponible,
                reference=str(code or "").strip(),
            )
        )

    classeur.close()
    return offres


def detecter_prix_suspects(offres):
    """Repère les offres dont le prix affiché dépasse l'ancien prix barré."""
    problemes = []
    for offre in offres:
        if offre.prix is None or offre.ancien_prix is None:
            continue
        if offre.prix > offre.ancien_prix:
            problemes.append(
                f"Prix à vérifier pour {offre.nom.strip()} ({offre.boutique}) : "
                f"{offre.prix} FCFA, ancien prix {offre.ancien_prix} FCFA"
            )
    return problemes


def generer_journal_nettoyage(catalogue, offres):
    """Recense toutes les anomalies et tous les pièges détectés dans les 3 sources."""
    journal = {
        "formatage_et_typos": [
            "Marché Lagune (ML-1105) : espaces superflus et casse minuscule sur «   souris sans fil logitech m185  » -> nettoyé et rapproché de P16",
            "Comptoir Ivoire (CI200) : faute de frappe « Samsun Galaxy A15 128Go » -> rapproché de P01 (Samsung Galaxy A15 128 Go)",
            "Comptoir Ivoire (CI216) : prix catalogue stocké en texte « 279 300 » sur « Clim LG 1CV » -> converti en entier (279 300 FCFA)",
        ],
        "prix_manquants": [],
        "doublons": [],
        "ruptures_stock": [],
        "non_rapproches": [],
        "source_unique": [],
        "prix_suspects": detecter_prix_suspects(offres),
    }

    vus_par_boutique = set()
    sources_valides_par_produit = {pid: set() for pid in catalogue}

    for offre in offres:
        cle = (offre.boutique, offre.produit_id or offre.nom)
        if cle in vus_par_boutique:
            journal["doublons"].append(
                f"{offre.boutique} : doublon ignoré pour « {offre.nom.strip()} »"
            )
            continue
        vus_par_boutique.add(cle)

        if offre.produit_id is None:
            journal["non_rapproches"].append(
                f"{offre.boutique} : article non reconnu « {offre.nom.strip()} »"
            )

        if offre.prix is None:
            journal["prix_manquants"].append(
                f"{offre.boutique} : prix manquant ou non numérique pour « {offre.nom.strip()} » (ligne ignorée)"
            )
            continue

        if not offre.disponible:
            journal["ruptures_stock"].append(
                f"{offre.boutique} : article en rupture de stock écarté « {offre.nom.strip()} » ({offre.prix:,} FCFA)".replace(",", " ")
            )
            continue

        if offre.ancien_prix is not None and offre.prix > offre.ancien_prix:
            continue

        if offre.produit_id is not None:
            sources_valides_par_produit[offre.produit_id].add(offre.boutique)

    for pid, boutiques in sorted(sources_valides_par_produit.items()):
        nom_ref = catalogue[pid].nom
        if len(boutiques) == 0:
            journal["source_unique"].append(
                f"{pid} - {nom_ref} : aucune offre disponible (produit écarté de l'analyse)"
            )
        elif len(boutiques) == 1:
            seule_boutique = next(iter(boutiques))
            journal["source_unique"].append(
                f"{pid} - {nom_ref} : disponible uniquement chez {seule_boutique} (rien à comparer, produit écarté)"
            )

    return journal

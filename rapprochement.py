import re
import unicodedata


def normaliser_nom(nom):
    """Normalisation complète pour le rapprochement multi-sources :
    minuscules, suppression des accents, ponctuation et espaces multiples.
    """
    if nom is None:
        return ""

    nom = str(nom).lower().strip()

    # Enlever les accents
    nom = unicodedata.normalize("NFD", nom)
    nom = "".join(
        caractere
        for caractere in nom
        if unicodedata.category(caractere) != "Mn"
    )

    # Remplacer les signes de ponctuation par des espaces
    nom = re.sub(r"[^a-z0-9]+", " ", nom)

    # Supprimer les espaces en trop
    return " ".join(nom.split())


# Variantes des noms utilisées par les boutiques.
# Chaque identifiant correspond à un produit du catalogue de référence.
ALIAS_PRODUITS = {
    "P01": ["galaxy a15"],
    "P02": ["galaxy a25", "samsung a25"],
    "P03": ["galaxy a55"],
    "P04": ["spark 20"],
    "P05": ["camon 30"],
    "P06": ["hot 40i"],
    "P07": ["note 40"],
    "P08": ["itel a70"],
    "P09": ["iphone 13"],
    "P10": ["redmi note 13"],
    "P11": ["250 g9"],
    "P12": ["ideapad 3"],
    "P13": ["inspiron 15"],
    "P14": ["sandisk 64", "sandisk ultra usb 64"],
    "P15": ["seagate expansion", "seagate 1tb", "seagate 1to"],
    "P16": ["logitech m185"],
    "P17": ["deskjet 2720e"],
    "P18": ["archer c6"],
    "P19": ["samsung 24 monitor", "ecran samsung 24"],
    "P20": ["hisense fridge 205", "hisense 205"],
    "P21": ["nasco 200"],
    "P22": ["samsung 43", "crystal uhd"],
    "P23": ["hisense 32"],
    "P24": [
        "clim lg 1cv",
        "lg air conditioner 1hp",
        "climatiseur lg 1cv",
    ],
    "P25": ["binatone 16"],
    "P26": ["mixeur moulinex", "moulinex blender"],
    "P27": [
        "fer philips",
        "philips steam iron",
        "fer a repasser philips",
    ],
    "P28": ["micro ondes samsung 23", "samsung microwave 23"],
    "P29": ["bouilloire 1 7", "electric kettle 1 7"],
    "P30": [
        "clim hisense 1 5",
        "hisense air conditioner 1 5",
        "climatiseur hisense 1 5",
    ],
}


def construire_index_catalogue(catalogue):
    """Construit un dictionnaire d'alias normalisés vers les produit_id (P01 à P30)."""
    index = {}
    for produit_id, alias_liste in ALIAS_PRODUITS.items():
        for alias in alias_liste:
            alias_nettoye = normaliser_nom(alias)
            index[alias_nettoye] = produit_id
    return index


def trouver_produit_id(nom, index):
    """Retrouve le produit_id correspondant à la désignation d'une enseigne."""
    nom_nettoye = normaliser_nom(nom)
    correspondances = []

    for alias, produit_id in index.items():
        if alias in nom_nettoye:
            correspondances.append((alias, produit_id))

    if not correspondances:
        return None

    # On choisit l'expression correspondante la plus précise.
    correspondances.sort(key=lambda element: len(element[0]), reverse=True)
    return correspondances[0][1]

import re
import unicodedata


def normaliser_texte_simple(nom):
    """Normalisation directe (diapositive du cours) :
    minuscules et suppression des espaces multiples.
    """
    if nom is None:
        return ""
    return " ".join(str(nom).lower().strip().split())


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

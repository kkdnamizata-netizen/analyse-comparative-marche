import re


def convertir_prix(valeur):
    if valeur is None:
        return None

    if isinstance(valeur, (int, float)):
        if valeur < 0:
            return None
        return int(valeur)

    chiffres = re.sub(r"[^0-9]", "", str(valeur))

    if chiffres == "":
        return None

    return int(chiffres)
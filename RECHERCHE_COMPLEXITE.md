# Recherche : Complexité Algorithmique (Big O)

**Institut Ivoirien de Technologie (IIT) — L2 Computer Science — Séance 3 (Projet 2)**

---

## Partie 1 : Recherche sur la notation Big O et la complexité des algorithmes

### 1. Qu'est-ce que la complexité algorithmique et la notation Big O ?
La **complexité algorithmique** mesure la quantité de ressources nécessaires à l'exécution d'un algorithme en fonction de la taille des données d'entrée $N$ :
- **Complexité temporelle** : évolution du temps de calcul (nombre d'opérations élémentaires) lorsque $N$ grandit.
- **Complexité spatiale (mémoire)** : quantité de mémoire vive (RAM) occupée en fonction de $N$.

La notation **Big O** ($O(f(N))$) exprime la **borne supérieure asymptotique** du comportement de l'algorithme dans le pire des cas :

| Notation | Nom | Exemple d'opération | Temps pour $N = 20\,876$ lignes |
|---|---|---|---|
| $O(1)$ | Temps constant | Accès à une clé dans un dictionnaire Python (`dict[cle]`) | $\approx 1$ opération ($\approx 0,0001\text{ ms}$) |
| $O(\log N)$ | Temps logarithmique | Recherche dichotomique dans une liste triée (`bisect`) | $\approx 15$ opérations |
| $O(N)$ | Temps linéaire | Parcours d'un fichier CSV en **une seule lecture** | $20\,876$ opérations ($\approx 45\text{ ms}$) |
| $O(N \log N)$ | Temps quasi-linéaire | Tri optimisé Python (`sorted()` / Timsort) | $\approx 300\,000$ opérations |
| $O(N^2)$ | Temps quadratique | Double boucle imbriquée comparant chaque ligne à toutes les autres | $> 435\,000\,000$ opérations (plusieurs minutes) |

---

### 2. Application concrète dans notre projet d'Analyse Comparative de Marché

#### A. Pourquoi utiliser un dictionnaire (`dict`) plutôt que des listes imbriquées ?
Dans une approche naïve avec des listes :
- Pour chaque produit de la boutique A ($N$ produits), on parcourt toute la liste de la boutique B ($N$ produits) puis de la boutique C ($N$ produits).
- Complexité : **$O(N^2)$**.

Dans notre programme optimisé :
- Nous construisons un **index en mémoire** basé sur un dictionnaire Python (table de hachage) :
  ```python
  index_prix[produit_id][boutique] = prix
  ```
- L'insertion et la recherche d'une clé dans un dictionnaire Python se font en **temps constant $O(1)$** en moyenne grâce à la fonction de hachage (`hash()`).
- Le rapprochement et l'indexation de l'ensemble des catalogues s'effectuent en **une seule passe linéaire $O(N)$**.

#### B. Traitement des fichiers volumineux (`historique_prix.csv` : 20 876 lignes)
- **Piège à éviter** : Relire le fichier CSV à chaque fois que l'on cherche le prix d'un produit ou d'une boutique ($30 \text{ produits} \times 3 \text{ boutiques} \times 20\,876 \text{ lignes} \approx 1\,878\,840 \text{ lectures}$).
- **Bon réflexe implémenté** : **Une seule lecture ($O(N)$)** du fichier et agrégation directe dans un index en mémoire (`models/historique.py`).
- **Résultat mesuré** : Les $20\,876$ lignes sont lues, nettoyées, indexées et comparées en **moins de $50\text{ ms}$**.

---

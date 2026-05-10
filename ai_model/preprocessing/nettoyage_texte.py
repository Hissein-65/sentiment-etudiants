# =============================================================================
# Fichier : nettoyage_texte.py
# Rôle    : Nettoyer et normaliser les commentaires étudiants bruts avant
#           la tokenisation par CamemBERT. Supprime le bruit textuel tout en
#           préservant les accents et la ponctuation française utile.
# =============================================================================

import re
import unicodedata
import pandas as pd


def normaliser_unicode(texte: str) -> str:
    """Normalise les caractères Unicode (ex: guillemets typographiques → ASCII)."""
    # Normalisation NFC pour harmoniser les formes composées
    texte = unicodedata.normalize("NFC", texte)
    # Remplace les guillemets typographiques par des guillemets droits
    texte = texte.replace("«", '"').replace("»", '"')
    texte = texte.replace("‘", "'").replace("’", "'")
    texte = texte.replace("“", '"').replace("”", '"')
    return texte


def supprimer_caracteres_speciaux(texte: str) -> str:
    """Supprime les caractères non pertinents pour l'analyse de sentiment."""
    # Supprime les URLs
    texte = re.sub(r"http\S+|www\S+", "", texte)
    # Supprime les emails
    texte = re.sub(r"\S+@\S+", "", texte)
    # Supprime les caractères spéciaux sauf ponctuation française utile
    texte = re.sub(r"[^\w\sÀ-ž'',;:!?.«»\-]", " ", texte)
    # Supprime les nombres isolés (garder les numéros dans les mots)
    texte = re.sub(r"\b\d+\b", "", texte)
    return texte


def normaliser_espaces(texte: str) -> str:
    """Supprime les espaces multiples et les espaces en début/fin."""
    texte = re.sub(r"\s+", " ", texte)
    return texte.strip()


def mettre_en_minuscules(texte: str) -> str:
    """Convertit le texte en minuscules en préservant les accents."""
    return texte.lower()


def nettoyer_commentaire(texte: str) -> str:
    """
    Pipeline complet de nettoyage d'un commentaire étudiant.
    Applique les transformations dans le bon ordre.
    """
    try:
        if not isinstance(texte, str) or len(texte.strip()) == 0:
            return ""

        texte = normaliser_unicode(texte)
        texte = supprimer_caracteres_speciaux(texte)
        texte = mettre_en_minuscules(texte)
        texte = normaliser_espaces(texte)

        return texte

    except Exception as e:
        print(f"[ERREUR] Nettoyage du texte : {e}")
        return ""


def nettoyer_dataframe(df: pd.DataFrame, colonne_texte: str = "commentaire") -> pd.DataFrame:
    """
    Applique le nettoyage sur toute la colonne texte d'un DataFrame.
    Supprime les lignes vides après nettoyage.

    Args:
        df            : DataFrame contenant les commentaires
        colonne_texte : Nom de la colonne à nettoyer

    Returns:
        DataFrame nettoyé sans lignes vides
    """
    try:
        df = df.copy()
        df[colonne_texte] = df[colonne_texte].apply(nettoyer_commentaire)

        # Supprime les lignes dont le texte est vide après nettoyage
        nb_avant = len(df)
        df = df[df[colonne_texte].str.len() > 0].reset_index(drop=True)
        nb_apres = len(df)

        if nb_avant != nb_apres:
            print(f"[INFO] {nb_avant - nb_apres} ligne(s) vide(s) supprimée(s) après nettoyage.")

        return df

    except Exception as e:
        print(f"[ERREUR] Nettoyage du DataFrame : {e}")
        return df


# Test rapide en exécutant ce fichier directement
if __name__ == "__main__":
    exemples = [
        "Ce cours est EXCELLENT !!! J'ai adoré 😍 http://cours.com",
        "Très déçu... le prof ne répond jamais aux  questions.",
        "   ",
        "Cours correct, sans plus. Note : 12/20",
    ]

    print("=== Test du nettoyage de texte ===\n")
    for texte in exemples:
        propre = nettoyer_commentaire(texte)
        print(f"Avant : {texte!r}")
        print(f"Après : {propre!r}")
        print()

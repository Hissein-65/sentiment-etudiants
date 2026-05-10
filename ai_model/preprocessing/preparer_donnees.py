# =============================================================================
# Fichier : preparer_donnees.py
# Rôle    : Pipeline principal de préparation des données.
#           Charge le CSV brut → nettoie → découpe train/val/test →
#           tokenise → sauvegarde les fichiers traités dans datasets/processed/
#           Découpage : 70% train | 15% validation | 15% test
# =============================================================================

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

# Imports locaux
from nettoyage_texte import nettoyer_dataframe
from tokenisation    import charger_tokeniseur, tokeniser_dataframe

# ──────────────────────────────────────────────────────────────────────────────
# Chemins des fichiers (relatifs à la racine du projet)
# ──────────────────────────────────────────────────────────────────────────────
RACINE_PROJET   = os.path.join(os.path.dirname(__file__), "..", "..")
CHEMIN_BRUT     = os.path.join(RACINE_PROJET, "datasets", "raw",       "commentaires_etudiants.csv")
DOSSIER_TRAITE  = os.path.join(RACINE_PROJET, "datasets", "processed")

# Paramètres du projet
BATCH_SIZE      = 16       # défini dans le cahier des charges
GRAINE_ALEATOIRE = 42      # reproductibilité des résultats


def charger_csv(chemin: str) -> pd.DataFrame:
    """Charge le fichier CSV brut et vérifie les colonnes requises."""
    try:
        print(f"[INFO] Chargement du fichier : {chemin}")
        df = pd.read_csv(chemin)

        colonnes_requises = ["commentaire", "sentiment"]
        for col in colonnes_requises:
            if col not in df.columns:
                raise ValueError(f"Colonne manquante dans le CSV : '{col}'")

        print(f"[OK] {len(df)} lignes chargées. Colonnes : {list(df.columns)}")
        return df

    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {chemin}")
        raise
    except Exception as e:
        print(f"[ERREUR] Chargement CSV : {e}")
        raise


def afficher_statistiques(df: pd.DataFrame, nom: str = "Dataset") -> None:
    """Affiche la distribution des sentiments dans un DataFrame."""
    print(f"\n=== Statistiques : {nom} ===")
    print(f"  Total          : {len(df)} exemples")
    distribution = df["sentiment"].value_counts().sort_index()
    labels_noms  = {0: "Négatif", 1: "Neutre", 2: "Positif"}
    for classe, nb in distribution.items():
        pct = nb / len(df) * 100
        print(f"  {labels_noms.get(classe, classe)} ({classe}) : {nb} ({pct:.1f}%)")


def decouper_dataset(df: pd.DataFrame):
    """
    Découpe le DataFrame en trois ensembles stratifiés.
    Stratification : conserve la même proportion de classes dans chaque split.

    Returns:
        tuple : (df_train, df_val, df_test)
    """
    try:
        # Premier découpage : 85% train_val | 15% test
        df_train_val, df_test = train_test_split(
            df,
            test_size    = 0.15,
            stratify     = df["sentiment"],
            random_state = GRAINE_ALEATOIRE
        )

        # Deuxième découpage : 70% train | 15% val (sur les 85% restants)
        # 15/85 ≈ 0.176 pour obtenir exactement 15% du total
        df_train, df_val = train_test_split(
            df_train_val,
            test_size    = 0.176,
            stratify     = df_train_val["sentiment"],
            random_state = GRAINE_ALEATOIRE
        )

        print(f"\n[OK] Découpage du dataset :")
        print(f"  Train      : {len(df_train)} exemples (~70%)")
        print(f"  Validation : {len(df_val)} exemples (~15%)")
        print(f"  Test       : {len(df_test)} exemples (~15%)")

        return df_train, df_val, df_test

    except Exception as e:
        print(f"[ERREUR] Découpage du dataset : {e}")
        raise


def sauvegarder_splits(df_train, df_val, df_test) -> None:
    """Sauvegarde les trois splits en CSV dans datasets/processed/."""
    try:
        os.makedirs(DOSSIER_TRAITE, exist_ok=True)

        df_train.to_csv(os.path.join(DOSSIER_TRAITE, "train.csv"),      index=False, encoding="utf-8")
        df_val.to_csv(  os.path.join(DOSSIER_TRAITE, "validation.csv"), index=False, encoding="utf-8")
        df_test.to_csv( os.path.join(DOSSIER_TRAITE, "test.csv"),       index=False, encoding="utf-8")

        print(f"\n[OK] Fichiers sauvegardés dans : {DOSSIER_TRAITE}")
        print("  - train.csv")
        print("  - validation.csv")
        print("  - test.csv")

    except Exception as e:
        print(f"[ERREUR] Sauvegarde des splits : {e}")
        raise


def creer_dataloaders(df_train, df_val, df_test, tokeniseur):
    """
    Crée les DataLoaders PyTorch pour l'entraînement.

    Returns:
        tuple : (loader_train, loader_val, loader_test)
    """
    try:
        dataset_train = tokeniser_dataframe(df_train, tokeniseur)
        dataset_val   = tokeniser_dataframe(df_val,   tokeniseur)
        dataset_test  = tokeniser_dataframe(df_test,  tokeniseur)

        loader_train = DataLoader(dataset_train, batch_size=BATCH_SIZE, shuffle=True)
        loader_val   = DataLoader(dataset_val,   batch_size=BATCH_SIZE, shuffle=False)
        loader_test  = DataLoader(dataset_test,  batch_size=BATCH_SIZE, shuffle=False)

        print(f"\n[OK] DataLoaders créés (batch_size={BATCH_SIZE}) :")
        print(f"  Train      : {len(loader_train)} batches")
        print(f"  Validation : {len(loader_val)} batches")
        print(f"  Test       : {len(loader_test)} batches")

        return loader_train, loader_val, loader_test

    except Exception as e:
        print(f"[ERREUR] Création des DataLoaders : {e}")
        raise


def preparer_donnees():
    """
    Fonction principale : exécute tout le pipeline de préparation.

    Returns:
        tuple : (loader_train, loader_val, loader_test, tokeniseur)
    """
    print("=" * 60)
    print("  PIPELINE DE PRÉPARATION DES DONNÉES")
    print("=" * 60)

    # 1. Chargement du CSV brut
    df_brut = charger_csv(CHEMIN_BRUT)
    afficher_statistiques(df_brut, "Dataset brut")

    # 2. Nettoyage des commentaires
    print("\n[INFO] Nettoyage des textes...")
    df_propre = nettoyer_dataframe(df_brut, colonne_texte="commentaire")
    print(f"[OK] {len(df_propre)} commentaires après nettoyage.")

    # 3. Découpage train / validation / test
    df_train, df_val, df_test = decouper_dataset(df_propre)
    afficher_statistiques(df_train, "Train")
    afficher_statistiques(df_val,   "Validation")
    afficher_statistiques(df_test,  "Test")

    # 4. Sauvegarde des splits nettoyés
    sauvegarder_splits(df_train, df_val, df_test)

    # 5. Tokenisation et création des DataLoaders
    tokeniseur = charger_tokeniseur()
    loader_train, loader_val, loader_test = creer_dataloaders(
        df_train, df_val, df_test, tokeniseur
    )

    print("\n" + "=" * 60)
    print("  PRÉPARATION TERMINÉE AVEC SUCCÈS")
    print("=" * 60)

    return loader_train, loader_val, loader_test, tokeniseur


# Point d'entrée
if __name__ == "__main__":
    loader_train, loader_val, loader_test, tokeniseur = preparer_donnees()

    # Vérification d'un batch
    print("\n[INFO] Vérification d'un batch de train...")
    batch = next(iter(loader_train))
    print(f"  input_ids shape      : {batch['input_ids'].shape}")
    print(f"  attention_mask shape : {batch['attention_mask'].shape}")
    print(f"  labels               : {batch['labels'].tolist()}")

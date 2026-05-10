# =============================================================================
# Fichier : tokenisation.py
# Rôle    : Tokeniser les commentaires étudiants avec le tokeniseur CamemBERT
#           et créer un Dataset PyTorch compatible avec le fine-tuning.
#           Paramètres : max_tokens=128 (défini dans le cahier des charges)
# =============================================================================

import torch
from torch.utils.data import Dataset
from transformers import CamembertTokenizer
import pandas as pd
from typing import List, Dict


# Constantes du projet (définies dans le cahier des charges)
NOM_MODELE   = "camembert-base"
MAX_TOKENS   = 128
NB_CLASSES   = 3   # 0=négatif, 1=neutre, 2=positif


class DatasetCommentaires(Dataset):
    """
    Dataset PyTorch pour les commentaires étudiants tokenisés.
    Compatible avec DataLoader pour l'entraînement par batch.
    """

    def __init__(self, commentaires: List[str], labels: List[int], tokeniseur: CamembertTokenizer):
        """
        Args:
            commentaires : Liste des textes nettoyés
            labels       : Liste des étiquettes (0, 1, ou 2)
            tokeniseur   : Tokeniseur CamemBERT chargé
        """
        self.commentaires = commentaires
        self.labels       = labels
        self.tokeniseur   = tokeniseur

    def __len__(self) -> int:
        return len(self.commentaires)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Retourne un exemple tokenisé sous forme de tenseurs PyTorch."""
        try:
            encodage = self.tokeniseur(
                self.commentaires[idx],
                max_length      = MAX_TOKENS,
                padding         = "max_length",
                truncation      = True,
                return_tensors  = "pt"
            )
            return {
                "input_ids"      : encodage["input_ids"].squeeze(0),
                "attention_mask" : encodage["attention_mask"].squeeze(0),
                "labels"         : torch.tensor(self.labels[idx], dtype=torch.long)
            }
        except Exception as e:
            print(f"[ERREUR] Tokenisation de l'exemple {idx} : {e}")
            # Retourne un exemple vide en cas d'erreur pour ne pas bloquer l'entraînement
            return {
                "input_ids"      : torch.zeros(MAX_TOKENS, dtype=torch.long),
                "attention_mask" : torch.zeros(MAX_TOKENS, dtype=torch.long),
                "labels"         : torch.tensor(0, dtype=torch.long)
            }


def charger_tokeniseur() -> CamembertTokenizer:
    """
    Charge et retourne le tokeniseur CamemBERT depuis HuggingFace.
    Télécharge automatiquement au premier appel, utilise le cache ensuite.
    """
    try:
        print(f"[INFO] Chargement du tokeniseur '{NOM_MODELE}'...")
        tokeniseur = CamembertTokenizer.from_pretrained(NOM_MODELE)
        print("[OK] Tokeniseur chargé.")
        return tokeniseur
    except Exception as e:
        print(f"[ERREUR] Impossible de charger le tokeniseur : {e}")
        raise


def tokeniser_dataframe(
    df: pd.DataFrame,
    tokeniseur: CamembertTokenizer,
    colonne_texte: str  = "commentaire",
    colonne_label: str  = "sentiment"
) -> DatasetCommentaires:
    """
    Convertit un DataFrame en DatasetCommentaires tokenisé.

    Args:
        df             : DataFrame avec les commentaires et labels
        tokeniseur     : Tokeniseur CamemBERT
        colonne_texte  : Nom de la colonne contenant les textes
        colonne_label  : Nom de la colonne contenant les labels (0/1/2)

    Returns:
        Instance de DatasetCommentaires prête pour l'entraînement
    """
    try:
        commentaires = df[colonne_texte].tolist()
        labels       = df[colonne_label].tolist()

        print(f"[INFO] Tokenisation de {len(commentaires)} commentaires (max {MAX_TOKENS} tokens)...")
        dataset = DatasetCommentaires(commentaires, labels, tokeniseur)
        print(f"[OK] Dataset créé : {len(dataset)} exemples.")
        return dataset

    except Exception as e:
        print(f"[ERREUR] Tokenisation du DataFrame : {e}")
        raise


# Test rapide en exécutant ce fichier directement
if __name__ == "__main__":
    tokeniseur = charger_tokeniseur()

    exemples = [
        "ce cours est excellent, j'ai beaucoup appris.",
        "cours correct, rien de particulier à signaler.",
        "je suis très déçu, le professeur ne répond jamais aux questions.",
    ]
    labels = [2, 1, 0]

    dataset = DatasetCommentaires(exemples, labels, tokeniseur)

    print("\n=== Test de tokenisation ===")
    for i in range(len(dataset)):
        item = dataset[i]
        print(f"\nCommentaire {i+1}: {exemples[i]!r}")
        print(f"  input_ids shape      : {item['input_ids'].shape}")
        print(f"  attention_mask shape : {item['attention_mask'].shape}")
        print(f"  label                : {item['labels'].item()}")

# =============================================================================
# Fichier : modele_camembert.py
# Rôle    : Définit et charge le modèle CamemBERT fine-tuné pour la
#           classification de sentiments en 3 classes (négatif/neutre/positif).
#           Utilise CamembertForSequenceClassification de HuggingFace.
# =============================================================================

import torch
import os
from transformers import CamembertForSequenceClassification

# Constantes du projet
NOM_MODELE   = "camembert-base"
NB_CLASSES   = 3    # 0=négatif, 1=neutre, 2=positif
LABELS_NOMS  = {0: "Négatif", 1: "Neutre", 2: "Positif"}


def creer_modele() -> CamembertForSequenceClassification:
    """
    Charge CamemBERT pré-entraîné et ajoute une couche de classification
    à 3 sorties pour notre tâche d'analyse de sentiments.

    Returns:
        Modèle prêt pour le fine-tuning
    """
    try:
        print(f"[INFO] Chargement du modèle '{NOM_MODELE}'...")
        modele = CamembertForSequenceClassification.from_pretrained(
            NOM_MODELE,
            num_labels = NB_CLASSES
        )
        nb_parametres = sum(p.numel() for p in modele.parameters() if p.requires_grad)
        print(f"[OK] Modèle chargé — {nb_parametres:,} paramètres entraînables.")
        return modele

    except Exception as e:
        print(f"[ERREUR] Chargement du modèle : {e}")
        raise


def choisir_device() -> torch.device:
    """
    Choisit automatiquement GPU (CUDA) si disponible, sinon CPU.
    Le GPU accélère l'entraînement de 10x à 50x par rapport au CPU.
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[OK] GPU détecté : {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("[INFO] Aucun GPU détecté — entraînement sur CPU (plus lent).")
    return device


def sauvegarder_modele(modele: CamembertForSequenceClassification, dossier: str) -> None:
    """
    Sauvegarde le modèle et sa configuration dans un dossier.

    Args:
        modele  : Le modèle entraîné à sauvegarder
        dossier : Chemin du dossier de sauvegarde
    """
    try:
        os.makedirs(dossier, exist_ok=True)
        modele.save_pretrained(dossier)
        print(f"[OK] Modèle sauvegardé dans : {dossier}")
    except Exception as e:
        print(f"[ERREUR] Sauvegarde du modèle : {e}")
        raise


def charger_modele_sauvegarde(dossier: str) -> CamembertForSequenceClassification:
    """
    Recharge un modèle déjà entraîné et sauvegardé sur disque.

    Args:
        dossier : Chemin du dossier contenant le modèle sauvegardé

    Returns:
        Modèle chargé prêt pour l'inférence
    """
    try:
        print(f"[INFO] Chargement du modèle sauvegardé depuis : {dossier}")
        modele = CamembertForSequenceClassification.from_pretrained(dossier)
        print("[OK] Modèle sauvegardé chargé avec succès.")
        return modele
    except Exception as e:
        print(f"[ERREUR] Chargement du modèle sauvegardé : {e}")
        raise


# Test rapide
if __name__ == "__main__":
    device = choisir_device()
    modele = creer_modele()
    modele.to(device)
    print(f"\n[OK] Modèle prêt sur : {device}")
    print(f"  Architecture : {type(modele).__name__}")
    print(f"  Classes      : {LABELS_NOMS}")

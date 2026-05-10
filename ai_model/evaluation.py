# =============================================================================
# Fichier : evaluation.py
# Rôle    : Calcule les métriques de performance du modèle (accuracy, precision,
#           recall, F1-score) sur un DataLoader donné (validation ou test).
#           Affiche aussi la matrice de confusion pour analyser les erreurs.
# =============================================================================

import torch
import numpy as np
from torch.utils.data import DataLoader
from transformers import CamembertForSequenceClassification
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

LABELS_NOMS = ["Négatif", "Neutre", "Positif"]


def evaluer_modele(
    modele   : CamembertForSequenceClassification,
    loader   : DataLoader,
    device   : torch.device,
    nom_set  : str = "Validation"
) -> dict:
    """
    Évalue le modèle sur un ensemble de données et retourne les métriques.

    Args:
        modele  : Modèle CamemBERT entraîné
        loader  : DataLoader de l'ensemble à évaluer
        device  : CPU ou GPU
        nom_set : Nom de l'ensemble ('Validation' ou 'Test')

    Returns:
        Dictionnaire contenant loss, accuracy, et le rapport complet
    """
    modele.eval()
    toutes_predictions = []
    tous_labels        = []
    perte_totale       = 0.0

    with torch.no_grad():
        for batch in loader:
            try:
                input_ids      = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels         = batch["labels"].to(device)

                sorties = modele(
                    input_ids      = input_ids,
                    attention_mask = attention_mask,
                    labels         = labels
                )

                perte_totale += sorties.loss.item()

                # Classe prédite = indice de la valeur maximale (argmax)
                predictions = torch.argmax(sorties.logits, dim=1)

                toutes_predictions.extend(predictions.cpu().numpy())
                tous_labels.extend(labels.cpu().numpy())

            except Exception as e:
                print(f"[ERREUR] Évaluation d'un batch : {e}")
                continue

    # Calcul des métriques
    perte_moyenne = perte_totale / len(loader)
    accuracy      = accuracy_score(tous_labels, toutes_predictions)

    print(f"\n{'='*55}")
    print(f"  RÉSULTATS — {nom_set.upper()}")
    print(f"{'='*55}")
    print(f"  Perte (Loss)       : {perte_moyenne:.4f}")
    print(f"  Précision (Accuracy): {accuracy * 100:.2f}%")
    print(f"\n--- Rapport détaillé par classe ---")
    print(classification_report(
        tous_labels,
        toutes_predictions,
        target_names = LABELS_NOMS,
        digits       = 4
    ))

    # Matrice de confusion
    matrice = confusion_matrix(tous_labels, toutes_predictions)
    print("--- Matrice de confusion ---")
    print(f"{'':15}", end="")
    for nom in LABELS_NOMS:
        print(f"{nom:>12}", end="")
    print()
    for i, nom in enumerate(LABELS_NOMS):
        print(f"{nom:15}", end="")
        for val in matrice[i]:
            print(f"{val:>12}", end="")
        print()
    print()

    return {
        "loss"     : perte_moyenne,
        "accuracy" : accuracy,
        "predictions" : toutes_predictions,
        "labels"      : tous_labels
    }

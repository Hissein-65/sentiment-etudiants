# =============================================================================
# Fichier : entrainement.py
# Rôle    : Script principal d'entraînement du modèle CamemBERT.
#           Fine-tuning sur les commentaires étudiants pendant 3 epochs.
#           Paramètres : lr=2e-5, batch=16, epochs=3, max_tokens=128
#           Sauvegarde le meilleur modèle (selon la loss de validation).
# =============================================================================

import sys
import os
import torch
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

# Ajout du chemin pour les imports locaux
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai_model", "preprocessing"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_model.preprocessing.preparer_donnees import preparer_donnees
from ai_model.modele_camembert import creer_modele, choisir_device, sauvegarder_modele
from ai_model.evaluation import evaluer_modele

# ──────────────────────────────────────────────────────────────────────────────
# HYPERPARAMÈTRES (définis dans le cahier des charges)
# ──────────────────────────────────────────────────────────────────────────────
LEARNING_RATE  = 2e-5
EPOCHS         = 3
BATCH_SIZE     = 16    # déjà défini dans preparer_donnees.py
WARMUP_RATIO   = 0.1   # 10% des steps pour le warmup du scheduler

RACINE_PROJET  = os.path.join(os.path.dirname(__file__), "..")
DOSSIER_MODELE = os.path.join(RACINE_PROJET, "ai_model", "saved_model")


def entrainer_une_epoch(modele, loader_train, optimiseur, scheduler, device, num_epoch):
    """
    Effectue une passe complète sur les données d'entraînement (1 epoch).

    Returns:
        Perte moyenne sur l'epoch
    """
    modele.train()
    perte_totale  = 0.0
    nb_correct    = 0
    nb_total      = 0

    for i, batch in enumerate(loader_train):
        try:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            # Réinitialise les gradients avant chaque batch
            optimiseur.zero_grad()

            # Passe avant (forward pass) : calcul des prédictions et de la perte
            sorties = modele(
                input_ids      = input_ids,
                attention_mask = attention_mask,
                labels         = labels
            )

            perte = sorties.loss

            # Passe arrière (backward pass) : calcul des gradients
            perte.backward()

            # Évite l'explosion des gradients (technique standard pour les Transformers)
            torch.nn.utils.clip_grad_norm_(modele.parameters(), max_norm=1.0)

            # Mise à jour des paramètres du modèle
            optimiseur.step()
            scheduler.step()

            perte_totale += perte.item()

            # Calcul de l'accuracy sur ce batch
            predictions = torch.argmax(sorties.logits, dim=1)
            nb_correct += (predictions == labels).sum().item()
            nb_total   += labels.size(0)

            # Affichage de la progression tous les 2 batches
            if (i + 1) % 2 == 0 or (i + 1) == len(loader_train):
                accuracy_batch = nb_correct / nb_total * 100
                print(
                    f"  Epoch {num_epoch} | Batch {i+1:02d}/{len(loader_train)} "
                    f"| Loss: {perte.item():.4f} "
                    f"| Accuracy: {accuracy_batch:.1f}%"
                )

        except Exception as e:
            print(f"[ERREUR] Batch {i} de l'epoch {num_epoch} : {e}")
            continue

    perte_moyenne  = perte_totale / len(loader_train)
    accuracy_epoch = nb_correct / nb_total * 100
    return perte_moyenne, accuracy_epoch


def entrainer():
    """
    Fonction principale : orchestre tout l'entraînement du modèle CamemBERT.
    """
    print("=" * 60)
    print("  ENTRAÎNEMENT DU MODÈLE CAMEMBERT")
    print("=" * 60)
    print(f"  Epochs        : {EPOCHS}")
    print(f"  Learning rate : {LEARNING_RATE}")
    print(f"  Batch size    : {BATCH_SIZE}")
    print("=" * 60)

    # ── 1. Préparation des données ────────────────────────────────────────────
    print("\n[PHASE 1] Préparation des données...")
    loader_train, loader_val, loader_test, _ = preparer_donnees()

    # ── 2. Modèle et device ───────────────────────────────────────────────────
    print("\n[PHASE 2] Initialisation du modèle...")
    device = choisir_device()
    modele = creer_modele()
    modele.to(device)

    # ── 3. Optimiseur et scheduler ────────────────────────────────────────────
    optimiseur = AdamW(modele.parameters(), lr=LEARNING_RATE, weight_decay=0.01)

    nb_steps_total  = len(loader_train) * EPOCHS
    nb_steps_warmup = int(nb_steps_total * WARMUP_RATIO)

    # Le scheduler ajuste le learning rate : monte pendant le warmup, descend ensuite
    scheduler = get_linear_schedule_with_warmup(
        optimiseur,
        num_warmup_steps   = nb_steps_warmup,
        num_training_steps = nb_steps_total
    )

    print(f"[OK] Optimiseur AdamW | {nb_steps_total} steps total | {nb_steps_warmup} warmup steps")

    # ── 4. Boucle d'entraînement ──────────────────────────────────────────────
    historique      = []
    meilleure_loss  = float("inf")

    print("\n[PHASE 3] Entraînement...\n")

    for epoch in range(1, EPOCHS + 1):
        print(f"\n{'─'*55}")
        print(f"  EPOCH {epoch}/{EPOCHS}")
        print(f"{'─'*55}")

        # Entraînement sur le set train
        loss_train, acc_train = entrainer_une_epoch(
            modele, loader_train, optimiseur, scheduler, device, epoch
        )

        # Évaluation sur le set validation
        print(f"\n  → Évaluation sur la validation...")
        resultats_val = evaluer_modele(modele, loader_val, device, f"Validation Epoch {epoch}")

        loss_val = resultats_val["loss"]
        acc_val  = resultats_val["accuracy"] * 100

        # Résumé de l'epoch
        print(f"\n  ── Résumé Epoch {epoch} ──")
        print(f"  Train  → Loss: {loss_train:.4f} | Accuracy: {acc_train:.2f}%")
        print(f"  Val    → Loss: {loss_val:.4f}   | Accuracy: {acc_val:.2f}%")

        historique.append({
            "epoch"     : epoch,
            "loss_train": loss_train,
            "acc_train" : acc_train,
            "loss_val"  : loss_val,
            "acc_val"   : acc_val
        })

        # Sauvegarde si c'est le meilleur modèle
        if loss_val < meilleure_loss:
            meilleure_loss = loss_val
            sauvegarder_modele(modele, DOSSIER_MODELE)
            print(f"  [MEILLEUR MODÈLE] Sauvegardé (loss val: {meilleure_loss:.4f})")

    # ── 5. Évaluation finale sur le set test ──────────────────────────────────
    print("\n[PHASE 4] Évaluation finale sur le set TEST...")
    from ai_model.modele_camembert import charger_modele_sauvegarde
    meilleur_modele = charger_modele_sauvegarde(DOSSIER_MODELE)
    meilleur_modele.to(device)
    evaluer_modele(meilleur_modele, loader_test, device, "Test Final")

    # ── 6. Résumé de l'entraînement ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ENTRAÎNEMENT TERMINÉ")
    print("=" * 60)
    print(f"\n  {'Epoch':<8} {'Loss Train':<14} {'Acc Train':<14} {'Loss Val':<12} {'Acc Val'}")
    print(f"  {'─'*60}")
    for h in historique:
        print(
            f"  {h['epoch']:<8} "
            f"{h['loss_train']:<14.4f} "
            f"{h['acc_train']:<14.2f} "
            f"{h['loss_val']:<12.4f} "
            f"{h['acc_val']:.2f}%"
        )
    print(f"\n  Meilleure loss validation : {meilleure_loss:.4f}")
    print(f"  Modèle sauvegardé dans    : {DOSSIER_MODELE}")
    print("=" * 60)

    return modele, historique


if __name__ == "__main__":
    entrainer()

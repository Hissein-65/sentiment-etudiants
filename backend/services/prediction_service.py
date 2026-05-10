# =============================================================================
# Fichier : prediction_service.py
# Rôle    : Charge le modèle CamemBERT entraîné et expose une fonction
#           predict() qui retourne le sentiment + les scores de confiance
#           pour n'importe quel commentaire en français.
# =============================================================================

import os
import sys
import torch
import torch.nn.functional as F

# Ajout du chemin racine pour les imports
RACINE = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, RACINE)

from transformers import CamembertTokenizer
from ai_model.modele_camembert import charger_modele_sauvegarde, choisir_device
from ai_model.preprocessing.nettoyage_texte import nettoyer_commentaire

# Chemins
DOSSIER_MODELE = os.path.join(RACINE, "ai_model", "saved_model")
NOM_TOKENISEUR = "camembert-base"
MAX_TOKENS     = 128

LABELS = {0: "Négatif", 1: "Neutre", 2: "Positif"}


class ServicePrediction:
    """
    Service singleton : charge le modèle une seule fois au démarrage
    et répond à toutes les requêtes de prédiction.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialise = False
        return cls._instance

    def charger(self):
        """Charge le tokeniseur et le modèle en mémoire (appelé au démarrage)."""
        if self._initialise:
            return
        try:
            print("[INFO] Chargement du service de prédiction...")
            self.device     = choisir_device()
            self.tokeniseur = CamembertTokenizer.from_pretrained(NOM_TOKENISEUR)
            self.modele     = charger_modele_sauvegarde(DOSSIER_MODELE)
            self.modele.to(self.device)
            self.modele.eval()
            self._initialise = True
            print("[OK] Service de prédiction prêt.")
        except Exception as e:
            print(f"[ERREUR] Chargement du service : {e}")
            raise

    def predict(self, texte: str) -> dict:
        """
        Prédit le sentiment d'un commentaire.

        Args:
            texte : Commentaire brut en français

        Returns:
            dict avec sentiment_predit, label, scores de confiance et texte nettoyé
        """
        if not self._initialise:
            self.charger()

        try:
            texte_nettoye = nettoyer_commentaire(texte)
            if not texte_nettoye:
                raise ValueError("Le commentaire est vide après nettoyage.")

            encodage = self.tokeniseur(
                texte_nettoye,
                max_length     = MAX_TOKENS,
                padding        = "max_length",
                truncation     = True,
                return_tensors = "pt"
            )

            input_ids      = encodage["input_ids"].to(self.device)
            attention_mask = encodage["attention_mask"].to(self.device)

            with torch.no_grad():
                sorties = self.modele(input_ids=input_ids, attention_mask=attention_mask)

            # Conversion en probabilités via softmax
            probabilites = F.softmax(sorties.logits, dim=1).squeeze().tolist()
            classe_predite = int(torch.argmax(sorties.logits, dim=1).item())

            return {
                "texte_original"  : texte,
                "texte_nettoye"   : texte_nettoye,
                "sentiment_predit": classe_predite,
                "label_sentiment" : LABELS[classe_predite],
                "score_negatif"   : round(probabilites[0], 4),
                "score_neutre"    : round(probabilites[1], 4),
                "score_positif"   : round(probabilites[2], 4),
            }

        except Exception as e:
            print(f"[ERREUR] Prédiction : {e}")
            raise


# Instance globale partagée dans toute l'application
service_prediction = ServicePrediction()

# =============================================================================
# Fichier : api_client.py
# Rôle    : Fonctions de communication entre le dashboard Streamlit et
#           l'API FastAPI. Centralise tous les appels HTTP.
# =============================================================================

import requests

API_BASE = "http://localhost:8000/api"
TIMEOUT  = 30  # secondes


def analyser_commentaire(texte: str, matiere: str = None) -> dict | None:
    """Envoie un commentaire à l'API et retourne la prédiction."""
    try:
        payload = {"texte": texte}
        if matiere:
            payload["matiere"] = matiere
        reponse = requests.post(f"{API_BASE}/predict", json=payload, timeout=TIMEOUT)
        reponse.raise_for_status()
        return reponse.json()
    except requests.exceptions.ConnectionError:
        return {"erreur": "Impossible de joindre l'API. Vérifiez que le serveur est démarré."}
    except Exception as e:
        return {"erreur": str(e)}


def obtenir_commentaires(limite=200, offset=0, matiere=None, sentiment=None) -> dict | None:
    """Récupère la liste des commentaires avec filtres optionnels."""
    try:
        params = {"limite": limite, "offset": offset}
        if matiere:
            params["matiere"] = matiere
        if sentiment is not None:
            params["sentiment"] = sentiment
        reponse = requests.get(f"{API_BASE}/commentaires", params=params, timeout=TIMEOUT)
        reponse.raise_for_status()
        return reponse.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def obtenir_statistiques() -> dict | None:
    """Récupère les statistiques globales depuis l'API."""
    try:
        reponse = requests.get(f"{API_BASE}/stats", timeout=TIMEOUT)
        reponse.raise_for_status()
        return reponse.json()
    except Exception:
        return None


def supprimer_commentaire(commentaire_id: int) -> bool:
    """Supprime un commentaire par son ID. Retourne True si succès."""
    try:
        reponse = requests.delete(f"{API_BASE}/commentaires/{commentaire_id}", timeout=TIMEOUT)
        return reponse.status_code == 200
    except Exception:
        return False


def verifier_api() -> bool:
    """Vérifie que l'API est accessible."""
    try:
        reponse = requests.get("http://localhost:8000/health", timeout=5)
        return reponse.status_code == 200
    except Exception:
        return False

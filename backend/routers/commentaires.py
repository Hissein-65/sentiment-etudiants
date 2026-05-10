# =============================================================================
# Fichier : commentaires.py
# Rôle    : Définit toutes les routes (endpoints) de l'API REST.
#           Routes disponibles :
#             POST /api/predict          → Analyser un commentaire
#             GET  /api/commentaires     → Lister tous les commentaires
#             GET  /api/commentaires/{id}→ Détail d'un commentaire
#             GET  /api/stats            → Statistiques globales
#             DELETE /api/commentaires/{id} → Supprimer un commentaire
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.database import get_db
from backend.models.modeles_db import Commentaire
from backend.services.prediction_service import service_prediction

router = APIRouter(prefix="/api", tags=["Commentaires"])


# ── Schémas Pydantic (validation des données entrantes/sortantes) ─────────────

class RequetePrediction(BaseModel):
    """Corps de la requête POST /api/predict"""
    texte   : str            = Field(..., min_length=5, max_length=2000,
                                     description="Commentaire étudiant à analyser")
    matiere : Optional[str]  = Field(None, max_length=100,
                                     description="Matière concernée (optionnel)")

class ReponseCommentaire(BaseModel):
    """Schéma de réponse pour un commentaire analysé"""
    id               : int
    texte_original   : str
    matiere          : Optional[str]
    sentiment_predit : int
    label_sentiment  : str
    scores           : dict
    date_creation    : Optional[str]

    class Config:
        from_attributes = True


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/predict", response_model=ReponseCommentaire, summary="Analyser un commentaire")
def predire_sentiment(requete: RequetePrediction, db: Session = Depends(get_db)):
    """
    Analyse le sentiment d'un commentaire étudiant et le sauvegarde en base.

    - **texte** : Le commentaire à analyser (5 à 2000 caractères)
    - **matiere** : La matière concernée (optionnel)

    Retourne le sentiment prédit (0=Négatif, 1=Neutre, 2=Positif) et les scores.
    """
    try:
        resultat = service_prediction.predict(requete.texte)

        nouveau = Commentaire(
            texte_original   = resultat["texte_original"],
            texte_nettoye    = resultat["texte_nettoye"],
            matiere          = requete.matiere,
            sentiment_predit = resultat["sentiment_predit"],
            label_sentiment  = resultat["label_sentiment"],
            score_negatif    = resultat["score_negatif"],
            score_neutre     = resultat["score_neutre"],
            score_positif    = resultat["score_positif"],
        )
        db.add(nouveau)
        db.commit()
        db.refresh(nouveau)

        return nouveau.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")


@router.get("/commentaires", summary="Lister les commentaires")
def lister_commentaires(
    limite  : int = 50,
    offset  : int = 0,
    matiere : Optional[str] = None,
    sentiment : Optional[int] = None,
    db      : Session = Depends(get_db)
):
    """
    Retourne la liste des commentaires analysés.

    Filtres optionnels :
    - **matiere** : Filtrer par matière
    - **sentiment** : Filtrer par classe (0, 1 ou 2)
    - **limite** : Nombre max de résultats (défaut 50)
    - **offset** : Décalage pour la pagination
    """
    try:
        query = db.query(Commentaire)
        if matiere:
            query = query.filter(Commentaire.matiere == matiere)
        if sentiment is not None:
            query = query.filter(Commentaire.sentiment_predit == sentiment)

        total = query.count()
        commentaires = query.order_by(Commentaire.date_creation.desc()) \
                            .offset(offset).limit(limite).all()

        return {
            "total"        : total,
            "limite"       : limite,
            "offset"       : offset,
            "commentaires" : [c.to_dict() for c in commentaires]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commentaires/{commentaire_id}", summary="Détail d'un commentaire")
def obtenir_commentaire(commentaire_id: int, db: Session = Depends(get_db)):
    """Retourne le détail complet d'un commentaire par son ID."""
    commentaire = db.query(Commentaire).filter(Commentaire.id == commentaire_id).first()
    if not commentaire:
        raise HTTPException(status_code=404, detail="Commentaire introuvable.")
    return commentaire.to_dict()


@router.get("/stats", summary="Statistiques globales")
def obtenir_statistiques(db: Session = Depends(get_db)):
    """
    Retourne les statistiques globales sur les commentaires analysés :
    total, répartition par sentiment, et répartition par matière.
    """
    try:
        total = db.query(Commentaire).count()

        if total == 0:
            return {"total": 0, "message": "Aucun commentaire analysé pour l'instant."}

        # Répartition par sentiment
        par_sentiment = db.query(
            Commentaire.label_sentiment,
            func.count(Commentaire.id).label("nombre")
        ).group_by(Commentaire.label_sentiment).all()

        # Répartition par matière
        par_matiere = db.query(
            Commentaire.matiere,
            func.count(Commentaire.id).label("nombre")
        ).filter(Commentaire.matiere != None) \
         .group_by(Commentaire.matiere) \
         .order_by(func.count(Commentaire.id).desc()).all()

        # Score moyen de confiance
        scores_moy = db.query(
            func.avg(Commentaire.score_negatif).label("moy_negatif"),
            func.avg(Commentaire.score_neutre).label("moy_neutre"),
            func.avg(Commentaire.score_positif).label("moy_positif"),
        ).first()

        return {
            "total": total,
            "par_sentiment": [
                {"label": row.label_sentiment, "nombre": row.nombre,
                 "pourcentage": round(row.nombre / total * 100, 1)}
                for row in par_sentiment
            ],
            "par_matiere": [
                {"matiere": row.matiere or "Non spécifiée", "nombre": row.nombre}
                for row in par_matiere
            ],
            "scores_moyens": {
                "negatif": round(float(scores_moy.moy_negatif or 0), 4),
                "neutre" : round(float(scores_moy.moy_neutre  or 0), 4),
                "positif": round(float(scores_moy.moy_positif or 0), 4),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/commentaires/{commentaire_id}", summary="Supprimer un commentaire")
def supprimer_commentaire(commentaire_id: int, db: Session = Depends(get_db)):
    """Supprime un commentaire de la base de données par son ID."""
    commentaire = db.query(Commentaire).filter(Commentaire.id == commentaire_id).first()
    if not commentaire:
        raise HTTPException(status_code=404, detail="Commentaire introuvable.")
    try:
        db.delete(commentaire)
        db.commit()
        return {"message": f"Commentaire {commentaire_id} supprimé avec succès."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Fichier : modeles_db.py
# Rôle    : Définit les tables PostgreSQL via SQLAlchemy ORM.
#           Table principale : commentaires (texte + sentiment prédit + meta)
# =============================================================================

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Commentaire(Base):
    """
    Table 'commentaires' : stocke chaque commentaire soumis avec sa prédiction.
    """
    __tablename__ = "commentaires"

    id              = Column(Integer, primary_key=True, index=True, autoincrement=True)
    texte_original  = Column(Text,    nullable=False)
    texte_nettoye   = Column(Text,    nullable=True)
    matiere         = Column(String(100), nullable=True)
    sentiment_predit = Column(Integer, nullable=False)      # 0, 1 ou 2
    label_sentiment  = Column(String(20), nullable=False)   # "Négatif", "Neutre", "Positif"
    score_negatif   = Column(Float, nullable=True)          # probabilité classe 0
    score_neutre    = Column(Float, nullable=True)          # probabilité classe 1
    score_positif   = Column(Float, nullable=True)          # probabilité classe 2
    date_creation   = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id"              : self.id,
            "texte_original"  : self.texte_original,
            "matiere"         : self.matiere,
            "sentiment_predit": self.sentiment_predit,
            "label_sentiment" : self.label_sentiment,
            "scores"          : {
                "negatif" : round(self.score_negatif or 0, 4),
                "neutre"  : round(self.score_neutre  or 0, 4),
                "positif" : round(self.score_positif or 0, 4),
            },
            "date_creation"   : self.date_creation.isoformat() if self.date_creation else None,
        }

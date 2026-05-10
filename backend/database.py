# =============================================================================
# Fichier : database.py
# Rôle    : Connexion à PostgreSQL via SQLAlchemy. Fournit le moteur (engine),
#           la session et la fonction de dépendance FastAPI get_db().
# =============================================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de connexion PostgreSQL
DATABASE_URL = "postgresql://postgres:admin123@localhost:5432/sentiment_etudiants"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("[OK] Connexion PostgreSQL initialisée.")
except Exception as e:
    print(f"[ERREUR] Connexion base de données : {e}")
    raise


def get_db():
    """
    Dépendance FastAPI : ouvre une session DB par requête et la ferme après.
    Utilisation dans les routes : db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def creer_tables():
    """Crée toutes les tables définies dans les modèles si elles n'existent pas."""
    try:
        from backend.models.modeles_db import Base as ModelBase
        ModelBase.metadata.create_all(bind=engine)
        print("[OK] Tables créées (ou déjà existantes).")
    except Exception as e:
        print(f"[ERREUR] Création des tables : {e}")
        raise

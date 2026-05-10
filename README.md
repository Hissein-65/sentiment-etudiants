# Système d'Analyse de Sentiments des Commentaires Étudiants

> Projet de Fin d'Études (PFE) — Intelligence Artificielle & NLP  
> Modèle CamemBERT fine-tuné pour l'analyse de sentiments en français

---

## Description

Ce projet implémente un système complet d'analyse de sentiments pour les commentaires d'étudiants sur leurs cours. Il utilise le modèle de langage **CamemBERT** (BERT adapté au français) pour classer automatiquement chaque commentaire en :

- 😞 **Négatif** (0)
- 😐 **Neutre** (1)
- 😊 **Positif** (2)

## Architecture du projet

```
sentiment_etudiants/
├── datasets/                    # Données d'entraînement (225 commentaires)
├── ai_model/                    # Modèle CamemBERT + entraînement
├── backend/                     # API REST FastAPI
├── dashboard/                   # Tableau de bord Streamlit
└── mobile_app/                  # Application mobile Flutter
```

## Technologies utilisées

| Composant | Technologie |
|-----------|-------------|
| Modèle IA | CamemBERT (HuggingFace) + PyTorch |
| API Backend | FastAPI + SQLAlchemy |
| Base de données | PostgreSQL |
| Dashboard | Streamlit + Plotly |
| Application mobile | Flutter (Dart) |

## Installation

### Prérequis
- Python 3.10+
- PostgreSQL 14+
- Flutter SDK
- Android Studio (pour l'émulateur)

### 1. Cloner le dépôt

```bash
git clone https://github.com/Hissein-65/sentiment-etudiants.git
cd sentiment-etudiants
```

### 2. Créer l'environnement Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install torch transformers sentencepiece fastapi uvicorn sqlalchemy psycopg2-binary streamlit plotly requests python-docx
```

### 3. Configurer la base de données PostgreSQL

```bash
sudo -u postgres psql -c "CREATE DATABASE sentiment_etudiants;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'admin123';"
```

### 4. Télécharger le modèle entraîné

Le modèle fine-tuné (fichiers `.bin` > 400 MB) n'est pas inclus dans ce dépôt.  
Pour l'entraîner vous-même :

```bash
cd ~/sentiment_etudiants
source venv/bin/activate
python -m ai_model.entrainement
```

### 5. Installer les dépendances Flutter

```bash
cd mobile_app
flutter pub get
```

## Lancement

### Étape 1 — Démarrer PostgreSQL

```bash
sudo service postgresql start
```

### Étape 2 — Lancer l'API FastAPI

```bash
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API disponible sur : `http://localhost:8000`  
Documentation interactive : `http://localhost:8000/docs`

### Étape 3 — Lancer le Dashboard Streamlit

```bash
source venv/bin/activate
streamlit run dashboard/app.py
```

Dashboard disponible sur : `http://localhost:8501`

### Étape 4 — Lancer l'application Flutter

```bash
cd mobile_app
flutter run
```

## Endpoints de l'API

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/predict` | Analyser un commentaire |
| GET | `/api/commentaires` | Lister les commentaires |
| GET | `/api/stats` | Statistiques globales |
| DELETE | `/api/commentaires/{id}` | Supprimer un commentaire |
| GET | `/health` | Vérifier l'état du serveur |

## Résultats du modèle

- Dataset : 225 commentaires (75 par classe)
- Précision globale : ~79% sur le jeu de test
- Modèle de base : `camembert-base` (CamemBERT)
- Fine-tuning : 3 epochs, lr=2e-5, batch=16

## Auteur

**Hissein Nasser** — PFE en Intelligence Artificielle

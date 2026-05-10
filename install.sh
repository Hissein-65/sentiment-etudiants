#!/bin/bash
# =============================================================================
# Script d'installation complet — Projet Analyse de Sentiments Étudiants
# Installe : Flutter, Android Studio, PostgreSQL, venv Python + librairies IA
# Auteur : généré automatiquement
# Usage  : bash install.sh
# =============================================================================

set -e  # Arrêter si une commande échoue

# Couleurs pour l'affichage
VERT='\033[0;32m'
BLEU='\033[0;34m'
JAUNE='\033[1;33m'
ROUGE='\033[0;31m'
NC='\033[0m' # Pas de couleur

ok()   { echo -e "${VERT}[OK]${NC} $1"; }
info() { echo -e "${BLEU}[INFO]${NC} $1"; }
etape(){ echo -e "\n${JAUNE}====== $1 ======${NC}"; }

# =============================================================================
# ÉTAPE 4 — FLUTTER + DART
# =============================================================================
etape "ÉTAPE 4 : Flutter + Dart"

info "Installation des dépendances système..."
sudo apt update -qq
sudo apt install -y curl unzip xz-utils zip libglu1-mesa clang cmake ninja-build pkg-config libgtk-3-dev
ok "Dépendances installées"

FLUTTER_DIR="$HOME/Documents/flutter"

if [ -d "$FLUTTER_DIR" ]; then
    ok "Flutter déjà présent dans $FLUTTER_DIR — on passe"
else
    info "Téléchargement de Flutter (peut prendre quelques minutes)..."
    cd "$HOME/Documents"
    FLUTTER_URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.5-stable.tar.xz"
    wget -q --show-progress "$FLUTTER_URL" -O flutter_stable.tar.xz
    info "Extraction de Flutter..."
    tar xf flutter_stable.tar.xz
    rm flutter_stable.tar.xz
    ok "Flutter extrait dans $FLUTTER_DIR"
fi

# Ajouter Flutter au PATH si pas déjà présent
if ! grep -q 'flutter/bin' "$HOME/.bashrc"; then
    echo '' >> "$HOME/.bashrc"
    echo '# Flutter SDK' >> "$HOME/.bashrc"
    echo 'export PATH="$HOME/Documents/flutter/bin:$PATH"' >> "$HOME/.bashrc"
    ok "Flutter ajouté au PATH dans .bashrc"
else
    ok "Flutter déjà dans le PATH"
fi

export PATH="$HOME/Documents/flutter/bin:$PATH"

info "Vérification Flutter..."
flutter --version | head -1
ok "Flutter installé avec succès"

# =============================================================================
# ÉTAPE 5 — ANDROID STUDIO
# =============================================================================
etape "ÉTAPE 5 : Android Studio"

STUDIO_DIR="/opt/android-studio"

if [ -d "$STUDIO_DIR" ]; then
    ok "Android Studio déjà installé dans $STUDIO_DIR — on passe"
else
    info "Téléchargement d'Android Studio (environ 1 Go, patience)..."
    cd "$HOME/Téléchargements"
    STUDIO_URL="https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.2.1.11/android-studio-2024.2.1.11-linux.tar.gz"
    wget -q --show-progress "$STUDIO_URL" -O android-studio.tar.gz
    info "Extraction vers /opt..."
    sudo tar -xzf android-studio.tar.gz -C /opt
    rm android-studio.tar.gz
    ok "Android Studio extrait dans $STUDIO_DIR"
fi

# Ajouter Android SDK au PATH si pas déjà présent
if ! grep -q 'ANDROID_HOME' "$HOME/.bashrc"; then
    echo '' >> "$HOME/.bashrc"
    echo '# Android SDK' >> "$HOME/.bashrc"
    echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> "$HOME/.bashrc"
    echo 'export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH"' >> "$HOME/.bashrc"
    ok "Android SDK ajouté au PATH"
else
    ok "Android SDK déjà dans le PATH"
fi

echo ""
echo -e "${JAUNE}[ACTION MANUELLE]${NC} Lance Android Studio pour finaliser le SDK :"
echo -e "  ${BLEU}/opt/android-studio/bin/studio.sh &${NC}"
echo "  → Choisis 'Standard', accepte les licences, attends la fin du téléchargement SDK"

# =============================================================================
# ÉTAPE 6 — POSTGRESQL
# =============================================================================
etape "ÉTAPE 6 : PostgreSQL"

info "Installation de PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
ok "PostgreSQL démarré et activé au démarrage"

info "Configuration du mot de passe et de la base de données..."
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'admin123';" 2>/dev/null && ok "Mot de passe postgres défini : admin123"
sudo -u postgres psql -c "CREATE DATABASE sentiment_etudiants;" 2>/dev/null && ok "Base 'sentiment_etudiants' créée" || echo "  (base déjà existante, ignoré)"

info "Vérification de la connexion..."
PGPASSWORD=admin123 psql -U postgres -c "\l" | grep sentiment_etudiants && ok "Connexion PostgreSQL OK" || echo "Connexion à vérifier"

# =============================================================================
# ÉTAPE 7 — VENV PYTHON + LIBRAIRIES IA
# =============================================================================
etape "ÉTAPE 7 : Environnement Python (venv + librairies)"

PROJET="$HOME/Documents/sentiment_etudiants"
VENV="$PROJET/venv"

info "Création du venv dans $VENV..."
python3 -m venv "$VENV"
ok "venv créé"

info "Activation du venv et mise à jour de pip..."
source "$VENV/bin/activate"
pip install --upgrade pip -q
ok "pip à jour"

info "Installation de PyTorch (version CPU)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q
ok "PyTorch installé"

info "Installation des librairies NLP et backend..."
pip install -q \
    transformers==4.40.0 \
    datasets \
    scikit-learn \
    pandas \
    numpy \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    psycopg2-binary \
    alembic \
    streamlit \
    plotly \
    python-dotenv \
    pydantic \
    httpx \
    pytest
ok "Toutes les librairies installées"

info "Vérification des imports clés..."
python -c "import transformers; print('  transformers :', transformers.__version__)"
python -c "import torch;         print('  torch        :', torch.__version__)"
python -c "import fastapi;       print('  fastapi      : OK')"
python -c "import streamlit;     print('  streamlit    : OK')"
python -c "import psycopg2;      print('  psycopg2     : OK')"
python -c "import sklearn;       print('  scikit-learn : OK')"

deactivate

# =============================================================================
# RÉSUMÉ FINAL
# =============================================================================
echo ""
echo -e "${VERT}╔══════════════════════════════════════════════╗${NC}"
echo -e "${VERT}║         INSTALLATION TERMINÉE !              ║${NC}"
echo -e "${VERT}╠══════════════════════════════════════════════╣${NC}"
echo -e "${VERT}║ ✅ Flutter + Dart                            ║${NC}"
echo -e "${VERT}║ ✅ Android Studio (extraction)               ║${NC}"
echo -e "${VERT}║    ⚠️  Ouvre Studio manuellement (SDK)        ║${NC}"
echo -e "${VERT}║ ✅ PostgreSQL (db: sentiment_etudiants)      ║${NC}"
echo -e "${VERT}║ ✅ venv Python + librairies IA               ║${NC}"
echo -e "${VERT}╠══════════════════════════════════════════════╣${NC}"
echo -e "${VERT}║ Active ton venv avec :                       ║${NC}"
echo -e "${VERT}║  source ~/Documents/sentiment_etudiants/    ║${NC}"
echo -e "${VERT}║         venv/bin/activate                    ║${NC}"
echo -e "${VERT}╚══════════════════════════════════════════════╝${NC}"

echo ""
echo "Recharge ton terminal : source ~/.bashrc"

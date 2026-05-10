# =============================================================================
# Fichier : app.py
# Rôle    : Page d'accueil du dashboard Streamlit. Point d'entrée principal.
#           Lancement : streamlit run dashboard/app.py
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from dashboard.components.api_client import verifier_api, obtenir_statistiques

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title = "Analyse de Sentiments Étudiants",
    page_icon  = "🎓",
    layout     = "wide",
    initial_sidebar_state = "expanded"
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    .titre-hero {
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(135deg, #1F497D, #2E74B5);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 1rem 0;
    }
    .sous-titre-hero {
        font-size: 1.15rem; color: #555; text-align: center;
        margin-bottom: 2rem;
    }
    .carte-stat {
        background: white; border-radius: 12px; padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center;
    }
    .carte-stat h2 { font-size: 2.2rem; margin: 0; }
    .carte-stat p  { color: #666; margin: 0; font-size: 0.95rem; }
    .badge-positif { background:#E8F8F0; color:#1F8A70;
                     padding:4px 12px; border-radius:20px; font-weight:600; }
    .badge-neutre  { background:#FFF9E0; color:#B7950B;
                     padding:4px 12px; border-radius:20px; font-weight:600; }
    .badge-negatif { background:#FFE8E8; color:#C0392B;
                     padding:4px 12px; border-radius:20px; font-weight:600; }
    .statut-ok  { background:#E8F8F0; color:#1F8A70; padding:6px 16px;
                  border-radius:8px; font-weight:600; display:inline-block; }
    .statut-ko  { background:#FFE8E8; color:#C0392B; padding:6px 16px;
                  border-radius:8px; font-weight:600; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown('<div class="titre-hero">🎓 Analyse de Sentiments Étudiants</div>', unsafe_allow_html=True)
st.markdown('<div class="sous-titre-hero">Système d\'analyse automatique des commentaires étudiants par Intelligence Artificielle (CamemBERT)</div>', unsafe_allow_html=True)
st.divider()

# ── Statut de l'API ───────────────────────────────────────────────────────────
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    api_ok = verifier_api()
    if api_ok:
        st.markdown('<div class="statut-ok">✅ API connectée — Modèle CamemBERT opérationnel</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="statut-ko">❌ API non joignable — Démarrez le serveur FastAPI</div>', unsafe_allow_html=True)
        st.code("uvicorn backend.main:app --port 8000", language="bash")

st.markdown("##")

# ── Cartes de statistiques rapides ───────────────────────────────────────────
stats = obtenir_statistiques() if api_ok else None

col1, col2, col3, col4 = st.columns(4)

total = stats.get("total", 0) if stats else 0

nb_pos = nb_neu = nb_neg = 0
if stats and stats.get("par_sentiment"):
    for s in stats["par_sentiment"]:
        if s["label"] == "Positif":  nb_pos = s["nombre"]
        if s["label"] == "Neutre":   nb_neu = s["nombre"]
        if s["label"] == "Négatif":  nb_neg = s["nombre"]

with col1:
    st.markdown(f"""
    <div class="carte-stat">
        <h2>📊 {total}</h2>
        <p>Commentaires analysés</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="carte-stat">
        <h2 style="color:#1F8A70">😊 {nb_pos}</h2>
        <p>Commentaires positifs</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="carte-stat">
        <h2 style="color:#B7950B">😐 {nb_neu}</h2>
        <p>Commentaires neutres</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="carte-stat">
        <h2 style="color:#C0392B">😞 {nb_neg}</h2>
        <p>Commentaires négatifs</p>
    </div>""", unsafe_allow_html=True)

st.markdown("##")
st.divider()

# ── Présentation des pages ────────────────────────────────────────────────────
st.markdown("### 📌 Navigation")
st.markdown("Utilise le **menu latéral gauche** pour naviguer entre les pages :")
st.markdown("##")

col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    st.markdown("""
    ### 🔍 Analyse
    Soumets un commentaire étudiant et obtiens instantanément :
    - La classe de sentiment (Positif / Neutre / Négatif)
    - Les scores de confiance pour chaque classe
    - Une jauge visuelle du résultat
    """)

with col_p2:
    st.markdown("""
    ### 📈 Statistiques
    Explore les données avec des graphiques interactifs :
    - Répartition des sentiments (camembert)
    - Distribution par matière (barres)
    - Scores moyens de confiance
    """)

with col_p3:
    st.markdown("""
    ### 📋 Historique
    Consulte tous les commentaires analysés :
    - Filtrage par matière et par sentiment
    - Tableau complet avec scores
    - Suppression individuelle
    """)

# ── Pied de page ──────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.85rem;'>"
    "Projet PFE — Analyse de Sentiments Étudiants · Modèle : CamemBERT · Backend : FastAPI · Dashboard : Streamlit"
    "</div>",
    unsafe_allow_html=True
)

# =============================================================================
# Fichier : pages/1_Analyse.py
# Rôle    : Page d'analyse de sentiment. Permet de soumettre un commentaire
#           et d'afficher la prédiction du modèle CamemBERT avec les scores.
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import plotly.graph_objects as go
from dashboard.components.api_client import analyser_commentaire, verifier_api

st.set_page_config(page_title="Analyse", page_icon="🔍", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .resultat-positif {
        background: linear-gradient(135deg, #E8F8F0, #D5F5E3);
        border-left: 5px solid #1F8A70; border-radius: 10px;
        padding: 1.5rem; margin: 1rem 0;
    }
    .resultat-neutre {
        background: linear-gradient(135deg, #FFF9E0, #FEF9CD);
        border-left: 5px solid #F1C40F; border-radius: 10px;
        padding: 1.5rem; margin: 1rem 0;
    }
    .resultat-negatif {
        background: linear-gradient(135deg, #FFE8E8, #FADBD8);
        border-left: 5px solid #E74C3C; border-radius: 10px;
        padding: 1.5rem; margin: 1rem 0;
    }
    .label-sentiment { font-size: 2rem; font-weight: 800; margin: 0; }
    .score-chip {
        display: inline-block; padding: 4px 14px;
        border-radius: 20px; font-weight: 600; font-size: 0.9rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.title("🔍 Analyse de Sentiment")
st.markdown("Saisit un commentaire étudiant et le modèle **CamemBERT** va analyser son sentiment automatiquement.")
st.divider()

# ── Vérification API ──────────────────────────────────────────────────────────
if not verifier_api():
    st.error("❌ L'API n'est pas accessible. Démarrez d'abord le serveur FastAPI.")
    st.code("uvicorn backend.main:app --port 8000", language="bash")
    st.stop()

# ── Formulaire de saisie ──────────────────────────────────────────────────────
MATIERES = [
    "— Sélectionner —", "Mathématiques", "Informatique", "Physique",
    "Algorithmique", "Base de données", "Réseaux", "Statistiques",
    "Intelligence artificielle", "Programmation", "Autre"
]

col_form, col_aide = st.columns([2, 1])

with col_form:
    commentaire = st.text_area(
        "💬 Commentaire de l'étudiant",
        placeholder="Ex : Ce cours est excellent, le professeur explique très bien...",
        height=150,
        max_chars=2000
    )
    matiere_selectionnee = st.selectbox("📚 Matière concernée (optionnel)", MATIERES)
    matiere = None if matiere_selectionnee == "— Sélectionner —" else matiere_selectionnee

    col_btn, col_nb = st.columns([1, 2])
    with col_btn:
        analyser = st.button("🚀 Analyser", type="primary", use_container_width=True)
    with col_nb:
        st.caption(f"**{len(commentaire)}/2000** caractères")

with col_aide:
    st.markdown("##### 💡 Conseils")
    st.info(
        "**Exemples à tester :**\n\n"
        "😊 *Ce cours est excellent, j'ai beaucoup appris !*\n\n"
        "😐 *Le cours est correct, rien de particulier.*\n\n"
        "😞 *Je suis très déçu, le professeur ne répond jamais.*"
    )

# ── Résultat ──────────────────────────────────────────────────────────────────
if analyser:
    if len(commentaire.strip()) < 5:
        st.warning("⚠️ Le commentaire doit contenir au moins 5 caractères.")
    else:
        with st.spinner("🤖 Analyse en cours..."):
            resultat = analyser_commentaire(commentaire, matiere)

        if not resultat or "erreur" in resultat:
            st.error(f"❌ Erreur : {resultat.get('erreur', 'Erreur inconnue')}")
        else:
            st.markdown("---")
            st.markdown("### 📊 Résultat de l'analyse")

            sentiment = resultat["sentiment_predit"]
            label     = resultat["label_sentiment"]
            s_neg     = resultat["scores"]["negatif"]
            s_neu     = resultat["scores"]["neutre"]
            s_pos     = resultat["scores"]["positif"]

            # Carte de résultat colorée
            classes_css = {0: "resultat-negatif", 1: "resultat-neutre", 2: "resultat-positif"}
            emojis      = {0: "😞", 1: "😐", 2: "😊"}
            css_class   = classes_css[sentiment]

            st.markdown(f"""
            <div class="{css_class}">
                <p class="label-sentiment">{emojis[sentiment]} {label}</p>
                <p style="color:#555; margin-top:0.5rem;">
                    <strong>Matière :</strong> {matiere or 'Non spécifiée'} &nbsp;|&nbsp;
                    <strong>ID :</strong> #{resultat.get('id', '—')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Graphique des scores de confiance
            col_g1, col_g2 = st.columns([1, 1])

            with col_g1:
                fig_bar = go.Figure(go.Bar(
                    x=["Négatif 😞", "Neutre 😐", "Positif 😊"],
                    y=[s_neg * 100, s_neu * 100, s_pos * 100],
                    marker_color=["#E74C3C", "#F1C40F", "#1F8A70"],
                    text=[f"{s_neg*100:.1f}%", f"{s_neu*100:.1f}%", f"{s_pos*100:.1f}%"],
                    textposition="outside"
                ))
                fig_bar.update_layout(
                    title="Scores de confiance par classe",
                    yaxis_title="Probabilité (%)",
                    yaxis=dict(range=[0, 110]),
                    plot_bgcolor="white",
                    height=350,
                    showlegend=False,
                    margin=dict(t=50, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_g2:
                # Jauge de confiance pour la classe prédite
                score_gagnant = [s_neg, s_neu, s_pos][sentiment]
                couleurs_jauge = {0: "#E74C3C", 1: "#F1C40F", 2: "#1F8A70"}

                fig_gauge = go.Figure(go.Indicator(
                    mode  = "gauge+number+delta",
                    value = score_gagnant * 100,
                    title = {"text": f"Confiance — {label}"},
                    number= {"suffix": "%", "font": {"size": 36}},
                    gauge = {
                        "axis": {"range": [0, 100], "tickwidth": 1},
                        "bar" : {"color": couleurs_jauge[sentiment]},
                        "steps": [
                            {"range": [0,  33], "color": "#FADBD8"},
                            {"range": [33, 66], "color": "#FEF9CD"},
                            {"range": [66, 100],"color": "#D5F5E3"},
                        ],
                        "threshold": {
                            "line": {"color": "#333", "width": 3},
                            "thickness": 0.8,
                            "value": score_gagnant * 100
                        }
                    }
                ))
                fig_gauge.update_layout(height=350, margin=dict(t=60, b=20, l=30, r=30))
                st.plotly_chart(fig_gauge, use_container_width=True)

            # Tableau récap
            st.markdown("##### 📋 Détails complets")
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.metric("😞 Score Négatif",  f"{s_neg*100:.1f}%")
            col_d2.metric("😐 Score Neutre",   f"{s_neu*100:.1f}%")
            col_d3.metric("😊 Score Positif",  f"{s_pos*100:.1f}%")

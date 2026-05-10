# =============================================================================
# Fichier : pages/2_Statistiques.py
# Rôle    : Page de visualisation des statistiques globales.
#           Affiche camembert, barres par matière, scores moyens.
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dashboard.components.api_client import obtenir_statistiques, obtenir_commentaires, verifier_api

st.set_page_config(page_title="Statistiques", page_icon="📈", layout="wide")

st.title("📈 Statistiques Globales")
st.markdown("Visualisation des sentiments analysés sur l'ensemble des commentaires étudiants.")
st.divider()

# ── Vérification API ──────────────────────────────────────────────────────────
if not verifier_api():
    st.error("❌ L'API n'est pas accessible. Démarrez d'abord le serveur FastAPI.")
    st.stop()

stats = obtenir_statistiques()
data  = obtenir_commentaires(limite=500)

if not stats or stats.get("total", 0) == 0:
    st.info("📭 Aucun commentaire analysé pour l'instant. Rendez-vous sur la page **Analyse** pour en soumettre.")
    st.stop()

total = stats["total"]

# ── KPIs ──────────────────────────────────────────────────────────────────────
nb_pos = nb_neu = nb_neg = 0
for s in stats.get("par_sentiment", []):
    if s["label"] == "Positif": nb_pos = s["nombre"]
    if s["label"] == "Neutre":  nb_neu = s["nombre"]
    if s["label"] == "Négatif": nb_neg = s["nombre"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total",    total)
col2.metric("😊 Positifs", nb_pos, f"{nb_pos/total*100:.1f}%")
col3.metric("😐 Neutres",  nb_neu, f"{nb_neu/total*100:.1f}%")
col4.metric("😞 Négatifs", nb_neg, f"{nb_neg/total*100:.1f}%")

st.markdown("##")

# ── Graphique 1 : Camembert des sentiments ────────────────────────────────────
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### 🥧 Répartition des sentiments")
    labels  = [s["label"]  for s in stats["par_sentiment"]]
    valeurs = [s["nombre"] for s in stats["par_sentiment"]]
    couleurs_pie = []
    for l in labels:
        if l == "Positif": couleurs_pie.append("#1F8A70")
        elif l == "Neutre": couleurs_pie.append("#F1C40F")
        else: couleurs_pie.append("#E74C3C")

    fig_pie = go.Figure(go.Pie(
        labels=labels,
        values=valeurs,
        marker=dict(colors=couleurs_pie),
        hole=0.4,
        textinfo="label+percent+value",
        textfont_size=13
    ))
    fig_pie.update_layout(
        height=380,
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Graphique 2 : Scores moyens de confiance ──────────────────────────────────
with col_g2:
    st.markdown("#### 🎯 Scores moyens de confiance")
    scores = stats.get("scores_moyens", {})
    noms   = ["Négatif 😞", "Neutre 😐", "Positif 😊"]
    vals   = [
        scores.get("negatif", 0) * 100,
        scores.get("neutre",  0) * 100,
        scores.get("positif", 0) * 100,
    ]
    coul = ["#E74C3C", "#F1C40F", "#1F8A70"]

    fig_scores = go.Figure(go.Bar(
        x=noms, y=vals,
        marker_color=coul,
        text=[f"{v:.1f}%" for v in vals],
        textposition="outside"
    ))
    fig_scores.update_layout(
        yaxis=dict(title="Score moyen (%)", range=[0, 60]),
        plot_bgcolor="white",
        height=380,
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_scores, use_container_width=True)

# ── Graphique 3 : Par matière ─────────────────────────────────────────────────
st.markdown("#### 📚 Commentaires par matière")
matieres_data = stats.get("par_matiere", [])

if matieres_data:
    df_mat = pd.DataFrame(matieres_data)
    df_mat = df_mat.sort_values("nombre", ascending=True)

    fig_mat = go.Figure(go.Bar(
        x=df_mat["nombre"],
        y=df_mat["matiere"],
        orientation="h",
        marker=dict(
            color=df_mat["nombre"],
            colorscale="Blues",
            showscale=True,
            colorbar=dict(title="Nb")
        ),
        text=df_mat["nombre"],
        textposition="outside"
    ))
    fig_mat.update_layout(
        xaxis_title="Nombre de commentaires",
        plot_bgcolor="white",
        height=max(300, len(df_mat) * 45),
        margin=dict(t=20, b=20, l=150, r=60)
    )
    st.plotly_chart(fig_mat, use_container_width=True)

# ── Graphique 4 : Sentiments par matière (détaillé) ───────────────────────────
if data and data.get("commentaires"):
    st.markdown("#### 🔬 Sentiments détaillés par matière")
    df = pd.DataFrame(data["commentaires"])
    df = df[df["matiere"].notna()]

    if not df.empty:
        pivot = df.groupby(["matiere", "label_sentiment"]).size().reset_index(name="count")
        fig_detail = px.bar(
            pivot,
            x="matiere", y="count", color="label_sentiment",
            barmode="group",
            color_discrete_map={"Positif": "#1F8A70", "Neutre": "#F1C40F", "Négatif": "#E74C3C"},
            labels={"matiere": "Matière", "count": "Nombre", "label_sentiment": "Sentiment"},
            height=400
        )
        fig_detail.update_layout(
            plot_bgcolor="white",
            margin=dict(t=20, b=80, l=20, r=20),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_detail, use_container_width=True)

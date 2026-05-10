# =============================================================================
# Fichier : pages/3_Historique.py
# Rôle    : Page historique. Affiche tous les commentaires analysés dans un
#           tableau interactif avec filtres et option de suppression.
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st
import pandas as pd
from dashboard.components.api_client import (
    obtenir_commentaires, supprimer_commentaire, verifier_api
)

st.set_page_config(page_title="Historique", page_icon="📋", layout="wide")

EMOJIS_LABEL  = {"Positif": "😊 Positif", "Neutre": "😐 Neutre", "Négatif": "😞 Négatif"}
COULEURS_BADGE = {
    "Positif": "background:#E8F8F0;color:#1F8A70;padding:3px 10px;border-radius:12px;font-weight:600",
    "Neutre":  "background:#FFF9E0;color:#B7950B;padding:3px 10px;border-radius:12px;font-weight:600",
    "Négatif": "background:#FFE8E8;color:#C0392B;padding:3px 10px;border-radius:12px;font-weight:600",
}
MATIERES_OPTIONS = [
    "Toutes", "Mathématiques", "Informatique", "Physique", "Algorithmique",
    "Base de données", "Réseaux", "Statistiques", "Intelligence artificielle",
    "Programmation", "Autre"
]

st.title("📋 Historique des Commentaires")
st.markdown("Consultez tous les commentaires analysés. Filtrez par matière ou sentiment.")
st.divider()

if not verifier_api():
    st.error("❌ L'API n'est pas accessible. Démarrez d'abord le serveur FastAPI.")
    st.stop()

# ── Filtres ───────────────────────────────────────────────────────────────────
col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
with col_f1:
    filtre_matiere = st.selectbox("📚 Filtrer par matière", MATIERES_OPTIONS)
with col_f2:
    filtre_sentiment = st.selectbox(
        "🎭 Filtrer par sentiment",
        ["Tous", "😊 Positif (2)", "😐 Neutre (1)", "😞 Négatif (0)"]
    )
with col_f3:
    st.markdown("##")
    actualiser = st.button("🔄 Actualiser", use_container_width=True)

# Conversion des filtres
matiere_api   = None if filtre_matiere == "Toutes" else filtre_matiere
sentiment_api = None
if "Positif" in filtre_sentiment: sentiment_api = 2
elif "Neutre" in filtre_sentiment: sentiment_api = 1
elif "Négatif" in filtre_sentiment: sentiment_api = 0

# ── Chargement des données ────────────────────────────────────────────────────
data = obtenir_commentaires(limite=500, matiere=matiere_api, sentiment=sentiment_api)

if not data or data.get("total", 0) == 0:
    st.info("📭 Aucun commentaire trouvé avec ces filtres.")
    st.stop()

commentaires = data["commentaires"]
total_affiche = data["total"]

st.markdown(f"**{total_affiche}** commentaire(s) trouvé(s)")
st.markdown("##")

# ── Tableau ───────────────────────────────────────────────────────────────────
rows = []
for c in commentaires:
    rows.append({
        "ID"           : c["id"],
        "Commentaire"  : c["texte_original"][:90] + ("..." if len(c["texte_original"]) > 90 else ""),
        "Matière"      : c["matiere"] or "—",
        "Sentiment"    : EMOJIS_LABEL.get(c["label_sentiment"], c["label_sentiment"]),
        "Score Positif": f"{c['scores']['positif']*100:.1f}%",
        "Score Neutre" : f"{c['scores']['neutre']*100:.1f}%",
        "Score Négatif": f"{c['scores']['negatif']*100:.1f}%",
        "Date"         : c["date_creation"][:16].replace("T", " ") if c["date_creation"] else "—",
    })

df = pd.DataFrame(rows)
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=min(600, 55 + len(df) * 35),
    column_config={
        "ID"           : st.column_config.NumberColumn("ID", width="small"),
        "Commentaire"  : st.column_config.TextColumn("Commentaire", width="large"),
        "Matière"      : st.column_config.TextColumn("Matière", width="medium"),
        "Sentiment"    : st.column_config.TextColumn("Sentiment", width="medium"),
        "Score Positif": st.column_config.TextColumn("✅ Positif", width="small"),
        "Score Neutre" : st.column_config.TextColumn("⚪ Neutre",  width="small"),
        "Score Négatif": st.column_config.TextColumn("❌ Négatif", width="small"),
        "Date"         : st.column_config.TextColumn("Date", width="medium"),
    }
)

# ── Détail et suppression ─────────────────────────────────────────────────────
st.divider()
st.markdown("#### 🗑️ Supprimer un commentaire")

col_s1, col_s2 = st.columns([1, 3])
with col_s1:
    ids_disponibles = [c["id"] for c in commentaires]
    id_a_supprimer  = st.number_input(
        "ID du commentaire à supprimer",
        min_value=1, step=1, value=ids_disponibles[0] if ids_disponibles else 1
    )
with col_s2:
    st.markdown("##")
    if st.button("🗑️ Supprimer", type="secondary"):
        if id_a_supprimer in ids_disponibles:
            succes = supprimer_commentaire(id_a_supprimer)
            if succes:
                st.success(f"✅ Commentaire #{id_a_supprimer} supprimé.")
                st.rerun()
            else:
                st.error("❌ Impossible de supprimer ce commentaire.")
        else:
            st.warning(f"⚠️ L'ID {id_a_supprimer} n'existe pas dans la liste affichée.")

# ── Export CSV ────────────────────────────────────────────────────────────────
st.divider()
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label     = "📥 Télécharger en CSV",
    data      = csv,
    file_name = "historique_commentaires.csv",
    mime      = "text/csv",
)

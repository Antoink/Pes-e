import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Pesée SDR", page_icon="logo_sdr.png", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    div[data-testid="stFormSubmitButton"] > button { height: 80px; border-radius: 12px; font-size: 28px !important; font-weight: bold; background-color: #d32f2f !important; border: 2px solid #b71c1c !important; width: 100%; color: #ffffff !important; }
    div[data-testid="stFormSubmitButton"] > button:hover { background-color: #b71c1c !important; border-color: #9b0000 !important; }
    h1 { color: #d32f2f !important; font-weight: 900 !important; text-align: center; font-size: 45px; margin-bottom: 0px; }
    h2 { color: #d32f2f !important; font-weight: 800 !important; text-align: center; }
    label { color: #000000 !important; font-weight: bold !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

fichier_poids = "suivi_poids_sdr.csv"
colonnes = ["Date", "Joueur", "Poids (kg)"]

joueurs = [
    "Abdoul KONE", "Adama BOJANG", "Alexandre OLLIERO", "Elie NTAMON", "Ewen JAOUEN", "Hafiz IBRAHIM", 
    "Hiroki SEKINE", "John PATRICK", "Joseph OKUMU", "Keito NAKAMURA", 
    "Martial TIA", "Maxime BUSI", "Mohamed DARAMY", "Mory GBANE", 
    "Nicolas PALLOIS", "ZABI", "Sergio AKIEME", 
    "Soumaila SYLLA", "Theo LEONI", "Thiemoko DIARRA", 
    "Yaya FOFANA", "Samuel KOTTO", "Yassine BENHATTAB", 
    "Tidiane DIARRASSOUBA", "Arone GADOU", "Lenny SYLLA"
]

if not os.path.exists(fichier_poids):
    pd.DataFrame(columns=colonnes).to_csv(fichier_poids, index=False)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if os.path.exists("logo_sdr.png"):
        st.image("logo_sdr.png", use_container_width=True)

st.markdown("<h1>PESÉE DU JOUR</h1>", unsafe_allow_html=True)
st.write("")

with st.form("form_poids", clear_on_submit=True):
    nom_joueur = st.selectbox("Sélectionner le joueur", joueurs)
    poids = st.number_input("Poids (kg)", min_value=0.0, max_value=150.0, step=0.1, format="%.1f")
    
    st.write("")
    submitted = st.form_submit_button("VALIDER")

    if submitted:
        if nom_joueur != "" and poids > 40.0:
            df = pd.read_csv(fichier_poids)
            nouveau_poids = pd.DataFrame([{"Date": str(date.today()), "Joueur": nom_joueur, "Poids (kg)": poids}])
            df = pd.concat([df, nouveau_poids], ignore_index=True)
            df.to_csv(fichier_poids, index=False)
            st.success(f"✅ {nom_joueur} : {poids} kg enregistré avec succès.")
        else:
            st.error("⚠️ Veuillez sélectionner un joueur et entrer un poids valide.")

st.divider()

df_histo = pd.read_csv(fichier_poids)
df_jour = df_histo[df_histo["Date"] == str(date.today())]

with st.expander("Aperçu des pesées du jour"):
    if not df_jour.empty:
        st.dataframe(df_jour.sort_values(by="Joueur"), use_container_width=True, hide_index=True)
        
        with open(fichier_poids, "rb") as f:
            st.download_button("Télécharger tout l'historique (CSV)", f, file_name="historique_poids_sdr.csv", use_container_width=True)
    else:
        st.info("Aucune donnée enregistrée pour le moment.")

st.divider()

st.markdown("<h2>Évolution de la Pesée</h2>", unsafe_allow_html=True)
joueur_evo = st.selectbox("Sélectionner un joueur pour voir son évolution", joueurs, key="evolution")

if joueur_evo != "":
    df_evo = df_histo[df_histo["Joueur"] == joueur_evo].copy()
    if not df_evo.empty:
        df_evo["Date"] = pd.to_datetime(df_evo["Date"]).dt.date
        df_evo = df_evo.sort_values(by="Date")
        
        fig = px.line(df_evo, x="Date", y="Poids (kg)", markers=True, text="Poids (kg)")
        fig.update_traces(textposition="top center", line_color="#d32f2f", marker=dict(size=10, color="#000000"))
        
        min_poids = df_evo["Poids (kg)"].min() - 2
        max_poids = df_evo["Poids (kg)"].max() + 2
        fig.update_layout(
            yaxis=dict(range=[min_poids, max_poids]), 
            hovermode="x unified",
            xaxis_title="",
            xaxis=dict(tickformat="%Y-%m-%d")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée enregistrée pour ce joueur.")

st.divider()

with st.expander("⚙️ Administration avancée (Édition / Suppression)"):
    st.info("Modifiez directement les valeurs dans le tableau ci-dessous, ou sélectionnez une ligne pour la supprimer.")
    
    df_histo["Date"] = pd.to_datetime(df_histo["Date"]).dt.date
    
    edited_df = st.data_editor(df_histo, num_rows="dynamic", use_container_width=True, key="admin_editor", hide_index=True)
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("💾 Sauvegarder les modifications", use_container_width=True):
            edited_df["Date"] = edited_df["Date"].astype(str)
            edited_df.to_csv(fichier_poids, index=False)
            st.success("Base de données mise à jour avec succès !")
            st.rerun()

st.markdown("""
    <br><br>
    <div style='text-align: center; color: #888888; font-size: 12px;'>
        <em>Développé par Antoine Kaczmarek - DÉPARTEMENT PERFORMANCE - Stade de Reims</em>
    </div>
""", unsafe_allow_html=True)

# streamlit run pesee.py
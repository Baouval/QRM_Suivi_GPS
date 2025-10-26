
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="QRM Dashboard Staff", layout="wide", page_icon="⚽")

# --- Logo et titre latéral ---
st.sidebar.image("Logo QRM.png", use_column_width=True)
st.sidebar.title("Tableau de bord QRM")
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio("Aller à :", ["Accueil", "Données GPS", "Bien-être", "RPE", "Alertes", "Comparaisons", "Export"])

# --- Chargement du fichier Excel ---
@st.cache_data
def load_data():
    return pd.read_excel("DATA BRUTES.xlsx")

df = load_data()

# --- Page Accueil ---
if page == "Accueil":
    st.title("⚽ Tableau de bord GPS & Bien-être – QRM Staff")
    st.write("Ce tableau de bord permet de suivre les indicateurs GPS, HID, HSR et bien-être des joueurs du QRM.")
    st.metric("Nombre de joueurs", df["Player Display Name"].nunique())
    st.metric("Nombre de séances", df["Session"].nunique())
    st.metric("Dernière date enregistrée", str(df["Date"].max().date()))

# --- Page Données GPS ---
elif page == "Données GPS":
    st.header("📊 Données GPS")
    joueurs = st.multiselect("Sélectionnez le(s) joueur(s)", df["Player Display Name"].unique())
    if joueurs:
        data = df[df["Player Display Name"].isin(joueurs)]
        fig = px.bar(data, x="Session", y=["Total Distance", "Distance Zone 4 (Absolute)", "Distance Zone 5 (Absolute)"],
                     barmode="group", title="Distances Totales / HID / HSR")
        st.plotly_chart(fig, use_container_width=True)

# --- Page Bien-être ---
elif page == "Bien-être":
    st.header("🧠 Bien-être (1-5)")
    cols = ["Sommeil 1-5", "Fatigue 1-5", "Stress 1-5", "Douleurs 1-5", "Motivation 1-5"]
    data = df.melt(id_vars=["Player Display Name", "Date"], value_vars=cols, var_name="Variable", value_name="Score")
    fig = px.bar(data, x="Date", y="Score", color="Variable", barmode="group", title="Scores de bien-être")
    st.plotly_chart(fig, use_container_width=True)

# --- Page RPE ---
elif page == "RPE":
    st.header("💪 RPE individuel (1-10)")
    fig = px.line(df, x="Date", y="RPE 1-10", color="Player Display Name", title="Évolution du RPE")
    st.plotly_chart(fig, use_container_width=True)

# --- Page Alertes ---
elif page == "Alertes":
    st.header("⚠️ Alertes automatiques")
    df["HSR"] = df["Distance Zone 5 (Absolute)"]
    mean_hsr = df.groupby("Player Display Name")["HSR"].transform("mean")
    alerts = df[df["HSR"] < 0.8 * mean_hsr]
    st.write("Joueurs avec HSR < 80% de leur moyenne :")
    st.dataframe(alerts[["Date", "Player Display Name", "HSR"]])

# --- Page Comparaisons ---
elif page == "Comparaisons":
    st.header("📈 Comparaisons entre joueurs")
    fig = px.box(df, x="Player Display Name", y="Distance Zone 5 (Absolute)", title="Distribution du HSR par joueur")
    st.plotly_chart(fig, use_container_width=True)

# --- Page Export ---
elif page == "Export":
    st.header("⬇️ Export des données")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger les données en CSV", data=csv, file_name="donnees_qrm.csv", mime="text/csv")

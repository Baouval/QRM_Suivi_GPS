
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =============================
# CONFIG + THEME (QRM)
# =============================
st.set_page_config(page_title="QRM — Tableau de bord GPS", layout="wide", page_icon=":soccer:")
QRM_RED    = "#D71920"
QRM_YELLOW = "#FFD100"
QRM_DARK   = "#0B132B"
QRM_LIGHT  = "#F7F7F7"
PALETTE    = [QRM_RED, QRM_YELLOW, "#2ca02c", "#1f77b4", "#9467bd", "#8c564b"]

# =============================
# HELPERS
# =============================
def find_col(df, candidates):
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        for c in cols:
            if cand in c:
                return cols[c]
    return None

def to_datetime_safe(series):
    if series is None:
        return None
    if np.issubdtype(series.dtype, np.datetime64):
        return series
    try:
        return pd.to_datetime(series, errors="coerce")
    except:
        return series

def kpi(title, value, suffix=""):
    st.markdown(f"""
    <div style="background:white;border-left:8px solid {QRM_RED};padding:16px;border-radius:14px;box-shadow:0 2px 10px rgba(0,0,0,0.06)">
      <div style="font-size:13px;color:{QRM_DARK};opacity:0.78">{title}</div>
      <div style="font-size:28px;font-weight:800;color:{QRM_DARK}">{value} {suffix}</div>
    </div>
    """, unsafe_allow_html=True)

def line_card(title, data, x, y, color=QRM_RED, unit="", y_range=None):
    fig = px.line(data, x=x, y=y, markers=True, color_discrete_sequence=[color])
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), title=title, template="plotly_white",
                      title_font=dict(color=QRM_LIGHT), xaxis_title=None, yaxis_title=unit)
    if y_range:
        fig.update_yaxes(range=y_range)
    st.plotly_chart(fig, use_container_width=True)

# =============================
# SIDEBAR — CHARGEMENT & FILTRES
# =============================
st.sidebar.header("Chargement des données")
up = st.sidebar.file_uploader("//Users//valentin//Desktop//QRM//gps//DATA BRUTES.xlsx", type=["csv","xlsx","xls"])
if up is None:
    st.info("Charge un fichier pour commencer. Le tableau détecte automatiquement Joueur, Équipe, Date, Distance, HID (Zone4), HSR (Zone5), etc.")
    st.stop()

def load(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    xls = pd.ExcelFile(file)
    return pd.concat([pd.read_excel(file, sheet_name=s) for s in xls.sheet_names], ignore_index=True)

df = load(up)

# Colonnes
col_player = find_col(df, ["joueur","player","athlete","nom","name"])
col_team   = find_col(df, ["equipe","team","squad","category","groupe"])
col_date   = find_col(df, ["date","jour","day"])
col_distance = find_col(df, ["distance","total distance","km"])
col_hid = find_col(df, ["hid","zone 4","z4","high intensity distance"])
col_hsr = find_col(df, ["hsr","zone 5","z5","high speed running"])
col_vmax = find_col(df, ["vmax","vitesse max","max speed"])
col_accel = find_col(df, ["accel","accelerations"])
col_decel = find_col(df, ["decel","decelerations"])
col_sprint = find_col(df, ["sprint"])

# Etat de forme et RPE
col_sleep   = find_col(df, ["sommeil","sleep"])
col_fatigue = find_col(df, ["fatigue"])
col_pain    = find_col(df, ["douleur","pain"])
col_motiv   = find_col(df, ["motivation"])
col_stress  = find_col(df, ["stress"])
col_rpe     = find_col(df, ["rpe","session rpe","srpe"])

# Dates
if col_date:
    df[col_date] = to_datetime_safe(df[col_date])

# Filtres
if col_team:
    teams = sorted(df[col_team].dropna().astype(str).unique())
    pick_teams = st.sidebar.multiselect("Équipe / Groupe", teams, default=teams[:1] if teams else [])
    if pick_teams:
        df = df[df[col_team].astype(str).isin(pick_teams)]

players = sorted(df[col_player].dropna().astype(str).unique() if col_player else ["—"])
pick_players = st.sidebar.multiselect("Joueurs (pour comparaison)", players, default=players[:1] if players else [])
player_main = pick_players[0] if pick_players else (players[0] if players else "—")

if col_date and df[col_date].notna().any():
    dmin, dmax = df[col_date].min(), df[col_date].max()
    d1, d2 = st.sidebar.date_input("Période", value=(dmin.date(), dmax.date()))
    df = df[(df[col_date] >= pd.to_datetime(d1)) & (df[col_date] <= pd.to_datetime(d2))]

# =============================
# ENTÊTE + KPIs
# =============================
st.markdown(f"<h1 style='color:{QRM_RED};margin-bottom:0'>Tableau de bord GPS — QRM</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{QRM_LIGHT};font-size:18px'>Joueur : <b>{player_main}</b></p>", unsafe_allow_html=True)

dplayer = df[df[col_player].astype(str)==str(player_main)] if col_player else df.copy()

cK = st.columns(7)
to_m = lambda s: int(s.sum()) if pd.api.types.is_numeric_dtype(s) else "—"
with cK[0]: kpi("Distance totale", to_m(dplayer[col_distance]) if col_distance else "—", "m")
with cK[1]: kpi("Distance HID", to_m(dplayer[col_hid]) if col_hid else "—", "m")
with cK[2]: kpi("Distance HSR", to_m(dplayer[col_hsr]) if col_hsr else "—", "m")
with cK[3]: kpi("Vitesse max", round(dplayer[col_vmax].max(),2) if col_vmax else "—", "km/h")
with cK[4]: kpi("Accélérations", int(dplayer[col_accel].sum()) if col_accel else "—")
with cK[5]: kpi("Décélérations", int(dplayer[col_decel].sum()) if col_decel else "—")
with cK[6]: kpi("Sprints", int(dplayer[col_sprint].sum()) if col_sprint else "—")

st.markdown("---")

# =============================
# SUIVI JOURNALIER
# =============================
st.subheader("📊 Suivi journalier")
if col_date:
    dday = dplayer.copy()
    dday["__jour__"] = dday[col_date].dt.date

    row1 = st.columns(3)
    if col_distance:
        g = dday.groupby("__jour__")[col_distance].sum().reset_index()
        with row1[0]: line_card("Distance totale (m/jour)", g, "__jour__", col_distance, color=QRM_RED, unit="m")
    if col_hid:
        g = dday.groupby("__jour__")[col_hid].sum().reset_index()
        with row1[1]: line_card("Distance HID (m/jour)", g, "__jour__", col_hid, color=QRM_RED, unit="m")
    if col_hsr:
        g = dday.groupby("__jour__")[col_hsr].sum().reset_index()
        with row1[2]: line_card("Distance HSR (m/jour)", g, "__jour__", col_hsr, color=QRM_YELLOW, unit="m")

st.markdown("---")

# =============================
# WELLNESS & RPE
# =============================
st.subheader("💤 État de forme (Sommeil, Fatigue, Douleurs, Motivation, Stress)")
well_cols = [("Sommeil", col_sleep), ("Fatigue", col_fatigue), ("Douleurs", col_pain), ("Motivation", col_motiv), ("Stress", col_stress)]
w_present = [(lbl, c) for lbl,c in well_cols if c is not None and pd.api.types.is_numeric_dtype(dplayer[c])]
if col_date and w_present:
    wdf = dplayer[[col_date] + [c for _,c in w_present]].dropna().copy()
    wdf = wdf.rename(columns={c:lbl for lbl,c in w_present}).sort_values(col_date)
    m = wdf.melt(id_vars=[col_date], var_name="Item", value_name="Score")
    m["Score"] = m["Score"].clip(0, 10)
    fig = px.line(m, x=col_date, y="Score", color="Item", markers=True, color_discrete_sequence=PALETTE)
    fig.update_layout(title="Wellness (échelle 0–10)", yaxis=dict(range=[0,10]))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Pas de données d'état de forme.")

st.subheader("🔥 RPE (Perception de l'effort)")
if col_date and col_rpe and pd.api.types.is_numeric_dtype(dplayer[col_rpe]):
    r = dplayer[[col_date, col_rpe]].dropna().copy().sort_values(col_date).rename(columns={col_rpe:"RPE"})
    fig = px.bar(r, x=col_date, y="RPE", color_discrete_sequence=[QRM_RED])
    fig.update_layout(title="RPE par jour (0–10)", yaxis=dict(range=[0,10]))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Pas de données RPE.")

st.markdown("---")

# =============================
# COMPARAISON MULTI-JOUEURS
# =============================
st.subheader("👥 Comparaison multi‑joueurs")
if pick_players:
    cmp = df[df[col_player].astype(str).isin(pick_players)] if col_player else df.copy()
    agg = {}
    if col_distance: agg["Distance (m)"] = cmp.groupby(col_player)[col_distance].sum()
    if col_hid: agg["HID (m)"] = cmp.groupby(col_player)[col_hid].sum()
    if col_hsr: agg["HSR (m)"] = cmp.groupby(col_player)[col_hsr].sum()
    if col_vmax: agg["Vitesse max"] = cmp.groupby(col_player)[col_vmax].max()
    cmp_df = pd.DataFrame(agg).reset_index().rename(columns={col_player:"Joueur"})
    st.plotly_chart(px.bar(cmp_df.melt(id_vars="Joueur", var_name="Indicateur", value_name="Valeur"),
                           x="Joueur", y="Valeur", color="Indicateur",
                           color_discrete_sequence=PALETTE, barmode="group",
                           title="Comparaison entre joueurs"),
                    use_container_width=True)
else:
    st.info("Sélectionne au moins un joueur.")


# app_qrm_dashboard_qrm_style_v2.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="QRM Performance Dashboard", page_icon="⚽", layout="wide")

# -----------------------
# 🎨 QRM Identity
# -----------------------
QRM_RED = "#D60000"
QRM_GOLD = "#F9B400"
PRIMARY_GREEN = "#2ECC71"
PRIMARY_RED = "#E74C3C"
PRIMARY_BLUE = "#3498DB"
PRIMARY_GREY = "#BDC3C7"

def load_logo_base64():
    logo_file = "Logo QRM.png"
    try:
        with open(logo_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def header_fixed():
    b64 = load_logo_base64()
    if b64:
        st.markdown(
            f'''
            <div style="position:sticky;top:0;z-index:999;background:white;border-bottom:1px solid #eee;padding:8px 10px;">
              <div style="display:flex;align-items:center;gap:10px;">
                <img src="data:image/png;base64,{b64}" style="height:46px;margin-top:2px;">
                <div>
                  <div style="font-weight:800;font-size:1.15rem;color:{QRM_RED};">QRM Performance Dashboard</div>
                  <div style="font-size:0.85rem;color:#555;">Suivi hebdomadaire des charges — Pôle Performance</div>
                </div>
              </div>
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'''
            <div style="position:sticky;top:0;z-index:999;background:white;border-bottom:1px solid #eee;padding:8px 10px;">
              <div style="font-weight:800;font-size:1.15rem;color:{QRM_RED};">QRM Performance Dashboard</div>
              <div style="font-size:0.85rem;color:#555;">Suivi hebdomadaire des charges — Pôle Performance</div>
            </div>
            ''',
            unsafe_allow_html=True
        )

def kpi_gauge(label, value, suffix="", min_val=0, max_val=100, color=PRIMARY_BLUE):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[value], y=[label], orientation="h",
        marker=dict(color=color),
        text=[f"{value:,.0f}{suffix}"], textposition="inside"
    ))
    fig.add_trace(go.Bar(
        x=[max(max_val - value, 0)], y=[label], orientation="h",
        marker=dict(color=PRIMARY_GREY), showlegend=False
    ))
    fig.update_layout(
        barmode="stack", height=80, margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(range=[min_val, max_val], visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    return fig

def donut(value, total, title, colors=(QRM_GOLD, PRIMARY_GREY)):
    val = float(value) if value is not None else 0.0
    # si total absent ou nul, on prend val (ou 1) pour éviter division par zéro
    tot = float(total) if total not in (None, 0) else (val if val > 0 else 1.0)
    other = tot - val
    # si complètement égal, garde une petite part visible pour le second segment
    if other <= 0:
        other = max(tot * 0.0001, 0.0001)
        val = tot - other
    # construit le donut en s'assurant que les couleurs soient bien passées
    fig = go.Figure(go.Pie(
        values=[val, other],
        labels=[title, ""],
        hole=0.7,
        sort=False,
        direction="clockwise",
        marker_colors=[colors[0], colors[1]],
        textinfo="none",
        hoverinfo="label+value+percent",
    ))
    # annotation centrée
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"<b>{val:,.0f}</b>",
        showarrow=False,
        font=dict(size=20, color="#111"),
        xanchor="center", yanchor="middle"
    )
    fig.update_layout(
        margin=dict(l=5, r=5, t=40, b=5),
        showlegend=False,
        height=240,
        autosize=True,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def dual_bar(x, y1, y2, name1="Accélérations", name2="Décélérations"):
    fig = go.Figure()
    fig.add_trace(go.Bar(name=name1, x=x, y=y1, marker_color=PRIMARY_GREEN))
    fig.add_trace(go.Bar(name=name2, x=x, y=y2, marker_color=PRIMARY_RED))
    fig.update_layout(barmode="group", height=320, margin=dict(l=10,r=10,t=40,b=10),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def wellness_bar(values: dict):
    items = list(values.keys())
    vals = [values[k] for k in items]
    colors = [PRIMARY_GREEN if k in ["Sommeil 1-5","Motivation 1-5"]
              else PRIMARY_RED if k in ["Fatigue 1-5","Douleurs 1-5","Stress 1-5"]
              else QRM_GOLD for k in items]
    fig = go.Figure(go.Bar(
        x=items, y=vals, marker_color=colors,
        text=[f"{v:.1f}" for v in vals], textposition="outside"
    ))
    fig.update_yaxes(range=[0,5], title="Score /5")
    fig.update_layout(height=320, margin=dict(l=10,r=10,t=40,b=10),
                      title="Wellness (scores 1 à 5)")
    return fig

def rpe_gauge(rpe_value: float):
    fig = kpi_gauge("RPE", float(rpe_value), suffix=" /10", min_val=0, max_val=10, color=QRM_GOLD)
    fig.update_layout(
        title=dict(text="RPE", x=0.5, xanchor="center", y=0.9, yanchor="top", font=dict(size=14)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=120,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# ---------- UI ----------
header_fixed()

with st.sidebar:
    st.subheader("📥 Données")
    uploaded = st.file_uploader("Importer 'DATA BRUTES.xlsx'", type=["xlsx"])
    st.caption("Feuille lue : **DATA (2)**. Les colonnes sont mappées automatiquement.")

# Load data
if uploaded is None:
    st.info("Importe le fichier Excel pour afficher le dashboard.")
    st.stop()

df = pd.read_excel(uploaded, sheet_name="DATA (2)")

# Rename columns to internal names
df = df.rename(columns={
    "Player Display Name": "Joueur",
    "Total Distance": "Distance_Totale",
    "Distance Zone 4 (Absolute)": "Zone4_Dist",
    "Distance Zone 5 (Absolute)": "Zone5_Dist",
    "Accelerations (Absolute)": "Accels",
    "Decelerations (Absolute)": "Decels",
    "Max Speed": "Vitesse_Max"
})

# Ensure Date is datetime
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    st.error("La colonne 'Date' est manquante."); st.stop()


# Sidebar filters (ajout d'un sélecteur de période)
with st.sidebar:
    # filtre période
    col_date = "Date"
    if col_date in df.columns and df[col_date].notna().any():
        dmin, dmax = df[col_date].min().date(), df[col_date].max().date()
        start_date, end_date = st.date_input("Période", value=(dmin, dmax), min_value=dmin, max_value=dmax)
        # filtrer inclusif sur la colonne Date (datetime)
        df = df[(df[col_date].dt.date >= pd.to_datetime(start_date).date()) & (df[col_date].dt.date <= pd.to_datetime(end_date).date())]

    joueurs = sorted(df["Joueur"].dropna().unique().tolist())
    joueur = st.selectbox("👤 Joueur", joueurs, index=0)

# Filtrer par joueur
pdf = df[df["Joueur"] == joueur].copy()
if pdf.empty:
    st.warning("Aucune donnée pour ce joueur.")
    st.stop()

# Appliquer le filtre de période (défini dans la sidebar) — sécurité et conversion date
if 'start_date' in locals() and 'end_date' in locals():
    sd = pd.to_datetime(start_date).date()
    ed = pd.to_datetime(end_date).date()
    if ed < sd:
        sd, ed = ed, sd
    pdf = pdf[(pdf["Date"].dt.date >= sd) & (pdf["Date"].dt.date <= ed)]

# fdf = données finales filtrées (identique à pdf ici)
fdf = pdf.copy()
if fdf.empty:
    st.warning("Aucune donnée pour cette sélection.")
    st.stop()

# Aggregation rules
sum_cols = ["Distance_Totale","Zone4_Dist","Zone5_Dist","Sprints","Accels","Decels"]
avg_cols = ["Vitesse_Max","RPE 1-10","Sommeil 1-5","Fatigue 1-5","Stress 1-5","Douleurs 1-5","Motivation 1-5"]

agg = {}
for c in sum_cols:
    if c in fdf.columns:
        agg[c] = float(fdf[c].sum(skipna=True))
for c in avg_cols:
    if c in fdf.columns:
        agg[c] = float(fdf[c].mean(skipna=True))

# --------- Layout ---------
# Row 1 KPIs
c1, c2, c3 = st.columns(3)
with c1:
    st.plotly_chart(donut(agg.get("Distance_Totale",0), agg.get("Distance_Totale",1), "Distance Totale (m)"),
                    use_container_width=True)
    st.metric("Distance totale (m)", f"{agg.get('Distance_Totale',0):.0f}")

with c2:
    hid_val = agg.get("Zone4_Dist",0)
    st.plotly_chart(kpi_gauge("HID (Zone 4)", hid_val, " m",
                              0, max(2000, hid_val*1.2 if hid_val else 2000), QRM_GOLD),
                    use_container_width=True)
    st.metric("HID (m)", f"{hid_val:.0f}")

with c3:
    hsr_val = agg.get("Zone5_Dist",0)
    st.plotly_chart(kpi_gauge("HSR (Zone 5)", hsr_val, " m",
                              0, max(1200, hsr_val*1.2 if hsr_val else 1200), QRM_RED),
                    use_container_width=True)
    st.metric("HSR (m)", f"{hsr_val:.0f}")

st.divider()

# Row 2: Sprints/Vmax and Acc/Dec
c4, c5 = st.columns([1.2,1])
with c4:
    fig = go.Figure()
    # x-axis depends on view
    if sd == "Journalier":
        x = fdf["Date"]
    else:
        x = fdf["Date"]  # keep daily points within selected week
    fig.add_trace(go.Bar(x=x, y=fdf["Sprints"], name="Sprints", marker_color=QRM_RED))
    if "Vitesse_Max" in fdf.columns:
        fig.add_trace(go.Scatter(x=x, y=fdf["Vitesse_Max"], name="Vitesse max (km/h)",
                                 mode="lines+markers", yaxis="y2", line=dict(color=QRM_GOLD)))
    fig.update_layout(
        title="Sprints & Vitesse maximale",
        yaxis=dict(title="Sprints"),
        yaxis2=dict(title="Vitesse max (km/h)", overlaying="y", side="right"),
        height=360, margin=dict(l=10,r=10,t=40,b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

with c5:
    fig = dual_bar(fdf["Date"], fdf.get("Accels",0), fdf.get("Decels",0))
    fig.update_layout(title="Accélérations & Décélérations")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# === Nouveau graphique détaillé : Distance Totale / HID / HSR (jour par jour) ===
# affiché en pleine largeur sous Row 2
def detailed_distance_chart(df_days):
    x = pd.to_datetime(df_days["Date"])
    fig = go.Figure()

    # Barres : Distance Totale / HID / HSR
    if "Distance_Totale" in df_days.columns:
        fig.add_trace(go.Bar(
            x=x,
            y=df_days["Distance_Totale"].fillna(0),
            name="Distance Totale (m)",
            marker_color=QRM_GOLD
        ))

    if "Zone4_Dist" in df_days.columns:
        fig.add_trace(go.Bar(
            x=x,
            y=df_days["Zone4_Dist"].fillna(0),
            name="HID - Zone 4 (m)",
            marker_color=QRM_RED
        ))

    if "Zone5_Dist" in df_days.columns:
        fig.add_trace(go.Bar(
            x=x,
            y=df_days["Zone5_Dist"].fillna(0),
            name="HSR - Zone 5 (m)",
            marker_color=PRIMARY_BLUE
        ))

    # Mise en forme
    fig.update_layout(
        title="Distance Totale, HID et HSR (jour par jour)",
        barmode="group",  # groupé (barres côte à côte)
        xaxis=dict(title="Date"),
        yaxis=dict(title="Distance (m)", showgrid=False),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=60, t=40, b=40),
        height=420,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig

# Affichage du graphique
st.plotly_chart(detailed_distance_chart(fdf.sort_values("Date")), use_container_width=True)

st.divider()


# Row 3: Wellness & RPE
c6, c7 = st.columns([1.4,0.8])
with c6:
    w_cols = ["Sommeil 1-5","Fatigue 1-5","Stress 1-5","Douleurs 1-5","Motivation 1-5"]
    w_vals = {c: float(fdf[c].mean()) for c in w_cols if c in fdf.columns}
    st.plotly_chart(wellness_bar(w_vals), use_container_width=True)

with c7:
    rpe_val = float(fdf["RPE 1-10"].mean()) if "RPE 1-10" in fdf.columns else 0.0
    st.plotly_chart(rpe_gauge(rpe_val), use_container_width=True)

st.divider()
st.subheader("Données sélectionnées")
st.dataframe(fdf.reset_index(drop=True))

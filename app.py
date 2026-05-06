"""
Dashboard d'audit et prédiction - leviers d'acquisition payante.

Lancer : streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from lib.data import load_benchmarks, get_format_kpis, list_leviers
from lib.audit import status_for, STATUS_LABEL, STATUS_COLOR, diagnostic
from lib.predict import predict


st.set_page_config(
    page_title="Audit & Prédiction — Acquisition payante (SaaS B2B RH)",
    page_icon="📊",
    layout="wide",
)

VERTICAL = "SaaS B2B RH — GTA & planification (audiences DRH / RRH / SIRH)"

# ----------------------------------------------------------------------------
# Chargement des données
# ----------------------------------------------------------------------------
data = load_benchmarks()
df_bench = data["benchmarks"]
df_formats = data["formats"]
df_sources = data["sources"]

# ----------------------------------------------------------------------------
# Sidebar - navigation + sélection levier
# ----------------------------------------------------------------------------
st.sidebar.title("📊 Acquisition payante")
st.sidebar.caption(VERTICAL)
mode = st.sidebar.radio("Mode", ["🔎 Audit", "🔮 Prédiction", "📋 Benchmarks", "ℹ️ Sources"], index=0)

leviers = list_leviers(df_bench)
levier_labels = [f"{p} — {f}" for p, f in leviers]
choice = st.sidebar.selectbox("Levier", levier_labels)
plateforme, fmt = leviers[levier_labels.index(choice)]

# Métadonnées du levier
meta = df_formats[(df_formats["plateforme"] == plateforme) & (df_formats["format"] == fmt)]
if not meta.empty:
    m = meta.iloc[0]
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Objectif :** {m['objectif']}")
    st.sidebar.markdown(f"**Audience :** {m['audience']}")
    st.sidebar.caption(m["conseils"])


# ============================================================================
# MODE AUDIT
# ============================================================================
if mode == "🔎 Audit":
    st.title("🔎 Audit de campagne")
    st.markdown(f"### {plateforme} — {fmt}")
    st.caption("Saisis tes chiffres réels pour les comparer au benchmark marché.")

    kpis_df = get_format_kpis(df_bench, plateforme, fmt)

    if kpis_df.empty:
        st.warning("Aucun benchmark pour ce levier.")
        st.stop()

    # Saisie utilisateur
    st.subheader("Tes chiffres")
    cols = st.columns(min(3, len(kpis_df)))
    user_values = {}
    for i, row in kpis_df.iterrows():
        col = cols[i % len(cols)]
        key = f"input_{plateforme}_{fmt}_{row['kpi']}"
        default = float(row["mediane"])
        user_values[row["kpi"]] = col.number_input(
            f"{row['kpi']} ({row['unite']})",
            min_value=0.0,
            value=default,
            step=max(0.01, float(row["mediane"]) / 100),
            key=key,
            help=row["note"],
        )

    st.markdown("---")
    st.subheader("Diagnostic vs benchmark marché")

    rows_html = []
    for _, row in kpis_df.iterrows():
        v = user_values[row["kpi"]]
        st_code = status_for(v, float(row["min"]), float(row["max"]), row["sens"])
        diag = diagnostic(v, float(row["mediane"]), row["sens"])
        rows_html.append({
            "KPI": row["kpi"],
            "Ta valeur": f"{v:.2f} {row['unite']}",
            "Min marché": f"{row['min']:.2f}",
            "Médiane": f"{row['mediane']:.2f}",
            "Max marché": f"{row['max']:.2f}",
            "Statut": STATUS_LABEL[st_code],
            "Diagnostic": diag,
            "_color": STATUS_COLOR[st_code],
        })

    df_view = pd.DataFrame(rows_html)

    # Affichage table colorée
    def color_row(r):
        return [f"background-color: {r['_color']}22; border-left: 4px solid {r['_color']}"] * len(r)

    styled = df_view.drop(columns=["_color"]).style.apply(
        lambda r: [
            f"background-color: {df_view.loc[r.name, '_color']}22; "
            f"border-left: 4px solid {df_view.loc[r.name, '_color']}"
        ] * len(r),
        axis=1,
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Synthèse globale
    st.markdown("---")
    st.subheader("Synthèse")
    n_green = sum(1 for r in rows_html if r["Statut"].startswith("✅"))
    n_orange = sum(1 for r in rows_html if r["Statut"].startswith("🟠"))
    n_red = sum(1 for r in rows_html if r["Statut"].startswith("🔴"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Au-dessus benchmark", n_green)
    c2.metric("Dans la moyenne", n_orange)
    c3.metric("Sous-performant", n_red)

    if n_red == 0 and n_green >= n_orange:
        st.success("Campagne saine — performance au-dessus du marché sur la majorité des KPIs.")
    elif n_red >= 2:
        st.error(f"{n_red} KPI(s) en zone rouge — actions correctives prioritaires à mener.")
    else:
        st.info("Performance moyenne — leviers d'optimisation identifiables.")


# ============================================================================
# MODE PRÉDICTION
# ============================================================================
elif mode == "🔮 Prédiction":
    st.title("🔮 Prédiction de performance")
    st.markdown(f"### {plateforme} — {fmt}")
    st.caption("Estime le volume attendu pour un budget donné, basé sur le benchmark marché.")

    budget = st.number_input(
        "Budget (€)",
        min_value=100.0,
        max_value=1_000_000.0,
        value=5000.0,
        step=500.0,
    )

    kpis_df = get_format_kpis(df_bench, plateforme, fmt)
    scenarios = predict(kpis_df, budget)

    if not scenarios:
        st.warning("Le moteur de prédiction ne supporte pas encore ce format.")
        st.stop()

    st.markdown("---")
    st.subheader("3 scénarios")

    cols = st.columns(3)
    labels = {"pessimiste": "📉 Pessimiste", "median": "📊 Médian", "optimiste": "📈 Optimiste"}
    colors = {"pessimiste": "#d64545", "median": "#e58e26", "optimiste": "#1f9d55"}

    for col, key in zip(cols, ["pessimiste", "median", "optimiste"]):
        s = scenarios.get(key, {})
        with col:
            st.markdown(
                f"<h4 style='color:{colors[key]}'>{labels[key]}</h4>",
                unsafe_allow_html=True,
            )
            if s.get("impressions") is not None:
                lib = "Envois" if "ouvertures" in s else "Impressions"
                st.metric(lib, f"{s['impressions']:,.0f}".replace(",", " "))
            if s.get("ouvertures") is not None:
                st.metric("Ouvertures", f"{s['ouvertures']:,.0f}".replace(",", " "))
            if s.get("vues") is not None:
                st.metric("Vues", f"{s['vues']:,.0f}".replace(",", " "))
            if s.get("clics") is not None:
                st.metric("Clics", f"{s['clics']:,.0f}".replace(",", " "))
            if s.get("leads") is not None:
                st.metric("Leads / Conv", f"{s['leads']:,.1f}".replace(",", " "))
            if s.get("cpa_effectif") is not None:
                st.metric("CPA / CPL effectif", f"{s['cpa_effectif']:,.0f} €".replace(",", " "))

    # Graphique comparatif
    st.markdown("---")
    st.subheader("Comparaison visuelle")

    metrics = ["impressions", "clics", "leads"]
    metric_labels = {"impressions": "Impressions / Envois", "clics": "Clics", "leads": "Leads / Conv"}
    fig = go.Figure()
    for metric in metrics:
        vals = [scenarios[s].get(metric) for s in ["pessimiste", "median", "optimiste"]]
        if all(v is None for v in vals):
            continue
        vals_clean = [v if v is not None else 0 for v in vals]
        fig.add_trace(go.Bar(
            name=metric_labels[metric],
            x=["Pessimiste", "Médian", "Optimiste"],
            y=vals_clean,
        ))
    fig.update_layout(barmode="group", height=380, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# MODE BENCHMARKS
# ============================================================================
elif mode == "📋 Benchmarks":
    st.title("📋 Benchmarks marché")
    st.caption("Vue complète des benchmarks par levier (B2B France/EU 2024-2025).")

    plateformes = ["Tous"] + sorted(df_bench["plateforme"].unique().tolist())
    p = st.selectbox("Plateforme", plateformes)
    df_view = df_bench if p == "Tous" else df_bench[df_bench["plateforme"] == p]
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Métadonnées par format")
    st.dataframe(df_formats, use_container_width=True, hide_index=True)


# ============================================================================
# MODE SOURCES
# ============================================================================
elif mode == "ℹ️ Sources":
    st.title("ℹ️ Sources & méthodologie")
    st.markdown(f"""
**Vertical ciblé** : {VERTICAL}

Les benchmarks compilés sont calibrés pour un éditeur SaaS B2B RH spécialisé GTA
(gestion des temps & activités) en évolution vers la planification. Audiences cibles :
DRH, RRH, Responsables paie, Responsables SIRH, dirigeants ETI/PME (50-2000 collab.).

Sources : rapports publics 2024-2025 (LinkedIn Ads Benchmark, WordStream B2B SaaS,
G2 Buyer Behavior) + retours agence STAENK sur clients SaaS RH.

**Conséquences vs benchmark B2B générique** :
- LinkedIn CPC/CPL plus élevés (cibles HR seniors = enchères tendues)
- Search CPC élevés (concurrence Kelio, Bodet, Octime, Horoquartz, Skello)
- Conversion = "demande de démo / RDV qualifié" (cycle long, pas d'achat direct)

**Pour personnaliser** : édite directement `data/benchmarks.xlsx` puis relance l'app.
La feuille `benchmarks` accepte des nouvelles lignes (plateforme/format/kpi).
""")
    st.dataframe(df_sources, use_container_width=True, hide_index=True)

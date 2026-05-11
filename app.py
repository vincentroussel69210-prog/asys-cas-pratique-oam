"""
Dashboard d'audit, prédiction et plan media - leviers d'acquisition payante.

Lancer : streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from lib.data import load_benchmarks, get_format_kpis, list_leviers
from lib.audit import status_for, STATUS_LABEL, STATUS_COLOR, diagnostic
from lib.predict import predict
from lib.plan_media import (
    SEGMENTS_DEFAULT,
    LEVIERS_PERF,
    LEVIERS_NOTORIETE,
    ALLOCATION_DEFAULT,
    ALLOCATION_NOTORIETE,
    CONV_BDR_DEFAULT,
    SHARE_NOTORIETE_DEFAULT,
    compute_plan,
)
from lib.contenus import CONTENUS, FUNNEL_COLORS


st.set_page_config(
    page_title="Audit & Prédiction — Acquisition payante (SaaS B2B RH)",
    page_icon="📊",
    layout="wide",
)

VERTICAL = "SaaS B2B RH — Chronos · GTA & planification multi-sites · grandes organisations privées + publiques (audiences DRH / RRH / SIRH)"

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
mode = st.sidebar.radio(
    "Mode",
    [
        "🔍 Diagnostic initial",
        "🔎 Audit",
        "🔮 Prédiction",
        "🎯 Plan media",
        "🎨 Contenus",
        "🚀 Stratégie",
        "📈 Aperçu reporting",
        "📋 Benchmarks",
        "📖 Glossaire",
        "ℹ️ Sources",
    ],
    index=0,
)

# Le sélecteur de levier ne sert que pour Audit + Prédiction
if mode in ("🔎 Audit", "🔮 Prédiction"):
    leviers = list_leviers(df_bench)
    levier_labels = [f"{p} — {f}" for p, f in leviers]
    choice = st.sidebar.selectbox("Levier", levier_labels)
    plateforme, fmt = leviers[levier_labels.index(choice)]

    meta = df_formats[(df_formats["plateforme"] == plateforme) & (df_formats["format"] == fmt)]
    if not meta.empty:
        m = meta.iloc[0]
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Objectif :** {m['objectif']}")
        st.sidebar.markdown(f"**Audience :** {m['audience']}")
        st.sidebar.caption(m["conseils"])


# ============================================================================
# MODE DIAGNOSTIC INITIAL — cadre d'audit en 7 axes
# ============================================================================
if mode == "🔍 Diagnostic initial":
    st.title("🔍 Diagnostic initial — premières analyses sur le poste")
    st.caption(
        "Cadre d'audit que je déroule lors de mes 30 premiers jours pour comprendre la "
        "performance actuelle de l'acquisition digitale, identifier les leviers les plus "
        "actionnables et bâtir une roadmap appuyée sur des faits."
    )

    # ---- Pitch d'intro ----
    st.html(
        '<div style="background:linear-gradient(135deg,#1264a3,#0a66c2);color:white;'
        'padding:18px 22px;border-radius:8px;margin:8px 0 18px 0;">'
        '<p style="margin:0;font-size:1.02em;line-height:1.55;font-style:italic;">'
        '« Avant de proposer un nouveau plan d\'attaque, je dois répondre à 3 questions : '
        '<b>(1)</b> la data est-elle fiable ? '
        '<b>(2)</b> où sont les fuites du funnel <i>(entonnoir de conversion)</i> actuel ? '
        '<b>(3)</b> quel mix segment génère le plus de pipeline rentable ? '
        '— Tant qu\'on n\'a pas ces réponses, optimiser la créa ou le bidding revient à '
        'colmater à l\'aveugle. »'
        '</p>'
        '</div>'
    )

    # ---- Périmètre produit Chronos ----
    st.html(
        '<div style="background:#f4f6fb;border-left:4px solid #0a66c2;'
        'border-radius:6px;padding:14px 18px;margin:8px 0 18px 0;">'
        '<h4 style="margin:0 0 8px 0;color:#0a66c2;">🎯 Périmètre produit Chronos</h4>'
        '<p style="margin:0 0 6px 0;font-size:0.93em;color:#333;line-height:1.55;">'
        '<b>Cible :</b> grandes organisations complexes, <b>privé + secteur public</b>, '
        'avec un fort enjeu de gestion multi-sites et de planification d\'équipes terrain.'
        '</p>'
        '<p style="margin:6px 0;font-size:0.93em;color:#333;line-height:1.55;">'
        '<b>Secteurs clés :</b> établissements de santé (CHU, cliniques, EHPAD) · '
        'collectivités & secteur public (régions, métropoles, conseils départementaux) · '
        'industrie · retail / distribution · structures multi-sites.'
        '</p>'
        '<p style="margin:6px 0 0 0;font-size:0.85em;color:#666;font-style:italic;">'
        'Cadrage segments (cf. brief) : Santé · Privé Mid Market 200-1000 · Large >1000. '
        'Le segment Large absorbe la cible publique (collectivités) et les grands comptes privés multi-sites.'
        '</p>'
        '</div>'
    )

    # ---- 7 axes d'audit ----
    axes_audit = [
        {
            "num": 1,
            "priority": "🔴 Bloquant",
            "color": "#d64545",
            "title": "Écosystème mesure & data",
            "why": "Sans data fiable, toutes les décisions suivantes sont du bricolage.",
            "analyse": [
                "Architecture tracking : GTM, dataLayer, server-side, cookies tiers",
                "Cohérence data <b>HubSpot ↔ régies</b> (Google Ads, LinkedIn Ads)",
                "Présence ou non des <b>conversions hors ligne</b> (RDV qualifié, opp, contrat)",
                "Modèle d'attribution actif (last-click ? data-driven ?)",
            ],
            "indicateurs": [
                "Écart spend <i>(dépense pub)</i> régie vs spend HubSpot (>5% = drift <i>(dérive)</i>)",
                "Taux de matching MQL → Contact HubSpot (cible >95%)",
                "% de conversions hors ligne remontées (cible 100% MQL, ≥70% SQL/contrat)",
            ],
            "objectif": "La base data est-elle utilisable pour décider ? Si non, M1 = chantier prioritaire avant toute optim media.",
        },
        {
            "num": 2,
            "priority": "🟠 Haute",
            "color": "#e58e26",
            "title": "Performance par levier",
            "why": "Identifier les leviers à scaler vs à couper net, sur 12 mois.",
            "analyse": [
                "Google Ads (Search / DSA / Demand Gen) + LinkedIn (Conv / SI / TL)",
                "Découpe par campagne, ad group, audience",
                "Cycle complet : spend / MQL / SQL / pipeline signé",
            ],
            "indicateurs": [
                "CPM, CPC, CTR, CPL vs benchmark SaaS B2B RH",
                "<b>CPA fin de funnel</b> (pas le CPL — le ROAS sur pipeline <i>(portefeuille d'opportunités)</i> signé)",
                "Search Impression Share, Quality Score moyen (Google)",
                "Frequency, Reach, Resonance (LinkedIn)",
            ],
            "objectif": "2-3 leviers à scaler · 1-2 à fermer · vrai coût par 1€ de pipeline.",
        },
        {
            "num": 3,
            "priority": "🟠 Haute",
            "color": "#e58e26",
            "title": "Funnel de conversion",
            "why": "Trouver les 1-2 fuites majeures où concentrer les efforts.",
            "analyse": [
                "Impression → Clic → Visite LP → MQL → SQL → Opp → Contrat",
                "Drop-off à chaque étape",
                "Performance des landing pages <i>(pages d'atterrissage)</i> par campagne",
            ],
            "indicateurs": [
                "Taux de conversion par étape",
                "Taux conv LP par campagne (cible >2% B2B)",
                "Taux conv BDR (MQL → SQL) <b>par source</b> (les 35% globaux d'Ingrid cachent peut-être 60% LinkedIn vs 15% DSA)",
                "Délai moyen MQL → SQL → contrat",
            ],
            "objectif": "Cible 80% des efforts d'optim sur les 1-2 plus grosses fuites (souvent LP + qualif BDR).",
        },
        {
            "num": 4,
            "priority": "🟡 Moyenne",
            "color": "#e6b800",
            "title": "Performance par segment & ICP",
            "why": "Vérifier que le mix Santé 44% / Large 36% / Mid 20% est respecté ET rentable.",
            "analyse": [
                "Performance comparative Santé / Large / Mid Market",
                "% MQLs alignés ICP / rejetés par Ingrid (BDR)",
                "Cohérence ACV constaté vs ACV cible par segment",
            ],
            "indicateurs": [
                "CAC par segment vs LTV (ACV × win rate × durée)",
                "Coût pour 1€ de pipeline <b>par segment</b>",
                "Distribution réelle du pipeline vs cible 44/36/20%",
                "Taux de qualification BDR par segment",
            ],
            "objectif": "Quel segment est performant naturellement ? Lequel rame ? (Santé demande probablement de l'ABM chirurgical.)",
        },
        {
            "num": 5,
            "priority": "🟡 Moyenne",
            "color": "#e6b800",
            "title": "Créa & message",
            "why": "Identifier les angles gagnants et le système de production créa actuel.",
            "analyse": [
                "Librairie créative existante (volume, diversité)",
                "Angles testés (témoignage, démo, livre blanc, coup de gueule, chiffre)",
                "Performance par auteur Thought Leader (CEO, CPO, etc.)",
                "Vélocité de production : nb créas / semaine",
            ],
            "indicateurs": [
                "CTR / CPL par angle créatif",
                "Lifetime des créas (jour de saturation = -30% CTR)",
                "Volume de tests A/B menés sur 12 mois",
                "Diversité d'assets (peu = signal de pénurie créa)",
            ],
            "objectif": "Industrialiser les angles gagnants, identifier le bottleneck de production.",
        },
        {
            "num": 6,
            "priority": "🟡 Moyenne",
            "color": "#e6b800",
            "title": "Concurrence & Share of Voice (part de voix)",
            "why": "Savoir où on est en retard sur la distribution, pas le produit.",
            "analyse": [
                "Concurrents : Kelio, Bodet, Octime, Skello, Horoquartz",
                "Présence Google Ads (Auction Insights)",
                "Présence LinkedIn (Ad Library)",
                "Visibilité dans les réponses LLM (état zéro = 23%)",
                "Notoriété sur médias d'autorité (G2, Capterra, MyRHline)",
            ],
            "indicateurs": [
                "Auction Insights : overlap rate, position above, top of page rate",
                "Volume ads concurrents en activité (LinkedIn Ad Library)",
                "<b>Score de visibilité LLM</b> par prompt thématique",
                "Domain Rating <i>(indice d'autorité de domaine)</i> + nb backlinks <i>(liens entrants)</i> DR>50 (Ahrefs)",
            ],
            "objectif": "Gaps prioritaires à combler · angles concurrents qui marchent à reprendre.",
        },
        {
            "num": 7,
            "priority": "🟢 Standard",
            "color": "#1f9d55",
            "title": "Budget historique & cohérence sales",
            "why": "Vérifier que les objectifs marketing sont alignés avec la capacity sales.",
            "analyse": [
                "Spend par mois sur 12 mois (volume + saisonnalité)",
                "Capacity BDR : combien Ingrid peut traiter sans dégrader la qualif",
                "Pipeline existant vs cible 4,5 M€ (gap à combler)",
                "Saisonnalité B2B RH (creux été, pic janv-mars budgets RH)",
            ],
            "indicateurs": [
                "Volume MQLs / mois moyen + std deviation",
                "Capacity BDR (cible : ≤ 80 MQLs/mois/BDR pour qualif sérieuse)",
                "Pipeline gap (objectif 4,5 M€ vs trajectoire actuelle)",
                "ROI fin de funnel (dépense / pipeline signé)",
            ],
            "objectif": "Aligner volume MQL généré avec capacity sales · sinon les MQLs pourrissent.",
        },
    ]

    # ---- Rendu des cards ----
    for axe in axes_audit:
        analyse_html = "".join([f"<li>{a}</li>" for a in axe["analyse"]])
        indicateurs_html = "".join([f"<li>{i}</li>" for i in axe["indicateurs"]])

        card = (
            f'<div style="background:#fafafa;border-left:5px solid {axe["color"]};'
            f'border-radius:6px;padding:18px 22px;margin:10px 0;">'

            # Header
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'margin-bottom:6px;">'
            f'<h3 style="margin:0;color:#222;">'
            f'<span style="display:inline-block;width:32px;height:32px;border-radius:50%;'
            f'background:{axe["color"]};color:white;text-align:center;line-height:32px;'
            f'font-size:0.9em;margin-right:10px;">{axe["num"]}</span>'
            f'{axe["title"]}'
            f'</h3>'
            f'<span style="background:{axe["color"]};color:white;font-size:0.78em;'
            f'padding:4px 12px;border-radius:12px;font-weight:600;">'
            f'{axe["priority"]}</span>'
            f'</div>'

            f'<p style="margin:6px 0 12px 0;font-size:0.92em;color:#666;font-style:italic;">'
            f'<b>Pourquoi :</b> {axe["why"]}'
            f'</p>'

            # 3 colonnes
            f'<div style="display:flex;gap:14px;flex-wrap:wrap;">'

            # Ce qu'on analyse
            f'<div style="flex:1;min-width:240px;background:white;border-radius:5px;'
            f'padding:12px 14px;">'
            f'<h5 style="margin:0 0 8px 0;color:{axe["color"]};">📋 Ce qu\'on analyse</h5>'
            f'<ul style="margin:0;padding-left:18px;font-size:0.88em;color:#333;line-height:1.6;">'
            f'{analyse_html}'
            f'</ul>'
            f'</div>'

            # Indicateurs
            f'<div style="flex:1;min-width:240px;background:white;border-radius:5px;'
            f'padding:12px 14px;">'
            f'<h5 style="margin:0 0 8px 0;color:{axe["color"]};">📊 Indicateurs suivis</h5>'
            f'<ul style="margin:0;padding-left:18px;font-size:0.88em;color:#333;line-height:1.6;">'
            f'{indicateurs_html}'
            f'</ul>'
            f'</div>'

            # Ce qu'on cherche
            f'<div style="flex:1;min-width:240px;background:white;border-radius:5px;'
            f'padding:12px 14px;">'
            f'<h5 style="margin:0 0 8px 0;color:{axe["color"]};">🎯 Ce qu\'on cherche</h5>'
            f'<p style="margin:0;font-size:0.88em;color:#333;line-height:1.55;">'
            f'{axe["objectif"]}'
            f'</p>'
            f'</div>'

            f'</div>'  # fin flex
            f'</div>'  # fin card
        )
        st.html(card)

    # ---- Checklist M1 actions concrètes ----
    st.markdown("---")
    st.subheader("✅ Checklist concrète — sortir du diagnostic en 30 jours")

    checklist = [
        ("S1", "Pull historique 12 mois sur Google Ads + LinkedIn Ads + HubSpot"),
        ("S1", "Récupérer les listes de comptes Santé / Large / Mid Market dans HubSpot"),
        ("S2", "Audit du tracking : GTM, dataLayer, déduplication leads, server-side"),
        ("S2", "Cartographie des sources HubSpot vs régies (matching MQL)"),
        ("S2", "Setup d'un dashboard Looker Studio brut (toutes les données en un endroit)"),
        ("S3", "Analyse perf par levier × segment (CPL / CAC / pipeline signé)"),
        ("S3", "Analyse drop-off <i>(taux d'abandon)</i> du funnel par étape et par source"),
        ("S3", "Entretien Ingrid (BDR) : volume MQL traités, critères de qualif, points bloquants"),
        ("S4", "Audit créatif : librairie + angles + lifetime + tests A/B"),
        ("S4", "Audit concurrentiel : Auction Insights + LinkedIn Ad Library + état zéro LLM"),
        ("S4", "Synthèse en 1 deck <i>(présentation)</i> : 3 problèmes prioritaires + 5 quick wins <i>(gains rapides)</i> + roadmap <i>(feuille de route)</i> M2-M6"),
    ]

    cl_html = (
        '<div style="background:#fafafa;border-radius:6px;padding:14px 18px;">'
        '<table style="width:100%;border-collapse:collapse;">'
        '<thead><tr style="background:#e8eef5;">'
        '<th style="padding:8px 10px;text-align:left;color:#666;font-size:0.85em;width:80px;">Semaine</th>'
        '<th style="padding:8px 10px;text-align:left;color:#666;font-size:0.85em;">Action</th>'
        '</tr></thead>'
        '<tbody>'
    )
    for week, action in checklist:
        cl_html += (
            f'<tr style="border-bottom:1px solid #eee;">'
            f'<td style="padding:8px 10px;font-weight:bold;color:#0a66c2;font-size:0.92em;">{week}</td>'
            f'<td style="padding:8px 10px;color:#333;font-size:0.92em;">{action}</td>'
            f'</tr>'
        )
    cl_html += '</tbody></table></div>'
    st.html(cl_html)

    st.info(
        "🎯 **Livrable de fin de M1** : un deck synthétique avec (a) les 3 problèmes prioritaires "
        "identifiés, (b) 5 quick wins activables sous 30 jours, (c) une roadmap M2-M6 chiffrée. "
        "→ Cf. mode **🚀 Stratégie** pour la suite."
    )


# ============================================================================
# MODE AUDIT
# ============================================================================
elif mode == "🔎 Audit":
    st.title("🔎 Audit de campagne")
    st.markdown(f"### {plateforme} — {fmt}")
    st.caption("Saisis tes chiffres réels pour les comparer au benchmark marché.")

    kpis_df = get_format_kpis(df_bench, plateforme, fmt)

    if kpis_df.empty:
        st.warning("Aucun benchmark pour ce levier.")
        st.stop()

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
    styled = df_view.drop(columns=["_color"]).style.apply(
        lambda r: [
            f"background-color: {df_view.loc[r.name, '_color']}22; "
            f"border-left: 4px solid {df_view.loc[r.name, '_color']}"
        ] * len(r),
        axis=1,
    )
    st.dataframe(styled, width="stretch", hide_index=True)

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
    st.plotly_chart(fig, width="stretch")


# ============================================================================
# MODE PLAN MEDIA
# ============================================================================
elif mode == "🎯 Plan media":
    st.title("🎯 Plan media — Reverse engineering du pipeline")
    st.caption(
        "Du pipeline cible vers le budget par levier. Pré-rempli avec l'étude de cas "
        "(4,5 M€ de pipeline, 3 segments Santé / Large (privé + public) / Mid Market, conv BDR 35%)."
    )

    # ------- Hypothèses : segments + ACV + SQLs -------
    with st.expander("🧮 Hypothèses (segments, ACV, taux conv BDR)", expanded=True):
        st.markdown("**Objectifs par segment**")
        cols = st.columns(len(SEGMENTS_DEFAULT))
        segments = {}
        for col, (seg_name, seg) in zip(cols, SEGMENTS_DEFAULT.items()):
            with col:
                st.markdown(
                    f"<h4 style='color:{seg['color']};margin-bottom:0'>{seg_name}</h4>"
                    f"<p style='color:#666;font-size:0.85em;margin-top:0'>{seg['note']}</p>",
                    unsafe_allow_html=True,
                )
                acv = st.number_input(
                    "ACV (€)",
                    min_value=1000,
                    max_value=500000,
                    value=int(seg["acv"]),
                    step=1000,
                    key=f"acv_{seg_name}",
                )
                sqls = st.number_input(
                    "SQLs cible (transactions HubSpot)",
                    min_value=1,
                    max_value=1000,
                    value=int(seg["sqls_target"]),
                    step=1,
                    key=f"sqls_{seg_name}",
                )
                pipeline_seg = sqls * acv
                st.metric("Pipeline segment", f"{pipeline_seg/1_000_000:.2f} M€")
                segments[seg_name] = {
                    "share_pipe_pct": seg["share_pipe_pct"],
                    "acv": acv,
                    "sqls_target": sqls,
                    "color": seg["color"],
                    "note": seg["note"],
                }

        c1, c2 = st.columns(2)
        conv_bdr = c1.slider(
            "Taux conv BDR (MQL → SQL) %",
            min_value=10.0, max_value=80.0,
            value=float(CONV_BDR_DEFAULT), step=1.0,
            help="Ingrid filtre 65% des MQLs → conv 35%",
        )
        share_noto = c2.slider(
            "Part budget notoriété (Thought Leader + Demand Gen) %",
            min_value=0.0, max_value=50.0,
            value=float(SHARE_NOTORIETE_DEFAULT), step=1.0,
            help="% du budget total alloué aux leviers de notoriété",
        )

    # ------- Allocation par segment (leviers performance) -------
    with st.expander("🎚️ Allocation par segment des leviers performance", expanded=False):
        st.caption(
            "Répartition % par levier au sein de chaque segment. Total par segment = 100%. "
            "Pré-réglé selon retours agence STAENK pour SaaS B2B RH."
        )
        allocation = {}
        cols = st.columns(len(segments))
        for col, seg_name in zip(cols, segments.keys()):
            with col:
                st.markdown(f"**{seg_name}**")
                seg_alloc = {}
                default = ALLOCATION_DEFAULT.get(seg_name, {})
                for plateforme, fmt in LEVIERS_PERF:
                    label = f"{plateforme} — {fmt}"
                    pct = st.number_input(
                        label,
                        min_value=0, max_value=100,
                        value=int(default.get((plateforme, fmt), 0)),
                        step=5,
                        key=f"alloc_{seg_name}_{plateforme}_{fmt}",
                    )
                    seg_alloc[(plateforme, fmt)] = pct
                total = sum(seg_alloc.values())
                if total != 100:
                    st.warning(f"Total = {total}% (doit faire 100%)")
                else:
                    st.success(f"Total = 100% ✓")
                allocation[seg_name] = seg_alloc

    # ------- Calcul du plan -------
    plan = compute_plan(
        df_bench=df_bench,
        segments=segments,
        allocation=allocation,
        conv_bdr_pct=conv_bdr,
        share_notoriete_pct=share_noto,
    )
    s = plan["synthese"]
    df_detail = plan["detail"]
    df_noto = plan["notoriete"]

    # ------- KPIs synthèse -------
    st.markdown("---")
    st.subheader("📊 Synthèse")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pipeline cible", f"{s['pipeline_target']/1_000_000:.2f} M€")
    c2.metric("Budget total", f"{s['budget_total']:,.0f} €".replace(",", " "))
    c3.metric("MQLs à générer", f"{s['mqls_target']:,.0f}".replace(",", " "))
    c4.metric("ROAS attendu", f"x{s['roas']:.1f}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Budget performance", f"{s['budget_perf']:,.0f} €".replace(",", " "))
    c6.metric("Budget notoriété", f"{s['budget_notoriete']:,.0f} €".replace(",", " "))
    c7.metric("Coût par MQL moyen", f"{s['cout_par_mql']:,.0f} €".replace(",", " "))
    c8.metric("Coût par 1€ pipeline", f"{s['cout_par_euro_pipeline']*100:.1f} c€")

    # ------- Expander pédagogique : comment est calculé le ROAS ? -------
    with st.expander("🧮 Comment est calculé le ROAS attendu ?"):
        st.markdown(
            f"""
**Formule finale** : `ROAS = Pipeline cible / Budget total`

C'est un **reverse-engineering descendant** : on part du pipeline business cible
et on remonte le budget nécessaire via les CPL benchmark de chaque levier.
Pas un chiffre estimé "à la louche" — c'est un ratio mathématique.

---

**Étape 1 — Pipeline cible** ({s['pipeline_target']/1e6:.2f} M€)

Pour chaque segment : `Pipeline = SQLs cibles × ACV`

| Segment | SQLs | ACV | Pipeline |
|---|---|---|---|
| Santé | {segments['Santé']['sqls_target']} | {segments['Santé']['acv']:,} € | {segments['Santé']['sqls_target']*segments['Santé']['acv']:,} € |
| Large | {segments['Large']['sqls_target']} | {segments['Large']['acv']:,} € | {segments['Large']['sqls_target']*segments['Large']['acv']:,} € |
| Mid Market | {segments['Mid Market']['sqls_target']} | {segments['Mid Market']['acv']:,} € | {segments['Mid Market']['sqls_target']*segments['Mid Market']['acv']:,} € |
| **Total** | **{s['sqls_target']:.0f}** | — | **{s['pipeline_target']:,.0f} €** |

---

**Étape 2 — MQLs nécessaires** ({s['mqls_target']:.0f} MQLs)

`MQLs = SQLs / (Taux conv MQL→SQL)`

Avec le taux BDR actuel ({conv_bdr:.0f}%) → il faut **{s['mqls_target']:.0f} MQLs**
pour obtenir les **{s['sqls_target']:.0f} SQLs** cibles.

---

**Étape 3 — Budget performance par levier** ({s['budget_perf']:,.0f} €)

Pour chaque segment, les MQLs sont répartis sur les 4 leviers performance
(LinkedIn Conv Ads, Single Image, Google Search, DSA) selon une **allocation
calibrée pour SaaS B2B RH** (cf. `lib/plan_media.py` → `ALLOCATION_DEFAULT`).

`Budget levier = MQLs alloués × CPL médian benchmark`

→ Somme sur tous les couples (segment × levier) = **{s['budget_perf']:,.0f} €**

---

**Étape 4 — Ajout du budget notoriété** ({s['budget_notoriete']:,.0f} €)

La notoriété (Thought Leader Ads + Demand Gen) n'a pas de CPL direct.
On la budgétise comme **{share_noto:.0f}% du budget total** :

`Budget total = Budget perf / (1 - {share_noto:.0f}%)`
→ **{s['budget_total']:,.0f} €**

---

**Étape 5 — ROAS final**

`ROAS = {s['pipeline_target']:,.0f} € / {s['budget_total']:,.0f} € = x{s['roas']:.1f}`

---

**Hypothèses qui font bouger le ROAS** (curseurs sidebar) :
- **Taux conv MQL→SQL** : si on passe de 35% à 40%, on a besoin de moins de MQLs
  → moins de budget → ROAS plus élevé.
- **% notoriété** : plus on monte (ex. 25%), plus le budget total grossit → ROAS baisse.
- **SQLs cibles par segment** : ajuste directement le pipeline visé.

**Limite à anticiper en Q&R** : le ROAS est une **estimation théorique**.
Sa fiabilité dépend de la justesse des CPL benchmark et du taux MQL→SQL réel
d'Asys — à valider en M1 lors du diagnostic (axe 1 *« Écosystème mesure & data »*).
            """
        )

    # ------- Détail par segment x levier -------
    st.markdown("---")
    st.subheader("💰 Détail performance — budget par segment × levier")
    if df_detail.empty:
        st.warning("Aucun budget calculable (vérifie l'allocation et les CPL benchmark).")
    else:
        df_show = df_detail.copy()
        df_show["levier"] = df_show["plateforme"] + " — " + df_show["format"]
        df_show = df_show[[
            "segment", "levier", "allocation_pct",
            "mqls", "sqls", "cpl_benchmark", "budget", "pipeline",
        ]].rename(columns={
            "allocation_pct": "Allocation %",
            "mqls": "MQLs",
            "sqls": "SQLs",
            "cpl_benchmark": "CPL (€)",
            "budget": "Budget (€)",
            "pipeline": "Pipeline (€)",
        })
        df_show["MQLs"] = df_show["MQLs"].round(0).astype(int)
        df_show["SQLs"] = df_show["SQLs"].round(1)
        df_show["CPL (€)"] = df_show["CPL (€)"].round(0).astype(int)
        df_show["Budget (€)"] = df_show["Budget (€)"].round(0).astype(int)
        df_show["Pipeline (€)"] = df_show["Pipeline (€)"].round(0).astype(int)
        st.dataframe(df_show, width="stretch", hide_index=True)

        # ------- Camemberts répartition -------
        cga, cgb = st.columns(2)
        with cga:
            st.markdown("**Budget par segment**")
            by_seg = df_detail.groupby("segment")["budget"].sum().reset_index()
            by_seg = by_seg.sort_values("budget", ascending=False)
            colors_seg = [segments[n]["color"] for n in by_seg["segment"]]
            fig = go.Figure(data=[go.Pie(
                labels=by_seg["segment"],
                values=by_seg["budget"],
                marker=dict(colors=colors_seg),
                hole=0.4,
            )])
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, width="stretch")

        with cgb:
            st.markdown("**Budget par levier (performance)**")
            df_detail["levier"] = df_detail["plateforme"] + " — " + df_detail["format"]
            by_lev = df_detail.groupby("levier")["budget"].sum().reset_index()
            by_lev = by_lev.sort_values("budget", ascending=False)
            fig2 = go.Figure(data=[go.Pie(
                labels=by_lev["levier"],
                values=by_lev["budget"],
                hole=0.4,
            )])
            fig2.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, width="stretch")

    # ------- Notoriété -------
    st.markdown("---")
    st.subheader("📣 Budget notoriété (Thought Leader + Demand Gen)")
    if df_noto.empty or df_noto["budget"].sum() == 0:
        st.info("Pas de budget notoriété (part = 0%).")
    else:
        df_n = df_noto.copy()
        df_n["levier"] = df_n["plateforme"] + " — " + df_n["format"]
        df_n = df_n[["levier", "allocation_pct", "cpm_benchmark", "budget", "impressions"]].rename(
            columns={
                "allocation_pct": "Allocation %",
                "cpm_benchmark": "CPM (€)",
                "budget": "Budget (€)",
                "impressions": "Impressions",
            }
        )
        df_n["CPM (€)"] = df_n["CPM (€)"].round(0).astype(int)
        df_n["Budget (€)"] = df_n["Budget (€)"].round(0).astype(int)
        df_n["Impressions"] = df_n["Impressions"].round(0).astype(int)
        st.dataframe(df_n, width="stretch", hide_index=True)


# ============================================================================
# MODE CONTENUS — types de contenu par format LinkedIn
# ============================================================================
elif mode == "🎨 Contenus":
    st.title("🎨 Types de contenu — LinkedIn")
    st.caption(
        "Bibliothèque d'angles éditoriaux calibrés SaaS B2B RH (GTA → planification). "
        "Chaque type est positionné sur le funnel et noté en engagement attendu / effort de production."
    )

    tab_tl, tab_conv = st.tabs(["💬 Thought Leader Ads", "📨 Conversation Ads"])

    def _render_format(items: list, format_name: str):
        # ---- Matrice de positionnement ----
        st.subheader("📍 Matrice — Engagement attendu × Effort de production")
        st.caption(
            "Idéal : haut à gauche (fort engagement / faible effort). "
            "Couleurs = stage funnel. Chaque point = 1 type (numéro) — légende sous le graphique."
        )

        # Numérotation globale stable
        numbered = [(i + 1, it) for i, it in enumerate(items)]

        fig = go.Figure()
        funnel_groups = {}
        for num, it in numbered:
            funnel_groups.setdefault(it["funnel"], []).append((num, it))

        for funnel_stage, group in funnel_groups.items():
            color = FUNNEL_COLORS.get(funnel_stage, "#888")
            fig.add_trace(go.Scatter(
                x=[it["effort"] for _, it in group],
                y=[it["engagement"] for _, it in group],
                mode="markers+text",
                name=funnel_stage,
                marker=dict(size=34, color=color, line=dict(width=2, color="white")),
                text=[str(num) for num, _ in group],
                textposition="middle center",
                textfont=dict(size=14, color="white", family="Arial Black"),
                hovertext=[
                    f"<b>{num}. {it['nom']}</b><br>{it['angle']}<br>"
                    f"Funnel : {it['funnel']}<br>"
                    f"Engagement : {it['engagement']}/5  &nbsp;  Effort : {it['effort']}/5"
                    for num, it in group
                ],
                hoverinfo="text",
            ))
        fig.update_layout(
            xaxis=dict(
                title="Effort de production (1 = facile, 5 = lourd)",
                range=[0.3, 5.7], dtick=1,
                showgrid=True, gridcolor="#eee",
            ),
            yaxis=dict(
                title="Engagement attendu (1 = faible, 5 = très fort)",
                range=[0.3, 5.7], dtick=1,
                showgrid=True, gridcolor="#eee",
            ),
            height=480, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(title="Stage funnel", orientation="h", y=-0.18, x=0),
            plot_bgcolor="#fafafa",
        )
        st.plotly_chart(fig, width="stretch")

        # ---- Légende numérotée ----
        st.markdown("**Légende numérotée**")
        legend_cols = st.columns(2)
        half = (len(numbered) + 1) // 2
        for col_idx, sub in enumerate([numbered[:half], numbered[half:]]):
            with legend_cols[col_idx]:
                lines = []
                for num, it in sub:
                    color = FUNNEL_COLORS.get(it["funnel"], "#888")
                    lines.append(
                        f"<div style='margin:4px 0;font-size:0.92em;'>"
                        f"<span style='display:inline-block;width:24px;height:24px;border-radius:50%;"
                        f"background:{color};color:white;text-align:center;line-height:24px;"
                        f"font-weight:bold;font-size:0.85em;margin-right:8px;'>{num}</span>"
                        f"<b>{it['nom']}</b> "
                        f"<span style='color:#888;font-size:0.85em;'>· {it['funnel']}</span>"
                        f"</div>"
                    )
                st.markdown("".join(lines), unsafe_allow_html=True)

        # ---- Cards détaillées ----
        st.markdown("---")
        st.subheader(f"🗂️ {len(items)} types de contenu — {format_name}")

        # 2 cards par ligne
        for i in range(0, len(items), 2):
            cols = st.columns(2)
            for col, (item, num) in zip(cols, [(items[j], j+1) for j in range(i, min(i+2, len(items)))]):
                color = FUNNEL_COLORS.get(item["funnel"], "#888")
                with col:
                    auteur_or_duree = item.get("auteur_type") or item.get("duree_offre", "")
                    auteur_label = "Auteur" if "auteur_type" in item else "Format"
                    st.markdown(
                        f"""
<div style="
    border-left: 4px solid {color};
    background: #fafafa;
    padding: 16px 18px;
    border-radius: 6px;
    margin-bottom: 8px;
    height: 100%;
">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <h4 style="margin:0 0 4px 0;color:#222;">
      <span style='display:inline-block;width:26px;height:26px;border-radius:50%;
      background:{color};color:white;text-align:center;line-height:26px;
      font-size:0.85em;margin-right:8px;'>{num}</span>
      {item['nom']}
    </h4>
    <span style="
        background:{color};color:white;font-size:0.75em;
        padding:3px 10px;border-radius:12px;font-weight:600;
        white-space:nowrap;margin-left:8px;
    ">{item['funnel']}</span>
  </div>
  <p style="color:#555;font-size:0.92em;margin:6px 0 12px 0;font-style:italic;">
    {item['angle']}
  </p>
  <p style="margin:6px 0;font-size:0.88em;">
    <b>{auteur_label} :</b> {auteur_or_duree}
  </p>
  <p style="margin:6px 0;font-size:0.88em;">
    <b>Engagement :</b> {'★' * item['engagement']}{'☆' * (5 - item['engagement'])}
    &nbsp;&nbsp;<b>Effort :</b> {'●' * item['effort']}{'○' * (5 - item['effort'])}
  </p>
  <div style="
    background:white;border-left:3px solid {color};
    padding:10px 12px;margin:10px 0;font-size:0.88em;color:#333;
  ">
    <b style="color:{color};">Exemple :</b><br>{item['exemple']}
  </div>
  <p style="margin:6px 0 0 0;font-size:0.82em;color:#666;">
    🎯 KPI clé : {item['kpi']}
  </p>
</div>
                        """,
                        unsafe_allow_html=True,
                    )

    with tab_tl:
        _render_format(CONTENUS["Thought Leader Ads"], "Thought Leader Ads")

    with tab_conv:
        _render_format(CONTENUS["Conversation Ads"], "Conversation Ads")


# ============================================================================
# MODE STRATÉGIE — plan d'action, ABM, automatisations, GEO LLM
# ============================================================================
elif mode == "🚀 Stratégie":
    st.title("🚀 Stratégie — Audit Asys / Chronos")
    st.caption(
        "Plan d'action 1/3/6 mois, nouveau levier ABM, automatisations IA et stratégie "
        "GEO (LLM Optimization) sur la thématique « planification »."
    )

    tab_plan, tab_abm, tab_auto, tab_geo = st.tabs([
        "🗓️ Plan 1/3/6 mois",
        "🆕 Levier ABM LinkedIn",
        "🤖 Automatisations & IA",
        "🔮 Stratégie GEO (LLM)",
    ])

    # ----- Tab 1 : Plan 1/3/6 mois -----
    with tab_plan:
        st.subheader("Roadmap 6 mois")
        phases = [
            {
                "label": "Mois 1",
                "title": "Fondations & Quick Wins",
                "color": "#3498db",
                "actions": [
                    ("Audit technique du tracking",
                     "Audit complet server-side pour réaligner la data HubSpot et les régies "
                     "publicitaires (Google Ads, LinkedIn Ads, Meta). Vérification du dataLayer, "
                     "des événements de conversion et de la déduplication leads."),
                    ("Transfo CRM & Conversions hors ligne",
                     "Amélioration de la transformation dans HubSpot (qualification BDR, "
                     "scoring) <b>+ mise en place des conversions hors ligne</b> pour tracker "
                     "le bas de funnel (RDV qualifié, opportunité, contrat signé) et "
                     "<b>remonter ces données à Google Ads et LinkedIn Ads via Zapier</b>. "
                     "Les algorithmes optimisent ainsi sur de vraies conversions ventes "
                     "plutôt que sur des MQLs."),
                    ("Optimisation SEA existant",
                     "Recentrage sur mots-clés intentionnels par secteur Chronos : "
                     "<b>Santé</b> (« logiciel planning hôpital », « GTA CHU »), "
                     "<b>Public</b> (« logiciel gestion temps collectivité », « WFM mairie »), "
                     "<b>Multi-sites privé</b> (« planning multi-sites industrie », « WFM retail »). "
                     "Audit search terms, négatifs systématiques."),
                    ("Cartographie comptes cibles par secteur",
                     "Build des 3 target lists ABM dans HubSpot : "
                     "<b>500 comptes Santé</b> (CHU, groupes hospitaliers privés, EHPAD >5000), "
                     "<b>300 comptes Public</b> (régions, métropoles, conseils départementaux), "
                     "<b>400 comptes Multi-sites privés</b> (industrie, retail, services). "
                     "Prérequis indispensable au pilote ABM M3."),
                ],
            },
            {
                "label": "Mois 3",
                "title": "Lancement & Itération",
                "color": "#e58e26",
                "actions": [
                    ("Déploiement campagnes paid",
                     "LinkedIn Ads (Conv. Ads, Single Image, Thought Leader) + Google Ads "
                     "(Search, DSA, Demand Gen) selon allocation segment."),
                    ("Landing Pages dédiées par segment",
                     "1 LP par segment (Santé / Large / Mid Market) en collaboration avec "
                     "<b>Baptiste (Design)</b>. Message-match strict avec annonces. "
                     "Variante secteur public pour Large avec angle conformité RGPD + achat public."),
                    ("Pilote ABM Santé (500 comptes CHU)",
                     "1<sup>er</sup> pilote ABM <b>focus segment Santé</b> car ACV élevé et "
                     "cycle décisionnel structuré. Séquence Conv Ads + Single Image retargeting "
                     "+ <b>« Guide planification CHU »</b> (Lola). Go/no-go chiffré : "
                     "CPL < 350 € ET ≥ 5 RDV démo qualifiés sur 4 semaines."),
                    ("Ouverture secteur public — Search & DSA appels d'offres",
                     "Campagne dédiée <b>collectivités / hôpitaux publics</b> via Google Search "
                     "(kw « logiciel gestion temps collectivité », « WFM secteur public ») "
                     "+ DSA sur landing pages secteur public. Veille active sur BOAMP et "
                     "plateformes AWS Achat — alerte Slack à Juline sur les marchés publics WFM."),
                    ("Baromètre Planification Multi-sites (étude propriétaire)",
                     "Lancement avec MyRHline + La Gazette des Communes d'un baromètre "
                     "<b>200 DRH multi-sites (privé + public)</b>. Alimente le contenu Q4 LLM, "
                     "les pages piliers de Baptiste, et la stratégie de pitch presse Q4."),
                ],
            },
            {
                "label": "Mois 6",
                "title": "Scale & Rentabilité",
                "color": "#1f9d55",
                "actions": [
                    ("Analyse ROI réel — fin de funnel",
                     "Mesure basée sur les <b>contrats signés</b> (pas sur les MQLs ou SQLs). "
                     "Boucle complète CRM → reporting. Modèle d'attribution data-driven activé "
                     "dans Google Ads (≥ 300 conversions cumulées atteintes)."),
                    ("Ajustement budgets par levier",
                     "Réallocation vers les leviers qui génèrent le plus de pipeline signé. "
                     "Fermeture des leviers sous-performants."),
                    ("Scale ABM Privé Multi-sites (industrie / retail)",
                     "Réplication du playbook ABM validé sur Santé au segment <b>Privé "
                     "Multi-sites</b> : 400 comptes industrie + retail, angles spécifiques "
                     "(planning multi-sites, gestion des roulements 3×8, conformité conventions "
                     "collectives sectorielles). Ingrid (BDR) sécurise la capacity démo."),
                    ("Test levier 2 — Go/No-Go data-driven",
                     "Selon résultats M3, lancement d'<b>un 2<sup>e</sup> nouveau levier</b> : "
                     "soit <b>G2/Capterra paid</b> (si SoV review déjà engagée par Ingrid), "
                     "soit <b>podcast sponsorisé secteur public</b> (La Gazette des Communes / "
                     "Acteurs Publics) si l'ouverture public est rentable."),
                ],
            },
        ]

        cols = st.columns(3)
        for col, ph in zip(cols, phases):
            with col:
                actions_html = "".join([
                    f"<div style='margin:10px 0;padding:10px 12px;background:white;"
                    f"border-left:3px solid {ph['color']};border-radius:4px;'>"
                    f"<b style='color:{ph['color']};font-size:0.95em;'>{title}</b>"
                    f"<p style='margin:4px 0 0 0;font-size:0.88em;color:#444;'>{desc}</p>"
                    f"</div>"
                    for title, desc in ph["actions"]
                ])
                st.markdown(
                    f"""
<div style="
    background:#fafafa; border-top:4px solid {ph['color']};
    border-radius:6px; padding:18px; height:100%;
">
  <div style="
    background:{ph['color']};color:white;display:inline-block;
    padding:4px 14px;border-radius:14px;font-size:0.82em;font-weight:600;
    margin-bottom:10px;
  ">{ph['label']}</div>
  <h3 style="margin:6px 0 12px 0;color:#222;">{ph['title']}</h3>
  {actions_html}
</div>
                    """,
                    unsafe_allow_html=True,
                )

    # ----- Tab 2 : Levier ABM LinkedIn -----
    with tab_abm:
        st.subheader("LinkedIn Ads en stratégie ABM (Account-Based Marketing)")
        st.markdown(
            """
<div style="background:#fafafa;border-left:4px solid #0a66c2;padding:18px 20px;border-radius:6px;">
  <h4 style="margin:0 0 6px 0;color:#0a66c2;">🎯 Pourquoi ce levier ?</h4>
  <p style="margin:0;font-size:0.95em;color:#333;">
    Canal <b>roi du B2B SaaS RH</b> : ciblage chirurgical des <b>DRH / DSI</b> sur les
    comptes cibles (Hôpitaux, Mid Market, Large) plutôt qu'une diffusion large.
    L'ABM transforme la dépense média en investissement comptes.
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("&nbsp;")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
<div style="background:white;border:1px solid #e0e0e0;border-radius:6px;padding:18px;height:100%;">
  <h4 style="margin:0 0 12px 0;color:#222;">🧪 Test 2 à 4 semaines</h4>
  <ul style="margin:0;padding-left:18px;font-size:0.92em;color:#444;line-height:1.7;">
    <li><b>Échantillon</b> : 500 comptes exclusifs (segment Santé prioritaire)</li>
    <li><b>Ciblage</b> : DRH, DSI, Resp. SIRH des comptes listés (LinkedIn Matched Audiences)</li>
    <li><b>Format</b> : Conversation Ads + Single Image Ads en retargeting</li>
    <li><b>Lead magnet</b> : « Guide de la planification sous contrainte pour les CHU » (par <b>Lola</b>)</li>
    <li><b>CTA</b> : Demande de démo directe</li>
  </ul>
</div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
<div style="background:white;border:1px solid #e0e0e0;border-radius:6px;padding:18px;height:100%;">
  <h4 style="margin:0 0 12px 0;color:#222;">📈 Résultats attendus</h4>
  <ul style="margin:0;padding-left:18px;font-size:0.92em;color:#444;line-height:1.7;">
    <li><b>Reach qualifié</b> : 100% de la base auprès des décideurs ciblés</li>
    <li><b>Volume</b> : 15-30 demandes de démo qualifiées sur 4 semaines</li>
    <li><b>CPL prévisionnel</b> : 200-350 € (premium ciblage ABM)</li>
    <li><b>Pipeline généré</b> : 5-10 transactions HubSpot post-test (segment Santé, ACV 50k€)</li>
    <li><b>Apprentissages</b> : valider angles + scaler aux segments Large + MidMkt</li>
  </ul>
</div>
                """,
                unsafe_allow_html=True,
            )

        # ----- Variante ABM secteur public -----
        st.markdown("&nbsp;")
        st.markdown(
            """
<div style="background:#fff5e6;border-left:4px solid #e58e26;border-radius:6px;padding:18px 22px;margin:18px 0 8px 0;">
  <h4 style="margin:0 0 8px 0;color:#e58e26;">🏛️ Variante ABM Secteur Public (Chronos cible >5000)</h4>
  <p style="margin:0;font-size:0.93em;color:#333;line-height:1.55;">
    L'ABM <b>secteur public</b> obéit à une logique radicalement différente de l'ABM LinkedIn privé :
    cycles de décision longs (12-18 mois), <b>passage par appel d'offres obligatoire au-dessus
    de 40 k€ HT</b>, audience LinkedIn moins active (DRH/DSI fonction publique territoriale et hospitalière),
    poids fort des prescripteurs (SG, DGS, élus). On change donc complètement de stack et de séquence.
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )

        c3, c4 = st.columns(2)
        with c3:
            st.markdown(
                """
<div style="background:white;border:1px solid #e0e0e0;border-radius:6px;padding:18px;height:100%;">
  <h4 style="margin:0 0 12px 0;color:#222;">🧪 Test 4 semaines — secteur public</h4>
  <ul style="margin:0;padding-left:18px;font-size:0.92em;color:#444;line-height:1.7;">
    <li><b>Échantillon</b> : 100 comptes prioritaires (régions, métropoles >50k habitants, conseils départementaux, CHU publics)</li>
    <li><b>Ciblage primaire</b> : <b>Google Search + DSA</b> sur kw « logiciel gestion temps collectivité », « WFM hôpital public », « marché public planification »</li>
    <li><b>Ciblage secondaire</b> : LinkedIn Single Image sur titres DGA RH / DRH fonction publique territoriale</li>
    <li><b>Veille marchés publics</b> : BOAMP + AWS Achat + PLACE — alerte Slack auto sur tout marché contenant « GTA », « WFM », « planification » > 40 k€</li>
    <li><b>Lead magnet</b> : « Guide RGPD + achat public WFM 2026 » (par <b>Laure</b>) + <b>cas d'usage Région</b> co-écrit avec un client public référent</li>
    <li><b>CTA</b> : RDV cadrage (pas démo directe — cycle plus long)</li>
  </ul>
</div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                """
<div style="background:white;border:1px solid #e0e0e0;border-radius:6px;padding:18px;height:100%;">
  <h4 style="margin:0 0 12px 0;color:#222;">📈 Résultats attendus — secteur public</h4>
  <ul style="margin:0;padding-left:18px;font-size:0.92em;color:#444;line-height:1.7;">
    <li><b>Volume</b> : 5-10 RDV cadrage qualifiés en 4 semaines (moins que privé mais ACV plus structurant)</li>
    <li><b>CPL prévisionnel</b> : 400-600 € (audience plus rare, Google premium)</li>
    <li><b>Pipeline généré</b> : 2-4 dossiers entrants au pipeline 12 mois (ACV 80-150 k€ public)</li>
    <li><b>Veille AO</b> : ≥ 3 réponses à appels d'offres déclenchées sur la période</li>
    <li><b>Go/No-Go M6</b> : si CPL < 600 € ET ≥ 2 dossiers entrés au pipeline → scale + recrutement BDR dédié public</li>
  </ul>
</div>
                """,
                unsafe_allow_html=True,
            )

    # ----- Tab 3 : Automatisations & IA -----
    with tab_auto:
        st.subheader("Automatisations & IA — 2 leviers prioritaires")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
<div style="background:#fafafa;border-left:4px solid #e74c3c;border-radius:6px;padding:18px;height:100%;">
  <div style="
    background:#e74c3c;color:white;display:inline-block;
    padding:3px 10px;border-radius:10px;font-size:0.78em;font-weight:600;
  ">Auto 1 — Sales</div>
  <h4 style="margin:8px 0 10px 0;color:#222;">⚡ Lead Scoring & Alertes BDR</h4>
  <p style="font-size:0.92em;color:#444;margin:0 0 10px 0;">
    Connecter via <b>Webhook / Zapier</b> le comportement de navigation des comptes
    stratégiques à HubSpot.
  </p>
  <div style="background:white;border-radius:4px;padding:10px 12px;font-size:0.88em;color:#333;">
    <b style="color:#e74c3c;">Trigger type :</b><br>
    Un compte « Hôpital » ciblé visite la page <b>tarifs</b> + la page <b>Chronos</b><br>
    →&nbsp;&nbsp;<b>Alerte Slack instantanée</b> à <b>Ingrid (BDR)</b><br>
    →&nbsp;&nbsp;Rappel téléphonique dans la journée
  </div>
  <p style="font-size:0.85em;color:#666;margin:10px 0 0 0;">
    🎯 <b>Impact :</b> taux de transformation MQL→SQL boosté (35% → 45-50%) sur les comptes ABM.
  </p>
</div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
<div style="background:#fafafa;border-left:4px solid #9b59b6;border-radius:6px;padding:18px;height:100%;">
  <div style="
    background:#9b59b6;color:white;display:inline-block;
    padding:3px 10px;border-radius:10px;font-size:0.78em;font-weight:600;
  ">Auto 2 — Créa</div>
  <h4 style="margin:8px 0 10px 0;color:#222;">🤖 Analyse IA des performances créatives</h4>
  <p style="font-size:0.92em;color:#444;margin:0 0 10px 0;">
    Script connecté à l'<b>API Claude</b> qui analyse chaque semaine les performances
    des créas et génère les briefs des prochaines itérations.
  </p>
  <div style="background:white;border-radius:4px;padding:10px 12px;font-size:0.88em;color:#333;">
    <b style="color:#9b59b6;">Pipeline hebdo :</b><br>
    1. Pull perfs visuels (<b>Baptiste</b>) + textes (<b>Lola</b> / <b>Laure</b>)<br>
    2. Claude identifie patterns gagnants (angles, hooks, formats)<br>
    3. Génération auto de briefs <i>(cahiers des charges)</i> visuels + copy <i>(textes d'annonces)</i> pour la semaine suivante
  </div>
  <p style="font-size:0.85em;color:#666;margin:10px 0 0 0;">
    🎯 <b>Impact :</b> CTR ads +20-30% en 8 semaines, divise par 2 le temps de brief créa.
  </p>
</div>
                """,
                unsafe_allow_html=True,
            )

        # ---- Architecture technique détaillée Auto 2 ----
        st.markdown("---")
        st.subheader("🔧 Auto 2 — Brief auto Design via Slack (avec visuels sources)")
        st.caption(
            "Comment l'analyse IA hebdomadaire produit un brief créa exploitable directement "
            "par Baptiste (Design) — message Slack contextualisé avec les visuels sources "
            "qui ont performé."
        )

        steps2 = [
            {
                "num": "1",
                "icon": "📥",
                "title": "Pull des données ads (lundi 7h)",
                "desc": (
                    "Script Python tiré chaque lundi qui récupère via APIs : <b>Google Ads</b> "
                    "(GAQL sur les 14 derniers jours) + <b>LinkedIn Ads</b> (Marketing API "
                    "Reporting). Données par créa : impressions, clics, CTR, dépense, conv, CPL."
                ),
                "tech": "google-ads-python · linkedin-api · pandas",
            },
            {
                "num": "2",
                "icon": "🖼️",
                "title": "Récupération des assets visuels",
                "desc": (
                    "Pour chaque créa, le script télécharge l'image source (asset URL Google "
                    "Ads / LinkedIn Ads) et la stocke dans un bucket S3 ou Google Drive — "
                    "indexée par <code>creative_id</code> pour les retrouver plus tard."
                ),
                "tech": "boto3 · gdrive-api · cache local sur disque",
            },
            {
                "num": "3",
                "icon": "🥇",
                "title": "Identification des top performers",
                "desc": (
                    "Sur chaque format (Single Image, Video, Carrousel), tri par <b>CTR × "
                    "volume</b> et <b>CPL inverse</b>. Sélection du <b>top 3</b> et du "
                    "<b>flop 3</b> par format pour analyse comparative."
                ),
                "tech": "pandas · score composite (CTR × log(impressions) / CPL)",
            },
            {
                "num": "4",
                "icon": "🧠",
                "title": "Analyse IA des patterns gagnants",
                "desc": (
                    "Les visuels top + flop sont envoyés à <b>Claude Sonnet 4.6</b> en mode "
                    "vision. Le prompt demande d'identifier ce qui distingue les gagnants : "
                    "type d'angle (testimony / produit / chiffre), tonalité, palette, "
                    "présence de visage humain, hiérarchie texte, hook visuel."
                ),
                "tech": "Anthropic API · multimodal (image_url) · prompt structuré JSON",
            },
            {
                "num": "5",
                "icon": "✍️",
                "title": "Génération du brief créa",
                "desc": (
                    "Claude génère un brief structuré pour Baptiste : objectif, angles "
                    "validés, 3 idées de variations à produire la semaine prochaine, "
                    "do's & don'ts (basés sur les flops), formats demandés (1080×1080, "
                    "1200×627, 1920×1080)."
                ),
                "tech": "Sortie JSON parsée → template Markdown",
            },
            {
                "num": "6",
                "icon": "💬",
                "title": "Envoi Slack avec visuels attachés",
                "desc": (
                    "Message posté dans le canal <code>#design-briefs</code>, en mention "
                    "<b>@Baptiste</b>, avec : (a) le brief en Block Kit formatté, "
                    "(b) les <b>3 visuels top</b> attachés en miniature avec leurs KPIs, "
                    "(c) un lien direct vers le bucket S3/Drive pour download HD, "
                    "(d) un bouton « Créer la tâche Notion » qui pré-remplit la fiche."
                ),
                "tech": "Slack Web API (chat.postMessage + files.upload) · Block Kit",
            },
        ]

        for i in range(0, len(steps2), 2):
            cols = st.columns(2)
            for col, step in zip(cols, steps2[i:i+2]):
                with col:
                    st.markdown(
                        f"""
<div style="background:#fafafa;border-left:3px solid #9b59b6;
    border-radius:6px;padding:14px 16px;margin:6px 0;height:100%;">
  <div style="display:flex;align-items:center;margin-bottom:8px;">
    <div style="background:#9b59b6;color:white;width:30px;height:30px;
      border-radius:50%;text-align:center;line-height:30px;
      font-weight:bold;margin-right:10px;">{step['num']}</div>
    <h5 style="margin:0;color:#222;">{step['icon']} {step['title']}</h5>
  </div>
  <p style="margin:6px 0;font-size:0.88em;color:#444;line-height:1.5;">
    {step['desc']}
  </p>
  <div style="background:white;border-radius:4px;padding:6px 10px;
    font-size:0.78em;color:#666;margin-top:8px;font-family:monospace;">
    🛠️ {step['tech']}
  </div>
</div>
                        """,
                        unsafe_allow_html=True,
                    )

        # ---- Mockup du message Slack envoyé à Baptiste ----
        st.markdown("&nbsp;")
        st.markdown("**📱 Aperçu du message Slack envoyé à Baptiste — semaine 18**")

        slack_html = (
            '<div style="background:white;border:1px solid #d8d8d8;border-radius:8px;padding:0;'
            'max-width:680px;margin:8px 0;font-family:-apple-system,BlinkMacSystemFont,sans-serif;'
            'box-shadow:0 1px 3px rgba(0,0,0,0.06);">'

            # Header
            '<div style="padding:12px 16px;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;">'
            '<div style="width:36px;height:36px;border-radius:6px;background:linear-gradient(135deg,#9b59b6,#e74c3c);'
            'color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;'
            'font-size:0.9em;margin-right:10px;">🤖</div>'
            '<div>'
            '<div style="font-weight:bold;color:#1d1c1d;font-size:0.95em;">'
            'Asys Creative Bot &nbsp;'
            '<span style="background:#1264a3;color:white;font-size:0.65em;padding:2px 6px;'
            'border-radius:3px;font-weight:bold;">APP</span>'
            '</div>'
            '<div style="color:#616061;font-size:0.78em;">#design-briefs · Aujourd\'hui 8h12</div>'
            '</div>'
            '</div>'

            # Body
            '<div style="padding:14px 18px;color:#1d1c1d;font-size:0.92em;line-height:1.55;">'

            '<p style="margin:0 0 10px 0;">'
            '👋 Salut <b style="color:#1264a3;">@Baptiste</b> — voici ton brief créa de la semaine, '
            'basé sur l\'analyse des 14 derniers jours.'
            '</p>'

            '<div style="background:#f4ede4;border-left:3px solid #ecb22e;padding:10px 12px;'
            'border-radius:4px;margin:10px 0;">'
            '<b>📊 Synthèse perf semaine 17</b><br>'
            '• <b>247 conversions</b> · CPL moyen <b>198 €</b> (-12% vs S16)<br>'
            '• Format gagnant : <b>Single Image avec témoignage client + chiffre clé</b><br>'
            '• Format en chute : <b>visuels produit screenshot pur</b> (CTR ÷ 2 vs S15)'
            '</div>'

            '<p style="margin:10px 0 6px 0;"><b>🥇 Top 3 visuels (à dupliquer en variations) :</b></p>'

            '<div style="display:flex;gap:10px;margin:8px 0;">'

            '<div style="flex:1;background:#f8f8f8;border-radius:6px;padding:8px;text-align:center;">'
            '<div style="background:linear-gradient(135deg,#3498db,#2980b9);height:90px;'
            'border-radius:4px;display:flex;align-items:center;justify-content:center;'
            'color:white;font-size:0.75em;font-weight:bold;text-align:center;padding:8px;">'
            '📷 CHU Lyon —<br>« -73% litiges paie »'
            '</div>'
            '<div style="font-size:0.75em;margin-top:6px;color:#444;">'
            'CTR <b style="color:#1f9d55;">1.42%</b> · CPL <b>185 €</b>'
            '</div>'
            '</div>'

            '<div style="flex:1;background:#f8f8f8;border-radius:6px;padding:8px;text-align:center;">'
            '<div style="background:linear-gradient(135deg,#e58e26,#d35400);height:90px;'
            'border-radius:4px;display:flex;align-items:center;justify-content:center;'
            'color:white;font-size:0.75em;font-weight:bold;text-align:center;padding:8px;">'
            '📷 Calculateur ROI —<br>« 2 min, gain 50k€/an »'
            '</div>'
            '<div style="font-size:0.75em;margin-top:6px;color:#444;">'
            'CTR <b style="color:#1f9d55;">4.85%</b> · CPL <b>168 €</b>'
            '</div>'
            '</div>'

            '<div style="flex:1;background:#f8f8f8;border-radius:6px;padding:8px;text-align:center;">'
            '<div style="background:linear-gradient(135deg,#1f9d55,#16a085);height:90px;'
            'border-radius:4px;display:flex;align-items:center;justify-content:center;'
            'color:white;font-size:0.75em;font-weight:bold;text-align:center;padding:8px;">'
            '📷 Audit GTA gratuit —<br>« 15 min, scoring sur 10 »'
            '</div>'
            '<div style="font-size:0.75em;margin-top:6px;color:#444;">'
            'CTR <b style="color:#1f9d55;">3.20%</b> · CPL <b>215 €</b>'
            '</div>'
            '</div>'

            '</div>'

            '<p style="margin:14px 0 6px 0;"><b>🧠 Patterns gagnants identifiés (Claude) :</b></p>'
            '<ul style="margin:4px 0 10px 18px;font-size:0.9em;line-height:1.6;color:#333;">'
            '<li><b>Visage humain</b> en haut à gauche → +35% CTR vs visuels produit pur</li>'
            '<li><b>Chiffre fort</b> (% ou €) en typo XL → ancre l\'attention en moins d\'1s</li>'
            '<li><b>Background coloré</b> contrasté (pas de blanc) → +20% engagement LinkedIn</li>'
            '<li><b>CTA explicite</b> sur le visuel → réduit la friction au clic</li>'
            '</ul>'

            '<p style="margin:14px 0 6px 0;"><b>✏️ Brief de la semaine — 3 variations à produire :</b></p>'
            '<ol style="margin:4px 0 10px 18px;font-size:0.9em;line-height:1.7;color:#333;">'
            '<li><b>Variante CHU Lyon</b> en version Mid-Market : remplacer hôpital par '
            'DRH industrie 800 collab. + chiffre « -65% erreurs planning »</li>'
            '<li><b>Calculateur ROI</b> décliné sur la planification : nouvelle promesse '
            '« Combien coûte 1h de planning manuel par mois ? »</li>'
            '<li><b>Audit GTA</b> en format <b>vidéo 15s</b> (pour Demand Gen) : portrait CEO '
            'Asys + voix-off + logo final</li>'
            '</ol>'

            '<p style="margin:10px 0 6px 0;"><b>🎯 Formats demandés :</b></p>'
            '<ul style="margin:4px 0 12px 18px;font-size:0.9em;line-height:1.5;color:#333;">'
            '<li>1080×1080 (LinkedIn Single Image)</li>'
            '<li>1200×627 (LinkedIn link preview)</li>'
            '<li>1920×1080 + 1080×1920 (Demand Gen vidéo)</li>'
            '</ul>'

            '<div style="background:#f4f4f4;border-radius:6px;padding:8px 12px;margin:10px 0;'
            'font-size:0.85em;color:#444;">'
            '📎 <b>Sources HD attachées</b> : '
            '<a href="#" style="color:#1264a3;">visuels-top-S17.zip</a> (3 fichiers, 4.2 Mo)<br>'
            '📊 <b>Rapport perf complet</b> : '
            '<a href="#" style="color:#1264a3;">creative-perf-week17.pdf</a>'
            '</div>'

            # Boutons (en spans stylés pour éviter sanitize de <button>)
            '<div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap;">'
            '<span style="background:#007a5a;color:white;padding:8px 16px;'
            'border-radius:4px;font-weight:bold;font-size:0.85em;display:inline-block;">'
            '📋 Créer tâche Notion</span>'
            '<span style="background:white;color:#1d1c1d;border:1px solid #d8d8d8;'
            'padding:8px 16px;border-radius:4px;font-weight:bold;font-size:0.85em;display:inline-block;">'
            '💬 Discuter du brief</span>'
            '<span style="background:white;color:#1d1c1d;border:1px solid #d8d8d8;'
            'padding:8px 16px;border-radius:4px;font-weight:bold;font-size:0.85em;display:inline-block;">'
            '⏰ Reporter à demain</span>'
            '</div>'

            '</div>'
            '</div>'
        )

        try:
            st.html(slack_html)
        except AttributeError:
            # Fallback pour anciennes versions de Streamlit
            st.markdown(slack_html, unsafe_allow_html=True)

        st.caption(
            "💡 Le bouton « Créer tâche Notion » pré-remplit une fiche dans la base Design "
            "avec brief + assets liés, deadline auto à J+5. Le bouton « Discuter » ouvre "
            "un thread sur le message pour itérer avec Lola/Laure si besoin."
        )

        # ---- Architecture technique détaillée Auto 1 ----
        st.markdown("---")
        st.subheader("🔧 Auto 1 — Architecture technique détaillée")
        st.caption(
            "Comment fonctionne concrètement le Lead Scoring & Alertes BDR : "
            "du visiteur anonyme jusqu'à l'appel d'Ingrid, étape par étape."
        )

        steps = [
            {
                "num": "1",
                "icon": "🌐",
                "title": "Visite anonyme du site",
                "desc": (
                    "Un visiteur arrive sur le site Asys (page tarifs, page produit Chronos, "
                    "case study hôpital, etc.). À ce stade, il n'a rempli aucun formulaire "
                    "donc il est <b>inconnu</b> du CRM."
                ),
                "tech": "HubSpot Tracking Code (script JS) sur toutes les pages",
            },
            {
                "num": "2",
                "icon": "🔍",
                "title": "Identification de l'entreprise (Reverse IP)",
                "desc": (
                    "Un outil de <b>reverse IP lookup</b> identifie l'entreprise du visiteur "
                    "à partir de son IP (avec un taux de match de 30-50% en B2B). On obtient : "
                    "nom de l'entreprise, secteur, taille, domaine, localisation."
                ),
                "tech": "Clearbit Reveal · Albacross · Leadfeeder · Lead Forensics",
            },
            {
                "num": "3",
                "icon": "🎯",
                "title": "Match vs liste de comptes ABM",
                "desc": (
                    "L'entreprise détectée est croisée avec la <b>liste des comptes cibles</b> "
                    "stockée dans HubSpot (target accounts ABM). Si match → l'événement est "
                    "rattaché à la fiche entreprise existante (sinon, ignoré pour les alertes)."
                ),
                "tech": "HubSpot Companies (target list ABM — <i>liste de comptes cibles</i>) · workflow de matching <i>(rapprochement)</i> domaine/nom",
            },
            {
                "num": "4",
                "icon": "📊",
                "title": "Scoring comportemental cumulé",
                "desc": (
                    "Chaque événement déclenche un ajout de points sur la fiche entreprise. "
                    "Le score se cumule sur une fenêtre glissante de 7 jours. Quand le seuil "
                    "défini est franchi (ex : <b>50 points</b>), un trigger est armé."
                ),
                "tech": "HubSpot Custom Properties + Workflows (rules-based)",
            },
            {
                "num": "5",
                "icon": "⚡",
                "title": "Webhook → Zapier",
                "desc": (
                    "Le franchissement du seuil déclenche un <b>webhook HubSpot</b> qui appelle "
                    "Zapier. Zapier orchestre alors la suite : enrichissement contact, création "
                    "tâche, notification."
                ),
                "tech": "HubSpot Webhook <i>(notification automatique)</i> (trigger workflow — <i>déclencheur de flux</i>) → Zapier (orchestration multi-step <i>(plusieurs étapes)</i>)",
            },
            {
                "num": "6",
                "icon": "🪪",
                "title": "Enrichissement contacts décideurs",
                "desc": (
                    "Zapier interroge un outil d'enrichissement pour récupérer les "
                    "<b>contacts décideurs</b> de l'entreprise (DRH, DSI, Resp. SIRH) avec "
                    "email pro, LinkedIn, téléphone. Ces contacts sont créés/mis à jour "
                    "dans HubSpot et associés à l'entreprise."
                ),
                "tech": "Clearbit Prospector · Apollo.io · Cognism · Dropcontact",
            },
            {
                "num": "7",
                "icon": "📋",
                "title": "Création tâche HubSpot pour Ingrid",
                "desc": (
                    "Une tâche HubSpot est créée automatiquement, assignée à <b>Ingrid (BDR)</b>, "
                    "avec deadline 24h, contenant : nom du compte, signaux détectés, contacts "
                    "enrichis, lien vers la fiche, suggestion de pitch."
                ),
                "tech": "HubSpot Tasks API (Zapier action)",
            },
            {
                "num": "8",
                "icon": "🔔",
                "title": "Alerte Slack contextualisée",
                "desc": (
                    "Message Slack envoyé au canal <code>#abm-hot-accounts</code> et en DM à "
                    "Ingrid. Format type :<br>"
                    "<i>« 🔥 CHU de Lyon (Santé, 8 000 collab.) — 3 visites en 2j : tarifs + "
                    "Chronos + case study Bordeaux. Score 62. Contact suggéré : Marie Dupont, "
                    "DRH adjointe. Tâche créée. »</i>"
                ),
                "tech": "Slack API (incoming webhook) — formatting Block Kit",
            },
        ]

        for i in range(0, len(steps), 2):
            cols = st.columns(2)
            for col, step in zip(cols, steps[i:i+2]):
                with col:
                    st.markdown(
                        f"""
<div style="background:#fafafa;border-left:3px solid #e74c3c;
    border-radius:6px;padding:14px 16px;margin:6px 0;height:100%;">
  <div style="display:flex;align-items:center;margin-bottom:8px;">
    <div style="background:#e74c3c;color:white;width:30px;height:30px;
      border-radius:50%;text-align:center;line-height:30px;
      font-weight:bold;margin-right:10px;">{step['num']}</div>
    <h5 style="margin:0;color:#222;">{step['icon']} {step['title']}</h5>
  </div>
  <p style="margin:6px 0;font-size:0.88em;color:#444;line-height:1.5;">
    {step['desc']}
  </p>
  <div style="background:white;border-radius:4px;padding:6px 10px;
    font-size:0.78em;color:#666;margin-top:8px;font-family:monospace;">
    🛠️ {step['tech']}
  </div>
</div>
                        """,
                        unsafe_allow_html=True,
                    )

        # Stack technique + Règles de scoring
        st.markdown("&nbsp;")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(
                """
<div style="background:white;border:1px solid #e0e0e0;border-radius:6px;padding:18px;height:100%;">
  <h4 style="margin:0 0 10px 0;color:#222;">🛠️ Stack technique recommandée</h4>
  <table style="width:100%;font-size:0.88em;border-collapse:collapse;">
    <tr><td style="padding:5px 0;color:#666;width:42%;">CRM</td>
        <td style="padding:5px 0;"><b>HubSpot</b> (Marketing + Sales Pro)</td></tr>
    <tr><td style="padding:5px 0;color:#666;">Reverse IP</td>
        <td style="padding:5px 0;"><b>Clearbit Reveal</b> ou <b>Albacross</b></td></tr>
    <tr><td style="padding:5px 0;color:#666;">Enrichissement contacts</td>
        <td style="padding:5px 0;"><b>Apollo.io</b> ou <b>Dropcontact</b> (RGPD)</td></tr>
    <tr><td style="padding:5px 0;color:#666;">Orchestration</td>
        <td style="padding:5px 0;"><b>Zapier</b> (Pro pour multi-step)</td></tr>
    <tr><td style="padding:5px 0;color:#666;">Notifications</td>
        <td style="padding:5px 0;"><b>Slack</b> (incoming webhook)</td></tr>
    <tr><td style="padding:5px 0;color:#666;">Coût mensuel estimé</td>
        <td style="padding:5px 0;"><b>~ 600-1 000 €/mois</b> (hors HubSpot)</td></tr>
  </table>
  <p style="margin:12px 0 0 0;font-size:0.8em;color:#888;font-style:italic;">
    Alternative no-IP : workflow purement HubSpot sur les leads identifiés (formulaires
    remplis), avec enrichissement Clearbit Enrichment côté contact.
  </p>
</div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                """
<div style="background:white;border:1px solid #e0e0e0;border-radius:6px;padding:18px;height:100%;">
  <h4 style="margin:0 0 10px 0;color:#222;">📊 Règles de scoring (exemple)</h4>
  <table style="width:100%;font-size:0.88em;border-collapse:collapse;">
    <tr><td style="padding:5px 0;color:#444;width:75%;">Visite page tarifs</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#1f9d55;">+20 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">Visite page produit Chronos</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#1f9d55;">+15 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">Visite case study secteur cible</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#1f9d55;">+15 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">Téléchargement livre blanc / étude</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#1f9d55;">+25 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">Visite > 3 pages en 1 session</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#1f9d55;">+10 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">2e visite dans la semaine</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#1f9d55;">+15 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">Demande de démo (formulaire)</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#e74c3c;">+50 pts</b></td></tr>
    <tr><td style="padding:5px 0;color:#444;">Compte appartient à liste ABM</td>
        <td style="padding:5px 0;text-align:right;"><b style="color:#e74c3c;">×1.5</b></td></tr>
  </table>
  <div style="margin-top:12px;padding:10px;background:#fff5e6;border-radius:4px;
    border-left:3px solid #e58e26;font-size:0.85em;">
    🚨 <b>Seuil d'alerte :</b> 50 points cumulés sur fenêtre de 7 jours.<br>
    🔥 <b>Hot account :</b> 80+ points → escalade Slack + relance prioritaire H+2.
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )

    # ----- Tab 4 : Stratégie GEO (LLM Optimization) -----
    with tab_geo:
        st.subheader("Stratégie GEO — passer de 23% à leader sur « planification »")
        st.caption(
            "Generative Engine Optimization : optimiser la visibilité de la marque dans les "
            "réponses des LLM (ChatGPT, Perplexity, Claude, Gemini)."
        )

        # KPI principal
        c1, c2, c3 = st.columns(3)
        c1.metric("Score visibilité actuel", "23%")
        c2.metric("Cible 6 mois", "55%+")
        c3.metric("Cible 12 mois", "Leader thématique")

        st.markdown("---")
        st.markdown("**5 axes — toute l'équipe marketing mobilisée**")

        axes = [
            {
                "color": "#3498db",
                "team": "Lola & Laure (Content)",
                "title": "Structuration éditoriale enrichie",
                "desc": (
                    "Structurer chaque article de blog et contenu webinar avec des "
                    "<b>données structurées Schema.org</b> (FAQPage, HowTo, Article, Author, "
                    "Organization). Objectif : que les moteurs d'IA captent directement la "
                    "<b>nouvelle proposition de valeur sur la planification</b> comme source "
                    "fiable et la citent dans leurs réponses."
                ),
                "kpi": "Contenus enrichis Schema.org + mentions IA",
                "budget_eur": 2000,
                "budget_desc": "Outils Schema (Yoast/RankMath Pro ~600 €/an) + Schema.org Validator gratuit + temps interne Lola/Laure (rédaction) + dev intégration JSON-LD",
                "exemple_titre": "Article pilote : « Les 7 défis de la planification multi-sites en milieu hospitalier »",
                "exemple_html": """
<p style="margin:6px 0;"><b>Contexte :</b> article de référence (3 500 mots) signé Lola, ciblant
les DRH hospitaliers — la requête type que ces décideurs posent à ChatGPT/Perplexity.</p>

<p style="margin:10px 0 6px 0;"><b>Avant (état actuel) :</b></p>
<ul style="margin:4px 0 10px 18px;font-size:0.92em;line-height:1.6;">
  <li>Article HTML standard, balise <code>&lt;Article&gt;</code> Schema.org basique</li>
  <li>Aucune FAQ structurée → les LLM doivent deviner les questions / réponses</li>
  <li>Auteur non identifié comme expert (pas de profil Schema)</li>
</ul>

<p style="margin:10px 0 6px 0;"><b>Après (mise en place GEO) — 4 schémas imbriqués :</b></p>
<ol style="margin:4px 0 10px 18px;font-size:0.92em;line-height:1.7;">
  <li><b>FAQPage</b> avec 7 Q/R en bas d'article. Chaque question reformule un prompt LLM
    réel : « Comment gérer les plannings de gardes 24/7 dans un CHU ? », « Quels indicateurs
    suivre pour optimiser la planification hospitalière ? »</li>
  <li><b>HowTo</b> sur la section « Méthodologie de déploiement » : 5 étapes structurées,
    durée estimée, prérequis. Format directement extractible par les IA.</li>
  <li><b>Author</b> : Lola Martin, Content Manager Asys, avec <code>sameAs</code> pointant
    vers son profil LinkedIn + ses articles déjà publiés sur MyRHline → légitimité prouvée.</li>
  <li><b>Organization</b> : Asys, avec <code>sameAs</code> pointant vers G2, Capterra,
    LinkedIn, Wikipédia → croisement d'autorité multi-sources.</li>
</ol>

<p style="margin:10px 0 6px 0;"><b>Outils :</b></p>
<ul style="margin:4px 0 10px 18px;font-size:0.92em;line-height:1.6;">
  <li><b>Yoast SEO Premium</b> ou <b>Rank Math Pro</b> pour générer le balisage</li>
  <li><b>Schema.org Validator</b> + Google Rich Results Test pour valider</li>
  <li>Process : Lola rédige → Laure relit + structure FAQ → dev push schémas en JSON-LD</li>
</ul>

<p style="margin:10px 0 6px 0;"><b>Résultat attendu (8-12 semaines) :</b></p>
<ul style="margin:4px 0 0 18px;font-size:0.92em;line-height:1.6;">
  <li>Position 0 (featured snippet — <i>encadré mis en avant en haut de Google</i>) sur 3-5 requêtes longue traîne</li>
  <li>Citation directe de l'article par Perplexity / ChatGPT search dans les réponses
    « planification CHU » et « WFM hôpitaux »</li>
  <li>Template à dupliquer ensuite sur 12 articles piliers (1 par mois)</li>
</ul>
                """,
            },
            {
                "color": "#e58e26",
                "team": "Juline (Growth)",
                "title": "Tracking citations LLM",
                "desc": (
                    "Tests hebdomadaires automatisés sur les principaux LLM (ChatGPT, "
                    "Perplexity, Claude, Gemini, Google AI Overviews — <i>réponses IA en haut de Google</i>) pour mesurer "
                    "l'évolution des <b>citations de la marque Chronos / Asys</b> sur un panel "
                    "de prompts test (« meilleur logiciel planification équipe », "
                    "« WFM hôpitaux », etc.)."
                ),
                "kpi": "Share of voice IA hebdo",
                "budget_eur": 5000,
                "budget_desc": "Otterly.ai ou Profound (~300 €/mois × 3 mois = 900 €) OU script Python DIY + crédits API (OpenAI + Anthropic + Perplexity ~500 €) + Looker Studio gratuit + temps Juline setup initial (~3 j)",
                "exemple_titre": "Panel de 30 prompts × 4 LLM × run hebdomadaire automatisé",
                "exemple_html": """
<p style="margin:6px 0;"><b>Setup mis en place par Juline :</b></p>
<ul style="margin:4px 0 10px 18px;font-size:0.92em;line-height:1.6;">
  <li><b>Panel de 30 prompts</b> représentatifs du buyer journey <i>(parcours d'achat)</i>, segmenté par stage funnel :</li>
</ul>

<table style="width:100%;font-size:0.88em;border-collapse:collapse;margin:6px 0 12px 0;">
  <tr style="background:#fff5e6;">
    <th style="padding:6px;text-align:left;border-bottom:1px solid #f0c674;">Stage</th>
    <th style="padding:6px;text-align:left;border-bottom:1px solid #f0c674;">Prompt exemple</th>
  </tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;"><b>TOFU</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;">« Comment choisir un logiciel de planification d'équipes en 2026 ? »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;"><b>TOFU</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;">« Liste-moi les 5 meilleurs SaaS de gestion des temps en France »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;"><b>MOFU</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;">« Quel logiciel WFM pour un groupe hospitalier de 5 000 collaborateurs ? »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;"><b>MOFU</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;">« Asys Chronos vs Kelio : différences sur la planification ? »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;background:#fff5e6;"><b>Public</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;background:#fff5e6;">« Quel logiciel WFM pour une collectivité de 8 000 agents ? »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;background:#fff5e6;"><b>Public</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;background:#fff5e6;">« Logiciel gestion temps mairie / métropole : marché public 2026 »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;background:#eef7ff;"><b>Multi-sites</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;background:#eef7ff;">« Logiciel planning multi-sites industrie 5000 salariés »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;background:#eef7ff;"><b>Multi-sites</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;background:#eef7ff;">« WFM retail multi-magasins France — comparatif »</td></tr>
  <tr><td style="padding:6px;border-bottom:1px solid #eee;"><b>BOFU</b></td>
      <td style="padding:6px;border-bottom:1px solid #eee;">« Pourquoi choisir Asys Chronos pour la GTA ? »</td></tr>
  <tr><td style="padding:6px;"><b>BOFU</b></td>
      <td style="padding:6px;">« Avis utilisateurs Chronos planification — est-ce fiable ? »</td></tr>
</table>

<p style="margin:6px 0;font-size:0.88em;color:#666;font-style:italic;">
  Panel élargi à <b>30 prompts couvrant les 3 segments Chronos</b> (privé multi-sites, secteur public,
  santé) — le SoV est calculé par segment pour identifier où Chronos décroche.
</p>

<p style="margin:6px 0;"><b>Stack technique :</b></p>
<ul style="margin:4px 0 10px 18px;font-size:0.92em;line-height:1.6;">
  <li><b>Outils SaaS spécialisés</b> : <b>Otterly.ai</b>, <b>Profound</b> ou <b>Peec.ai</b>
    (~200-500 €/mois) — UI prête, dashboards intégrés</li>
  <li><b>Alternative DIY</b> (gratuit hors crédits API) : script Python qui interroge
    chaque semaine les APIs OpenAI / Anthropic / Perplexity / Gemini, parse les réponses,
    pousse dans Google Sheets, dashboard <b>Looker Studio</b></li>
  <li><b>Programmation</b> : GitHub Action ou cron le lundi matin → résultats dispo le mardi</li>
</ul>

<p style="margin:10px 0 6px 0;"><b>3 KPIs trackés par Juline chaque semaine :</b></p>
<table style="width:100%;font-size:0.88em;border-collapse:collapse;">
  <tr><td style="padding:5px 0;color:#666;width:35%;">Share of Voice IA</td>
      <td style="padding:5px 0;">% de prompts où Asys/Chronos est <b>cité</b> (vs ignoré)</td></tr>
  <tr><td style="padding:5px 0;color:#666;">Position moyenne</td>
      <td style="padding:5px 0;">Quand cité, à quel rang dans la liste (1ère, 3ème, 5ème place ?)</td></tr>
  <tr><td style="padding:5px 0;color:#666;">Sentiment</td>
      <td style="padding:5px 0;">Tonalité de la mention (positive / neutre / critique)</td></tr>
</table>

<p style="margin:10px 0 6px 0;"><b>Output concret :</b></p>
<ul style="margin:4px 0 0 18px;font-size:0.92em;line-height:1.6;">
  <li>Dashboard Looker Studio partagé COMEX, refresh lundi à 8h</li>
  <li>Alerte Slack à Juline si chute > 10 pts d'une semaine sur l'autre</li>
  <li>Vue concurrence : SoV Asys vs Kelio / Bodet / Octime / Skello sur les mêmes prompts</li>
</ul>
                """,
            },
            {
                "color": "#1f9d55",
                "team": "Médias externes",
                "title": "Articles sponsorisés & autorité de domaine",
                "desc": (
                    "Négocier articles sponsorisés et achats de liens sur des plateformes "
                    "d'autorité : <b>Capterra, G2, blogs RH reconnus</b> (Parlons RH, "
                    "MyRHline, Focus RH). Objectif : que les IA, en croisant leurs sources, "
                    "<b>recommandent systématiquement Asys</b> sur la planification."
                ),
                "kpi": "Domain Rating + nb backlinks autorité",
                "budget_eur": 33000,
                "budget_desc": "G2 profil premium + incentives reviews 6 k€ · Capterra featured listing 4 k€ · MyRHline 3 articles + webinar 12 k€ · Wikipédia 3 k€ · La Gazette + Acteurs Publics 8 k€ · Reddit 0 €",
                "exemple_titre": "Campagne Q1 2026 — 3 plateformes, budget ~22 k€, 1 trimestre",
                "exemple_html": """
<p style="margin:6px 0;"><b>Plan de bataille concret par plateforme :</b></p>

<div style="background:white;border-left:3px solid #1f9d55;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#1f9d55;">1️⃣ G2.com — Devenir « Leader Mid-Market »</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Action</b> : programme de review collection <i>(collecte d'avis clients)</i> — 15 reviews vérifiées de DRH clients
      sur 6 semaines (incentive : carte cadeau 50 €)</li>
    <li><b>Objectif badge</b> : G2 Leader Mid-Market Spring 2026 sur catégorie
      « Workforce Management » <i>(gestion de la main-d'œuvre)</i> (seuil ~20 reviews avec note ≥ 4.4/5)</li>
    <li><b>Budget</b> : ~6 k€ (2 k€ G2 profil premium + 4 k€ incentives)</li>
    <li><b>Impact LLM</b> : G2 est <b>la source #1</b> citée par ChatGPT et Perplexity sur
      les requêtes comparatives B2B SaaS</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #1f9d55;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#1f9d55;">2️⃣ Capterra — Profil enrichi + témoignages</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Action</b> : profil Asys Chronos enrichi (screenshots produit, vidéo 2 min,
      cas d'usage par taille d'entreprise) + 10 témoignages clients courts</li>
    <li><b>Backlinks</b> : depuis le profil Capterra vers les pages produit Asys et 2 articles
      blog (planification CHU + GTA Mid-Market)</li>
    <li><b>Budget</b> : ~4 k€ (Capterra featured listing 3 mois)</li>
    <li><b>Impact LLM</b> : citations multiples sur prompts « top SaaS WFM » et « comparatif
      logiciels GTA »</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #1f9d55;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#1f9d55;">3️⃣ MyRHline — 3 publications + 1 webinar</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Article 1</b> (sponsorisé) : « Tribune CEO Asys — Pourquoi la GTA classique va
      disparaître d'ici 2028 »</li>
    <li><b>Article 2</b> (étude propriétaire) : « Baromètre Planification 2026 — résultats
      sur 200 DRH français »</li>
    <li><b>Article 3</b> (cas d'usage) : « Comment le CHU de Lyon a divisé ses litiges paie
      par 3 grâce à Asys »</li>
    <li><b>Webinar joint</b> : « Réforme du temps de travail 2026 » avec MyRHline + avocat
      RH partenaire (450 inscrits estimés)</li>
    <li><b>Budget</b> : ~12 k€ (3 articles 8 k€ + webinar 4 k€)</li>
    <li><b>Impact</b> : 3 backlinks DR 60+ vers les pages piliers Asys + co-branding
      sur audience MyRHline (40 k abonnés newsletter)</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #1f9d55;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#1f9d55;">4️⃣ Wikipédia — Page éditeur + page produit</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Action</b> : création (ou enrichissement) d'une page Wikipédia Asys + section dédiée
      Chronos avec sources tierces vérifiables (presse, études, sources institutionnelles).
      Sous-traitance à un rédacteur Wikipédia expérimenté pour éviter la suppression éditoriale.</li>
    <li><b>Pourquoi critique</b> : Wikipédia est <b>la source #1</b> ingérée par tous les LLM
      (ChatGPT, Claude, Perplexity, Gemini). Une page absente = invisibilité structurelle.</li>
    <li><b>Budget</b> : ~3 k€ (rédacteur Wikipédia + dossier de sources documentaires)</li>
    <li><b>Impact LLM</b> : présence assurée dans les réponses « Qu'est-ce qu'Asys ? » /
      « Éditeurs SaaS GTA en France » + signal d'autorité pour les autres LLM.</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #1f9d55;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#1f9d55;">5️⃣ Médias secteur public — La Gazette des Communes & Acteurs Publics</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Pourquoi</b> : Chronos cible 20% de son pipeline sur le secteur public (collectivités,
      hôpitaux publics). MyRHline ne touche pas cette audience. Il faut des médias institutionnels
      <i>(presse référente fonction publique)</i>.</li>
    <li><b>La Gazette des Communes</b> : 1 article sponsorisé + 1 webinar joint
      (« Réforme du temps de travail dans la fonction publique territoriale 2026 »).
      Audience : 80 k DRH/SG/DGS collectivités.</li>
    <li><b>Acteurs Publics</b> : 1 tribune CEO + co-branding sur une étude (« Baromètre
      planification fonction publique » — version publique du baromètre Multi-sites).</li>
    <li><b>Budget</b> : ~8 k€ (Gazette 5 k€ + Acteurs Publics 3 k€)</li>
    <li><b>Impact LLM</b> : citations sur prompts <i>« logiciel collectivité »</i> + <i>« WFM secteur public »</i>
      — sources autoritatives reconnues par les LLM sur ces requêtes spécifiques.</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #1f9d55;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#1f9d55;">6️⃣ Reddit & forums RH — Présence organique</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Action</b> : présence active sur <b>r/humanresources</b>, <b>r/sysadmin</b>
      (sujets WFM), <b>r/france</b> (politique RH), et forums FR (APEC, Welcome to the Jungle,
      Cadremploi). Un membre de l'équipe répond avec un compte identifié Asys, sans pitch
      commercial, et cite des cas d'usage.</li>
    <li><b>Pourquoi critique</b> : Reddit est dans le top 5 des sources citées par
      <b>Google AI Overviews et Perplexity</b> depuis 2024. Une thread <i>(fil de discussion)</i> bien répondue = citation
      LLM à long terme.</li>
    <li><b>Budget</b> : 0 € hors temps interne (~2h/semaine)</li>
    <li><b>Impact LLM</b> : citations sur prompts conversationnels longs (« j'hésite entre…
      qu'est-ce que vous me conseillez ? »).</li>
  </ul>
</div>

<p style="margin:6px 0;"><b>Budget global revu :</b> ~33 k€ (vs 22 k€ initial) — +Wikipédia 3 k€,
+médias secteur public (La Gazette + Acteurs Publics) 8 k€, Reddit 0 k€.</p>

<p style="margin:10px 0 6px 0;"><b>Mesure de l'impact GEO sur 12 semaines :</b></p>
<table style="width:100%;font-size:0.88em;border-collapse:collapse;">
  <tr><td style="padding:5px 0;color:#666;width:50%;">Domain Rating Ahrefs</td>
      <td style="padding:5px 0;"><b style="color:#1f9d55;">38 → 48</b> (+10 pts)</td></tr>
  <tr><td style="padding:5px 0;color:#666;">Backlinks DR > 50</td>
      <td style="padding:5px 0;"><b style="color:#1f9d55;">12 → 28</b> (+16 nouveaux)</td></tr>
  <tr><td style="padding:5px 0;color:#666;">Mentions cumulées G2 + Capterra</td>
      <td style="padding:5px 0;"><b style="color:#1f9d55;">~ 35</b> avis vérifiés</td></tr>
  <tr><td style="padding:5px 0;color:#666;">SoV LLM thématique « planification »</td>
      <td style="padding:5px 0;"><b style="color:#1f9d55;">23% → 42%</b> (objectif Q1)</td></tr>
</table>
                """,
            },
            {
                "color": "#9b59b6",
                "team": "Baptiste (Design / UX / Web)",
                "title": "Pages piliers & assets visuels citables par les LLM",
                "desc": (
                    "Refondre l'UX du site et du blog pour produire des <b>pages piliers</b> sur "
                    "la planification (structure FAQ / HowTo / comparatifs), créer des "
                    "<b>infographies et data visualisations originales</b> facilement citables, "
                    "et relancer la <b>chaîne YouTube</b> avec des vidéos courtes (60-90 s) "
                    "indexées sur les requêtes planification."
                ),
                "kpi": "Pages piliers publiées + assets visuels sourçables",
                "budget_eur": 9000,
                "budget_desc": "Dev intégration JSON-LD + refonte UX 6 pages piliers 3 k€ · Infographies Figma/Canva (temps interne Baptiste) 0 € · YouTube 24 vidéos (freelance montage 250 €/vidéo) 6 k€",
                "exemple_titre": "6 pages piliers refondues + 12 infographies + chaîne YouTube relancée (Q1)",
                "exemple_html": """
<p style="margin:6px 0;"><b>3 livrables concrets pilotés par Baptiste :</b></p>

<div style="background:white;border-left:3px solid #9b59b6;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#9b59b6;">1️⃣ 6 pages piliers « planification » refondues</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Structure type</b> : H1 question + résumé extractible 60 mots (TL;DR) + sommaire
      ancré + sections H2 sous forme de questions + FAQ schema en bas + bloc « En 1 phrase »
      par section (idéal pour citation LLM)</li>
    <li><b>Sujets</b> : « Logiciel de planification d'équipes : guide complet 2026 »,
      « Planification hospitalière : méthode », « WFM vs GTA vs planification », etc.</li>
    <li><b>Process</b> : Lola/Laure rédigent le fond → Baptiste structure l'UX (Figma)
      → dev intègre avec balisage JSON-LD complet (HowTo, FAQ, BreadcrumbList)</li>
    <li><b>Impact LLM</b> : extraits cités directement (réponse type « selon Asys, … »)</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #9b59b6;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#9b59b6;">2️⃣ 12 infographies & data viz originales</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Format</b> : 1 infographie / mois, format paysage 1200×800, données issues du
      « Baromètre Planification Asys » (étude propriétaire avec MyRHline)</li>
    <li><b>Distribution</b> : LinkedIn (Lola/Laure), <b>embed code</b> <i>(code d'intégration)</i> proposé aux médias RH
      → backlinks naturels vers la page pilier source</li>
    <li><b>Pourquoi ça marche</b> : les LLM (GPT-4o, Gemini, Claude) lisent les images. Une
      infographie originale citée par 5 sites RH = source d'autorité multi-canale</li>
    <li><b>Exemple</b> : « Coût moyen d'un litige paie lié à une planif mal gérée — étude
      sur 200 DRH français » → infographie reprise par les LLM en réponse aux prompts ROI</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #9b59b6;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#9b59b6;">3️⃣ Chaîne YouTube Asys — relance + 24 vidéos</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Format</b> : 2 vidéos/mois — 60 à 90 s (verticales, sous-titres) sur des cas
      d'usage planification + 1 long-format/mois (5-8 min, table ronde DRH)</li>
    <li><b>SEO YouTube</b> : titres en questions naturelles (« Comment planifier 500 agents
      hospitaliers ? »), <b>transcript optimisé</b> <i>(transcription vidéo)</i> et chapitres horodatés</li>
    <li><b>Pourquoi YouTube</b> : Google AI Overviews et Bing Chat citent les transcripts YouTube
      → présence sur les requêtes « comment / pourquoi / quel logiciel »</li>
    <li><b>Budget</b> : ~6 k€ Q1 (équipement léger déjà OK, freelance montage 250 €/vidéo)</li>
  </ul>
</div>
                """,
            },
            {
                "color": "#e74c3c",
                "team": "Ingrid (BDR)",
                "title": "Voice of Customer (voix du client) → FAQ Schema + collecte de reviews",
                "desc": (
                    "Ingrid est en première ligne sur la qualification : elle entend chaque "
                    "semaine les <b>vraies questions, objections et vocabulaire</b> des DRH/RRH "
                    "qu'aucun outil SEO ne capte. Deux flux : (1) réinjection dans la "
                    "<b>FAQ Schema</b> des pages piliers, (2) programme structuré de "
                    "<b>collecte de reviews G2/Capterra</b> auprès des clients qualifiés."
                ),
                "kpi": "Questions VoC capturées/mois + reviews G2/Capterra obtenues",
                "budget_eur": 1000,
                "budget_desc": "Incentives G2 reviews (15 × 50 €) 750 € · 1 propriété custom HubSpot + workflow d'extract hebdo (déjà inclus dans HubSpot Pro) 0 € · temps Ingrid 2h/sem",
                "exemple_titre": "Pipeline VoC mensuel + programme review collection (15 avis Q1)",
                "exemple_html": """
<p style="margin:6px 0;"><b>2 process pilotés par Ingrid (zéro outil supplémentaire) :</b></p>

<div style="background:white;border-left:3px solid #e74c3c;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#e74c3c;">1️⃣ Pipeline VoC → FAQ Schema (hebdomadaire)</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Process</b> : après chaque call de qualif, Ingrid logue dans HubSpot 1 propriété
      custom <code>question_recue</code> + <code>objection_principale</code> + <code>vocabulaire_metier</code></li>
    <li><b>Output</b> : extract hebdo (Juline via automation HubSpot → Google Sheet partagé) →
      top 10 questions de la semaine remontées à Lola/Laure le vendredi</li>
    <li><b>Réinjection</b> : Lola/Laure rédigent les réponses (50-80 mots, ton métier) →
      Baptiste push en FAQ Schema sur les pages piliers concernées</li>
    <li><b>Pourquoi ça marche</b> : les LLM <b>extraient en priorité les FAQ schema</b> car
      ils reproduisent le pattern Q/R conversationnel attendu en réponse</li>
    <li><b>Cible</b> : 40 nouvelles Q/R/trimestre = 40 nouveaux points de citation LLM</li>
  </ul>
</div>

<div style="background:white;border-left:3px solid #e74c3c;border-radius:4px;padding:12px 14px;margin:10px 0;">
  <h5 style="margin:0 0 6px 0;color:#e74c3c;">2️⃣ Programme review G2 / Capterra (déclenché par Ingrid)</h5>
  <ul style="margin:4px 0 4px 18px;font-size:0.9em;line-height:1.6;">
    <li><b>Trigger</b> <i>(déclencheur)</i> : à chaque <b>SQL signé</b> (déclaré gagné dans HubSpot), workflow <i>(flux automatisé)</i> auto
      → Ingrid reçoit une tâche J+30 pour solliciter une review G2 ou Capterra</li>
    <li><b>Script</b> : email court + lien direct + carte cadeau 50 € (G2 autorise l'incentive
      à condition de mentionner « review incentivée »)</li>
    <li><b>Objectif chiffré</b> : 15 reviews vérifiées Q1, 30 cumul Q2 → badge G2 Leader
      Mid-Market (seuil ≥ 20 reviews, note ≥ 4.4/5)</li>
    <li><b>Synergie axe Médias</b> : ces reviews alimentent le bloc « G2 » de l'axe Médias
      externes — c'est Ingrid qui les collecte, pas un prestataire externe</li>
    <li><b>Bonus</b> : les verbatims des reviews G2 sont publics et <b>scrappés par les LLM</b>
      → source d'avis « clients réels » qui pèse lourd dans les réponses comparatives</li>
  </ul>
</div>

<p style="margin:10px 0 6px 0;"><b>Synergie avec les autres axes :</b></p>
<ul style="margin:4px 0 0 18px;font-size:0.92em;line-height:1.6;">
  <li><b>Lola/Laure</b> : reçoivent les questions VoC chaque vendredi → calendrier éditorial alimenté</li>
  <li><b>Baptiste</b> : intègre les FAQ Schema sur les pages piliers</li>
  <li><b>Juline</b> : automatise l'extract HubSpot + le workflow de relance review J+30</li>
  <li><b>Médias externes</b> : les reviews G2 collectées par Ingrid déverrouillent le badge G2 Leader</li>
</ul>
                """,
            },
        ]

        for axe in axes:
            st.markdown(
                f"""
<div style="background:#fafafa;border-left:4px solid {axe['color']};
    border-radius:6px;padding:16px 20px;margin:10px 0;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <h4 style="margin:0;color:#222;">{axe['title']}</h4>
    <span style="background:{axe['color']};color:white;font-size:0.78em;
      padding:3px 12px;border-radius:12px;font-weight:600;">
      Avec {axe['team']}
    </span>
  </div>
  <p style="margin:10px 0;font-size:0.93em;color:#333;line-height:1.6;">
    {axe['desc']}
  </p>
  <p style="margin:6px 0 0 0;font-size:0.85em;color:{axe['color']};">
    🎯 <b>KPI suivi :</b> {axe['kpi']}
  </p>
  <p style="margin:6px 0 0 0;font-size:0.85em;color:{axe['color']};">
    💰 <b>Budget Q1 :</b> {axe['budget_eur']:,} €
    <span style="color:#666;font-style:italic;font-weight:normal;"> — {axe['budget_desc']}</span>
  </p>
</div>
                """.replace(",", " "),
                unsafe_allow_html=True,
            )
            with st.expander(f"💡 Exemple concret — {axe['exemple_titre']}"):
                st.markdown(axe["exemple_html"], unsafe_allow_html=True)

        # --- Répartition budgétaire GEO (Q1) — pie chart ---
        st.markdown("---")
        st.subheader("💰 Répartition budgétaire GEO — Q1 (3 mois)")

        labels = [a["title"] for a in axes]
        values = [a["budget_eur"] for a in axes]
        colors = [a["color"] for a in axes]
        teams  = [a["team"] for a in axes]
        total_budget_geo = sum(values)

        c1, c2 = st.columns([3, 2])

        with c1:
            fig_geo = go.Figure(
                data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.45,
                    marker=dict(colors=colors, line=dict(color="white", width=2)),
                    textposition="outside",
                    textinfo="label+percent",
                    hovertemplate="<b>%{label}</b><br>%{value:,.0f} €<br>%{percent}<extra></extra>",
                    sort=False,
                )]
            )
            fig_geo.update_layout(
                showlegend=False,
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                annotations=[dict(
                    text=f"<b>{total_budget_geo/1000:.0f} k€</b><br><span style='font-size:0.7em;color:#666;'>Total Q1</span>",
                    x=0.5, y=0.5, font=dict(size=22, color="#222"), showarrow=False,
                )],
            )
            st.plotly_chart(fig_geo, width="stretch")

        with c2:
            st.markdown("**Détail par axe**")
            rows_html = ""
            for axe, v in zip(axes, values):
                pct = v / total_budget_geo * 100
                rows_html += f"""
<tr>
  <td style="padding:6px 4px;border-bottom:1px solid #eee;">
    <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{axe['color']};margin-right:6px;"></span>
    <b style="font-size:0.88em;">{axe['team']}</b>
  </td>
  <td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:right;font-size:0.88em;">
    <b>{v:,.0f} €</b>
  </td>
  <td style="padding:6px 4px;border-bottom:1px solid #eee;text-align:right;font-size:0.82em;color:#666;">
    {pct:.1f}%
  </td>
</tr>
                """.replace(",", " ")
            st.markdown(
                f"""
<table style="width:100%;border-collapse:collapse;margin:4px 0;">
  {rows_html}
  <tr>
    <td style="padding:8px 4px;border-top:2px solid #222;"><b>Total GEO Q1</b></td>
    <td style="padding:8px 4px;border-top:2px solid #222;text-align:right;"><b>{total_budget_geo:,.0f} €</b></td>
    <td style="padding:8px 4px;border-top:2px solid #222;text-align:right;color:#666;">100%</td>
  </tr>
</table>
                """.replace(",", " "),
                unsafe_allow_html=True,
            )
            st.caption(
                "**Budget = coûts externes uniquement** (outils SaaS + achats média + freelances + incentives). "
                "Le temps de l'équipe (Lola, Laure, Baptiste, Juline, Ingrid) n'est pas valorisé ici — il est déjà couvert par les salaires existants. "
                "Reconductible en Q2 hors investissements ponctuels (Wikipédia, refonte UX pages piliers, équipement YouTube)."
            )


# ============================================================================
# MODE APERÇU REPORTING — mockup du dashboard de pilotage des campagnes
# ============================================================================
elif mode == "📈 Aperçu reporting":
    st.title("📈 Aperçu — Dashboard de reporting Asys / Chronos")
    st.caption(
        "Maquette du reporting custom une fois les campagnes lancées. "
        "Données illustratives sur les 6 derniers mois, alignées avec les hypothèses du plan media. "
        "À terme : connecté aux APIs Google Ads / LinkedIn Ads / HubSpot."
    )

    # ------- Données simulées cohérentes avec le plan media -------
    months = ["Déc 2025", "Janv 2026", "Févr 2026", "Mars 2026", "Avril 2026", "Mai 2026"]
    spend_monthly  = [4500, 6200, 7800, 8500, 9200, 9800]
    mqls_monthly   = [22, 30, 38, 42, 45, 48]
    sqls_monthly   = [int(m * 0.35) for m in mqls_monthly]

    # Répartition par segment alignée sur l'objectif annuel : Santé 44% / Large 36% / Mid 20%
    # On part de la répartition cible des SQLs et on remonte le pipeline via les ACV.
    segments_names = ["Santé", "Large", "Mid Market"]
    segments_acv   = [50000, 40000, 15000]
    segments_sqls  = [21, 22, 32]   # 75 SQLs total (= sum sqls_monthly), répartis pour respecter les ratios
    segments_pipe  = [s * a for s, a in zip(segments_sqls, segments_acv)]
    segments_total = sum(segments_pipe)
    segments_share = [round(p / segments_total * 100, 1) for p in segments_pipe]
    # → Santé ≈ 43.6% (≈44) · Large ≈ 36.5% (≈36) · Mid ≈ 19.9% (≈20)

    avg_acv = segments_total / sum(segments_sqls)  # ≈ 32 133 € pondéré

    total_spend    = sum(spend_monthly)
    total_mqls     = sum(mqls_monthly)
    total_sqls     = sum(segments_sqls)        # = 75
    total_pipeline = segments_total            # = 2 410 000 €

    # ------- Top KPIs (5 cards) -------
    st.markdown("### Indicateurs clés (6 derniers mois)")
    kc = st.columns(5)
    kc[0].metric("Pipeline généré", f"{total_pipeline/1e6:.2f} M€", "+18% vs N-1")
    kc[1].metric("Spend total", f"{total_spend/1000:.1f} k€", f"+{(spend_monthly[-1]-spend_monthly[0])/spend_monthly[0]*100:.0f}% évol.")
    kc[2].metric("SQLs (Transactions HS)", f"{total_sqls}", f"+{sqls_monthly[-1]-sqls_monthly[0]} vs M1")
    kc[3].metric("Coût par SQL", f"{total_spend/total_sqls:,.0f} €".replace(",", " "), "-12% vs N-1", delta_color="inverse")
    kc[4].metric("ROAS", f"x{total_pipeline/total_spend:.1f}", "+6 pts")

    # ------- Évolution temporelle -------
    st.markdown("---")
    st.subheader("📈 Évolution mensuelle — Spend × MQLs × SQLs")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=spend_monthly, name="Spend (€)",
        marker_color="#3498db", opacity=0.7, yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=mqls_monthly, name="MQLs",
        mode="lines+markers", marker=dict(size=10),
        line=dict(color="#e58e26", width=3), yaxis="y2",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=sqls_monthly, name="SQLs",
        mode="lines+markers", marker=dict(size=10),
        line=dict(color="#1f9d55", width=3), yaxis="y2",
    ))
    fig.update_layout(
        yaxis=dict(title="Spend (€)", side="left"),
        yaxis2=dict(title="MQLs / SQLs", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", y=-0.15),
        height=380, margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="#fafafa",
    )
    st.plotly_chart(fig, width="stretch")

    # ------- Funnel + Spend par levier -------
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🔻 Funnel global (6 mois)")
        impressions = 1_500_000
        clics       = 12000
        visites_lp  = 8500
        fig_funnel = go.Figure(go.Funnel(
            y=["Impressions", "Clics", "Visites LP", "MQLs", "SQLs"],
            x=[impressions, clics, visites_lp, total_mqls, total_sqls],
            textinfo="value+percent initial",
            marker=dict(color=["#3498db", "#5dade2", "#85c1e9", "#e58e26", "#1f9d55"]),
        ))
        fig_funnel.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_funnel, width="stretch")

    with c2:
        st.subheader("💰 Répartition du spend par levier")
        leviers_lib = [
            "LinkedIn Single Image",
            "Google Ads Search",
            "LinkedIn Conv Ads",
            "Google Ads DSA",
            "LinkedIn Thought Leader",
            "Google Ads Demand Gen",
        ]
        spend_par_levier = [13800, 11200, 9600, 4800, 4500, 1900]
        fig_pie = go.Figure(go.Pie(
            labels=leviers_lib,
            values=spend_par_levier,
            hole=0.45,
            textinfo="label+percent",
            textposition="outside",
        ))
        fig_pie.update_layout(
            height=380, margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_pie, width="stretch")

    # ------- Performance par levier -------
    st.markdown("---")
    st.subheader("📊 Performance par levier (cumul 6 mois)")

    mqls_par_levier = [60, 55, 42, 22, 18, 8]
    sqls_par_levier = [21, 19, 15, 8, 6, 3]
    pipe_par_levier = [s * avg_acv for s in sqls_par_levier]

    df_perf = pd.DataFrame({
        "Levier": leviers_lib,
        "Spend (€)": spend_par_levier,
        "MQLs": mqls_par_levier,
        "SQLs": sqls_par_levier,
        "Pipeline (€)": pipe_par_levier,
    })
    df_perf["CPL (€)"]      = (df_perf["Spend (€)"] / df_perf["MQLs"]).round(0).astype(int)
    df_perf["Coût/SQL (€)"] = (df_perf["Spend (€)"] / df_perf["SQLs"]).round(0).astype(int)
    df_perf["ROAS"]         = (df_perf["Pipeline (€)"] / df_perf["Spend (€)"]).round(1)
    df_perf = df_perf.sort_values("Pipeline (€)", ascending=False).reset_index(drop=True)

    df_show = df_perf.copy()
    df_show["Spend (€)"]    = df_show["Spend (€)"].apply(lambda x: f"{x:,}".replace(",", " "))
    df_show["Pipeline (€)"] = df_show["Pipeline (€)"].apply(lambda x: f"{x:,}".replace(",", " "))
    df_show["ROAS"]         = df_show["ROAS"].apply(lambda x: f"x{x}")

    st.dataframe(df_show, width="stretch", hide_index=True)

    # ------- Pipeline par segment + Top créatives -------
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("🏥 Pipeline par segment")
        st.caption(
            f"Répartition cible : **Santé 44% · Large 36% · Mid Market 20%** "
            f"(objectif annuel 4,5 M€ → mockup 6 mois ≈ {total_pipeline/1e6:.2f} M€)."
        )
        segments_cpl = [380, 280, 200]
        colors_seg   = ["#e74c3c", "#3498db", "#9b59b6"]

        fig_seg = go.Figure(go.Bar(
            x=segments_names,
            y=segments_pipe,
            marker_color=colors_seg,
            text=[f"{p/1000:.0f} k€<br><b>{share}%</b>"
                  for p, share in zip(segments_pipe, segments_share)],
            textposition="outside",
        ))
        fig_seg.update_layout(
            yaxis=dict(title="Pipeline (€)"),
            height=340, margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="#fafafa",
        )
        st.plotly_chart(fig_seg, width="stretch")

        df_seg = pd.DataFrame({
            "Segment": segments_names,
            "% Pipeline": [f"{share}%" for share in segments_share],
            "SQLs": segments_sqls,
            "ACV moyen": [f"{a/1000:.0f} k€" for a in segments_acv],
            "Pipeline": [f"{p/1000:.0f} k€" for p in segments_pipe],
            "CPL moyen": [f"{c} €" for c in segments_cpl],
        })
        st.dataframe(df_seg, width="stretch", hide_index=True)

    with c4:
        st.subheader("⚡ Top 5 créatives (4 dernières semaines)")
        creas = [
            ("Storytelling CHU Lyon — DRH adjointe",   "TL Ads",         1.42, 185, "🟢"),
            ("Calculateur ROI erreurs planning",       "Conv Ads",       4.85, 168, "🟢"),
            ("Audit GTA gratuit en 15 min",            "Conv Ads",       3.20, 215, "🟢"),
            ("Démo planification multisites",          "Single Image",   0.92, 245, "🟠"),
            ("Réforme temps de travail 2026",          "Single Image",   0.78, 280, "🟠"),
        ]
        df_creas = pd.DataFrame(creas, columns=["Créa", "Format", "CTR (%)", "CPL (€)", "Statut"])
        st.dataframe(df_creas, width="stretch", hide_index=True)

        st.caption(
            "🟢 = au-dessus du benchmark · 🟠 = dans la moyenne · 🔴 = sous-performant. "
            "Section générée automatiquement chaque semaine par l'Auto 2 (analyse IA des créas)."
        )

    # ------- Note méthodo -------
    st.markdown("---")
    st.info(
        "💡 **Cette maquette est illustrative**. À terme, ce reporting sera connecté en "
        "automatique aux APIs Google Ads, LinkedIn Ads et HubSpot — refresh quotidien, "
        "alertes seuils, export PDF mensuel pour le COMEX."
    )


# ============================================================================
# MODE BENCHMARKS
# ============================================================================
elif mode == "📋 Benchmarks":
    st.title("📋 Benchmarks marché")
    st.caption("Vue complète des benchmarks par levier (SaaS B2B RH 2024-2025).")

    plateformes = ["Tous"] + sorted(df_bench["plateforme"].unique().tolist())
    p = st.selectbox("Plateforme", plateformes)
    df_view = df_bench if p == "Tous" else df_bench[df_bench["plateforme"] == p]
    st.dataframe(df_view, width="stretch", hide_index=True)

    st.markdown("---")
    st.subheader("Métadonnées par format")
    st.dataframe(df_formats, width="stretch", hide_index=True)


# ============================================================================
# MODE GLOSSAIRE — abréviations utilisées dans la restitution
# ============================================================================
elif mode == "📖 Glossaire":
    st.title("📖 Glossaire — abréviations & acronymes")
    st.caption(
        "Toutes les abréviations utilisées dans cette restitution, regroupées par thème. "
        "À ouvrir en Q&R si une définition est demandée."
    )

    GLOSSAIRE = [
        {
            "titre": "🎯 Acquisition & marketing",
            "color": "#1264a3",
            "items": [
                ("GEO", "Generative Engine Optimization", "Optimisation de la visibilité de la marque dans les réponses des LLM (ChatGPT, Claude, Perplexity, Gemini)."),
                ("AEO", "Answer Engine Optimization", "Variante de GEO centrée sur les moteurs de réponse (Bing Chat, Google AI Overviews)."),
                ("AIO", "AI Optimization", "Terme générique pour les techniques d'optimisation IA, parfois employé à la place de GEO/AEO."),
                ("SEO", "Search Engine Optimization", "Référencement naturel — visibilité organique sur Google."),
                ("SEA", "Search Engine Advertising", "Référencement payant — Google Ads, Bing Ads."),
                ("SoV", "Share of Voice", "Part de voix : % de prompts où la marque est citée vs les concurrents."),
                ("ABM", "Account Based Marketing", "Stratégie ciblée compte par compte (vs masse) — adaptée Mid Market & Large."),
                ("TOFU / MOFU / BOFU", "Top / Middle / Bottom Of Funnel", "Haut, milieu et bas de l'entonnoir de conversion."),
                ("GTA", "Gestion des Temps et des Activités", "Cœur historique de l'offre Asys / Chronos."),
                ("WFM", "Workforce Management", "Équivalent anglo-saxon de la GTA, plus large (intègre planification + budget temps)."),
                ("VoC", "Voice of Customer", "Voix du client : vocabulaire et questions remontés du terrain par Ingrid (BDR)."),
            ],
        },
        {
            "titre": "💰 KPIs paid (publicité)",
            "color": "#e58e26",
            "items": [
                ("CPC", "Coût Par Clic", "Combien je paie chaque clic sur une annonce."),
                ("CPM", "Coût Pour Mille impressions", "Coût pour 1 000 affichages d'une annonce."),
                ("CPL", "Coût Par Lead", "Coût pour générer un lead (formulaire rempli)."),
                ("CPA", "Coût Par Acquisition / Action", "Coût pour une action de conversion (lead qualifié, RDV, signature)."),
                ("CTR", "Click-Through Rate", "Taux de clic = clics / impressions."),
                ("CR", "Conversion Rate", "Taux de conversion = conversions / clics ou sessions."),
                ("CPS", "Coût Par Send", "Spécifique LinkedIn Conversation Ads : coût par message envoyé."),
                ("CPV", "Coût Par Vue", "Spécifique vidéo : coût par vue qualifiée (≥3s ou ≥10s selon plateforme)."),
                ("VTR", "View-Through Rate", "Taux de visionnage complet d'une vidéo."),
                ("LGF", "Lead Gen Form", "Formulaire natif LinkedIn pré-rempli avec les données du profil."),
            ],
        },
        {
            "titre": "📈 KPIs business",
            "color": "#1f9d55",
            "items": [
                ("ROAS", "Return On Ad Spend", "Retour sur dépense publicitaire = pipeline ou revenu / dépense pub."),
                ("ROI", "Return On Investment", "Retour sur investissement (plus large que le ROAS, intègre les coûts internes)."),
                ("CAC", "Coût d'Acquisition Client", "Coût total marketing + sales pour signer un client."),
                ("LTV", "Lifetime Value", "Valeur vie client = revenu cumulé d'un client sur sa durée de contrat."),
                ("ACV", "Annual Contract Value", "Valeur annuelle d'un contrat (clé en SaaS B2B : Santé ~50 k€, Large ~40 k€, Mid ~15 k€)."),
                ("MRR / ARR", "Monthly / Annual Recurring Revenue", "Revenu récurrent mensuel / annuel — métrique reine en SaaS."),
                ("MQL", "Marketing Qualified Lead", "Lead qualifié par le marketing (score d'engagement suffisant)."),
                ("SQL", "Sales Qualified Lead", "Lead qualifié par les Sales / BDR — RDV démo accepté."),
            ],
        },
        {
            "titre": "👥 Équipe, org & cible",
            "color": "#9b59b6",
            "items": [
                ("BDR", "Business Development Representative", "Rôle d'Ingrid : qualif des leads inbound + prospection outbound."),
                ("SDR", "Sales Development Representative", "Variante US du BDR — souvent confondus."),
                ("AE", "Account Executive", "Commercial closer qui prend le relai du BDR pour signer."),
                ("DRH / RRH / SIRH", "Directeur / Responsable RH / Système d'Information RH", "Personae cibles d'Asys."),
                ("CHU", "Centre Hospitalier Universitaire", "Cible clé du segment Santé."),
                ("COMEX", "Comité Exécutif", "Instance de direction — destinataire du reporting hebdo/mensuel."),
                ("B2B", "Business to Business", "Vente d'entreprise à entreprise (vs B2C)."),
                ("SaaS", "Software as a Service", "Logiciel en abonnement cloud — modèle économique d'Asys."),
            ],
        },
        {
            "titre": "⚙️ Tech & data",
            "color": "#7f8c8d",
            "items": [
                ("API", "Application Programming Interface", "Interface pour échanger des données entre 2 systèmes (HubSpot ↔ Ads, etc.)."),
                ("JSON-LD", "JSON for Linking Data", "Format des données structurées Schema.org embarquées dans une page HTML."),
                ("GTM", "Google Tag Manager", "Outil de gestion des tags (tracking) sans dev."),
                ("GA4", "Google Analytics 4", "Version actuelle de Google Analytics (event-based)."),
                ("UX / UI", "User Experience / User Interface", "Expérience / interface utilisateur — scope de Baptiste."),
                ("DR", "Domain Rating", "Indice d'autorité de domaine Ahrefs (0-100). Asys vise 38 → 48."),
                ("Schema.org FAQ / HowTo", "Types de données structurées", "Schémas qui décrivent une FAQ ou un mode d'emploi — directement extraits par les LLM."),
            ],
        },
        {
            "titre": "🤖 IA & LLM",
            "color": "#e74c3c",
            "items": [
                ("LLM", "Large Language Model", "Grand modèle de langage : GPT-4o, Claude, Gemini, Mistral, Llama."),
                ("AI Overviews", "Réponses IA Google", "Encadré IA en haut de Google Search depuis 2024."),
                ("Otterly / Profound / Peec.ai", "SaaS de tracking LLM", "Outils de mesure des citations de marque dans les LLM (~200-500 €/mois)."),
                ("Clay", "Outil d'enrichissement", "Plateforme de data enrichment + scoring pour leads."),
                ("n8n / Make / Zapier", "Orchestration no-code", "Plateformes d'automatisation de workflows entre apps."),
                ("HubSpot", "CRM + Marketing Automation", "CRM utilisé par Asys (source de vérité pipeline)."),
            ],
        },
    ]

    for groupe in GLOSSAIRE:
        st.markdown(
            f"""
<div style="background:{groupe['color']}11;border-left:4px solid {groupe['color']};
    border-radius:6px;padding:14px 18px;margin:14px 0 6px 0;">
  <h3 style="margin:0;color:{groupe['color']};font-size:1.1em;">{groupe['titre']}</h3>
</div>
            """,
            unsafe_allow_html=True,
        )
        rows_html = ""
        for sigle, dev, defi in groupe["items"]:
            rows_html += f"""
<tr>
  <td style="padding:8px 10px;border-bottom:1px solid #eee;width:18%;vertical-align:top;">
    <b style="color:{groupe['color']};">{sigle}</b>
  </td>
  <td style="padding:8px 10px;border-bottom:1px solid #eee;width:30%;vertical-align:top;color:#333;font-style:italic;">
    {dev}
  </td>
  <td style="padding:8px 10px;border-bottom:1px solid #eee;color:#555;line-height:1.5;">
    {defi}
  </td>
</tr>
            """
        st.markdown(
            f"""
<table style="width:100%;font-size:0.93em;border-collapse:collapse;margin:0 0 10px 0;">
  {rows_html}
</table>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.info(
        "💡 **Astuce démo** : ouvrir ce mode en cas de question du jury sur une abréviation. "
        "Tous les sigles utilisés dans les autres modes y sont définis."
    )


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
    st.dataframe(df_sources, width="stretch", hide_index=True)

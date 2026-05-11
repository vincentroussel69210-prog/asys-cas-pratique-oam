"""
Plan media : reverse engineering du pipeline cible vers le budget par levier.

Logique :
1. Pipeline cible (€) → SQLs par segment (selon ACV) → MQLs (via taux conv BDR)
2. Pour chaque segment, on répartit les MQLs sur les leviers performance selon une
   allocation type (calibrée pour SaaS B2B RH). Budget = MQLs × CPL benchmark.
3. Le budget notoriété (Thought Leader + Demand Gen) est ajouté en % du total.
"""
from dataclasses import dataclass
import pandas as pd

# ----------------------------------------------------------------------------
# Configuration par défaut - étude de cas SaaS B2B RH
# ----------------------------------------------------------------------------
SEGMENTS_DEFAULT = {
    "Santé": {
        "share_pipe_pct": 44.0,
        "acv": 50000,
        "sqls_target": 40,
        "color": "#e74c3c",
        "note": "CHU, groupes hospitaliers publics/privés, cliniques, EHPAD multi-sites — cœur historique Chronos",
    },
    "Large": {
        "share_pipe_pct": 36.0,
        "acv": 40000,
        "sqls_target": 40,
        "color": "#3498db",
        "note": "Grands comptes > 1000 salariés — privé (industrie, retail, services multi-sites) ET secteur public (régions, métropoles, conseils départementaux, collectivités)",
    },
    "Mid Market": {
        "share_pipe_pct": 20.0,
        "acv": 15000,
        "sqls_target": 60,
        "color": "#9b59b6",
        "note": "Privé 200-1000 salariés — industrie, retail/distribution, services, BTP, structures multi-sites",
    },
}

# Leviers qui génèrent du MQL direct (calculés via CPL/CPA)
LEVIERS_PERF = [
    ("LinkedIn", "Conversation Ads"),
    ("LinkedIn", "Single Image Ads"),
    ("Google Ads", "Search"),
    ("Google Ads", "DSA"),
]

# Leviers de notoriété (budget % séparé, pas de MQL direct)
LEVIERS_NOTORIETE = [
    ("LinkedIn", "Thought Leader Ads"),
    ("Google Ads", "Demand Gen"),
]

# Allocation % par segment des leviers performance
# Calibré sur retours agence STAENK pour SaaS B2B RH
ALLOCATION_DEFAULT = {
    "Santé": {
        ("Google Ads", "Search"):           35,  # kw "logiciel pointage hôpital", "GTA santé"
        ("LinkedIn", "Conversation Ads"):   30,  # ciblage précis DRH hospitalier
        ("LinkedIn", "Single Image Ads"):   25,  # audiences santé sur LinkedIn
        ("Google Ads", "DSA"):              10,  # couverture longue traîne
    },
    "Large": {
        ("LinkedIn", "Single Image Ads"):   35,  # volume sur grandes audiences HR
        ("LinkedIn", "Conversation Ads"):   30,  # DRH grands comptes
        ("Google Ads", "Search"):           25,  # cycle plus long
        ("Google Ads", "DSA"):              10,
    },
    "Mid Market": {
        ("Google Ads", "Search"):           35,  # intent fort sur 200-1000 salariés
        ("LinkedIn", "Single Image Ads"):   30,  # ciblage taille entreprise
        ("Google Ads", "DSA"):              20,  # longue traîne PME
        ("LinkedIn", "Conversation Ads"):   15,  # ciblage moins précis sur ces tailles
    },
}

# Répartition par défaut du budget notoriété entre les 2 leviers
ALLOCATION_NOTORIETE = {
    ("LinkedIn", "Thought Leader Ads"): 60,  # levier clé pour SaaS RH
    ("Google Ads", "Demand Gen"):       40,
}

CONV_BDR_DEFAULT = 35.0       # % MQL → SQL
SHARE_NOTORIETE_DEFAULT = 18.0  # % du budget total alloué à la notoriété


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def _cpl_median(df_bench: pd.DataFrame, plateforme: str, fmt: str) -> float | None:
    """Renvoie le CPL median (ou CPA pour Google) d'un levier."""
    df = df_bench[(df_bench["plateforme"] == plateforme) & (df_bench["format"] == fmt)]
    for kpi in ["CPL", "CPA"]:
        row = df[df["kpi"] == kpi]
        if not row.empty:
            return float(row.iloc[0]["mediane"])
    return None


def _cpm_median(df_bench: pd.DataFrame, plateforme: str, fmt: str) -> float | None:
    df = df_bench[(df_bench["plateforme"] == plateforme) & (df_bench["format"] == fmt)]
    row = df[df["kpi"] == "CPM"]
    return float(row.iloc[0]["mediane"]) if not row.empty else None


# ----------------------------------------------------------------------------
# Calcul du plan
# ----------------------------------------------------------------------------
def compute_plan(
    df_bench: pd.DataFrame,
    segments: dict,
    allocation: dict,
    conv_bdr_pct: float,
    share_notoriete_pct: float,
    allocation_notoriete: dict | None = None,
) -> dict:
    """
    Calcule le plan media complet.

    Retourne :
      - df_detail : 1 ligne par (segment, levier perf) avec MQLs, CPL, budget, pipeline
      - df_notoriete : 1 ligne par levier notoriété avec budget, impressions
      - synthese : totaux globaux
    """
    if allocation_notoriete is None:
        allocation_notoriete = ALLOCATION_NOTORIETE

    rows = []
    total_pipeline = 0
    total_sqls = 0
    total_mqls = 0
    total_budget_perf = 0

    for seg_name, seg in segments.items():
        sqls = seg["sqls_target"]
        acv = seg["acv"]
        pipeline_seg = sqls * acv
        mqls_needed = sqls / (conv_bdr_pct / 100)
        total_pipeline += pipeline_seg
        total_sqls += sqls
        total_mqls += mqls_needed

        seg_alloc = allocation.get(seg_name, {})
        for (plateforme, fmt), pct in seg_alloc.items():
            mqls_levier = mqls_needed * (pct / 100)
            cpl = _cpl_median(df_bench, plateforme, fmt)
            if cpl is None:
                continue
            budget = mqls_levier * cpl
            sqls_levier = mqls_levier * (conv_bdr_pct / 100)
            pipeline_levier = sqls_levier * acv
            total_budget_perf += budget
            rows.append({
                "segment": seg_name,
                "plateforme": plateforme,
                "format": fmt,
                "allocation_pct": pct,
                "mqls": mqls_levier,
                "sqls": sqls_levier,
                "cpl_benchmark": cpl,
                "budget": budget,
                "pipeline": pipeline_levier,
                "acv": acv,
            })

    df_detail = pd.DataFrame(rows)

    # --- Budget notoriété : % du budget total ---
    # share_notoriete_pct est sur le total final, donc :
    #   budget_total = budget_perf / (1 - share/100)
    if share_notoriete_pct > 0 and share_notoriete_pct < 100:
        budget_total = total_budget_perf / (1 - share_notoriete_pct / 100)
    else:
        budget_total = total_budget_perf
    budget_notoriete = budget_total - total_budget_perf

    rows_noto = []
    for (plateforme, fmt), pct in allocation_notoriete.items():
        b = budget_notoriete * (pct / 100)
        cpm = _cpm_median(df_bench, plateforme, fmt)
        impressions = (b / cpm * 1000) if cpm else None
        rows_noto.append({
            "plateforme": plateforme,
            "format": fmt,
            "allocation_pct": pct,
            "budget": b,
            "cpm_benchmark": cpm,
            "impressions": impressions,
        })
    df_notoriete = pd.DataFrame(rows_noto)

    synthese = {
        "pipeline_target": total_pipeline,
        "sqls_target": total_sqls,
        "mqls_target": total_mqls,
        "budget_perf": total_budget_perf,
        "budget_notoriete": budget_notoriete,
        "budget_total": budget_total,
        "cout_par_mql": budget_total / total_mqls if total_mqls else 0,
        "cout_par_sql": budget_total / total_sqls if total_sqls else 0,
        "cout_par_euro_pipeline": budget_total / total_pipeline if total_pipeline else 0,
        "roas": total_pipeline / budget_total if budget_total else 0,
    }

    return {
        "detail": df_detail,
        "notoriete": df_notoriete,
        "synthese": synthese,
    }

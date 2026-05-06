"""
Prédictions de performance à partir d'un budget et des benchmarks.

Logique : pour chaque scénario (pessimiste / médian / optimiste), on chaîne les KPIs :
- impressions = budget / CPM * 1000
- clics       = impressions * CTR
- leads/conv  = clics * taux_conv
- CPA effectif = budget / leads

Pessimiste = pire combo (CPM max, CTR min, conv min)
Médian     = mediane sur tous
Optimiste  = meilleur combo (CPM min, CTR max, conv max)
"""
import pandas as pd


def _get_kpi(df: pd.DataFrame, kpi_name: str, col: str) -> float | None:
    row = df[df["kpi"] == kpi_name]
    if row.empty:
        return None
    return float(row.iloc[0][col])


def predict(df_levier: pd.DataFrame, budget: float) -> dict:
    """
    df_levier : DataFrame filtré sur (plateforme, format) avec colonnes min/mediane/max.
    Retourne un dict avec 3 scénarios contenant impressions, clics, leads/conv et CPA.
    """
    # Mapping flexible des KPIs (selon le format présent dans l'Excel)
    cpm_min, cpm_med, cpm_max = _get_kpi(df_levier, "CPM", "min"), _get_kpi(df_levier, "CPM", "mediane"), _get_kpi(df_levier, "CPM", "max")
    cpc_min, cpc_med, cpc_max = _get_kpi(df_levier, "CPC", "min"), _get_kpi(df_levier, "CPC", "mediane"), _get_kpi(df_levier, "CPC", "max")
    ctr_min, ctr_med, ctr_max = _get_kpi(df_levier, "CTR", "min"), _get_kpi(df_levier, "CTR", "mediane"), _get_kpi(df_levier, "CTR", "max")
    conv_min, conv_med, conv_max = _get_kpi(df_levier, "Taux conv", "min"), _get_kpi(df_levier, "Taux conv", "mediane"), _get_kpi(df_levier, "Taux conv", "max")
    cpa_min, cpa_med, cpa_max = _get_kpi(df_levier, "CPA", "min"), _get_kpi(df_levier, "CPA", "mediane"), _get_kpi(df_levier, "CPA", "max")
    cpl_min, cpl_med, cpl_max = _get_kpi(df_levier, "CPL", "min"), _get_kpi(df_levier, "CPL", "mediane"), _get_kpi(df_levier, "CPL", "max")
    cps_min, cps_med, cps_max = _get_kpi(df_levier, "CPS (cost per send)", "min"), _get_kpi(df_levier, "CPS (cost per send)", "mediane"), _get_kpi(df_levier, "CPS (cost per send)", "max")
    open_min, open_med, open_max = _get_kpi(df_levier, "Open Rate", "min"), _get_kpi(df_levier, "Open Rate", "mediane"), _get_kpi(df_levier, "Open Rate", "max")
    cpv_min, cpv_med, cpv_max = _get_kpi(df_levier, "CPV", "min"), _get_kpi(df_levier, "CPV", "mediane"), _get_kpi(df_levier, "CPV", "max")
    vtr_min, vtr_med, vtr_max = _get_kpi(df_levier, "VTR", "min"), _get_kpi(df_levier, "VTR", "mediane"), _get_kpi(df_levier, "VTR", "max")

    scenarios = {}

    # Taux conv LinkedIn Lead Gen Form (fallback si "Taux conv" absent)
    if conv_min is None:
        conv_min = _get_kpi(df_levier, "Taux conv (LGF)", "min")
        conv_med = _get_kpi(df_levier, "Taux conv (LGF)", "mediane")
        conv_max = _get_kpi(df_levier, "Taux conv (LGF)", "max")

    # --- Scénario via CPM/CTR (Single Image, Demand Gen, Thought Leader) ---
    if cpm_min is not None and ctr_min is not None:
        for label, cpm, ctr, conv, cpl in [
            ("pessimiste", cpm_max, ctr_min, conv_min if conv_min else 0, cpl_max),
            ("median",     cpm_med, ctr_med, conv_med if conv_med else 0, cpl_med),
            ("optimiste",  cpm_min, ctr_max, conv_max if conv_max else 0, cpl_min),
        ]:
            impressions = budget / cpm * 1000
            clics = impressions * (ctr / 100)
            # Priorité au CPL direct s'il existe (plus fiable que chaîner CPM*CTR*conv)
            if cpl:
                leads = budget / cpl
                cpa = cpl
            elif conv:
                leads = clics * (conv / 100)
                cpa = budget / leads if leads else None
            else:
                leads = None
                cpa = None
            scenarios[label] = {
                "impressions": impressions,
                "clics": clics,
                "leads": leads,
                "cpa_effectif": cpa,
                "vues": None,
            }

    # --- Scénario via CPC pour Search/DSA ---
    elif cpc_min is not None and conv_min is not None:
        for label, cpc, conv in [
            ("pessimiste", cpc_max, conv_min),
            ("median",     cpc_med, conv_med),
            ("optimiste",  cpc_min, conv_max),
        ]:
            clics = budget / cpc
            leads = clics * (conv / 100)
            cpa = budget / leads if leads else None
            scenarios[label] = {
                "impressions": None,
                "clics": clics,
                "leads": leads,
                "cpa_effectif": cpa,
                "vues": None,
            }

    # --- Scénario Conversation Ads (CPS + Open Rate + CTR sur ouverture) ---
    elif cps_min is not None:
        ctr_open_min = _get_kpi(df_levier, "CTR (sur ouverture)", "min") or 4
        ctr_open_med = _get_kpi(df_levier, "CTR (sur ouverture)", "mediane") or 8
        ctr_open_max = _get_kpi(df_levier, "CTR (sur ouverture)", "max") or 15
        for label, cps, open_r, ctr_o in [
            ("pessimiste", cps_max, open_min, ctr_open_min),
            ("median",     cps_med, open_med, ctr_open_med),
            ("optimiste",  cps_min, open_max, ctr_open_max),
        ]:
            envois = budget / cps
            ouvertures = envois * (open_r / 100)
            clics = ouvertures * (ctr_o / 100)
            cpl_used = cpl_max if label == "pessimiste" else cpl_med if label == "median" else cpl_min
            leads = (budget / cpl_used) if cpl_used else None
            scenarios[label] = {
                "impressions": envois,  # ici impressions = envois
                "ouvertures": ouvertures,
                "clics": clics,
                "leads": leads,
                "cpa_effectif": cpl_used,
                "vues": None,
            }

    # --- Si CPV présent (Demand Gen vidéo) on ajoute aussi les vues ---
    if cpv_min is not None and scenarios:
        for label, cpv, vtr in [
            ("pessimiste", cpv_max, vtr_min),
            ("median",     cpv_med, vtr_med),
            ("optimiste",  cpv_min, vtr_max),
        ]:
            scenarios[label]["vues"] = budget / cpv if cpv else None

    return scenarios

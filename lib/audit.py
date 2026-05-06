"""Logique d'audit : comparaison valeur saisie vs benchmark."""
from typing import Literal

Status = Literal["green", "orange", "red"]


def status_for(value: float, min_v: float, max_v: float, sens: str) -> Status:
    """
    sens="cost"  → plus c'est bas, mieux c'est (CPC, CPA, CPM, etc.)
       value <= min       : vert
       min < value <= max : orange
       value > max        : rouge
    sens="perf"  → plus c'est haut, mieux c'est (CTR, taux conv, VTR, etc.)
       value >= max       : vert
       min <= value < max : orange
       value < min        : rouge
    """
    if sens == "cost":
        if value <= min_v:
            return "green"
        if value <= max_v:
            return "orange"
        return "red"
    # perf
    if value >= max_v:
        return "green"
    if value >= min_v:
        return "orange"
    return "red"


STATUS_LABEL = {
    "green": "✅ Au-dessus du benchmark",
    "orange": "🟠 Dans la moyenne",
    "red": "🔴 Sous-performant vs benchmark",
}

STATUS_COLOR = {
    "green": "#1f9d55",
    "orange": "#e58e26",
    "red": "#d64545",
}


def diagnostic(value: float, mediane: float, sens: str) -> str:
    """Génère un commentaire court : écart en % vs médiane."""
    if mediane == 0:
        return ""
    ecart = (value - mediane) / mediane * 100
    if sens == "cost":
        if ecart < -10:
            return f"{abs(ecart):.0f}% sous la médiane (bon signe : coût maîtrisé)."
        if ecart > 10:
            return f"{ecart:.0f}% au-dessus de la médiane (coût élevé)."
        return "Proche de la médiane marché."
    # perf
    if ecart > 10:
        return f"+{ecart:.0f}% vs médiane (performance forte)."
    if ecart < -10:
        return f"{ecart:.0f}% sous la médiane (à améliorer)."
    return "Proche de la médiane marché."

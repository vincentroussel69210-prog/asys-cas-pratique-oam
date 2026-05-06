"""
Génère data/benchmarks.xlsx avec les benchmarks marché par levier.

PÉRIMÈTRE : éditeur SaaS B2B RH, spécialité Gestion des Temps & Activités (GTA),
en évolution vers la planification. Audiences cibles : DRH, RRH, Responsables paie,
Responsables SIRH, dirigeants ETI/PME (50-2000 collaborateurs principalement).

Conséquences vs benchmarks B2B "génériques" :
- LinkedIn : CPC/CPM/CPL plus élevés (audiences HR seniors = enchères plus tendues)
- Google Search : CPC élevés sur kw "GTA", "logiciel pointage", "planification équipe",
  "WFM", "SIRH", car concurrence Kelio, Bodet, Octime, Horoquartz, Skello, etc.
- Cycle de vente long → taux conv "demande de démo" plus parlant que "achat"
- Demand Gen utile pour gagner en notoriété face aux acteurs établis

Sources : LinkedIn Ads Benchmark Report 2024, WordStream B2B SaaS 2024,
G2 Buyer Behavior Reports, retours agence STAENK sur clients SaaS RH.

Structure :
- Feuille "benchmarks" : 1 ligne par couple (plateforme, format, KPI)
- Feuille "formats" : métadonnées + conseils ciblés SaaS RH
- Feuille "sources" : références
"""
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parent / "data" / "benchmarks.xlsx"

# ----------------------------------------------------------------------------
# Benchmarks SaaS B2B RH (GTA / planification)
# (plateforme, format, kpi, unite, min, mediane, max, sens, note)
# ----------------------------------------------------------------------------
BENCHMARKS = [
    # --- LinkedIn Conversation Ads (Message Ads) ---
    # Cible = DRH, RRH, Resp. SIRH (seniors, très sollicités)
    ("LinkedIn", "Conversation Ads", "Open Rate",            "%",   25,    38,    50,    "perf", "Audiences HR très sollicitées : viser 35-45%"),
    ("LinkedIn", "Conversation Ads", "CTR (sur envoi)",      "%",   1.0,   2.5,   4.5,   "perf", "Clic CTA / nb envois"),
    ("LinkedIn", "Conversation Ads", "CTR (sur ouverture)",  "%",   3.0,   7.0,   12.0,  "perf", "Clic CTA / ouvertures (proxy intérêt offre)"),
    ("LinkedIn", "Conversation Ads", "CPS (cost per send)",  "EUR", 0.30,  0.55,  0.90,  "cost", "Cible HR = enchère élevée"),
    ("LinkedIn", "Conversation Ads", "CPC",                  "EUR", 12,    22,    40,    "cost", "Coût par clic CTA"),
    ("LinkedIn", "Conversation Ads", "CPL",                  "EUR", 120,   220,   400,   "cost", "Coût par démo / RDV qualifié SaaS RH"),

    # --- LinkedIn Single Image Ads (Sponsored Content) ---
    ("LinkedIn", "Single Image Ads", "CPM",                  "EUR", 30,    55,    90,    "cost", "Audiences HR premium"),
    ("LinkedIn", "Single Image Ads", "CPC",                  "EUR", 7,     12,    22,    "cost", "Coût par clic"),
    ("LinkedIn", "Single Image Ads", "CTR",                  "%",   0.40,  0.65,  1.10,  "perf", "Bon visuel + bon angle GTA = >0.7%"),
    ("LinkedIn", "Single Image Ads", "Frequency (mois)",     "x",   1.5,   3.5,   6.0,   "cost", "Saturation au-delà de 6 sur audience HR"),
    ("LinkedIn", "Single Image Ads", "CPL",                  "EUR", 100,   220,   450,   "cost", "Lead Gen Form B2B SaaS RH"),
    ("LinkedIn", "Single Image Ads", "Taux conv (LGF)",      "%",   8.0,   13.0,  22.0,  "perf", "Conv sur Lead Gen Form ouverte"),

    # --- LinkedIn Thought Leader Ads (Advocacy) ---
    # Format clé pour SaaS RH : sponsoriser posts de DG / experts produit / responsables RH internes
    ("LinkedIn", "Thought Leader Ads", "CPM",                "EUR", 22,    40,    65,    "cost", "CPM plus bas que Single Image car perçu organique"),
    ("LinkedIn", "Thought Leader Ads", "CPC",                "EUR", 4,     8,     14,    "cost", "Excellent levier coût/notoriété pour SaaS RH"),
    ("LinkedIn", "Thought Leader Ads", "CTR",                "%",   0.55,  0.95,  1.60,  "perf", "Souvent supérieur aux Single Image"),
    ("LinkedIn", "Thought Leader Ads", "Engagement Rate",    "%",   2.5,   4.5,   7.5,   "perf", "Likes + commentaires + partages / impressions"),
    ("LinkedIn", "Thought Leader Ads", "Cost per Engagement","EUR", 0.50,  1.20,  2.50,  "cost", "Coût par interaction"),

    # --- Google Ads Search (kw GTA / pointage / planning / WFM / SIRH) ---
    ("Google Ads", "Search", "CTR",                          "%",   4.0,   7.0,   12.0,  "perf", "Intention forte sur kw transactionnels GTA/WFM"),
    ("Google Ads", "Search", "CPC",                          "EUR", 2.5,   5.5,   15.0,  "cost", "Kw HR/SIRH/WFM = forte concurrence"),
    ("Google Ads", "Search", "Taux conv",                    "%",   2.0,   4.0,   8.0,   "perf", "Conv = demande démo / contact (cycle long)"),
    ("Google Ads", "Search", "CPA",                          "EUR", 80,    180,   450,   "cost", "Coût par lead démo qualifié"),
    ("Google Ads", "Search", "Quality Score",                "/10", 5,     7,     9,     "perf", "Crucial pour maîtriser CPC sur kw chers"),
    ("Google Ads", "Search", "Taux d'impression",            "%",   40,    65,    85,    "perf", "Search impression share marque + générique"),

    # --- Google Ads DSA ---
    ("Google Ads", "DSA", "CTR",                             "%",   2.0,   4.5,   8.0,   "perf", "Couverture longue traîne"),
    ("Google Ads", "DSA", "CPC",                             "EUR", 1.0,   3.0,   7.0,   "cost", "CPC inférieur au Search exact"),
    ("Google Ads", "DSA", "Taux conv",                       "%",   1.0,   2.5,   5.0,   "perf", "Inférieur au Search ciblé"),
    ("Google Ads", "DSA", "CPA",                             "EUR", 100,   220,   500,   "cost", "Audit search terms hebdo indispensable"),
    ("Google Ads", "DSA", "Taux d'impression",               "%",   35,    55,    80,    "perf", "Dynamic impression share"),

    # --- Google Ads Demand Gen (notoriété face concurrents installés) ---
    ("Google Ads", "Demand Gen", "CPM",                      "EUR", 5,     11,    20,    "cost", "Notoriété B2B SaaS"),
    ("Google Ads", "Demand Gen", "CPV",                      "EUR", 0.03,  0.07,  0.15,  "cost", "Coût par vue vidéo"),
    ("Google Ads", "Demand Gen", "VTR",                      "%",   18,    30,    45,    "perf", "View-through rate (>10s)"),
    ("Google Ads", "Demand Gen", "CTR",                      "%",   0.40,  1.00,  2.00,  "perf", "CTR images / carrousels"),
    ("Google Ads", "Demand Gen", "Cout/vue 25%+",            "EUR", 0.05,  0.10,  0.20,  "cost", "Vue jusqu'à 25% du contenu vidéo"),
    ("Google Ads", "Demand Gen", "Frequency (mois)",         "x",   2,     5,     10,    "cost", "Saturation au-delà de 10"),
]

# ----------------------------------------------------------------------------
# Métadonnées + conseils par format (contextualisés SaaS RH)
# ----------------------------------------------------------------------------
FORMATS_META = [
    ("LinkedIn", "Conversation Ads",
     "Acquisition / nurturing — décideurs RH",
     "DRH, RRH, Resp. SIRH, Resp. paie (ETI 50-2000 collab.)",
     "Idéal pour offre HOF (livre blanc 'Réforme code travail', démo 'planification équipe'). "
     "Personnaliser le sender (DG ou expert métier). Limiter fréquence 1/mois max. "
     "CTA clair : 'Réserver une démo de 30 min'."),
    ("LinkedIn", "Single Image Ads",
     "Notoriété / acquisition large",
     "Audiences HR larges + retargeting visiteurs site",
     "Tester 3-5 angles : conformité, gain de temps, pénurie main d'œuvre, planification multi-sites. "
     "Lead Gen Form recommandé. Visuels : éviter mockup générique, privilégier témoignage client."),
    ("LinkedIn", "Thought Leader Ads",
     "Notoriété / engagement / différenciation",
     "Audiences HR chaudes, lookalike, intérêts (logiciels SIRH)",
     "LEVIER CLÉ pour SaaS RH face aux concurrents installés (Kelio, Bodet, Octime). "
     "Sponsoriser posts du DG, du CPO ou d'experts métier. Tonalité authentique, "
     "raconter une histoire (ex: comment X a réduit ses litiges paie). Ne pas pitcher direct."),
    ("Google Ads", "Search",
     "Acquisition / intention forte",
     "Recherches : 'logiciel GTA', 'pointage entreprise', 'logiciel planning équipe', 'WFM', 'SIRH temps'",
     "Mots-clés exact match prioritaires. Négatifs systématiques : 'gratuit', 'open source', 'pour étudiants'. "
     "Annonces RSA + extensions sitelinks (démo, tarifs, témoignages). Surveiller Quality Score."),
    ("Google Ads", "DSA",
     "Acquisition / coverage longue traîne",
     "Recherches non couvertes par keywords (variantes, secteurs verticaux)",
     "Couvrir les variantes 'logiciel pointage [secteur]', 'gestion temps [taille entreprise]'. "
     "Audit search terms hebdomadaire impératif. Exclusions : concurrents nominatifs, recherches RH/emploi."),
    ("Google Ads", "Demand Gen",
     "Notoriété / considération — gagner du share of voice",
     "In-market 'HR software', lookalike clients, intérêts SIRH/management",
     "Format vidéo + image. Asset diversity max. Mesurer view-through conversions sur le site. "
     "Capitaliser sur événements RH (salon SRH, Tech RH) en boost pré/post-événement."),
]

# ----------------------------------------------------------------------------
# Sources
# ----------------------------------------------------------------------------
SOURCES = [
    ("LinkedIn", "LinkedIn Ads Benchmark Report 2024",       "https://business.linkedin.com/marketing-solutions/blog"),
    ("LinkedIn", "Hootsuite LinkedIn Ads Benchmarks 2024",   "https://blog.hootsuite.com/linkedin-ads-cost/"),
    ("LinkedIn", "AJ Wilcox / B2Linked agency benchmarks",   "https://b2linked.com/"),
    ("Google Ads", "WordStream B2B SaaS Benchmarks 2024",    "https://www.wordstream.com/blog/ws/2024/google-ads-benchmarks"),
    ("Google Ads", "Tinuiti SaaS Industry Reports",          "https://tinuiti.com/blog/"),
    ("Tous",      "G2 B2B Buyer Behavior Reports 2024",      "https://www.g2.com/research"),
    ("Tous",      "Retours agence STAENK clients SaaS RH",   "interne"),
]


def main():
    df_bench = pd.DataFrame(
        BENCHMARKS,
        columns=["plateforme", "format", "kpi", "unite", "min", "mediane", "max", "sens", "note"],
    )
    df_formats = pd.DataFrame(
        FORMATS_META,
        columns=["plateforme", "format", "objectif", "audience", "conseils"],
    )
    df_sources = pd.DataFrame(SOURCES, columns=["plateforme", "source", "url"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        df_bench.to_excel(writer, sheet_name="benchmarks", index=False)
        df_formats.to_excel(writer, sheet_name="formats", index=False)
        df_sources.to_excel(writer, sheet_name="sources", index=False)

    print(f"OK -> {OUT}  ({len(df_bench)} benchmarks, {len(df_formats)} formats)")


if __name__ == "__main__":
    main()

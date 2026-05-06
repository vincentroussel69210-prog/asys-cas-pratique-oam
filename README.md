# Audit & Prédiction — Acquisition payante (SaaS B2B RH)

Dashboard local Streamlit pour auditer et prédire la performance de campagnes
d'acquisition payante sur les leviers **LinkedIn Ads** (Conversation Ads, Single Image,
Thought Leader) et **Google Ads** (Search, DSA, Demand Gen).

**Vertical ciblé** : éditeur SaaS B2B RH, spécialité GTA (gestion des temps & activités)
en évolution vers la planification. Audiences DRH / RRH / Resp. SIRH (ETI/PME).

## Architecture

```
audit-prediction-acquisition/
├── app.py                   # Application Streamlit (entrée principale)
├── build_benchmarks.py      # Génère data/benchmarks.xlsx depuis le code
├── data/
│   └── benchmarks.xlsx      # Source des benchmarks (3 feuilles)
├── lib/
│   ├── data.py              # Chargement Excel + helpers
│   ├── audit.py             # Logique audit (vert/orange/rouge vs benchmark)
│   └── predict.py           # Logique prédiction (3 scénarios par budget)
├── requirements.txt
└── venv/                    # (gitignored)
```

## Lancer le dashboard

```powershell
# Activer le venv
.\venv\Scripts\Activate.ps1

# Lancer Streamlit
streamlit run app.py
```

L'app s'ouvre sur `http://localhost:8501`.

## Régénérer les benchmarks

L'Excel `data/benchmarks.xlsx` est généré depuis `build_benchmarks.py` (toutes les
valeurs sont en code, donc versionnables et éditables facilement).

```powershell
python build_benchmarks.py
```

Pour ajuster les benchmarks : modifier la liste `BENCHMARKS` dans le script, puis
relancer. Tu peux aussi éditer directement l'Excel si tu préfères saisir à la main —
dans ce cas ne relance pas `build_benchmarks.py` qui écrase le fichier.

## Modes du dashboard

### 🔎 Audit
Saisis les chiffres réels d'une campagne (CPC, CTR, CPL, etc.) → comparaison vs benchmark
marché avec code couleur (vert / orange / rouge) et diagnostic automatique.

### 🔮 Prédiction
Saisis un budget → 3 scénarios de performance attendue (pessimiste / médian / optimiste) :
volume d'impressions/envois, clics, leads, CPA effectif.

### 📋 Benchmarks
Vue tabulaire complète des benchmarks par plateforme et format.

### ℹ️ Sources
Méthodologie + références utilisées pour les benchmarks.

## Périmètre des benchmarks

6 leviers couverts :

| Plateforme | Format | KPIs principaux |
|---|---|---|
| LinkedIn Ads | Conversation Ads | Open Rate, CTR, CPS, CPC, CPL |
| LinkedIn Ads | Single Image Ads | CPM, CPC, CTR, CPL, Taux conv LGF |
| LinkedIn Ads | Thought Leader Ads | CPM, CPC, CTR, Engagement Rate |
| Google Ads | Search | CTR, CPC, Taux conv, CPA, Quality Score |
| Google Ads | DSA | CTR, CPC, Taux conv, CPA |
| Google Ads | Demand Gen | CPM, CPV, VTR, CTR |

## Notes

- **Strictement local, non synchronisé.** Le projet vit hors OneDrive et n'a pas de remote git.
- Les benchmarks sont des **ordres de grandeur** issus de sources publiques + retours
  agence. À affiner après collecte de tes propres données réelles.
- Pour ajouter un levier (ex: Meta Ads, TikTok), ajouter les lignes correspondantes
  dans `build_benchmarks.py` puis régénérer l'Excel — l'app les détectera automatiquement.

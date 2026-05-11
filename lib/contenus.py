"""
Bibliothèque de types de contenu par format LinkedIn.
Calibré pour éditeur SaaS B2B RH (GTA → planification).

Chaque type a :
- nom court
- angle / promesse
- stage funnel (TOFU / MOFU / BOFU)
- engagement attendu (1-5)
- effort de production (1-5)
- exemple concret pour le vertical
- KPI principal à suivre
"""

# ----------------------------------------------------------------------------
# Thought Leader Ads — sponsoriser un post personnel d'un dirigeant / expert
# ----------------------------------------------------------------------------
THOUGHT_LEADER = [
    {
        "nom": "Décryptage réglementaire",
        "angle": "Réagir à une actu (loi, jurisprudence, accord) en explicitant l'impact opérationnel",
        "funnel": "TOFU",
        "engagement": 4,
        "effort": 2,
        "auteur_type": "CEO ou DPO/RH interne",
        "exemple": "« La Cour de cassation vient de requalifier les temps de pause : voici ce que vos plannings doivent absolument intégrer dès lundi »",
        "kpi": "CTR + commentaires (proxy intérêt sujet)",
    },
    {
        "nom": "Storytelling client",
        "angle": "Raconter le parcours d'un client (avant/après) sans pitcher le produit",
        "funnel": "MOFU",
        "engagement": 5,
        "effort": 3,
        "auteur_type": "CEO ou Customer Success",
        "exemple": "« Ce DRH d'un groupe hospitalier a divisé ses litiges paie par 3 en 6 mois. Voici les 4 décisions qu'il a prises »",
        "kpi": "CTR + saves (signal d'inspiration)",
    },
    {
        "nom": "Coup de gueule sectoriel",
        "angle": "Prendre position contre une norme du marché, polariser",
        "funnel": "TOFU",
        "engagement": 5,
        "effort": 2,
        "auteur_type": "CEO uniquement (besoin d'incarnation forte)",
        "exemple": "« Stop aux logiciels RH qui demandent 9 mois de déploiement. C'est de la rente, pas de la valeur. »",
        "kpi": "Engagement rate + partages (viralité)",
    },
    {
        "nom": "Insight terrain (étude propriétaire)",
        "angle": "Partager un chiffre exclusif issu de votre base ou d'une étude",
        "funnel": "TOFU/MOFU",
        "engagement": 4,
        "effort": 4,
        "auteur_type": "CMO ou Head of Product",
        "exemple": "« On a analysé 1,2 M de plannings sur 200 entreprises. 73% des DRH font la même erreur — laquelle ? »",
        "kpi": "Téléchargement étude + clics CTA",
    },
    {
        "nom": "Tribune contrarienne",
        "angle": "Affirmer une thèse à contre-courant et la défendre",
        "funnel": "TOFU",
        "engagement": 5,
        "effort": 3,
        "auteur_type": "CEO ou Chief Strategy",
        "exemple": "« La GTA est en train de mourir. Voici ce qui la remplace dans les 18 prochains mois. »",
        "kpi": "Commentaires (qualité du débat) + abonnés",
    },
    {
        "nom": "Behind the scenes produit",
        "angle": "Montrer l'envers du décor, humaniser, créer de la connivence",
        "funnel": "MOFU",
        "engagement": 3,
        "effort": 2,
        "auteur_type": "CPO ou Head of Engineering",
        "exemple": "« Comment on a conçu notre moteur de planification IA. Les 3 erreurs qu'on a faites avant de trouver la bonne archi »",
        "kpi": "Engagement (likes/comm.) + visites profil",
    },
    {
        "nom": "Tendances métier (prospective)",
        "angle": "Listes prédictives, inspirantes, hautement partageables",
        "funnel": "TOFU",
        "engagement": 4,
        "effort": 2,
        "auteur_type": "CEO ou Head of Strategy",
        "exemple": "« 5 mutations RH qui vont reshape la planification d'ici 2027. Personne n'en parle (encore) »",
        "kpi": "Partages + abonnés",
    },
    {
        "nom": "Recrutement / culture",
        "angle": "Poster sur l'équipe, le manifeste, la mission — attire candidats ET clients",
        "funnel": "TOFU",
        "engagement": 3,
        "effort": 2,
        "auteur_type": "CEO ou DRH interne",
        "exemple": "« Pourquoi on n'embauchera jamais de Chief AI Officer. Notre conviction sur l'IA dans le SaaS RH. »",
        "kpi": "Profile views + engagement qualitatif",
    },
]


# ----------------------------------------------------------------------------
# Conversation Ads — InMail sponsorisé avec CTA
# ----------------------------------------------------------------------------
CONVERSATION_ADS = [
    {
        "nom": "Démo express",
        "angle": "Proposer un RDV court, ultra-spécifique au contexte du destinataire",
        "funnel": "BOFU",
        "engagement": 4,
        "effort": 1,
        "duree_offre": "20-30 min",
        "exemple": "Objet : 30 min pour voir comment [Concurrent client] a réduit ses litiges paie de 60%. CTA : Réserver un créneau",
        "kpi": "CPL + taux RDV qualifié",
    },
    {
        "nom": "Audit gratuit / diagnostic",
        "angle": "Offrir une valeur immédiate (scoring, audit) en échange du RDV",
        "funnel": "MOFU/BOFU",
        "engagement": 5,
        "effort": 2,
        "duree_offre": "15 min",
        "exemple": "Objet : Audit GTA gratuit — 10 critères scorés sur votre process actuel. CTA : Recevoir mon audit",
        "kpi": "Taux ouverture + CPL",
    },
    {
        "nom": "Étude sectorielle premium",
        "angle": "Lead magnet à forte valeur perçue (étude, baromètre)",
        "funnel": "TOFU/MOFU",
        "engagement": 4,
        "effort": 5,
        "duree_offre": "PDF 30+ pages",
        "exemple": "Objet : Baromètre Planification 2026 — 200 DRH interrogés, 50 pages d'insights. CTA : Télécharger gratuitement",
        "kpi": "Volume MQLs + taux conv BDR",
    },
    {
        "nom": "Webinaire / événement",
        "angle": "Inscription à un live, format impliquant",
        "funnel": "MOFU",
        "engagement": 4,
        "effort": 3,
        "duree_offre": "30-45 min",
        "exemple": "Objet : Réforme temps de travail 2026 — webinaire express avec [Avocat partenaire]. CTA : Je m'inscris",
        "kpi": "Inscrits + taux présence",
    },
    {
        "nom": "Calculateur ROI / outil",
        "angle": "Outil interactif qui chiffre la perte / le gain potentiel",
        "funnel": "MOFU",
        "engagement": 5,
        "effort": 4,
        "duree_offre": "2-3 min",
        "exemple": "Objet : Combien vos erreurs de planning vous coûtent ? Calculez votre perte annuelle en 2 min. CTA : Lancer le calcul",
        "kpi": "Conversions calculateur + retargeting list",
    },
    {
        "nom": "Comparatif / benchmark personnalisé",
        "angle": "Montrer où le destinataire se situe vs sa peer group",
        "funnel": "MOFU",
        "engagement": 4,
        "effort": 4,
        "duree_offre": "Rapport 5 pages",
        "exemple": "Objet : Comment vos KPIs RH se situent vs les meilleurs DRH de votre secteur ? CTA : Recevoir mon comparatif",
        "kpi": "CPL + qualité segmentation",
    },
    {
        "nom": "Newsletter expert (subscribe)",
        "angle": "S'inscrire à un contenu série, créer une habitude",
        "funnel": "TOFU",
        "engagement": 3,
        "effort": 2,
        "duree_offre": "Mensuelle",
        "exemple": "Objet : La Lettre du DRH digital — décryptages mensuels signés [CEO]. CTA : M'abonner gratuitement",
        "kpi": "Abonnés + nurturing CTR email",
    },
    {
        "nom": "Invitation événement physique",
        "angle": "Petit-déjeuner, table ronde, dîner sectoriel",
        "funnel": "BOFU",
        "engagement": 5,
        "effort": 4,
        "duree_offre": "1h30 - 2h",
        "exemple": "Objet : Petit-déj DRH — 12 invités, 1 thème : la planification multisites. CTA : Demander mon invitation",
        "kpi": "Présents + RDV générés post-event",
    },
]


# ----------------------------------------------------------------------------
# Mapping pour faciliter l'accès
# ----------------------------------------------------------------------------
CONTENUS = {
    "Thought Leader Ads": THOUGHT_LEADER,
    "Conversation Ads": CONVERSATION_ADS,
}

FUNNEL_COLORS = {
    "TOFU": "#3498db",         # bleu
    "TOFU/MOFU": "#9b59b6",    # violet
    "MOFU": "#e58e26",         # orange
    "MOFU/BOFU": "#e74c3c",    # rouge-orange
    "BOFU": "#1f9d55",         # vert
}

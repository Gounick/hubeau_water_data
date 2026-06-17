# Hub'Eau - Données sur l'eau — Intégration Home Assistant

Intégration personnalisée (custom component) pour Home Assistant, installable via
[HACS](https://hacs.xyz), qui relève les données publiées par les
**13 API de [Hub'Eau](https://hubeau.eaufrance.fr/page/apis)** (OFB, BRGM,
Ministère de la Santé, Agences de l'eau, IFREMER...).

Aucune clé API n'est requise : toutes les API Hub'Eau sont publiques et gratuites.

## Thématiques disponibles

| Thématique | Localisation | Données |
|---|---|---|
| Qualité de l'eau potable | Commune (code INSEE) | pH, chlore, turbidité, nitrates, bactériologie, conformité du contrôle sanitaire |
| Piézométrie | Station (recherche GPS) | Niveau et profondeur des nappes souterraines |
| Hydrométrie | Station (recherche GPS) | Hauteur d'eau et débit des cours d'eau (quasi temps réel) |
| Température des cours d'eau | Station (recherche GPS) | Température de l'eau en continu |
| Qualité des cours d'eau | Commune (code INSEE) | Nitrates, phosphore, oxygène dissous en rivière |
| Qualité des nappes souterraines | Station (recherche GPS) | Nitrates, pH des eaux souterraines (ADES) |
| Hydrobiologie | Station (recherche GPS) | Indices biologiques diatomées (IBD) et macrophytes (IBMR) |
| Prélèvements en eau | Commune (code INSEE) | Volumes annuels prélevés (BNPE) |
| Indicateurs des services d'eau | Commune (code INSEE) | Prix de l'eau, rendement réseau, conformité sanitaire |
| Écoulement des cours d'eau (ONDE) | Commune (code INSEE) | Observations visuelles d'étiage |
| Surveillance des eaux littorales ⚠️ | Station (recherche GPS) | Contaminants chimiques marins — **API en cours de fermeture (10/09/2026)** |
| Poisson | Commune (nom) | Dernière espèce observée lors de pêches scientifiques |
| Vente de produits phytopharmaceutiques | Département | Quantités de substances vendues |

## Fonctionnalités

- Configuration 100 % via l'interface utilisateur (config flow multi-étapes), pas de YAML.
- Sélection libre d'une ou plusieurs thématiques par intégration ajoutée.
- Pour les thématiques géolocalisées par station (piézométrie, hydrométrie,
  température des cours d'eau, qualité des nappes, hydrobiologie,
  littoral) : recherche automatique des stations à proximité de vos
  coordonnées GPS dans un rayon configurable, ou saisie manuelle d'un code
  de station Hub'Eau connu.
- Un appareil Home Assistant par thématique activée, avec ses capteurs dédiés.
- Rafraîchissement périodique configurable (par défaut toutes les 12h —
  la plupart des données Hub'Eau ne sont mises à jour que quotidiennement
  ou mensuellement selon la thématique).
- Carte Lovelace d'exemple fournie dans `lovelace/dashboard_hubeau.yaml`.

## Installation

### Via HACS (recommandé)

1. Dans HACS, menu **⋮ > Dépôts personnalisés**, ajoutez l'URL de ce dépôt
   avec la catégorie **Intégration**.
2. Recherchez **"Hub'Eau - Données sur l'eau"** dans HACS et installez.
3. Redémarrez Home Assistant.

### Manuelle

Copiez le dossier `custom_components/hubeau_water_data` dans le dossier
`custom_components` de votre installation Home Assistant, puis redémarrez.

## Configuration

1. **Paramètres → Appareils et services → Ajouter une intégration**
2. Recherchez **"Hub'Eau"**
3. **Étape 1** : sélectionnez une ou plusieurs thématiques à activer.
4. **Étape 2** : saisissez le code INSEE de votre commune (pour les
   thématiques par commune) et/ou vos coordonnées GPS et un rayon de
   recherche en km (pour les thématiques par station).
5. **Étape 3** (si applicable) : pour chaque thématique géolocalisée par
   station, choisissez la station la plus pertinente parmi celles trouvées
   à proximité, ou saisissez un code de station connu.

Vous pouvez ajouter plusieurs fois l'intégration (par exemple une fois par
commune ou point d'intérêt) si vous souhaitez suivre plusieurs lieux.

L'intervalle de rafraîchissement se modifie ensuite via le bouton
**Options** de l'intégration.

## Limites connues

- Les données Hub'Eau ont des fréquences de mise à jour très variables
  selon la thématique : quasi temps réel pour l'hydrométrie, quotidienne
  pour la piézométrie, mensuelle pour l'eau potable et les indicateurs de
  services, trimestrielle pour la température des cours d'eau.
- Certaines stations ne disposent pas de données pour tous les paramètres
  suivis ; les capteurs correspondants resteront `unavailable` si aucune
  donnée n'existe.
- L'API **Surveillance des eaux littorales** sera fermée par Hub'Eau le
  10 septembre 2026 (migration prévue vers l'API Quadrige de l'IFREMER,
  non encore disponible sur Hub'Eau à ce jour) ; elle reste incluse pour
  compatibilité mais affichera un avertissement lors de la sélection.
- L'API **Poisson** filtre par nom de commune (et non par code INSEE) :
  les résultats peuvent être incomplets en cas d'homonymie de communes.

## Licence

MIT

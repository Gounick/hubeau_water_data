"""Constantes et registre central des thématiques Hub'Eau.

Ce module définit, pour chacune des 13 API Hub'Eau, les informations
nécessaires à une gestion générique par le coordinator et la plateforme
sensor : endpoints, mode de localisation, paramètres de requête et liste
des « métriques » exposées comme capteurs Home Assistant.
"""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "hubeau_water_quality"

# ---------------------------------------------------------------------------
# Modes de localisation
# ---------------------------------------------------------------------------
LOC_COMMUNE = "commune"  # filtrage par code INSEE commune
LOC_STATION = "station"  # filtrage par code de station, recherche par rayon GPS

# ---------------------------------------------------------------------------
# Identifiants des thématiques
# ---------------------------------------------------------------------------
THEME_EAU_POTABLE = "eau_potable"
THEME_PIEZOMETRIE = "piezometrie"
THEME_HYDROMETRIE = "hydrometrie"
THEME_TEMPERATURE_RIVIERE = "temperature_riviere"
THEME_QUALITE_RIVIERE = "qualite_riviere"
THEME_QUALITE_NAPPES = "qualite_nappes"
THEME_HYDROBIOLOGIE = "hydrobiologie"
THEME_PRELEVEMENTS = "prelevements"
THEME_INDICATEURS_SERVICES = "indicateurs_services"
THEME_ECOULEMENT = "ecoulement"
THEME_LITTORAL = "littoral"
THEME_POISSON = "poisson"
THEME_PHYTOPHARMACEUTIQUES = "phytopharmaceutiques"

ALL_THEMES = [
    THEME_EAU_POTABLE,
    THEME_PIEZOMETRIE,
    THEME_HYDROMETRIE,
    THEME_TEMPERATURE_RIVIERE,
    THEME_QUALITE_RIVIERE,
    THEME_QUALITE_NAPPES,
    THEME_HYDROBIOLOGIE,
    THEME_PRELEVEMENTS,
    THEME_INDICATEURS_SERVICES,
    THEME_ECOULEMENT,
    THEME_LITTORAL,
    THEME_POISSON,
    THEME_PHYTOPHARMACEUTIQUES,
]

THEMES: dict[str, dict] = {
    THEME_EAU_POTABLE: {
        "name": "Qualité de l'eau potable",
        "icon": "mdi:cup-water",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis",
        "commune_param": "code_commune",
        "date_field": "date_prelevement",
        "sort_param": "desc",
        "metrics": [
            {"key": "1302", "name": "pH", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": "ph", "icon": "mdi:ph", "filter": {"code_parametre": "1302"}},
            {"key": "1398", "name": "Chlore libre", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:flask", "filter": {"code_parametre": "1398"}},
            {"key": "1399", "name": "Chlore total", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:flask-outline", "filter": {"code_parametre": "1399"}},
            {"key": "1295", "name": "Turbidité", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:water-opacity", "filter": {"code_parametre": "1295"}},
            {"key": "1340", "name": "Nitrates", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:flask-round-bottom", "filter": {"code_parametre": "1340"}},
            {"key": "1301", "name": "Température", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": "temperature", "icon": "mdi:thermometer", "filter": {"code_parametre": "1301"}},
            {"key": "1303", "name": "Conductivité", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:lightning-bolt", "filter": {"code_parametre": "1303"}},
            {"key": "1449", "name": "Bactéries coliformes", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:bacteria", "filter": {"code_parametre": "1449"}},
            {"key": "1447", "name": "Entérocoques", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:bacteria-outline", "filter": {"code_parametre": "1447"}},
            {"key": "1339", "name": "Dureté (TH)", "value_field": "resultat_numerique", "unit_field": "libelle_unite", "device_class": None, "icon": "mdi:water-percent", "filter": {"code_parametre": "1339"}},
        ],
        "conformity_metric": {
            "key": "conformite_globale",
            "name": "Conformité du dernier prélèvement",
            "value_field": "conclusion_conformite_prelevement",
            "icon": "mdi:shield-check-outline",
        },
    },
    THEME_PIEZOMETRIE: {
        "name": "Piézométrie",
        "icon": "mdi:waves-arrow-up",
        "localisation": LOC_STATION,
        "deprecated": False,
        "stations_endpoint": "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations",
        "stations_code_field": "code_bss",
        "stations_name_field": "libelle_pe",
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques",
        "station_param": "code_bss",
        "date_field": "date_mesure",
        "sort_param": "desc",
        "metrics": [
            {"key": "niveau_nappe", "name": "Niveau de la nappe", "value_field": "niveau_nappe_eau", "fixed_unit": "m NGF", "device_class": None, "icon": "mdi:waves-arrow-up", "filter": {}},
            {"key": "profondeur_nappe", "name": "Profondeur de la nappe", "value_field": "profondeur_nappe", "fixed_unit": "m", "device_class": None, "icon": "mdi:arrow-collapse-down", "filter": {}},
        ],
    },
    THEME_HYDROMETRIE: {
        "name": "Hydrométrie",
        "icon": "mdi:waves",
        "localisation": LOC_STATION,
        "deprecated": False,
        "stations_endpoint": "https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations",
        "stations_code_field": "code_station",
        "stations_name_field": "libelle_station",
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr",
        "station_param": "code_entite",
        "date_field": "date_obs",
        "sort_param": None,
        "metrics": [
            {"key": "hauteur", "name": "Hauteur d'eau", "value_field": "resultat_obs", "fixed_unit": "mm", "device_class": None, "icon": "mdi:waves", "filter": {"grandeur_hydro": "H"}},
            {"key": "debit", "name": "Débit", "value_field": "resultat_obs", "fixed_unit": "L/s", "device_class": None, "icon": "mdi:speedometer", "filter": {"grandeur_hydro": "Q"}},
        ],
    },
    THEME_TEMPERATURE_RIVIERE: {
        "name": "Température des cours d'eau",
        "icon": "mdi:thermometer-water",
        "localisation": LOC_STATION,
        "deprecated": False,
        "stations_endpoint": "https://hubeau.eaufrance.fr/api/v1/temperature/station",
        "stations_code_field": "code_station",
        "stations_name_field": "libelle_station",
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/temperature/chronique",
        "station_param": "code_station",
        "date_field": "date_mesure_temp",
        "sort_param": "desc",
        "metrics": [
            {"key": "temperature", "name": "Température de l'eau", "value_field": "resultat", "unit_field": "symbole_unite", "device_class": "temperature", "icon": "mdi:thermometer", "filter": {}},
        ],
    },
    THEME_QUALITE_RIVIERE: {
        "name": "Qualité des cours d'eau",
        "icon": "mdi:water-check",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/analyse_pc",
        "commune_param": "code_commune",
        "date_field": "date_prelevement",
        "sort_param": "desc",
        "metrics": [
            {"key": "nitrates", "name": "Nitrates (rivière)", "value_field": "resultat", "unit_field": "symbole_unite", "device_class": None, "icon": "mdi:flask-round-bottom", "filter": {"code_parametre": "1340"}},
            {"key": "phosphore", "name": "Phosphore total (rivière)", "value_field": "resultat", "unit_field": "symbole_unite", "device_class": None, "icon": "mdi:flask", "filter": {"code_parametre": "1350"}},
            {"key": "oxygene_dissous", "name": "Oxygène dissous (rivière)", "value_field": "resultat", "unit_field": "symbole_unite", "device_class": None, "icon": "mdi:weather-windy", "filter": {"code_parametre": "1311"}},
        ],
    },
    THEME_QUALITE_NAPPES: {
        "name": "Qualité des nappes souterraines",
        "icon": "mdi:water-check-outline",
        "localisation": LOC_STATION,
        "deprecated": False,
        "stations_endpoint": "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations",
        "stations_code_field": "bss_id",
        "stations_name_field": "libelle_pe",
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/qualite_nappes/analyses",
        "station_param": "bss_id",
        "date_field": "date_debut_prelevement",
        "sort_param": "desc",
        "metrics": [
            {"key": "nitrates_nappe", "name": "Nitrates (nappe)", "value_field": "resultat", "unit_field": "symbole_unite", "device_class": None, "icon": "mdi:flask-round-bottom", "filter": {"code_parametre": "1340"}},
            {"key": "ph_nappe", "name": "pH (nappe)", "value_field": "resultat", "unit_field": "symbole_unite", "device_class": "ph", "icon": "mdi:ph", "filter": {"code_parametre": "1302"}},
        ],
    },
    THEME_HYDROBIOLOGIE: {
        "name": "Hydrobiologie",
        "icon": "mdi:fish",
        "localisation": LOC_STATION,
        "deprecated": False,
        "stations_endpoint": "https://hubeau.eaufrance.fr/api/v1/hydrobio/stations_hydrobio",
        "stations_code_field": "code_station_hydrobio",
        "stations_name_field": "libelle_station_hydrobio",
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/hydrobio/indices",
        "station_param": "code_station_hydrobio",
        "date_field": "date_prelevement",
        "sort_param": None,
        "metrics": [
            {"key": "ibd", "name": "Indice Biologique Diatomées (IBD)", "value_field": "resultat_indice", "fixed_unit": None, "device_class": None, "icon": "mdi:leaf", "filter": {"code_indice": "5856"}},
            {"key": "ibmr", "name": "Indice Biologique Macrophytique (IBMR)", "value_field": "resultat_indice", "fixed_unit": None, "device_class": None, "icon": "mdi:flower", "filter": {"libelle_indice": "IBMR"}},
        ],
    },
    THEME_PRELEVEMENTS: {
        "name": "Prélèvements en eau",
        "icon": "mdi:water-pump",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques",
        "commune_param": "code_commune_insee",
        "date_field": "annee",
        "sort_param": "desc",
        "metrics": [
            {"key": "volume_preleve", "name": "Volume annuel prélevé", "value_field": "volume", "fixed_unit": "m³", "device_class": None, "icon": "mdi:water-pump", "filter": {}},
        ],
    },
    THEME_INDICATEURS_SERVICES: {
        "name": "Indicateurs des services d'eau",
        "icon": "mdi:chart-box-outline",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v0/indicateurs_services/communes",
        "commune_param": "code_commune",
        "date_field": "annee",
        "sort_param": "desc",
        "metrics": [
            {"key": "prix_eau", "name": "Prix du service d'eau potable", "value_field": "valeur_indicateur_min", "fixed_unit": "€/m³", "device_class": "monetary", "icon": "mdi:cash", "filter": {"code_indicateur": "D102.0", "type_service": "AEP"}},
            {"key": "rendement_reseau", "name": "Rendement du réseau de distribution", "value_field": "valeur_indicateur_min", "fixed_unit": "%", "device_class": None, "icon": "mdi:pipe-leak", "filter": {"code_indicateur": "P104.3", "type_service": "AEP"}},
            {"key": "taux_conformite", "name": "Taux de conformité du contrôle sanitaire", "value_field": "valeur_indicateur_min", "fixed_unit": "%", "device_class": None, "icon": "mdi:check-decagram", "filter": {"code_indicateur": "P101.1", "type_service": "AEP"}},
        ],
    },
    THEME_ECOULEMENT: {
        "name": "Ecoulement des cours d'eau (ONDE)",
        "icon": "mdi:waves",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/ecoulement/observations",
        "commune_param": "code_commune",
        "date_field": "date_observation",
        "sort_param": "desc",
        "metrics": [
            {"key": "ecoulement", "name": "Écoulement visuel du cours d'eau", "value_field": "libelle_ecoulement", "fixed_unit": None, "device_class": None, "icon": "mdi:waves", "filter": {}, "numeric": False},
        ],
    },
    THEME_LITTORAL: {
        "name": "Surveillance des eaux littorales",
        "icon": "mdi:beach",
        "localisation": LOC_STATION,
        "deprecated": True,
        "stations_endpoint": "https://hubeau.eaufrance.fr/api/v1/surveillance_littoral/lieux_surv",
        "stations_code_field": "code_lieusurv",
        "stations_name_field": "libelle_lieusurv",
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/surveillance_littoral/contaminants_chimiques",
        "station_param": "code_lieusurv",
        "date_field": "date_prel",
        "sort_param": "desc",
        "metrics": [
            {"key": "contaminant", "name": "Dernier contaminant chimique analysé", "value_field": "resultat_analyse", "unit_field": "libelle_unite_resultat", "device_class": None, "icon": "mdi:flask-outline", "filter": {}},
        ],
    },
    THEME_POISSON: {
        "name": "Poisson (pêches scientifiques)",
        "icon": "mdi:fish",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/etat_piscicole/observations",
        "commune_param": "libelle_commune",
        "commune_uses_name": True,
        "date_field": "date_operation",
        "sort_param": "desc",
        "metrics": [
            {"key": "derniere_espece", "name": "Dernière espèce observée", "value_field": "nom_commun_taxon", "fixed_unit": None, "device_class": None, "icon": "mdi:fish", "filter": {}, "numeric": False},
        ],
    },
    THEME_PHYTOPHARMACEUTIQUES: {
        "name": "Vente de produits phytopharmaceutiques (département)",
        "icon": "mdi:spray-bottle",
        "localisation": LOC_COMMUNE,
        "deprecated": False,
        "data_endpoint": "https://hubeau.eaufrance.fr/api/v1/vente_achat_phyto/ventes/substances",
        "commune_param": "code_territoire",
        "commune_uses_departement": True,
        "date_field": "annee",
        "sort_param": "desc",
        "metrics": [
            {"key": "ventes_substances", "name": "Quantité de substances vendues (dernière année)", "value_field": "quantite_substance", "fixed_unit": "kg", "device_class": None, "icon": "mdi:spray-bottle", "filter": {"type_territoire": "Département"}},
        ],
    },
}

CONF_THEMES = "themes"
CONF_CODE_COMMUNE = "code_commune"
CONF_NOM_COMMUNE = "nom_commune"
CONF_CODE_DEPARTEMENT = "code_departement"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS_KM = "radius_km"
CONF_STATIONS = "stations"
CONF_SCAN_INTERVAL_HOURS = "scan_interval_hours"

DEFAULT_SCAN_INTERVAL = timedelta(hours=12)
DEFAULT_RADIUS_KM = 15
DEFAULT_SCAN_INTERVAL_HOURS = 12

RESULTS_PAGE_SIZE = 100
STATIONS_PAGE_SIZE = 20

ATTR_DATE_MESURE = "date_mesure"
ATTR_NOM_COMMUNE = "nom_commune"
ATTR_NOM_STATION = "nom_station"
ATTR_CODE_STATION = "code_station"
ATTR_CONFORMITE_BACT = "conformite_bact"
ATTR_CONFORMITE_PC = "conformite_pc"
ATTR_CODE_PRELEVEMENT = "code_prelevement"

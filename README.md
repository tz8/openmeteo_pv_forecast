# Open-Meteo PV Forecast

[English version below / Englische Version weiter unten]

## 🇩🇪 Übersicht

**Open-Meteo PV Forecast** ist eine Home Assistant Integration, die lokale Solarstrom-Vorhersagen (Photovoltaik) direkt auf Basis der aktuellen Wetterdaten von Open-Meteo berechnet.

- **Umfassende Prognosewerte:** Die [Open-Meteo Ensemble-API](https://open-meteo.com/en/docs/ensemble-api) nutzt verschiedene Modellläufe mit leicht unterschiedlichen Ausgangsbedingungen für eine robuste und probabilistische Wetterprognose. So erhältst du nicht nur den wahrscheinlichsten Wert (Median), sondern auch eine Einschätzung des bestmöglichen und des minimal zu erwartenden Solarertrags (Maximum/Minimum). Die Prognosewerte werden für jeden String, aggregiert pro Wechselrichter und für das gesamte System als Sensoren bereitgestellt.
- **Keine Cloud-PV-Dienste:** Die Prognose läuft lokal und nutzt ausschließlich öffentliche Wetterdaten von Open-Meteo (keine anderen Drittanbieter!).
- **Kein Account nötig:** Die Open-Meteo-API ist ohne Anmeldung sofort nutzbar.
- **Großzügiges Freikontingent:** Das freie Kontingent reicht für die stündlichen Abrufe der Vorhersagedaten problemlos aus.
- **Multi-Inverter & Multi-String Support:** Unterstützt beliebig viele Wechselrichter mit je mehreren Strings.
- **Moderne Konfiguration:** Einfaches Hinzufügen, Bearbeiten und Löschen von Wechselrichtern und Strings per Home Assistant UI.
- **Forecast für 48 Stunden:** Vorhersage für alle Stunden zwischen Sonnenaufgang und Sonnenuntergang.

#### aktuell unterstützte Wetter-Modelle:
| nationaler Wetterdienst	| Wetter Model |	Region	| Auflösung	| Einzelmodelle	| Prognose Zeitraum	| Aktualisierung |
|---|---|---|---|---|---|---|
| Deutscher Wetterdienst (DWD)	| ICON-D2-EPS	| Central Europe	| 2 km, stündlich	| 20	| 2 Tage	| Alle 3 Stunden |
| | ICON-EU-EPS	| Europe	| 13 km, stündlich	| 40	| 5 Tage	| Alle 6 Stunden |
| | ICON-EPS	| Global	| 26 km, stündlich	| 40	| 7.5 Tage	| Alle 12 Stunden |
| UK Met Office	| MOGREPS-UK	| UK	| 2 km, stündlich	| 3	| 5 Tage	| jede Stunde |
||  MOGREPS-G	| Global	| 20 km, stündlich	| 18	| 8 Tage	| Alle 6 Stunden |

**Hinweis:** Die Integration ist auf Wetterdaten von [Open-Meteo](https://open-meteo.com/) angewiesen. Es findet **keine** Datenweitergabe an PV-Cloud-Dienste statt, aber eine Internetverbindung zu Open-Meteo ist erforderlich.

### Funktionen

- PV-Ertragsprognose auf Basis aktueller Wetterdaten (Open-Meteo)
- Flexible Modellierung deiner Anlage: Mehrere Wechselrichter, Strings, Ausrichtung, Neigungswinkel, Modulparameter
- Home Assistant Sensoren für stündliche Vorhersage (kW)
- Volle lokale Verarbeitung (keine Cloud für PV-Prognose selbst!)

### Installation

1. Kopiere das Verzeichnis `openmeteo_pv_forecast` in deinen Home Assistant `custom_components` Ordner.
2. Starte Home Assistant neu.
3. Füge die Integration „Open-Meteo PV Forecast“ in Home Assistant hinzu.
4. Konfiguriere deine Wechselrichter und Strings bequem über das UI.

### Hinweise

- Das Projekt ist in der aktiven Entwicklung. Bug-Reports, Feature-Wünsche und Pull Requests sind willkommen!
- **Getestet mit Home Assistant Core 2024.5+ im offiziellen Devcontainer.**

---

## 🇬🇧 Overview

**Open-Meteo PV Forecast** is a Home Assistant integration that calculates your photovoltaic power forecast locally, using up-to-date weather data from Open-Meteo.

- **Comprehensive forecasting:** The [Open-Meteo Ensemble API](https://open-meteo.com/en/docs/ensemble-api) uses multiple model runs with slightly different initial conditions for robust probabilistic weather forecasting. This provides not just the most likely yield (median), but also estimates for best and worst-case scenarios (maximum/minimum). Forecast values are available as sensors for each string, aggregated per inverter, and for your entire system.
- **No cloud-based PV providers:** The forecast runs 100% locally and uses only public weather data from Open-Meteo (no other third parties!).
- **No account required:** The Open-Meteo API is open for use, with no registration needed.
- **Generous free quota:** The free tier easily covers the number of API calls needed for regular forecasts.
- **Multi-inverter & multi-string support:** Model as many inverters (with strings) as you like.
- **Modern configuration:** Easily add, edit, and remove inverters and strings via Home Assistant UI.
- **48-hour forecast:** Hourly prediction from sunrise to sunset.

#### supported weather models

| National Weather Service	| Weather Model |	Region	| Resolution	| Members	| Forecast Length	| Update frequency |
|---|---|---|---|---|---|---|
| Deutscher Wetterdienst (DWD)	| ICON-D2-EPS	| Central Europe	| 2 km, hourly	| 20	| 2 days	| Every 3 hours |
| | ICON-EU-EPS	| Europe	| 13 km, hourly	| 40	| 5 days	| Every 6 hours |
| | ICON-EPS	| Global	| 26 km, hourly	| 40	| 7.5 days	| Every 12 hours |
| UK Met Office	| MOGREPS-UK	| UK	| 2 km, hourly	| 3	| 5 days	| Every hour |
||  MOGREPS-G	| Global	| 20 km, hourly	| 18	| 8 days	| Every 6 hours |

**Note:** The integration depends on weather data from [Open-Meteo](https://open-meteo.com/). No data is sent to any PV cloud provider, but an internet connection to Open-Meteo is required.

### Features

- PV yield forecast based on real Open-Meteo weather data
- Flexible system modeling: Multiple inverters, strings, orientation, tilt, and module parameters
- Home Assistant sensors for hourly forecast (kW)
- 100% local calculation (privacy friendly!)

### Installation

1. Copy the `openmeteo_pv_forecast` directory to your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. Add the "Open-Meteo PV Forecast" integration in Home Assistant.
4. Configure your inverters and strings via the user interface.

### Notes

- This project is under active development. Bug reports, feature requests, and pull requests are very welcome!
- **Tested with Home Assistant Core 2024.5+ in the official devcontainer.**

---

**GPLv3 – 2024 [@tz8](https://github.com/tz8)**

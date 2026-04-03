# Tech Stack – PlaneComparison

## Jazyk a runtime

| Technologie | Verze | Účel |
|---|---|---|
| **Python** | 3.13+ | Backend, datové skripty, výpočetní logika |
| **JavaScript** | ES6+ (vanilla) | Frontend logika (žádný framework) |
| **HTML5 / CSS3** | – | UI šablona (single-file SPA) |

## Backend

| Balíček | Verze | Účel |
|---|---|---|
| **Flask** | 3.1.3 | Webový framework, REST API, routing |
| **Werkzeug** | 3.1.7 | WSGI server (vývojový) |
| **Jinja2** | 3.1.6 | Šablonovací engine pro `templates/index.html` |
| **Pandas** | 3.0.1 | Načítání a zpracování CSV databáze letadel |
| **NumPy** | 2.4.3 | Numerické výpočty, NaN/Inf handling |
| **MarkupSafe** | 3.0.3 | Závislost Jinja2 |
| **itsdangerous** | 2.2.0 | Závislost Flask |
| **click** | 8.3.1 | Závislost Flask (CLI) |
| **python-dateutil** | 2.9.0.post0 | Závislost Pandas |
| **six** | 1.17.0 | Kompatibilní modul |
| **tzdata** | 2025.3 | Časové zóny pro Pandas |

## Frontend

| Technologie | Popis |
|---|---|
| **Vanilla JavaScript (ES6+)** | Žádný framework (React, Vue, apod.) – veškerá logika v `<script>` uvnitř `index.html` |
| **CSS3 custom properties** | Tmavé barevné schéma (dark mode), CSS variables (`--app-fs`) |
| **Fetch API** | REST volání na backend (`/api/compute`, `/api/hangar`) |
| **DOM manipulation** | Přímá práce s DOM (getElementById, innerHTML, classList) |

## Testování

| Nástroj | Účel |
|---|---|
| **pytest** | Testovací runner |
| **pytest-playwright** | E2E / UI testy v prohlížeči (Chromium) |
| **Flask test client** | Unit testy REST API (bez prohlížeče) |

## Nasazení

| Služba | Konfigurace |
|---|---|
| **Vercel** | Serverless Python via `@vercel/python` |
| **vercel.json** | Routuje vše na `api/index.py` |
| **api/index.py** | Vercel entry point – importuje Flask `app` z `app.py` |

## Datový zdroj

| Soubor | Formát | Popis |
|---|---|---|
| **plane_table.csv** | CSV (metrické SI jednotky) | Hlavní databáze ~30 GA letadel |
| **plane_table_calculated.csv** | CSV | Offline odvozená data (vedlejší produkt `compute_data.py`) |

## IDE & tooling

| Nástroj | Popis |
|---|---|
| **PyCharm** | Hlavní IDE |
| **Git** | Verzování |
| **pip** | Správa Python závislostí (`requirements.txt`) |


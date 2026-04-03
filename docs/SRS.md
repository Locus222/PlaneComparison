# Software Requirements Specification (SRS)

## PlaneComparison – Webová aplikace pro porovnání letadel

| Položka             | Hodnota                                          |
|---------------------|--------------------------------------------------|
| **Verze dokumentu** | 1.1                                              |
| **Datum**           | 2026-03-30                                       |
| **Projekt**         | PlaneComparison                                  |
| **Jazyk aplikace**  | Čeština (UI), Python + JavaScript (implementace) |

---

## 1. Úvod

### 1.1 Účel dokumentu

Tento dokument definuje softwarové požadavky (Software Requirements Specification) pro webovou aplikaci **PlaneComparison**. Aplikace slouží k porovnání provozních nákladů, výkonových parametrů a vhodnosti malých letadel (kategorie GA – General Aviation) pro konkrétní plánovaný let na základě uživatelsky zadaných vstupních parametrů.

### 1.2 Rozsah produktu

PlaneComparison je single-page webová aplikace (SPA) s Flask backendem, která:
- Načítá databázi letadel z CSV souboru (`plane_table.csv`)
- Přijímá vstupní parametry od uživatele (palivo, obsazení, vzdálenost, vítr, měna, jednotky)
- Provádí letové výpočty (doba letu, spotřeba, náklady, hmotnostní bilance, mezipřistání)
- Zobrazuje výsledky v interaktivní sortovatelné tabulce s více režimy zobrazení
- Označuje nevhodná letadla (přetížení, nedostatek sedadel, nedostatečný dolet)
- Podporuje nasazení na platformu Vercel (serverless)

### 1.3 Cílová skupina

Piloti a provozovatelé malých letadel (GA), kteří potřebují porovnat ekonomiku provozu různých typů letadel pro plánované lety.

### 1.4 Definice a zkratky

| Zkratka | Význam                                                 |
|---------|--------------------------------------------------------|
| GA      | General Aviation – všeobecné letectví                  |
| SEP     | Single Engine Piston – jednomotorové pístové letadlo   |
| MEP     | Multi Engine Piston – vícemotorové pístové letadlo     |
| MTOW    | Maximum Take-Off Weight – maximální vzletová hmotnost  |
| AVGAS   | Aviation Gasoline 100LL – letecký benzin               |
| JET A-1 | Letecký petrolej (kerosín)                             |
| FOB     | Fuel On Board – palivo na palubě                       |
| NM      | Nautical Mile – námořní míle (1.852 km)                |
| kt      | Knot – uzel (1.852 km/h)                               |
| GPH     | Gallons Per Hour – galony za hodinu (US gal)           |
| LPH     | Litres Per Hour – litry za hodinu                      |
| POH     | Pilot's Operating Handbook – provozní příručka letadla |
| VFR     | Visual Flight Rules – pravidla letu za viditelnosti    |
| Vs0     | Pádová rychlost v přistávací konfiguraci (klapky)      |
| Vs1     | Pádová rychlost v čisté konfiguraci (bez klapek)       |
| Vx      | Rychlost nejlepšího úhlu stoupání                      |
| Vy      | Rychlost nejlepší rychlosti stoupání                   |
| Vno     | Maximální rychlost v normálním provozu                 |
| Vne     | Nikdy nepřekračovatelná rychlost                       |
| Va      | Manévrovací rychlost                                   |
| CpDis   | Cost per Distance – náklad na jednotku vzdálenosti     |
| CpSeat  | Cost per Seat – náklad na sedadlo                      |
| CpOSeat | Cost per Occupied Seat – náklad na obsazené sedadlo    |
| MP      | Max Power – režim maximálního výkonu (75 %)            |
| EC      | Economy Cruise – ekonomický cestovní režim (55 %)      |

---

## 2. Celkový popis systému

### 2.1 Perspektiva produktu

Aplikace je samostatná webová aplikace bez externích databází. Data letadel jsou uložena v CSV souboru, který je součástí repozitáře. Aplikace nemá uživatelské účty ani trvalé ukládání dat na straně serveru.

### 2.2 Architektura systému

```
┌─────────────────────────────────────────────────────┐
│  Klient (prohlížeč)                                 │
│  ┌───────────────────────────────────────────────┐  │
│  │  index.html (SPA)                             │  │
│  │  ┌─────────┬──────────┬──────────┬──────────┐ │  │
│  │  │ Obecné  │  Plán    │ Obsazení │ Hangár   │ │  │
│  │  └─────────┴──────────┴──────────┴──────────┘ │  │
│  │  ┌───────────────────────────────────────────┐ │  │
│  │  │ Výsledková tabulka letadel               │ │  │
│  │  │ (Max Power / Economy / Compare / HourRate)│ │  │
│  │  └───────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────┘  │
│            │ REST API (JSON)                        │
│            ▼                                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  Flask Backend (app.py)                       │  │
│  │  ┌──────────────────┐  ┌───────────────────┐  │  │
│  │  │ /api/compute     │  │ /api/hangar       │  │  │
│  │  │ (POST → JSON)    │  │ (GET → JSON)      │  │  │
│  │  └──────┬───────────┘  └──────┬────────────┘  │  │
│  │         │                     │                │  │
│  │         ▼                     ▼                │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │ plane_table.csv (databáze letadel)       │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2.3 Technologický stack

| Vrstva              | Technologie                            | Verze |
|---------------------|----------------------------------------|-------|
| Backend framework   | Flask                                  | 3.1.3 |
| WSGI server         | Werkzeug                               | 3.1.7 |
| Šablonovací engine  | Jinja2                                 | 3.1.6 |
| Datové zpracování   | Pandas                                 | 3.0.1 |
| Numerické výpočty   | NumPy                                  | 2.4.3 |
| Frontend            | Vanilla JavaScript (ES6+), HTML5, CSS3 | –     |
| Testovací framework | Pytest + Playwright                    | –     |
| Nasazení            | Vercel (serverless Python)             | –     |
| Jazyk               | Python 3.13+                           | –     |

### 2.4 Databáze letadel

Databáze je uložena v souboru `plane_table.csv` (39 sloupců, 37 letadel) a obsahuje typy letadel z těchto výrobců:
- **Beechcraft** – G33 Debonair, G36 Bonanza, G55/G58 Baron, G58P Baron II
- **Piper** – Pa-28-180 Cherokee/Challanger, Pa-32 Cherokee Six/Saratoga/Lance, Pa-34 Seneca III
- **Bristell** – B23, B23T, RG
- **Cessna** – C172 Skyhawk, C172T Turbo, 210 Centurion, 310R, 340A, 414 Chancellor, C177 Cardinal, C188 AgWagon
- **Diamond** – DA-50 RG, DA-42, DA-62
- **Zlin Aviation** – Norden, Savage Cub
- **de Havilland Canada** – DHC-2 Beaver
- **Mooney** – M20C, M20K, M20J, M20R

#### 2.4.1 Základní jednotky CSV

CSV soubor ukládá všechny hodnoty v **metrických/SI jednotkách**:

| Veličina           | Jednotka v CSV | Příklad sloupce                                      |
|--------------------|----------------|------------------------------------------------------|
| Hmotnost           | kg             | `Empty Weight [kg]`, `MTOW [kg]`, `Useful Load [kg]` |
| Objem (palivo)     | litry          | `Fuel Capacity [l]`                                  |
| Rychlost           | km/h           | `Vcruise_75 [km/h]`, `Vs1 [km/h]`                    |
| Spotřeba           | l/h            | `FF_75 [l/h]`, `FF_55 [l/h]`                         |
| Vzdálenost (dolet) | km             | `Range_MP [km]`, `Range_EC [km]`                     |
| Náklady            | CZK/rok        | `Fixed cost [CZK/yr]`, `Variable cost [CZK/yr]`      |
| Rozměry            | m              | `Wingspan [m]`, `Length [m]`, `Height [m]`           |

> **Poznámka:** Převod z letecky tradičních jednotek (kt, GPH, NM) na metrické byl proveden jednorázově. Backend (`app.py`) interně přepočítává km/h → kt a l/h → GPH pro letové výpočty.

#### 2.4.2 Struktura sloupců CSV

| #     | Sloupec                                                                                       | Skupina      | Popis                                      |
|-------|-----------------------------------------------------------------------------------------------|--------------|--------------------------------------------|
| 0     | `type`                                                                                        | Identifikace | Kategorie letadla (SEP / MEP)              |
| 1     | `Manufacturer`                                                                                | Identifikace | Výrobce                                    |
| 2     | `Designation`                                                                                 | Identifikace | Typové označení                            |
| 3     | `Name`                                                                                        | Identifikace | Obchodní název                             |
| 4     | `No. Seats`                                                                                   | Konfigurace  | Počet sedadel                              |
| 5     | `Gear Type`                                                                                   | Konfigurace  | Typ podvozku                               |
| 6–8   | `Wingspan [m]`, `Length [m]`, `Height [m]`                                                    | Rozměry      | Rozměry letadla                            |
| 9–11  | `Empty Weight [kg]`, `MTOW [kg]`, `Useful Load [kg]`                                          | Hmotnosti    | Hmotnostní údaje                           |
| 12–16 | `Engine Manufacturer`, `Engine type`, `No. pistons`, `Engine power [kW]`, `Engine power [HP]` | Motor        | Pohonná jednotka                           |
| 17    | `Fuel type`                                                                                   | Palivo       | Typ paliva (AVGAS 100LL / JET A1 / MOGAS)  |
| 18    | `Fuel Capacity [l]`                                                                           | Palivo       | Kapacita nádrže [l] – jeden sloupec        |
| 19–22 | `FF_75 [l/h]`, `FF_65 [l/h]`, `FF_55 [l/h]`, `FF_45 [l/h]`                                    | Spotřeba     | Spotřeba paliva při 75%/65%/55%/45% výkonu |
| 23–27 | `Vcruise [km/h]`, `Vcruise_75..45 [km/h]`                                                     | Rychlosti    | Cestovní rychlosti                         |
| 28–34 | `Vs0..Va [km/h]`                                                                              | Rychlosti    | Charakteristické rychlosti                 |
| 35–36 | `Range_MP [km]`, `Range_EC [km]`                                                              | Dolet        | Dolet max power / economy                  |
| 37–38 | `Fixed cost [CZK/yr]`, `Variable cost [CZK/yr]`                                               | Ekonomika    | Roční náklady                              |

---

## 3. Funkční požadavky

### 3.1 Uživatelské rozhraní – Layout

| ID        | Požadavek                                                                                                           | Priorita |
|-----------|---------------------------------------------------------------------------------------------------------------------|----------|
| FR-UI-001 | Aplikace je rozdělena vertikálně na horní panel (vstupní karty) a dolní panel (výsledková tabulka)                  | Musí     |
| FR-UI-002 | Horní panel obsahuje záložky: **Obecné**, **Plán**, **Obsazení**, **Hangár**                                        | Musí     |
| FR-UI-003 | Při přepnutí na záložku Hangár se skryje dolní panel s výsledkovou tabulkou a zobrazí se samostatná tabulka hangáru | Musí     |
| FR-UI-004 | Aplikace používá tmavé barevné schéma (dark mode)                                                                   | Musí     |
| FR-UI-005 | Uživatel může přepínat velikost písma: Small (13 px), Medium (15 px), Large (17 px)                                 | Musí     |

---

### 3.2 Karta Obecné (`general`)

#### 3.2.1 Vstupní pole

| ID         | Pole                       | Klíč                  | Typ        | Výchozí hodnota | Jednotka | Popis                                                 |
|------------|----------------------------|-----------------------|------------|-----------------|----------|-------------------------------------------------------|
| FR-GEN-001 | Cena AVGAS                 | `avgas_price`         | číslo      | 75.0            | CZK/l    | Cena paliva AVGAS 100LL                               |
| FR-GEN-002 | Cena JET A-1               | `jet_a1_price`        | číslo      | 45.0            | CZK/l    | Cena paliva JET A-1                                   |
| FR-GEN-003 | Hustota AVGAS              | `avgas_density`       | číslo      | 0.72            | kg/l     | Hustota AVGAS při 15 °C                               |
| FR-GEN-004 | Hustota JET A-1            | `jet_a1_density`      | číslo      | 0.81            | kg/l     | Hustota JET A-1 při 15 °C                             |
| FR-GEN-005 | Palivová rezerva           | `fuel_reserve_min`    | celé číslo | 30              | min      | Min. VFR rezerva při economy cruise                   |
| FR-GEN-006 | Průměrná váha osoby        | `person_weight_kg`    | číslo      | 95              | kg       | Výchozí váha pilota/cestujícího                       |
| FR-GEN-007 | Průměrné zavazadlo/sedadlo | `baggage_per_seat_kg` | číslo      | 5               | kg       | Průměrná váha zavazadla na sedadlo                    |
| FR-GEN-008 | Nalétané hodiny ročně      | `annual_hours`        | číslo      | 80              | h/rok    | Pro přepočet fixních a variabilních nákladů na hodinu |

#### 3.2.2 Přepínače jednotek

| ID | Přepínač   | Volby                   | Výchozí | Popis                                               |
|---|------------|-------------------------|---------|-----------------------------------------------------|
| FR-GEN-010 | Váha       | kg / lb                 | kg      | Jednotka hmotnosti pro zobrazení                    |
| FR-GEN-011 | Objem      | litr / US gal / Imp gal | litr    | Jednotka objemu pro zobrazení                       |
| FR-GEN-012 | Rychlost   | kt / km/h               | kt      | Jednotka rychlosti pro zobrazení                    |
| FR-GEN-013 | Vzdálenost | NM / km                 | NM      | Jednotka vzdálenosti pro zobrazení a výpočet CpDis  |
| FR-GEN-014 | Měna       | CZK / EUR / USD / GBP   | CZK     | Měna pro zobrazení nákladů                          |

#### 3.2.3 Kurzovní lístek

| ID | Požadavek | Priorita |
|---|---|---|
| FR-GEN-020 | Při výběru cizí měny (EUR/USD/GBP) se zobrazí editovatelné pole kurzu „1 [měna] = X CZK" | Musí |
| FR-GEN-021 | Výchozí kurzy: 1 EUR = 24.545 CZK, 1 USD = 21.315 CZK, 1 GBP = 28.299 CZK | Musí |
| FR-GEN-022 | Změna kurzu automaticky přepočítá výsledkovou tabulku (debounce 600 ms) | Musí |
| FR-GEN-023 | Ceny paliva se vždy zadávají v CZK; výstupní náklady se přepočítávají kurzem do zvolené měny | Musí |

#### 3.2.4 Převodní hodnoty (informativní, needitovatelné)

| ID | Převod | Hodnota |
|---|---|---|
| FR-GEN-030 | 1 US gal → litry | 3.78541 |
| FR-GEN-031 | 1 NM → km | 1.852 |
| FR-GEN-032 | 1 kt → km/h | 1.852 |
| FR-GEN-033 | 1 kg → lbs | 2.20462 |

---

### 3.3 Karta Plán (`plan`)

| ID | Pole | Klíč | Typ | Výchozí hodnota | Popis |
|---|---|---|---|---|---|
| FR-PLN-001 | Vzdálenost A→B (NM) | `distance_nm` | číslo | 200 | Plánovaná vzdálenost letu |
| FR-PLN-002 | Vzdálenost A→B (km) | `distance_km` | číslo | 370 | Stejná vzdálenost v km |
| FR-PLN-003 | Průměrný vítr (kt) | `wind_kt` | číslo | 0 | + = zadní vítr, − = čelní vítr |
| FR-PLN-004 | Alternativní letiště (NM) | `alternate_nm` | číslo | 0 | Vzdálenost k alternativě (informativní) |

| ID | Požadavek | Priorita |
|---|---|---|
| FR-PLN-010 | Pole NM ↔ km jsou vzájemně provázána – změna jednoho automaticky přepočítá druhé (koeficient 1.852) | Musí |
| FR-PLN-011 | Změna vstupů na kartě Plán automaticky přepočítá výsledky (debounce 600 ms) | Musí |

#### 3.3.1 Filtr typu letadla

| ID | Požadavek | Priorita |
|---|---|---|
| FR-PLN-020 | Nad výsledkovou tabulkou je přepínač „Typ: All / SEP / MEP" | Musí |
| FR-PLN-021 | Výchozí hodnota je **All** (zobrazit všechna letadla) | Musí |
| FR-PLN-022 | Při přepnutí na SEP/MEP se ve výsledkové tabulce zobrazí pouze letadla daného typu | Musí |

---

### 3.4 Karta Obsazení (`crew`)

| ID | Pole | Klíč | Výchozí | Popis |
|---|---|---|---|---|
| FR-CRW-001 | Pilot – váha | `pax1_weight` | 95 | Váha pilota [kg] |
| FR-CRW-002 | Pilot – zavazadlo | `pax1_baggage` | 5 | Zavazadlo pilota [kg] |
| FR-CRW-003 | PAX 2 – váha | `pax2_weight` | 65 | Přední cestující [kg] |
| FR-CRW-004 | PAX 2 – zavazadlo | `pax2_baggage` | 5 | Zavazadlo [kg] |
| FR-CRW-005–012 | PAX 3–6 – váha + zavazadlo | `pax3..6_weight/baggage` | 0 | Další cestující (0 = neobsazeno) |

| ID | Požadavek | Priorita |
|---|---|---|
| FR-CRW-020 | Automatický souhrn: Celková hmotnost osádky (kg), Počet obsazených sedadel | Musí |
| FR-CRW-021 | Payload badge v action-baru zobrazuje celkovou hmotnost osádky + zavazadel | Musí |
| FR-CRW-022 | Změna obsazení automaticky přepočítá výsledky (debounce 600 ms) | Musí |
| FR-CRW-023 | Výchozí váha pilota je 95 kg | Musí |

---

### 3.5 Karta Hangár

| ID | Požadavek | Priorita |
|---|---|---|
| FR-HNG-001 | Záložka Hangár zobrazuje statickou tabulku všech letadel z databáze bez výpočtů | Musí |
| FR-HNG-002 | Data se načítají přes API endpoint `GET /api/hangar` | Musí |
| FR-HNG-003 | Tabulka obsahuje skupiny sloupců v pořadí: Identifikace, Konfigurace, Rozměry, Hmotnosti, Nádrž, Motor, Rychlosti, Spotřeba, Dolet, Náklady | Musí |
| FR-HNG-004 | Sloupec „Nádrž" je jeden sloupec `Fuel Capacity [l]`, který se přepočítává podle zvolené objemové jednotky na kartě Obecné | Musí |
| FR-HNG-005 | Rychlosti v tabulce Hangár (uloženy v CSV jako km/h) se přepočítávají dle zvolené jednotky rychlosti (kt / km/h) z karty Obecné | Musí |
| FR-HNG-006 | Hmotnosti v tabulce Hangár respektují zvolené jednotky hmotnosti (kg / lb) z karty Obecné | Musí |
| FR-HNG-007 | Spotřeba (uložena v CSV jako l/h) se přepočítává dle zvolené objemové jednotky z karty Obecné | Musí |
| FR-HNG-008 | Dolet (uložen v CSV jako km) se přepočítává dle zvolené jednotky vzdálenosti (NM / km) z karty Obecné | Musí |
| FR-HNG-009 | Tabulka je sortovatelná kliknutím na záhlaví sloupce (vzestupně / sestupně) | Musí |
| FR-HNG-010 | Nad tabulkou je fulltextové vyhledávání, které filtruje řádky | Musí |
| FR-HNG-011 | Záhlaví sloupců zobrazuje zkrácené názvy, po najetí myší (tooltip) se zobrazí celý popis | Musí |

#### 3.5.1 Kategorie rychlostí v Hangáru

| ID | Požadavek | Priorita |
|---|---|---|
| FR-HNG-020 | Skupina „Rychlosti" obsahuje sloupce: 75%, 65%, 55%, Vs0, **Vs1**, **Vx**, **Vy**, Vno, Vne | Musí |
| FR-HNG-021 | Sloupce Vs1, Vx, Vy mají zkrácený název v záhlaví (Vs1, Vx, Vy) a po najetí myší tooltip s plným popisem | Musí |
| FR-HNG-022 | Tooltip pro Vs1: „Pádová rychlost v čisté konfiguraci (bez klapek)" | Musí |
| FR-HNG-023 | Tooltip pro Vx: „Rychlost nejlepšího úhlu stoupání (největší výška na nejkratší vzdálenost)" | Musí |
| FR-HNG-024 | Tooltip pro Vy: „Rychlost nejlepší rychlosti stoupání (největší výška za jednotku času)" | Musí |

---

### 3.6 Výpočetní logika (Backend)

#### 3.6.1 Definice hmotnostní bilance

| ID | Definice | Vzorec |
|---|---|---|
| FR-CMP-001 | **Payload** | Součet vah všech cestujících + jejich zavazadel (pevná hodnota, nezávislá na letadle) |
| FR-CMP-002 | **Trip Fuel** | Palivo nutné k provedení letu A → B [l] = FuelFlow [l/h] × doba_letu [h] |
| FR-CMP-003 | **Reserve Fuel** | Palivo na `fuel_reserve_min` minut letu při daném FF [l] = FuelFlow [l/h] × (fuel_reserve_min / 60) |
| FR-CMP-004 | **FOB (Fuel On Board)** | Trip Fuel + Reserve Fuel [l] |
| FR-CMP-005 | **Trip Load** | FOB [kg] + Payload [kg] (kde FOB [kg] = FOB [l] × hustota_paliva) |
| FR-CMP-006 | **Load Reserve** | Useful Load − Trip Load [kg] |
| FR-CMP-007 | **Podmínka vhodnosti** | Useful Load ≥ Trip Load → letadlo je vhodné |
| FR-CMP-008 | **MTOW podmínka** | MTOW ≥ TOW (plyne z FR-CMP-007) |

#### 3.6.2 Výpočet pro režim letu

| ID | Požadavek | Priorita |
|---|---|---|
| FR-CMP-010 | Pro každé letadlo se počítají dva výkonové režimy: **Max Power (75 %)** a **Economy Cruise (55 %)** | Musí |
| FR-CMP-011 | Ground Speed (GS) = V_cruise + vítr (min. 1 kt); backend interně převádí km/h z CSV na kt pro výpočet | Musí |
| FR-CMP-012 | Doba letu [h] = vzdálenost [NM] / GS [kt] | Musí |
| FR-CMP-013 | Trip Fuel [l] = FuelFlow [l/h] × doba_letu [h] | Musí |
| FR-CMP-014 | Náklady palivo [CZK] = Trip Fuel [l] × cena_paliva [CZK/l] | Musí |
| FR-CMP-015 | Náklady letadlo [CZK/h] = (fixní_roční_náklady + variabilní_roční_náklady) / nalétané_hodiny_ročně | Musí |
| FR-CMP-016 | Celkové náklady = Náklady palivo + Náklady letadlo × doba_letu | Musí |
| FR-CMP-017 | Pokud FOB > kapacita nádrže → varování o nedostatečném doletu (range_warning) | Musí |

#### 3.6.3 Mezipřistání (Stops)

| ID | Požadavek | Priorita |
|---|---|---|
| FR-CMP-020 | Pokud vzdálenost překračuje dolet na jedno natankování, vypočítá se počet mezipřistání | Musí |
| FR-CMP-021 | Max. dolet jednoho úseku = (kapacita_nádrže − reserve) / FF × GS × 0.8 (bezpečnostní koeficient) | Musí |
| FR-CMP-022 | Počet stops = ceil(vzdálenost / leg_length) − 1 | Musí |
| FR-CMP-023 | Celková doba cesty = doba_letu + stops × 45 min (doba tankování) | Musí |

#### 3.6.4 Vyhodnocení vhodnosti letadla

| ID | Požadavek | Priorita |
|---|---|---|
| FR-CMP-030 | Letadlo je **nevhodné**, pokud obsazených sedadel > kapacita sedadel letadla | Musí |
| FR-CMP-031 | Letadlo je **nevhodné**, pokud Trip Load > Useful Load pro alespoň jeden výkonový profil | Musí |
| FR-CMP-032 | Důvody nevhodnosti se zobrazují textově | Musí |
| FR-CMP-033 | Nevhodnost je vyhodnocena pro každý profil (MP/EC) samostatně | Musí |

#### 3.6.5 Hodinové sazby (Hour Rates)

| ID | Požadavek | Priorita |
|---|---|---|
| FR-CMP-040 | Pro každé letadlo se počítají hodinové sazby nezávisle na vzdálenosti | Musí |
| FR-CMP-041 | Palivo MP/h = FuelFlow_75 [l/h] × cena_paliva × kurz | Musí |
| FR-CMP-042 | Palivo EC/h = FuelFlow_55 [l/h] × cena_paliva × kurz | Musí |
| FR-CMP-043 | Letadlo/h = (fixní + variabilní) / nalétané_hodiny × kurz | Musí |
| FR-CMP-044 | Celkem MP/h = Palivo MP/h + Letadlo/h | Musí |
| FR-CMP-045 | Celkem EC/h = Palivo EC/h + Letadlo/h | Musí |

---

### 3.7 Výsledková tabulka

#### 3.7.1 Režimy zobrazení (View Modes)

| ID | Požadavek | Priorita |
|---|---|---|
| FR-TBL-001 | Přepínač režimů: **⚡ Max Power** / **🍃 Economy** / **⚖ Compare** / **🕐 Hour Rates** | Musí |
| FR-TBL-002 | Výchozí režim je **Compare** | Musí |
| FR-TBL-003 | V každém režimu se zobrazují pouze relevantní skupiny sloupců; ostatní jsou skryté | Musí |

#### 3.7.2 Režim Compare

| ID | Požadavek | Priorita |
|---|---|---|
| FR-TBL-010 | Compare porovnává celkovou cenu z MP a EC – zobrazí tu nižší | Musí |
| FR-TBL-011 | Compare přidává sloupec **Režim** s hodnotou „MP" nebo „EC" podle zvoleného profilu | Musí |
| FR-TBL-012 | Sloupec Režim zobrazuje badge s barevným odlišením (MP = modrý, EC = zelený) | Musí |
| FR-TBL-013 | Sloupce Compare: Režim, Load Reserve, V, Spotřeba, FOB, Trip Fuel, Náklady palivo, Náklady letadlo, Celkem, Doba letu, Mezipřistání, Celková doba cesty | Musí |

#### 3.7.3 Kategorie Studie (v režimu Compare)

| ID | Požadavek | Priorita |
|---|---|---|
| FR-TBL-020 | V režimu Compare se zobrazuje kategorie **📊 Studie** se 3 sloupci | Musí |
| FR-TBL-021 | **CpDis** (Cost per Distance) = celková cena / vzdálenost ve zvolené jednotce (NM nebo km) | Musí |
| FR-TBL-022 | **CpSeat** (Cost per Seat) = celková cena / počet sedadel letadla | Musí |
| FR-TBL-023 | **CpOSeat** (Cost per Occupied Seat) = celková cena / min(kapacita_sedadel, počet_obsazených) | Musí |
| FR-TBL-024 | CpOSeat logika: Pokud letadlo má méně sedadel než cestujících, dělí se cenou letadla / kapacitou (simulace více letadel) | Musí |

> **Příklad CpOSeat** (4 cestující):
> - Debonair (4 místa): cena / 4
> - Bristell B23 (2 místa): cena / 2 (reálně by musela letět 2 letadla)
> - Bonanza (6 míst): cena / 4 (nevyužitá sedadla se nezapočítávají)

#### 3.7.4 Skupiny sloupců tabulky

| Skupina | Sloupce | Zobrazení |
|---|---|---|
| Identifikace (frozen) | Typ, Výrobce, Model, Název | Vždy |
| Hmotnosti | Sedadel, Prázdná, MTOW, Kapacita paliva, Užitečná zátěž | Vždy |
| Max Power (75 %) | Load Reserve, V, Spotřeba, FOB, Trip Fuel, Náklady palivo/letadlo/celkem, Doba letu, Mezipřistání, Celk. doba, Varování | Režim Max Power |
| Economy (55 %) | Load Reserve, V, Spotřeba, FOB, Trip Fuel, Náklady palivo/letadlo/celkem, Doba letu, Mezipřistání, Celk. doba, Varování | Režim Economy |
| Compare | Režim, Load Reserve, V, Spotřeba, FOB, Trip Fuel, Náklady palivo/letadlo/celkem, Doba letu, Mezipřistání, Celk. doba | Režim Compare |
| Studie | CpDis, CpSeat, CpOSeat | Režim Compare |
| Hour Rates | Spotřeba MP, Palivo MP/h, Spotřeba EC, Palivo EC/h, Letadlo/h, Celkem MP/h, Celkem EC/h | Režim Hour Rates |

#### 3.7.5 Řazení a filtrování

| ID | Požadavek | Priorita |
|---|---|---|
| FR-TBL-030 | Výchozí řazení: vhodná letadla nahoře, pak dle Compare celkových nákladů vzestupně | Musí |
| FR-TBL-031 | Kliknutím na záhlaví sloupce lze řadit vzestupně / sestupně | Musí |
| FR-TBL-032 | Šipka ▲/▼ v záhlaví indikuje směr řazení | Musí |
| FR-TBL-033 | Tlačítko „Zobrazit nevhodná" / „Skrýt nevhodná" přepíná viditelnost nevhodných letadel | Musí |
| FR-TBL-034 | Filtr typu (All / SEP / MEP) omezuje zobrazení na danou kategorii | Musí |

#### 3.7.6 Vizuální značení

| ID | Značení | Popis |
|---|---|---|
| FR-TBL-040 | Nejlevnější vhodné letadlo je zvýrazněno zeleným řádkem (třída `best-row`) | Musí |
| FR-TBL-041 | Nevhodná letadla mají šedý text a jsou standardně skrytá | Musí |
| FR-TBL-042 | Buňky nevhodného profilu mají červený text (`col-fail`) | Musí |
| FR-TBL-043 | Load Reserve < 0 má červený text, ≥ 0 zelený | Musí |
| FR-TBL-044 | Mezipřistání > 0 mají žlutý tučný text | Musí |
| FR-TBL-045 | Varování ⚠ se zobrazuje u letadel s FOB > kapacita nádrže | Musí |
| FR-TBL-046 | Sloupce Identifikace (první 4) jsou přichycené (sticky left) s shadows | Musí |

#### 3.7.7 Souhrn pod tabulkou

| ID | Požadavek | Priorita |
|---|---|---|
| FR-TBL-050 | Zobrazení počtu: „X vhodných z Y letadel" | Musí |
| FR-TBL-051 | Nejlevnější letadlo: typové označení + cena + režim (MP/EC) | Musí |
| FR-TBL-052 | Nejrychlejší letadlo: typové označení + doba letu (max power) | Musí |

---

### 3.8 Převod jednotek v tabulce

| ID | Požadavek | Priorita |
|---|---|---|
| FR-UNT-001 | Hmotnosti (Prázdná, MTOW, Užitečná zátěž, Load Reserve, Trip Load) se přepočítávají dle zvolené přepínače kg/lb | Musí |
| FR-UNT-002 | Objemy (Kapacita paliva, FOB, Trip Fuel) se přepočítávají dle zvolené přepínače l/US gal/Imp gal | Musí |
| FR-UNT-003 | Spotřeba za hodinu se přepočítává dle zvolené přepínače objemu | Musí |
| FR-UNT-004 | Rychlosti se přepočítávají dle zvolené přepínače kt/kmh | Musí |
| FR-UNT-005 | Záhlaví sloupců se dynamicky aktualizují při změně jednotky (zobrazují aktuální jednotku) | Musí |
| FR-UNT-006 | Změna jednotky okamžitě přepočítá zobrazení (bez nového API volání) | Musí |

---

### 3.9 Měna

| ID | Požadavek | Priorita |
|---|---|---|
| FR-CUR-001 | Podpora měn: CZK (Kč), EUR (€), USD ($), GBP (£) | Musí |
| FR-CUR-002 | Ceny paliva se vždy zadávají v CZK | Musí |
| FR-CUR-003 | Výstupní náklady se přepočítávají kurzem: cena_CZK / kurz_cizí_měny_za_CZK | Musí |
| FR-CUR-004 | Záhlaví nákladových sloupců zobrazuje aktuální symbol měny | Musí |
| FR-CUR-005 | Pro CZK se náklady formátují bez desetinných míst, pro cizí měny s 2 desetinnými místy | Musí |

---

### 3.10 REST API

#### 3.10.1 `POST /api/compute`

| Vlastnost    | Hodnota                                                                                                     |
|--------------|-------------------------------------------------------------------------------------------------------------|
| Metoda       | POST                                                                                                        |
| Content-Type | application/json                                                                                            |
| Vstup        | JSON objekt se všemi parametry z karet Obecné + Plán + Obsazení                                             |
| Výstup       | JSON: `{ ok, planes[], currency, currency_symbol, weight_unit, volume_unit, total_pax_kg, occupied_seats }` |

**Vstupní parametry:**

| Parametr                       | Typ    | Popis                          |
|--------------------------------|--------|--------------------------------|
| `avgas_price`                  | float  | Cena AVGAS [CZK/l]             |
| `jet_a1_price`                 | float  | Cena JET A-1 [CZK/l]           |
| `avgas_density`                | float  | Hustota AVGAS [kg/l]           |
| `jet_a1_density`               | float  | Hustota JET A-1 [kg/l]         |
| `fuel_reserve_min`             | float  | Palivová rezerva [min]         |
| `person_weight_kg`             | float  | Průměrná váha osoby [kg]       |
| `baggage_per_seat_kg`          | float  | Průměrné zavazadlo [kg]        |
| `annual_hours`                 | float  | Nalétané hodiny/rok (min. 1)   |
| `currency`                     | string | Zvolená měna (CZK/EUR/USD/GBP) |
| `eur_to_czk`                   | float  | Kurz 1 EUR = X CZK             |
| `usd_to_czk`                   | float  | Kurz 1 USD = X CZK             |
| `gbp_to_czk`                   | float  | Kurz 1 GBP = X CZK             |
| `weight_unit`                  | string | Jednotka hmotnosti (kg/lb)     |
| `volume_unit`                  | string | Jednotka objemu (l/usg/img)    |
| `distance_nm`                  | float  | Vzdálenost [NM]                |
| `wind_kt`                      | float  | Složka větru [kt]              |
| `pax1_weight`..`pax6_weight`   | float  | Váhy cestujících               |
| `pax1_baggage`..`pax6_baggage` | float  | Zavazadla cestujících          |

**Výstupní struktura jednoho letadla:**

```json
{
  "type": "SEP",
  "manufacturer": "Beechcraft",
  "designation": "G33",
  "name": "Debonair",
  "no_seats": 4,
  "empty_weight": "880",
  "mtow": "1338",
  "useful_load": "458",
  "fuel_type": "AVGAS 100LL",
  "fuel_cap_l": 280,
  "payload_kg": 175.0,
  "suitable": true,
  "unsuitable_reason": "",
  "fail_seats": false,
  "fail_load": false,
  "fail_load_mp": false,
  "fail_load_ec": false,
  "max_power": {
    "v_kt": 160, "v_kmh": 296, "ff_gph": 13.0, "ff_lph": 49.2,
    "flight_time_h": 1.25, "flight_time_fmt": "1h 15m",
    "trip_fuel_l": 61.5, "fob_l": 69.9,
    "trip_load_kg": 225.3, "load_reserve_kg": 232.7,
    "fuel_cost": 4612.5, "plane_cost": 1250.0, "total_cost": 5862.5,
    "range_warning": false, "stops": 0, "leg_nm": null,
    "total_time_h": 1.25, "total_time_fmt": "1h 15m"
  },
  "econ_cruise": { "..." },
  "hour_rates": {
    "mp_ff_lph": 49.2, "mp_fuel_cost_ph": 3690.0,
    "ec_ff_lph": 37.9, "ec_fuel_cost_ph": 2842.5,
    "plane_cost_ph": 1000.0,
    "mp_total_ph": 4690.0, "ec_total_ph": 3842.5
  },
  "currency": "CZK",
  "currency_symbol": "Kč",
  "weight_unit": "kg",
  "volume_unit": "l"
}
```

#### 3.10.2 `GET /api/hangar`

| Vlastnost | Hodnota |
|---|---|
| Metoda | GET |
| Výstup | JSON: `{ ok, columns[], rows[] }` |
| Popis | Vrátí surová data z plane_table.csv pro záložku Hangár |

**Vrácené skupiny sloupců (nová struktura CSV):**
- Identifikace: `type`, `Manufacturer`, `Designation`, `Name`
- Konfigurace: `No. Seats`, `Gear Type`, `Fuel type`
- Rozměry: `Wingspan [m]`, `Length [m]`, `Height [m]`
- Hmotnosti: `Empty Weight [kg]`, `MTOW [kg]`, `Useful Load [kg]`
- Nádrž: `Fuel Capacity [l]` (jeden sloupec v litrech)
- Motor: `Engine Manufacturer`, `Engine type`, `No. pistons`, `Engine power [HP]`, `Engine power [kW]`
- Rychlosti [km/h]: `Vcruise_75`, `Vcruise_65`, `Vcruise_55`, `Vs0`, `Vs1`, `Vx`, `Vy`, `Vno`, `Vne`
- Spotřeba [l/h]: `FF_75`, `FF_55`
- Dolet [km]: `Range_MP`, `Range_EC`
- Náklady [CZK/rok]: `Fixed cost [CZK/yr]`, `Variable cost [CZK/yr]`

---

### 3.11 Auto-výpočet

| ID | Požadavek | Priorita |
|---|---|---|
| FR-AUT-001 | Při načtení stránky se automaticky spustí výpočet s výchozími hodnotami | Musí |
| FR-AUT-002 | Při změně obsazení se výpočet spustí automaticky (debounce 600 ms) | Musí |
| FR-AUT-003 | Při změně polí na kartě Plán se výpočet spustí automaticky (debounce 600 ms) | Musí |
| FR-AUT-004 | Při změně měny nebo kurzu se výpočet spustí automaticky | Musí |
| FR-AUT-005 | Během výpočtu se zobrazí spinner s textem „⏳ Počítám…" | Musí |
| FR-AUT-006 | Status bar zobrazuje čas poslední aktualizace nebo chybovou hlášku | Musí |

---

## 4. Nefunkční požadavky

### 4.1 Výkonnost

| ID | Požadavek | Priorita |
|---|---|---|
| NFR-PRF-001 | API `/api/compute` odpovídá do 2 sekund pro celou databázi (~30 letadel) | Musí |
| NFR-PRF-002 | Render tabulky v prohlížeči probíhá plynule (<100 ms) | Měl by |
| NFR-PRF-003 | Debounce vstupů je nastaven na 600 ms pro zabránění nadměrného volání API | Musí |

### 4.2 Kompatibilita

| ID | Požadavek | Priorita |
|---|---|---|
| NFR-CMP-001 | Aplikace funguje v moderních prohlížečích: Chrome, Firefox, Edge, Safari | Musí |
| NFR-CMP-002 | Testy jsou spouštěny přes Playwright s Chromium | Musí |
| NFR-CMP-003 | Backend je kompatibilní s Python 3.13+ | Musí |

### 4.3 Nasazení

| ID | Požadavek | Priorita |
|---|---|---|
| NFR-DEP-001 | Aplikace podporuje nasazení na Vercel jako serverless Python | Musí |
| NFR-DEP-002 | Vstupní bod pro Vercel: `api/index.py` importuje Flask app | Musí |
| NFR-DEP-003 | `vercel.json` routuje všechny požadavky na `api/index.py` | Musí |
| NFR-DEP-004 | Lokální spuštění: `python app.py` → `http://127.0.0.1:5000` | Musí |
| NFR-DEP-005 | Závislosti definovány v `requirements.txt` | Musí |

### 4.4 Testování

| ID | Požadavek | Priorita |
|---|---|---|
| NFR-TST-001 | Automatizované testy pokrývají API (unit testy přes Flask test client) | Musí |
| NFR-TST-002 | Automatizované testy pokrývají UI (E2E testy přes Playwright) | Musí |
| NFR-TST-003 | Testy se spouštějí přes `pytest` s konfigurací v `pytest.ini` | Musí |
| NFR-TST-004 | Flask test server běží na portu 5099 pro izolaci od produkčního serveru | Musí |

### 4.5 Udržovatelnost

| ID | Požadavek | Priorita |
|---|---|---|
| NFR-MNT-001 | Data letadel jsou udržována v jednom CSV souboru | Musí |
| NFR-MNT-002 | Technická data letadel se doplňují přes script `fill_data.py` | Měl by |
| NFR-MNT-003 | Odvozená data se počítají přes script `compute_data.py` | Měl by |
| NFR-MNT-004 | Konstanty (hustoty, převodní jednotky, ceny) jsou centralizovány v `setup.py` a `config.py` | Musí |

### 4.6 Uživatelská přívětivost

| ID | Požadavek | Priorita |
|---|---|---|
| NFR-UX-001 | Formátování čísel používá české locale (oddělovač tisíců = mezera, des. čárka) | Musí |
| NFR-UX-002 | Doba letu se zobrazuje ve formátu `Xh YYm` | Musí |
| NFR-UX-003 | Chybějící / nevypočitatelné hodnoty se zobrazují jako „–" | Musí |
| NFR-UX-004 | Finanční hodnoty obsahují symbol měny za číslem | Musí |

---

## 5. Datový model

### 5.1 Základní jednotky CSV (plane_table.csv)

CSV soubor používá výhradně metrické / SI jednotky jako základ:

| Veličina | Základní jednotka v CSV | Převod z leteckých jednotek |
|---|---|---|
| Hmotnost | kg | – (přímo) |
| Objem paliva | l (litry) | US gal × 3.78541 |
| Rychlost | km/h | kt × 1.852 |
| Spotřeba | l/h | GPH × 3.78541 |
| Vzdálenost | km | NM × 1.852 |
| Náklady | CZK/rok | – (přímo) |

> Backend (`app.py`) při výpočtech interně převádí km/h → kt a l/h → GPH, protože letové výpočty (ground speed, doba letu) pracují v námořních jednotkách.

### 5.2 Fyzikální konstanty (setup.py)

| Konstanta | Hodnota | Popis |
|---|---|---|
| AVGAS_DENSITY_KPL | 0.72 | Hustota AVGAS 100LL [kg/l] |
| JET_A1_DENSITY_KPL | 0.81 | Hustota JET A-1 [kg/l] |
| GAL_TO_LITERS | 3.78541 | 1 US galon → litry |
| NM_TO_KM | 1.852 | 1 NM → km |
| KT_TO_KPH | 1.852 | 1 kt → km/h |
| KG_TO_LBS | 2.20462 | 1 kg → libry |

### 5.3 Výchozí konfigurace (config.py)

Soubor `config.py` obsahuje výchozí hodnoty pro offline výpočty (`compute_data.py`).
Webová aplikace (`app.py`) používá vlastní výchozí hodnoty z UI:

| Parametr | config.py (offline) | app.py / UI (webová) | Popis |
|---|---|---|---|
| PERSON_WEIGHT_KG | 76 | **95** | Průměrná váha osoby |
| BAGGAGE_PER_SEAT_KG | 5 | 5 | Průměrné zavazadlo/sedadlo |
| SEAT_WEIGHT_KG | 81 | 100 | Celková váha na sedadlo (osoba + zavazadlo) |
| FUEL_RESERVE_MINUTES | 30 | 30 | VFR palivová rezerva [min] |

### 5.4 Výchozí měnové kurzy (app.py)

| Měna | 1 cizí = X CZK |
|---|---|
| EUR | 24.545 |
| USD | 21.315 |
| GBP | 28.299 |

---

## 6. Soubory a struktura projektu

```
PlaneComparison/
├── app.py                      # Flask backend (výpočetní logika + API endpointy)
├── config.py                   # Konfigurace pro offline výpočty (váhy posádky)
├── setup.py                    # Fyzikální konstanty a převodní jednotky
├── compute_data.py             # Offline výpočet odvozených dat do CSV
├── fill_data.py                # Doplnění technických dat do CSV z POH (POZOR: používá staré názvy sloupců)
├── main.py                     # Vývojový entry point (nepoužívaný)
├── plane_table.csv             # Hlavní databáze letadel (39 sloupců, metrické jednotky)
├── plane_table_calculated.csv  # Odvozená data (offline výpočet – může být zastaralý)
├── plane_table_backup_20260330.csv  # Záloha CSV před restrukturalizací
├── requirements.txt            # Python závislosti
├── vercel.json                 # Konfigurace Vercel nasazení
├── pytest.ini                  # Konfigurace testů
├── global_values.md            # Poznámky k referenčním hodnotám
├── api/
│   └── index.py                # Vercel serverless entry point
├── docs/
│   ├── input_cards_definition.md
│   ├── table_definition.md
│   ├── weight_balance_rules.md
│   └── SRS.md                  # Tento dokument
├── templates/
│   └── index.html              # SPA frontend (HTML + CSS + JS)
└── tests/
    ├── conftest.py             # Sdílené test fixtures (Flask server, Playwright page)
    ├── test_api.py             # API unit testy
    ├── test_compute.py         # Testy výpočtu a zobrazení
    ├── test_crew_summary.py    # Testy souhrnu obsazení
    ├── test_currency.py        # Testy měnových přepočtů
    ├── test_font_size.py       # Testy přepínání velikosti písma
    ├── test_hangar.py          # Testy záložky Hangár
    ├── test_nm_km_sync.py      # Testy synchronizace NM ↔ km
    ├── test_sorting.py         # Testy řazení tabulky
    ├── test_tabs.py            # Testy přepínání záložek
    ├── test_ui_layout.py       # Testy rozložení UI
    ├── test_units.py           # Testy přepínání jednotek
    └── test_unsuitable.py      # Testy zobrazení nevhodných letadel
```

---

## 7. Testovací pokrytí

### 7.1 API testy (`test_api.py`)

| Oblast | Pokrytí |
|---|---|
| Základní API odpověď | HTTP 200, `ok: true`, struktura planes[] |
| Struktura letadla | Povinné klíče: type, manufacturer, designation, name, no_seats, suitable, max_power, econ_cruise |
| Struktura profilu | v_kt, v_kmh, ff_lph, flight_time_h, trip_fuel_l, fob_l, trip_load_kg, load_reserve_kg, fuel_cost, total_cost |
| Hmotnostní bilance | Payload, trip_load, load_reserve, podmínka vhodnosti |
| Měnové přepočty | EUR, USD, GBP kurzy |
| Hour Rates | Hodinové sazby a roční náklady |

### 7.2 UI / E2E testy (Playwright)

| Soubor | Oblast |
|---|---|
| test_compute.py | Auto-výpočet, tabulka s řádky, formát doby letu, souhrn, range warning |
| test_crew_summary.py | Souhrn obsazení, celková hmotnost, počet sedadel |
| test_currency.py | Přepínání měn, zobrazení kurzů |
| test_font_size.py | Přepínání velikosti písma |
| test_hangar.py | Načtení hangáru, vyhledávání, sortování |
| test_nm_km_sync.py | Synchronizace NM ↔ km polí |
| test_sorting.py | Řazení tabulky kliknutím na záhlaví |
| test_tabs.py | Přepínání záložek |
| test_ui_layout.py | Rozložení panelů, viditelnost prvků |
| test_units.py | Přepínání jednotek (kg/lb, l/gal, kt/kmh) |
| test_unsuitable.py | Zobrazení/skrytí nevhodných letadel |

---

## 8. Převodní vzorce (reference)

| Převod | Vzorec |
|---|---|
| US gal → litry | `gal × 3.78541` |
| litry → US gal | `l × 0.264172` |
| litry → Imp gal | `l × 0.219969` |
| kg → lb | `kg × 2.20462` |
| lb → kg | `lb × 0.453592` |
| NM → km | `NM × 1.852` |
| kt → km/h | `kt × 1.852` |
| GPH → LPH | `gph × 3.78541` |
| FOB [kg] | `FOB [l] × hustota_paliva [kg/l]` |
| Náklady v cizí měně | `náklady_CZK / kurz_cizí_za_CZK` |

---

## 9. Historie změn

| Verze | Datum | Autor | Popis |
|---|---|---|---|
| 1.0 | 2026-03-30 | – | Prvotní vytvoření SRS z existujícího zdrojového kódu |
| 1.1 | 2026-03-30 | – | Aktualizace po restrukturalizaci CSV: nové názvy sloupců (metrické jednotky: km/h, l/h, km), deduplikace (39 sloupců), odstranění offline-computed sloupců, aktualizace API dokumentace |

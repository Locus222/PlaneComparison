# Definice výsledkové tabulky letadel – PlaneComparison

Tabulka je zobrazena v dolní polovině okna aplikace.
Každý řádek odpovídá jednomu letadlu ze souboru `plane_table.csv`.
Letadla **nevhodná pro daný let** jsou vizuálně odlišena (šedá / přeškrtnutá) nebo zcela skryta.

---

## Skupiny sloupců

### A – Identifikace letadla

| Sloupec | Zdroj | Popis |
|---|---|---|
| Typ | `type` | Kategorie (SEP / MEP / TME …) |
| Výrobce | `Manufacturer` | Výrobce letadla |
| Označení | `Designation` | Typové označení |
| Název | `Name` | Obchodní název |


---

### B – Hmotnosti a payload

| Sloupec | Zdroj / Výpočet | Popis |
|---|---|---|
| Sedadla | `No. Seats` | Celkový počet sedadel |
| Prázdná hmotnost (kg) | `Empty Weight [kg]` | Prázdná hmotnost dle POH |
| MTOW (kg) | `MTOW [kg]` | Max. vzletová hmotnost |
| Užitečné zatížení (kg) | `Usefull Load [kg]` | MTOW − prázdná hmotnost |
| **Payload letu (kg)** | `Usefull Load` − `celková hmotnost osádky` | **Vypočteno** – kolik zbývá na palivo |
| Vhodné | logika | ✅ / ❌ – letadlo zvládne obsazení |

---

### C – Výsledky pro **Max Power (75 %)**

| Sloupec | Výpočet | Popis |
|---|---|---|
| Cestovní rychlost (kt) | `Vcruise 75%` | Přímá hodnota z tabulky |
| Cestovní rychlost (km/h) | `Vcruise 75%` × 1.852 | Převedeno |
| Spotřeba (GPH) | `FuelFlow_75_gph` | Palivo za hodinu v US galony |
| Spotřeba (l/h) | `FuelFlow_75_gph` × 3.785 | Přepočteno na litry |
| Doba letu (h:mm) | `vzdálenost_nm` / (`Vcruise 75%` + `vítr`) | Plánovaná doba letu |
| Spotřeba letu (l) | `Spotřeba (l/h)` × `Doba letu (h)` | Celkové palivo na let |
| Náklady palivo | `Spotřeba letu (l)` × `cena paliva` × `kurz` | Cena paliva za let (ve zvolené měně) |
| Náklady letadlo | `total cost per hour` × `Doba letu (h)` × `kurz` | Provozní náklady za let (ve zvolené měně) |
| **Celkové náklady** | Palivo + letadlo | Celkem za let (ve zvolené měně) |

---

### D – Výsledky pro **Economy Cruise (55 %)**

| Sloupec | Výpočet | Popis |
|---|---|---|
| Cestovní rychlost (kt) | `Vcruise 55%` | Přímá hodnota z tabulky |
| Cestovní rychlost (km/h) | `Vcruise 55%` × 1.852 | Převedeno |
| Spotřeba (GPH) | `FuelFlow_55_gph` | Palivo za hodinu v US galony |
| Spotřeba (l/h) | `FuelFlow_55_gph` × 3.785 | Přepočteno na litry |
| Doba letu (h:mm) | `vzdálenost_nm` / (`Vcruise 55%` + `vítr`) | Plánovaná doba letu |
| Spotřeba letu (l) | `Spotřeba (l/h)` × `Doba letu (h)` | Celkové palivo na let |
| Náklady palivo | `Spotřeba letu (l)` × `cena paliva` × `kurz` | Cena paliva za let (ve zvolené měně) |
| Náklady letadlo | `total cost per hour` × `Doba letu (h)` × `kurz` | Provozní náklady za let (ve zvolené měně) |
| **Celkové náklady** | Palivo + letadlo | Celkem za let (ve zvolené měně) |

---

## Pravidla zobrazení

| Stav | Vizuální označení |
|---|---|
| Letadlo vhodné | Normální řádek (bílý / střídavý) |
| Nedostatečný payload (přetíženo) | Červený odznak / šedý řádek / přeškrtnutý |
| Málo sedadel | Červený odznak / šedý řádek |
| Nedostatečný dolet (vzdálenost > range) | Oranžový odznak / varování |
| Nejlepší letadlo dle celkových nákladů | Zelené zvýraznění řádku |

---

## Měna nákladů

Měna se nastavuje na kartě **Obecné**. Ceny paliva se vždy zadávají v CZK;
výsledné náklady se přepočítají kurzem do zvolené měny.

| Měna | Symbol | Výchozí kurz (CZK → měna) |
|---|---|---|
| CZK | Kč | 1.0 (žádný převod) |
| EUR | € | 0.04 (1 CZK = 0.04 EUR) |
| USD | $ | 0.0435 (1 CZK = 0.0435 USD) |
| GBP | £ | 0.0345 (1 CZK = 0.0345 GBP) |

Kurzy jsou editovatelné na kartě Obecné (zobrazí se po výběru měny).
Záhlaví nákladových sloupců v tabulce se automaticky aktualizuje na symbol zvolené měny.

---

## Řazení a filtrování

- Výchozí řazení: **Celkové náklady economy cruise** vzestupně
- Tlačítko pro přepnutí: zobrazit všechna / skrýt nevhodná letadla
- Kliknutím na záhlaví sloupce lze třídit vzestupně / sestupně

---

## Souhrn pod tabulkou

| Hodnota | Popis |
|---|---|
| Počet zobrazených letadel | Z celkového počtu v databázi |
| Nejlevnější let | Označení nejlevnějšího letadla a cena (ve zvolené měně) |
| Nejrychlejší let (h:mm) | Označení nejrychlejšího letadla a čas |

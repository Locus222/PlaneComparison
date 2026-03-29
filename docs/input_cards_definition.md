# Definice vstupních karet webové aplikace PlaneComparison

Okno aplikace je rozděleno horizontálně:
- **Horní polovina** – vstupní karty (záložky): Obecné | Plán | Obsazení
- **Dolní polovina** – výsledková tabulka letadel

---

## Karta 1 – Obecné (`general`)

Obsahuje globální konstanty platné pro všechny výpočty.

| Pole | Klíč | Typ | Výchozí hodnota | Popis |
|---|---|---|---|---|
| Cena AVGAS (CZK/l) | `avgas_price` | číslo | 75.0 | Cena AVGAS 100LL v CZK za litr |
| Cena JET A-1 (CZK/l) | `jet_a1_price` | číslo | 45.0 | Cena JET A-1 v CZK za litr |
| Hustota AVGAS (kg/l) | `avgas_density` | číslo | 0.72 | Hustota paliva AVGAS 100LL |
| Hustota JET A-1 (kg/l) | `jet_a1_density` | číslo | 0.81 | Hustota paliva JET A-1 |
| Palivová rezerva (min) | `fuel_reserve_min` | celé číslo | 30 | Min. VFR rezerva v minutách letu při ekon. cruise |
| Prům. váha osoby (kg) | `person_weight_kg` | číslo | 76 | Průměrná váha cestujícího bez zavazadla |
| Prům. zavazadlo/sedadlo (kg) | `baggage_per_seat_kg` | číslo | 5 | Průměrná váha zavazadla na sedadlo |

### Převodní hodnoty (zobrazeny informativně, needitovatelné)

| Převod | Hodnota |
|---|---|
| 1 US gallon → litry | 3.78541 |
| 1 NM → km | 1.852 |
| 1 kt → km/h | 1.852 |
| 1 kg → lbs | 2.20462 |

---

## Karta 2 – Plán (`plan`)

Popisuje konkrétní naplánovaný let.

| Pole | Klíč | Typ | Výchozí hodnota | Popis |
|---|---|---|---|---|
| Vzdálenost A→B (NM) | `distance_nm` | číslo | 200 | Plánovaná vzdálenost letu v námořních mílích |
| Vzdálenost A→B (km) | `distance_km` | číslo | 370 | Stejná vzdálenost v km (provázaný výpočet) |
| Průměrný vítr (kt) | `wind_kt` | číslo | 0 | Složka větru podél trati: + = zadní vítr, − = čelní |
| Alternativní letiště (NM) | `alternate_nm` | číslo | 0 | Vzdálenost k alternativnímu letišti (ovlivňuje rezervu) |

> **Poznámka:** Pole vzdálenost NM ↔ km jsou vzájemně provázána – změna jednoho automaticky přepočte druhé.

---

## Karta 3 – Obsazení (`crew`)

Definuje skutečnou osádku a zavazadla pro konkrétní let.

| Pole | Klíč | Typ | Výchozí hodnota | Popis |
|---|---|---|---|---|
| Pilot – váha (kg) | `pax1_weight` | číslo | 100 | Váha pilota |
| Pilot – zavazadlo (kg) | `pax1_baggage` | číslo | 5 | Zavazadlo pilota |
| PAX 2 – váha (kg) | `pax2_weight` | číslo | 65 | Přední cestující – váha |
| PAX 2 – zavazadlo (kg) | `pax2_baggage` | číslo | 5 | Přední cestující – zavazadlo |
| PAX 3 – váha (kg) | `pax3_weight` | číslo | 0 | Zadní cestující 1 – váha (0 = neobsazeno) |
| PAX 3 – zavazadlo (kg) | `pax3_baggage` | číslo | 0 | Zadní cestující 1 – zavazadlo |
| PAX 4 – váha (kg) | `pax4_weight` | číslo | 0 | Zadní cestující 2 – váha |
| PAX 4 – zavazadlo (kg) | `pax4_baggage` | číslo | 0 | Zadní cestující 2 – zavazadlo |
| PAX 5 – váha (kg) | `pax5_weight` | číslo | 0 | Zadní cestující 3 – váha (jen vícemístná) |
| PAX 5 – zavazadlo (kg) | `pax5_baggage` | číslo | 0 | Zadní cestující 3 – zavazadlo |
| PAX 6 – váha (kg) | `pax6_weight` | číslo | 0 | Zadní cestující 4 – váha (jen vícemístná) |
| PAX 6 – zavazadlo (kg) | `pax6_baggage` | číslo | 0 | Zadní cestující 4 – zavazadlo |

### Souhrn (vypočteno automaticky)

| Hodnota | Popis |
|---|---|
| **Celková hmotnost osádky (kg)** | Součet všech vah + zavazadel |
| **Počet obsazených sedadel** | Počet osob s váhou > 0 |

---

## Logika výpočtů (spouštěna po změně libovolného pole)

1. **Payload** = `Usefull Load [kg]` − `celková hmotnost osádky`
2. **Vyřazení nevhodných letadel** – letadlo je vyřazeno, pokud:
   - payload < 0 (letadlo přetíženo)
   - počet obsazených sedadel > `No. Seats`
3. **Pro vhodná letadla** se počítají dvě sady výsledků:
   - **Max power (75%):** Vcruise 75%, doba letu, spotřeba, náklady na palivo, náklady na letadlo
   - **Economy cruise (55%):** Vcruise 55%, doba letu, spotřeba, náklady na palivo, náklady na letadlo


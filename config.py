# =============================================================================
# config.py – konfigurace konkrétního letu
# Upravte tyto hodnoty podle plánované posádky a letu.
# =============================================================================

# --- Váhy cestujících a zavazadel ---
# Zadejte skutečné váhy pro každé obsazené místo.
# Neobsazená místa nastavte na 0.

PAX1_WEIGHT_KG   = 100   # pilot (sedí vepředu)
PAX1_BAGGAGE_KG  =   5   # zavazadlo pilota

PAX2_WEIGHT_KG   =  65   # přední cestující
PAX2_BAGGAGE_KG  =   5   # zavazadlo předního cestujícího

PAX3_WEIGHT_KG   =   0   # zadní cestující 1
PAX3_BAGGAGE_KG  =   0

PAX4_WEIGHT_KG   =   0   # zadní cestující 2
PAX4_BAGGAGE_KG  =   0

PAX5_WEIGHT_KG   =   0   # zadní cestující 3 (jen vícemístná letadla)
PAX5_BAGGAGE_KG  =   0

PAX6_WEIGHT_KG   =   0   # zadní cestující 4 (jen vícemístná letadla)
PAX6_BAGGAGE_KG  =   0

# --- Vypočtené celkové váhy posádky ---
# Přední dvojice (pilot + PAX2) – používáno pro výpočty range/endurance
FRONT_CREW_WEIGHT_KG = (PAX1_WEIGHT_KG + PAX1_BAGGAGE_KG
                        + PAX2_WEIGHT_KG + PAX2_BAGGAGE_KG)

# Celková hmotnost všech cestujících i se zavazadly
TOTAL_PAX_WEIGHT_KG  = (PAX1_WEIGHT_KG + PAX1_BAGGAGE_KG
                        + PAX2_WEIGHT_KG + PAX2_BAGGAGE_KG
                        + PAX3_WEIGHT_KG + PAX3_BAGGAGE_KG
                        + PAX4_WEIGHT_KG + PAX4_BAGGAGE_KG
                        + PAX5_WEIGHT_KG + PAX5_BAGGAGE_KG)

# --- Průměrná váha cestujícího pro výpočet max. payload ---
# Použito při výpočtu "Fuel with max Payload" (standardní hodnota)
PERSON_WEIGHT_KG    = 76   # průměrná váha osoby [kg]
BAGGAGE_PER_SEAT_KG =  5   # průměrné zavazadlo na sedadlo [kg]
SEAT_WEIGHT_KG      = PERSON_WEIGHT_KG + BAGGAGE_PER_SEAT_KG  # 81 kg

# --- Palivová rezerva ---
# Minimální VFR rezerva = 30 minut letu při ekonomickém cruise
FUEL_RESERVE_MINUTES = 30

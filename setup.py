# =============================================================================
# setup.py – obecné konstanty, fyzikální hodnoty, ceny a převodní jednotky
# =============================================================================

# --- Hustota paliva ---
# AVGAS 100LL při 15 °C
AVGAS_DENSITY_KPL   = 0.72   # kg/l
# JET A-1 při 15 °C
JET_A1_DENSITY_KPL  = 0.81   # kg/l

# --- Ceny paliva (CZK/litr) ---
AVGAS_PRICE_CZK_PER_LITER   = 75.0   # orientační cena AVGAS 100LL
JET_A1_PRICE_CZK_PER_LITER  = 45.0   # orientační cena JET A-1

# --- Cena motorového oleje ---
OIL_PRICE_CZK_PER_LITER = 350.0   # CZK/litr

# --- Převodní jednotky ---
GAL_TO_LITERS   = 3.78541          # 1 US gallon → litry
LITERS_TO_GAL   = 1 / GAL_TO_LITERS
KG_TO_LBS       = 2.20462          # 1 kg → libry
LBS_TO_KG       = 1 / KG_TO_LBS
NM_TO_KM        = 1.852            # 1 NM → km
KM_TO_NM        = 1 / NM_TO_KM
KT_TO_KPH       = 1.852            # 1 kt → km/h
KPH_TO_KT       = 1 / KT_TO_KPH


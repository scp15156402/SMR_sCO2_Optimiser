"""config.py: every fixed number in the study, grouped by where it comes from."""

# ---------- A. Fixed by the brief ----------
Q_THERMAL_MW       = 100.0    # reactor heat input
ETA_COMPRESSOR     = 0.89     # isentropic, every compressor
ETA_TURBINE        = 0.90     # isentropic
T_WATER_IN_C       = 25.0     # cooling water supply
HOURS_PER_YEAR     = 7000.0
USD_PER_MWH        = 70.0     # electricity value
USD_PER_KG         = 250.0    # installed hardware
KG_PER_KW_K        = 2.5      # PCHE mass per unit UA
EXTRA_COMPRESSOR_T = 1.5      # per compressor beyond the first
BASELINE_MASS_T    = 60.0     # baseline PCS (simple recuperated)
BASELINE_VOLUME_M3 = 120.0
PRESSURE_DROP      = 0.0      # neglected on first pass (brief allows); fraction per exchanger side

# ---------- B. Constraints from the brief ----------
T_INLET_MIN_C      = 32.0     # compressor inlet
P_INLET_MIN_MPA    = 7.7      # compressor inlet
P_MAX_MPA          = 20.0     # maximum cycle pressure (compressor outlet)
T_TURBINE_MAX_C    = 500.0    # turbine inlet is swept at or below this
RECUP_PINCH_MIN_K  = 5.0      # points below this are infeasible
SPLIT_MIN, SPLIT_MAX = 0.0, 0.5

# ---------- C. Interpretation of the brief ----------
RECUP_EFFECTIVENESS = 0.90    # brief's baseline value, held fixed
COOLER_PINCH_K      = 5.0     # CO2-water minimum approach; sets water flow and cooler UA
COOLER_KG_PER_KW_K  = 2.5     # same PCHE rule applied to coolers
COOLANT_P_PA        = None    # cooling-water pressure; None = solver default (6 bar)
# every cooler and intercooler cools the CO2 to the compressor inlet temperature T_in
EXTRA_COMPRESSORS   = {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}   # by layout number
DENSITY_T_PER_M3    = BASELINE_MASS_T / BASELINE_VOLUME_M3   # volume = mass / this
STRICT_INLET_PRESSURE = False # 7.7 MPa limit applied to the main compressor only; under the literal reading layout 6 is excluded
# (economics also writes a second, "strict" ranking with every design whose lowest
#  compressor inlet is below P_INLET_MIN_MPA removed: data/results_econ_strict.csv)
RANK_EXCLUDE_LAYOUTS = [1]    # kept in the results, left out of Pareto / knee / TOPSIS (report ranks 2-6)
P_EXH_MIN_MPA       = 2.0     # refinement bound on layout 6 turbine exhaust pressure

LIFETIME_YEARS      = 10      # N in the lifetime payout
N_TOP               = 5       # size of each top-N list
TOPSIS_WEIGHTS      = {"payout": 0.5, "mass": 0.5}   # payout max, mass min

T_CRIT_C, P_CRIT_MPA = 30.978, 7.377   # CO2 critical point

COOLER_NODES = 50    # cooler profile slices for sweeps (UA within 0.05 % of 100 at both reference points); state export uses 100
SWEEP_WORKERS = 8    # throughput peaked at 8 on this machine

# ---------- D. Calibrated in part A (pasted in by hand) ----------
M0_T      = 39.059   # tonnes: 60 - recuperator mass - cooler mass at the reference point
M0_REF_ID = "L2_Ph200_Pl077_T340_Tt500"   # ID of the best-efficiency feasible layout-2 point
# reference: eta 0.33306362, UA_recup_1 1865.63 kW/K, UA_cooler_1 6510.83 kW/K (50 cooler slices)

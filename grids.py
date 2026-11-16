"""grids.py: sweep ranges. A tuple is (start, stop, step), inclusive; a list is explicit values.
Integer units: pressure 0.1 MPa, T_in 0.1 degC, T_turb 1 degC, split 0.01.
"""

T_TURB = [500, 475, 451]   # degC, 500 * 0.95^k, top three only (compute budget)

GRIDS = {
    "L2_cal": dict(layout=2,
        P_high=(140, 200, 10),    # 14 - 20 MPa, step 1
        P_low =(77, 97, 5),       # 7.7 - 9.7 MPa, step 0.5
        T_in  =(320, 400, 20),    # 32 - 40 degC, step 2
        T_turb=T_TURB),           # 7 * 5 * 5 * 3 = 525 points
    "L1": dict(layout=1,
        P_high=(160, 200, 20), P_low=(77, 87, 10), T_in=(320, 400, 40),
        T_turb=[500]),
    "L3": dict(layout=3,
        P_high=(160, 200, 20), P_low=(77, 82, 5), T_in=(320, 400, 40),
        T_turb=[500], split=(15, 40, 5)),
    "L4": dict(layout=4,
        P_high=(160, 200, 20), P_low=(77, 82, 5), T_in=(320, 400, 40),
        T_turb=[500], P_mid=(100, 140, 20)),
    "L5": dict(layout=5,
        P_high=(180, 200, 20), P_low=(77, 82, 5), T_in=(320, 400, 40),
        T_turb=[500], split=(20, 35, 5), P_mid=(100, 140, 20)),
    "L6": dict(layout=6,
        P_high=(180, 200, 20), P_mid=(77, 87, 5), P_exh=(55, 75, 10),
        T_in=(320, 400, 40), T_turb=[500], split=(20, 40, 10)),
    "L3_fine": dict(layout=3, P_high=[200], P_low=[77], T_in=(320, 340, 10),
        T_turb=[500], split=(30, 40, 1)),
    "L6_fine": dict(layout=6, P_high=[200], P_mid=[77], P_exh=[45, 55], T_in=[320, 360],
        T_turb=[500], split=[35, 45, 50]),
}

# refinement round 1 (core/refine.py)
GRIDS.update({
    'W1_L3': dict(layout=3, P_high=[200], P_low=(77, 85, 2), T_in=(320, 360, 5), split=(30, 48, 1), T_turb=[500]),
    'W1_L6': dict(layout=6, P_high=[200], P_mid=(77, 85, 4), P_exh=(40, 65, 5), T_in=(320, 360, 10), split=(30, 50, 5), T_turb=[500]),
    'W1_L5': dict(layout=5, P_high=[200], P_low=[77, 80], T_in=(320, 340, 10), split=(30, 42, 2), P_mid=(90, 110, 10), T_turb=[500]),
    'W1_L2': dict(layout=2, P_high=[200], P_low=(77, 82, 1), T_in=(320, 360, 5), T_turb=[500]),
    'W1_L4': dict(layout=4, P_high=[200], P_low=(77, 85, 4), T_in=(320, 340, 10), P_mid=(100, 160, 20), T_turb=[500]),
})

# refinement round 2 (core/refine.py)
GRIDS.update({
    'W2_L5a': dict(layout=5, T_turb=[500], P_high=[200], P_low=[77], T_in=[320], P_mid=[80, 90], split=[35, 36, 37]),
    'W2_L5b': dict(layout=5, T_turb=[500], P_high=[200], P_low=[77], T_in=[325, 330, 335], P_mid=[80, 90], split=[42, 44, 46]),
    'W2_L6a': dict(layout=6, T_turb=[500], P_high=[200], T_in=[320], P_mid=[77], P_exh=[53, 55, 57], split=[43, 45, 47]),
    'W2_L6b': dict(layout=6, T_turb=[500], P_high=[200], T_in=[335, 340, 345], P_mid=[79, 81, 83], P_exh=[30, 35, 40], split=[33, 35, 37]),
})

# refinement round 3 (core/refine.py)
GRIDS.update({
    'W3_L5d': dict(layout=5, T_turb=[500], P_high=[200], P_low=[77], T_in=[320], P_mid=[78, 79, 80], split=[36]),
    'W3_L6e': dict(layout=6, T_turb=[500], P_high=[200], T_in=[320], P_mid=[77], P_exh=[52, 53, 54], split=[44, 45, 46]),
    'W3_L6f': dict(layout=6, T_turb=[500], P_high=[200], T_in=[335], P_mid=[78, 79, 80], P_exh=[33, 35, 37], split=[36, 37, 38]),
})

# refinement round 4 (core/refine.py)
GRIDS.update({
    'W4_L6f': dict(layout=6, T_turb=[500], P_high=[200], T_in=[335], P_mid=[79], P_exh=[36, 37, 38], split=[38]),
})

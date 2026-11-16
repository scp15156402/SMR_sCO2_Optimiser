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

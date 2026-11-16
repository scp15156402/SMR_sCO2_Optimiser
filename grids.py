"""grids.py: sweep ranges. A tuple is (start, stop, step), inclusive; a list is explicit values.
Integer units: pressure 0.1 MPa, T_in 0.1 degC, T_turb 1 degC, split 0.01.
"""

T_TURB = [500, 475, 451, 429, 407, 387, 368, 349, 332, 315]   # degC, 500 * 0.95^k

GRIDS = {
    "L2_cal": dict(layout=2,
        P_high=(140, 200, 5),     # 14.0 - 20.0 MPa, step 0.5
        P_low =(77, 97, 5),       # 7.7 - 9.7 MPa, step 0.5
        T_in  =(320, 410, 10),    # 32 - 41 degC, step 1
        T_turb=T_TURB),           # 13 * 5 * 10 * 10 = 6,500 points
}

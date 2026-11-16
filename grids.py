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
}

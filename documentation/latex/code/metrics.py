# --- cycle metrics ----------------------------------------------------
w_t = sum(e["w_total"] for e in extras.values() if e["kind"] == "turbine")
w_c = sum(e["w_total"] for e in extras.values() if e["kind"] == "compressor")
q_in = sum(e["q_total"] for e in extras.values() if e["kind"] == "heater")
q_out = sum(e["q_total"] for e in extras.values() if e["kind"] == "cooler")
w_net = w_t - w_c

# Coolant-pump work, summed over every cooler that was given a circuit.
# It is an auxiliary load rather than cycle work, so it stays out of
# w_net and out of eta_th -- those remain comparable with any textbook
# figure -- and is subtracted separately, which is what a plant sees.
w_pump = sum(e.get("pump_w_total", 0.0) for e in extras.values()
             if e["kind"] == "cooler")

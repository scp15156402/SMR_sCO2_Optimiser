def fixed_outlets(params):
    if "T_out" in params:
        return {"out": {"T": params["T_out"]}}
    return {}

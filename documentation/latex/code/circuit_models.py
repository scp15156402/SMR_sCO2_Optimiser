@dataclass(frozen=True)
class NoPumping:

@dataclass(frozen=True)
class FixedDrop:
    dP: float

@dataclass(frozen=True)
class QuadraticDrop:
    dP_ref: float
    flow_ref: float

def pressure_drop(model, flow: float) -> float:
    if model is None or isinstance(model, NoPumping):
        return 0.0
    if isinstance(model, FixedDrop):
        return model.dP
    if isinstance(model, QuadraticDrop):
        if model.flow_ref <= 0.0:
            raise ValueError("QuadraticDrop.flow_ref must be positive")
        return model.dP_ref * (flow / model.flow_ref) ** 2
    raise TypeError(
        f"circuit must be one of "
        f"{', '.join(m.__name__ for m in CIRCUIT_MODELS)}, "
        f"got {type(model).__name__}")

def pump_work(flow: float, dP: float, rho: float, eta: float) -> float:
    if dP <= 0.0 or flow <= 0.0:
        return 0.0
    return flow * dP / (rho * eta)

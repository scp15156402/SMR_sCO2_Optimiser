@dataclass(frozen=True)
class Relation:
    src: str
    dst: str
    forward: Callable[[float], float]
    backward: Callable[[float], float]

def drop_relation(src: str, dst: str, delta: float) -> Relation:
    from ..physics.pressure_drop import drop, undrop
    return Relation(src, dst, lambda P: drop(P, delta), lambda P: undrop(P, delta))

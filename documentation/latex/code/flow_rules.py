@dataclass(frozen=True)
class Identity:
    pairs: tuple        # ((in_port, out_port), ...)

@dataclass(frozen=True)
class Scale:
    inlet: str
    outlets: tuple      # ((out_port, index, fraction), ...)

@dataclass(frozen=True)
class Sum:
    inlet: str
    outlet: str

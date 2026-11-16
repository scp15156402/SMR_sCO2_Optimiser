@dataclass(frozen=True)
class Stream:
    fluid: str
    P: float            # Pa
    h: float            # J/kg
    flow: float = 1.0   # fraction of total cycle mass flow

    def with_(self, **kw) -> "Stream":
        return replace(self, **kw)

    def describe(self, props) -> dict:
        """Full state, for reporting.  Needs a property backend."""
        p = props(self.fluid)
        return {
            "fluid": self.fluid,
            "P": self.P,
            "h": self.h,
            "T": p.T_ph(self.P, self.h),
            "s": p.s_ph(self.P, self.h),
            "rho": p.rho_ph(self.P, self.h),
            "flow": self.flow,
        }

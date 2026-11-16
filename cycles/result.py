"""What a solved cycle hands back.

This is the only object Stage 2 ever sees.  Everything a study, a cost model
or a plot could need is already in here, so nothing downstream has to reach
back into the solver or re-run it.

Failures are flags, not exceptions.  A sweep of ten thousand points must keep
going when one of them asks for a pinch the exchanger cannot deliver.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Result:
    case: object                      # the Case that produced this
    ok: bool                          # solved and passed every check
    flags: list = field(default_factory=list)

    streams: dict = field(default_factory=dict)   # id -> P,T,h,s,rho,flow
    blocks: dict = field(default_factory=dict)    # id -> that block's extras
    metrics: dict = field(default_factory=dict)   # cycle-level numbers
    checks: dict = field(default_factory=dict)    # closure, pinch, entropy
    schedule: dict = field(default_factory=dict)  # order, tears, iterations
    exergy: dict = field(default_factory=dict)    # component-resolved E_D

    # --- convenience ------------------------------------------------------
    def __getitem__(self, key):
        return self.metrics[key]

    def blocks_of(self, kind: str) -> dict:
        return {k: v for k, v in self.blocks.items() if v.get("kind") == kind}

    def summary(self) -> str:
        m = self.metrics
        head = f"{self.case.name}  [{'ok' if self.ok else 'FLAGGED'}]"
        if not m:
            return head + "\n  (no metrics: solve failed)"
        lines = [
            head,
            f"  eta_th      {m['eta_th']*100:8.3f} %",
            f"  w_net       {m['w_net']/1e3:8.2f} kJ/kg",
            f"  BWR         {m['bwr']:8.4f}",
            f"  q_in        {m['q_in']/1e3:8.2f} kJ/kg",
            f"  mdot        {m['mdot']:8.2f} kg/s",
            f"  W_net       {m['W_net']/1e6:8.3f} MW",
            f"  pinch_min   {m['pinch_min']:8.3f} K",
            f"  T margin    {m['T_crit_margin']:8.3f} K above critical",
        ]
        for f in self.flags:
            lines.append(f"  ! {f}")
        return "\n".join(lines)

    def state_table(self) -> str:
        """Every stream, with its exergy alongside its enthalpy.

        `e_x` is specific flow exergy in kJ/kg: how much work could be got
        out of this stream by bringing it reversibly to the environment.
        It is zero at the dead state and never negative for a stream hotter
        or denser than ambient.
        """
        ex = (self.exergy or {}).get("streams", {})
        head = ("  stream        P [MPa]    T [degC]   h [kJ/kg]  "
                "s [kJ/kgK]   flow")
        rows = [head + ("  e_x [kJ/kg]" if ex else "")]
        for sid in sorted(self.streams):
            s = self.streams[sid]
            row = (f"  {sid:<10} {s['P']/1e6:9.4f} {s['T']-273.15:11.2f} "
                   f"{s['h']/1e3:11.2f} {s['s']/1e3:11.4f} {s['flow']:7.3f}")
            if ex:
                row += f" {ex[sid]['e_x']/1e3:12.2f}"
            rows.append(row)
        return "\n".join(rows)

# --- propagate both ways until nothing changes ------------------------
for _ in range(len(layout.streams()) + 2):
    changed = False
    for a, b, fwd, bwd in edges:
        if a in P and b not in P:
            P[b] = fwd(P[a]); changed = True
        elif b in P and a not in P:
            P[a] = bwd(P[b]); changed = True
    if not changed:
        break

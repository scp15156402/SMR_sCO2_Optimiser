def compressor_inlets(result):
    out = []
    for bid, e in result.blocks.items():
        if e["kind"] != "compressor":
            continue
        node = result.case.layout.node(bid)
        sid = node.inlets["in"]
        st = result.streams[sid if isinstance(sid, str) else sid[0]]
        out.append((bid, st["T"] - 273.15, st["P"] / 1e6))
    return out

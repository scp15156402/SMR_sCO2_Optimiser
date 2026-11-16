def _entropy_balance(node, streams, props):
    out = sum(s.flow * _s(props, s)
              for s in (streams[i] for ids in node.outlets.values()
                        for i in (ids if isinstance(ids, (list, tuple)) else [ids])))
    inn = sum(s.flow * _s(props, s)
              for s in (streams[i] for ids in node.inlets.values()
                        for i in (ids if isinstance(ids, (list, tuple)) else [ids])))
    return out - inn

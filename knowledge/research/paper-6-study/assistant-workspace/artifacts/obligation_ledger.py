"""Authored static conformance engine; no runtime validation or learned rules."""
import copy
import json


def rename_refs(state, mapping):
    """Rename node identities and scoped references, never intent/evidence IDs."""
    s = copy.deepcopy(state)
    for n in s.get('nodes', []):
        n['id'] = mapping.get(n['id'], n['id'])
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('node', 'source', 'target', 'required_agent', 'old', 'new') and isinstance(v, str):
                    x[k] = mapping.get(v, v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(s)
    return s


def evaluate(case, catalog, method='ledger'):
    if method not in ('ledger', 'B0', 'B1'):
        raise ValueError('method must be ledger, B0 or B1')
    s = copy.deepcopy(case)
    blockers, patches, tiers = [], [], []
    def add(kind, node=None, field=None, details='', evidence=None, status='MISSING'):
        blockers.append(dict(kind=kind, node=node, field=field, details=details,
                             evidence=evidence or [], status=status))
    cat = {c['type']: c for c in catalog['components']}
    intent = s.get('intent', {})
    revision = s.get('revision')
    # Only the ledger interprets revisions. Baselines assess the supplied state.
    if method == 'ledger' and revision:
        r = revision
        op, node = r.get('op'), r.get('node')
        ids = {n['id']: n['type'] for n in s['nodes']}
        if not r.get('authorized'):
            add('revision_unknown', node, details='Explicit revision authorization needed', status='UNKNOWN')
        elif op == 'rename_node' and r.get('old') in ids and r.get('new') not in ids:
            s = rename_refs(s, {r['old']: r['new']})
            patches.append(copy.deepcopy(r))
        elif op == 'revoke_model' and node in ids:
            for b in s.get('bindings', []):
                if b.get('node') == node and b.get('field') == 'model':
                    b['state'] = 'revoked'
            patches.append(copy.deepcopy(r))
        elif op == 'remove_node' and intent.get('route') == 'through_agent' and (intent.get('required_agent') == node or ids.get(node) == 'Agent'):
            add('revision_intent_conflict', node, details='Removal conflicts with retained through-Agent requirement', evidence=[intent.get('id'), r], status='CONFLICT')
        elif op == 'route_through_agent' and ids.get(node) == 'Agent' and intent.get('required_agent') == node:
            direct = [e for e in s['edges'] if ids.get(e['source']) == 'ChatInput' and ids.get(e['target']) == 'ChatOutput' and e['output'] == 'message' and e['input'] == 'input_value']
            if len(direct) == 1:
                e = direct[0]
                used = {x['id'] for x in s['edges']}
                def fresh(base):
                    while base in used:
                        base += '_'
                    used.add(base)
                    return base
                s['edges'].remove(e)
                s['edges'].extend([
                    dict(id=fresh(e['id'] + '_in'), source=e['source'], output='message', target=node, input='input_value'),
                    dict(id=fresh(e['id'] + '_out'), source=node, output='response', target=e['target'], input='input_value')])
                patches.append(copy.deepcopy(r))
            else:
                add('revision_unknown', node, details='A unique direct route is needed', status='UNKNOWN')
        else:
            add('revision_unknown', node, details='Revision predicate not implemented or preconditions not established', evidence=[r], status='UNKNOWN')
        if patches:
            s['revision'] = None
    intent = s.get('intent', {})
    nodes = {n['id']: n['type'] for n in s['nodes']}
    for nid in sorted(nodes):
        types = {n['type'] for n in s['nodes'] if n['id'] == nid}
        types.update(a['type'] for a in s.get('node_type_assertions', []) if a['node'] == nid)
        if len(types) > 1:
            add('node_type_conflict', nid, details='Conflicting type assertions', evidence=sorted(types), status='CONFLICT')
        if nodes[nid] not in cat:
            add('catalog_unknown', nid, details='Type outside pinned catalog', status='UNKNOWN')
    valid_edges = []
    for e in s.get('edges', []):
        src, dst = cat.get(nodes.get(e['source']), {}), cat.get(nodes.get(e['target']), {})
        out = next((p for p in src.get('outputs', []) if p['name'] == e['output']), None)
        inp = next((p for p in dst.get('inputs', []) if p['name'] == e['input']), None)
        if not out or not inp:
            add('port_unknown', e['target'], e['input'], 'Node or port declaration unavailable', [e], 'UNKNOWN')
            continue
        declared = out.get('declaredTypes', [])
        ot = set(declared or ([out['returnAnnotation']] if out.get('returnAnnotation') else []))
        it = set(inp.get('types', []))
        tier = 'catalog-declared' if declared else 'return-annotation'
        tiers.append(dict(subject=e['id'], tier=tier, declared_types=declared, return_annotation=out.get('returnAnnotation')))
        if not ot or not it:
            add('port_unknown', e['target'], e['input'], 'Static type predicate lacks type evidence', [e], 'UNKNOWN')
        elif not ot & it:
            add('edge_type_conflict', e['target'], e['input'], 'Source and target static types are disjoint', [e], 'CONFLICT')
        else:
            valid_edges.append(e)
    if method != 'B0':
        for b in s.get('bindings', []):
            if b['node'] not in nodes:
                add('orphan_binding', b['node'], b['field'], 'Binding target absent; cannot transfer evidence', [b])
        for nid, typ in sorted(nodes.items()):
            for f in cat.get(typ, {}).get('inputs', []):
                if not f.get('required'):
                    continue
                bs = [b for b in s.get('bindings', []) if b['node'] == nid and b['field'] == f['name']]
                states = {b.get('state') for b in bs}
                conflict = 'attested' in states and 'revoked' in states
                if conflict:
                    add('model_conflict' if f['name'] == 'model' else 'binding_conflict', nid, f['name'], 'Attested and revoked assertions coexist', bs, 'CONFLICT')
                witnesses = [b for b in bs if b.get('state') == 'attested' and b.get('kind') in f.get('types', []) and b.get('tier') == 'synthetic-assumption']
                wired = any(e['target'] == nid and e['input'] == f['name'] for e in valid_edges)
                if not conflict and not witnesses and not wired:
                    add('required_model' if f['name'] == 'model' else 'required_input', nid, f['name'], 'Required field lacks a valid scoped witness', bs)
                if witnesses and not conflict:
                    tiers.extend(dict(subject=b['id'], node=nid, field=f['name'], tier='synthetic-assumption') for b in witnesses)
    if method == 'ledger':
        for cap in sorted(set(intent.get('capabilities', []))):
            add('unsupported_capability', details='No capability witness in pinned three-type alphabet: ' + cap, evidence=[intent.get('id'), cap], status='UNSUPPORTED')
        routes = set(intent.get('route_assertions', [])) | {intent.get('route', 'any')}
        if 'through_agent' in routes and ('forbid_agent' in routes or 'direct' in routes):
            add('intent_conflict', details='Route simultaneously requires and excludes Agent', evidence=sorted(routes), status='CONFLICT')
        if intent.get('certify_active_ports'):
            add('runtime_certification', details='Active ports cannot be certified from static metadata; revise request or supply separate evidence', evidence=[intent.get('id')], status='UNKNOWN')
        if intent.get('selected_provider'):
            p = intent['selected_provider']
            add('provider_requirements_unknown', p.get('node'), details='Provider-specific requirements unavailable; supply nonsecret requirement metadata', evidence=[p], status='UNKNOWN')
        route = intent.get('route', 'any')
        agents = sorted(n for n, t in nodes.items() if t == 'Agent')
        agent = intent.get('required_agent')
        if route == 'through_agent' and (agent not in agents):
            if agent is None and len(agents) == 1:
                agent = agents[0]
            else:
                add('ambiguous_identity', agent, details='Select an existing Agent identity', evidence=agents, status='UNKNOWN')
        def has(src_type, dst_type, via=None):
            return any(nodes.get(e['source']) == src_type and nodes.get(e['target']) == dst_type and e['input'] == 'input_value' and (via is None or via in (e['source'], e['target'])) for e in valid_edges)
        if route == 'through_agent' and agent in agents:
            if not (has('ChatInput', 'Agent', agent) and has('Agent', 'ChatOutput', agent)):
                add('intent_route', agent, details='Need ChatInput -> specified Agent -> ChatOutput route; authorize explicit rewiring', evidence=[intent.get('id')])
        elif route == 'direct' and not has('ChatInput', 'ChatOutput'):
            add('intent_route', details='Required direct chat route absent', evidence=[intent.get('id')])
        elif route not in ('any', 'direct', 'through_agent'):
            add('intent_predicate_unknown', details='Route predicate not implemented', evidence=[route], status='UNKNOWN')
    # Deduplicate identical witness records, preserving genuinely conflicting evidence.
    def unique(items):
        return [json.loads(x) for x in sorted({json.dumps(x, sort_keys=True) for x in items})]
    blockers = unique(blockers)
    if method == 'ledger':
        action = 'REJECT_SCOPE' if any(b['kind'] == 'unsupported_capability' for b in blockers) else 'ASK' if blockers else 'REVISE' if patches else 'SPEC_GROUNDED'
    else:
        prefix = 'PORTS' if method == 'B0' else 'FIELDS'
        action = prefix + ('_FAIL' if any(b['status'] != 'UNKNOWN' for b in blockers) else '_UNKNOWN' if blockers else '_PASS')
    questions = [dict(kind=b['kind'], node=b['node'], field=b['field'], question=b['details']) for b in blockers] if method == 'ledger' else []
    return dict(action=action, blockers=blockers, questions=questions, patches=patches,
                post_state=s, evidence_tiers=unique(tiers), runtime_unknowns=[
                    'Port activation unverified', 'Provider/resource availability unverified',
                    'Behavior and task usefulness untested'],
                coverage='full authored static DSL' if method == 'ledger' else 'ports only' if method == 'B0' else 'ports and unconditional required fields; no intent or revisions')

"""Inspect existing judgments for measured neighbor pairs, preserving unknowns."""


def check_pairs(measurements, judgments):
    checked = []
    for pair in measurements['pairs']:
        findings = []
        for item in judgments:
            original = next((f for f in item.get('forms', []) if f['form'] == 'original'), None)
            if not original:
                continue
            units = {c['unit'] for c in original.get('counterexamples', [])}
            hit = sorted(units.intersection(pair['units']))
            if hit:
                findings.append({'target': item['id'], 'counterexamples': hit,
                    'other_status': '未確認（反例一覧にないだけでは、成立・前提不成立・未判定を区別できない）'})
        checked.append({**pair, 'findings': findings, 'exploratory': True,
                        'independently_confirmed': False})
    return checked

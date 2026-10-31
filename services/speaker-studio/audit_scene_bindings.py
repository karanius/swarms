"""Independently check saved scene/reference wiring without running inference."""
from pathlib import Path
import hashlib
import json
import wave

ROOT = Path(__file__).resolve().parent


def audit(folder):
    rows = []
    for manifest in folder.glob('*/experiment.json'):
        run = json.loads(manifest.read_text())
        for line in run['scene']['lines']:
            saved = run['lines'].get(line['id'], {})
            if saved.get('state') != 'saved':
                continue
            record = saved['record']
            source = json.loads((folder / saved['source_experiment'] / 'experiment.json').read_text())
            role = source['library_snapshot']['roles'][line['role']]
            expected = {'identity': role['identity'], 'emotion': role['performances'][line['emotion']]} if run['model'] == 'index' else {'performance': role['performances'][line['emotion']]}
            if run['model'] == 'dia' and not record['settings'].get('use_reference', True):
                expected = {}
            bindings = {b['role']: b for b in record['reference_bindings']}
            errors = []
            if set(bindings) != set(expected):
                errors.append('Reference roles differ')
            for kind, ref in expected.items():
                actual = bindings.get(kind, {})
                for key in ('path', 'sha256', 'transcript'):
                    if actual.get(key) != ref[key]:
                        errors.append(kind + ': ' + key + ' differs')
                if hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest() != ref['sha256']:
                    errors.append(kind + ': source bytes changed')
            if record['settings'] != source['settings']:
                errors.append('Settings differ from generating experiment')
            try:
                with wave.open(record['path'], 'rb') as audio:
                    if audio.getnframes() < 1 or audio.getframerate() < 8000:
                        errors.append('Empty or invalid WAV')
            except (wave.Error, OSError) as exc:
                errors.append('WAV cannot be read: ' + str(exc))
            rows.append({'experiment': run['id'], 'line': line['id'], 'library': run['library'], 'model': run['model'], 'errors': errors})
    return {'saved_lines_checked': len(rows), 'failures': [r for r in rows if r['errors']], 'rows': rows, 'scope': 'Saved reference bindings, source bytes, settings and decoded WAV headers; not emotion or speaker similarity.'}


if __name__ == '__main__':
    result = audit(ROOT / '.runtime/scenes')
    destination = ROOT.parents[1] / 'knowledge/research/paper-16-study/scene-binding-audit.json'
    destination.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))
    raise SystemExit(bool(result['failures']))

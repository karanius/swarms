"""Configured native PythonFunction entrypoint; trusted local code, never model-authored code."""
from pathlib import Path
import json
from controller import Tower
D=Path(__file__).resolve().parents[1]
def dispatch(run_id,node_id):
 if not isinstance(run_id,str) or len(run_id)!=32 or any(c not in '0123456789abcdef' for c in run_id):raise ValueError('Invalid run identifier')
 if node_id not in {'intake','discover','retrieve','normalize','compare','form_claims','assess','assemble','review','handoff','impact'}:raise ValueError('Unknown stage')
 root=D/'.runtime'/'tower'
 # No path, URL, source code or model credential accepted at this interface.
 from store import Store
 profile=Store(root).run(run_id)['body']['profile']
 tower=Tower(root,profile);artifacts=tower.step(run_id,node_id)
 if node_id in ('handoff','impact'):tower.finalize_outputs(run_id,'delivery_pending' if node_id=='handoff' else 'revision_requested')
 return {'data':{'stage':node_id,'artifacts':artifacts}}

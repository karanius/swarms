"""Persist and enforce explicit per-node Langfuse permissions."""
from pathlib import Path
import json,threading,os
path=Path(__file__).parent/'pipeline-runtime'/'grants.json'
lock=threading.Lock()
CAPABILITIES={'listObservations','listScores','createScore'}
def get_grant(node_id):
    with lock:
        data=json.loads(path.read_text()) if path.exists() else {}
        return data.get(node_id,{'enabled':False,'tools':[]})
def set_grant(node_id,enabled,tools):
    if not set(tools)<=CAPABILITIES:raise ValueError('Unsupported capability')
    with lock:
        data=json.loads(path.read_text()) if path.exists() else {}
        data[node_id]={'enabled':enabled,'tools':tools}
        path.parent.mkdir(exist_ok=True);temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data));os.replace(temp,path)
    return data[node_id]
def require(node_id,tool):
    grant=get_grant(node_id)
    if not grant['enabled'] or tool not in grant['tools']:raise PermissionError('Langfuse permission is not granted for this node')

"""Project-local workflow snapshots; independent of the browser session."""
import json
import os
import threading
from pathlib import Path
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field

router=APIRouter(prefix='/workflows')
_store=Path(__file__).parent/'langfuse'/'pipeline-runtime'/'saved-workflows.json'
_lock=threading.Lock()
class WorkflowSnapshot(BaseModel):
    id:str=Field(min_length=1,max_length=120)
    name:str=Field(min_length=1,max_length=180)
    pipeline:str
    snapshot:dict

def read():
    return json.loads(_store.read_text()) if _store.exists() else []

@router.get('')
def list_workflows():
    with _lock:return read()

@router.post('')
def save_workflow(workflow:WorkflowSnapshot):
    if workflow.pipeline not in ('images','draft','failure'):raise HTTPException(400,'Unsupported workflow type')
    record=workflow.model_dump()
    with _lock:
        records=read();records=[r for r in records if r['id']!=record['id']]+[record]
        _store.parent.mkdir(parents=True,exist_ok=True)
        temporary=_store.with_suffix('.tmp')
        temporary.write_text(json.dumps(records))
        os.chmod(temporary,0o600)
        os.replace(temporary,_store)
    return record

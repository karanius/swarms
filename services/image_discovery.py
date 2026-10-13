"""Read-only image inventory and a single Swarms reporting agent."""
import os
import stat
import threading
import uuid
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix='/images')
EXTENSIONS = {'.jpg','.jpeg','.png','.gif','.webp','.heic','.heif','.avif','.tif','.tiff','.bmp','.svg','.ico','.dng','.raw','.cr2','.cr3','.nef','.arw','.orf','.rw2','.pef','.raf','.jxl','.psd'}
_jobs = {}
_lock = threading.Lock()

def scan_image_files(roots, progress=None):
    """Inventory image files by recognized extension; never open file contents or follow symlinks."""
    pending = list(roots)
    visited = set()
    images = set()
    formats = Counter()
    folders = Counter()
    inaccessible = []
    symlinks = 0
    examined = 0
    while pending:
        folder = pending.pop()
        try:
            info = os.lstat(folder)
            if stat.S_ISLNK(info.st_mode):
                symlinks += 1
                continue
            identity = (info.st_dev, info.st_ino)
            if identity in visited:
                continue
            if not stat.S_ISDIR(info.st_mode):
                continue
            visited.add(identity)
            with os.scandir(folder) as entries:
                for entry in entries:
                    examined += 1
                    try:
                        if entry.is_symlink():
                            symlinks += 1
                        elif entry.is_dir(follow_symlinks=False):
                            pending.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            suffix = Path(entry.name).suffix.lower()
                            if suffix in EXTENSIONS and entry.path not in images:
                                images.add(entry.path)
                                formats[suffix] += 1
                                folders[str(Path(entry.path).parent)] += 1
                    except OSError as error:
                        inaccessible.append({'path':entry.path,'reason':str(error)})
        except OSError as error:
            inaccessible.append({'path':str(folder),'reason':str(error)})
        if progress and len(visited) % 100 == 0:
            progress({'directories':len(visited),'entries':examined,'imageFiles':len(images)})
    return {'imageFiles':len(images),'directories':len(visited),'entries':examined,'formats':dict(formats.most_common()),'folders':dict(folders.most_common()),'unreadable':inaccessible,'symlinksSkipped':symlinks,'roots':roots,'completedAt':datetime.now(timezone.utc).isoformat(),'definition':'Files with recognized image extensions. Copies count separately; Photos library files are physical files, not a count of Photos assets. Cloud-only items may not be locally downloaded. No contents read.'}

def verify_image_inventory(inventory):
    """Check that independently aggregated folder and format totals equal the file count."""
    return {'consistent':sum(inventory['formats'].values())==sum(inventory['folders'].values())==inventory['imageFiles'],'coverage':'partial' if inventory['unreadable'] else 'requested folders scanned','unreadableFolders':len(inventory['unreadable'])}

class ScanRequest(BaseModel):
    roots:list[str]=Field(min_length=1,max_length=20)
    explain:bool=True

@router.get('/scope')
def scope():
    return {'home':str(Path.home()),'extensions':sorted(EXTENSIONS),'readOnly':True}

@router.post('/run')
def run(request:ScanRequest):
    roots=[]
    for value in request.roots:
        root=Path(value).expanduser().absolute()
        if not root.is_dir():raise HTTPException(400,f'Folder not found: {root}')
        roots.append(str(root))
    job_id=str(uuid.uuid4())
    def update(**values):
        with _lock:_jobs[job_id].update(values)
    with _lock:
        if any(j['phase'] in ('scanning','explaining') for j in _jobs.values()):raise HTTPException(409,'An image inventory is already running.')
        _jobs[job_id]={'id':job_id,'phase':'scanning','progress':{},'inventory':None,'verification':None,'explanation':None,'error':None}
        while len(_jobs)>20:_jobs.pop(next(iter(_jobs)))
    def worker():
        try:
            inventory=scan_image_files(roots,lambda p:update(progress=p))
            verification=verify_image_inventory(inventory)
            update(inventory=inventory,verification=verification,phase='explaining' if request.explain else 'complete')
            if request.explain:
                from swarms import Agent
                # The controller executes deterministic read-only tools. Only this object is an LLM agent.
                agent=Agent(agent_name='Image inventory agent',system_prompt='Explain the supplied inventory. Copy the exact imageFiles count. If unreadableFolders is nonzero, explicitly call the count partial. Do not claim unique photographs or Photos asset counts. Do not invent files.',model_name='openai/mlx-community/Llama-3.2-3B-Instruct-4bit',llm_base_url='http://127.0.0.1:52415/v1',llm_api_key='local-exo',max_loops=1,max_tokens=250,temperature=.1,output_type='final',verbose=False,telemetry=False,retry_attempts=1,llm_args={'timeout':60})
                context={**inventory,'folders':dict(list(inventory['folders'].items())[:15]),'unreadable':inventory['unreadable'][:10],'verification':verification}
                text='How many image files are on my Mac? Explain this read-only inventory and its coverage:\n'+json.dumps(context,indent=2)
                update(agentInput=text)
                answer=agent.run(text)
                update(explanation=str(answer),phase='complete')
        except Exception as error:
            update(phase='error',error=str(error))
    threading.Thread(target=worker,daemon=True).start()
    return {'id':job_id}

@router.get('/jobs/{job_id}')
def job(job_id:str):
    with _lock:
        if job_id not in _jobs:raise HTTPException(404,'Inventory unavailable. Start a new scan.')
        return dict(_jobs[job_id])

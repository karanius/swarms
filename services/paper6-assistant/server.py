"""Authenticated localhost broker for the exclusive Paper6 assistant."""
import json,os,secrets
from pathlib import Path
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from runtime import ResearchRuntime
BASE=Path(__file__).resolve().parent;RUNTIME=BASE/'.runtime';RUNTIME.mkdir(exist_ok=True,mode=0o700)
p=RUNTIME/'token'
if not p.exists():
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:f.write(secrets.token_hex(32))
os.chmod(p,0o600)
TOKEN=p.read_text().strip();assistant=ResearchRuntime();app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
@app.middleware('http')
async def boundary(request:Request,call_next):
 if request.headers.get('authorization')!='Bearer '+TOKEN:return JSONResponse({'error':'Local assistant authorization required'},status_code=403)
 if request.headers.get('sec-fetch-site')=='cross-site':return JSONResponse({'error':'Cross-site requests rejected'},status_code=403)
 if request.headers.get('content-length') and int(request.headers['content-length'])>100000:return JSONResponse({'error':'Request exceeds budget'},status_code=413)
 return await call_next(request)
class Turn(BaseModel):
 text:str=Field(min_length=1,max_length=40000)
 mode:str='interview'
@app.get('/state')
async def state():return assistant.state()
@app.post('/turn')
async def turn(body:Turn):
 try:return await assistant.turn(body.text,body.mode)
 except ValueError as e:raise HTTPException(status_code=409 if assistant.running else 400,detail=str(e)) from e
@app.post('/cancel')
async def cancel():return await assistant.cancel()
@app.get('/artifact')
async def artifact(path:str):
 try:return assistant.ws.read_artifact(path,limit=60000)
 except (ValueError,OSError) as e:raise HTTPException(status_code=400,detail=str(e)) from e

@app.get('/section')
async def section(number:int):
 try:return assistant.ws.section(number)
 except ValueError as e:raise HTTPException(status_code=400,detail=str(e)) from e

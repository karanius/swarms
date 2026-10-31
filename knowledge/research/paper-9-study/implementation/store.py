"""Scoped immutable artifact store, transactional run/event state and review ledger."""
from pathlib import Path
import sqlite3,json,hashlib,time,uuid,os

class Conflict(RuntimeError):pass
class Store:
 def __init__(self,root):
  self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(self.root,0o700)
  self.db=self.root/'state.sqlite3'
  with self.connect() as db:
   db.executescript('''PRAGMA journal_mode=WAL;
   CREATE TABLE IF NOT EXISTS artifacts(id TEXT,revision INTEGER,kind TEXT,hash TEXT,body TEXT,PRIMARY KEY(id,revision));
   CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,revision INTEGER,state TEXT,body TEXT,deadline REAL,cancelled INTEGER DEFAULT 0);
   CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,run_id TEXT,stage TEXT,status TEXT,at REAL,body TEXT);
   CREATE TABLE IF NOT EXISTS deliveries(key TEXT PRIMARY KEY,run_id TEXT,artifact_ref TEXT,recipient TEXT,status TEXT,body TEXT);
   CREATE TABLE IF NOT EXISTS leases(run_id TEXT,stage TEXT,owner TEXT,expires REAL,PRIMARY KEY(run_id,stage));
   CREATE TABLE IF NOT EXISTS approvals(run_id TEXT,artifact_ref TEXT,actor TEXT,decision TEXT,body TEXT,PRIMARY KEY(run_id,artifact_ref,actor));
   ''')
 def connect(self):
  db=sqlite3.connect(self.db,timeout=20);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON');return db
 def put(self,artifact):
  body=json.dumps(artifact,sort_keys=True,separators=(',',':'));digest=hashlib.sha256(body.encode()).hexdigest()
  key=(artifact['artifact_id'],artifact['revision'])
  with self.connect() as db:
   old=db.execute('SELECT hash FROM artifacts WHERE id=? AND revision=?',key).fetchone()
   if old:
    if old['hash']!=digest:raise Conflict('Immutable artifact revision already exists')
   else:db.execute('INSERT INTO artifacts VALUES(?,?,?,?,?)',(*key,artifact['artifact_type'],digest,body))
  return f'{key[0]}@{key[1]}'
 def get(self,ref):
  ident,revision=ref.rsplit('@',1)
  with self.connect() as db:r=db.execute('SELECT hash,body FROM artifacts WHERE id=? AND revision=?',(ident,int(revision))).fetchone()
  if not r:raise KeyError(ref)
  if hashlib.sha256(r['body'].encode()).hexdigest()!=r['hash']:raise Conflict('Stored artifact digest mismatch')
  return json.loads(r['body'])
 def create_run(self,body,seconds):
  if not isinstance(seconds,(int,float)) or not 0<seconds<=3600:raise ValueError('Run deadline outside permitted range')
  ident=uuid.uuid4().hex
  with self.connect() as db:db.execute('INSERT INTO runs(id,revision,state,body,deadline) VALUES(?,1,?,?,?)',(ident,'draft',json.dumps(body),time.time()+seconds))
  return ident
 def run(self,ident):
  with self.connect() as db:r=db.execute('SELECT * FROM runs WHERE id=?',(ident,)).fetchone()
  if not r:raise KeyError(ident)
  d=dict(r);d['body']=json.loads(d['body']);return d
 def update(self,ident,revision,state,body):
  with self.connect() as db:
   cur=db.execute('UPDATE runs SET revision=revision+1,state=?,body=? WHERE id=? AND revision=?',(state,json.dumps(body),ident,revision))
   if cur.rowcount!=1:raise Conflict('Stale run update')
 def check_bound(self,ident):
  r=self.run(ident)
  if r['cancelled']:raise InterruptedError('Run cancelled')
  if time.time()>=r['deadline']:raise TimeoutError('Run time budget exhausted')
  return max(.01,r['deadline']-time.time())
 def cancel(self,ident):
  with self.connect() as db:db.execute('UPDATE runs SET cancelled=1 WHERE id=?',(ident,))
 def event(self,run,stage,status,body,event_id=None):
  ident=event_id or uuid.uuid4().hex;payload=json.dumps(body,sort_keys=True)
  with self.connect() as db:
   existing=db.execute('SELECT * FROM events WHERE id=?',(ident,)).fetchone()
   if existing:
    if (existing['run_id'],existing['stage'],existing['status'],existing['body'])!=(run,stage,status,payload):raise Conflict('Event identity collision')
   else:db.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',(ident,run,stage,status,time.time(),payload))
  return ident
 def events(self,run):
  with self.connect() as db:rows=db.execute('SELECT * FROM events WHERE run_id=? ORDER BY at,id',(run,)).fetchall()
  return [{**dict(r),'body':json.loads(r['body'])} for r in rows]
 def approve(self,run,artifact_ref,actor,decision,body):
  if decision not in ('accepted','rework','rejected'):raise ValueError('Invalid review decision')
  self.get(artifact_ref)
  with self.connect() as db:
   row=db.execute('SELECT decision,body FROM approvals WHERE run_id=? AND artifact_ref=? AND actor=?',(run,artifact_ref,actor)).fetchone()
   encoded=json.dumps(body,sort_keys=True)
   if row and (row['decision'],row['body'])!=(decision,encoded):raise Conflict('Review decisions immutable; create a revision')
   db.execute('INSERT OR IGNORE INTO approvals VALUES(?,?,?,?,?)',(run,artifact_ref,actor,decision,encoded))
 def deliver(self,run,artifact_ref,recipient,actor):
  artifact=self.get(artifact_ref)
  cost_handoff=recipient=='finance-performance' and artifact['artifact_type']=='cost_ledger'
  if recipient!='content-strategy' and not cost_handoff:raise PermissionError('Recipient not authorized')
  if not cost_handoff and actor==artifact['owner_ref']:raise PermissionError('Author cannot approve own dossier')
  with self.connect() as db:
   row=db.execute('SELECT decision FROM approvals WHERE run_id=? AND artifact_ref=? AND actor=?',(run,artifact_ref,actor)).fetchone()
   if not cost_handoff and (not row or row['decision']!='accepted'):raise PermissionError('Exact artifact revision lacks review acceptance')
   key=hashlib.sha256(f'{run}|{artifact_ref}|{recipient}'.encode()).hexdigest()
   db.execute('INSERT OR IGNORE INTO deliveries VALUES(?,?,?,?,?,?)',(key,run,artifact_ref,recipient,'pending',json.dumps({'reviewer':actor})))
   return dict(db.execute('SELECT * FROM deliveries WHERE key=?',(key,)).fetchone())
 def acknowledge(self,key,recipient):
  with self.connect() as db:
   row=db.execute('SELECT recipient FROM deliveries WHERE key=?',(key,)).fetchone()
   if not row or row['recipient']!=recipient:raise PermissionError('Acknowledgment recipient mismatch')
   db.execute('UPDATE deliveries SET status=? WHERE key=?',('acknowledged',key))

 def claim_stage(self,run,stage,owner,seconds):
  with self.connect() as db:
   db.execute('BEGIN IMMEDIATE')
   old=db.execute('SELECT owner,expires FROM leases WHERE run_id=? AND stage=?',(run,stage)).fetchone()
   if old and old['expires']>time.time():raise Conflict('Stage already leased by active worker')
   db.execute('INSERT OR REPLACE INTO leases VALUES(?,?,?,?)',(run,stage,owner,time.time()+seconds))
 def release_stage(self,run,stage,owner):
  with self.connect() as db:db.execute('DELETE FROM leases WHERE run_id=? AND stage=? AND owner=?',(run,stage,owner))

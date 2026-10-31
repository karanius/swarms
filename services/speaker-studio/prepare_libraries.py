"""Import explicit research reference mappings; never infer validated acting quality."""
from pathlib import Path
import array,csv,hashlib,importlib.util,json,math,struct,tarfile,urllib.request,wave,zlib,subprocess
S=Path(__file__).resolve().parents[2]/'knowledge/research/paper-16-study';D=Path.home()/'.local/share/swarms/scene-datasets';D.mkdir(parents=True,exist_ok=True)
FF='/Users/x/.local/share/money/f5-tts/venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fetch(url):
 with urllib.request.urlopen(url,timeout=60) as r:return r.read()
def ref(ident,p,text,source,annotations):
 with wave.open(str(p)) as w:duration=w.getnframes()/w.getframerate();rate=w.getframerate();samples=array.array('h',w.readframes(w.getnframes())) if w.getsampwidth()==2 else []
 return {'id':ident,'path':str(p),'sha256':sha(p),'transcript':text,'source':source,'annotations':annotations,'qc':{'duration_seconds':duration,'sample_rate':rate,'near_full_scale_samples':sum(abs(x)>=32760 for x in samples) if samples else None},'qualification':'Candidate; source annotations retained, acting and transcript unreviewed'}
def crema(actor_ids=None):
 audit=json.loads((S/'crema-d-audit/audit-results.json').read_text());rev=audit['revision'];roles={}
 utterances={'IEO':"It's eleven o'clock.",'TIE':'That is exactly what happened.','IOM':"I'm on my way to the meeting.",'IWW':'I wonder what this is about.','TAI':'The airplane is almost full.','MTI':'Maybe tomorrow it will be cold.','IWL':'I would like a new alarm clock.','ITH':"I think I have a doctor's appointment.",'DFA':"Don't forget a jacket.",'ITS':"I think I've seen this before.",'TSI':'The surface is slick.','WSI':"We'll stop in a couple of minutes."}
 actors=audit['ranked_actors'][:2] if actor_ids is None else [next(a for a in audit['ranked_actors'] if a['actor']==ident) for ident in actor_ids]
 for role,actor in zip(['A','B'],actors):
  performances={};folder=D/'crema'/actor['actor'];folder.mkdir(parents=True,exist_ok=True)
  for emotion,code in [('neutral','N'),('anger','A'),('sadness','S'),('happiness','H')]:
   r=actor['candidate_references'][code][0];name=r['file']+'.wav';p=folder/name;url=f'https://media.githubusercontent.com/media/CheyneyComputerScience/CREMA-D/{rev}/AudioWAV/{name}'
   if not p.exists():p.write_bytes(fetch(url))
   performances[emotion]=ref('crema:'+r['file'],p,utterances[r['sentence']],url,{'intended_emotion':r['intended'],'intended_intensity':r['intended_intensity'],'audio_only_votes':r['counts'],'n':r['n'],'target_share':r['target_share'],'conditional_intensity':r['perceived_intensity_given_emotion'],'selection':'Top source-metadata candidate, not listener-approved'})
  roles[role]={'speaker_id':'crema:'+actor['actor'],'identity':performances['neutral'],'performances':performances}
 return {'id':'crema','name':'CREMA-D · actors 1006 / 1058','state':'ready_for_generation','comparison':'two-role','terms':'ODbL database / DbCL contents. Research comparison; no unrestricted commercial identity-use claim.','roles':roles}
def ravdess(actor_ids=('01','02')):
 url='https://zenodo.org/records/1188976/files/Audio_Speech_Actors_01-24.zip?download=1'
 def read(start,end=None):
  req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end if end is not None else ""}'})
  with urllib.request.urlopen(req,timeout=60) as r:
   if r.status!=206:raise RuntimeError('RAVDESS server did not honour range request')
   return r.read()
 tail=read(-65557);i=tail.rfind(b'PK\x05\x06');e=struct.unpack_from('<4s4H2LH',tail,i);cd=read(e[6],e[6]+e[5]-1);entries={};offset=0
 while offset<len(cd):
  h=struct.unpack_from('<4s6H3L5H2L',cd,offset)
  if h[0]!=b'PK\x01\x02':raise ValueError('Invalid ZIP central directory')
  name=cd[offset+46:offset+46+h[10]].decode();entries[name]=h;offset+=46+h[10]+h[11]+h[12]
 roles={};folder=D/'ravdess';folder.mkdir(exist_ok=True)
 for role,actor in zip(['A','B'],actor_ids):
  performances={}
  for emotion,code in [('neutral','01'),('anger','05'),('sadness','04'),('happiness','03')]:
   name=f'03-01-{code}-'+('01' if emotion=='neutral' else '02')+f'-01-01-{actor}.wav';member=next(n for n in entries if n.endswith('/'+name) or n==name);h=entries[member];p=folder/name
   if not p.exists():
    chunk=read(h[16],min(208468072,h[16]+30+len(member.encode())+1000+h[8]));fn,extra=struct.unpack_from('<HH',chunk,26);body=chunk[30+fn+extra:30+fn+extra+h[8]];raw=zlib.decompress(body,-15) if h[4]==8 else body
    if len(raw)!=h[9] or zlib.crc32(raw)!=h[7]:raise ValueError('ZIP member CRC mismatch')
    p.write_bytes(raw)
   performances[emotion]=ref('ravdess:'+name,p,'Kids are talking by the door.',url+'#'+member,{'emotion_code':code,'intensity_code':'01' if emotion=='neutral' else '02','statement':'01','repetition':'01','actor':actor,'selection':'Fixed first statement/repetition; no claim these are the best takes','zip_crc32':h[7]})
  roles[role]={'speaker_id':'ravdess:'+actor,'identity':performances['neutral'],'performances':performances}
 return {'id':'ravdess','name':'RAVDESS · actors 01 / 02','state':'ready_for_generation','comparison':'two-role','terms':'CC BY-NC-SA 4.0, non-commercial research. Livingstone & Russo (2018), https://zenodo.org/records/1188976. Member CRCs verified; full archive checksum not verified by selective retrieval.','roles':roles}
def emns(esd):
 rows=list(csv.DictReader((D/'emns-metadata.csv').open(),delimiter='|'));folder=D/'emns';folder.mkdir(exist_ok=True);performances={}
 with tarfile.open(D/'emns.tar.xz') as archive:
  entries={Path(m.name).name:m for m in archive.getmembers() if m.isfile()}
  for emotion,label in [('neutral','Neutral'),('anger','Angry'),('sadness','Sad'),('happiness','Happy')]:
   candidates=[r for r in rows if r['emotion']==label and r['status']=='Complete' and len(r['utterance'])>=55];chosen=None
   for r in candidates:
    member=entries.get(Path(r['audio_recording']).name)
    if not member:continue
    source=folder/Path(member.name).name;target=source.with_suffix('.wav')
    if not source.exists():source.write_bytes(archive.extractfile(member).read())
    if not target.exists():subprocess.run([FF,'-v','error','-nostdin','-i',str(source),'-ac','1','-ar','24000','-c:a','pcm_s16le',str(target)],capture_output=True,check=True,timeout=30)
    with wave.open(str(target)) as w:duration=w.getnframes()/w.getframerate()
    if 5<=duration<=12:chosen=(r,target,source);break
   if chosen is None:raise ValueError('No suitable EMNS duration candidate for '+label)
   r,target,source=chosen;performances[emotion]=ref('emns:'+r['id'],target,r['utterance'],'https://www.openslr.org/136/',{'original_row':r,'original_path':str(source),'original_sha256':sha(source),'conversion':'mono 24 kHz PCM; no mastering','level_note':'Source numeric level retained; not equated to any model strength','selection':'First complete source row with >54 characters and 5–12 second audio, not a listening-quality ranking'})
 return {'id':'emns','name':'EMNS · role A swap / fixed ESD role B','state':'ready_for_generation','comparison':'one-role-swap','terms':'OpenSLR lists Apache 2.0. EMNS source speaker 3 replaces A; B remains ESD 0015 with research-only terms. Not a two-actor EMNS dataset.','roles':{'A':{'speaker_id':'emns:3','identity':performances['neutral'],'performances':performances},'B':esd['roles']['B']}}
if __name__=='__main__':
 # Preserve independently prepared libraries if one import fails.
 import sys
 spec=importlib.util.spec_from_file_location('scene',Path(__file__).with_name('scene.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);libraries=m.libraries()
 for key,fn in [('crema',lambda:crema()),('ravdess',lambda:ravdess()),('emns',lambda:emns(libraries['esd']))]:
  try:libraries[key]=fn();print(key,'imported',flush=True)
  except Exception as e:print(key,'FAILED',str(e),flush=True);libraries[key]['reason']=str(e)
  (S/'scene-libraries.json').write_text(json.dumps(libraries,indent=2))

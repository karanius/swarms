"""Download one metadata-selected actor's candidates; retain unqualified status."""
from pathlib import Path
import hashlib,json,urllib.request,wave,array,math
S=Path(__file__).resolve().parent
report=json.loads((S/'audit-results.json').read_text());actor=report['ranked_actors'][0];rev=report['revision'];folder=Path.home()/'.local/share/swarms/crema-d'/rev/actor['actor'];folder.mkdir(parents=True,exist_ok=True)
utterances={'IEO':"It's eleven o'clock.",'TIE':'That is exactly what happened.','IOM':"I'm on my way to the meeting.",'IWW':'I wonder what this is about.','TAI':'The airplane is almost full.','MTI':'Maybe tomorrow it will be cold.','IWL':'I would like a new alarm clock.','ITH':"I think I have a doctor's appointment.",'DFA':"Don't forget a jacket.",'ITS':"I think I've seen this before.",'TSI':'The surface is slick.','WSI':"We'll stop in a couple of minutes."}
clips=[]
for emotion,records in actor['candidate_references'].items():
 for r in records:
  name=r['file']+'.wav';path=folder/name;url=f'https://media.githubusercontent.com/media/CheyneyComputerScience/CREMA-D/{rev}/AudioWAV/{name}'
  if not path.exists():
   raw=urllib.request.urlopen(url,timeout=60).read()
   if not raw.startswith(b'RIFF'):raise ValueError('Not decoded audio; possibly LFS pointer')
   path.write_bytes(raw)
  with wave.open(str(path)) as w:
   sr=w.getframerate();channels=w.getnchannels();width=w.getsampwidth();n=w.getnframes();pcm=w.readframes(n)
  if width!=2:raise ValueError('Unexpected sample width')
  samples=array.array('h',pcm);rms=math.sqrt(sum((x/32768)**2 for x in samples)/len(samples));duration=n/sr
  clips.append({**r,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_url':url,'transcript':{'text':utterances.get(r['sentence']),'status':'official_sentence_code_mapping_not_independently_transcribed'},'audio_qc':{'duration_seconds':duration,'sample_rate':sr,'channels':channels,'sample_width_bytes':width,'rms':rms,'peak':max(abs(x) for x in samples)/32768,'near_full_scale_samples':sum(abs(x)>=32760 for x in samples),'non_silent':rms>1e-6},'qualification':'metadata_candidate; listening and generation-transfer tests pending','engine_fit':{'index':'candidate; audition identity/performance independently','vox':'short-reference candidate; test before adoption','f5':'short-reference candidate; test before adoption','dia':'short reference; documented guidance recommends longer conditioning'}})
profile={'schema_version':1,'dataset':'CREMA-D','actor':actor['actor'],'revision':rev,'state':'candidate_not_approved','selection_policy':report['candidate_policy'],'conditioning_modes':{'index':{'identity':'neutral candidate, not yet selected','emotion':'same actor selected emotional candidate'},'vox':{'performance':'selected candidate'},'f5':{'performance':'selected candidate'},'dia':{'performance':'selected candidate; short-reference limitation'}},'references':clips,'limitations':report['limitations'],'licence_files':['LICENSE.txt'],'identity_anchor':None,'listening_ratings':[],'generation_transfer_results':[]}
(S/'actor-candidate.json').write_text(json.dumps(profile,indent=2));print(json.dumps({'actor':profile['actor'],'clips':len(clips),'duration_range':[min(x['audio_qc']['duration_seconds'] for x in clips),max(x['audio_qc']['duration_seconds'] for x in clips)],'sample_rates':sorted(set(x['audio_qc']['sample_rate'] for x in clips)),'non_silent':all(x['audio_qc']['non_silent'] for x in clips),'clipped_clips':sum(bool(x['audio_qc']['near_full_scale_samples']) for x in clips),'status':profile['state']},indent=2))

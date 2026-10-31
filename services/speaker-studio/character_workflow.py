"""Persistent five-stage character development; listener judgements are never inferred."""
from pathlib import Path
import copy,io,json,shutil,threading,time,uuid,zipfile
import scene
import voice_designer as designer
import performance_bridge as bridge
import sentence_policy
ROOT=Path(__file__).resolve().parent/'.runtime/character-workflow'
PROJECTS=ROOT/'projects';PACKAGES=ROOT/'packages'
PROJECTS.mkdir(parents=True,exist_ok=True);PACKAGES.mkdir(exist_ok=True)
LOCK=threading.RLock()
STYLES={
 'neutral':'Natural, unforced conversational speech. No added emotional emphasis.',
 'reassurance':'Speak tenderly to someone frightened. Gentle warmth, patient pauses and a reassuring falling cadence.',
 'anger':'Controlled anger at being betrayed. Firm consonants, restrained intensity and sharp emphasis; do not shout.',
 'sadness':'Quiet grief. Intimate, subdued energy, hesitant pauses and a sense of loss.',
 'happiness':'Genuine delighted happiness. Warm smiling delivery with lively emphasis.',
 'excitement':'An exciting discovery. Rising energy, animated rhythm and eager anticipation.',
 'curiosity':'Sincerely intrigued. Questioning intonation, attentive pauses and inviting warmth.'}
DEVELOPMENT_TEXT='I need you to stay right here.'
LEGACY_TRIAL_TEXTS=['The door was open when I arrived. I waited outside until you came back.', 'We can talk about the details tomorrow. For now, tell me what you need.']
TRIAL_TEXTS=['The door was open when I arrived.', 'We can talk about the details tomorrow.']
def load(value):return json.loads((PROJECTS/(designer.ident(value)+'.json')).read_text())
def save(p):
 p['updated']=time.time();scene.dump(PROJECTS/(p['id']+'.json'),p)
def snapshot(audition):
 if audition['state']!='saved':raise ValueError('Choose a successfully saved recording')
 path=audition['audio']['path']
 return {'id':'character-audition:'+audition['id'],'source':'Locally designed synthetic character','audition_id':audition['id'],'path':path,'sha256':scene.digest(path),'transcript':audition['request']['text']}
def check_ref(ref):
 if scene.digest(ref['path'])!=ref['sha256']:raise ValueError('A pinned recording changed. Restore the original before continuing.')
def selected(s):return next((c for c in s['candidates'] if c['audition_id']==s['selected']),None)
def evidence(s):
 c=selected(s)
 trials=[v for v in s['trials'] if c and v['candidate_id']==c['audition_id'] and v['state']=='saved']
 # A pair is one immutable trial batch, not two repeated copies of the same line.
 groups={}
 for t in trials:groups.setdefault(t['batch_id'],[]).append(t)
 pair=next((g for g in reversed(list(groups.values())) if len(g)==2 and {t['text'] for t in g}==set(g[0].get('expected_texts',LEGACY_TRIAL_TEXTS if {t['text'] for t in g}==set(LEGACY_TRIAL_TEXTS) else TRIAL_TEXTS))),[])
 binding={'candidate_id':s['selected'],'trial_ids':sorted(t['audition_id'] for t in pair)}
 review=next((r for r in reversed(s['reviews']) if r['binding']==binding),None)
 single_sentence=bool(c and sentence_policy.inspect(c.get('text') or designer.get(c['audition_id'])['request']['text'])['valid'] and all(sentence_policy.inspect(t['text'])['valid'] for t in pair))
 qualified=bool(single_sentence and c and len(pair)==2 and review and all(review[k] for k in ['words','identity','delivery']))
 return {'candidate':c,'trials':pair,'binding':binding,'review':review,'qualified':qualified,'single_sentence':single_sentence}
def public(p):
 p=copy.deepcopy(p);problems=[]
 if not p['identity']:problems.append('Fix one voice identity in stage 2.')
 for style,s in p['styles'].items():
  e=evidence(s);s['evidence']=e
  if not e['candidate']:problems.append(style+': generate and select a performance.')
  elif not sentence_policy.inspect(e['candidate'].get('text') or designer.get(e['candidate']['audition_id'])['request']['text'])['valid']:problems.append(style+': regenerate the earlier multi-sentence performance as one sentence.')
  elif not e['trials']:problems.append(style+': test the performance on two new lines.')
  elif not e['qualified']:problems.append(style+': listen and record words, identity and delivery checks.')
 p['blockers']=problems;p['ready_to_publish']=not problems;p['busy']=scene.QUEUE.locked()
 from guided_loop import view
 p['guided']={style:view(p,style) for style in p['styles']}
 return p
def state():
 return {'projects':sorted([{'id':p['id'],'name':p['name'],'stage':p['stage'],'identity_locked':bool(p['identity']),'package_id':p['package_id'],'updated':p['updated']} for f in PROJECTS.glob('*.json') for p in [json.loads(f.read_text())]],key=lambda p:p['updated'],reverse=True),'styles':STYLES,'emotion_references':list(bridge.catalog().values()),'reference_defaults':{k:bridge.default_reference(k) for k in STYLES},'busy':scene.QUEUE.locked()}
def create(q):
 name=str(q.get('name','')).strip()
 if not 1<=len(name)<=100:raise ValueError('Name your character, up to 100 characters')
 p={'id':str(uuid.uuid4()),'name':name,'created':time.time(),'stage':1,'design_audition_id':None,'identity':None,'styles':{k:{'direction':v,'selected':None,'candidates':[],'trials':[],'reviews':[]} for k,v in STYLES.items()},'jobs':[],'package_id':None,'schema_version':1}
 save(p);return public(p)
def editable(p):
 if p['package_id']:raise ValueError('This character version is published. Start a revision to make changes.')
 if any(j['state'] in ['queued','running'] for j in p['jobs']):raise ValueError('Wait for the current character generation to finish')
def mutate(q):
 with LOCK:
  p=load(q['id']);action=q['action']
  if action=='stage':
   stage=int(q['stage'])
   if stage not in range(1,6):raise ValueError('Unknown stage')
   p['stage']=stage;save(p);return public(p)
  if action=='revision':
   new=create({'name':str(q.get('name') or p['name']+' · revision')[:100]});n=load(new['id']);n['parent_project_id']=p['id'];n['version']=p.get('version',1)+1;n['design_audition_id']=p['design_audition_id'];n['identity']=copy.deepcopy(p['identity']);n['stage']=3 if n['identity'] else 1;save(n);return public(n)
  editable(p)
  if action=='choose_design':
   if p['identity']:raise ValueError('The identity is fixed. Create a revision or a new character to choose another voice.')
   r=designer.get(q['audition_id'])
   if r['request']['mode']!='voice_design':raise ValueError('Choose a reference-free voice design audition')
   snapshot(r);p['design_audition_id']=r['id'];p['stage']=2
  elif action=='fix_identity':
   if p['identity']:raise ValueError('This voice identity is already fixed')
   if not p['design_audition_id']:raise ValueError('Choose an audition in stage 1 first')
   r=designer.get(p['design_audition_id']);ref=snapshot(r)
   profile=designer.save_profile({'audition_id':r['id'],'name':p['name']+' · fixed identity'})
   p['identity']={'reference':ref,'profile_id':profile['id'],'engine':'voxcpm2','fixed_at':time.time(),'design_request':r['request']};p['stage']=3
  elif action=='select':
   s=p['styles'][q['style']];candidate=next((c for c in s['candidates'] if c['audition_id']==q['audition_id']),None)
   if not candidate:raise ValueError('Select a recording belonging to this performance')
   check_ref(candidate['reference']);s['selected']=candidate['audition_id']
  elif action=='feedback':
   s=p['styles'][q['style']];e=evidence(s)
   if q.get('candidate_id')!=s['selected']:raise ValueError('The selected performance changed')
   note=str(q.get('note','')).strip()
   if not 1<=len(note)<=2000:raise ValueError('Describe the listening result')
   s.setdefault('feedback',[]).append({'candidate_id':s['selected'],'trial_ids':e['binding']['trial_ids'],'note':note,'at':time.time(),'source':'listener_feedback'})
  elif action=='review':
   s=p['styles'][q['style']];e=evidence(s)
   if not e['single_sentence']:raise ValueError('Regenerate this performance and its checks using one sentence per take before qualifying it')
   if len(e['trials'])!=2:raise ValueError('Generate two new-line checks before reviewing')
   if q.get('binding')!=e['binding']:raise ValueError('The selected performance or checks changed. Reload before reviewing.')
   if any(type(q.get(k)) is not bool for k in ['words','identity','delivery']):raise ValueError('Explicit listener checks are required')
   note=str(q.get('note','')).strip()[:2000]
   automatic_flags=any(not designer.get(t['audition_id']).get('word_check',{}).get('exact_words') for t in e['trials']+[e['candidate']])
   if automatic_flags and q['words'] and not note:raise ValueError('A word check was flagged. Explain what you heard before overriding it.')
   s['reviews'].append({'binding':e['binding'],'words':q['words'],'identity':q['identity'],'delivery':q['delivery'],'note':note,'at':time.time(),'source':'explicit_listener_review'})
  else:raise ValueError('Unknown character action')
  save(p);return public(p)
def generate(q):
 with LOCK:
  p=load(q['id']);editable(p)
  if not p['identity']:raise ValueError('Fix the voice identity in stage 2 first')
  check_ref(p['identity']['reference'])
  kind=q.get('kind','performance')
  if kind not in ['performance','validation']:raise ValueError('Unknown generation step')
  keys=q.get('styles',list(p['styles']))
  if not isinstance(keys,list) or not keys or len(keys)!=len(set(keys)) or set(keys)-set(p['styles']):raise ValueError('Choose valid performance styles')
  settings={k:q.get(k,v) for k,v in [('seed',23),('steps',20),('guidance',2.5)]}
  plans=[]
  for key in keys:
   s=p['styles'][key]
   if kind=='performance':
    direction=str(q.get('directions',{}).get(key,s['direction'])).strip()
    if not 5<=len(direction)<=1500:raise ValueError('Give each performance a clear direction')
    reference_id=q.get('references',{}).get(key,s.get('reference_id',bridge.default_reference(key)))
    strength=q.get('strengths',{}).get(key,s.get('strength',1.0))
    text=sentence_policy.require(q.get('text',DEVELOPMENT_TEXT))
    request=bridge.request(p['identity']['reference'],p['name'],text,key,reference_id,strength,settings['seed'],q.get('duration_scale',1.0))
    plans.append({'style':key,'request':request,'direction':direction,'reference_id':reference_id,'strength':float(strength)})
   else:
    c=selected(s)
    if not c:raise ValueError('Select a '+key+' performance before testing it')
    sentence_policy.require(c['reference']['transcript'])
    check_ref(c['reference'])
    for text in TRIAL_TEXTS:
     request=designer.validate({'text':text,**settings},reference_profile={'name':p['name']+' · '+key,'reference':c['reference']})
     plans.append({'style':key,'request':request,'candidate_id':c['audition_id'],'expected_texts':TRIAL_TEXTS})
  return launch(p,kind,plans)
def launch(p,kind,plans):
 check_ref(p['identity']['reference'])
 inventory={m['id']:m for m in scene.B.inventory()}
 engines={'index' if plan['request'].get('mode')=='reference_performance' else 'vox' for plan in plans}
 if any(not inventory.get(engine,{}).get('ready') for engine in engines):raise ValueError('A required local generation engine is unavailable')
 if not scene.QUEUE.acquire(False):raise ValueError('Another generation is running. Wait until it finishes.')
 job={'id':str(uuid.uuid4()),'kind':kind,'state':'queued','created':time.time(),'total':len(plans),'done':0,'results':[]}
 try:p['jobs'].append(job);save(p)
 except Exception:scene.QUEUE.release();raise
 threading.Thread(target=run,args=(p['id'],job['id'],plans),daemon=True).start();return public(p)
def run(value,job_id,plans):
 new_candidate=None
 try:
  for plan in plans:
   with LOCK:
    p=load(value);j=next(j for j in p['jobs'] if j['id']==job_id);j['state']='running';j['current_style']=plan['style'];save(p)
   if plan.get('bind_to_previous') and not new_candidate:raise ValueError('The new character take failed; no misleading control was attached.')
   r=designer.create_record(plan['request'])
   if plan['request'].get('mode')=='reference_performance':bridge.run(r,release_queue=False)
   else:designer.run(r,release_queue=False)
   with LOCK:
    p=load(value);j=next(j for j in p['jobs'] if j['id']==job_id);s=p['styles'][plan['style']]
    result={'audition_id':r['id'],'state':r['state'],'engine':r.get('engine'),'style':plan['style'],'batch_id':job_id,'text':r['request']['text'],'sentence_policy':sentence_policy.VERSION,'error':r.get('error')}
    if r['state']=='saved':result['reference']=snapshot(r)
    purpose=plan.get('purpose',j['kind'])
    if purpose=='performance':
     if r['state']=='saved':
      c={**result,'reference':snapshot(r),'identity_sha256':p['identity']['reference']['sha256'],'direction':plan['direction']};s['candidates'].append(c);s['selected']=r['id'];new_candidate=r['id'];s['direction']=plan['direction']
      if plan.get('reference_id'):s['reference_id']=plan['reference_id'];s['strength']=plan['strength'];c['method']='independent_identity_and_acted_emotion';c['emotion_reference']=r['request']['emotion_reference'];c['strength']=plan['strength'];c['emotion_mode']=r['request'].get('emotion_mode','audio')
    elif purpose=='control':
     s.setdefault('loop',{}).setdefault('controls',[]).append({**result,'candidate_id':new_candidate if plan.get('bind_to_previous') else plan['candidate_id']})
    else:s['trials'].append({**result,'candidate_id':plan['candidate_id'],'expected_texts':plan.get('expected_texts',TRIAL_TEXTS)})
    j['results'].append(result);j['done']+=1;save(p)
  with LOCK:
   p=load(value);j=next(j for j in p['jobs'] if j['id']==job_id);j['state']='finished' if all(r['state']=='saved' for r in j['results']) else 'finished_with_failures';save(p)
 except Exception as exc:
  with LOCK:
   p=load(value);j=next(j for j in p['jobs'] if j['id']==job_id);j['state']='failed';j['error']=str(exc);save(p)
 finally:scene.QUEUE.release()
def package(q):
 with LOCK:
  p=load(q['id']);editable(p)
  if not public(p)['ready_to_publish']:raise ValueError('Complete the performance and listening checks in stage 4 before publishing')
  refs=[p['identity']['reference']]
  for s in p['styles'].values():
   e=evidence(s);refs.append(e['candidate']['reference']);refs.extend(t['reference'] for t in e['trials'])
  for s in p['styles'].values():
   guide=designer.get(evidence(s)['candidate']['audition_id'])['request'].get('emotion_reference')
   if guide:refs.append(guide)
  for ref in refs:check_ref(ref)
  package_id=str(uuid.uuid4());folder=PACKAGES/package_id;folder.mkdir()
  try:
   manifest={'id':package_id,'name':p['name'],'version':p.get('version',1),'project_id':p['id'],'parent_project_id':p.get('parent_project_id'),'created':time.time(),'engine':'vox','qualified_engines':['vox'],'status':'listener_qualified','identity':copy.deepcopy(p['identity']),'performances':{},'qualification_scope':'One listener, two held-out lines per selected style. No general reliability or identity guarantee.','provenance':designer.get(p['identity']['reference']['audition_id']).get('model_provenance')}
   def copy_ref(ref):
    r=copy.deepcopy(ref);r.setdefault('id','character-audition:'+r['audition_id']);r.setdefault('source','Locally designed synthetic character');name=r['audition_id']+'.wav';shutil.copyfile(r['path'],folder/name);r['path']=str(folder/name);r['archive_path']=name;return r
   manifest['identity']['reference']=copy_ref(p['identity']['reference'])
   for key,s in p['styles'].items():
    e=evidence(s);manifest['performances'][key]={'reference':copy_ref(e['candidate']['reference']),'direction':e['candidate']['direction'],'word_check':designer.get(e['candidate']['audition_id']).get('word_check'),'model_provenance':designer.get(e['candidate']['audition_id']).get('model_provenance'),'recipe':designer.get(e['candidate']['audition_id'])['request'],'trials':[{'reference':copy_ref(t['reference']),'word_check':designer.get(t['audition_id']).get('word_check'),'recipe':designer.get(t['audition_id'])['request']} for t in e['trials']],'review':e['review']}
    guide=designer.get(e['candidate']['audition_id'])['request'].get('emotion_reference')
    if guide:
     name='emotion-'+key+'.wav';shutil.copyfile(guide['path'],folder/name);manifest['performances'][key]['emotion_reference']={**guide,'path':str(folder/name),'archive_path':name}
   manifest['guided_history']={key:copy.deepcopy(s.get('loop',{}).get('events',[])) for key,s in p['styles'].items()}
   scene.dump(folder/'manifest.json',manifest)
   p['package_id']=package_id;p['stage']=5;save(p)
  except Exception:shutil.rmtree(folder);raise
  return public(p)
def export(value):
 p=load(value);buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
  if p['package_id']:
   folder=PACKAGES/designer.ident(p['package_id'])
   for f in folder.iterdir():z.write(f,f.name)
  else:
   z.writestr('draft-project.json',json.dumps(public(p),indent=2));z.writestr('STATUS.txt','DRAFT. Not listener-qualified or available for casting.\n')
   ids=set()
   if p['identity']:ids.add(p['identity']['reference']['audition_id'])
   for s in p['styles'].values():ids.update(c['audition_id'] for c in s['candidates']);ids.update(t['audition_id'] for t in s['trials'] if t['state']=='saved')
   for s in p['styles'].values():ids.update(t['audition_id'] for t in s.get('loop',{}).get('controls',[]) if t['state']=='saved')
   guides={}
   for ident in ids:
    r=designer.get(ident);z.write(r['audio']['path'],ident+'.wav');z.writestr(ident+'.json',json.dumps(r,indent=2))
    guide=r['request'].get('emotion_reference')
    if guide:guides[guide['id']]=guide
   for guide in guides.values():z.write(guide['path'],'emotion-'+guide['sha256']+'.wav')
   if guides:z.writestr('emotion-references.json',json.dumps([{**g,'archive_path':'emotion-'+g['sha256']+'.wav'} for g in guides.values()],indent=2))
 return buf.getvalue()
def casting_voices():
 voices={}
 for f in PACKAGES.glob('*/manifest.json'):
  m=json.loads(f.read_text());key='character:'+m['id'];refs={k:v['reference'] for k,v in m['performances'].items()}
  voices[key]={'speaker_id':key,'display_name':m['name']+' · v'+str(m['version'])+' · qualified character','identity':m['identity']['reference'],'performances':refs,'qualified_engines':['vox'],'source':'Character wizard · listener-qualified','package_id':m['id'],'performance_guides':{k:v['emotion_reference'] for k,v in m['performances'].items() if v.get('emotion_reference')},'source_terms':list({v['emotion_reference']['terms'] for v in m['performances'].values() if v.get('emotion_reference',{}).get('terms')})}
 return voices
# A process restart cannot leave a phantom running job that blocks edits forever.
def recover():
 with LOCK:
  for f in PROJECTS.glob('*.json'):
   p=json.loads(f.read_text());changed=False
   for j in p['jobs']:
    if j['state'] in ['queued','running']:j['state']='interrupted';j['error']='The service stopped. Completed recordings are preserved; retry the unfinished work.';changed=True
   if changed:save(p)

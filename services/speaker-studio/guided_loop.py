"""Deterministic, bounded experiments driven by explicitly bound listening feedback."""
import copy,time,uuid
import character_workflow as w
import performance_bridge as bridge
POLICY='guided-qualify-v1'
ISSUES={'emotion_character','emotion_both','identity','words','naturalness','uncertain'}
def recording(value):return w.designer.get(value)
def control_for(s,c):
 return next((r for r in reversed(s.get('loop',{}).get('controls',[])) if r['candidate_id']==c['audition_id'] and r['state']=='saved'),None)
def plan_for(p,style,issue,phase):
 s=p['styles'][style];c=w.selected(s);q=recording(c['audition_id'])['request'];events=s.get('loop',{}).get('events',[])
 attempts=[e for e in events if e.get('action')=='try' and e.get('issue')==issue]
 if issue=='uncertain':return {'kind':'relisten','reason':'Replay the same comparison; no generation settings change.'}
 if phase=='validation' and issue in ['emotion_character','emotion_both']:
  return {'kind':'stop','reason':'The emotion did not survive the new-word test. Return to Develop performances and choose another acted example; this version stays unqualified. Direct generation with another engine needs a separate casting qualification.'}
 if issue=='emotion_character' and style in ['happiness','anger','sadness'] and q.get('emotion_mode','audio')=='audio' and not any(e.get('rule')=='native_vector' for e in attempts):
  return {'kind':'performance','rule':'native_vector','mode':'vector','reason':'Only the character lacks emotion; test the model’s native emotion control while keeping the character identity, sentence and seed fixed.'}
 if issue in ['emotion_character','emotion_both']:
  used={recording(cand['audition_id'])['request'].get('emotion_reference',{}).get('id') for cand in s['candidates']}
  choices=[r for r in bridge.catalog().values() if r['emotion']==style and r['id'] not in used and r.get('library')=='crema']
  choices.sort(key=lambda r:(-r.get('annotations',{}).get('target_share',0),r.get('qc',{}).get('near_full_scale_samples',0),r['id']))
  if choices and len([e for e in attempts if e.get('rule')=='different_guide'])<2:return {'kind':'performance','rule':'different_guide','reference_id':choices[0]['id'],'mode':'audio','reason':'Test a different acted example to see whether the current guide is transferring poorly; keep the character identity and target sentence fixed.'}
 if issue=='identity' and float(q.get('strength',1))>.6 and len(attempts)<2:
  return {'kind':'performance','rule':'reduce_strength','strength':round(max(.6,float(q.get('strength',1))-.2),2),'reason':'Reduce emotion conditioning slightly to test whether the character’s identity returns; then listen for any loss of expression.'}
 if issue in ['words','naturalness'] and len(attempts)<2:
  return {'kind':'performance','rule':'new_seed','seed':(int(q['seed'])+1)%2147483648,'reason':'Try one different sampling seed with the same voice, emotion and sentence; check whether the wording or delivery becomes cleaner.'}
 return {'kind':'stop','reason':'These supported adjustments have not established an improvement. Keep the evidence and review another voice or engine; no further automatic tweak is justified.'}
def has_guide(value):
 try:return bool(recording(value)['request'].get('emotion_reference'))
 except (ValueError,FileNotFoundError):return False
def word_flag(value):
 try:return not recording(value).get('word_check',{}).get('exact_words')
 except (ValueError,FileNotFoundError):return True
def view(p,style):
 s=p['styles'][style];e=w.evidence(s);c=e['candidate'];loop=s.get('loop',{});control=control_for(s,c) if c else None
 binding={'candidate_id':s['selected'],'control_id':control['audition_id'] if control else None,'trial_ids':e['binding']['trial_ids']}
 kept=bool(c and any(v.get('action')=='keep_performance' and v['binding']['candidate_id']==c['audition_id'] for v in loop.get('events',[])))
 if not c or not w.sentence_policy.inspect(c.get('text') or recording(c['audition_id'])['request']['text'])['valid']:phase='needs_performance'
 elif not control and not has_guide(c['audition_id']):phase='needs_performance'
 elif e['qualified']:phase='qualified'
 elif kept:phase='validation' if len(e['trials'])==2 else 'needs_validation'
 else:phase='comparison' if control else 'needs_control'
 latest=next((v for v in reversed(loop.get('events',[])) if v.get('action')=='improve' and v['binding']==binding and v.get('phase')==phase),None)
 tried=bool(latest and any(v.get('action')=='try' and v.get('feedback_id')==latest['id'] for v in loop.get('events',[])))
 recommendation=plan_for(p,style,latest['issue'],phase) if latest and not tried else None
 return {'phase':phase,'binding':binding,'control':control,'candidate':c,'trials':e['trials'],'recommendation':recommendation,'feedback':latest,'kept':kept,'policy':POLICY,'history':loop.get('events',[]),'word_flags':[r['audition_id'] for r in ([c]+e['trials'] if c else []) if word_flag(r['audition_id'])]}
def make_control(candidate):
 q=copy.deepcopy(recording(candidate['audition_id'])['request']);guide=q.get('emotion_reference')
 if not guide:raise ValueError('Create an acted-reference performance before preparing the controlled comparison')
 q['profile']={'name':'Actor control — diagnostic only','reference':copy.deepcopy(guide)};q['diagnostic_control']=True;q.pop('emotion_vector',None);q['emotion_mode']='audio'
 return q
def performance_plan(p,style,recommendation):
 s=p['styles'][style];c=w.selected(s);old=recording(c['audition_id'])['request'];reference_id=recommendation.get('reference_id',old['emotion_reference']['id'])
 if old['emotion_reference'].get('audition_id')==p['identity']['reference']['audition_id'] and 'reference_id' not in recommendation:reference_id='identity'
 strength=recommendation.get('strength',old.get('strength',1));q=bridge.request(p['identity']['reference'],p['name'],old['text'],style,reference_id,strength,recommendation.get('seed',old['seed']),old.get('duration_scale',1))
 mode=recommendation.get('mode',old.get('emotion_mode','audio'));q['emotion_mode']=mode
 if mode=='vector':
  names=['happiness','anger','sadness','fear','disgust','melancholy','surprise','calm']
  if style not in names:raise ValueError('This style has no documented native emotion vector; choose an acted-reference experiment instead')
  q['emotion_vector']=[int(k==style) for k in names]
 plan={'style':style,'purpose':'performance','request':q,'direction':s['direction'],'reference_id':reference_id,'strength':strength}
 control=copy.deepcopy(q);control['profile']={'name':'Actor control — diagnostic only','reference':copy.deepcopy(q['emotion_reference'])};control['diagnostic_control']=True;control.pop('emotion_vector',None);control['emotion_mode']='audio'
 return [plan,{'style':style,'purpose':'control','request':control,'bind_to_previous':True}]
def validation_plans(p,style):
 s=p['styles'][style];c=w.selected(s);source=recording(c['audition_id'])['request'];plans=[]
 for text in w.TRIAL_TEXTS:
  q=w.designer.validate({'text':text,'seed':source['seed'],'steps':20,'guidance':2.5},reference_profile={'name':p['name']+' · '+style,'reference':c['reference']})
  plans.append({'style':style,'purpose':'validation','request':q,'candidate_id':c['audition_id'],'expected_texts':w.TRIAL_TEXTS})
 return plans
def command(q):
 with w.LOCK:
  p=w.load(q['id']);w.editable(p);style=q['style'];s=p['styles'][style];v=view(p,style);action=q['action']
  if q.get('binding')!=v['binding']:raise ValueError('The comparison changed. Listen to the current version before deciding.')
  loop=s.setdefault('loop',{});events=loop.setdefault('events',[])
  event={'id':str(uuid.uuid4()),'at':time.time(),'action':action,'binding':v['binding'],'phase':v['phase'],'policy':POLICY}
  if action=='prepare':
   if v['phase']!='needs_control':raise ValueError('This comparison is already prepared, or needs a new one-sentence performance first')
   plans=[{'style':style,'purpose':'control','request':make_control(v['candidate']),'candidate_id':s['selected']}]
  elif action=='resume':
   if v['phase']!='needs_validation':raise ValueError('There are no missing new-sentence checks to resume')
   plans=validation_plans(p,style)
  elif action=='improve':
   if v['phase'] not in ['comparison','validation']:raise ValueError('Prepare and listen to the comparison first')
   issue=q.get('issue')
   if issue not in ISSUES:raise ValueError('Choose what needs improvement')
   event['issue']=issue;events.append(event);w.save(p);return w.public(p)
  elif action=='try':
   r=v['recommendation']
   if not r or r['kind'] in ['stop','relisten']:raise ValueError('There is no supported generation step for this feedback')
   event.update(issue=v['feedback']['issue'],feedback_id=v['feedback']['id'],rule=r.get('rule',r['kind']),reason=r['reason'])
   plans=performance_plan(p,style,r)
  elif action=='keep':
   if q.get('confirm_words_voice_emotion') is not True:raise ValueError('Keeping requires explicit confirmation of words, voice and emotion')
   if v['phase']=='comparison':
    event['action']='keep_performance';events.append(event)
    if len(v['trials'])==2:w.save(p);return w.public(p)
    plans=validation_plans(p,style)
   elif v['phase']=='validation':
    if v['word_flags'] and not str(q.get('note','')).strip():raise ValueError('An automatic word check was flagged. Add what you heard before keeping this version.')
    # All criteria are explicitly confirmed by the Keep action after its explanation in the UI.
    w.mutate({'id':p['id'],'action':'review','style':style,'binding':w.evidence(s)['binding'],'words':True,'identity':True,'delivery':True,'note':str(q.get('note','')).strip() or 'Listener explicitly kept both new-sentence tests in the guided flow.'})
    p=w.load(p['id']);p['styles'][style].setdefault('loop',{}).setdefault('events',[]).append(event);w.save(p);return w.public(p)
   else:raise ValueError('Finish the comparison and its new-sentence checks before keeping this version')
  else:raise ValueError('Unknown guided action')
  if action!='keep':events.append(event)
  # launch saves the event and plans together only after a queue slot is available.
  return w.launch(p,'guided',plans)

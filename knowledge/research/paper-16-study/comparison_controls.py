"""Native Jupyter take library: delivery rows, model columns, immutable versions."""
from pathlib import Path
import fcntl,html,importlib.util,json,shutil
import ipywidgets as w
from IPython.display import Audio,display
S=Path(__file__).resolve().parent;ROOT=S.parents[2]
spec=importlib.util.spec_from_file_location('paper16_take_backends',S/'take_backends.py')
backends=importlib.util.module_from_spec(spec);spec.loader.exec_module(backends)
analysis_spec=importlib.util.spec_from_file_location('paper16_audio_analysis',S/'audio_analysis.py')
analysis=importlib.util.module_from_spec(analysis_spec);analysis_spec.loader.exec_module(analysis)
ref_spec=importlib.util.spec_from_file_location('paper16_take_references',S/'take_references.py')
reference_module=importlib.util.module_from_spec(ref_spec);ref_spec.loader.exec_module(reference_module)
LIBRARY=S/'take-library.json'
MODELS={m['id']:m for m in backends.inventory()}
EMOTIONS=['neutral','anger','happiness','sadness','surprise']
SPEAKERS=[(f'Reference {i:04d}',f'{i:04d}') for i in range(11,21)]
def atomic_json(path,value):
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2));temp.replace(path)
def library():
 if LIBRARY.exists():return json.loads(LIBRARY.read_text())
 baseline=json.loads((ROOT/'knowledge/research/paper-15-study/reference-guidance-analysis.json').read_text())
 native=json.loads((S/'runs/indextts-20261030-213743-26ac87ee/result.json').read_text())
 records=[]
 for i,take in enumerate(native['takes']):
  ident='initial-index-'+str(i)
  records.append({**take,'id':ident,'root_id':ident,'model':'index','speaker':'0012','text':native['request']['text'],'settings':{'strength':take['strength'],'seed':7},'created':0,'assessment':'Unrated','source':'First IndexTTS trial'})
 for i,take in enumerate(baseline['conditions']):
  ident='initial-vox-'+str(i);emotion='anger' if take['condition']=='angry-reference' else 'neutral'
  export=ROOT/'knowledge/research/notebooks/paper-16-audio'/(ident+'.wav');shutil.copy2(take['raw_path'],export)
  records.append({'url':'/research-jupyter/files/paper-16-audio/'+export.name,'id':ident,'root_id':ident,'model':'vox','speaker':'0012','text':take['request']['text'],'emotion':emotion,'settings':{'seed':7,'steps':10,'guidance':2.,'direction':''},'created':0,'assessment':'Paper 15 user feedback; not a universal validation','path':take['raw_path'],'listening_path':take['matched_path'],'sha256':take['raw_sha256'],'source':'Saved Paper 15 baseline','duration_seconds':take['duration_seconds']})
 atomic_json(LIBRARY,{'records':records});return {'records':records}
def save_record(record,root_id=None):
 with (S/'take-library.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  data=library();record['root_id']=root_id or record['id'];data['records'].append(record);atomic_json(LIBRARY,data)
 return record
def queue_matrix(outcomes,current='',title='Last generation queue'):
 rows=[]
 for outcome in outcomes:
  name,sep,result=outcome.partition(' — ')
  rows.append('<tr><th style="text-align:left;padding:4px 8px">'+html.escape(name)+'</th><td style="padding:4px 8px">'+html.escape(result if sep else outcome)+'</td></tr>')
 return '<h4>'+html.escape(title)+'</h4><table style="width:100%;border-collapse:collapse"><thead><tr><th style="text-align:left;padding:4px 8px">Model</th><th style="text-align:left;padding:4px 8px">Result</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'+('<p>'+html.escape(current)+'</p>' if current else '')
class ComparisonControls:
 def __init__(self):
  self.data=library();self.busy=False;self.buttons=[];self.inputs=[]
  self.draft_path=S/'take-drafts.json';self.drafts=json.loads(self.draft_path.read_text()) if self.draft_path.exists() else {}
  self.status=w.HTML('<p>Choose a model section and compare its AI output with the voice sample. Play replays; Generate new version creates a new file.</p>')
  self.model_checks={}
  self.model_draft_path=S/'model-control-drafts.json'
  self.model_drafts=json.loads(self.model_draft_path.read_text()) if self.model_draft_path.exists() else {}
  self.model_fields={}
  inv='<table style="width:100%;text-align:left;table-layout:fixed"><colgroup><col style="width:34%"><col style="width:10%"><col style="width:56%"></colgroup><thead><tr><th style="padding:8px">Local speech model</th><th style="padding:8px">Assets</th><th style="padding:8px">Native controls</th></tr></thead><tbody>'
  for m in MODELS.values():inv+=f"<tr><td style='padding:8px;vertical-align:top'><strong>{html.escape(m['name'])}</strong><br>{html.escape(m['note'])}</td><td style='padding:8px;vertical-align:top'>{'Present' if m['ready'] else 'Missing'}</td><td style='padding:8px;vertical-align:top'>{html.escape(m['controls'])}</td></tr>"
  self.inventory=w.HTML('<details><summary>Available speech models and controls</summary>'+inv+'</tbody></table><p>These are the four downloaded speech models connected to this workbench. Codec and enhancement models are supporting tools, not extra voices. Other catalog entries are not installed models.</p></details>')
  self.grid=w.VBox()
  self.new_text=w.Textarea(value='I need you to stay right here.',description='Script:',layout=w.Layout(width='100%',height='60px'))
  self.new_model=w.Dropdown(options=[('All four models — sequential','all')]+[(m['name'],k) for k,m in MODELS.items()],value='all',description='Model:',layout=w.Layout(width='300px'))
  self.new_speaker=w.Dropdown(options=SPEAKERS,value='0012',description='Speaker:',layout=w.Layout(width='220px'))
  self.new_emotion=w.Dropdown(options=EMOTIONS,value='neutral',description='Reference:',layout=w.Layout(width='220px'))
  add=w.Button(description='Generate a new take',button_style='primary',layout=w.Layout(width='auto'));self.add=add
  add.on_click(self.create)
  self.preview=w.VBox();self.preview_buttons=[];self.queue_status=w.HTML()
  saved_queue=S/'last-queue.json'
  if saved_queue.exists():
   q=json.loads(saved_queue.read_text());self.queue_status.value=queue_matrix(q.get('outcomes',[]),q.get('current',''))
  for control in (self.new_model,self.new_speaker,self.new_emotion,self.new_text):control.observe(self.preview_references,names='value')
  self.preview_references()
  self.new_box=w.Accordion(children=[w.VBox([w.HBox([self.new_model,self.new_speaker,self.new_emotion],layout=w.Layout(flex_flow='row wrap',grid_gap='8px')),self.new_text,add,self.queue_status,self.preview,w.HTML('<p>One shared script and speaker. All runs IndexTTS, VoxCPM2, F5, then Dia, one at a time with each model’s controls below. Each result is saved separately; failures do not discard successful recordings.</p>')])]);self.new_box.set_title(0,'Create another take');self.new_box.selected_index=0
  self.history=w.Checkbox(value=False,description='Show saved versions and advanced controls',indent=False,layout=w.Layout(width='auto'));self.history.observe(self.render,names='value')
  self.view=w.VBox([self.inventory,w.HTML('<h3>Compare recordings</h3><p><a href="http://127.0.0.1:5197/" target="_blank" rel="noopener"><strong>Open scene comparison studio ↗</strong></a> · Compare two-person audio scenes across reference libraries and generators. Your recording wizard remains available inside.</p>'),self.new_box,self.status,self.history,self.grid],layout=w.Layout(width='100%'))
  self.render()
 def heads(self):
  heads={}
  for r in self.data['records']:heads[r.get('root_id',r['id'])]=r
  return list(heads.values())
 def execute(self,model,text,speaker,emotion,settings,root_id=None,parent_id=None):
  if self.busy:return
  self.busy=True
  for b in self.buttons+getattr(self,'preview_buttons',[])+[self.add,*self.inputs,*self.model_checks.values(),self.new_text,self.new_model,self.new_speaker,self.new_emotion]:b.disabled=True
  self.status.value='<p><strong>Generating one new take.</strong> Existing recordings are preserved. Only successful results enter the library.</p>'
  try:
   with (S/'take-generation.lock').open('a') as lock:
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('Another Paper 16 take is running; wait for it to finish.')
    r=backends.generate(model,text,speaker,emotion,settings,parent_id=parent_id)
    save_record(r,root_id)
   if root_id:
    self.drafts.pop(root_id,None);atomic_json(self.draft_path,self.drafts)
   self.data=library();self.status.value='<p><strong>New version ready.</strong> Earlier versions remain in its Version selector. The saved file was not overwritten.</p>'
   self.render();self.preview_references()
  except Exception as exc:
   self.status.value='<p><strong>Generation did not finish.</strong> '+html.escape(str(exc))+' Previous audio and edits are preserved.</p>'
  finally:
   self.busy=False
   for b in self.buttons+getattr(self,'preview_buttons',[])+[self.add,*self.inputs,*self.model_checks.values(),self.new_text,self.new_model,self.new_speaker,self.new_emotion]:b.disabled=False
 def preview_references(self,*_):
  try:
   catalog=backends.refs();speaker=self.new_speaker.value;emotion=self.new_emotion.value;text=self.new_text.value.strip()
   identity=catalog[f'esd:{speaker}:neutral'];feeling=catalog[f'esd:{speaker}:{emotion}']
   models=list(MODELS) if self.new_model.value=='all' else [self.new_model.value]
   rows=[w.HTML(backends.reference_library.summary(speaker)),w.HTML('<h4>Listen and generate per model</h4><p>Inputs and latest matching output for the script, speaker and feeling above. Emotion names are dataset labels; performance and intensity are not yet rated.</p>')];self.preview_buttons=[];self.model_fields={}
   for model in models:
    inputs=[('Voice identity','identity',identity),('Emotion guide','emotion',feeling)] if model=='index' else [('Source performance','reference',feeling)]
    cells=[]
    for title,role,ref in inputs:
     path=reference_module.verified_path(ref)
     content='<strong>'+html.escape(title)+'</strong>'+analysis.audio_panel(path,MODELS[model]['name']+' · '+title,role=role,transcript=ref.get('transcript',''),compact=True).data
     cells.append(w.HTML(content,layout=w.Layout(flex='1 1 220px',min_width='200px')))
    matches=[r for r in library()['records'] if (r['model'],r['text'].strip(),r['speaker'],r['emotion'])==(model,text,speaker,emotion)]
    output=w.HTML();saved=w.HTML()
    version_controls=[]
    if matches:
     def show_output(record,view=output,summary=saved,m=model):
      try:view.value=analysis.audio_panel(record.get('listening_path',record['path']),MODELS[m]['name']+' · Latest matching output',transcript=record['text'],compact=True).data
      except (OSError,ValueError):view.value='<p>Saved output unavailable. Generate a replacement below.</p>'
      summary.value='<small>Saved settings: '+html.escape(str(record.get('applied_settings',record.get('settings',{}))))+'</small>'
     selector=w.Dropdown(options=[('Take '+str(i+1)+(' — latest' if i==len(matches)-1 else ''),r['id']) for i,r in reversed(list(enumerate(matches)))],value=matches[-1]['id'],description='Version:',layout=w.Layout(width='100%'))
     def choose_output(change,records=matches,show=show_output):show(next(r for r in records if r['id']==change['new']))
     selector.observe(choose_output,names='value');show_output(matches[-1]);version_controls=[selector]
     title='AI output';action='Generate another take'
    else:output.value='<p>No matching output yet.</p>';title='AI output';action='Generate this model'
    settings_panel,fields=self.model_settings(model)
    self.model_fields[model]=fields
    button=w.Button(description=action,button_style='primary',layout=w.Layout(width='auto'));self.preview_buttons.append(button)
    def generate_one(_,m=model,t=text,sp=speaker,e=emotion,controls=fields):
     self.execute(m,t,sp,e,{k:c.value for k,c in controls.items()})
    button.on_click(generate_one);button.disabled=self.busy or not MODELS[model]['ready']
    cells.append(w.VBox([w.HTML('<strong>'+title+'</strong>'),*version_controls,output,saved],layout=w.Layout(flex='1 1 220px',min_width='200px')))
    rows.append(w.VBox([w.HTML('<strong>'+html.escape(MODELS[model]['name'])+' · '+html.escape(speaker)+' · '+html.escape(emotion)+'</strong>'),w.HBox(cells,layout=w.Layout(flex_flow='row wrap',grid_gap='8px')),settings_panel,button],layout=w.Layout(border='1px solid #d9dfe3',padding='6px',margin='0 0 6px')))
   self.preview.children=rows
  except Exception as exc:self.preview.children=[w.HTML('<p>Preview unavailable: '+html.escape(str(exc))+'</p>')]
 def model_settings(self,model):
  cfg={**backends.default_settings(model),**self.model_drafts.get(model,{})};fields={}
  def number(key,label,lo,hi,step=1,integer=False):
   cls=w.BoundedIntText if integer else w.BoundedFloatText
   fields[key]=cls(value=cfg[key],min=lo,max=hi,step=step,description=label,layout=w.Layout(width='220px'),style={'description_width':'80px'})
  number('seed','Seed:',0,2147483647,integer=True)
  notes=[]
  if model=='index':
   number('strength','Strength:',0,1,.1);number('duration_scale','Duration:',.5,2,.1)
   notes=['Emotion reference strength; duration above 1 slows synthesis.']
  if model in ('vox','f5'):
   number('steps','Steps:',1,64,integer=True);number('guidance','Guidance:',.1,8,.1)
  if model=='vox':
   fields['direction']=w.Textarea(value=cfg.get('direction',''),description='Direction:',layout=w.Layout(width='100%',height='60px'))
   notes=['Guidance is not emotion strength. Empty direction uses reference continuation; written direction switches to directed cloning.']
  if model=='f5':
   number('speed','Speed:',.3,2,.05);number('sway','Sway:',-1,1,.05);number('crossfade','Crossfade:',0,.5,.05)
   notes=['Crossfade is seconds. Production mastering defaults remain unchanged.']
  if model=='dia':
   fields['use_reference']=w.Checkbox(value=cfg.get('use_reference',True),description='Use reference continuation',indent=False)
   notes=['No native strength control. Each take receives a word check.']
  def remember(*_):
   self.model_drafts[model]={k:c.value for k,c in fields.items()};atomic_json(self.model_draft_path,self.model_drafts)
  for control in fields.values():control.observe(remember,names='value')
  self.preview_buttons.extend(fields.values())
  panel=w.Accordion(children=[w.VBox([w.HBox(list(fields.values()),layout=w.Layout(flex_flow='row wrap',grid_gap='6px')),w.HTML('<small>'+' '.join(notes)+' Changes apply to the next generation, not saved playback.</small>')])])
  panel.set_title(0,'Model controls');panel.selected_index=None
  return panel,fields
 def create(self,_):
  if self.busy or getattr(self,'queue_running',False):return
  models=list(MODELS) if self.new_model.value=='all' else [self.new_model.value]
  text,speaker,emotion=self.new_text.value,self.new_speaker.value,self.new_emotion.value
  # Validate the entire request before starting any model.
  try:
   for model in models:backends.validate(model,text,speaker,emotion,{k:c.value for k,c in self.model_fields[model].items()})
  except Exception as exc:
   self.queue_status.value='<p><strong>Nothing started.</strong> '+html.escape(str(exc))+'</p>';return
  queue_settings={m:{k:c.value for k,c in self.model_fields[m].items()} for m in models}
  self.queue_running=True;outcomes=[]
  def report(current=''):
   atomic_json(S/'last-queue.json',{'models':models,'text':text,'speaker':speaker,'emotion':emotion,'outcomes':outcomes,'current':current})
   self.queue_status.value=queue_matrix(outcomes,current,'Generation queue')
  try:
   for i,model in enumerate(models):
    report(f'{i+1} of {len(models)}: generating {MODELS[model]["name"]}. Only one model runs at a time.')
    before={r['id'] for r in library()['records']}
    self.execute(model,text,speaker,emotion,queue_settings[model])
    fresh=[r for r in library()['records'] if r['id'] not in before]
    if fresh:outcomes.append(MODELS[model]['name']+' — saved; '+format(fresh[-1].get('duration_seconds',0),'.2f')+' seconds. Inspect its output below.')
    else:outcomes.append(MODELS[model]['name']+' — failed. '+self.status.value.replace('<p>','').replace('</p>','').replace('<strong>','').replace('</strong>',''))
    report()
  finally:
   self.queue_running=False;report('Queue finished. Saved outputs are below; earlier recordings remain available.')

 def card(self,record):
  root=record.get('root_id',record['id']);versions=[r for r in self.data['records'] if r.get('root_id',r['id'])==root];current=[record]
  draft=self.drafts.get(root,{})
  record=next((r for r in versions if r['id']==draft.get('version_id')),record);current[0]=record
  model=record['model'];cfg={**record.get('applied_settings',record.get('settings',{})),**draft.get('settings',{})}
  label=w.HTML();player=w.HTML();references_view=w.HTML();details=w.HTML();pending=w.HTML();output_summary=w.HTML()
  selector=w.Dropdown(options=[(f"Version {i+1}"+(' — original' if i==0 else ''),r['id']) for i,r in reversed(list(enumerate(versions)))],value=record['id'],description='Version:',layout=w.Layout(width='240px'),style={'description_width':'70px'})
  text=w.Textarea(value=draft.get('text',record['text']),description='Script:',layout=w.Layout(width='100%',height='76px'),style={'description_width':'70px'})
  speaker=w.Dropdown(options=SPEAKERS,value=draft.get('speaker',record['speaker']),description='Speaker:',layout=w.Layout(width='100%'),style={'description_width':'70px'})
  emotion=w.Dropdown(options=EMOTIONS,value=draft.get('emotion',record['emotion']),description='Reference:',layout=w.Layout(width='100%'),style={'description_width':'70px'})
  seed=w.BoundedIntText(continuous_update=True,value=int(cfg.get('seed',7)),min=0,max=2147483647,description='Seed:',layout=w.Layout(width='100%'),style={'description_width':'70px'})
  fields={'seed':seed};native=[speaker,emotion,seed]
  visible=[]
  if model=='index':
   strength=w.FloatSlider(value=float(cfg.get('strength',record.get('strength',1))),min=0,max=1,step=.1,description='Strength:',continuous_update=False,layout=w.Layout(width='280px'),style={'description_width':'70px'});fields['strength']=strength;visible.append(strength)
   fields['duration_scale']=w.BoundedFloatText(continuous_update=True,value=float(cfg.get('duration_scale',1)),min=.5,max=2,step=.1,description='Duration:',layout=w.Layout(width='100%'),style={'description_width':'70px'});native.extend([fields['duration_scale'],w.HTML('<p>Duration scale above 1 slows speech; below 1 shortens it. This is native synthesis control, not playback speed.</p>')])
  else:pass
  if model in ('vox','f5'):
   fields['steps']=w.BoundedIntText(continuous_update=True,value=int(cfg.get('steps',10 if model=='vox' else 32)),min=1,max=64,description='Steps:',layout=w.Layout(width='100%'),style={'description_width':'70px'})
   fields['guidance']=w.BoundedFloatText(continuous_update=True,value=float(cfg.get('guidance',2)),min=.1,max=8,step=.1,description='Guidance:',layout=w.Layout(width='100%'),style={'description_width':'70px'})
   native.extend([fields['steps'],fields['guidance']])
  if model=='vox':
   fields['direction']=w.Textarea(value=cfg.get('direction',''),description='Direction:',layout=w.Layout(width='100%',height='70px'),style={'description_width':'70px'});native.extend([fields['direction'],w.HTML('<p>Empty direction uses reference continuation. Adding direction switches to instruction-conditioned cloning; it is not an emotion-strength control.</p>')])
  if model=='f5':
   for key,title,value,lo,hi in [('speed','Speed:',1,.3,2),('sway','Sway:',-1,-1,1),('crossfade','Crossfade:',.15,0,.5)]:
    fields[key]=w.BoundedFloatText(continuous_update=True,value=float(cfg.get(key,value)),min=lo,max=hi,step=.05,description=title,layout=w.Layout(width='100%'),style={'description_width':'70px'});native.append(fields[key])
   native.append(w.HTML('<p>Crossfade is seconds. These are raw synthesis comparisons; Money’s production mastering settings remain unchanged.</p>'))
  if model=='dia':
   fields['use_reference']=w.Checkbox(value=cfg.get('use_reference',True),description='Use reference continuation',indent=False);native.extend([fields['use_reference'],w.HTML('<p>Dia works best with roughly 5–20 seconds of speech. Same-speaker reference continuation is formatted automatically. No native strength or speed controls. Each new take gets an offline word check; delivery still needs listening.</p>')])
  advanced=w.Accordion(children=[w.VBox([text,*native])]);advanced.set_title(0,'Edit script and native settings');advanced.selected_index=None
  button=w.Button(description='Generate new version',button_style='primary',layout=w.Layout(width='auto'));self.buttons.append(button)
  def show(r):
   version_number=next(i+1 for i,v in enumerate(versions) if v['id']==r['id'])
   saved=r.get('applied_settings',r.get('settings',{}))
   strength_note=(' · saved strength '+str(saved.get('strength',r.get('strength',1)))) if model=='index' else ''
   output_summary.value='<p style="padding:6px;background:#edf4f8;border-left:4px solid #426b83"><strong>Version '+str(version_number)+' of '+str(len(versions))+' · '+('Latest saved recording' if r['id']==versions[-1]['id'] else 'Earlier saved recording')+'</strong><br>'+format(r.get('duration_seconds',0),'.2f')+' seconds'+html.escape(strength_note)+'</p>'
   label.value='<p><strong>'+html.escape(MODELS[model]['name'])+' · '+html.escape(r['emotion'].title())+'</strong></p>'
   try:player.value=analysis.audio_panel(r.get('listening_path',r['path']),MODELS[model]['name']+' '+r['emotion'],transcript=r['text'],compact=True).data
   except (OSError,ValueError):player.value='<p>Saved audio is unavailable. Other takes remain usable; generate a new version to recover this one.</p>'
   ref_parts=[];refs=[]
   try:
    refs=reference_module.references(r)
    if not refs:ref_parts.append('<p><strong>No reference used for this version.</strong> Its voice was generated without reference conditioning.</p>')
    for role,ref in refs:
     path=reference_module.verified_path(ref)
     ref_parts.append('<h4>'+html.escape(role)+'</h4><p>'+html.escape(ref.get('label',r['speaker']+' '+r['emotion']))+'</p>'+analysis.audio_panel(path,MODELS[model]['name']+' '+role,role=('identity' if role=='Voice identity reference' else 'emotion' if role=='Emotion reference' else 'reference'),transcript=ref.get('transcript',''),compact=True)._repr_html_())
     ref_parts.append('<details><summary>Reference transcript</summary><p>'+html.escape(ref.get('transcript','Transcript not recorded'))+'</p></details>')
   except (OSError,ValueError,KeyError) as exc:ref_parts.append('<p><strong>Reference unavailable.</strong> '+html.escape(str(exc))+'</p>')
   if model=='index' and len(refs)==2 and refs[0][1].get('sha256')==refs[1][1].get('sha256'):ref_parts.insert(0,'<p><strong>Same recording, two roles.</strong> This neutral take uses the same sample for voice identity and emotion guidance.</p>')
   references_view.value=''.join(ref_parts)
   conf=r.get('applied_settings',r.get('settings',{}))
   applied='Reference strength '+str(conf.get('strength',r.get('strength',1))) if model=='index' else ('No strength setting; '+('steps '+str(conf.get('steps'))+', ' if model in ('vox','f5') else '')+'seed '+str(conf.get('seed',7)))
   if model=='index':applied+=', duration scale '+str(conf.get('duration_scale',1))
   if model in ('vox','f5'):applied+=', guidance '+str(conf.get('guidance',2))
   if model=='f5':applied+=', speed '+str(conf.get('speed',1))+', sway '+str(conf.get('sway',-1))+', crossfade '+str(conf.get('crossfade',.15))+' s'
   if model=='vox':applied+='; directed cloning' if conf.get('direction','').strip() else '; reference continuation'
   if model=='dia':applied+='; reference continuation' if conf.get('use_reference',True) else '; generated speaker, no reference conditioning'
   source=html.escape(r.get('source','Generated in Paper 16'))
   if model=='dia':source+='; '+('MLX fp16 isolated continuation adapter' if r.get('native_backend') else 'original VoiceStudio MLX adapter')
   download=("<p><a href='"+html.escape(r['url'],quote=True)+"' download>Download raw WAV</a></p>") if r.get('url') else '<p>Original raw file preserved in Paper 15.</p>'
   check=r.get('word_check',{});verdict=('<p><strong>Word check: '+('exact words recovered' if check.get('exact_words') else 'not passed')+'</strong><br>Heard by ASR: '+html.escape(check.get('transcript','No transcript'))+'</p>') if check else ''
   script='<details><summary>Script for this version</summary><p>'+html.escape(r['text'])+'</p></details>'
   details.value='<details><summary>Saved settings, script and download</summary>'+verdict+script+'<p>Applied: '+html.escape(applied)+'. '+source+'.</p>'+download+'</details>'
  def choose(change):
   r=next(x for x in versions if x['id']==change['new']);current[0]=r;show(r)
   text.value=r['text'];speaker.value=r['speaker'];emotion.value=r['emotion']
   for k,c in fields.items():
    if k in r.get('applied_settings',r.get('settings',{})):c.value=r['settings'][k]
  selector.observe(choose,names='value')
  def regenerate(_):
   r=current[0];settings={k:c.value for k,c in fields.items()};self.execute(model,text.value,speaker.value,emotion.value,settings,root_id=root,parent_id=r['id'])
  def remember(*_):
   self.drafts[root]={'version_id':current[0]['id'],'text':text.value,'speaker':speaker.value,'emotion':emotion.value,'settings':{k:c.value for k,c in fields.items()}}
   atomic_json(self.draft_path,self.drafts)
   r=current[0];edited=text.value!=r['text'] or speaker.value!=r['speaker'] or emotion.value!=r['emotion'] or any(c.value!=r.get('applied_settings',r.get('settings',{})).get(k,c.value) for k,c in fields.items())
   pending.value='<p><strong>Edits pending.</strong> Play still uses the saved settings above. Generate a new version to apply.</p>' if edited else ''
  for control in [text,speaker,emotion,*fields.values()]:control.observe(remember,names='value')
  selector.observe(remember,names='value')
  self.inputs.extend([selector,text,speaker,emotion,*fields.values()])
  button.on_click(regenerate);show(record);remember()
  media=w.Box([
   w.VBox([w.HTML('<h4>AI output — newly generated speech</h4>'),output_summary,player],layout=w.Layout(flex='1 1 260px',min_width='260px')),
   w.VBox([references_view],layout=w.Layout(flex='1 1 260px',min_width='260px'))
  ],layout=w.Layout(display='flex',flex_flow='row wrap',grid_gap='16px',width='100%'))
  return w.VBox([w.HBox([label,selector],layout=w.Layout(flex_flow='row wrap',grid_gap='12px',align_items='center')),media,details,*visible,pending,advanced,button],layout=w.Layout(width='100%',padding='4px 0 8px')).add_class('p16-take-'+root)
 def render(self,*_):
  if hasattr(self,'history') and not self.history.value:
   self.grid.children=[]
   if hasattr(self,'preview'):self.preview_references()
   return
  self.data=library();self.buttons=[];self.inputs=[]
  selected=list(MODELS)
  if not selected:self.grid.children=[w.HTML('<p>Select at least one model above.</p>')];return
  heads=self.heads();groups=list(dict.fromkeys((r['text'],r['speaker'],r['emotion']) for r in heads))
  sections=[]
  for text,speaker,emotion in groups:
   sections.append(w.HTML('<h3>'+html.escape(emotion.title())+' · same requested words</h3><p><strong>'+html.escape(text)+'</strong><br>Speaker reference '+html.escape(speaker)+'</p>'))
   for model in selected:
    records=[r for r in heads if (r['text'],r['speaker'],r['emotion'],r['model'])==(text,speaker,emotion,model)]
    content=[w.HTML('<h3>'+html.escape(MODELS[model]['name'])+'</h3>')]
    if records:content.extend(self.card(r) for r in records)
    else:
     content.append(w.HTML('<p>This model has no generated take for these words and delivery yet.</p>'))
     button=w.Button(description='Generate matching take',layout=w.Layout(width='auto'));self.buttons.append(button)
     def make(_,m=model,t=text,s=speaker,e=emotion):
      self.execute(m,t,s,e,backends.default_settings(m))
     button.on_click(make);button.disabled=not MODELS[model]['ready'];content.append(button)
    sections.append(w.VBox(content,layout=w.Layout(width='100%',border='1px solid #d9dfe3',padding='8px',margin='0 0 8px')).add_class('p16-model-section'))
  self.grid.children=[w.HTML('<p><strong>One model per section.</strong> Blue: AI output. Amber: source voice sample. Olive: voice identity. Purple: emotion guide. Each has its own Play button. Sections stay full width when you select more models.</p>'),*sections]

def show_controls(previous=None):
 values={};checks={}
 if previous is not None:
  values={name:getattr(previous,name).value for name in ('new_text','new_speaker','new_emotion')}
  # Paper 16 now owns a single live widget workspace. Retire stale displays.
  from ipywidgets import Widget
  Widget.close_all()
 panel=ComparisonControls()
 for name,value in values.items():getattr(panel,name).value=value
 display(panel.view)
 return panel

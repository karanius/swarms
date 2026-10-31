"""Run a source-pinned IndexTTS-2.5 audition outside the notebook kernel."""
from pathlib import Path
import os,json,time,hashlib,subprocess,sys,uuid,importlib.util
STUDY=Path(__file__).resolve().parent
ROOT=STUDY.parents[2]
RUNTIME=Path('/Users/x/.local/share/swarms/indextts-paper16')
CODE_REV='d9e41aac89fd00b3d71497fddb287b7f24613712'
MODEL_REV='c39ce5ba981572cb187443877ff559dfb246ce63'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(text='I need you to stay right here.',speaker='0012',seed=7,conditions=None,duration_scale=1.0,reference_overrides=None):
    if not text.strip() or len(text)>500:raise ValueError('Use 1–500 characters.')
    if not .5<=duration_scale<=2:raise ValueError('Duration scale must be 0.5–2')
    downloads=json.loads((STUDY/'indextts-downloads.json').read_text())
    if downloads['stage']!='complete':raise RuntimeError('Model preparation is not complete')
    spec=importlib.util.spec_from_file_location('index_reference_library',STUDY/'reference_library.py')
    library=importlib.util.module_from_spec(spec);spec.loader.exec_module(library)
    catalog=list(library.catalog().values())
    refs={}
    if reference_overrides is not None:
        refs=dict(reference_overrides)
        if 'neutral' not in refs:raise ValueError('Neutral identity reference is required')
        for ref in refs.values():
            if sha(ref['path'])!=ref['sha256']:raise ValueError('Reference changed')
    else:
        for emotion in ('neutral','anger','happiness','sadness','surprise'):
            ref=next(x for x in catalog if x['id']==f'esd:{speaker}:{emotion}')
            if sha(ref['path'])!=ref['sha256']:raise ValueError('Reference changed')
            refs[emotion]=ref
    conditions=conditions or [{'emotion':'neutral','strength':1.0},{'emotion':'anger','strength':0.5},{'emotion':'anger','strength':1.0}]
    for c in conditions:
        if c['emotion'] not in refs or not 0<=c['strength']<=1:raise ValueError('Invalid emotion / strength')
        if c.get('emo_vector') is not None and (len(c['emo_vector'])!=8 or any(not 0<=v<=1 for v in c['emo_vector'])):raise ValueError('Use eight emotion values between zero and one')
    run_dir=STUDY/'runs'/('indextts-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True)
    request={'text':text,'speaker':speaker,'seed':seed,'conditions':conditions,'references':refs,
        'code_revision':CODE_REV,'model_revision':MODEL_REV,'device':'mps',
        'native_method':'per-condition emotion audio reference or native emotion vector','use_emo_text':False,'use_random':False,
        'precision':'float32','duration_factor':float(duration_scale)}
    (run_dir/'request.json').write_text(json.dumps(request,indent=2))
    env={**os.environ,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1',
         'ORT_DISABLE_TELEMETRY':'1','DO_NOT_TRACK':'1','PYTORCH_ENABLE_MPS_FALLBACK':'1',
         'NLTK_DATA':str(RUNTIME/'nltk_data'),'XDG_CACHE_HOME':str(RUNTIME/'cache')}
    with (run_dir/'inference.log').open('w') as log:
        proc=subprocess.run([str(RUNTIME/'venv/bin/python'),str(Path(__file__).resolve()),'worker',str(run_dir)],
             cwd=RUNTIME/'source',env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
    if proc.returncode:raise RuntimeError(f'IndexTTS failed; preserved log: {run_dir}/inference.log')
    result=json.loads((run_dir/'result.json').read_text())
    (STUDY/'indextts-latest.json').write_text(json.dumps(result,indent=2))
    return result
def worker(folder):
    import random,numpy as np,soundfile as sf,torch
    d=Path(folder);q=json.loads((d/'request.json').read_text())
    actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=RUNTIME/'source',text=True).strip()
    if actual!=CODE_REV:raise RuntimeError('Code revision mismatch')
    if not torch.backends.mps.is_available():raise RuntimeError('Apple GPU unavailable')
    from indextts.infer_v2_5 import IndexTTS2
    started=time.time()
    model=IndexTTS2(cfg_path=str(RUNTIME/'checkpoints/config.yaml'),model_dir=str(RUNTIME/'checkpoints'),
       device='mps',use_bf16=False,use_cuda_kernel=False,use_deepspeed=False,
       use_accel=False,use_torch_compile=False,use_qwen_emo=False)
    devices=[]
    def observe(_module,args,kwargs):
        for x in [*args,*kwargs.values()]:
            if isinstance(x,torch.Tensor):devices.append(str(x.device))
    model.semantic_model.register_forward_pre_hook(observe,with_kwargs=True)
    result={'run_dir':str(d),'request':q,'load_seconds':time.time()-started,'torch':torch.__version__,
       'parameter_device':str(next(model.gpt.parameters()).device),'takes':[],
       'listening_assessment':'Not yet rated','mps_fallback_enabled':True}
    for i,c in enumerate(q['conditions']):
        random.seed(q['seed']);np.random.seed(q['seed']);torch.manual_seed(q['seed'])
        out=d/f"{i+1}-{c['emotion']}-{c['strength']}.wav"
        tick=time.time()
        model.infer(spk_audio_prompt=q['references']['neutral']['path'],emo_audio_prompt=None if c.get('emo_vector') is not None else q['references'][c['emotion']]['path'],emo_vector=c.get('emo_vector'),
            emo_alpha=c['strength'],text=q['text'],lang='EN',output_path=str(out),
            use_random=False,use_emo_text=False,do_sample=True,duration_factor=q.get('duration_factor',1.0),verbose=False)
        samples,sr=sf.read(out)
        if not samples.size or not np.isfinite(samples).all() or np.sqrt(np.mean(samples**2))<1e-6:raise RuntimeError('Invalid audio')
        export=ROOT/'knowledge/research/notebooks/paper-16-audio'/(d.name+'-'+out.name)
        import shutil
        shutil.copy2(out,export)
        ffmpeg='/Users/x/.local/share/money/f5-tts/venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
        meter=subprocess.run([ffmpeg,'-hide_banner','-i',str(out),'-af','loudnorm=I=-23:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
        measured=json.loads(meter[meter.rfind('{'):meter.rfind('}')+1])
        gain=10**(min(-23-float(measured['input_i']),-2-float(measured['input_tp']))/20)
        listening=out.with_name(out.stem+'-listening.wav')
        sf.write(listening,samples*gain,sr,subtype='PCM_24')
        result['takes'].append({'listening_path':str(listening),'listening_gain':gain,'raw_loudness':measured,'target_lufs':-23,**c,'path':str(out),'url':'/research-jupyter/files/paper-16-audio/'+export.name,
          'sha256':sha(out),'sample_rate':sr,'duration_seconds':len(samples)/sr,
          'peak':float(np.max(np.abs(samples))),'rms':float(np.sqrt(np.mean(samples**2))),'elapsed_seconds':time.time()-tick})
        result['observed_feature_tensor_devices']=sorted(set(devices))
        (d/'result.json').write_text(json.dumps(result,indent=2))
        print('TAKE_COMPLETE',out.name,flush=True)
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='worker':worker(sys.argv[2])
    else:print(json.dumps(run(),indent=2))


def show_trial():
    import ipywidgets as w
    from IPython.display import display,Audio,HTML
    text=w.Textarea(value='I need you to stay right here.',description='Script:',layout=w.Layout(width='100%'))
    speaker=w.Dropdown(options=[('Male reference 0012','0012'),('Female reference 0015','0015')],description='Speaker:')
    emotion=w.Dropdown(options=['anger','happiness','sadness','surprise'],description='Emotion:')
    strength=w.FloatSlider(value=0.5,min=0,max=1,step=0.1,description='Strength:',continuous_update=False)
    button=w.Button(description='Generate comparison',button_style='primary',layout=w.Layout(width='auto'))
    status=w.HTML('<p>Generates neutral, selected emotion at the chosen strength, and selected emotion at full strength. Playback does not regenerate.</p>')
    output=w.Output()
    def render(result):
        import html
        output.clear_output(wait=True)
        baseline={}
        if result['request']['text']=='I need you to stay right here.' and result['request']['speaker']=='0012':
            saved=json.loads((ROOT/'knowledge/research/paper-15-study/reference-guidance-analysis.json').read_text())
            baseline={('anger' if item['condition']=='angry-reference' else 'neutral'):item for item in saved['conditions']}
        emotions=list(dict.fromkeys(take['emotion'] for take in result['takes']))
        rows=[]
        for feeling in emotions:
            index=[]
            for take in result['takes']:
                if take['emotion']!=feeling:continue
                player=Audio(filename=take.get('listening_path',take['path']))._repr_html_()
                player=player.replace('<audio ', '<audio style="width:100%;max-width:340px" ')
                index.append(f"<div style='margin:8px 0 18px'><p>Emotion strength {take['strength']}</p>{player}<p><a href='{html.escape(take['url'],quote=True)}' download>Download raw WAV</a></p></div>")
            if feeling in baseline:
                item=baseline[feeling]
                player=Audio(filename=item['matched_path'])._repr_html_().replace('<audio ', '<audio style="width:100%;max-width:340px" ')
                vox=f"<p>{html.escape(feeling.title())} reference — saved Paper 15 take</p>{player}<p>No equivalent emotion-strength setting; not regenerated.</p>"
            else:
                vox='<p>No matching recording for this speaker, script and delivery.</p>'
            rows.append(f"<tr><th scope='row' style='vertical-align:top;padding:12px'>{html.escape(feeling.title())}</th><td style='vertical-align:top;padding:12px'>{''.join(index)}</td><td style='vertical-align:top;padding:12px'>{vox}</td></tr>")
        with output:
            display(HTML("<div style='overflow-x:auto'><table style='width:100%;min-width:680px;text-align:left;table-layout:fixed'><colgroup><col style='width:14%'><col style='width:43%'><col style='width:43%'></colgroup><thead><tr><th scope='col'>Delivery</th><th scope='col'>IndexTTS 2.5</th><th scope='col'>VoxCPM2</th></tr></thead><tbody>"+''.join(rows)+"</tbody></table></div><p>Same delivery across each row. Model controls differ; strength numbers are not interchangeable. Judge acting, identity and wording separately.</p>"))
    def clicked(_):
        for c in (button,text,speaker,emotion,strength):c.disabled=True
        status.value='<p>Generating in the isolated IndexTTS process. Existing recordings stay saved.</p>'
        try:
            result=run(text=text.value,speaker=speaker.value,conditions=[{'emotion':'neutral','strength':1.0},{'emotion':emotion.value,'strength':strength.value},{'emotion':emotion.value,'strength':1.0}])
            render(result)
            status.value='<p><strong>Comparison ready.</strong> Three new recordings saved with provenance.</p>'
        except Exception as exc:
            status.value='<p><strong>Experiment failed.</strong> Previous recordings remain available.</p>'
            with output:print(str(exc))
        finally:
            for c in (button,text,speaker,emotion,strength):c.disabled=False
    button.on_click(clicked)
    display(w.VBox([speaker,emotion,strength,text,button,status,output]))
    latest=STUDY/'indextts-latest.json'
    if latest.exists():render(json.loads(latest.read_text()))
    return {'text':text,'button':button,'status':status,'output':output}

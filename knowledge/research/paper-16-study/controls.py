"""Native Jupyter controls for reference-guided local speech experiments."""
from pathlib import Path
import hashlib, html, importlib.util, json, shutil, time, uuid
import ipywidgets as w
from IPython.display import Audio, HTML, display

STUDY=Path(__file__).resolve().parent
ROOT=STUDY.parents[2]

def references():
    raw=(ROOT/'knowledge/research/paper-14-study/f5-catalog.json.txt').read_text()
    catalog=json.loads(raw.split('CATALOG=',1)[1])
    return [r for r in catalog['presets'] if r['id'].startswith('esd:')]

class PerformanceControls:
    def __init__(self):
        self.catalog=references()
        speakers={r['id'].split(':')[1]:r['label'].split(' · ')[1] for r in self.catalog}
        ordered=sorted(speakers,key=lambda k:(k not in ('0012','0015'),k))
        self.speaker=w.Dropdown(options=[(f"{speakers[s].title()} reference {s}",s) for s in ordered],value='0012',description='Speaker:',layout=w.Layout(width='100%'),style={'description_width':'90px'})
        self.emotion=w.Dropdown(options=[(e.title(),e) for e in ('neutral','anger','happiness','sadness','surprise')],description='Emotion:',layout=w.Layout(width='100%'),style={'description_width':'90px'})
        self.text=w.Textarea(value='I need you to stay right here.',description='Script:',placeholder='Enter the words you want spoken.',layout=w.Layout(width='100%',height='100px'),style={'description_width':'90px'})
        self.seed=w.BoundedIntText(value=7,min=0,max=2147483647,description='Seed:')
        self.steps=w.IntSlider(value=10,min=1,max=64,description='Steps:',continuous_update=False)
        self.generate=w.Button(description='Generate audio',button_style='primary',icon='play',layout=w.Layout(width='auto',min_width='150px'))
        self.preview=w.Button(description='Listen to reference',icon='volume-up',layout=w.Layout(width='auto',min_width='180px'))
        self.status=w.HTML('<p>Ready. Choose an emotion, edit the script, then generate.</p>')
        self.inventory=w.HTML()
        self.output=w.Output()
        self.reference_output=w.Output()
        advanced=w.Accordion(children=[w.VBox([self.seed,self.steps])]);advanced.set_title(0,'Generation settings');advanced.selected_index=None
        self.view=w.VBox([w.HTML('<h3>Generate a voice performance</h3><p>Available reference emotions are listed below. Availability does not mean a delivery is validated for every script.</p>'),self.speaker,self.inventory,self.emotion,self.text,advanced,w.HBox([self.generate,self.preview],layout=w.Layout(flex_flow='row wrap',gap='8px')),self.status,w.HTML("<h4>Reference recording</h4>"),self.reference_output,w.HTML("<h4>Latest generated recording</h4><p>Press Play to replay. Generate audio creates a new recording; listening to a reference keeps this one here.</p>"),self.output],layout=w.Layout(width='100%',max_width='800px'))
        self.speaker.observe(self._update_inventory,names='value')
        self.emotion.observe(self._update_inventory,names='value')
        self.generate.on_click(self._generate)
        self.preview.on_click(self._preview)
        self.last_result=None
        self._update_inventory()

    def selected_reference(self):
        key=f'esd:{self.speaker.value}:{self.emotion.value}'
        return next(r for r in self.catalog if r['id']==key)

    def _update_inventory(self,*_):
        rows=[]
        for emotion in ('neutral','anger','happiness','sadness','surprise'):
            r=next(x for x in self.catalog if x['id']==f'esd:{self.speaker.value}:{emotion}')
            available=Path(r['path']).is_file()
            evidence='Used in the user-approved Paper 15 comparison' if self.speaker.value=='0012' and emotion in ('neutral','anger') else 'Not yet evaluated for this speaker in Paper 16'
            rows.append(f'<tr><td>{emotion.title()}</td><td>{"Available" if available else "File missing"}</td><td>{evidence}</td></tr>')
        self.inventory.value='<table style="width:100%;text-align:left"><thead><tr><th>Emotion</th><th>Reference</th><th>Evidence</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><p><strong>Not yet cataloged:</strong> warm reassurance, curiosity, skepticism, disappointment, restrained frustration.</p>'
        missing=not Path(self.selected_reference()['path']).is_file()
        self.generate.disabled=missing;self.preview.disabled=missing
        self.reference_output.clear_output(wait=True)
        with self.reference_output:
            if not missing:display(Audio(filename=self.selected_reference()['path'],label='Selected source reference',role='reference'))

    def _preview(self,_):
        self.reference_output.clear_output(wait=True)
        self.status.value='<p><strong>Reference ready.</strong> Press Play below if it does not start automatically.</p>'
        with self.reference_output:
            print('Reference sample:',self.emotion.value,'— input recording, not newly generated speech')
            display(Audio(filename=self.selected_reference()['path'],label='Selected source reference',role='reference'))

    def _generate(self,_):
        text=self.text.value.strip()
        if not text:
            self.status.value='<p><strong>Enter a script before generating.</strong></p>';return
        if len(text)>500:
            self.status.value='<p><strong>Use 500 characters or fewer for this audition.</strong> Short passages make delivery easier to evaluate.</p>';return
        ref=self.selected_reference();path=Path(ref['path'])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=ref['sha256']:
            self.status.value='<p><strong>The selected reference is missing or changed.</strong> Restore it before generating.</p>';return
        controls=[self.speaker,self.emotion,self.text,self.seed,self.steps,self.generate,self.preview]
        for c in controls:c.disabled=True
        self.status.value='<p>Generating audio from the selected reference…</p>'
        try:
            spec=importlib.util.spec_from_file_location('paper16_api',STUDY/'api_experiment.py')
            api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
            name='interactive-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
            result=api.generate(name,text,engine='voxcpm2',instruct=None,seed=self.seed.value,
                ref_audio=str(path),ref_text=ref['transcript'],num_step=self.steps.value)
            self.last_result=result
            result['selection']={'speaker':self.speaker.value,'emotion':self.emotion.value,'reference_id':ref['id'],'mode':'audio-continuation','evidence_status':'Experimental output; listener assessment required'}
            audio=Path(result['audio']['path'])
            exports=ROOT/'knowledge/research/notebooks/paper-16-audio';exports.mkdir(exist_ok=True)
            export=exports/(name+'.wav');shutil.copy2(audio,export)
            result['selection']['download_url']='/research-jupyter/files/paper-16-audio/'+export.name
            (audio.parent/'ui-selection.json').write_text(json.dumps(result['selection'],indent=2))
            self.status.value=f"<p><strong>Audio generated.</strong> {result['audio']['duration_seconds']:.2f} seconds of audio. Listen for the requested delivery and exact words.</p>"
            self.output.clear_output(wait=True)
            with self.output:
                print('Generated recording —',self.emotion.value,'reference')
                display(Audio(filename=str(audio)))
                display(HTML(f'<p><a download="{html.escape(export.name)}" href="{html.escape(result["selection"]["download_url"])}">Download WAV</a></p>'))
                print('Saved with its script, reference, settings and measurements in Paper 16.')
        except Exception as exc:
            self.status.value='<p><strong>Generation failed.</strong> Check that the local VoiceStudio backend is running, then try again. Your script is preserved.</p>'
            with self.output:print(type(exc).__name__+': '+str(exc)[:500])
        finally:
            for c in controls:c.disabled=False
            self._update_inventory()

# Shared renderer also covers reference previews and newly generated tracks.
_spec=importlib.util.spec_from_file_location('paper16_audio_analysis',STUDY/'audio_analysis.py')
_analysis=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_analysis)
Audio=_analysis.audio_panel

def show_controls(previous=None):
    panel=PerformanceControls()
    if previous is not None:
        for name in ('speaker','emotion','text','seed','steps'):
            getattr(panel,name).value=getattr(previous,name).value
        panel.last_result=previous.last_result
        if panel.last_result:
            # Reconstruct from the saved recording even if preview hid the old player.
            result=panel.last_result
            audio=Path(result['audio']['path'])
            selection=result.get('selection',{})
            with panel.output:
                print('Generated recording —',selection.get('emotion','saved'),'reference')
                display(Audio(filename=str(audio)))
                url=selection.get('download_url')
                if url:
                    display(HTML(f'<p><a href="{html.escape(url)}" download>Download WAV</a></p>'))
            panel.status.value='<p><strong>Latest recording preserved.</strong> Both players can be replayed without generating again.</p>'
    display(panel.view)
    return panel

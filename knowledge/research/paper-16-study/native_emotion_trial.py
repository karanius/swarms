"""Controlled reference-versus-native-vector anger audition."""
from pathlib import Path
import importlib.util,json
S=Path(__file__).resolve().parent
def load(name):
 spec=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def run():
 result=load('indextts_experiment').run(text='I need you to stay right here.',speaker='0012',seed=7,duration_scale=1.0,conditions=[{'emotion':'anger','strength':1.0,'method':'External angry reference'},{'emotion':'anger','strength':1.0,'method':'Built-in anger vector','emo_vector':[0,1,0,0,0,0,0,0]}])
 result['comparison_note']='Same neutral identity reference, words, seed, duration and sampling; emotion method differs. Static-gain listening copies; no acting quality inferred from generation.'
 (S/'native-emotion-comparison.json').write_text(json.dumps(result,indent=2));return result
def show():
 from IPython.display import display,HTML
 result=json.loads((S/'native-emotion-comparison.json').read_text());a=load('audio_analysis')
 display(HTML('<h3>IndexTTS: recorded anger versus built-in anger</h3><p>Same voice, same words: <strong>I need you to stay right here.</strong> Seed 7, strength 1.0, duration scale 1.0. The built-in take uses no external anger recording. Listen for convincing anger, correct words and the same speaker. No winner is claimed.</p>'))
 display(a.audio_panel(result['request']['references']['neutral']['path'],'Shared voice identity',role='identity',compact=True))
 for take in result['takes']:
  display(HTML('<h4>'+take['method']+'</h4>'))
  if 'emo_vector' not in take:display(a.audio_panel(result['request']['references']['anger']['path'],'External anger input',role='emotion',compact=True))
  else:display(HTML('<p>Native control: anger 1.0; all seven other emotion values zero. No external emotion clip.</p>'))
  display(a.audio_panel(take['listening_path'],take['method']+' output',compact=True))
  check=take.get('word_check',{});display(HTML('<p>Automatic word check: '+('exact words recovered' if check.get('exact_words') else 'not established')+'. Emotional performance still needs listening.</p>'))
if __name__=='__main__':
 r=run();print([(t['method'],t['duration_seconds']) for t in r['takes']])

"""Canonical reference metadata; unknown acting attributes stay unknown."""
from pathlib import Path
import hashlib,json,wave,html
S=Path(__file__).resolve().parent
MANIFEST=S/'reference-library.json'
def load():return json.loads(MANIFEST.read_text())
def catalog():
 return {r['id']:{'id':r['id'],'label':r['speaker_id']+' · '+r['emotion']+' · research reference','path':r['audio']['path'],'sha256':r['audio']['sha256'],'transcript':r['transcript']['text'],'annotation_id':r['id'],'annotation_status':r['review']['status']} for r in load()['references']}
def bindings(model,speaker,emotion,settings):
 refs=catalog();identity=refs[f'esd:{speaker}:neutral'];performance=refs[f'esd:{speaker}:{emotion}']
 if model=='dia' and not settings.get('use_reference',True):return []
 pairs=[('identity',identity),('emotion',performance)] if model=='index' else [('performance',performance)]
 return [{'role':role,'reference_id':r['id'],'path':r['path'],'sha256':r['sha256'],'transcript':r['transcript'],'library_version':load()['version']} for role,r in pairs]
def validate(data,verify_files=True):
 import jsonschema
 jsonschema.validate(data,json.loads((S/'reference-library.schema.json').read_text()))
 ids=set()
 for r in data['references']:
  if r['id'] in ids:raise ValueError('Duplicate reference ID')
  ids.add(r['id'])
  if r['id']!=f"esd:{r['speaker_id']}:{r['emotion']}":raise ValueError('Reference identity mismatch')
  if verify_files:
   for a in [r['audio'],r['original_audio'],r['source_audio']]:
    p=Path(a['path'])
    if hashlib.sha256(p.read_bytes()).hexdigest()!=a['sha256']:raise ValueError('Audio integrity mismatch: '+r['id'])
 return True
def summary(speaker):
 data=load();rows=[]
 for r in data['references']:
  if r['speaker_id']!=speaker:continue
  rows.append('<tr><td>'+html.escape(r['emotion'])+'</td><td>'+str(round(r['audio']['duration_seconds'],2))+' s</td><td>Dataset label; intensity unannotated</td><td>'+html.escape(r['review']['status'])+'</td></tr>')
 return '<details><summary>Reference library · speaker '+html.escape(speaker)+' · annotation status</summary><p>One canonical library across all four models. Research use; commercial permission is not established. Labels describe source categories, not verified output emotions.</p><table style="width:100%;text-align:left"><tr><th>Emotion</th><th>Length</th><th>Annotation</th><th>Review</th></tr>'+''.join(rows)+'</table><p>Transcript is inherited from the dataset and has not been independently verified. Intensity, intent, emphasis and word timings remain unannotated. Enhanced clips retain links to their original recordings and processing history. IndexTTS uses neutral identity plus the chosen emotion; other engines use the chosen performance, unless Dia reference continuation is off.</p></details>'

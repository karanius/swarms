"""Local diagnostic: ASR exact-word check, not a substitute for listening."""
import json,re,sys
from pathlib import Path
from faster_whisper import WhisperModel
S=Path(__file__).resolve().parent
model=WhisperModel('/Users/x/.local/share/swarms/paper16-asr/tiny.en',device='cpu',compute_type='int8',local_files_only=True)
def words(x):return re.findall(r"[a-z]+",re.sub(r"\[S[12]\]", "", x).lower())
records=[next(r for r in json.loads((S/'take-library.json').read_text())['records'] if r['model']=='dia')]
if (S/'dia-no-reference-result.json').exists():records.append(json.loads((S/'dia-no-reference-result.json').read_text()))
for arg in sys.argv[1:]:records.append(json.loads(Path(arg).read_text()))
results=[]
for r in records:
 segments,info=model.transcribe(r['path'],language='en',beam_size=5,condition_on_previous_text=False,vad_filter=False)
 text=' '.join(s.text for s in segments).strip();expected=r['text'];item={'id':r['id'],'path':r['path'],'expected':expected,'transcript':text,'exact_words':words(expected)==words(text)};results.append(item);print(json.dumps(item),flush=True)
(S/'dia-word-check.json').write_text(json.dumps(results,indent=2))

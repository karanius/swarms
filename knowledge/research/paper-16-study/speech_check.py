"""Offline English word-check diagnostic; no text prompt or forced alignment."""
import sys,json,re
from pathlib import Path
from faster_whisper import WhisperModel
p=Path(sys.argv[1]);r=json.loads(p.read_text());model=WhisperModel('/Users/x/.local/share/swarms/paper16-asr/tiny.en',device='cpu',compute_type='int8',local_files_only=True)
segments,_=model.transcribe(sys.argv[2],language='en',beam_size=5,condition_on_previous_text=False,vad_filter=False)
transcript=' '.join(s.text for s in segments).strip()
def words(t):return re.findall('[a-z]+',re.sub(r'\[S[12]\]','',t).lower())
result={'transcript':transcript,'expected':r['text'],'exact_words':words(transcript)==words(r['text']),'method':'Offline Faster-Whisper tiny.en, fixed English, beam 5, no VAD or text prompt','limitation':'ASR is fallible; exact words do not validate emotion or voice identity'}
(p.parent/'word-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

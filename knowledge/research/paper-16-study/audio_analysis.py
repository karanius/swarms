"""One React waveform/analysis renderer shared by every Paper 16 player."""
from pathlib import Path
import hashlib,html,json
from urllib.parse import quote
from IPython.display import HTML

def audio_panel(filename,label='Recording',autoplay=False,role='generated',transcript='',compact=False):
    path=Path(filename)
    # Embed precisely these bytes: no stale filename cache or raw/listening mix-up.
    data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
    media_dir=Path(__file__).resolve().parents[1]/'notebooks'/'paper-16-audio'
    media_dir.mkdir(exist_ok=True);cached=media_dir/('playback-'+digest+'.wav')
    if not cached.exists():cached.write_bytes(data)
    url='/research-jupyter/files/paper-16-audio/'+cached.name
    payload=quote(json.dumps({'url':url,'label':label,'role':role,'transcript':transcript,'compact':compact}),safe='')
    return HTML('<iframe title="'+html.escape(label+' waveform and analysis',quote=True)+'" src="/paper16-analysis/index.html#'+payload+'" style="width:100%;height:'+('100' if compact else '520')+'px;border:0" loading="lazy"></iframe>')

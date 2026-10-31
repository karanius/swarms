"""Lossless-content migration of Research prose and embedded notebooks to native .ipynb.
Never overwrites an existing target. Keeps the source collection and code notebooks.
"""
from pathlib import Path
import base64,copy,hashlib,json,re,shutil
import nbformat
import subprocess,os,sys
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'knowledge/research/papers.json'
DEST=ROOT/'knowledge/research/notebooks'
ARCHIVE=ROOT/'knowledge/research/notebook-migration'
TITLES={
 '8c8e315d-55c9-4262-8a6d-b884ad2e06cb':'Paper 1 - From Components to Instances',
 '8d975b9f-7f46-42f5-8366-093a1894bbce':'Paper 2 - Boundary Resolution',
 '8b72d1b8-2f32-4968-8b7f-c33b9e6c3eca':'Paper 3 - Iterative Development of Boundary Resolution',
}
def text(parts):
 if isinstance(parts,str):return parts
 result=''
 for x in parts or []:
  if x.get('type')=='link':result+='['+text(x.get('content',[]))+']('+x['href']+')';continue
  s=x.get('text','');style=x.get('styles',{})
  if style.get('code'):s='`'+s+'`'
  if style.get('bold'):s='**'+s+'**'
  if style.get('italic'):s='*'+s+'*'
  if style.get('strike'):s='~~'+s+'~~'
  result+=s
 return result

def rasterize_svg(image):
 env=dict(os.environ)
 if sys.platform=='darwin':env['DYLD_FALLBACK_LIBRARY_PATH']='/opt/homebrew/lib:'+env.get('DYLD_FALLBACK_LIBRARY_PATH','')
 return subprocess.run([sys.executable,'-c','import cairosvg,sys;sys.stdout.buffer.write(cairosvg.svg2png(url=sys.argv[1],scale=2))',str(image)],env=env,check=True,capture_output=True).stdout

def migrate():
 DEST.mkdir(parents=True,exist_ok=True);ARCHIVE.mkdir(parents=True,exist_ok=True)
 raw=SOURCE.read_bytes();backup=ARCHIVE/'original-papers.json'
 if not backup.exists():backup.write_bytes(raw)
 collection=json.loads(raw);manifest=[]
 for paper in collection['papers']:
  filename=TITLES.get(paper['id'],re.sub(r'[^\w -]','',paper['title']))+'.ipynb';target=DEST/filename
  if target.exists():print('Preserved existing notebook:',filename);continue
  cells=[];section=['# '+paper['title']];attachments={};embedded=[]
  def flush():
   nonlocal section,attachments
   if section:
    cell=nbformat.v4.new_markdown_cell('\n\n'.join(section));
    if attachments:cell['attachments']=attachments
    cells.append(cell)
   section=[];attachments={}
  def convert(b):
   nonlocal section,attachments
   kind=b['type'];content=b.get('content');props=b.get('props',{})
   if kind=='heading':
    flush();section.append('#'*min(6,props.get('level',2))+' '+text(content))
   elif kind=='paragraph':
    if text(content):section.append(text(content))
   elif kind=='table':
    rows=[[text(c.get('content',[])) if isinstance(c,dict) else text(c) for c in r['cells']] for r in content['rows']]
    if rows:
     def row(r):return '| '+' | '.join(v.replace('|','\\|').replace('\n','<br>') for v in r)+' |'
     section.append('\n'.join([row(rows[0]),row(['---']*len(rows[0]))]+[row(r) for r in rows[1:]]))
   elif kind=='image':
    url=props['url'];name=url.rsplit('/',1)[-1]
    if not re.fullmatch(r'[a-zA-Z0-9_.-]+',name):raise ValueError('Unsafe image reference')
    image=ROOT/'frontend/public/research-figures/paper-2'/name
    if not image.is_file():raise ValueError('Image not available locally: '+name)
    data=rasterize_svg(image) if name.endswith('.svg') else image.read_bytes()
    name=Path(name).stem+'.png'
    attachments[name]={'image/png':base64.b64encode(data).decode()}
    section.append('!['+props.get('caption',name)+'](attachment:'+name+')')
    if props.get('caption'):section.append('*'+props['caption']+'*')
   elif kind=='researchNotebook':
    flush();name=props['paperId']+'--'+props['notebookId']+'.ipynb';src=DEST/name
    if not src.exists():src=ARCHIVE/'embedded-notebooks'/name
    old=nbformat.read(src,as_version=4);cells.extend(copy.deepcopy(old.cells));embedded.append(name)
   else:raise ValueError('Unmapped Research block: '+kind)
   for child in b.get('children',[]):convert(child)
  for b in paper['content']:convert(b)
  flush()
  notebook=nbformat.v4.new_notebook(cells=cells,metadata={'kernelspec':{'name':'research-python','display_name':'Research Python','language':'python'},'language_info':{'name':'python'},'research':{'paper_id':paper['id'],'title':paper['title'],'source':'papers.json','source_updated_at':paper['updatedAt'],'migration':'native-notebook-v1'}})
  nbformat.validate(notebook);nbformat.write(notebook,target)
  for name in embedded:
   folder=ARCHIVE/'embedded-notebooks';folder.mkdir(exist_ok=True);src=DEST/name
   if src.exists() and not (folder/name).exists():shutil.move(src,folder/name)
  manifest.append({'paper_id':paper['id'],'title':paper['title'],'notebook':filename,'source_blocks':len(paper['content']),'notebook_cells':len(cells),'embedded_sources':embedded,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 if manifest:(ARCHIVE/'manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'papers':manifest},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':migrate()

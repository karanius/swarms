"""Source-grounded hybrid retrieval. Never imports or executes archived component code."""
from pathlib import Path
import collections, hashlib, html, json, math, re, sqlite3, time
import numpy as np
import requests
from urllib.parse import urlsplit

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
CORPUS = ROOT / 'knowledge/research/paper-6-corpus'
RUNTIME = D / '.runtime'
MODEL = 'nomic-embed-text:latest'
STOP = set('a an the and or to of for with in on is are be can could would should find search show give get me us our we i want need pieces piece relevant reusable build building create instance instances that these this how what which does do from through using use help please allow allows into it them any some'.split())
FACETS = {
 'audience': {'query': ['audience','customer','viewer','listening','feedback'], 'expand': 'youtube comments sentiment social listening customer feedback', 'evidence': ['comment','sentiment','listening','feedback','audience']},
 'competitors': {'query': ['competitor','competition','pricing','market research'], 'expand': 'market research company pricing plans features comparison', 'evidence': ['competitor','pricing','cheapestplan','pricingtiers','market research','company']},
 'attention': {'query': ['trend','trending','attention','viral','popular'], 'expand': 'trends social media youtube search research', 'evidence': ['trend','social media','youtube','social listening']},
 'monetization': {'query': ['monetization','monetisation','revenue','profit','money','earn','affiliate'], 'expand': 'creator monetization revenue affiliate rpm cpm advertising earnings', 'evidence': ['monetiz','monetis','affiliate','rpm','cpm','ad revenue']},
 'research': {'query': ['research','investigate','evidence'], 'expand': 'research search sources web structured report', 'evidence': ['research','search','sources']},
}
SECRET = re.compile(r'api[_ -]?key|password|credential|client[_ -]?secret|access[_ -]?token|auth[_ -]?token', re.I)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',',':')).encode()).hexdigest()

def clean(value, limit=1800):
    text = re.sub(r'\s+', ' ', str(value or '')).strip()
    text = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{12,}|AIza[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{15,})\b', '[REDACTED]', text)
    text = re.sub(r'(?i)(api[_ -]?key|password|access[_ -]?token|client[_ -]?secret)\s*[:=]\s*[\"\']?[^\s,;\"\']+', r'\1=[REDACTED]', text)
    return text[:limit]

def tokens(text):
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if len(t)>1 and t not in STOP]

def requested_facets(query):
    q=query.lower()
    return [name for name, f in FACETS.items() if any(word in q for word in f['query'])]

def provenance(a):
    return {k:a.get(k) for k in ('sourceUrl','repository','revision','sourcePath','file','sha256','collector')} | {'license':a.get('licenseAssessment',{}).get('label','unknown'),'license_review_required':True}

def resolve_pointer(obj, pointer):
    for part in pointer.removeprefix('$').strip('/').split('/'):
        if part: obj=obj[int(part)] if isinstance(obj,list) else obj[part.replace('~1','/').replace('~0','~')]
    return obj

def node_record(node):
    data=node.get('data',{}); definition=data.get('node',{})
    typ=str(data.get('type') or node.get('type') or 'unknown')
    template=definition.get('template',{})
    inputs=[]; requirements=[]; texts=[]
    for key, field in template.items():
        if not isinstance(field,dict) or key=='code' or key.startswith('_'):continue
        secret=bool(field.get('password')) or bool(SECRET.search(key))
        inputs.append({'name':key,'required':bool(field.get('required',False)),'types':field.get('input_types',[]),'field_type':field.get('type'),'secret_binding':secret})
        if field.get('required') or secret:requirements.append({'name':key,'kind':'credential' if secret else 'required_field','status':'binding requires review; saved values intentionally not indexed'})
        if not secret and key in ('system_prompt','instructions','template','prompt','output_schema','schema','text'):
            value=field.get('value')
            if value and not (isinstance(value,str) and value.startswith('You are a Langflow Agent')):texts.append(clean(json.dumps(value) if not isinstance(value,str) else value,800))
    outputs=[{'name':o.get('name'),'types':o.get('types',[]),'method':o.get('method')} for o in definition.get('outputs',[]) if isinstance(o,dict)]
    metadata=definition.get('metadata',{}) or {}
    deps=metadata.get('dependencies',{})
    if isinstance(deps,dict):deps=deps.get('dependencies',[])
    deps=[{'name':d.get('name'),'version':d.get('version')} for d in deps if isinstance(d,dict)] if isinstance(deps,list) else []
    return {'node_id':str(node.get('id') or data.get('id')),'type':typ,'display_name':clean(definition.get('display_name') or typ,180),'description':clean(definition.get('description'),500),'inputs':inputs,'outputs':outputs,'requirements':requirements,'dependencies':deps,'declared_class':metadata.get('module'),'archived_code_hash':metadata.get('code_hash'),'purpose_text':' '.join(texts)[:2400]}

def edge_record(edge):
    data=edge.get('data',{}) or {}; sh=data.get('sourceHandle',{});th=data.get('targetHandle',{})
    sh=sh if isinstance(sh,dict) else {};th=th if isinstance(th,dict) else {}
    return {'source':str(edge.get('source')),'target':str(edge.get('target')),'source_port':sh.get('name'),'target_port':th.get('fieldName'),'output_types':sh.get('output_types',[]),'input_types':th.get('inputTypes',[]),'port_details_resolved':bool(sh.get('name') and th.get('fieldName'))}

def extract_documents():
    raw=(CORPUS/'index.json').read_bytes(); index=json.loads(raw)
    by_hash=collections.defaultdict(list)
    for a in index['artifacts']:
        if a.get('miningEligible') and a.get('graphFormat')=='langflow' and not a.get('fixture'):by_hash[a['sha256']].append(a)
    documents=[];components={};failures=[];graphs_seen=0
    for sha,origins in sorted(by_hash.items()):
        origins.sort(key=lambda a:(a.get('collector')!='official',a['file']))
        a=origins[0]; path=(CORPUS/a['file']).resolve()
        if not path.is_relative_to(CORPUS.resolve()):failures.append({'file':a['file'],'reason':'unsafe path'});continue
        try:
            content=path.read_bytes()
            if hashlib.sha256(content).hexdigest()!=sha:raise ValueError('source hash mismatch')
            obj=json.loads(content)
            for gi,graph_meta in enumerate(a['graphs']):
                if graph_meta.get('format')!='langflow':continue
                graph=resolve_pointer(obj,graph_meta['pointer']);graphs_seen+=1
                nodes=[node_record(n) for n in graph.get('nodes',[]) if isinstance(n,dict)]
                nodes=[n for n in nodes if n['type'].lower() not in ('note','sticky note')]
                ids={n['node_id'] for n in nodes};edges=[edge_record(e) for e in graph.get('edges',[]) if isinstance(e,dict)]
                valid_edges=[e for e in edges if e['source'] in ids and e['target'] in ids]
                name=clean(obj.get('name') or Path(a['sourcePath']).stem,200)
                description=clean(obj.get('description'),1200)
                src={'origins':[provenance(o) for o in origins],'file':a['file'],'sha256':sha,'graph_pointer':graph_meta['pointer']}
                requirements=[{'component':n['type'],**r} for n in nodes for r in n['requirements']]
                base={'sources':src,'component_types':sorted({n['type'] for n in nodes}),'requirements':requirements,'runtime_status':'archived definition; execution and current component compatibility unverified','saved_operational_values_indexed':False,'selected_redacted_prompt_schema_text_indexed':True,'structural_warnings':graph_meta.get('structuralIssues',{}),'unresolved_edges':len(edges)-len(valid_edges)}
                purpose=' '.join(n['purpose_text'] for n in nodes)[:5000]
                doc={**base,'id':f'template:{sha}:{gi}','kind':'template','title':name,'description':description,'purpose_text':purpose,'nodes':nodes,'edges':valid_edges,'boundary':{'inputs':[],'outputs':[],'note':'Full workflow graph; reusable composite boundary not asserted'}}
                documents.append(doc)
                for node in nodes:
                    signature=digest({k:node[k] for k in ('type','description','inputs','outputs','dependencies','declared_class','archived_code_hash')})
                    if signature not in components:
                        components[signature]={**base,'id':'component:'+signature,'kind':'component','title':node['display_name'],'description':node['description'],'purpose_text':'','component_types':[node['type']],'nodes':[node],'edges':[],'requirements':[{'component':node['type'],**r} for r in node['requirements']],'occurrence_refs':[],'boundary':{'inputs':node['inputs'],'outputs':node['outputs']}}
                    components[signature]['occurrence_refs'].append({'template_id':doc['id'],'node_id':node['node_id'],'source':provenance(a),'graph_pointer':graph_meta['pointer']})
                neighbors=collections.defaultdict(set)
                for edge in valid_edges:neighbors[edge['source']].add(edge['target']);neighbors[edge['target']].add(edge['source'])
                used=set()
                for anchor in nodes:
                    if anchor['type'] in ('ChatInput','ChatOutput','TextInput','TextOutput','Prompt','ParserComponent'):continue
                    selected={anchor['node_id']}
                    for other in sorted(neighbors[anchor['node_id']]):
                        if len(selected)<4:selected.add(other)
                    if len(selected)<2:continue
                    key=tuple(sorted(selected))
                    if key in used:continue
                    used.add(key);members=[n for n in nodes if n['node_id'] in selected]
                    inner=[e for e in valid_edges if e['source'] in selected and e['target'] in selected]
                    inbound=[e for e in valid_edges if e['source'] not in selected and e['target'] in selected]
                    outbound=[e for e in valid_edges if e['source'] in selected and e['target'] not in selected]
                    label=' + '.join(sorted({n['display_name'] for n in members}))
                    documents.append({**base,'id':'group:'+digest([doc['id'],key]),'kind':'connected_group','title':label+' — '+name,'description':description,'purpose_text':' '.join(n['purpose_text'] for n in members)[:2400],'component_types':sorted({n['type'] for n in members}),'nodes':members,'edges':inner,'requirements':[{'component':n['type'],**r} for n in members for r in n['requirements']],'parent_template':doc['id'],'boundary':{'inputs':inbound,'outputs':outbound,'note':'Observed connected subset, not a validated composite. Required fields may also need exposure.'}})
        except Exception as exc:failures.append({'file':a['file'],'reason':str(exc)})
    documents.extend(components.values())
    for doc in documents:
        for n in doc['nodes']:
            # Never retain saved input values or executable code in the searchable representation.
            n.pop('purpose_text',None)
        doc['search_text']=clean(' '.join([doc['title'],doc['description'],' '.join(doc['component_types']),doc.get('purpose_text','')]),7000)
        doc['capability_evidence']={name:[word for word in f['evidence'] if word in doc['search_text'].lower()] for name,f in FACETS.items()}
        # Marketing taglines or a generic sales KPI do not establish creator monetization capability.
        purpose=(doc.get('purpose_text','')+' '+doc['title']+' '+' '.join(doc['component_types'])).lower()
        money=[]
        for word in ['monetiz','monetis','affiliate','ad revenue','advertising revenue','youtube analytics','youtubeanalytics']:
            if word in purpose:money.append(word)
        for acronym in ['rpm','cpm']:
            if re.search(r'\b'+acronym+r'\b',purpose):money.append(acronym)
        if 'revenue' in purpose and re.search(r'youtube|creator|channel|advertising',purpose):money.append('revenue with creator/channel context')
        doc['capability_evidence']['monetization']=money
    stats={'corpus_index_sha256':hashlib.sha256(raw).hexdigest(),'corpus_counts':index['counts'],'unique_eligible_contents':len(by_hash),'graphs_indexed':graphs_seen,'documents':len(documents),'kinds':dict(collections.Counter(d['kind'] for d in documents)),'failures':failures,'exclusions':'Non-Langflow, fixtures and exact-byte duplicate copies excluded; all origins of included content retained.'}
    return documents,stats

def embed(texts,query=False):
    prefix='search_query: ' if query else 'search_document: '
    response=requests.post('http://127.0.0.1:11434/api/embed',json={'model':MODEL,'input':[prefix+t[:2400] for t in texts],'truncate':True},timeout=(5,120))
    response.raise_for_status();data=response.json()
    values=np.asarray(data['embeddings'],dtype=np.float32)
    if values.ndim!=2 or values.shape[0]!=len(texts) or not np.isfinite(values).all():raise ValueError('Invalid local embedding result')
    norm=np.linalg.norm(values,axis=1,keepdims=True)
    if (norm<=0).any():raise ValueError('Zero embedding')
    return values/norm

def build_index(semantic=True):
    RUNTIME.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(RUNTIME/'search.sqlite3')
    db.executescript('CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY,vector BLOB); CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT);')
    documents,stats=extract_documents()
    tags=requests.get('http://127.0.0.1:11434/api/tags',timeout=10).json()['models'] if semantic else []
    model_info=next((m for m in tags if m['name']==MODEL),None)
    if semantic and not model_info:raise ValueError('Existing local embedding model required; no automatic download')
    binding={'model':MODEL,'digest':model_info['digest'],'dimensions':768} if semantic else None
    vectors=[];missing=[]
    if semantic:
        for i,doc in enumerate(documents):
            key=digest([binding,doc['search_text'][:2400]]);doc['embedding_key']=key
            row=db.execute('SELECT vector FROM cache WHERE key=?',(key,)).fetchone()
            vectors.append(np.frombuffer(row[0],dtype=np.float32).copy() if row else None)
            if not row:missing.append(i)
        for start in range(0,len(missing),24):
            positions=missing[start:start+24];batch=embed([documents[i]['search_text'] for i in positions])
            for i,vec in zip(positions,batch):vectors[i]=vec;db.execute('INSERT OR REPLACE INTO cache VALUES(?,?)',(documents[i]['embedding_key'],vec.tobytes()))
            db.commit()
            if start%240==0:print(f'Local embeddings: {min(start+24,len(missing))}/{len(missing)} new records',flush=True)
        matrix=np.stack(vectors);binding['dimensions']=matrix.shape[1];np.save(RUNTIME/'vectors.npy',matrix)
    db.executescript('DROP TABLE IF EXISTS docs; DROP TABLE IF EXISTS lexical; CREATE TABLE docs(id TEXT PRIMARY KEY,kind TEXT,title TEXT,body TEXT); CREATE VIRTUAL TABLE lexical USING fts5(id UNINDEXED,title,description,components,purpose);')
    for doc in documents:
        db.execute('INSERT INTO docs VALUES(?,?,?,?)',(doc['id'],doc['kind'],doc['title'],json.dumps(doc)))
        db.execute('INSERT INTO lexical VALUES(?,?,?,?,?)',(doc['id'],doc['title'],doc['description'],' '.join(doc['component_types']),doc.get('purpose_text','')))
    stats['embedding_binding']=binding;stats['generated_at']=time.time()
    db.execute('INSERT OR REPLACE INTO metadata VALUES(?,?)',('stats',json.dumps(stats)));db.commit();db.close()
    (D/'INDEX-REPORT.json').write_text(json.dumps(stats,indent=2)+'\n')
    return stats

class CorpusSearch:
    def __init__(self):
        self.db=sqlite3.connect(RUNTIME/'search.sqlite3');self.db.row_factory=sqlite3.Row
        self.stats=json.loads(self.db.execute("SELECT value FROM metadata WHERE key='stats'").fetchone()[0])
        self.docs=[json.loads(r['body']) for r in self.db.execute('SELECT body FROM docs ORDER BY rowid')]
        self.by_id={d['id']:d for d in self.docs};self.positions={d['id']:i for i,d in enumerate(self.docs)}
        self.vectors=np.load(RUNTIME/'vectors.npy',mmap_mode='r') if self.stats['embedding_binding'] else None
        self._query_cache={}
        self.corpus_current=hashlib.sha256((CORPUS/'index.json').read_bytes()).hexdigest()==self.stats['corpus_index_sha256']
        self.embedding_current=False
        if self.vectors is not None:
            try:
                installed=requests.get('http://127.0.0.1:11434/api/tags',timeout=3).json()['models']
                self.embedding_current=any(m['name']==MODEL and m['digest']==self.stats['embedding_binding']['digest'] for m in installed)
            except Exception:pass
    def answer(self,question,k=3):
        facets=requested_facets(question)
        if len(facets)<2:
            return {'question':question,'sections':{'requested capability':self.search(question,k=k)},'scope':'Retrieval only; no instance assembled or source template executed'}
        sections={}
        for name in facets:
            sections[name]=self.search(name+' '+FACETS[name]['expand'],k=k)
        return {'question':question,'sections':sections,'scope':'Capability facets are an explicit small ontology, not an unrestricted intent parser. Each section needs inspection; matches do not prove an assembled instance works.'}
    def search(self,query,k=6,kind=None,semantic=True):
        if not isinstance(query,str) or not 3<=len(query.strip())<=1200:raise ValueError('Enter a question between 3 and 1200 characters')
        if not isinstance(k,int) or not 1<=k<=30:raise ValueError('Result limit must be 1–30')
        if kind not in (None,'template','component','connected_group'):raise ValueError('Unknown result kind')
        start=time.monotonic();facets=requested_facets(query)
        terms=list(dict.fromkeys(tokens(query)+' '.join(FACETS[f]['expand'] for f in facets).split()))[:50]
        if not terms:return {'query':query,'results':[],'gaps':['No searchable capability terms'],'requested_facets':facets}
        expression=' OR '.join('"'+t.replace('"','')+'"' for t in terms)
        rows=self.db.execute('SELECT id,bm25(lexical,0,5,3,2,1) AS rank FROM lexical WHERE lexical MATCH ? ORDER BY rank LIMIT 150',(expression,)).fetchall()
        lex={r['id']:i+1 for i,r in enumerate(rows)};scores={ident:1/(35+rank) for ident,rank in lex.items()};semantic_status='disabled'
        similarities=None
        if semantic and self.vectors is not None and self.embedding_current:
            try:
                if query not in self._query_cache:self._query_cache[query]=embed([query],query=True)[0]
                similarities=self.vectors@self._query_cache[query];order=np.argsort(-similarities)[:150]
                for rank,i in enumerate(order,1):scores[self.docs[i]['id']]=scores.get(self.docs[i]['id'],0)+0.8/(35+rank)
                semantic_status='local embeddings active'
            except Exception:semantic_status='local embeddings unavailable; explicit lexical fallback'
        elif semantic:semantic_status='embedding service/model binding unavailable; explicit lexical fallback'
        hits=[];query_terms=set(tokens(query));expanded_terms=set(terms)
        needs_comment_collector=bool(re.search(r'comment',query,re.I) and re.search(r'collect|retrieve|fetch|extract|get\b',query,re.I))
        needs_transcript=bool(re.search(r'transcript|spoken words',query,re.I))
        for ident,score in scores.items():
            doc=self.by_id[ident]
            if kind and doc['kind']!=kind:continue
            types=' '.join(doc['component_types']).lower()
            # A parent workflow description cannot grant a subset a tool that sits outside it.
            if needs_comment_collector and not re.search(r'comment|youtubeapi',types):continue
            if needs_transcript and not re.search(r'transcript|transcription|whisper',types):continue
            doc_terms=set(tokens(doc['search_text']));direct=sorted(query_terms&doc_terms);expanded=sorted(expanded_terms&doc_terms)
            covered=[f for f in facets if doc['capability_evidence'].get(f)]
            # Do not turn a nearest-neighbor similarity into evidence for an unknown capability.
            if not direct and not covered:continue
            if facets and not covered:continue
            score*=1+0.2*len(covered)+min(len(direct),5)*0.07
            if doc['kind']=='component' and doc['component_types'][0] in ('Agent','ChatInput','ChatOutput','Prompt','TextInput','TextOutput'):score*=0.65
            result={k:doc.get(k) for k in ('id','kind','title','description','component_types','requirements','dependencies','sources','nodes','edges','boundary','structural_warnings','unresolved_edges','runtime_status','parent_template','occurrence_refs')}
            result.update(rank_score=round(score,6),semantic_similarity=round(float(similarities[self.positions[ident]]),4) if similarities is not None else None,matched_terms=direct,expanded_terms=expanded[:15],capability_matches=covered,match_evidence={f:doc['capability_evidence'][f] for f in covered},fit='Candidate for inspection; purpose, boundary, dependencies and execution require validation')
            hits.append(result)
        hits.sort(key=lambda r:(-r['rank_score'],r['id']))
        # Keep near-identical archived versions from occupying every result slot.
        # They remain individually inspectable; this is display diversification, not proof of duplication.
        selected=[];families={}
        for hit in hits:
            by_node={n['node_id']:n['type'] for n in hit['nodes']}
            wiring=sorted((by_node.get(e['source']),e['source_port'] or '',by_node.get(e['target']),e['target_port'] or '') for e in hit['edges'])
            key=digest([hit['kind'],hit['title'].lower().split(' — ')[0],hit['component_types'],wiring])
            if key in families:
                families[key]['similar_variant_ids'].append(hit['id'])
            elif len(selected)<k:
                hit['similar_variant_ids']=[];families[key]=hit;selected.append(hit)
        stale=[r['id'] for r in selected if not self.verify_source(r['id'])]
        selected=[r for r in selected if r['id'] not in stale]
        covered={f for r in selected for f in r['capability_matches']}
        gaps=[f+' has no direct capability evidence in the returned matches' for f in facets if f not in covered]
        if stale:gaps.append('Changed/unavailable original files were withheld: rebuild and review the index.')
        if not self.corpus_current:gaps.append('The collection index changed since this search snapshot; new or changed material requires rebuilding.')
        if 'monetization' in facets:gaps.append('Company pricing or financial analysis is not proof of creator revenue; audience/revenue data and cost assumptions still need a supported connector and evaluation.')
        if re.search(r'\bmy\b|private|actual earnings',query,re.I):gaps.append('Search reads archived definitions only. It has no access to your accounts, private audience data or actual earnings.')
        if not selected:gaps.append('No source-grounded match passed the evidence screen; do not infer the capability exists.')
        return {'query':query,'results':selected,'requested_facets':facets,'gaps':gaps,'semantic_status':semantic_status,'seconds':round(time.monotonic()-start,4),'score_meaning':'Retrieval ranking only, not probability of relevance, compatibility or business success','scope':'Archived pieces only; no instance assembled or template executed'}
    def filename_search(self,query,k=6):
        terms=set(tokens(query));ranked=[]
        for doc in self.docs:
            if doc['kind']!='template':continue
            overlap=len(terms&set(tokens(Path(doc['sources']['file']).stem)))
            if overlap:ranked.append((overlap,doc['id'],doc))
        return [r[2] for r in sorted(ranked,key=lambda x:(-x[0],x[1]))[:k]]
    def inspect(self,identifier):return json.loads(json.dumps(self.by_id[identifier]))
    def verify_source(self,identifier):
        doc=self.by_id[identifier];path=(CORPUS/doc['sources']['file']).resolve()
        try:return path.is_relative_to(CORPUS.resolve()) and hashlib.sha256(path.read_bytes()).hexdigest()==doc['sources']['sha256']
        except OSError:return False

def render_results(answer):
    """Safe notebook HTML: every archived title and string is escaped."""
    from IPython.display import display,HTML
    esc=html.escape
    pieces=['<h3>'+esc(answer['query'])+'</h3><p>'+esc(answer.get('semantic_status',''))+'</p>']
    for r in answer['results']:
        origin=r['sources']['origins'][0]
        context=('Parent-workflow context, not a claim about this subset: ' if r['kind']=='connected_group' else '')+(r['description'] or 'No original description recorded')
        pieces.append('<hr><h4>'+esc(r['title'])+'</h4><p>'+esc(r['kind'])+' · '+esc(context)+'</p>')
        pieces.append('<p><strong>Components:</strong> '+esc(', '.join(r['component_types']))+'</p><p><strong>Why matched:</strong> '+esc(', '.join(r['matched_terms']))+'; capability evidence '+esc(json.dumps(r['match_evidence']))+'</p>')
        url=origin.get('sourceUrl') or ''
        if urlsplit(url).scheme not in ('http','https'):url=''
        pieces.append('<p><a target="_blank" rel="noopener noreferrer" href="'+esc(url,quote=True)+'">Original source</a> · '+esc(origin.get('license','unknown'))+' (review required)</p>')
        pieces.append('<details><summary>Ports, configuration, dependencies and boundaries</summary><pre>'+esc(json.dumps({'inputs_outputs':[{'type':n['type'],'inputs':n['inputs'],'outputs':n['outputs'],'dependencies':n['dependencies']} for n in r['nodes']],'requirements':r['requirements'],'observed_edges':r['edges'],'boundary':r['boundary'],'warnings':r['structural_warnings'],'unresolved_edges':r['unresolved_edges']},indent=2))+'</pre></details><p>'+esc(r['fit'])+'</p>')
    pieces.append('<p><strong>Unresolved:</strong> '+esc('; '.join(answer['gaps']) or 'No requested facet absent from these matches; compatibility and usefulness remain unverified.')+'</p>')
    display(HTML(''.join(pieces)))

if __name__=='__main__':
    stats=build_index();print(json.dumps({k:v for k,v in stats.items() if k!='corpus_counts'},indent=2))

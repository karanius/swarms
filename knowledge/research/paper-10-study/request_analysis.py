"""Retrieval-only request interpretation and evidence qualification; no build planning."""
import copy,re,time,html,json
from urllib.parse import urlsplit

# Explicit, versioned search vocabulary. Unknown requests remain unknown, never silently 'research'.
CAPS={
 'language_model':('Language-model inference',r'\b(language models?|local llms?|text generation|chat models?)\b','language model inference local Ollama text generation',r'OllamaModel|OpenAIModel|LanguageModel|AnthropicModel|MistralModel|GroqModel',r'language model|text generation'),
 'script_input':('Script input',r'\bscript input\b|\b(text|script) (input|ingestion)\b','text input script input TextInput ChatInput',r'TextInput|ChatInput',r'accept.{0,30}(text|script)'),
 'script_writing':('Script writing',r'\b(script ?writing|write scripts?|generate scripts?|video scripts?)\b','write video script screenplay narration script',r'__no_native_signature__',r'(write|generate|draft).{0,35}(script|screenplay)'),
 'image_generation':('Image generation',r'\bimage (generation|generator|synthesis)\b|\b(text.to.image|generate images?|create images?)\b','image generation text to image diffusion DallE',r'DallE|DALLE|TextToImage|ImageGenerator|StableDiffusion',r'(generat|creat).{0,35}images?|text.to.image|image (generation|synthesis)'),
 'video_generation':('Video generation',r'\bvideo[ -]?(generation|generator|synthesis)\b|\b(text.to.video|generate videos?|create videos?)\b','video generation text to video Veo Heygen',r'VideoGenerator|Heygen|TextToVideo|Runway|Kling',r'generat.{0,30}videos?|text.to.video'),
 'narration':('Narration / speech synthesis',r'\b(narration|voiceover|voice.over|text.to.speech|speech synthesis|speech generation)\b','speech synthesis text to speech narration ElevenLabs audio generator',r'ElevenLabs|MultiSpeakerAudioGenerator|TextToSpeech|\bTTS\b',r'text.to.speech|speech synthesis|generat.{0,25}(speech|narration)'),
 'transcription':('Speech transcription',r'\b(transcrib\w*|transcription|speech.to.text|speech recognition|spoken words)\b','speech transcription speech to text Whisper AssemblyAI',r'Transcrib|Transcription|Whisper',r'speech.to.text|transcri'),
 'subtitles':('Subtitles / captions',r'\b(subtitles?|captions?|srt|vtt)\b','subtitle captions SRT VTT AssemblyAIGetSubtitles',r'GetSubtitles|Subtitle|CaptionGenerator',r'(generat|export|creat|convert).{0,35}(subtitle|caption|srt|vtt)'),
 'video_assembly':('Final video assembly',r'\b(video (assembly|editing|rendering|composition)|assemble videos?|edit videos?|final video assembly|ffmpeg|moviepy)\b','video assembly rendering concatenate clips FFmpeg MoviePy',r'FFmpeg|MoviePy|VideoAssembler|VideoEditor|VideoRenderer',r'(assembl|concatenat|render|stitch|mux).{0,35}(video|clip)|ffmpeg|moviepy'),
 'audience':('Audience feedback',r'\b(audience|viewer|customer)\b.{0,35}\b(feedback|reaction|comment|sentiment)|\b(viewer comments?|social listening|voice of customer)\b','audience feedback viewer comments sentiment YouTubeCommentsComponent',r'Comments|YoutubeAPI|RedditAPI|Sentiment',r'customer feedback|audience sentiment|viewer comments'),
 'competitors':('Competitor research',r'\b(competitors?|competition|pricing|market research|pricing tiers|free trials?)\b','competitor company pricing tiers market research',r'__no_native_signature__',r'pricing|competitor|target industries|cheapestPlan'),
 'attention':('Trends and attention',r'\b(trend(?:s|ing)?|viral|audience attention|attention grabbing)\b','social media trending attention search',r'__no_native_signature__',r'\btrend(?:s|ing)?\b|social listening'),
 'monetization':('Monetization evidence',r'\b(moneti[sz]\w*|revenue|profit\w*|money|earnings?|affiliate|rpm|cpm)\b','creator monetization revenue affiliate RPM CPM',r'YouTubeAnalytics|AdSense|Affiliate',r'\b(moneti[sz]\w*|affiliate|rpm|cpm)\b'),
 'web_search':('Web search',r'\b(web search|search (the )?(current )?web|search engines?|search for sources)\b','web search evidence sources Tavily UnifiedWebSearch',r'Search|Serp|Tavily',r'web search'),
 'page_fetch':('Read web pages',r'\b(webpages?|web pages?|fetch urls?|read (a |the )?(webpages?|web pages?)|scrap\w*)\b','read webpage URL content scrape',r'URLComponent|WebBaseLoader|Scrape|Firecrawl',r'(fetch|read|scrap).{0,20}(url|page|website)'),
 'document_chunks':('Document chunking',r'\b(chunk\w*|split.{0,20}(document|text))\b','split document text chunks RecursiveCharacterTextSplitter SplitText',r'SplitText|TextSplitter',r'split.{0,25}(text|document)'),
 'structured_output':('Typed structured output',r'\b(typed json|typed.{0,15}(json|fields)|structured (output|json)|json fields)\b','typed JSON schema structured output',r'StructuredOutput',r'json schema|typed json'),
 'sql':('Relational data queries',r'\b(sql|relational tables?|query.{0,20}database)\b','SQL database query relational tables',r'SQL|Database',r'\bsql\b'),
 'vector_retrieval':('Vector retrieval',r'\b(vector (search|retrieval|database)|semantic retrieval|rag|retrieval.augmented)\b','vector semantic retrieval RAG database embeddings',r'AstraDB|Chroma|FAISS|Qdrant|Pinecone|Retriever',r'vector search|semantic retrieval'),
}
REMOTE=r'Composio|Heygen|ElevenLabs|GoogleVeo|AssemblyAI|Tavily|Serper|SerpAPI|GoogleSearch|Firecrawl|ScrapeGraph|HuggingFaceInferenceAPI|AstraDB|Pinecone'

def interpret(question):
    if not isinstance(question,str) or not 3<=len(question.strip())<=1200:raise ValueError('Enter a question between 3 and 1200 characters')
    # Presentation clauses must not become requested capabilities.
    objective=re.split(r'\b(show each|show (?:their|the) (?:hardware|requirements)|identify anything requiring|report capabilities with|include (?:their |the )?(?:sources|dependencies)|with sources|with evidence)\b',question,flags=re.I)[0]
    matches=[]
    # 'image or video generation' explicitly requests alternatives; no order or wiring is inferred.
    compound=bool(re.search(r'\bimage or video generation\b',objective,re.I))
    for key,(label,pattern,query,types,decl) in CAPS.items():
        m=re.search(pattern,objective,re.I)
        if m and re.search(r'(?:do not|don\x27t|exclude|without|no)\s*$',objective[max(0,m.start()-20):m.start()],re.I):continue
        if m or (compound and key=='image_generation'):matches.append({'id':key,'label':label,'query':query,'request_evidence':m.group(0) if m else 'image or video generation','evidence_kind':'explicit vocabulary match'})
    if not matches:
        cleaned=re.sub(r'\b(find|show|reusable|pieces|capabilities|please)\b',' ',objective,flags=re.I).strip()
        matches=[{'id':'unmapped','label':'Unmapped requested capability','query':cleaned or objective,'request_evidence':objective,'evidence_kind':'unmapped: no domain-specific interpretation is claimed'}]
    else:
        residual=[]
        for clause in re.split(r'[,;.!?]|\band\b|\bplus\b',objective,flags=re.I):
            if any(re.search(v[1],clause,re.I) for v in CAPS.values()):continue
            if re.search(r'\b(do not|don\x27t|exclude|without)\b',clause,re.I):continue
            words=re.findall(r'[a-z]+',clause.lower())
            context=set('find reusable relevant pieces tools capabilities for a an the i we need want system pipeline that runs run locally local on my our mac apple silicon offline only english and to in with'.split())
            remaining=[w for w in words if w not in context]
            if remaining:residual.append(clause.strip())
        if residual:matches.append({'id':'unmapped','label':'Unmapped request clauses','query':' '.join(residual),'request_evidence':'; '.join(residual),'evidence_kind':'Unmapped clauses retained rather than silently dropped.'})
    constraint_text=re.sub(r'\bnot offline\b|\bno need to (?:run locally|be offline)\b','',question,flags=re.I)
    constraints={
      'local_required':bool(re.search(r'local.only|runs? locally|run locally|entirely (?:on|local)|fully local|offline|locally on|\blocal (?:video|image|audio|speech|generation|pipeline|system)',constraint_text,re.I)),
      'apple_silicon':bool(re.search(r'apple silicon|\bM[1-5](?:\s+(?:Max|Pro|Ultra))?\b',question,re.I)),
      'mac':bool(re.search(r'\bmac\b|macos|apple silicon',question,re.I)),
      'no_paid_apis':bool(re.search(r'\b(?:no|without|exclude|avoid)\s+(?:any\s+)?paid (?:apis?|services?)',question,re.I)),
      'offline_required':bool(re.search(r'\boffline\b|without (?:an? )?internet',constraint_text,re.I))}
    return {'capabilities':matches,'constraints':constraints,'alternatives':[['image_generation','video_generation']] if compound else [],'display_requirements':[key for key,pattern in {'hardware':r'hardware|memory|ram','dependencies':r'dependenc','ports':r'inputs|outputs|ports','sources':r'sources|evidence','cost':r'paid|cost|price'}.items() if re.search(pattern,question,re.I)],'limitations':['Versioned vocabulary; arbitrary unknown or ambiguous capabilities remain explicitly unmapped.','No architecture, execution order or build plan inferred.','Runtime and hardware constraints require evidence, not semantic similarity.']}

def endpoint_hosts(doc):
    from search_engine import CORPUS,resolve_pointer
    hosts=set()
    try:
        graph=resolve_pointer(json.loads((CORPUS/doc['sources']['file']).read_text()),doc['sources']['graph_pointer'])
        selected={n['node_id'] for n in doc['nodes']}
        for n in graph['nodes']:
            if str(n.get('id') or n.get('data',{}).get('id')) not in selected:continue
            fields=n.get('data',{}).get('node',{}).get('template',{})
            for key,field in fields.items():
                if key not in ('url','base_url','api_url','endpoint','curl_command','curl','command') or not isinstance(field,dict):continue
                for url in re.findall(r'https?://[^\s\"\x27<>]+',str(field.get('value') or '')):
                    host=urlsplit(url).hostname
                    if host and re.search(r'openai|googleapis|heygen|elevenlabs|replicate|fal\.run|fal\.ai|assemblyai|api-inference\.huggingface',host,re.I):hosts.add(host)
    except (KeyError,ValueError,OSError,TypeError):pass
    return sorted(hosts)

def qualification(doc,capability,constraints):
    key=capability['id'];types=' '.join(doc['component_types'])
    # A connected subset is qualified using only its own definitions/purpose, never its parent's description.
    own=' '.join(n.get('description','') for n in doc['nodes'])+' '+doc.get('purpose_text','')
    if doc['kind']=='template':own=doc['description']+' '+own
    if key=='unmapped':relevance='unknown';basis='No domain-specific relevance rule; text similarity only.'
    elif re.search(CAPS[key][3],types,re.I):relevance='supported';basis='A declared component type within this result matches the requested primitive.'
    elif re.search(CAPS[key][4],own,re.I):relevance='partial';basis='Selected definitions or prompt/schema text mention the capability, but no dedicated primitive is established.'
    else:return None
    remote=sorted({t for t in doc['component_types'] if re.search(REMOTE,t,re.I)}|set(endpoint_hosts(doc)))
    for provider in ['fal.ai','api.openai.com','api.elevenlabs.io','api.heygen.com']:
        if provider in own.lower():remote.append('declared provider: '+provider)
    local_types=sorted({t for t in doc['component_types'] if re.search(r'Ollama|MLX|LlamaCpp|CTransformers',t,re.I)})
    checks={};reasons=[]
    if constraints['local_required'] or constraints['offline_required']:
        checks['local_execution']={'status':'conflict' if remote else 'unknown','evidence':remote or local_types,'reason':'External-service component declared in this result.' if remote else 'Local-capable components do not prove the entire result runs locally; bindings and execution unverified.'}
        reasons.append(checks['local_execution']['reason'])
    if constraints['apple_silicon'] or constraints['mac']:
        checks['mac_hardware']={'status':'unknown','evidence':[], 'reason':'No runtime proof of Mac/Apple Silicon support, memory fit or acceleration is indexed.'};reasons.append(checks['mac_hardware']['reason'])
    if constraints['no_paid_apis']:
        checks['no_paid_apis']={'status':'unknown','evidence':remote,'reason':'An API dependency does not establish its price. No billing/entitlement evidence is indexed.'};reasons.append(checks['no_paid_apis']['reason'])
    overall='partial' if relevance=='supported' and checks else relevance
    return {'status':overall,'relevance_status':relevance,'basis':basis,'constraint_checks':checks,'constraint_conflict':any(c['status']=='conflict' for c in checks.values()),'external_service_components':remote,'local_capable_components':local_types,'missing_evidence':reasons,'meaning':'Supported refers to an archived capability declaration only, never a tested implementation.'}

def answer_request(engine,question,k=3,kind=None):
    intent=interpret(question);sections={};start=time.monotonic()
    if kind not in (None,'template','component','connected_group'):raise ValueError('Unknown result kind')
    if not isinstance(k,int) or not 1<=k<=30:raise ValueError('Result limit must be 1–30')
    for capability in intent['capabilities']:
        raw=engine.search(capability['query'],k=30,kind=kind)
        # Exact declared primitive matches are not allowed to disappear behind generic full-workflow hits.
        if kind in (None,'component') and capability['id'] in CAPS:
            present={r['id'] for r in raw['results']}
            for doc in engine.docs:
                if doc['kind']!='component' or doc['id'] in present or not re.search(CAPS[capability['id']][3],' '.join(doc['component_types']),re.I):continue
                if not engine.verify_source(doc['id']):continue
                item={key:copy.deepcopy(doc.get(key)) for key in ('id','kind','title','description','component_types','requirements','sources','nodes','edges','boundary','structural_warnings','unresolved_edges','runtime_status','parent_template','occurrence_refs')}
                item.update(rank_score=0.0001,matched_terms=[],match_evidence={'declared_primitive_types':doc['component_types']},fit='Declared primitive candidate; current runtime, configuration and hardware fit remain unverified.')
                raw['results'].append(item)
        hits=[]
        for result in raw['results']:
            doc=engine.by_id[result['id']];q=qualification(doc,capability,intent['constraints'])
            if q:
                item=copy.deepcopy(result);item['assessment']=q;hits.append(item)
        hits.sort(key=lambda r:({'supported':0,'partial':1,'unknown':2}.get(r['assessment']['relevance_status'],3),r['assessment']['constraint_conflict'],r['kind']!='component',-r['rank_score']))
        unique=[];component_types_seen=set()
        for hit in hits:
            key=tuple(hit['component_types'])
            if hit['kind']=='component' and key in component_types_seen:continue
            if hit['kind']=='component':component_types_seen.add(key)
            unique.append(hit)
        hits=unique[:k];statuses=[h['assessment']['status'] for h in hits]
        status='supported' if 'supported' in statuses else ('partial' if 'partial' in statuses else ('unknown' if hits else 'not_found'))
        if capability['id']=='unmapped':status='unknown'
        gaps=list(raw['gaps'])
        if 'cost' in intent['display_requirements']:gaps.append('API pricing and paid entitlements are not indexed. An external-service declaration is not proof of a paid plan.')
        if not hits:gaps.append('No source-backed qualifying match in the retrieved candidate pool. This is not proof the library or custom development cannot supply it.')
        if status=='partial':gaps.append('Relevant declarations exist, but a complete capability or one or more requested constraints remain unverified or conflict.')
        if capability['id']=='unmapped':gaps.append('Request outside the explicit vocabulary: returned items, if any, are unknown-relevance candidates.')
        sections[capability['id']]={'query':capability['label'],'requested_text':capability['request_evidence'],'status':status,'results':hits,'gaps':gaps,'semantic_status':raw.get('semantic_status'),'scope':'Capability retrieval and qualification only; no build sequence or architecture.'}
    return {'question':question,'intent':intent,'sections':sections,'seconds':round(time.monotonic()-start,4),'scope':'Search only. No instance, architecture or build plan created. Not found is a bounded retrieval outcome, not impossibility.'}

def render_answer(answer):
    from IPython.display import display,HTML
    from search_engine import render_results
    esc=html.escape;rows=''.join('<tr><td>'+esc(s['query'])+'</td><td>'+esc(s['status'])+'</td><td>'+str(len(s['results']))+'</td></tr>' for s in answer['sections'].values())
    required=[k.replace('_',' ') for k,v in answer['intent']['constraints'].items() if v]
    display(HTML('<h3>Understood request</h3><p>Constraints: '+esc(', '.join(required) or 'none explicitly recognized')+'</p><table><tr><th>Requested capability</th><th>Evidence status</th><th>Matches</th></tr>'+rows+'</table><p>Supported = archived declaration; partial = incomplete or constraints unresolved; unknown = relevance unestablished; not found = no qualifying retrieved match. None certifies execution.</p>'))
    if answer['intent']['alternatives']:display(HTML('<p><strong>Alternatives requested:</strong> '+esc('; '.join(' OR '.join(CAPS[key][0] for key in group) for group in answer['intent']['alternatives']))+'. These are not assumed to be jointly required.</p>'))
    for section in answer['sections'].values():render_results(section)

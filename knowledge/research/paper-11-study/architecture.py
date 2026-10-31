"""Evidence-backed architecture hypotheses over Paper 10 retrieval. No execution/compiler."""
from pathlib import Path
import sys,json,copy,hashlib,collections
P10=Path(__file__).resolve().parents[1]/'paper-10-study'
if str(P10) not in sys.path:sys.path.insert(0,str(P10))
from search_engine import CorpusSearch,CORPUS,resolve_pointer,edge_record
from design_adviser import advise,normalize_context,refined_request,candidate_rank
from request_analysis import CAPS

def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

# Authored domain hypotheses, not inferred native ports or observed wiring.
MEDIA_CONTRACTS={
 'script_input':{'inputs':['user_text'],'outputs':['script_text']},
 'script_writing':{'inputs':['brief_text'],'outputs':['script_text']},
 'image_generation':{'inputs':['script_text'],'outputs':['image_asset']},
 'video_generation':{'inputs':['script_text'],'outputs':['video_asset']},
 'narration':{'inputs':['script_text'],'outputs':['audio_asset']},
 'transcription':{'inputs':['audio_asset'],'outputs':['transcript']},
 'subtitles':{'inputs':['audio_asset'],'outputs':['subtitle_asset']},
 'video_assembly':{'inputs':['visual_asset','audio_asset','subtitle_asset'],'outputs':['video_product']},
}
MEDIA_RELATIONS=[('script_input','image_generation','script_text'),('script_input','video_generation','script_text'),('script_input','narration','script_text'),('script_writing','narration','script_text'),('narration','transcription','audio_asset'),('narration','subtitles','audio_asset'),('image_generation','video_assembly','visual_asset'),('video_generation','video_assembly','visual_asset'),('narration','video_assembly','audio_asset'),('subtitles','video_assembly','subtitle_asset')]

def port_inventory(candidate):
    inputs=[];outputs=[];wired={(e['target'],e.get('target_port')) for e in candidate['edges']}
    source_nodes={n['node_id'] for n in candidate['nodes']}
    for n in candidate['nodes']:
        for p in n['inputs']:
            if (n['node_id'],p['name']) not in wired:
                raw=p.get('types') or []
                types=raw if isinstance(raw,list) else [raw]
                inputs.append({'node_id':n['node_id'],'component':n['type'],'port':p['name'],'declared_types':types,'field_type':p.get('field_type'),'required':p.get('required',False),'credential':p.get('secret_binding',False),'public_interface':'unconfirmed; recorded unconnected field, not automatically a composite input'})
        for p in n['outputs']:
            raw=p.get('types') or [];types=raw if isinstance(raw,list) else [raw]
            outputs.append({'node_id':n['node_id'],'component':n['type'],'port':p['name'],'declared_types':types,'public_interface':'candidate output; intended semantic role unverified'})
    return {'inputs':inputs,'outputs':outputs,'source_boundary':candidate['boundary'],'scope':'Exact archived declarations. Public interface and configuration bindings remain proposed/unconfirmed.'}

def possible_port_pairs(source,target):
    pairs=[]
    for out in source['outputs']:
        for inp in target['inputs']:
            if inp['credential']:continue
            overlap=sorted(set(out['declared_types'])&set(inp['declared_types']))
            if overlap:pairs.append({'source':out,'target':inp,'literal_type_overlap':overlap,'status':'type-overlap-only; semantic/public-interface/runtime compatibility unverified'})
    return pairs[:12]

def realizations(candidate):
    if candidate['kind']=='component':
        result=[]
        for occ in candidate.get('occurrence_refs',[]) or []:
            result.append({'file':occ['source']['file'],'sha256':occ['source']['sha256'],'pointer':occ['graph_pointer'],'nodes':{occ['node_id']}})
        return result
    return [{'file':candidate['sources']['file'],'sha256':candidate['sources']['sha256'],'pointer':candidate['sources']['graph_pointer'],'nodes':{n['node_id'] for n in candidate['nodes']}}]

def observed_witnesses(source,target):
    left=collections.defaultdict(list);right=collections.defaultdict(list)
    for r in realizations(source):left[(r['file'],r['pointer'])].append(r)
    for r in realizations(target):right[(r['file'],r['pointer'])].append(r)
    shared=sorted(left.keys()&right.keys());witnesses=[];checked=0
    for key in shared[:8]:
        path=(CORPUS/key[0]).resolve()
        if not path.is_relative_to(CORPUS.resolve()):continue
        content=path.read_bytes();expected=left[key][0]['sha256']
        if hashlib.sha256(content).hexdigest()!=expected or any(r['sha256']!=expected for r in right[key]):continue
        graph=resolve_pointer(json.loads(content),key[1]);checked+=1
        for a in left[key]:
            for b in right[key]:
                for edge in graph['edges']:
                    if str(edge.get('source')) in a['nodes'] and str(edge.get('target')) in b['nodes']:
                        witnesses.append({'file':key[0],'sha256':expected,'graph_pointer':key[1],'edge':edge_record(edge),'meaning':'Observed original wiring; intended role and execution remain unverified'})
    return {'witnesses':witnesses[:12],'shared_source_graphs':len(shared),'graphs_checked':checked,'search_limit':8,'absence_meaning':'No witness found in the bounded inspection is not proof no compatible connection exists.'}

def summarize_candidate(candidate,excluded):
    assessment=copy.deepcopy(candidate['assessment']);reasons=[]
    if candidate['id'] in excluded:reasons.append('Explicitly excluded for this design revision; no defect is inferred')
    if assessment['constraint_conflict']:reasons.append('Conflicts with a declared hard runtime constraint')
    if assessment['relevance_status']=='unknown':reasons.append('Capability relevance is unestablished')
    if assessment['relevance_status']=='partial' and candidate['kind']!='template':reasons.append('A partial subset/definition is not enough evidence to assign this capability')
    if candidate['structural_warnings'] or candidate['unresolved_edges']:reasons.append('Source graph has unresolved structural issues; repair/requalification required')
    return {'id':candidate['id'],'title':candidate['title'],'kind':candidate['kind'],'assessment':assessment,'admissibility':'rejected' if reasons else 'provisional','reasons':reasons or ['Archived declaration is a design hypothesis; behavior, configuration, current version and license require qualification'],'sources':copy.deepcopy(candidate['sources']),'ports':port_inventory(candidate),'requirements':copy.deepcopy(candidate['requirements']),'dependencies':[{'component':n['type'],'declared_dependencies':n['dependencies']} for n in candidate['nodes']],'structural_warnings':candidate['structural_warnings'],'unresolved_edges':candidate['unresolved_edges']}

class ArchitectureDesigner:
    def __init__(self,engine=None):self.engine=engine or CorpusSearch();self._history=[]
    def propose(self,question,k=6,parent=None,excluded_ids=None,revision_reason=None,context=None):
        if parent is not None and (not isinstance(parent,int) or not 1<=parent<=len(self._history)):raise ValueError('Unknown parent revision')
        if parent is not None and not revision_reason:raise ValueError('A child revision requires an explicit reason')
        context=normalize_context(context if context is not None else (self._history[parent-1].get('design_context',{}) if parent else {}))
        excluded=set(excluded_ids or [])|set(self._history[parent-1].get('excluded_ids',[]) if parent else [])
        effective=refined_request(question,context)
        retrieval=self.engine.answer(effective,k=k)
        slots=[];selected={};raw_selected={};gaps=[]
        for capability,section in retrieval['sections'].items():
            candidates=[summarize_candidate(c,excluded) for c in section['results']]
            admissible=sorted([c for c in candidates if c['admissibility']=='provisional'],key=candidate_rank)
            # Prefer declared primitives; do not silently substitute a generic prompt for an implementation.
            primary=admissible[0] if admissible else None
            state='provisional' if primary else ('unmapped' if capability=='unmapped' else 'unfilled')
            if primary:
                selected[capability]=primary
                raw_selected[capability]=next(c for c in section['results'] if c['id']==primary['id'])
            else:gaps.append({'capability':capability,'reason':'No admissible source-backed candidate among retrieved alternatives','retrieval_status':section['status'],'not_impossibility':True})
            slots.append({'capability':capability,'label':section['query'],'requested_text':section['requested_text'],'search_query':CAPS[capability][2] if capability in CAPS else section['requested_text'],'search_limit':k,'state':state,'primary':primary,'alternatives':candidates,'semantic_interface_hypothesis':MEDIA_CONTRACTS.get(capability),'interface_basis':'Authored domain profile, not an archived native interface' if capability in MEDIA_CONTRACTS else 'No profile; preserve retrieved ports and ask for design evidence','retrieval_gaps':section['gaps'],'choice_reason':'Prefer declared capability evidence, then fewer external dependencies and configuration obligations, then a narrower primitive. This ordering is authored, not a success probability.'})
        relations=[];keys={s['capability'] for s in slots}
        for source,target,artifact in MEDIA_RELATIONS:
            if source not in keys or target not in keys:continue
            bound=source in selected and target in selected
            overlaps=possible_port_pairs(selected[source]['ports'],selected[target]['ports']) if bound else []
            witness=observed_witnesses(raw_selected[source],raw_selected[target]) if bound else {'witnesses':[],'graphs_checked':0,'search_limit':8,'absence_meaning':'Unfilled endpoint: no source-wiring search performed'}
            relations.append({'source_capability':source,'target_capability':target,'semantic_artifact_hypothesis':artifact,'relation_kind':'authored architecture hypothesis, not observed source wiring','status':'unresolved' if not bound else ('observed-wire-exists-role-unverified' if witness['witnesses'] else 'proposed-interface-unverified'),'candidate_port_overlaps':overlaps,'source_wiring_evidence':witness,'adapter_gap':bool(bound and not overlaps),'automatic_adapter_selected':False,'semantic_mapping_verified':False})
        if not relations and len(slots)>1:gaps.append({'capability':'cross-capability relationships','reason':'No authored relationship profile for this domain; no wiring or ordering invented.'})
        groups=[];alternative_members=set()
        for alternatives in retrieval['intent']['alternatives']:
            members=[c for c in alternatives if c in keys];alternative_members.update(members)
            groups.append({'kind':'OR','members':members,'provisionally_covered':any(c in selected for c in members),'validated':False})
        for key in keys-alternative_members:groups.append({'kind':'required','members':[key],'provisionally_covered':key in selected,'validated':False})
        obligations=len(groups);covered=sum(g['provisionally_covered'] for g in groups)
        proposal={'revision':len(self._history)+1,'parent_revision':parent,'parent_digest':self._history[parent-1]['digest'] if parent else None,'revision_reason':revision_reason,'question':question,'constraints':retrieval['intent']['constraints'],'requirement_groups':groups,'slots':slots,'relations':relations,'gaps':gaps,'coverage':{'logical_requirement_groups':obligations,'provisionally_covered':covered,'unfilled':obligations-covered,'validated_implementations':0},'readiness':'design-only; not executable or build-ready','profile':'Authored local-media capability relations' if relations else 'No cross-capability relation profile supplied','retrieval_snapshot':self.engine.stats['corpus_index_sha256'],'provenance_scope':'Every option is retrieved from a hash-checked original; no archived code executed','costs':'No cost, hardware fit, execution or monetization outcome inferred','architecture_accepted':False}
        proposal.update(design_context=context,effective_request=effective,excluded_ids=sorted(excluded))
        proposal['decision_support']=advise(proposal,context)
        proposal['digest']=sha(proposal);self._history.append(copy.deepcopy(proposal));return copy.deepcopy(proposal)
    def revision(self,number):
        if not isinstance(number,int) or not 1<=number<=len(self._history):raise ValueError('Unknown revision')
        record=copy.deepcopy(self._history[number-1]);h=record.pop('digest')
        if sha(record)!=h:raise ValueError('Proposal history changed')
        record['digest']=h;return record
    def history(self):return [self.revision(i) for i in range(1,len(self._history)+1)]
    @classmethod
    def restore(cls,history,engine=None):
        designer=cls(engine)
        for i,p in enumerate(history,1):
            if p.get('revision')!=i or validate_proposal(p,designer.engine):raise ValueError('Invalid saved proposal')
            parent=p.get('parent_revision')
            if parent is not None and (not isinstance(parent,int) or not 1<=parent<i or p['parent_digest']!=designer._history[parent-1]['digest']):raise ValueError('Broken saved parent chain')
            designer._history.append(copy.deepcopy(p))
        return designer

def validate_proposal(proposal,engine):
    errors=[];p=copy.deepcopy(proposal);h=p.pop('digest',None)
    if sha(p)!=h:errors.append('Proposal digest mismatch')
    if proposal.get('architecture_accepted') is not False or proposal.get('coverage',{}).get('validated_implementations')!=0:errors.append('Unverified architecture promoted')
    if 'decision_support' in proposal and proposal['decision_support']!=advise(proposal,proposal.get('design_context',{})):errors.append('Decision support differs from grounded proposal')
    slots={s['capability']:s for s in proposal['slots']}
    for slot in slots.values():
        primary=slot['primary']
        if primary:
            if primary['id'] not in engine.by_id or not engine.verify_source(primary['id']):errors.append('Unresolved/changed source')
            if primary['assessment']['constraint_conflict'] or primary['admissibility']=='rejected':errors.append('Conflicting candidate selected')
            if primary['id'] in engine.by_id:
                original=engine.by_id[primary['id']]
                if primary['ports']!=port_inventory(original) or primary['sources']!=original['sources']:errors.append('Candidate contract/source differs from archive')
    for r in proposal['relations']:
        if r['source_capability'] not in slots or r['target_capability'] not in slots:
            errors.append('Unknown relation endpoint');continue
        if r.get('semantic_mapping_verified') or r.get('automatic_adapter_selected'):errors.append('Unverified connection promoted')
        if not slots[r['source_capability']]['primary'] or not slots[r['target_capability']]['primary']:
            if r['status']!='unresolved':errors.append('Unfilled endpoint treated as connected')
        for witness in r['source_wiring_evidence']['witnesses']:
            try:
                path=(CORPUS/witness['file']).resolve()
                if not path.is_relative_to(CORPUS.resolve()):raise ValueError('unsafe witness path')
                content=path.read_bytes()
                if hashlib.sha256(content).hexdigest()!=witness['sha256']:raise ValueError('witness source hash changed')
                graph=resolve_pointer(json.loads(content),witness['graph_pointer'])
                if witness['edge'] not in [edge_record(e) for e in graph['edges']]:raise ValueError('fabricated witness edge')
                for role,endpoint in [('source_capability','source'),('target_capability','target')]:
                    candidate=slots[r[role]]['primary']
                    if not candidate:raise ValueError('witness on unfilled endpoint')
                    realizations_for_role=realizations(engine.by_id[candidate['id']])
                    if not any(x['file']==witness['file'] and x['pointer']==witness['graph_pointer'] and witness['edge'][endpoint] in x['nodes'] for x in realizations_for_role):raise ValueError('witness unrelated to assigned candidate')
            except (KeyError,ValueError,OSError,TypeError):errors.append('Invalid archived wiring witness')
    return errors

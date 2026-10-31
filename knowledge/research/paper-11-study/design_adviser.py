"""Decision support over archived evidence, not a runtime compatibility oracle.
Approach branches are authored alternatives over requested OR groups. No new
components, wiring or successful implementations are invented here.
"""
import itertools,re
TASKS={
 'video_assembly':('Locate or specify a local video assembler accepting visual assets, narration audio and subtitle files.','Produce one playable video with the requested duration, audible narration and synchronized captions; record dependencies and actual Mac execution.','local video assembly visual assets audio SRT mux render'),
 'image_generation':('Locate a local image generator for the chosen Mac and memory budget.','Generate one image from a script-derived prompt, record model/license, peak memory and elapsed time.','local Apple Silicon image generation model memory'),
 'video_generation':('Locate a local motion-clip generator for the chosen Mac and memory budget.','Generate one short clip; record model/license, duration, peak memory and elapsed time.','local Apple Silicon text to video generation model memory'),
 'narration':('Qualify a local text-to-speech implementation that accepts script text.','Render one intelligible audio file locally; record voice/model license and measured runtime.','local text to speech script audio Apple Silicon'),
 'subtitles':('Locate subtitle generation with timestamps and an SRT or VTT export.','Produce subtitles from representative narration and check timestamps against the audio.','local subtitle transcription timestamps SRT VTT'),
}
FIELDS={'memory_gb','output_goal','duration_seconds','visual_path'}

def normalize_context(context):
    if context is None:return {}
    if not isinstance(context,dict) or set(context)-FIELDS:raise ValueError('Unknown design context fields')
    out={}
    for key,value in context.items():
        if value in ('',None):continue
        if key in ('memory_gb','duration_seconds'):
            if isinstance(value,bool):raise ValueError('Enter positive numeric hardware/duration values')
            try:value=float(value)
            except (ValueError,TypeError):raise ValueError('Enter numeric hardware/duration values')
            if not 0<value<=100000:raise ValueError('Hardware/duration value is outside the supported range')
        elif key=='output_goal' and value not in ('clips','narrated_video'):raise ValueError('Choose clips or narrated video')
        elif key=='visual_path' and value not in ('image_generation','video_generation'):raise ValueError('Unknown visual path')
        out[key]=value
    return out

def clarification_questions(question,context):
    context=normalize_context(context);q=question.lower();media=bool(re.search(r'video|narrat|image|subtitles|voiceover',q));questions=[]
    def add(key,label,why):questions.append({'field':key,'question':label,'changes':why})
    if media and re.search(r'mac|apple silicon',q) and 'memory_gb' not in context and not re.search(r'\b\d+\s*(?:gb|gigabytes?)\b',q):add('memory_gb','How much unified memory does your Mac have?','Changes which model sizes are worth investigating; memory fit still needs a real run.')
    if media and 'output_goal' not in context and not (re.search(r'narrat|voiceover|text.to.speech',q) and re.search(r'assembly|assemble|finished|complete narrated',q)):add('output_goal','Do you want generated clips or a complete narrated video?','Changes whether narration, timing, captions and final assembly belong in the design.')
    if media and 'duration_seconds' not in context:add('duration_seconds','How long should one finished output be, in seconds?','Changes the generation/assembly workload and the first validation target.')
    return questions

def refined_request(question,context):
    """Add explicit capability requirements only after a user chooses an output."""
    context=normalize_context(context)
    if context.get('output_goal')=='narrated_video':
        return question+'; script input; image or video generation; narration; subtitles; final video assembly'
    return question

def candidate_rank(c):
    a=c['assessment']
    # Prefer narrower declared evidence, fewer unknown obligations, fewer external dependencies.
    # This is an authored ordering, not an empirically learned success probability.
    return (a['relevance_status']!='supported',len(a.get('external_service_components',[])),len(c['requirements']),c['kind']!='component',c['id'])

def diagnose(slot):
    options=slot['alternatives'];conflicting=[c for c in options if c['assessment']['constraint_conflict']]
    if slot['capability']=='unmapped':kind='interpretation_gap';meaning='The engine cannot reliably interpret this part of the request.';action='Clarify the unmapped requirement before selecting parts.'
    elif slot['primary']:kind='unverified';meaning='A source declares a relevant capability, but the proposed use is not proven.';action='Check configuration, local execution, license and one input/output example for the selected piece.'
    elif not options:kind='retrieval_gap';meaning='No qualifying evidence was returned by this bounded library search.';action='Expand the corpus/search for this capability, or specify a custom implementation; do not infer impossibility.'
    elif conflicting and len(conflicting)==len(options):kind='constraint_conflict';meaning='Every inspected option conflicts with a hard constraint.';action='Find a constraint-compatible implementation. Keep the constraint unless the user explicitly changes it.'
    elif conflicting:kind='mixed_evidence_gap';meaning='Some options conflict; the remaining options have insufficient relevance or unresolved structure.';action='Investigate the nonconflicting evidence and search for a dedicated implementation.'
    else:kind='qualification_gap';meaning='Candidates were found but none has enough admissible evidence.';action='Inspect rejection reasons and qualify a complete implementation or repair source structure.'
    task=TASKS.get(slot['capability'])
    if task and not slot['primary'] and kind!='interpretation_gap':action=task[0]+' Preserve all declared hard constraints.'
    return {'acceptance_evidence':task[1] if task else 'Show a source-backed interface and one representative input/output check; state any remaining uncertainty.','search_query':task[2] if task else slot.get('requested_text',slot['label']),'capability':slot['capability'],'label':slot['label'],'category':kind,'explanation':meaning,'next_action':action,'inspected':len(options),'conflicting':len(conflicting),'evidence_ids':[c['id'] for c in options],'search_scope':'At most 30 qualified candidates per capability; no claim of exhaustive absence.'}

def advise(proposal,context=None):
    context=normalize_context(context);slots={s['capability']:s for s in proposal['slots']};diagnoses=[diagnose(s) for s in slots.values()]
    groups=proposal['requirement_groups'];ors=[g['members'] for g in groups if g['kind']=='OR'];required=[c for g in groups if g['kind']=='required' for c in g['members']]
    combinations=list(itertools.product(*ors)) if ors else [()];approaches=[]
    for index,chosen in enumerate(combinations[:8]):
        members=required+list(chosen);members=list(dict.fromkeys(members));picks={c:slots[c]['primary'] for c in members};unfilled=[c for c,v in picks.items() if not v]
        relations=[r for r in proposal['relations'] if r['source_capability'] in members and r['target_capability'] in members]
        name=' + '.join(slots[c]['label'] for c in chosen) if chosen else 'Requested capability approach'
        if chosen==('image_generation',):name='Still-image video path'
        if chosen==('video_generation',):name='Generated-motion video path'
        tradeoff='Authored option over the requested capabilities; no performance or cost advantage established.'
        if chosen==('image_generation',):tradeoff='Create still images and assemble them with audio/captions when requested. Optional pan/zoom requires assembly support; no hardware or cost advantage is yet measured.'
        if chosen==('video_generation',):tradeoff='Generate motion clips and assemble them with audio/captions when requested. Clip consistency, runtime and memory fit need separate validation.'
        sources=[v['id'] for v in picks.values() if v]
        approaches.append({'id':f'approach-{index+1}','name':name,'members':members,'choices':{k:v['id'] if v else None for k,v in picks.items()},'source_evidence_ids':sources,'unfilled':unfilled,'provisional_count':len(members)-len(unfilled),'required_count':len(members),'relations':relations,'tradeoff':tradeoff,'status':'incomplete' if unfilled else 'requires_validation','verified_implementations':0,'selection_basis':'Requested capability structure plus archived candidate evidence; semantic relationships are authored hypotheses.'})
    preferred=context.get('visual_path');ranking=sorted(approaches,key=lambda a:(bool(preferred) and preferred not in a['members'],len(a['unfilled']),-a['provisional_count']))
    recommended=ranking[0] if ranking else None
    tied=[a for a in ranking if recommended and len(a['unfilled'])==len(recommended['unfilled'])]
    if preferred:why='Your selected visual path is prioritized. This is a preference, not evidence that it will work.'
    elif len(tied)>1:why='The alternatives have equal retrieved coverage. There is no evidence-backed winner; choose the output style before committing.'
    else:why='This approach has the fewest unfilled requested capability slots among the compared paths. Coverage does not prove feasibility.'
    actions=[]
    questions=clarification_questions(proposal['question'],context)
    for q in questions:actions.append({'priority':'clarify','title':q['question'],'why':q['changes'],'evidence_ids':[]})
    # Solve missing core capabilities before spending effort validating a trivial text input.
    missing_order={'video_assembly':0,'video_generation':1,'image_generation':1,'narration':2,'subtitles':3,'script_input':9}
    needed=set(recommended['members'] if recommended else slots)
    for d in sorted(diagnoses,key=lambda d:missing_order.get(d['capability'],4)):
        if d['category']=='unverified':continue
        actions.append({'priority':'resolve_gap','title':d['label']+': '+d['next_action'],'why':d['explanation'],'acceptance_evidence':d['acceptance_evidence'],'search_query':d['search_query'],'evidence_ids':d['evidence_ids']})
    if proposal['relations']:actions.append({'priority':'validate','title':'Validate one adjacent pair with representative input and output.','why':'Declared port types and archived wires do not establish the intended semantic transfer.','evidence_ids':recommended['source_evidence_ids'] if recommended else []})
    else:actions.append({'priority':'design','title':'Define the cross-capability handoffs before proposing wiring.','why':'No relationship profile for this domain is implemented.','evidence_ids':[]})
    targets=[]
    if context.get('memory_gb'):targets.append(str(context['memory_gb']).removesuffix('.0')+' GB unified memory')
    if context.get('duration_seconds'):targets.append(str(context['duration_seconds']).removesuffix('.0')+' second output')
    for action in actions:
        if action['priority']=='resolve_gap' and targets:
            action['target_context']='User target: '+', '.join(targets)+'. Measure feasibility; do not assume it.'
    first=next((a for a in actions if a['priority']=='resolve_gap' and any(a['title'].startswith(d['label']+':') and d['capability'] in needed for d in diagnoses)),actions[0] if actions else None)
    summary=(f"{recommended['name']}: {recommended['provisional_count']} of {recommended['required_count']} capability slots have provisional library candidates. " if recommended else '')+'No complete, runnable system is established.'
    return {'version':1,'context':context,'questions':questions,'diagnoses':diagnoses,'approaches':approaches,'recommended_approach':recommended['id'] if recommended else None,'recommendation_reason':why,'summary':summary,'next_actions':actions,'next_technical_action':first,'comparison_limits':'Only requested OR branches and retrieved candidates are compared. No global optimality, cost, hardware fit or task success is established.','hardware_status':'User-supplied context only; not a compatibility test.'}

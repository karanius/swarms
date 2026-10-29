"""Authored structural tasks. Same-author exposed evaluation, not held out."""
from copy import deepcopy


def component(key,cap,inp,out,resources=None,extra=False,locality='local'):
    ports={'in':{'type':inp,'required':True}}
    if extra: ports['context']={'type':'Context','required':True}
    return {'id':key+'@1','layer':'components','cap':cap,'inputs':ports,'outputs':{'out':out},
            'config':{'mode':'declared'},'resources':resources or [],'locality':locality}


def refinement(key,cap,inp,out,steps,edges=None,bridge='met'):
    return {'id':key+'@1','cap':cap,'in':inp,'out':out,
            'steps':[{'key':k,'cap':c,'in':i,'out':o} for k,c,i,o in steps],
            'edges':edges if edges is not None else [[steps[i][0],steps[i+1][0]] for i in range(len(steps)-1)],
            'entry':steps[0][0],'exit':steps[-1][0],'bridge':bridge}


def requirement(key,cap,inp='Text',out='Report',**kw):
    return dict(id=key,cap=cap,**{'in':inp,'out':out},**kw)


def base(cid):
    return {'id':cid,'baseline_version':'requirements@1','library_version':'synthetic-library@1',
            'profile':'components-to-composite-dag@1',
            'requirements':[requirement('R-report','report')],
            'library':[component('extract','extract','Text','Facts'),component('write','write','Facts','Report')],
            'rules':[refinement('report-standard','report','Text','Report', [('a','extract','Text','Facts'),('b','write','Facts','Report')])],
            'resources':{},'limits':{'attempts':160,'frontier':16,'depth':5,'nodes':24,'candidates':8},
            'ambient_edges':[], 'oracle':{'outcome':'design-closed','nodes':2,'edges':1,'backtrack':False}}


def build():
    dev=[];ev=[]
    c=base('D-decompose');dev.append(c)
    c=base('D-backtrack');c['rules'].insert(0,refinement('a-dead','report','Text','Report',[('x','missing','Text','Report')]))
    c['oracle']['backtrack']=True;dev.append(c)
    c=base('D-resource');c['library'][0]['resources']=['resource:model'];c['resources']={'resource:model':{'version':'1','described':True}};dev.append(c)
    c=base('D-clarify');c['requirements'][0]['cap']=None;c['oracle']={'outcome':'awaiting-clarification','gap_prefix':'ambiguous-capability'};dev.append(c)
    c=base('E-three-step');c['library']=[component('clean','clean','Text','Clean'),component('tag','tag','Clean','Tags'),component('render','render','Tags','Report')]
    c['rules']=[refinement('three','report','Text','Report',[('a','clean','Text','Clean'),('b','tag','Clean','Tags'),('c','render','Tags','Report')])];c['oracle'].update(nodes=3,edges=2);ev.append(c)
    c=base('E-direct-reuse');c['library'].append(component('direct','report','Text','Report'));c['oracle'].update(nodes=1,edges=0);ev.append(c)
    c=base('E-nested');c['library']=[component('clean','clean','Text','Clean'),component('extract','extract','Clean','Facts'),component('write','write','Facts','Report')]
    c['rules']=[refinement('outer','report','Text','Report',[('prepare','prepare','Text','Facts'),('write','write','Facts','Report')]),refinement('inner','prepare','Text','Facts',[('clean','clean','Text','Clean'),('extract','extract','Clean','Facts')])];c['oracle'].update(nodes=3,edges=2);ev.append(c)
    c=base('E-backtrack');c['rules'].insert(0,refinement('a-dead','report','Text','Report',[('x','unsupported','Text','Report')]))
    c['oracle']['backtrack']=True;ev.append(c)
    c=base('E-type-reject');c['library'].insert(0,component('a-wrong','extract','Image','Facts'));ev.append(c)
    c=base('E-locality');c['requirements'][0]['locality']='local';c['library'].insert(0,component('a-cloud','extract','Text','Facts',locality='remote'));ev.append(c)
    c=base('E-extra-input');c['library'][1]['inputs']['context']={'type':'Context','required':True};c['oracle']['extra_input']=True;ev.append(c)
    c=base('E-crossing');c['ambient_edges']=[['occ:R-report/report-standard@1/a','out','outside','in']];c['oracle']['crossings']=1;ev.append(c)
    c=base('E-two-roots');c['requirements'].append(requirement('R-other','report'));c['oracle'].update(nodes=4,edges=2);ev.append(c)
    c=base('E-prerequisite');c['requirements'].append(requirement('R-before','report'));c['requirements'][0]['needs']=['R-before'];c['oracle'].update(nodes=4,edges=2);ev.append(c)
    c=base('E-missing');c['library']=c['library'][:1];c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'unsupported-boundary'};ev.append(c)
    c=base('E-no-resource');c['library'][0]['resources']=['resource:absent'];c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'missing-resource'};ev.append(c)
    c=base('E-bound-resource');c['library'][0]['resources']=['resource:store'];c['resources']={'resource:store':{'version':'1','described':True}};ev.append(c)
    c=base('E-unknown-bridge');c['rules'][0]['bridge']='unknown';c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'unsupported-boundary'};ev.append(c)
    c=base('E-rule-cycle');c['rules'][0]['edges']=[['a','b'],['b','a']];c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'unsupported-boundary'};ev.append(c)
    c=base('E-prerequisite-cycle');c['requirements'][0]['needs']=['R-before'];c['requirements'].append(requirement('R-before','report',needs=['R-report']));c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'prerequisite-cycle'};ev.append(c)
    c=base('E-missing-prerequisite');c['requirements'][0]['needs']=['unknown'];c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'missing-prerequisite'};ev.append(c)
    c=base('E-budget');c['limits']['attempts']=2;c['oracle']={'outcome':'partial','gap_prefix':'budget-exhausted'};ev.append(c)
    c=base('E-profile');c['profile']='flows-to-processes@unprovided';c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'unsupported-profile'};ev.append(c)
    c=base('E-frontier-pruned');c['limits']['frontier']=0;c['rules'].insert(0,refinement('a-dead','report','Text','Report',[('x','unsupported','Text','Report')]))
    c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'unsupported-boundary'};ev.append(c)
    c=base('E-conflict-priority');c['requirements'].append(requirement('R-conflict','report',conflict=True));c['limits']['attempts']=4;c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'mandatory-conflict'};ev.append(c)
    c=base('E-empty');c['requirements']=[];c['oracle']={'outcome':'awaiting-clarification','gap_prefix':'empty-scope'};ev.append(c)
    c=base('E-depth-limit');c['limits']['depth']=0;c['oracle']={'outcome':'blocked-within-horizon','gap_prefix':'unsupported-boundary'};ev.append(c)
    c=base('E-distractor');c['library'].append(component('other','unrelated','Text','Report'));ev.append(c)
    for c in dev:c['collection']='development-exposed'
    for c in ev:c['collection']='evaluation-same-author-exposed'
    return dev+ev

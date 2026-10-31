"""Controller-owned discovery state and generated document projections."""
import json
import os
from pathlib import Path
import tempfile
from rich.text import Text
import pi_adapter


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary=tempfile.mkstemp(dir=path.parent,prefix='.pending-')
    try:
        with os.fdopen(fd,'w') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def workspace(root, instance):
    return root / 'workspaces' / instance['id']


def load(root, instance):
    directory=workspace(root,instance)
    path=directory/'state.json'
    state=json.loads(path.read_text()) if path.exists() else pi_adapter.initial_state(instance)
    if state['intent']!=instance['outcome']:
        raise pi_adapter.PiError('The outcome changed since discovery began. Restore its original wording or create a new instance to preserve the earlier decisions.')
    state.setdefault('assumptions',[])
    return state


def persist(root, instance, state):
    directory=workspace(root,instance)
    # Authoritative state commits first. Derived documents can always be regenerated.
    atomic_write(directory/'state.json',json.dumps(state,indent=2,ensure_ascii=False)+'\n')
    project(directory,state)


def project(directory,state):
    atomic_write(directory/'INTENT.md','# Intent\n\n'+state['intent']+'\n')
    atomic_write(directory/'DECISIONS.md','# Confirmed decisions\n\n'+'\n'.join('- '+d['text'] for d in state['decisions'])+'\n')
    atomic_write(directory/'MAP.md','# Discovery map\n\n'+state['summary']+'\n\n## Open questions\n\n'+'\n'.join('- '+q['text'] for q in state['questions'])+'\n\n## Next question\n\n'+state['next_question']+'\n')
    atomic_write(directory/'GLOSSARY.md','# Glossary\n\n'+'\n'.join('- **'+g['term']+'**: '+g['definition'] for g in state['glossary'])+'\n')
    atomic_write(directory/'tower.json',json.dumps({'instance_id':state['instance_id'],'name':state['name'],'blocks':state['tower']},indent=2)+'\n')
    atomic_write(directory/'ASSUMPTIONS.md','# Working assumptions\n\n'+'\n'.join('- '+a['text']+' ('+a['provenance']+')' for a in state.get('assumptions',[]))+'\n')
    atomic_write(directory/'SPEC.md','# Working specification\n\n## Intent\n\n'+state['intent']+'\n\n## Current understanding\n\n'+state['summary']+'\n\n## Decisions\n\n'+'\n'.join('- '+d['text'] for d in state['decisions'])+'\n\n## Unresolved\n\n'+'\n'.join('- '+q['text'] for q in state['questions'])+'\n\n## Working assumptions\n\n'+'\n'.join('- '+a['text'] for a in state.get('assumptions',[]))+'\n\nDesign only; no execution capability is asserted.\n')


def finish(root,instance,state):
    state=dict(state,lifecycle='design_handoff_ready')
    persist(root,instance,state)
    directory=workspace(root,instance)
    handoff='# Design handoff — '+state['name']+'\n\nStatus: provisional design complete; research and execution remain open.\n\n## Outcome\n\n'+state['intent']+'\n\n## Design\n\n'+state['summary']+'\n\n## Proposed building blocks\n\n'+'\n'.join('- '+b['layer']+': '+b['name'] for b in state['tower'])+'\n\n## Working assumptions\n\n'+'\n'.join('- '+a['text'] for a in state['assumptions'])+'\n\n## Open work\n\n'+'\n'.join('- '+q['text'] for q in state['questions'])+'\n'
    atomic_write(directory/'HANDOFF.md',handoff)
    return state


def run(root,instance,ui):
    state=load(root,instance)
    project(workspace(root,instance),state)
    pending=workspace(root,instance)/'pending.json'
    if pending.exists():
        proposed=pi_adapter.validate(json.loads(pending.read_text()),state)
        ui.card(' SAVED PROPOSAL / REVIEW ',Text(proposed['name']+'\n\n'+proposed['summary']+'\n\nNext: '+proposed['next_question']))
        ui.console.print('  A  Accept and save     R  Discard     B  Back     Q  Exit',style='cyan')
        action=ui.ask('  Review  ›  ',{'a','A','r','R'},back=True)
        if action.lower()=='a':
            proposed['conversation']=state['conversation']+[{'user':None,'question':proposed['next_question']}]
            persist(root,instance,proposed)
            state=proposed
        pending.unlink()
    while True:
        reply_role='user'
        if state['name']:
            ui.card(' DISCOVERY / '+state['name']+' ',Text(state['summary']))
            ui.card(' NEXT DECISION ',Text(state['next_question']+'\n\nRecommendation: '+state['recommendation']))
            ui.console.print('  T  View tower     D  View documents     M  Model setup',style='cyan')
            ui.console.print('  /assume TEXT  Delegated defaults     /finish  Finish design',style='cyan')
            ui.console.print('  Reply naturally · /back returns · /quit saves and exits',style='dim')
            reply=ui.ask('  You  ›  ',back=True)
            if reply.lower()=='/finish':
                finish(root,instance,state)
                ui.card(' DESIGN HANDOFF READY ',Text('Provisional design saved. The handoff lists assumptions, proposed blocks, and unresolved research. No live property search has been performed.'),'green')
                return
            if reply.startswith('/assume '):
                reply=reply[len('/assume '):].strip()
                reply_role='assistant'
                if not reply:
                    continue
            if reply.lower()=='t':
                ui.card(' PROPOSED TOWER ',Text('\n'.join(b['layer']+' · '+b['name'] for b in state['tower']) or 'No blocks proposed yet.'))
                continue
            if reply.lower()=='d':
                ui.card(' INSTANCE DOCUMENTS ',Text(str(workspace(root,instance))+'\nINTENT.md · MAP.md · DECISIONS.md · GLOSSARY.md · SPEC.md · tower.json'))
                continue
            if reply.lower()=='m':
                pi_adapter.setup()
                continue
        else:
            ui.card(' DISCOVERY / ORIENT ',Text('Pi will load your saved intent and propose an instance name, an initial map, and the next discovery question.'))
            ui.console.print('  C  Continue with Pi     M  Model setup     B  Back     Q  Exit',style='cyan')
            action=ui.ask('  Next  ›  ',{'c','C','m','M'},back=True)
            if action.lower()=='m':
                pi_adapter.setup()
                continue
            reply=None
        try:
            with ui.console.status('Pi is reconstructing the instance and charting the next decision…',spinner='dots'):
                proposed=pi_adapter.propose(state,reply,reply_role=reply_role)
        except pi_adapter.PiError as error:
            ui.card(' MODEL CONNECTION ',Text(str(error)),'yellow')
            ui.console.print('  Model setup opens API Proxy. Connect your account, choose a model, and start the local API.',style='dim')
            continue
        ui.card(' PROPOSED UPDATE ',Text(proposed['name']+'\n\n'+proposed['summary']+'\n\nNext: '+proposed['next_question']))
        ui.console.print('  A  Accept and save     R  Discard     B  Back     Q  Exit',style='cyan')
        action=ui.ask('  Review  ›  ',{'a','A','r','R'},back=True)
        if action.lower()=='a':
            proposed['conversation']=state['conversation']+[{'actor':reply_role,'text':reply,'question':proposed['next_question']}]
            persist(root,instance,proposed)
            state=proposed
            ui.console.print('  ✓ Model, documents, and tower manifest saved.',style='green')

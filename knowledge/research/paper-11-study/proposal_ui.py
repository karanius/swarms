"""Native notebook interface for inspecting hypotheses, never executing source templates."""
import html,time
import ipywidgets as widgets
from IPython.display import display,HTML,JSON
import pandas as pd
from architecture import ArchitectureDesigner,validate_proposal

def draw_proposal(proposal):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch
    slots=proposal['slots'];known={'script_input':(0,2),'script_writing':(0,3),'image_generation':(2,3),'video_generation':(2,1),'narration':(2,-1),'transcription':(4,-2),'subtitles':(4,-1),'video_assembly':(6,2)}
    positions={s['capability']:known.get(s['capability'],(i*2,0)) for i,s in enumerate(slots)}
    fig,ax=plt.subplots(figsize=(9,5))
    for s in slots:
        x,y=positions[s['capability']];color='#dbe4ff' if s['primary'] else '#f1f3f5'
        ax.text(x,y,s['label'].replace(' / ','\n')+'\n['+s['state']+']',ha='center',va='center',fontsize=11,bbox={'boxstyle':'round,pad=.5','facecolor':color,'edgecolor':'#4263eb' if s['primary'] else '#868e96'})
    for r in proposal['relations']:
        a,b=positions[r['source_capability']],positions[r['target_capability']]
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,shrinkA=48,shrinkB=48,linestyle='--',color='#868e96',connectionstyle='arc3,rad=.06'))
    xs=[p[0] for p in positions.values()];ys=[p[1] for p in positions.values()]
    ax.set_xlim(min(xs)-1.2,max(xs)+1.2);ax.set_ylim(min(ys)-1,max(ys)+1);ax.axis('off');ax.set_title('Architecture hypothesis — not executable\nDashed arrows: semantic hypotheses, not verified wiring\nImage OR video: alternative visual paths, not jointly required')
    plt.tight_layout();plt.show();plt.close(fig)

def render_proposal(proposal,designer):
    esc=html.escape;coverage=proposal['coverage']
    display(HTML('<h3>Evidence-backed architecture proposal</h3><p><strong>'+esc(proposal['readiness'])+'</strong></p><p>'+str(coverage['logical_requirement_groups'])+' logical requirements; '+str(coverage['provisionally_covered'])+' provisionally covered; '+str(coverage['unfilled'])+' unfilled; zero validated implementations. Image OR video remains an alternative when requested.</p>'))
    display(pd.DataFrame([{'Capability':s['label'],'State':s['state'],'Proposed candidate':s['primary']['title'] if s['primary'] else 'No admissible candidate','Alternatives inspected':len(s['alternatives'])} for s in proposal['slots']]))
    draw_proposal(proposal)
    for slot in proposal['slots']:
        chunks=['<details><summary>'+esc(slot['label'])+': candidates, reasons and interface evidence</summary>']
        for option in slot['alternatives']:
            origin=option['sources']['origins'][0];url=origin.get('sourceUrl') or ''
            if not url.startswith(('https://','http://')):url=''
            chunks.append('<h4>'+esc(option['title'])+'</h4><p>'+esc(option['admissibility'])+' — '+esc('; '.join(option['reasons']))+'</p><p><a target="_blank" rel="noopener noreferrer" href="'+esc(url,quote=True)+'">Original source</a></p><pre>'+esc(__import__('json').dumps({'assessment':option['assessment'],'ports':option['ports'],'configuration_requirements':option['requirements'],'dependencies':option['dependencies']},indent=2))+'</pre>')
        if not slot['alternatives']:chunks.append('<p>No qualifying match was retrieved. This is a library/search evidence gap, not impossibility.</p>')
        chunks.append('</details>');display(HTML(''.join(chunks)))
    display(pd.DataFrame([{'From':r['source_capability'],'To':r['target_capability'],'Relation status':r['status'],'Literal port-type overlaps':len(r['candidate_port_overlaps']),'Archived wire witnesses':len(r['source_wiring_evidence']['witnesses']),'Semantic mapping verified':r['semantic_mapping_verified']} for r in proposal['relations']]))
    display(JSON({'current_proposal':proposal,'complete_history':designer.history()},expanded=False))

def show_designer():
    from test_upgrade import VIDEO_QUERY
    designer=ArchitectureDesigner();question=widgets.Textarea(value=VIDEO_QUERY,description='Request:',layout=widgets.Layout(width='100%',height='100px'))
    propose=widgets.Button(description='Propose architecture',button_style='primary',icon='search',layout=widgets.Layout(width='220px'))
    choice=widgets.Dropdown(options=[('No candidate selected',None)],description='Exclude:',layout=widgets.Layout(width='100%'))
    reason=widgets.Text(value='Explore an alternative candidate; this is a design hypothesis.',description='Reason:',layout=widgets.Layout(width='100%'))
    revise=widgets.Button(description='Revise with exclusion',disabled=True,layout=widgets.Layout(width='220px'))
    status=widgets.HTML(value='Retrieval and design hypotheses only. No archived template is executed.')
    out=widgets.Output();current={'revision':None}
    def run(parent=None,exclude=None):
        propose.disabled=True;revise.disabled=True;start=time.monotonic()
        try:
            p=designer.propose(question.value,parent=parent,excluded_ids=[exclude] if exclude else [],revision_reason=reason.value if parent else None)
            errors=validate_proposal(p,designer.engine)
            if errors:raise ValueError('; '.join(errors))
            with out:out.clear_output(wait=True);render_proposal(p,designer)
            current['revision']=p['revision'];choice.options=[('Choose a provisional candidate to exclude',None)]+[(s['label']+' — '+s['primary']['title'],s['primary']['id']) for s in p['slots'] if s['primary']]
            status.value=f'Proposal revision {p["revision"]} recorded in {time.monotonic()-start:.2f}s. Earlier revisions retained; no archived component code executed or instance deployed.'
        except Exception as exc:
            with out:out.clear_output();print('Proposal could not complete:',str(exc))
            status.value='No proposal is being represented as successful.'
        finally:propose.disabled=False;revise.disabled=current['revision'] is None
    propose.on_click(lambda _:run())
    def revise_click(_):
        if not choice.value:status.value='Select a candidate to exclude first.';return
        run(current['revision'],choice.value)
    revise.on_click(revise_click)
    display(widgets.VBox([question,propose,choice,reason,revise,status,out]));return {'designer':designer,'question':question,'propose':propose,'choice':choice,'reason':reason,'revise':revise,'status':status,'output':out}

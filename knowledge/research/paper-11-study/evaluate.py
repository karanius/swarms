import json,copy
from pathlib import Path
from architecture import ArchitectureDesigner,validate_proposal
from test_upgrade import VIDEO_QUERY
D=Path(__file__).resolve().parent

def run():
    d=ArchitectureDesigner();retrieval=d.engine.answer(VIDEO_QUERY,k=6)
    baseline=[{'capability':k,'first_hit':s['results'][0]['id'],'known_constraint_conflict':s['results'][0]['assessment']['constraint_conflict']} for k,s in retrieval['sections'].items() if s['results']]
    first=d.propose(VIDEO_QUERY,k=6)
    excluded=next(s['primary']['id'] for s in first['slots'] if s['capability']=='script_input')
    second=d.propose(VIDEO_QUERY,k=6,parent=1,excluded_ids=[excluded],revision_reason='Controlled candidate exclusion to exercise revision; not an observed source defect')
    assert not validate_proposal(first,d.engine) and not validate_proposal(second,d.engine)
    assert d.revision(1)==first
    unknown=d.propose('Find SQL queries and vector retrieval')
    report={'scope':'Exposed, authored architecture-development cases; source and contract checks only. No build or runtime experiment. First-hit baseline is an unqualified selection heuristic, not a previous architecture implementation.','baseline':baseline,'first_hit_conflicts':sum(x['known_constraint_conflict'] for x in baseline),'qualified_selected_conflicts':sum(s['primary']['assessment']['constraint_conflict'] for s in first['slots'] if s['primary']),'proposal':first,'revision':second,'unprofiled_domain':unknown,'parent_preserved':d.revision(1)==first}
    (D/'EVALUATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'baseline_conflicts':report['first_hit_conflicts'],'qualified_conflicts':report['qualified_selected_conflicts'],'coverage':first['coverage'],'parent_preserved':report['parent_preserved']},indent=2));return report

if __name__=='__main__':run()

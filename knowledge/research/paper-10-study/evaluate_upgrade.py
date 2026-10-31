"""Before/after intent and qualification comparison; exposed development evidence."""
import importlib.util,json
from search_engine import CorpusSearch,D,CORPUS
from test_upgrade import VIDEO_QUERY

def run():
    spec=importlib.util.spec_from_file_location('paper10_legacy',D/'revisions/search-v1/search_engine.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy);legacy.CORPUS=CORPUS
    engine=CorpusSearch();old=legacy.CorpusSearch.__new__(legacy.CorpusSearch);old.__dict__=engine.__dict__.copy()
    before=old.answer(VIDEO_QUERY,k=3);after=engine.answer(VIDEO_QUERY,k=3)
    report={'scope':'Exposed regression and evidence qualification, not independent semantic evaluation or runtime compatibility proof.','query':VIDEO_QUERY,'before':{'sections':list(before['sections']),'titles':{k:[r['title'] for r in s['results']] for k,s in before['sections'].items()}},'after':{'intent':after['intent'],'sections':{k:{'status':s['status'],'matches':[{'id':r['id'],'title':r['title'],'assessment':r['assessment']} for r in s['results']],'gaps':s['gaps']} for k,s in after['sections'].items()}},'full_after_answer':after}
    (D/'UPGRADE-EVALUATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Before:',list(before['sections']))
    print('After:',{k:s['status'] for k,s in after['sections'].items()});return report
if __name__=='__main__':run()

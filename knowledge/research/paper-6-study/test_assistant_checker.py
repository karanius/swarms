"""Fault injection checks that the coordinator checker rejects broken result artifacts."""
import copy,json,tempfile,unittest
from pathlib import Path
from verify_assistant_experiment import verify,ART
class CheckerSensitivity(unittest.TestCase):
 def test_faults_are_rejected(self):
  original=json.loads((ART/'obligation-results.json').read_text())
  mutations={
   'route_bypass':lambda d:next(r for r in d['records'] if r['base_case_id']=='C20' and r['variant']=='base')['decisions']['ledger']['post_state']['edges'][1].update(source='i',output='message'),
   'missing_record':lambda d:d['records'].pop(),
   'dropped_blocker':lambda d:d['records'][0]['decisions']['ledger'].__setitem__('blockers',[]),
   'invented_success':lambda d:d['records'][0]['decisions']['ledger'].__setitem__('action','SPEC_GROUNDED'),
   'unauthorized_patch':lambda d:d['records'][0]['decisions']['ledger']['patches'].append({'op':'remove_node'}),
   'lost_unknowns':lambda d:d['records'][0]['decisions']['ledger'].__setitem__('runtime_unknowns',[]),
   'rewritten_input':lambda d:d['records'][0]['input']['nodes'][0].__setitem__('type','UnknownType'),
   'changed_intent':lambda d:d['records'][0]['decisions']['ledger']['post_state']['intent'].__setitem__('id','silently-changed'),
  }
  baseline={(x['case'],x['reason']) for x in verify(ART/'obligation-results.json')['failures']}
  for name,mutate in mutations.items():
   with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
    data=copy.deepcopy(original);mutate(data);p=Path(folder)/'result.json';p.write_text(json.dumps(data))
    failures={(x['case'],x['reason']) for x in verify(p)['failures']}
    self.assertTrue(failures-baseline,'Mutation escaped: '+name)
if __name__=='__main__':unittest.main(verbosity=2)

import copy,unittest
from contracts import compile_graph
class GraphContracts(unittest.TestCase):
 def graph(self):return {'text':'This is a bounded local speech test.','nodes':[{'id':t,'type':t,'config':c} for t,c in [('text',{}),('voice',{'reference':'bundled','steps':16,'speed':1,'seed':42}),('master',{'profile':'Balanced'}),('enhance',{'evaluations':16,'denoise':.1})]],'edges':[{'source':'text','target':'voice'},{'source':'voice','target':'master'},{'source':'master','target':'enhance'}]}
 def test_full_chain(self):self.assertEqual([x['type'] for x in compile_graph(self.graph(),set())['ordered']],['text','voice','master','enhance'])
 def test_generation_only(self):
  g=self.graph();g['nodes']=g['nodes'][:2];g['edges']=g['edges'][:1];self.assertEqual(len(compile_graph(g,set())['ordered']),2)
 def test_enhancement_optional(self):
  g=self.graph();g['nodes'].pop();g['edges'].pop();self.assertEqual(len(compile_graph(g,set())['ordered']),3)
 def test_disconnect_rejected(self):
  g=self.graph();g['edges'].pop()
  with self.assertRaisesRegex(ValueError,'Connect every'):compile_graph(g,set())
 def test_wrong_contract_and_cycles_rejected(self):
  for pair in [('voice','enhance'),('enhance','voice'),('text','master')]:
   g=self.graph();g['edges'].append(dict(zip(['source','target'],pair)))
   with self.assertRaises(ValueError):compile_graph(g,set())
 def test_duplicate_rejected(self):
  g=self.graph();g['nodes'].append(copy.deepcopy(g['nodes'][1]))
  with self.assertRaises(ValueError):compile_graph(g,set())
 def test_unknown_voice_rejected(self):
  g=self.graph();g['nodes'][1]['config']['reference']='../../sensitive'
  with self.assertRaises(ValueError):compile_graph(g,set())
 def test_bad_settings_rejected(self):
  for field,value in [('speed',float('nan')),('steps',999),('seed',True)]:
   g=self.graph();g['nodes'][1]['config'][field]=value
   with self.assertRaises(ValueError):compile_graph(g,set())
 def test_unapproved_engine_rejected(self):
  g=self.graph();g['nodes'][1]['type']='shell'
  with self.assertRaises(ValueError):compile_graph(g,set())
 def test_short_text_rejected(self):
  g=self.graph();g['text']='x'
  with self.assertRaises(ValueError):compile_graph(g,set())
 def test_extraneous_settings_rejected(self):
  g=self.graph();g['nodes'][1]['config']['command']='anything'
  with self.assertRaises(ValueError):compile_graph(g,set())
if __name__=='__main__':unittest.main(verbosity=2)

class AdvancedContracts(unittest.TestCase):
 def test_full_generation_range(self):
  g=GraphContracts().graph();g['nodes'][1]['config'].update(steps=17,cross_fade_duration=.1,cfg_strength=2.1,sway_sampling_coef=-.9)
  self.assertEqual(compile_graph(g,set())['ordered'][1]['config']['steps'],17)
 def test_advanced_constraints(self):
  for kind,key,value in [('master','sample_rate',12345),('enhance','solver','unknown'),('master','target_lufs',float('nan')),('enhance','threads',True),('voice','cfg_strength',99)]:
   g=GraphContracts().graph();next(n for n in g['nodes'] if n['type']==kind)['config'][key]=value
   with self.assertRaises(ValueError):compile_graph(g,set())
 def test_custom_transcript_required(self):
  g=GraphContracts().graph();g['nodes'][1]['config']['reference']='upload:test'
  with self.assertRaises(ValueError):compile_graph(g,{'upload:test'})
  g['nodes'][1]['config']['reference_text']='Exact spoken reference.'
  self.assertEqual(compile_graph(g,{'upload:test'})['ordered'][1]['config']['reference_text'],'Exact spoken reference.')

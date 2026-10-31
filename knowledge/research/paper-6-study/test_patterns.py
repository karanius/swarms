import unittest,collections,json
from mine_patterns import neighborhoods,score_rule,family_groups,key

def node(n,t):return {'id':n,'type':t}
def edge(i,s,t,st,tt,sp='out',tp='in'):
 return {'id':str(i),'source':s,'target':t,'sourceType':st,'targetType':tt,'sourcePort':sp,'targetPort':tp,'resolved':True}
class Patterns(unittest.TestCase):
 def test_two_centers_never_join(self):
  g={'id':'g','nodes':[node('a','Center'),node('b','Center'),node('x','X'),node('y','Y')],'edges':[edge(0,'x','a','X','Center'),edge(1,'b','y','Center','Y')]}
  tx,_=neighborhoods(g);centers=[t for t in tx if t['centerType']=='Center'];self.assertEqual(len(centers),2);self.assertTrue(all(len(t['items'])==1 for t in centers))
 def test_duplicate_edges_binary(self):
  e=edge(0,'a','b','A','B');f=dict(e,id='1');g={'id':'g','nodes':[node('a','A'),node('b','B')],'edges':[e,f]};tx,_=neighborhoods(g);self.assertEqual(len(tx[0]['items']),1);self.assertEqual(len(next(iter(tx[0]['edgeWitnesses'].values()))),2)
 def test_shared_neighbor_retained(self):
  g={'id':'g','nodes':[node('a','A'),node('b','B')],'edges':[edge(0,'a','b','A','B','p','q'),edge(1,'a','b','A','B','r','s')]};tx,_=neighborhoods(g);self.assertEqual(len(tx[0]['items']),2)
 def test_unknown_incident_excludes_center(self):
  g={'id':'g','nodes':[node('a','A'),node('b','B')],'edges':[edge(0,'a','b','A','B',None,'in')]};tx,skip=neighborhoods(g);self.assertEqual(tx,[]);self.assertEqual(skip['unknown-endpoint-type-port-or-self-loop'],2)
 def test_zero_degree_not_negative(self):
  tx,skip=neighborhoods({'id':'g','nodes':[node('a','A')],'edges':[]});self.assertFalse(tx);self.assertEqual(skip['no-recorded-incident-edge'],1)
 def test_output_activation_not_inferred(self):
  g={'id':'g','nodes':[{'id':'a','type':'A','outputs':[{'name':'inactive','types':['Message']}]},node('b','B')],'edges':[edge(0,'a','b','A','B')]};tx,_=neighborhoods(g);self.assertFalse(any('inactive' in item for t in tx for item in t['items']))
 def test_confidence_and_center_conditioned_lift(self):
  a=key(('T','in','A','p','q'));b=key(('T','out','B','r','s'));tx=[{'centerType':'T','graph':str(i)} for i in range(4)]+[{'centerType':'W','graph':str(i)} for i in range(4,14)];families={str(i):str(i) for i in range(14)}
  r=score_rule(a,b,{a:[0,1,2],b:[0,1]},tx,families,14);self.assertEqual(r['jointCount'],2);self.assertEqual(r['withoutHeadCount'],1);self.assertAlmostEqual(r['confidence'],2/3);self.assertAlmostEqual(r['lift'],4/3);self.assertAlmostEqual(r['support'],2/14)
 def test_all_duplicate_origins_union_before_filter(self):
  g=[{'id':'x','fixture':True,'sources':[{'repository':'A'},{'repository':'B'}]},{'id':'y','fixture':False,'sources':[{'repository':'B'},{'repository':'C'}]},{'id':'z','fixture':False,'sources':[{'repository':'C'}]}];f=family_groups(g);self.assertEqual(len(set(f.values())),1)
 def test_fp_growth_hand_counted_reference(self):
  import pandas as pd
  from mlxtend.frequent_patterns import fpgrowth,association_rules
  rows=[{'A':True,'B':True}]*5+[{'A':True,'B':False}]*5+[{'A':False,'B':True}]
  df=pd.DataFrame(rows);fi=fpgrowth(df,min_support=(5-.000001)/11,use_colnames=True,max_len=2);rules=association_rules(fi,num_itemsets=11,metric='confidence',min_threshold=0)
  rule=next(r for r in rules.itertuples() if r.antecedents==frozenset(['A']));self.assertAlmostEqual(rule.support,5/11);self.assertAlmostEqual(rule.confidence,.5);self.assertAlmostEqual(rule.lift,.5/(6/11))
if __name__=='__main__':unittest.main()

import unittest,tempfile
from store import Store,Conflict
class StorageTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.s=Store(self.tmp.name)
  self.art={'artifact_id':'example','revision':1,'artifact_type':'dossier','owner_ref':'author','payload':{'result':'controlled fixture'}}
  self.ref=self.s.put(self.art);self.run=self.s.create_run({},60)
 def tearDown(self):self.tmp.cleanup()
 def test_concurrent_stage_lease_rejected(self):
  self.s.claim_stage(self.run,'retrieve','worker-a',60)
  with self.assertRaises(Conflict):self.s.claim_stage(self.run,'retrieve','worker-b',60)
  self.s.release_stage(self.run,'retrieve','worker-a');self.s.claim_stage(self.run,'retrieve','worker-b',60)
 def test_private_store_directory_permissions(self):
  self.assertEqual(self.s.root.stat().st_mode & 0o777,0o700)
 def test_immutable_revision(self):
  self.assertEqual(self.ref,self.s.put(self.art))
  with self.assertRaises(Conflict):self.s.put({**self.art,'payload':{'different':True}})
 def test_compare_and_swap(self):
  self.s.update(self.run,1,'planned',{})
  with self.assertRaises(Conflict):self.s.update(self.run,1,'collecting',{})
 def test_cancel_is_enforced(self):
  self.s.cancel(self.run)
  with self.assertRaises(InterruptedError):self.s.check_bound(self.run)
 def test_expired_deadline_is_enforced(self):
  with self.s.connect() as db:db.execute('UPDATE runs SET deadline=0 WHERE id=?',(self.run,))
  with self.assertRaises(TimeoutError):self.s.check_bound(self.run)
 def test_duplicate_events_cannot_change_meaning(self):
  self.s.event(self.run,'retrieval','failed',{},'fixed');self.s.event(self.run,'retrieval','failed',{},'fixed')
  with self.assertRaises(Conflict):self.s.event(self.run,'retrieval','completed',{},'fixed')
  self.assertEqual(len(self.s.events(self.run)),1)
 def test_review_required_for_exact_revision(self):
  with self.assertRaises(PermissionError):self.s.deliver(self.run,self.ref,'content-strategy','reviewer')
  self.s.approve(self.run,self.ref,'reviewer','accepted',{})
  delivery=self.s.deliver(self.run,self.ref,'content-strategy','reviewer');self.assertEqual(delivery,self.s.deliver(self.run,self.ref,'content-strategy','reviewer'))
  newer=self.s.put({**self.art,'revision':2})
  with self.assertRaises(PermissionError):self.s.deliver(self.run,newer,'content-strategy','reviewer')
 def test_no_self_approval(self):
  self.s.approve(self.run,self.ref,'author','accepted',{})
  with self.assertRaises(PermissionError):self.s.deliver(self.run,self.ref,'content-strategy','author')
 def test_wrong_consumer_cannot_acknowledge(self):
  self.s.approve(self.run,self.ref,'reviewer','accepted',{});d=self.s.deliver(self.run,self.ref,'content-strategy','reviewer')
  with self.assertRaises(PermissionError):self.s.acknowledge(d['key'],'other')
  self.s.acknowledge(d['key'],'content-strategy')
if __name__=='__main__':unittest.main(verbosity=2)

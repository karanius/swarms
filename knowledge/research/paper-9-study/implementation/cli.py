"""Trusted local-user CLI. No listening server or remote authorization boundary."""
import argparse,json,uuid
from pathlib import Path
from controller import Tower
D=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description='Local JSON-driven Market Intelligence tower')
 sub=p.add_subparsers(dest='command',required=True)
 r=sub.add_parser('run');r.add_argument('--request',type=Path,required=True)
 for cmd in ['status','resume','cancel']:
  c=sub.add_parser(cmd);c.add_argument('run_id')
 c=sub.add_parser('feedback');c.add_argument('run_id');c.add_argument('--record',type=Path,required=True)
 c=sub.add_parser('record-effort');c.add_argument('run_id');c.add_argument('--minutes',type=float,required=True);c.add_argument('--event-id',required=True)
 c=sub.add_parser('refresh');c.add_argument('run_id');c.add_argument('--notice',type=Path,required=True)
 c=sub.add_parser('review');c.add_argument('run_id');c.add_argument('--record',type=Path,required=True)
 args=p.parse_args();root=D/'.runtime'/'tower'
 if args.command=='run':
  request=json.loads(args.request.read_text());e=Tower(root,request['profile']);ident=e.create(request['brief'],request.get('source_catalog',[]));print(json.dumps(e.execute(ident),indent=2));return
 from store import Store
 state=Store(root).run(args.run_id);e=Tower(root,state['body']['profile'])
 if args.command=='status':print(json.dumps(state,indent=2))
 elif args.command=='cancel':e.store.cancel(args.run_id);e.finalize_outputs(args.run_id,'cancelled');print('Cancellation recorded; active bounded calls terminate by timeout, no further stage may begin')
 elif args.command=='review':e.submit_review(args.run_id,json.loads(args.record.read_text()));print(json.dumps(e.execute(args.run_id),indent=2))
 elif args.command=='feedback':
  record=json.loads(args.record.read_text());ident=e.revise_from_feedback(args.run_id,record['assessments'],record['recommendation'],record['reason']);print(json.dumps(e.execute(ident),indent=2))
 elif args.command=='record-effort':
  if not 0<=args.minutes<=10080:raise ValueError('Invalid effort minutes')
  e.store.event(args.run_id,'operator-effort','completed',{'attempt_id':'operator-'+args.event_id,'wall_seconds':0,'owner_minutes':args.minutes,'amount':None,'currency':None,'cost_basis':'unknown','reason':'Owner-reported effort, not an automatic measurement'},event_id='operator-'+args.event_id);print('Owner-reported effort recorded without duplicating event identity')
 elif args.command=='refresh':
  parent=state['body']['outputs']['assemble']['dossier'];notice=json.loads(args.notice.read_text())
  if notice.get('parent_dossier_ref')!=parent:raise ValueError('Refresh notice does not match selected parent')
  e.run_id=args.run_id;nref=e.emit('change_notice',notice);brief=e.payload(state['body']['inputs']['brief'])
  ident=e.create(brief,[],flow='refresh',extra_inputs={'notice':nref,'parent':parent});print(json.dumps(e.execute(ident),indent=2))
 elif args.command=='resume':print(json.dumps(e.execute(args.run_id),indent=2))
if __name__=='__main__':main()

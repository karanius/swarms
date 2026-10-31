import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {seedMembers,analyzeCandidate} from '../../../frontend/candidate-explorer/model.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..'),base=resolve(root,'knowledge/research/paper-6-corpus');
const indexBytes=readFileSync(resolve(base,'patterns/index.json')),index=JSON.parse(indexBytes),seen=new Set(),rows=[];
for(const rule of index.rules){
 const pair=JSON.stringify([rule.body,rule.head].sort());if(seen.has(pair))continue;seen.add(pair);
 const w=rule.representative,bytes=readFileSync(resolve(base,'topology/graphs',w.graph+'.json')),g=JSON.parse(bytes),members=seedMembers(g,w),c=analyzeCandidate(g,members),s=new Set(members);
 // Independent predicates on each source edge audit the shared UI model's partition.
 for(const e of g.edges){const actual=c.internal.includes(e)?'internal':c.incoming.includes(e)?'incoming':c.outgoing.includes(e)?'outgoing':'outside';const expected=s.has(e.source)?s.has(e.target)?'internal':'outgoing':s.has(e.target)?'incoming':'outside';assert.equal(actual,expected)}
 assert(c.members.every(n=>g.nodes.some(x=>x.id===n.id)));assert(w.previewEdgeIds.every(id=>c.internal.some(e=>e.id===id)));assert.deepEqual(c.sources,g.sources);
 rows.push({association:rule.id,graph:g.id,graphFileSha256:createHash('sha256').update(bytes).digest('hex'),name:g.name,members,internal:c.internal.length,incoming:c.incoming.length,outgoing:c.outgoing.length,requiredUnwired:c.unconnectedInputs.filter(p=>p.required).length,terminalDeclarations:c.terminalOutputs.length,unknownIncident:c.unresolved.length,connected:c.checks[1].status,acyclic:c.checks[2].status,status:c.status});
}
const result={scope:'One ranked representative for each unordered frequent feature pair; not all witnesses, not independent evaluation',patternIndexSha256:createHash('sha256').update(indexBytes).digest('hex'),modelSha256:createHash('sha256').update(readFileSync(resolve(root,'frontend/candidate-explorer/model.mjs'))).digest('hex'),stats:{candidates:rows.length,withCrossingWires:rows.filter(r=>r.incoming+r.outgoing>0).length,withRequiredUnwired:rows.filter(r=>r.requiredUnwired>0).length,withUnresolvedIncident:rows.filter(r=>r.unknownIncident>0).length,connected:rows.filter(r=>r.connected==='observed').length,acyclic:rows.filter(r=>r.acyclic==='observed').length},candidates:rows};
mkdirSync(resolve(base,'candidates'),{recursive:true});writeFileSync(resolve(base,'candidates/audit.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result.stats,null,2));

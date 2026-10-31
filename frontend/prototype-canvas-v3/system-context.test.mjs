import test from 'node:test';
import assert from 'node:assert/strict';
import {buildSystemContext,projectCanvasGraph,sanitizeContextValue,readContextCheckpoints,saveContextCheckpoint,CONTEXT_STORAGE_KEY,createContextChannel} from './system-context.mjs';
const template={id:'swift',kind:'agent-template',version:'fixture',resources:{model:{providerRef:'api-proxy'}},architecture:[{piece:'Library tools',tools:['Search items'],status:'planned'}],documents:[{path:'knowledge/instance-machine/domain-model.md',sha256:'fixture'}],assembly:{scriptRef:'assemble.mjs',status:'implemented'},deployment:{launcherRef:'deploy.mjs',status:'implemented'}};
const inputs={planes:['Flows','Composite Components','Components'],catalog:[{name:'Input Output',items:[{id:'ChatInput',name:'Chat Input'}]}],officialTemplates:{items:[]},swiftTemplate:template};
test('shared consumer channel publishes isolated redacted snapshots and unsubscribes cleanly',()=>{
 const channel=createContextChannel();let observed;let calls=0;
 assert.equal(channel.reader.getSnapshot(),null);
 channel.reader.subscribe(()=>{throw new Error('isolated consumer');});
 const unsubscribe=channel.reader.subscribe(value=>{observed=value;calls++;value.changed=true;});
 channel.publish({kind:'system-context',access_token:'private-token',workingRevision:1});
 assert.equal(calls,1);assert.equal(observed.workingRevision,1);
 assert.equal(channel.reader.getSnapshot().changed,undefined);
 assert.ok(!JSON.stringify(channel.reader.getSnapshot()).includes('private-token'));
 const copy=channel.reader.getSnapshot();copy.workingRevision=99;
 assert.equal(channel.reader.getSnapshot().workingRevision,1);
 unsubscribe();channel.publish({workingRevision:2});assert.equal(calls,1);
 channel.clear();assert.equal(channel.reader.getSnapshot(),null);
});
const node={id:'agent-one',data:{type:'Agent',node:{display_name:'Agent',template:{api_key:{value:'private-api-key',type:'str',password:true},system_prompt:{value:'Help with a task'},max_tokens:{value:1000},code:{value:'private embedded source'},headers:{value:{Authorization:'Bearer private-bearer',nested:{refresh_token:'private-refresh'}}},endpoint:{value:'https://user:private-password@example.test/path?api_key=private-query'}}}},position:{x:10,y:20}};
function memoryStorage(){let value=null;return {getItem:()=>value,setItem:(key,next)=>{assert.equal(key,CONTEXT_STORAGE_KEY);value=next;},raw:()=>value};}
test('projection retains graph configuration and connections but exports credential references, not secrets or code',()=>{
 const original=structuredClone(node);
 const graph=projectCanvasGraph({nodes:[node],edges:[{id:'edge',source:'a',target:'b',sourceHandle:'message',targetHandle:'input'}]});
 const text=JSON.stringify(graph);
 for(const secret of ['private-api-key','private-bearer','private-refresh','private-password','private-query','private embedded source'])assert.ok(!text.includes(secret),secret);
 assert.equal(graph.nodes[0].configuration.max_tokens,1000);
 assert.equal(graph.nodes[0].configuration.system_prompt,'Help with a task');
 assert.equal(graph.nodes[0].configuration.api_key.status,'not-exported');
 assert.equal(graph.connections[0].sourceHandle,'message');
 assert.deepEqual(node,original);
});
test('system context covers all planes and available definitions while preserving uncertainty',()=>{
 const context=buildSystemContext({...inputs,nativeGraph:{nodes:[node],edges:[]},planeGraphs:{Flows:{nodes:[{id:'custom',data:{label:'Report',customItemId:'saved-report'},position:{x:0,y:0}}],edges:[]}},instancePositions:{Flows:{x:31,y:44}},activePlane:'Flows',nativeContext:{catalog:{componentTypes:['ChatInput','Agent']},isBuilding:true}});
 assert.equal(context.kind,'system-context');
 assert.equal(context.workspace.activePlane,'Flows');
 assert.equal(context.workspace.canvases.Flows.layout.instancePosition.x,31);
 assert.equal(context.workspace.canvases.Components.nodes[0].id,'agent-one');
 assert.equal(context.library.components[0].availability,'available-in-connected-catalog');
 assert.equal(context.library.layers[1].label,'Composite');
 assert.equal(context.validation.schema.status,'not-integrated');
 assert.equal(context.discovery.requirements.status,'documented-not-normalized');
 assert.equal(context.runtime.activity,'building');
 assert.equal(context.templates[0].documents[0].sha256,'fixture');
 assert.ok(!JSON.stringify(context).includes('private-api-key'));
});
test('fresh graph, layout, library and deployment inputs change the live projection without mutating the prior projection',()=>{
 const first=buildSystemContext(inputs);
 const second=buildSystemContext({...inputs,nativeGraph:{nodes:[node],edges:[]},customItems:[{id:'saved',name:'Saved design',plane:'Composite Components',status:'design-saved',assembly:{nodes:[node],edges:[]}}],nativeContext:{activeInstance:{id:'swift-live'},knownInstances:[{id:'swift-live',templateRef:{id:'swift',version:'fixture'},deployment:{runtime:'langflow',flowId:'flow-live'}}]}});
 assert.equal(first.workspace.canvases.Components.nodes.length,0);
 assert.equal(second.workspace.canvases.Components.nodes.length,1);
 assert.equal(second.library.customItems.length,1);
 assert.equal(second.instances.activeInstanceRef,'swift-live');
 assert.equal(second.deployments.records[0].flowId,'flow-live');
});
test('explicit checkpoints are versioned, immutable and sanitized again at the storage boundary',()=>{
 const storage=memoryStorage();
 const context=buildSystemContext(inputs);context.untrusted={access_token:'private-checkpoint-token'};
 const first=saveContextCheckpoint(storage,context,{id:'one',createdAt:'first'});
 context.workspace.activePlane='Flows';
 const second=saveContextCheckpoint(storage,context,{id:'two',createdAt:'second'});
 assert.equal(first.checkpoint.version,1);assert.equal(second.checkpoint.version,2);
 const saved=readContextCheckpoints(storage);
 assert.equal(saved.checkpoints[0].context.workspace.activePlane,'Components');
 assert.equal(saved.checkpoints[1].context.workspace.activePlane,'Flows');
 assert.ok(!storage.raw().includes('private-checkpoint-token'));
});
test('damaged and full checkpoint storage is preserved, with visible errors instead of silent replacement',()=>{
 let writes=0;const damaged={getItem:()=>'{bad',setItem:()=>writes++};
 assert.throws(()=>saveContextCheckpoint(damaged,buildSystemContext(inputs)),/preserved/);assert.equal(writes,0);
 const full={getItem:()=>null,setItem:()=>{throw new Error('quota exceeded');}};
 assert.throws(()=>saveContextCheckpoint(full,buildSystemContext(inputs)),/quota/);
 const cyclic={};cyclic.self=cyclic;assert.throws(()=>sanitizeContextValue(cyclic),/circular/);
});

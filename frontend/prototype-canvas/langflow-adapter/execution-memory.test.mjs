import test from 'node:test';
import assert from 'node:assert/strict';
import {configureExecutionMemory,prepareIsolatedRun} from './execution-memory.mjs';
const nodes=[{id:'input',data:{type:'ChatInput',node:{template:{session_id:{value:'old-session',load_from_db:true}}}}},{id:'research',data:{type:'Agent',node:{template:{n_messages:{value:100},context_id:{value:'shared'},system_prompt:{value:'Research carefully'}}}}},{id:'verify',data:{type:'Agent',node:{template:{n_messages:{value:100},context_id:{value:'shared'}}}}},{id:'output',data:{type:'ChatOutput',node:{template:{session_id:{value:'old-session'}}}}}];
test('every run has a distinct session shared by its input and output',()=>{
 const a=prepareIsolatedRun(nodes,()=> 'first'),b=prepareIsolatedRun(nodes,()=> 'second');
 assert.notEqual(a.session,b.session);
 for(const i of [0,3])assert.equal(a.nodes[i].data.node.template.session_id.value,a.session);
 assert.equal(a.nodes[0].data.node.template.session_id.load_from_db,false);
});
test('agents disable automatic history and have distinct contexts without changing prompts',()=>{
 const run=prepareIsolatedRun(nodes,()=> 'first');
 for(const i of [1,2])assert.equal(run.nodes[i].data.node.template.n_messages.value,0);
 assert.notEqual(run.nodes[1].data.node.template.context_id.value,run.nodes[2].data.node.template.context_id.value);
 assert.equal(run.nodes[1].data.node.template.system_prompt.value,'Research carefully');
 assert.equal(nodes[1].data.node.template.n_messages.value,100);
});
test('library snapshots retain policy configuration without carrying an execution session',()=>{
 const run=prepareIsolatedRun(nodes,()=> 'first');
 const snapshot=configureExecutionMemory(run.nodes);
 assert.equal(snapshot[0].data.node.template.session_id.value,'');
 assert.equal(snapshot[1].data.node.template.context_id.value,'');
 assert.equal(snapshot[1].data.node.template.n_messages.value,0);
});
test('unsupported agent definitions fail explicitly rather than silently load history',()=>{
 assert.throws(()=>configureExecutionMemory([{id:'unknown',data:{type:'Agent',node:{template:{}}}}]),/history control/);
});

test('fresh-session runs forward the actual canvas input instead of an empty message',()=>{
 const input=[{id:'question',data:{type:'ChatInput',node:{template:{input_value:{value:'SWARM_SENTINEL_1'},session_id:{value:''}}}}}];
 const run=prepareIsolatedRun(input,()=> 'forward');
 assert.equal(run.inputValue,'SWARM_SENTINEL_1');
});

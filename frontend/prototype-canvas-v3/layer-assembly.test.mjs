import test from 'node:test';
import assert from 'node:assert/strict';
import {packageAssembly,assertDAG,compositeNode,canConnectComposite} from './layer-assembly.mjs';
function node(id,type){return {id,type:'genericNode',position:{x:0,y:0},data:{id,type,node:{display_name:type,template:{input_value:{display_name:'Input',type:'str',input_types:['Message'],required:true,value:''}},outputs:[{name:type==='Agent'?'response':'message',types:['Message']}]}}};}
const graph={nodes:[node('in','ChatInput'),node('agent','Agent'),node('out','ChatOutput')],edges:[{id:'a',source:'in',target:'agent',data:{sourceHandle:{name:'message',output_types:['Message']},targetHandle:{fieldName:'input_value',inputTypes:['Message']}}},{id:'b',source:'agent',target:'out',data:{sourceHandle:{name:'response',output_types:['Message']},targetHandle:{fieldName:'input_value',inputTypes:['Message']}}}],viewport:{x:0,y:0,zoom:1}};
const options={id:'composite-a',createdAt:'fixture'};
test('packaging preserves child identities and original graph, exposes entry/exit ports',()=>{
 const before=structuredClone(graph),item=packageAssembly(graph,['in','agent','out'],'Conversation',options);
 assert.deepEqual(graph,before);
 assert.deepEqual(item.realization.childNodeIds,['in','agent','out']);
 assert.deepEqual(item.realization.order,['in','agent','out']);
 assert.equal(item.contract.inputs[0].internal.nodeId,'in');
 assert.equal(item.contract.outputs[0].internal.nodeId,'out');
 assert.equal(item.validation.behavior,'not-tested');
 const upper=compositeNode(item,{id:'upper-a'});
 assert.deepEqual(upper.data.childNodeIds,['in','agent','out']);
 item.assembly.nodes[0].data.node.display_name='Saved library edit';
 assert.equal(graph.nodes[0].data.node.display_name,'ChatInput');
});
test('partial selection maps incoming and outgoing cut edges to exact internal ports',()=>{
 const item=packageAssembly(graph,['agent'],'Worker',options);
 assert.equal(item.assembly.edges.length,0);
 assert.deepEqual(item.contract.inputs[0].internal,{nodeId:'agent',port:'input_value'});
 assert.deepEqual(item.contract.outputs[0].internal,{nodeId:'agent',port:'response'});
 assert.equal(item.contract.inputs.length,1);assert.equal(item.contract.outputs.length,1);
});
test('invalid cyclic, disconnected, missing, or template selections cannot become DAG composites',()=>{
 assert.throws(()=>packageAssembly({...graph,edges:[...graph.edges,{id:'back',source:'out',target:'in'}]},['in','agent','out'],'Loop',options),/cycle/);
 assert.throws(()=>packageAssembly(graph,['in','out'],'Disconnected',options),/connected group/);
 assert.throws(()=>packageAssembly(graph,['missing'],'Missing',options),/no longer/);
 assert.throws(()=>packageAssembly({nodes:[{...node('t','SwiftTemplate'),type:'swiftTemplate'}],edges:[]},['t'],'Template',options),/executable Langflow components/);
});
test('composite wiring enforces type compatibility and rejects back edges',()=>{
 const item=packageAssembly(graph,['agent'],'Worker',options);
 const a=compositeNode(item,{id:'a'}),b=compositeNode(item,{id:'b'});
 const connection={source:'a',sourceHandle:'output-0',target:'b',targetHandle:'input-0'};
 assert.equal(canConnectComposite([a,b],[],connection),true);
 assert.throws(()=>canConnectComposite([a,b],[{id:'b-to-a',source:'b',target:'a'}],connection),/cycle/);
 b.data.contract.inputs[0].dataTypes=['DataFrame'];
 assert.throws(()=>canConnectComposite([a,b],[],connection),/incompatible/);
 assert.deepEqual(assertDAG(graph.nodes,graph.edges),['in','agent','out']);
});

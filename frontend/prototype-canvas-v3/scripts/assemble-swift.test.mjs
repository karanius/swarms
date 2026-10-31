import test from 'node:test';
import assert from 'node:assert/strict';
import {assembleSwift} from './assemble-swift.mjs';
import {deploySwift} from './deploy-swift.mjs';
const template={kind:'agent-template',id:'swift',version:'test',resources:{model:{provider:'example',name:'test'}}};
const definitions=Object.fromEntries(['ChatInput','Agent','ChatOutput'].map(type=>[type,{template:{model:{value:''},system_prompt:{value:''},n_messages:{value:0}}}]));
test('assembly is repeatable, preserves library definitions and wires both boundaries',()=>{
 const before=structuredClone(definitions);let counter=0;
 const instance=assembleSwift(template,definitions,()=>String(++counter));
 counter=0;assert.deepEqual(instance,assembleSwift(template,definitions,()=>String(++counter)));
 assert.deepEqual(before,definitions);
 assert.equal(instance.data.nodes.length,3);assert.equal(instance.data.edges.length,2);
 assert.equal(instance.data.edges[1].data.sourceHandle.name,'response');
 assert.throws(()=>assembleSwift(template,{}),/Missing Langflow component/);
});
test('deployment creates an independent flow without changing the template or assembled instance',async()=>{
 const instance=assembleSwift(template,definitions);const before=structuredClone(instance);let body;
 const deployed=await deploySwift(instance,async(url,options)=>{assert.equal(url,'/api/v1/flows/');body=JSON.parse(options.body);return {ok:true,json:async()=>({id:'new-flow',...body})};});
 assert.deepEqual(instance,before);assert.equal(deployed.deployment.flowId,'new-flow');assert.equal(deployed.state,'deployed');
 await assert.rejects(deploySwift(instance,async()=>({ok:false,status:403})),/deployment failed/);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { buildBaseline } from './composition-baseline.mjs';

function fixture() {
 const input = {type:'str',input_types:['Message'],value:''};
 return {
  ChatInput:{template:{input_value:structuredClone(input)},outputs:[{name:'message',types:['Message']}]},
  Agent:{template:{model:{type:'model',input_types:['LanguageModel'],value:''},system_prompt:{value:''},n_messages:{value:20},max_iterations:{value:15},input_value:structuredClone(input),stream:{value:true},api_key:{password:true,value:''}},outputs:[{name:'response',types:['Message']}]},
  ChatOutput:{template:{input_value:structuredClone(input)},outputs:[]}
 };
}
test('deterministic assembly preserves definitions and uses current port types', () => {
 const definitions=fixture(); const before=structuredClone(definitions);
 const a=buildBaseline(definitions); const b=buildBaseline({io:definitions});
 assert.deepEqual(a,b); assert.deepEqual(definitions,before);
 assert.equal(a.method,'fixed-recipe'); assert.equal(a.evidence.execution,'not-run');
 const fields=a.instance.data.nodes[1].data.node.template;
 assert.equal(fields.n_messages.value,0); assert.equal(fields.max_iterations.value,1); assert.equal(fields.stream.value,false);
 assert.deepEqual(fields.model.value,[{provider:'OpenAI Compatible',name:'gpt-6.1-sol'}]);
 assert.equal(a.instance.data.edges.length,2);
 assert.deepEqual(a.instance.data.edges[0].data.sourceHandle.output_types,['Message']);
});
test('rejects incompatible or missing ports and missing model definition', () => {
 const definitions=fixture(); definitions.Agent.template.input_value.input_types=['Data'];
 assert.throws(()=>buildBaseline(definitions),/Incompatible required edge/);
 delete definitions.Agent.template.model;
 assert.throws(()=>buildBaseline(definitions),/Missing Agent field: model/);
});
test('refuses credential material before serializing and metadata contains hashes only', () => {
 const definitions=fixture(); definitions.Agent.template.api_key.value='private-example';
 assert.throws(()=>buildBaseline(definitions),/Nonempty credential material/);
 definitions.Agent.template.api_key.value='';
 const artifact=buildBaseline(definitions);
 assert.deepEqual(Object.keys(artifact.evidence.definitionHashes),['ChatInput','Agent','ChatOutput']);
 assert.ok(Object.values(artifact.evidence.definitionHashes).every(value=>/^[a-f0-9]{64}$/.test(value)));
 assert.ok(!JSON.stringify(artifact.evidence).includes('template'));
});

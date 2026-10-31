import test from 'node:test';
import assert from 'node:assert/strict';
import {validateArtifact,createDesignArtifact,createLayerArtifact,captureCanvasArtifact} from './research-artifact-model.mjs';

test('design factory explicitly marks proposed stages and feedback as synthetic',()=>{
 const artifact=createDesignArtifact();
 assert.equal(artifact.provenance.kind,'synthetic-design');
 assert.match(artifact.provenance.label,/not an implemented or proven/);
 assert.deepEqual(artifact.nodes.map(node=>node.id),['intent','requirements','resolve','select','compose','check','promote','reassess']);
 assert.equal(artifact.edges.filter(edge=>edge.kind==='feedback').length,2);
});
test('normalization strips arbitrary config and returns an independent clone',()=>{
 const input=createLayerArtifact(); input.auth='private'; input.nodes[0].data={code:'private',api_key:'private'};input.provenance.settings={secret:'private'};
 const result=validateArtifact(input);
 assert.ok(!JSON.stringify(result).includes('private'));
 result.nodes[0].position.x=99;
 assert.equal(input.nodes[0].position.x,0);
 assert.deepEqual(Object.keys(result),['schemaVersion','kind','title','provenance','layers','nodes','edges']);
});
test('layer membership reuses component identity rather than duplicating nodes',()=>{
 const artifact=createLayerArtifact();
 assert.deepEqual(artifact.layers.map(layer=>layer.order),[0,1]);
 const membership=artifact.edges.filter(edge=>edge.kind==='membership');
 assert.deepEqual(membership.map(edge=>edge.source),['receive','process','respond']);
 assert.ok(membership.every(edge=>edge.target==='summary-composite'));
 assert.equal(artifact.nodes.length,4);
});
test('rejects malformed, oversized, duplicate and dangling graphs',()=>{
 for(const mutate of [a=>{a.layers=[];},a=>{a.nodes[0].position.x=Infinity;},a=>{a.nodes[0].layer='missing';},a=>{a.nodes[1].id=a.nodes[0].id;},a=>{a.edges[0].source='missing';},a=>{a.edges[0].kind='execute';},a=>{a.layers[1].id=a.layers[0].id;},a=>{a.nodes[0].label='x'.repeat(161);},a=>{a.nodes=Array(101).fill(a.nodes[0]);},a=>{a.edges=Array(501).fill(a.edges[0]);}]){
  const value=createLayerArtifact();mutate(value);assert.throws(()=>validateArtifact(value));
 }
});
test('canvas labels allow only exact public component types',()=>{
 const types=['ChatInput','Agent','ChatOutput','private','__proto__'];
 const artifact=captureCanvasArtifact({nodes:types.map((type,index)=>({id:String(index),position:{x:index,y:0},data:{type,label:'private',template:{code:'private'}}})),edges:[]});
 assert.deepEqual(artifact.nodes.map(node=>node.label),['Chat Input','Agent','Chat Output','Node 4','Node 5']);
 assert.ok(!JSON.stringify(artifact).includes('private'));
});
test('canvas capture preserves topology and positions without leaking ids, labels or native data',()=>{
 const graph={nodes:[{id:'secret-first',label:'credential',position:{x:10,y:20},data:{node:{template:{api_key:{value:'private'}}}}},{id:'secret-second',position:{x:40,y:50}}],edges:[{id:'secret-edge',source:'secret-first',target:'secret-second',sourceHandle:'private'}],settings:{password:'private'}};
 const before=structuredClone(graph);const artifact=captureCanvasArtifact(graph);
 assert.deepEqual(graph,before);
 assert.equal(artifact.provenance.kind,'canvas-snapshot');
 assert.deepEqual(artifact.nodes[0].position,{x:10,y:20});
 assert.deepEqual(artifact.edges,[{id:'canvas-edge-1',source:'canvas-node-1',target:'canvas-node-2',kind:'data'}]);
 assert.ok(!/private|secret|credential/.test(JSON.stringify(artifact)));
 graph.edges[0].target='missing';assert.throws(()=>captureCanvasArtifact(graph));
});

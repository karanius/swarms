import test from 'node:test';
import assert from 'node:assert/strict';
import {layerSceneModel} from './layer-scene-model.mjs';
import {packageAssembly,compositeNode} from './layer-assembly.mjs';
const node=(id,type)=>({id,type:'genericNode',position:{x:0,y:0},data:{id,type,node:{display_name:type,template:{input_value:{value:'',required:true,input_types:['Message']}},outputs:[{name:'message',types:['Message']}]}}});
test('three-dimensional planes project the same identities and distinguish data-flow from membership',()=>{
 const graph={nodes:[node('a','ChatInput'),node('b','ChatOutput')],edges:[{id:'ab',source:'a',target:'b'}]};
 const item=packageAssembly(graph,['a','b'],'Example',{id:'example',createdAt:'fixture'}),upper={nodes:[compositeNode(item,{id:'upper'})],edges:[]};
 const before=structuredClone(graph),model=layerSceneModel(graph,upper,[item]);
 assert.deepEqual(model.components.map(node=>node.id),['a','b']);
 assert.deepEqual(model.composites[0].children,['a','b']);
 assert.equal(model.edges.filter(edge=>edge.kind==='data-flow').length,1);
 assert.equal(model.edges.filter(edge=>edge.kind==='membership').length,2);
 assert.ok(model.composites[0].position[1]>model.components[0].position[1]);
 assert.deepEqual(graph,before);
});

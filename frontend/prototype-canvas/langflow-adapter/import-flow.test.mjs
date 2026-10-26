import test from 'node:test';
import assert from 'node:assert/strict';
import {parseFlowImport} from './import-flow.mjs';
const node=id=>({id,type:'genericNode',position:{x:0,y:0},data:{type:'ChatInput',node:{template:{}}}});
test('imports a named Langflow graph with its definitions and connections intact',()=>{
 const flow={name:'Example',data:{nodes:[node('a'),node('b')],edges:[{id:'edge',source:'a',target:'b'}]}};
 assert.deepEqual(parseFlowImport(JSON.stringify(flow)),flow);
});
test('rejects malformed graphs before any canvas mutation',()=>{
 for(const value of [{data:{}},{data:{nodes:[node('a'),node('a')],edges:[]}},{data:{nodes:[node('a')],edges:[{source:'a',target:'missing'}]}}])assert.throws(()=>parseFlowImport(JSON.stringify(value)));
});

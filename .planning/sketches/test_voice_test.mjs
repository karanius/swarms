import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('./001-santa-audition/live.js',import.meta.url),'utf8');
const handler=source.slice(source.indexOf("dom('generateVoiceTest').onclick=async()=>"),source.indexOf("dom('keepTestVoice').onclick="));
function fixture(reject=false){
 const elements={testSentence:{value:'So now.. I must give you gifts to make up for my mistakes with your father.',setAttribute(){}},testStatus:{textContent:''},testResult:{textContent:'Previous recordings'},generateVoiceTest:{},characterName:{value:'Santa'}};
 const calls=[];const context={dom:id=>elements[id],testBusy:false,testRecordId:'candidate',lastRecords:[{id:'candidate',request:{seed:65,steps:10,guidance:2}}],tracked:['candidate'],persistTestDraft(){},saveTestRuns(){},refresh:async()=>{},testRuns:[],voiceWordCount:text=>(text.match(/[\p{L}\p{N}]+(?:['’][\p{L}\p{N}]+)*/gu)||[]).length,api:async(path,q)=>{calls.push({path,q});if(path.endsWith('/profile'))return {id:'profile'};if(reject)throw Error('Use exactly one sentence per take');return {id:'result'}}};vm.createContext(context);vm.runInContext(handler,context);return {elements,calls,context};
}
const good=fixture();await good.elements.generateVoiceTest.onclick();assert.equal(good.calls[1].q.text,'So now… I must give you gifts to make up for my mistakes with your father.');assert.equal(good.context.testRuns[0].source,'candidate');assert.equal(good.calls[1].q.profile_id,'profile');
const bad=fixture(true);await bad.elements.generateVoiceTest.onclick();assert.match(bad.elements.testStatus.textContent,/exactly one sentence/);assert.equal(bad.elements.testResult.textContent,'Previous recordings');assert.equal(bad.elements.generateVoiceTest.disabled,false);
console.log('PASS: pause normalisation, reference binding, persistent error location, preserved recordings, retry enabled');

for(const count of [35,36]){const f=fixture();f.elements.testSentence.value=Array(count).fill('word').join(' ');await f.elements.generateVoiceTest.onclick();assert.equal(f.calls.length,count===35?2:0);if(count===36)assert.match(f.elements.testStatus.textContent,/35 words/)}
console.log('PASS: 35 words accepted; 36 rejected before any request');

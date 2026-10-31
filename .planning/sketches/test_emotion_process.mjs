import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const source=fs.readFileSync('.planning/sketches/001-santa-audition/checkpoints.js','utf8');const code=source.slice(source.indexOf('function checkpointProcess('),source.indexOf('function openEmotionCheckpoint('));const context={};vm.createContext(context);vm.runInContext(code,context);
const cases=[
 [null,1,'Inputs saved',false,false],
 [{actor_state:'running'},2,'Generating actor line',false,false],
 [{actor_state:'failed'},2,'Actor generation failed',false,false],
 [{actor_state:'saved',actor_words_checked:false},2,'Actor words need review',true,false],
 [{actor_state:'saved',actor_words_checked:true},2,'Actor ready for your approval',true,false],
 [{actor_state:'saved',conversion_state:'running'},3,'Creating Santa from approved acting',true,false],
 [{actor_state:'saved',conversion_state:'failed'},3,'Santa conversion needs attention',true,false],
 [{actor_state:'saved',conversion_state:'saved'},3,'Santa ready to review',true,true],
 [{actor_state:'saved',conversion_state:'saved',final_decision:'keep'},3,'Santa result kept',true,true]
];
for(const [input,phase,status,actor,santa] of cases){const state=context.checkpointProcess(input);assert.equal(state.phase,phase);assert.equal(state.status,status);assert.equal(state.actor,actor);assert.equal(state.santa,santa);assert.ok(state.next)}
console.log('PASS: all nine checkpoint states identify the recording role and a next action; unfinished actor audio is never presented as Santa.');

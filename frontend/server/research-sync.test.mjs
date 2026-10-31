import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync as exec} from 'node:child_process';
import {createResearchStore} from './research-sync.mjs';
test('research saves detect conflicts and push only research, preserving staged work',async()=>{
 const base=await mkdtemp(join(tmpdir(),'research-sync-')),root=join(base,'repo'),remote=join(base,'remote.git');
 const git=(...args)=>exec('git',args,{cwd:root,stdio:'pipe'}).toString();let store;
 try{exec('git',['init','--bare',remote]);exec('git',['init',root]);git('config','user.email','test@example.invalid');git('config','user.name','Research test');await writeFile(join(root,'unrelated.txt'),'original');git('add','.');git('commit','-m','Initial');git('remote','add','origin',remote);git('push','-u','origin','HEAD');
 await writeFile(join(root,'unrelated.txt'),'keep staged');git('add','unrelated.txt');
 store=createResearchStore(root,{pushDelay:60000});const document={schemaVersion:1,papers:[{id:'test',title:'Test paper',content:[]}]};
 const saved=await store.save(document,null);assert.ok(saved.revision);await assert.rejects(store.save(document,null),error=>error.status===409);
 const result=await store.publish();assert.equal(result.state,'synced');assert.equal(git('show','--format=','--name-only','HEAD').trim(),'knowledge/research/papers.json');assert.equal(git('diff','--cached','--name-only').trim(),'unrelated.txt');
 assert.deepEqual(JSON.parse(await readFile(join(root,'knowledge/research/papers.json'),'utf8')),document);
 assert.equal(exec('git',['--git-dir='+remote,'rev-parse','HEAD']).toString().trim(),git('rev-parse','HEAD').trim());
 }finally{store?.close();await rm(base,{recursive:true,force:true});}
});

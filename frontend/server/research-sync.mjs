import {readFile,writeFile,mkdir,rename} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash} from 'node:crypto';
const exec=promisify(execFile);
export function createResearchStore(root,{pushDelay=5000}={}){
 const relative='knowledge/research/papers.json',file=resolve(root,relative);
 let queue=Promise.resolve(),timer,status={state:'idle',message:'No research changes queued.'};
 const git=(...args)=>exec('git',args,{cwd:root,timeout:60000,maxBuffer:1024*1024});
 const revision=text=>createHash('sha256').update(text).digest('hex');
 async function read(){try{const text=await readFile(file,'utf8');return {exists:true,revision:revision(text),document:JSON.parse(text)};}catch(error){if(error.code!=='ENOENT')throw error;return {exists:false,revision:null,document:{schemaVersion:1,papers:[]}};}}
 function serialize(operation){const work=queue.then(operation);queue=work.catch(()=>{});return work;}
 async function publish(){return serialize(async()=>{clearTimeout(timer);status={state:'pushing',message:'Pushing research to GitHub…'};try{
  await git('add','--',relative);
  const diff=await git('diff','--cached','--numstat','--',relative);
  if(diff.stdout.trim())await git('commit','--only','-m','Save research papers','--',relative);
  await git('push','origin','HEAD');
  const head=await git('rev-parse','HEAD');status={state:'synced',message:'Saved to disk and pushed to GitHub.',commit:head.stdout.trim(),syncedAt:new Date().toISOString()};
 }catch{status={state:'error',message:'Saved to disk; GitHub push failed. Retry when the connection or repository is ready.'};}return {...status};});}
 async function save(document,baseRevision){return serialize(async()=>{
  if(document?.schemaVersion!==1||!Array.isArray(document.papers)||document.papers.some(p=>typeof p.id!=='string'||typeof p.title!=='string'||!Array.isArray(p.content)))throw Object.assign(Error('Invalid research document.'),{status:400});
  const current=await read();if(current.revision!==baseRevision)throw Object.assign(Error('Research changed on disk. Reload to review it before saving.'),{status:409});
  const text=JSON.stringify({schemaVersion:1,papers:document.papers},null,2)+'\n';
  if(current.revision===revision(text))return {...current,status:{...status}};
  await mkdir(dirname(file),{recursive:true});const temporary=file+'.tmp';await writeFile(temporary,text,'utf8');await rename(temporary,file);
  clearTimeout(timer);status={state:'queued',message:'Saved to disk. GitHub push queued.'};timer=setTimeout(()=>{publish();},pushDelay);timer.unref?.();
  return {exists:true,revision:revision(text),document:JSON.parse(text),status:{...status}};
 });}
 return {read,save,publish,status:()=>({...status}),close:()=>clearTimeout(timer)};
}
export function researchSyncPlugin(root){const store=createResearchStore(root);return {name:'research-repository-sync',configureServer(server){server.httpServer?.once('close',()=>store.close());server.middlewares.use('/research-api',async(req,res)=>{
 const reply=(code,value)=>{res.statusCode=code;res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');res.end(JSON.stringify(value));};
 try{
  const host=req.headers.host??'';if(!/^(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$/.test(host)||req.headers['sec-fetch-site']==='cross-site'||(req.headers.origin&&req.headers.origin!=='http://'+host)){reply(403,{error:'Local same-origin requests only.'});return;}
  if(req.method==='GET'){reply(200,{...await store.read(),status:store.status()});return;}
  if(req.method!=='PUT'&&req.method!=='POST'){reply(405,{error:'Method not allowed.'});return;}
  if(!req.headers['content-type']?.startsWith('application/json')){reply(415,{error:'JSON required.'});return;}
  let text='';for await(const chunk of req){text+=chunk;if(Buffer.byteLength(text)>5*1024*1024){reply(413,{error:'Research collection exceeds the 5 MB request limit.'});return;}}
  const body=JSON.parse(text||'{}');if(req.method==='POST'&&req.url==='/push'){reply(200,{status:await store.publish()});return;}
  if(req.method==='PUT'){reply(200,await store.save(body.document,body.baseRevision??null));return;}
  reply(404,{error:'Unknown research action.'});
 }catch(error){reply(error.status??500,{error:error.status?error.message:'Research storage is unavailable. Your browser draft is preserved.'});}
 });}};}

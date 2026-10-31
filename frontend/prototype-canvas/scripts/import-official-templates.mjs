// Downloads data only. Never imports or executes component Python code.
import {mkdir,writeFile,readFile,readdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {parseFlowImport} from '../langflow-adapter/import-flow.mjs';

const root=fileURLToPath(new URL('../../',import.meta.url));
const output=path.join(root,'public/langflow-templates/official');
const sourcePath='src/backend/base/langflow/initial_setup/starter_projects';
const repo='https://github.com/langflow-ai/langflow';
async function get(url){const response=await fetch(url,{headers:{'User-Agent':'Swarms-template-importer'},signal:AbortSignal.timeout(30000)});if(!response.ok)throw Error(`Download failed (${response.status}): ${url}`);return response;}
const localRoot=process.argv[2]==='--local'?path.resolve(process.argv[3]??'../langflow'):null;
const revision=localRoot?execFileSync('git',['-C',localRoot,'rev-parse','HEAD'],{encoding:'utf8'}).trim():process.argv[2]??(await (await get('https://api.github.com/repos/langflow-ai/langflow/commits/main')).json()).sha;
if(!/^[a-f0-9]{40}$/.test(revision))throw Error('Pass an exact 40-character source revision.');
const listing=localRoot?(await readdir(path.join(localRoot,sourcePath),{withFileTypes:true})).filter(entry=>entry.isFile()&&entry.name.endsWith('.json')).map(entry=>({name:entry.name,type:'file',sha:execFileSync('git',['-C',localRoot,'rev-parse',`${revision}:${sourcePath}/${entry.name}`],{encoding:'utf8'}).trim()})):await (await get(`https://api.github.com/repos/langflow-ai/langflow/contents/${sourcePath}?ref=${revision}`)).json();
if(localRoot){
 for(const entry of await readdir(path.join(localRoot,'docs/static/files'),{withFileTypes:true})){
  if(!entry.isFile()||!entry.name.endsWith('.json'))continue;
  const relativePath='docs/static/files/'+entry.name;
  try{parseFlowImport(await readFile(path.join(localRoot,relativePath),'utf8'));}catch{continue;}
  listing.push({name:entry.name,type:'file',relativePath,sha:execFileSync('git',['-C',localRoot,'rev-parse',`${revision}:${relativePath}`],{encoding:'utf8'}).trim()});
 }
}
const files=listing.filter(file=>file.type==='file'&&file.name.endsWith('.json')).sort((a,b)=>a.name.localeCompare(b.name));
await mkdir(output,{recursive:true});
const license=localRoot?await readFile(path.join(localRoot,'LICENSE'),'utf8'):await (await get(`https://raw.githubusercontent.com/langflow-ai/langflow/${revision}/LICENSE`)).text();
await writeFile(path.join(output,'LICENSE'),license);
const categories={
 'Knowledge and Retrieval':['Document Q&A','Hybrid Search RAG','Knowledge Retrieval','Memory Chatbot','Vector Store RAG'],
 'Research and Analysis':['Deep Research Agent','Market Research','Price Deal Finder','Research Translation Loop','SaaS Pricing'],
 'Content Production':['Blog Writer','Content Aggregator','Instagram Copywriter','Meeting Summary','SEO Keyword Generator','Social Media Agent','Twitter Thread Generator'],
 'Data Extraction and Classification':['Financial Report Parser','Image Sentiment Analysis','Text Sentiment Analysis'],
 'Development':['Custom Component Generator','Portfolio Website Code Generator'],
 'Agent Patterns':['Basic Prompting','Multi Agent Flow','Sequential Tasks Agents','Simple Agent','Travel Planning Agents']
};
const items=[];
// Bounded download concurrency; each raw file retains its exact upstream bytes.
let cursor=0;
await Promise.all(Array.from({length:4},async()=>{while(cursor<files.length){const file=files[cursor++];const relativePath=file.relativePath??sourcePath+'/'+file.name;const rawUrl=`https://raw.githubusercontent.com/langflow-ai/langflow/${revision}/${relativePath.split('/').map(encodeURIComponent).join('/')}`;const bytes=localRoot?await readFile(path.join(localRoot,relativePath)):Buffer.from(await (await get(rawUrl)).arrayBuffer());const blob=createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');if(blob!==file.sha)throw Error('Git blob mismatch: '+file.name);const title=file.name.slice(0,-5),id=title.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');const flow=parseFlowImport(bytes.toString('utf8'));const types=[...new Set(flow.data.nodes.filter(n=>n.type!=='noteNode').map(n=>n.data?.type).filter(Boolean))].sort();
const configurationFields=[];
for(const node of flow.data.nodes){const fields=node.data?.node?.template??{};for(const [name,field]of Object.entries(fields)){if(field&&typeof field==='object'&&(field.password||field.type==='SecretStrInput'))configurationFields.push({nodeId:node.id,field:name,required:Boolean(field.required)});}}
await writeFile(path.join(output,id+'.json'),bytes);
items.push({id:'langflow-official:'+id,name:title,category:Object.entries(categories).find(([,names])=>names.includes(title))?.[0]??'Documentation Examples',candidatePlane:'Composite Components',classificationStatus:'unreviewed',validationStatus:'unverified',source:{repository:repo,revision,collectionMethod:localRoot?'local-deep-copy':'download',path:relativePath,url:`${repo}/blob/${revision}/${relativePath.split('/').map(encodeURIComponent).join('/')}`,gitBlobSha:file.sha,sha256:createHash('sha256').update(bytes).digest('hex'),license:'MIT',licensePath:'/langflow-templates/official/LICENSE'},file:'/langflow-templates/official/'+id+'.json',nodeCount:flow.data.nodes.length,edgeCount:flow.data.edges.length,componentTypes:types,configurationFields,lastTestedVersion:JSON.parse(bytes.toString()).last_tested_version??null});}}));
items.sort((a,b)=>a.name.localeCompare(b.name));
if(new Set(items.map(i=>i.id)).size!==items.length)throw Error('Duplicate item IDs');
await writeFile(path.join(root,'prototype-canvas/official-templates.json'),JSON.stringify({schemaVersion:1,sourceRevision:revision,placementNote:'Imported candidates, not validated composite boundaries. Review contracts before promotion.',items},null,2)+'\n');
console.log(`${localRoot?'Deep-copied from local checkout':'Downloaded'} ${items.length} original templates at ${revision}. None executed.`);

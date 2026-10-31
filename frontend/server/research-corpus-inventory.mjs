import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
export function corpusInventory(root){
 const collectors=['official','community-github','public-catalog'];
 return {name:'research-corpus-inventory',configureServer(server){server.middlewares.use('/research-corpus-inventory.json',(req,res)=>{
  if(!/^(localhost|127\.0\.0\.1)(:\d+)?$/.test(req.headers.host??'')||req.headers['sec-fetch-site']==='cross-site'){res.statusCode=403;res.end();return;}
  const items=[],errors=[];const counts={};
  for(const collector of collectors){try{const doc=JSON.parse(readFileSync(resolve(root,'knowledge/research/paper-6-corpus/collectors',collector,'manifest.json'),'utf8'));counts[collector]=doc.artifacts.length;for(const a of doc.artifacts)items.push({name:a.sourcePath?.split('/').pop()??a.file,collector,path:'knowledge/research/paper-6-corpus/collectors/'+collector+'/'+a.file,source:a.sourceUrl,revision:a.revision??'Unknown',license:a.license??'Unknown',sha256:a.sha256,bytes:a.bytes??0});}catch{errors.push(collector);}}
  res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');res.end(JSON.stringify({updatedAt:new Date().toISOString(),records:items.length,uniqueFiles:new Set(items.map(x=>x.sha256)).size,counts,errors,items}));
 });}};
}

import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
export function patternAnalysis(root){return {name:'connected-pattern-analysis',configureServer(server){server.middlewares.use('/research-pattern-analysis',(req,res)=>{
 if(!/^(localhost|127\.0\.0\.1)(:\d+)?$/.test(req.headers.host??'')||req.headers['sec-fetch-site']==='cross-site'){res.statusCode=403;res.end();return;}
 const url=new URL(req.url,'http://localhost'),rule=url.searchParams.get('rule');
 if(rule&&!/^[a-f0-9]{24}$/.test(rule)){res.statusCode=400;res.end('Invalid rule');return;}
 try{const base=resolve(root,'knowledge/research/paper-6-corpus/patterns');
  if(rule){const current=JSON.parse(readFileSync(resolve(base,'all-rules.json'),'utf8'));if(!current.some(r=>r.id===rule)){res.statusCode=404;res.end('Rule is not in current analysis');return;}}
  res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');res.end(readFileSync(resolve(base,rule?'rules/'+rule+'.json':url.searchParams.has('all')?'all-rules.json':'index.json')));
 }catch{res.statusCode=503;res.end(JSON.stringify({error:'Pattern analysis unavailable. Run the bounded local analysis first.'}));}
 });}};}

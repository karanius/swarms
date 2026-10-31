import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
export function corpusTopology(root){return {name:'corpus-topology',configureServer(server){server.middlewares.use('/research-corpus-topology',(req,res)=>{
 if(!/^(localhost|127\.0\.0\.1)(:\d+)?$/.test(req.headers.host??'')||req.headers['sec-fetch-site']==='cross-site'){res.statusCode=403;res.end();return;}
 const graph=new URL(req.url,'http://localhost').searchParams.get('graph');
 if(graph&&!/^[a-f0-9]{64}$/.test(graph)){res.statusCode=400;res.end('Invalid graph');return;}
 try{const path=resolve(root,'knowledge/research/paper-6-corpus/topology',graph?'graphs/'+graph+'.json':'index.json');res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');res.end(readFileSync(path));}catch{res.statusCode=503;res.end(JSON.stringify({error:'Topology data unavailable. Rebuild the local corpus topology.'}));}
 });}};}

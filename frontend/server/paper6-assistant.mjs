import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
export function paper6Assistant(root){return {name:'paper6-exclusive-assistant',configureServer(server){server.middlewares.use('/paper6-agent-api',async(req,res)=>{
 const host=req.headers.host??'';
 const reply=(code,data)=>{res.statusCode=code;res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');res.end(JSON.stringify(data))};
 if(!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(host)||req.headers['sec-fetch-site']==='cross-site'||(req.headers.origin&&req.headers.origin!=='http://'+host)){reply(403,{error:'Local Research requests only'});return;}
 const u=new URL(req.url,'http://localhost');if(!['/state','/turn','/cancel','/artifact','/section'].includes(u.pathname)){reply(404,{error:'Unknown assistant action'});return;}
 if(!['GET','POST'].includes(req.method)){reply(405,{error:'Method not allowed'});return;}
 try{
  let body='';if(req.method==='POST'){if(!req.headers['content-type']?.startsWith('application/json')){reply(415,{error:'JSON required'});return;}for await(const chunk of req){body+=chunk;if(Buffer.byteLength(body)>100000){reply(413,{error:'Message exceeds the research budget'});return;}}}
  const token=readFileSync(resolve(root,'services/paper6-assistant/.runtime/token'),'utf8').trim();
  const response=await fetch('http://127.0.0.1:5192'+u.pathname+u.search,{method:req.method,headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:req.method==='POST'?body:undefined,signal:AbortSignal.timeout(15000)});
  reply(response.status,await response.json());
 }catch{reply(503,{error:'The dedicated research assistant is unavailable. Start its local service, then reconnect.'});}
 });}};}

import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
export function researchNotebookProxy(root){
 const local=req=>{const host=req.headers.host??'';return /^(127\.0\.0\.1|localhost)(:\d+)?$/.test(host)&&(!req.headers.origin||req.headers.origin==='http://'+host)&&req.headers['sec-fetch-site']!=='cross-site';};
 return {name:'research-notebook-local-boundary',configureServer(server){server.middlewares.use('/research-jupyter',(req,res,next)=>{if(!local(req)){res.statusCode=403;res.end('Local Research requests only.');return;}next();});},config(){return {server:{proxy:{'/research-jupyter':{target:'http://127.0.0.1:5191',ws:true,selfHandleResponse:true,configure(proxy){
 const authorize=(proxyReq,req)=>{if(!local(req)){proxyReq.destroy();return;}try{const token=readFileSync(resolve(root,'services/research-notebook/.runtime/token'),'utf8').trim();proxyReq.setHeader('Authorization','token '+token);proxyReq.setHeader('Accept-Encoding','identity');if(/\/(tree|notebooks)(\/|\?|$)/.test(req.url??'')){proxyReq.removeHeader('If-None-Match');proxyReq.removeHeader('If-Modified-Since');}}catch{proxyReq.destroy();}};
 proxy.on('proxyRes',(upstream,req,res)=>{
  const html=String(upstream.headers['content-type']??'').includes('text/html');
  const headers={...upstream.headers};delete headers['transfer-encoding'];
  if(!html){res.writeHead(upstream.statusCode??502,headers);upstream.pipe(res);return;}
  headers['cache-control']='no-store';delete headers.etag;delete headers['last-modified'];
  const chunks=[];upstream.on('data',chunk=>chunks.push(chunk));upstream.on('end',()=>{let body=Buffer.concat(chunks).toString('utf8');body=body.replace('</head>','<script src="/research-frame-navigation.js"></script></head>');headers['content-length']=Buffer.byteLength(body);res.writeHead(upstream.statusCode??502,headers);res.end(body);});
 });
 proxy.on('proxyReq',authorize);proxy.on('proxyReqWs',authorize);
}}}}};}};
}

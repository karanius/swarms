import{build}from'esbuild';import{copyFileSync,mkdirSync}from'node:fs';import{fileURLToPath}from'node:url';import{resolve}from'node:path';
const root=fileURLToPath(new URL('../../../',import.meta.url));
await build({entryPoints:[resolve(root,'frontend/src/audio-analysis/main.jsx')],bundle:true,minify:true,outfile:resolve(root,'frontend/public/paper16-analysis/app.js'),define:{'process.env.NODE_ENV':'"production"'}});
const dest=resolve(root,'knowledge/research/notebooks/paper-16-analysis');mkdirSync(dest,{recursive:true});for(const f of ['app.js','app.css','index.html'])copyFileSync(resolve(root,'frontend/public/paper16-analysis',f),resolve(dest,f));

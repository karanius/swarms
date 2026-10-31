import {mkdir,symlink,lstat} from 'node:fs/promises';
await mkdir(new URL('./public/',import.meta.url),{recursive:true});
const link=new URL('./public/opendaw-wasm',import.meta.url);
try{await lstat(link)}catch{await symlink('../node_modules/@opendaw/studio-core-wasm/dist',link,'dir')}

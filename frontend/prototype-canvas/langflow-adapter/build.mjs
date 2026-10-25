import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const source=process.env.LANGFLOW_FRONTEND_PATH || fileURLToPath(new URL('../../../../langflow/src/frontend/',import.meta.url));
const outDir=fileURLToPath(new URL('../../public/langflow-native/',import.meta.url));
const require=createRequire(source+'/package.json');
const {build}=await import(require.resolve('vite'));
const adapter=fileURLToPath(new URL('entry.tsx',import.meta.url));
process.chdir(source);
await build({root:source,configFile:source+'/vite.config.mts',base:'/langflow-native/',define:{'process.env.NODE_ENV':JSON.stringify('production')},resolve:{alias:{'@':source+'/src','@queries':source+'/src/controllers/API/queries',...Object.fromEntries(Object.keys(require(source+'/package.json').dependencies).map(name=>[name,source+'/node_modules/'+name]))}},build:{outDir,emptyOutDir:true,minify:false,sourcemap:false,lib:{entry:adapter,formats:['es'],fileName:()=> 'adapter.js'},rollupOptions:{output:{inlineDynamicImports:true}}}});

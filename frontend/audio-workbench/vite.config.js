import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
export default defineConfig({root:fileURLToPath(new URL('.',import.meta.url)),server:{host:'127.0.0.1',port:5194,strictPort:true,proxy:{'/engine':{target:'http://127.0.0.1:5195',changeOrigin:true,rewrite:p=>p.replace(/^\/engine/,'')}}},build:{outDir:'../dist-audio-workbench',emptyOutDir:true}});

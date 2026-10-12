import {defineConfig} from 'vite';
export default defineConfig({server:{proxy:{'/exo-api':{target:'http://127.0.0.1:52416',changeOrigin:true,rewrite:path=>path.replace(/^\/exo-api/,'')}}}});

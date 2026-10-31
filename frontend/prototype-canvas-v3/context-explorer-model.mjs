export function valueKind(value){return value===null?'null':Array.isArray(value)?'array':typeof value;}
export function humanizeKey(key){
 if(typeof key==='number')return 'Item '+(key+1);
 const special={id:'ID',schemaVersion:'Schema version',workingRevision:'Working revision',updatedAt:'Updated at',discovery:'Intent & decisions',assemblies:'Assembly',validation:'Validation',checkpoints:'Saved checkpoints'};
 if(special[key])return special[key];
 const text=String(key).replace(/([a-z0-9])([A-Z])/g,'$1 $2').replace(/[_-]+/g,' ');
 return text.charAt(0).toUpperCase()+text.slice(1);
}
export function pathText(path=[]){return '$'+path.map(key=>typeof key==='number'?'['+key+']':/^[A-Za-z_$][\w$]*$/.test(key)?'.'+key:'['+JSON.stringify(key)+']').join('');}
export function valueAtPath(root,path=[]){
 let current=root;
 for(const key of path){if(current===null||typeof current!=='object'||!Object.prototype.hasOwnProperty.call(current,key))return {found:false,value:undefined};current=current[key];}
 return {found:true,value:current};
}
export function childrenOf(value){
 if(value===null||typeof value!=='object')return [];
 return Object.keys(value).map(key=>({key:Array.isArray(value)?Number(key):key,value:value[key]}));
}
export function summarizeValue(value,max=130){
 const type=valueKind(value);
 if(type==='object')return Object.keys(value).length+' fields';
 if(type==='array')return value.length+' items';
 const text=type==='string'?value:JSON.stringify(value)??String(value);
 return text.length>max?text.slice(0,max)+'…':text;
}
export function buildSearchIndex(root,limit=50000){
 const entries=[];let truncated=false;const ancestors=new WeakSet();
 const visit=(value,path)=>{
  if(entries.length>=limit){truncated=true;return;}
  const type=valueKind(value),key=path.at(-1)??'System context',preview=summarizeValue(value);
  entries.push({path,key,type,preview,search:(pathText(path)+' '+String(key)+' '+(typeof value==='string'?value:preview)).toLocaleLowerCase()});
  if(value&&typeof value==='object'){
   if(ancestors.has(value))return;ancestors.add(value);
   for(const child of childrenOf(value)){visit(child.value,[...path,child.key]);if(truncated)break;}
   ancestors.delete(value);
  }
 };
 visit(root,[]);return {entries,truncated};
}
export function searchContext(index,query,limit=100){
 const tokens=query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
 if(!tokens.length)return {results:[],total:0};
 let total=0;const results=[];
 for(const entry of index.entries)if(tokens.every(token=>entry.search.includes(token))){total++;if(results.length<limit)results.push(entry);}
 return {results,total};
}
export function absoluteTreePath(scope,reverseKeyPath){return [...scope,...(reverseKeyPath.at(-1)==='$'?reverseKeyPath.slice(0,-1):reverseKeyPath).slice().reverse()];}

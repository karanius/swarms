import React,{useEffect,useMemo,useState} from 'react';
import {JSONTree} from 'react-json-tree';
import {absoluteTreePath,buildSearchIndex,childrenOf,humanizeKey,pathText,searchContext,summarizeValue,valueAtPath,valueKind} from './context-explorer-model.mjs';
import './context-explorer.css';

const theme={scheme:'Swarms workbench',author:'Swarms',base00:'#151b24',base01:'#202a36',base02:'#344253',base03:'#8c9fb5',base04:'#a7b8cb',base05:'#dce7f2',base06:'#e8f1f8',base07:'#f2f8fc',base08:'#e8aaa9',base09:'#e0be8a',base0A:'#dfca9c',base0B:'#a8c9b8',base0C:'#9acbd4',base0D:'#adc9ec',base0E:'#c8bce6',base0F:'#d8b49f',tree:{margin:0,padding:0,backgroundColor:'transparent',fontFamily:'ui-monospace, SFMono-Regular, Menlo, monospace',fontSize:12,lineHeight:1.8},nestedNode:{paddingTop:3},value:{paddingTop:3}};
const preferredSections=['scope','library','templates','instances','discovery','assemblies','deployments','resources','documents','validation','evidence','gaps','workspace','runtime','checkpoints'];

export default function ContextExplorer({value}){
 const [mode,setMode]=useState('explore'),[query,setQuery]=useState(''),[scope,setScope]=useState([]),[selected,setSelected]=useState([]),[expansion,setExpansion]=useState({mode:'initial',revision:0}),[copyMessage,setCopyMessage]=useState('');
 const available=value!==null&&value!==undefined;
 const index=useMemo(()=>available?buildSearchIndex(value):{entries:[],truncated:false},[value,available]);
 const matches=useMemo(()=>searchContext(index,query),[index,query]);
 const resolvedScope=valueAtPath(value,scope),scopeValue=resolvedScope.value;
 const resolvedSelected=valueAtPath(value,selected),selectedValue=resolvedSelected.value;
 const scopeText=pathText(scope),selectedText=pathText(selected);
 const sections=useMemo(()=>available&&typeof value==='object'?Object.keys(value).filter(key=>preferredSections.includes(key)).sort((a,b)=>preferredSections.indexOf(a)-preferredSections.indexOf(b)):[],[value,available]);
 useEffect(()=>{if(!resolvedScope.found)setScope([]);if(!resolvedSelected.found)setSelected([]);},[value,resolvedScope.found,resolvedSelected.found]);
 useEffect(()=>{if(!copyMessage)return;const timer=setTimeout(()=>setCopyMessage(''),2500);return ()=>clearTimeout(timer);},[copyMessage]);
 function navigate(path){setScope(path);setSelected(path);setQuery('');setExpansion(current=>({mode:'initial',revision:current.revision+1}));}
 async function copy(text,label){try{await navigator.clipboard.writeText(text);setCopyMessage(label+' copied.');}catch{setCopyMessage('Copy is unavailable here. Use Raw to select the JSON text.');}}
 const chooseTreeValue=path=>setSelected(path);
 const treePath=keys=>absoluteTreePath(scope,keys);
 const selectedChildren=childrenOf(selectedValue);
 if(!available)return <div className="context-explorer-empty" role="status"><strong>System context is not available yet.</strong><p>The explorer will appear when a readable context snapshot is received.</p></div>;
 return <div className="context-explorer">
  <div className="context-explorer-controls">
   <div className="context-explorer-search"><label className="context-sr-only" htmlFor="context-search">Search system context</label><input id="context-search" type="search" placeholder="Find a key, value, or path…" value={query} onChange={event=>setQuery(event.target.value)}/>{query&&<button type="button" onClick={()=>setQuery('')} aria-label="Clear context search">Clear</button>}</div>
   <div className="context-mode-switch" role="group" aria-label="Context display"><button type="button" aria-pressed={mode==='explore'} onClick={()=>setMode('explore')}>Explore</button><button type="button" aria-pressed={mode==='raw'} onClick={()=>setMode('raw')}>Raw</button></div>
   <button className="context-secondary-button" type="button" onClick={()=>copy(JSON.stringify(value,null,2),'Full context JSON')}>Copy all JSON</button>
  </div>
  <div className="context-explorer-grid">
   <nav className="context-section-nav" aria-label="System context sections"><button type="button" aria-current={scope.length===0?'page':undefined} onClick={()=>navigate([])}><span>Overview</span><small>{sections.length} sections</small></button>{sections.map(key=><button key={key} type="button" aria-current={scope[0]===key?'page':undefined} onClick={()=>navigate([key])}><span>{humanizeKey(key)}</span><small>{summarizeValue(value[key],28)}</small></button>)}</nav>
   <section className="context-explorer-main" aria-label={mode==='raw'?'Raw context JSON':'Context tree'}>
    <nav className="context-breadcrumbs" aria-label="Context path"><button type="button" onClick={()=>navigate([])}>System</button>{scope.map((key,index)=><React.Fragment key={index}><span aria-hidden="true">/</span><button type="button" onClick={()=>navigate(scope.slice(0,index+1))}>{humanizeKey(key)}</button></React.Fragment>)}</nav>
    {query.trim()?<div className="context-search-results"><header><strong>{matches.total} {matches.total===1?'match':'matches'}</strong><span>{matches.total>matches.results.length?'Showing the first '+matches.results.length+'. Narrow your search.':'Searches keys, values, and paths.'}</span></header>{index.truncated&&<p className="context-search-limit">This large snapshot exceeds the search index limit. Browse a section to inspect its remaining values.</p>}{matches.results.length?<ul>{matches.results.map(entry=><li key={pathText(entry.path)}><button type="button" onClick={()=>navigate(entry.path)}><span>{pathText(entry.path)}</span><small><b>{entry.type}</b> · {entry.preview}</small></button></li>)}</ul>:<div className="context-inline-empty"><strong>No matching context fields.</strong><p>Try a component name, a status such as “planned”, or part of a path.</p></div>}</div>:mode==='raw'?<textarea className="context-raw-json" aria-label="Raw system context JSON" readOnly spellCheck={false} value={JSON.stringify(scopeValue,null,2)??'null'}/>:<>
     <div className="context-tree-toolbar"><span>{scopeText} <small>· {valueKind(scopeValue)}</small></span><div><button type="button" onClick={()=>setExpansion(current=>({mode:'expand',revision:current.revision+1}))}>Expand all</button><button type="button" onClick={()=>setExpansion(current=>({mode:'collapse',revision:current.revision+1}))}>Collapse all</button></div></div>
     <p className="context-tree-hint">Expand with the arrows. Select a field to inspect its exact path and value.</p>
     <div className="context-json-tree" key={scopeText+':'+expansion.revision}>
      {scopeValue!==null&&typeof scopeValue==='object'&&Object.keys(scopeValue).length===0?<div className="context-inline-empty"><strong>{Array.isArray(scopeValue)?'This list is empty.':'This section has no fields yet.'}</strong><p>Nothing is hidden. This is the current value.</p></div>:<JSONTree data={scopeValue} theme={theme} invertTheme={false} hideRoot={scopeValue!==null&&typeof scopeValue==='object'} keyPath={['$']} collectionLimit={40} shouldExpandNodeInitially={(_keys,_data,level)=>expansion.mode==='expand'||(expansion.mode==='initial'&&level<2)} labelRenderer={keys=>{const path=treePath(keys);return <button type="button" className={'context-tree-key'+(pathText(path)===selectedText?' is-selected':'')} title={pathText(path)} aria-label={'Inspect '+pathText(path)} onClick={event=>{event.stopPropagation();chooseTreeValue(path);}}>{keys[0]==='$'?'Value':humanizeKey(keys[0])}</button>;}} valueRenderer={(display,_raw,...keys)=>{const path=treePath(keys);return <button type="button" className="context-tree-value" aria-label={'Inspect value at '+pathText(path)} onClick={event=>{event.stopPropagation();chooseTreeValue(path);}}>{String(display).length>220?String(display).slice(0,220)+'…':display}</button>;}} getItemString={(_type,data)=> <span className="context-tree-count">{summarizeValue(data)}</span>}/>}</div>
    </>}
   </section>
   <aside className="context-value-inspector" aria-label="Selected context value"><header><strong>{selected.length?humanizeKey(selected.at(-1)):'System context'}</strong><span>{valueKind(selectedValue)}</span></header><code className="context-selected-path">{selectedText}</code><div className="context-inspector-actions"><button type="button" onClick={()=>copy(selectedText,'Path')}>Copy path</button><button type="button" onClick={()=>copy(JSON.stringify(selectedValue,null,2)??'null','Selected value')}>Copy value</button></div>{selectedChildren.length?<><p>{summarizeValue(selectedValue)} · choose one to explore</p><ul>{selectedChildren.slice(0,60).map(child=><li key={child.key}><button type="button" onClick={()=>navigate([...selected,child.key])}><span>{humanizeKey(child.key)}</span><small>{summarizeValue(child.value,56)}</small></button></li>)}</ul>{selectedChildren.length>60&&<p>Showing the first 60 fields. Use the tree or search to reach the rest.</p>}</>:<pre className="context-selected-value">{JSON.stringify(selectedValue,null,2)??'null'}</pre>}</aside>
  </div>
  <div className="context-explorer-footer" role="status">{copyMessage||'Read only · live values update without changing your section or selected path'}</div>
 </div>;
}

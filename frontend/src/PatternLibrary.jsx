import {Button,Input} from './ui/components';
import React, {useState} from 'react';
import {MagnifyingGlass, ArrowRight, X, Stack, FlowArrow} from './ui/icons';

export const starterPatterns = [
  {id:'images',pipeline:'images',name:'Images on my Mac',description:'Discover local image files, verify the count, and explain the evidence with one agent.',category:'Analysis',sequence:[1,1,5,0,3],labels:['Mac folders','Discover files','Verify count','One inventory agent','Report'],detail:'Read-only file tools → one Swarms Agent → grounded count.'},
  {id:'research',name:'Research and decision',description:'Gather evidence from two angles, compare findings, and review the recommendation.',category:'Research',sequence:[1,4,0,0,2,3,5,6],labels:['Read the brief','Parallel research','Research performance','Research compatibility','Compare findings','Write recommendation','Review evidence','Refine research'],links:[[0,1],[1,2],[1,3],[2,4],[3,4],[4,5],[5,6],[6,7],[7,1]],objective:'Recommend an option using performance and compatibility evidence.',detail:'Two research branches, comparison table, Markdown recommendation, and one review round.'},
  {id:'brief',name:'Evidence to brief',description:'Turn a research question into a concise, reviewed brief.',category:'Writing',sequence:[0,3,5],labels:['Research sources','Write brief','Review claims'],links:[[0,1],[1,2]],objective:'Produce a concise brief supported by cited sources.',detail:'Source research, Markdown output, and a final accuracy review.'},
  {id:'documents',name:'Document comparison',description:'Read two documents and explain the differences that matter.',category:'Analysis',sequence:[1,1,2,3],labels:['Read first document','Read second document','Compare documents','Write summary'],links:[[0,2],[1,2],[2,3]],objective:'Compare the supplied documents and summarize meaningful differences.',detail:'Two file inputs, comparison table, and a written summary.'},
  {id:'perspectives',name:'Parallel perspectives',description:'Explore an objective from three independent perspectives.',category:'Research',sequence:[4,0,0,0,2,3,5],labels:['Parallel team','Research benefits','Research risks','Research alternatives','Compare perspectives','Write decision','Review decision'],links:[[0,1],[0,2],[0,3],[1,4],[2,4],[3,4],[4,5],[5,6]],objective:'Evaluate benefits, risks, and alternatives before recommending a decision.',detail:'Three research branches, synthesis, and a final review.'},
  {id:'refine',name:'Draft and refine',description:'Draft an answer, review it, and return for another pass.',category:'Writing',sequence:[3,5,6],labels:['Write draft','Review draft','Revise draft'],links:[[0,1],[1,2],[2,0]],objective:'Create a clear draft and improve it against the review criteria.',detail:'Markdown draft, quality review, and two revision rounds.'},
];

export default function PatternLibrary({workflows,blocks,onUse,onClose}) {
  const [query,setQuery]=useState('');
  const [filter,setFilter]=useState('All');
  const records=[...starterPatterns,...workflows.map(w=>({...w,category:'Saved',description:'Your saved canvas configuration.',sequence:w.nodes.map(n=>n.data.kind),detail:`${w.nodes.length} nodes and ${w.edges.length} connections.`,saved:true}))];
  const visible=records.filter(p=>(filter==='All'||p.category===filter)&&`${p.name} ${p.description}`.toLowerCase().includes(query.toLowerCase()));
  return <section className="pattern-library" aria-label="Pattern library" onKeyDown={e=>{if(e.key==='Escape')onClose();}}>
    <header><div><h2>Pattern library</h2><p>Start with a configured canvas.</p></div><Button aria-label="Close pattern library" onClick={onClose}><X size={18}/></Button></header>
    <label className="pattern-search"><MagnifyingGlass size={17}/><Input className="ui-input--embedded" type="search" aria-label="Search patterns" placeholder="Search patterns" value={query} onChange={e=>setQuery(e.target.value)}/></label>
    <div className="pattern-filters" aria-label="Pattern categories">{['All','Research','Writing','Analysis','Saved'].map(f=><Button key={f} className={filter===f?'active':''} aria-pressed={filter===f} onClick={()=>setFilter(f)}>{f}</Button>)}</div>
    <div className="pattern-records">{visible.map(p=><article className="pattern-record" key={p.id}><div className="pattern-record-title"><span className="pattern-symbol">{p.saved?<Stack size={20}/>:<FlowArrow size={20}/>}</span><div><h3>{p.name}</h3><span>{p.category} / {p.sequence.length} nodes</span></div></div><p>{p.description}</p><div className="pattern-sequence" aria-label="Node sequence">{p.sequence.map((kind,i)=>{const Icon=blocks[kind]?.icon||Stack;return <React.Fragment key={i}>{i>0&&<ArrowRight size={10}/>}<span title={p.labels?.[i]||blocks[kind]?.name}><Icon size={15}/></span></React.Fragment>;})}</div><footer><small>{p.detail}</small><Button onClick={()=>onUse(p)}>Use pattern <ArrowRight size={14}/></Button></footer></article>)}</div>
    {visible.length===0&&<div className="pattern-empty"><h3>No matching patterns</h3><p>{filter==='Saved'?'Save a canvas in Settings to add it here.':'Try another search or category.'}</p></div>}
    <div className="pattern-library-foot">Hover to browse. Use a pattern to replace the canvas.</div>
  </section>;
}

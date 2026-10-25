import React, {useState} from 'react';
import sequenceDocument from '../../INSTANCE-BUILDER-SEQUENCE.md?raw';
import './machine-sequence.css';

const titles=['Describe the outcome','Create the instance','Structure the specification','Map the layers','Decompose downward','Resolve the library','Assemble upward','Validate each assembly','Synchronize documents and tower','Keep reusable assemblies','Refine through conversation'];
const steps=Array.from(sequenceDocument.matchAll(/^\d+\.\s+(.+)$/gm), (match,index)=>({title:titles[index]??`Step ${index+1}`,description:match[1].replace(/\*\*/g,'')}));

export default function MachineSequence(){
 const [hovered,setHovered]=useState(false),[focused,setFocused]=useState(false),[pinned,setPinned]=useState(false),[dismissed,setDismissed]=useState(false);
 const open=!dismissed&&(hovered||focused||pinned);
 return <aside className="machine-sequence" onMouseEnter={()=>{setHovered(true);setDismissed(false);}} onMouseLeave={()=>setHovered(false)} onFocusCapture={()=>{setFocused(true);setDismissed(false);}} onBlurCapture={event=>{if(!event.currentTarget.contains(event.relatedTarget))setFocused(false);}} onKeyDown={event=>{if(event.key==='Escape'){event.stopPropagation();event.currentTarget.querySelector('.machine-sequence-trigger')?.focus();setDismissed(true);setPinned(false);}}}>
  <button className="machine-sequence-trigger" aria-expanded={open} aria-controls="machine-sequence-panel" title="Hover to open; click to keep open" onClick={()=>{setPinned(value=>!value);setDismissed(false);}}>
   <span>Machine Sequence</span><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m10 4-4 4 4 4"/></svg>
  </button>
  <section id="machine-sequence-panel" className={'machine-sequence-panel'+(open?' is-open':'')} aria-label="Instance builder sequence" aria-hidden={!open} inert={!open}>
   <header><h2>Machine Sequence</h2><p>The intended workflow, not a live execution trace.</p></header>
   <ol>{steps.map((step,index)=><li key={step.title}><details><summary><span className="machine-sequence-number" aria-hidden="true">{index+1}</span><span>{step.title}</span><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m6 4 4 4-4 4"/></svg></summary><p>{step.description}</p></details></li>)}</ol>
   <footer>Requirements go down. Tested assemblies build up.</footer>
  </section>
 </aside>;
}

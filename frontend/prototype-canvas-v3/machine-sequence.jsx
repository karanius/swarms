import React, {useEffect,useRef,useState} from 'react';
import sequenceDocument from './machine-sequence.md?raw';
import './machine-sequence.css';

const titles=['Describe the outcome','Create the instance','Structure the specification','Map the layers','Decompose downward','Resolve the library','Assemble upward','Validate each assembly','Synchronize documents and tower','Keep reusable assemblies','Refine through conversation'];
const steps=Array.from(sequenceDocument.matchAll(/^\d+\.\s+(.+)$/gm), (match,index)=>({title:titles[index]??`Step ${index+1}`,description:match[1].replace(/\*\*/g,'')}));

export default function MachineSequence(){
 const [open,setOpen]=useState(false);const root=useRef(null);
 useEffect(()=>{
  const outside=event=>{if(!root.current?.contains(event.target))setOpen(false);};
  const escape=event=>{if(event.key==='Escape'&&open){setOpen(false);root.current?.querySelector('button')?.focus();}};
  document.addEventListener('pointerdown',outside);document.addEventListener('keydown',escape);
  return ()=>{document.removeEventListener('pointerdown',outside);document.removeEventListener('keydown',escape);};
 },[open]);
 useEffect(()=>{if(!open)for(const detail of root.current?.querySelectorAll('details[open]')??[])detail.open=false;},[open]);
 return <aside className="machine-sequence" ref={root}>
  <button className="machine-sequence-trigger" aria-expanded={open} aria-controls="machine-sequence-panel" title="Click to open or close" onClick={()=>setOpen(value=>!value)}>
   <span>Machine Sequence</span><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m10 4-4 4 4 4"/></svg>
  </button>
  <section id="machine-sequence-panel" className={'machine-sequence-panel'+(open?' is-open':'')} aria-label="Instance builder sequence" aria-hidden={!open} inert={!open}>
   <header><h2>Machine Sequence</h2><p>The intended workflow, not a live execution trace.</p></header>
   <ol>{steps.map((step,index)=><li key={step.title}><details><summary><span className="machine-sequence-number" aria-hidden="true">{index+1}</span><span>{step.title}</span><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m6 4 4 4-4 4"/></svg></summary><p>{step.description}</p></details></li>)}</ol>
   <footer>Requirements go down. Tested assemblies build up.</footer>
  </section>
 </aside>;
}

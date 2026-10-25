import React, {useLayoutEffect,useRef} from 'react';
import catalog from './v2-catalog.json';
import './v2-library.css';

function CustomItems({plane,items,onAdd}){
 const selected=items.filter(item=>item.plane===plane);
 return <details className="custom-category"><summary>Custom{selected.length?' · '+selected.length:''}</summary>{selected.length?<ul>{selected.map(item=><li key={item.id}><button type="button" className="draggable-component" draggable onDragStart={event=>{event.dataTransfer.setData('application/x-canvas-custom',item.id);event.dataTransfer.effectAllowed='copy';}} onClick={()=>onAdd?.(item)} title="Add saved assembly to this plane">{item.name}</button></li>)}</ul>:<p className="custom-empty">No custom items yet.</p>}</details>;
}
// Independent V2 library copy; edits here do not change the V1 stack.
export default function V2Library({onAddComponent,activePlane="Components",onSelectPlane,customItems=[],onAddCustom}){
 const libraryRef=useRef(null);
 useLayoutEffect(()=>{
  const root=libraryRef.current;
  let frame=0;
  const positionTrays=()=>{
   const margin=12,width=Math.min(300,window.innerWidth-margin*2);
   for(const tray of root.querySelectorAll('.component-tray')){
    const panel=tray.querySelector('.tray-content'),list=tray.querySelector('.tray-list');
    if(!panel||!list)continue;
    panel.style.width=width+'px';
    const anchor=tray.getBoundingClientRect();
    const height=list.getBoundingClientRect().height+8;
    const top=Math.max(margin,Math.min(anchor.bottom,window.innerHeight-margin-height));
    const left=Math.max(margin,Math.min(anchor.left,window.innerWidth-margin-width));
    panel.style.top=(top-anchor.top)+'px';
    panel.style.left=(left-anchor.left)+'px';
    panel.style.bottom='auto';
   }
  };
  const schedule=()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(positionTrays);};
  const observer=new ResizeObserver(schedule);
  root.querySelectorAll('.tray-list,.tray-stack').forEach(element=>observer.observe(element));
  root.addEventListener('pointerover',positionTrays);
  root.addEventListener('focusin',positionTrays);
  root.addEventListener('toggle',schedule,true);
  window.addEventListener('resize',schedule);
  positionTrays();
  return ()=>{cancelAnimationFrame(frame);observer.disconnect();root.removeEventListener('pointerover',positionTrays);root.removeEventListener('focusin',positionTrays);root.removeEventListener('toggle',schedule,true);window.removeEventListener('resize',schedule);};
 },[]);
 return (<div className="v2-library" ref={libraryRef}><div className="tray-stack"><div className="stack-label">LIBRARY</div><aside className="component-tray"><button className="plane-selector" aria-label={'Open Confederations plane'} aria-pressed={activePlane==='Confederations'} onClick={()=>onSelectPlane?.('Confederations')}>{activePlane==='Confederations'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open confederations list">Confederations</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Confederations'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Regional Development",items:["Regional Development Confederation","Regional Innovation Confederation","Regional Enterprise Confederation","Regional Resilience Confederation"]},
{category:"Research and Knowledge",items:["Research Collaboration Confederation","Open Knowledge Confederation","Shared Research Infrastructure Confederation","Evidence Exchange Confederation"]},
{category:"Trade and Commerce",items:["Trade Network Confederation","Producer Network Confederation","Supply Network Confederation","Circular Commerce Confederation"]},
{category:"Education and Workforce",items:["Education Collaboration Confederation","Workforce Development Confederation","Professional Learning Confederation","Skills Mobility Confederation"]},
{category:"Technology and Infrastructure",items:["Digital Infrastructure Confederation","Open Technology Confederation","Platform Interoperability Confederation","Shared Computing Confederation"]},
{category:"Sustainability and Resources",items:["Resource Stewardship Confederation","Clean Energy Collaboration Confederation","Circular Economy Confederation","Environmental Research Confederation"]},
{category:"Community and Public Services",items:["Community Collaboration Confederation","Public Services Confederation","Digital Inclusion Confederation","Local Resilience Confederation"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Federation plane'} aria-pressed={activePlane==='Federation'} onClick={()=>onSelectPlane?.('Federation')}>{activePlane==='Federation'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open federation list">Federation</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Federation'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Regional Development",items:["Regional Development Federation","Regional Innovation Federation","Regional Enterprise Federation","Regional Resilience Federation"]},
{category:"Research and Knowledge",items:["Research Alliance Federation","Open Knowledge Federation","Shared Research Infrastructure Federation","Evidence Collaboration Federation"]},
{category:"Trade and Commerce",items:["Trade Alliance Federation","Producer Network Federation","Supply Network Federation","Circular Commerce Federation"]},
{category:"Education and Workforce",items:["Education Alliance Federation","Workforce Development Federation","Professional Learning Federation","Skills Collaboration Federation"]},
{category:"Technology and Infrastructure",items:["Digital Infrastructure Federation","Open Technology Federation","Platform Interoperability Federation","Shared Computing Federation"]},
{category:"Sustainability and Resources",items:["Resource Stewardship Federation","Clean Energy Alliance Federation","Circular Economy Federation","Environmental Research Federation"]},
{category:"Community and Public Services",items:["Community Alliance Federation","Public Services Collaboration Federation","Digital Inclusion Federation","Local Resilience Federation"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Alliances plane'} aria-pressed={activePlane==='Alliances'} onClick={()=>onSelectPlane?.('Alliances')}>{activePlane==='Alliances'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open alliances list">Alliances</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Alliances'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Regional Development",items:["Regional Innovation Alliance","Regional Enterprise Development Alliance","Urban-Rural Collaboration Alliance","Regional Skills and Industry Alliance"]},
{category:"Research and Innovation",items:["Applied Research Alliance","Open Science Alliance","Research Commercialization Alliance","Cross-Industry Innovation Alliance"]},
{category:"Trade and Supply Networks",items:["Regional Trade Alliance","Supply Network Resilience Alliance","Producer and Distributor Alliance","Circular Supply Alliance"]},
{category:"Education and Workforce",items:["Workforce Development Alliance","Lifelong Learning Alliance","Industry Apprenticeship Alliance","Skills Mobility Alliance"]},
{category:"Technology and Infrastructure",items:["Digital Infrastructure Alliance","Open Technology Alliance","Platform Interoperability Alliance","Shared Computing Infrastructure Alliance"]},
{category:"Sustainability and Resources",items:["Resource Efficiency Alliance","Clean Energy Collaboration Alliance","Circular Economy Alliance","Environmental Research Alliance"]},
{category:"Community and Public Services",items:["Community Services Alliance","Public Knowledge Alliance","Local Resilience Alliance","Digital Inclusion Alliance"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Ecosystems plane'} aria-pressed={activePlane==='Ecosystems'} onClick={()=>onSelectPlane?.('Ecosystems')}>{activePlane==='Ecosystems'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open ecosystems list">Ecosystems</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Ecosystems'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Innovation",items:["Innovation Network","Research Commercialization Network","Startup Collaboration Network","Industry Innovation Network"]},
{category:"Commerce",items:["Retail Partner Network","Producer-to-Market Network","Regional Trade Network","Circular Commerce Network"]},
{category:"Learning",items:["Workforce Learning Network","Professional Education Network","Community Learning Network","Industry Training Network"]},
{category:"Knowledge",items:["Open Knowledge Network","Research Publishing Network","Expert Collaboration Network","Evidence Exchange Network"]},
{category:"Technology",items:["Developer Platform Network","Technology Partner Network","Digital Infrastructure Network","Open Source Collaboration Network"]},
{category:"Creative Industries",items:["Creative Production Network","Independent Media Network","Design Collaboration Network","Creator Distribution Network"]},
{category:"Community Development",items:["Local Enterprise Network","Community Services Network","Social Impact Network","Regional Development Network"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Enterprises plane'} aria-pressed={activePlane==='Enterprises'} onClick={()=>onSelectPlane?.('Enterprises')}>{activePlane==='Enterprises'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open enterprises list">Enterprises</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Enterprises'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Digital Businesses",items:["Digital Product Business","Software Subscription Business","Digital Platform Business","Digital Marketplace Business"]},
{category:"Professional Services",items:["Consulting Practice","Creative Agency","Software Services Firm","Managed Services Firm"]},
{category:"Commerce",items:["Online Retail Business","Wholesale Business","Subscription Commerce Business","Specialty Retail Business"]},
{category:"Media and Publishing",items:["Digital Publication","Content Studio","Educational Publisher","Industry News Organization"]},
{category:"Education and Training",items:["Online Learning Provider","Professional Training Organization","Corporate Learning Provider","Community Learning Organization"]},
{category:"Research Organizations",items:["Independent Research Institute","Market Research Firm","Applied Research Organization","Public Interest Research Organization"]},
{category:"Community Organizations",items:["Professional Association","Member Community","Volunteer Organization","Community Services Organization"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Operations plane'} aria-pressed={activePlane==='Operations'} onClick={()=>onSelectPlane?.('Operations')}>{activePlane==='Operations'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open operations list">Operations</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Operations'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Digital Products",items:["Digital Product Operations","Product Portfolio Operations","Platform Operations","Product Launch Operations"]},
{category:"Customer",items:["Customer Operations","Customer Lifecycle Operations","Customer Experience Operations","Customer Enablement Operations"]},
{category:"Marketing",items:["Marketing Operations","Demand Generation Operations","Brand and Communications Operations","Market Expansion Operations"]},
{category:"Knowledge",items:["Knowledge Operations","Research and Intelligence Operations","Knowledge Governance Operations","Organizational Learning Operations"]},
{category:"Data",items:["Data Operations","Analytics Operations","Data Platform Operations","Data Governance Operations"]},
{category:"Content",items:["Content Operations","Editorial Operations","Multilingual Content Operations","Content Distribution Operations"]},
{category:"Service",items:["Service Operations","Service Reliability Operations","Incident Response Operations","Service Improvement Operations"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Programs plane'} aria-pressed={activePlane==='Programs'} onClick={()=>onSelectPlane?.('Programs')}>{activePlane==='Programs'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open programs list">Programs</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Programs'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Marketing",items:["Market Growth Program","Brand Development Program","Demand Generation Program","Market Expansion Program"]},
{category:"Product",items:["Product Development","Product Discovery Program","Product Modernization Program","Product Adoption Program"]},
{category:"Customer",items:["Customer Success","Customer Onboarding Program","Customer Retention Program","Customer Experience Improvement"]},
{category:"Knowledge",items:["Knowledge Operations","Organizational Intelligence Program","Research and Evidence Program","Knowledge Governance Program"]},
{category:"Data",items:["Data Operations","Data Quality Improvement Program","Analytics Enablement Program","Data Governance Program"]},
{category:"Reliability",items:["Service Reliability","Incident Readiness Program","Operational Resilience Program","Service Improvement Program"]},
{category:"Content",items:["Content Operations","Editorial Development Program","Content Localization Program","Content Lifecycle Program"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Processes plane'} aria-pressed={activePlane==='Processes'} onClick={()=>onSelectPlane?.('Processes')}>{activePlane==='Processes'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open processes list">Processes</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Processes'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Marketing",items:["Campaign Lifecycle","Audience Development","Marketing Optimization"]},
{category:"Research",items:["Continuous Intelligence","Research Program","Evidence Maintenance"]},
{category:"Content",items:["Editorial Lifecycle","Content Localization Program","Content Refresh and Governance"]},
{category:"Data",items:["Data Product Lifecycle","Data Quality Management","Continuous Analytics"]},
{category:"Software Delivery",items:["Feature Delivery Lifecycle","Defect Resolution Lifecycle","Release and Maintenance"]},
{category:"Business Operations",items:["Customer Support Lifecycle","Procurement and Approval","Customer Onboarding"]},
{category:"Monitoring",items:["Incident Management","Service Reliability Improvement","Change Impact Monitoring"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Flows plane'} aria-pressed={activePlane==='Flows'} onClick={()=>onSelectPlane?.('Flows')}>{activePlane==='Flows'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open flows list">Flows</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Flows'} items={customItems} onAdd={onAddCustom}/>{[
{category:"Research and Reporting",items:["Research brief to sourced report","Competitor landscape report","Literature review and evidence synthesis","Product comparison and recommendation"]},
{category:"Content Production",items:["Brief to reviewed article","Source material to presentation","Campaign brief to content package","Document translation and quality review"]},
{category:"Data Processing and Analysis",items:["Raw files to validated dataset","Documents to structured records","Dataset to analysis report","Recurring data quality assessment"]},
{category:"Software Development",items:["Feature request to implementation proposal","Bug report to verified fix","Code changes to review report","Repository to technical documentation"]},
{category:"Marketing",items:["Market research and audience insights","Campaign strategy and planning","Campaign brief to content campaign","Marketing performance analysis"]},
{category:"Business Operations",items:["Support request to resolution proposal","Meeting transcript to action plan","Invoice intake to approval package","Customer inquiry to reviewed response"]},
{category:"Monitoring and Response",items:["Service signals to incident brief","Document changes to impact report","Incoming events to triaged alerts","Incident report to response plan"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray composite-tray"><button className="plane-selector" aria-label="Open Composite Components plane" aria-pressed={activePlane==='Composite Components'} onClick={()=>onSelectPlane?.('Composite Components')}>{activePlane==='Composite Components'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open composite component list">Composite Components</button><div className="tray-content"><div className="tray-list composite-list"><CustomItems plane={'Composite Components'} items={customItems} onAdd={onAddCustom}/><details><summary>Coordination Patterns</summary><ul>{["Research and verify", "Create and critique", "Divide and consolidate", "Plan and execute"].map(name=><li key={name}>{name}</li>)}</ul></details>{[
{category:"Knowledge and Research",items:["Document retrieval and synthesis","Multi-source research","Evidence collection and citation","Knowledge ingestion and indexing"]},
{category:"Content Production",items:["Brief to draft","Editing and refinement","Translation and localization","Multi-format publishing preparation"]},
{category:"Data Processing",items:["Structured data extraction","Cleaning and normalization","Enrichment and classification","Dataset merging and deduplication"]},
{category:"Evaluation and Quality",items:["Schema and contract validation","Factual consistency review","Rubric-based scoring","Candidate comparison and ranking"]},
{category:"Actions and Integrations",items:["API request and response mapping","Cross-system record synchronization","Event filtering and dispatch","Action execution and confirmation"]},
{category:"Memory and Context",items:["Conversation summarization","Task context assembly","Persistent fact storage and retrieval","Context selection and compression"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="plane-selector" aria-label={'Open Components plane'} aria-pressed={activePlane==='Components'} onClick={()=>onSelectPlane?.('Components')}>{activePlane==='Components'?'👉':'⭕'}</button><button className="tray-handle" aria-label="Open component list">Components</button><div className="tray-content"><div className="tray-list"><CustomItems plane={'Components'} items={customItems} onAdd={onAddCustom}/>{catalog.map(group=><details key={group.name}><summary>{group.name}</summary><ul>{group.items.map(item=><li key={item.id}>{<button type="button" className="draggable-component" disabled={!onAddComponent} draggable={Boolean(onAddComponent)} onDragStart={event=>{event.dataTransfer.setData('application/x-langflow-component',item.id);event.dataTransfer.effectAllowed='copy';}} onClick={()=>onAddComponent?.(item.id)} title={onAddComponent?"Drag onto the canvas, or click to add":"Loading Langflow components"}>{item.name}{item.legacy&&<small> · legacy</small>}</button>}</li>)}</ul></details>)}</div></div></aside></div></div>);
}

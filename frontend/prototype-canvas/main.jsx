// Empty React Flow playground; components will be introduced together later.
import React, {useCallback, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {ReactFlow, Background, Controls, ControlButton, addEdge, useNodesState, useEdgesState} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './style.css';
import catalog from './catalog.json';
import VersionTwo from './v2-canvas.jsx';
const instanceLayers = [
{layer:"Confederations",category:"Research and Knowledge",items:["Research Collaboration Confederation"]},
{layer:"Federation",category:"Research and Knowledge",items:["Research Alliance Federation"]},
{layer:"Alliances",category:"Research and Innovation",items:["Applied Research Alliance"]},
{layer:"Ecosystems",category:"Innovation",items:["Innovation Network"]},
{layer:"Enterprises",category:"Research Organizations",items:["Applied Research Organization"]},
{layer:"Operations",category:"Knowledge",items:["Research and Intelligence Operations"]},
{layer:"Programs",category:"Knowledge",items:["Research and Evidence Program"]},
{layer:"Processes",category:"Research",items:["Research Program","Evidence Maintenance"]},
{layer:"Full Flow",category:"Research and Reporting",items:["Research brief to sourced report"]},
{layer:"Composite Components",category:"Knowledge and Research",items:["Multi-source research","Evidence collection and citation"]},
{layer:"Components",category:"Selected building blocks",items:["Chat Input","Prompt Template","Agent","Language Model","Web Search","URL","Parser","Chat Output"]}
];
const referralLayers = [
{layer:"Confederations",category:"Trade and Commerce",items:["Trade Network Confederation"]},
{layer:"Federation",category:"Trade and Commerce",items:["Trade Alliance Federation"]},
{layer:"Alliances",category:"Regional Development",items:["Regional Enterprise Development Alliance"]},
{layer:"Ecosystems",category:"Community Development",items:["Local Enterprise Network"]},
{layer:"Enterprises",category:"Digital Businesses",items:["Digital Marketplace Business"]},
{layer:"Operations",category:"Customer and Marketing",items:["Customer Lifecycle Operations","Marketing Operations","Analytics Operations"]},
{layer:"Programs",category:"Growth and Customer",items:["Demand Generation Program","Customer Onboarding Program","Analytics Enablement Program"]},
{layer:"Processes",category:"Marketing and Data",items:["Audience Development","Campaign Lifecycle","Customer Onboarding","Continuous Analytics"]},
{layer:"Full Flow",category:"Marketing and Business Operations",items:["Market research and audience insights","Campaign strategy and planning","Customer inquiry to reviewed response","Marketing performance analysis"]},
{layer:"Composite Components",category:"Research, Data, and Quality",items:["Multi-source research","Structured data extraction","Enrichment and classification","Cross-system record synchronization","Schema and contract validation","Human referral review — proposed addition"]},
{layer:"Components",category:"Selected building blocks",items:["Chat Input","Prompt Template","Agent","Language Model","Structured Output","API Request","SQL Database","Chat Output"]}
];
function VersionOne(){
 const [nodes,,onNodesChange]=useNodesState([]);
 const [edges,setEdges,onEdgesChange]=useEdgesState([]);
 const onConnect=useCallback(connection=>setEdges(current=>addEdge(connection,current)),[setEdges]);
 return <main><ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} colorMode="dark" fitView fitViewOptions={{padding:0.3}}><Background color="#303640" gap={24}/><Controls showFitView={false}><ControlButton title="Fullscreen" aria-label="Fullscreen" onClick={()=>{if(document.fullscreenElement){document.exitFullscreen();}else{document.documentElement.requestFullscreen();}}}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/></svg></ControlButton></Controls></ReactFlow><div className="tray-stack"><div className="stack-label">LIBRARY</div><aside className="component-tray"><button className="tray-handle" aria-label="Open confederations list">Confederations</button><div className="tray-content"><div className="tray-list">{[
{category:"Regional Development",items:["Regional Development Confederation","Regional Innovation Confederation","Regional Enterprise Confederation","Regional Resilience Confederation"]},
{category:"Research and Knowledge",items:["Research Collaboration Confederation","Open Knowledge Confederation","Shared Research Infrastructure Confederation","Evidence Exchange Confederation"]},
{category:"Trade and Commerce",items:["Trade Network Confederation","Producer Network Confederation","Supply Network Confederation","Circular Commerce Confederation"]},
{category:"Education and Workforce",items:["Education Collaboration Confederation","Workforce Development Confederation","Professional Learning Confederation","Skills Mobility Confederation"]},
{category:"Technology and Infrastructure",items:["Digital Infrastructure Confederation","Open Technology Confederation","Platform Interoperability Confederation","Shared Computing Confederation"]},
{category:"Sustainability and Resources",items:["Resource Stewardship Confederation","Clean Energy Collaboration Confederation","Circular Economy Confederation","Environmental Research Confederation"]},
{category:"Community and Public Services",items:["Community Collaboration Confederation","Public Services Confederation","Digital Inclusion Confederation","Local Resilience Confederation"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open federation list">Federation</button><div className="tray-content"><div className="tray-list">{[
{category:"Regional Development",items:["Regional Development Federation","Regional Innovation Federation","Regional Enterprise Federation","Regional Resilience Federation"]},
{category:"Research and Knowledge",items:["Research Alliance Federation","Open Knowledge Federation","Shared Research Infrastructure Federation","Evidence Collaboration Federation"]},
{category:"Trade and Commerce",items:["Trade Alliance Federation","Producer Network Federation","Supply Network Federation","Circular Commerce Federation"]},
{category:"Education and Workforce",items:["Education Alliance Federation","Workforce Development Federation","Professional Learning Federation","Skills Collaboration Federation"]},
{category:"Technology and Infrastructure",items:["Digital Infrastructure Federation","Open Technology Federation","Platform Interoperability Federation","Shared Computing Federation"]},
{category:"Sustainability and Resources",items:["Resource Stewardship Federation","Clean Energy Alliance Federation","Circular Economy Federation","Environmental Research Federation"]},
{category:"Community and Public Services",items:["Community Alliance Federation","Public Services Collaboration Federation","Digital Inclusion Federation","Local Resilience Federation"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open alliances list">Alliances</button><div className="tray-content"><div className="tray-list">{[
{category:"Regional Development",items:["Regional Innovation Alliance","Regional Enterprise Development Alliance","Urban-Rural Collaboration Alliance","Regional Skills and Industry Alliance"]},
{category:"Research and Innovation",items:["Applied Research Alliance","Open Science Alliance","Research Commercialization Alliance","Cross-Industry Innovation Alliance"]},
{category:"Trade and Supply Networks",items:["Regional Trade Alliance","Supply Network Resilience Alliance","Producer and Distributor Alliance","Circular Supply Alliance"]},
{category:"Education and Workforce",items:["Workforce Development Alliance","Lifelong Learning Alliance","Industry Apprenticeship Alliance","Skills Mobility Alliance"]},
{category:"Technology and Infrastructure",items:["Digital Infrastructure Alliance","Open Technology Alliance","Platform Interoperability Alliance","Shared Computing Infrastructure Alliance"]},
{category:"Sustainability and Resources",items:["Resource Efficiency Alliance","Clean Energy Collaboration Alliance","Circular Economy Alliance","Environmental Research Alliance"]},
{category:"Community and Public Services",items:["Community Services Alliance","Public Knowledge Alliance","Local Resilience Alliance","Digital Inclusion Alliance"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open ecosystems list">Ecosystems</button><div className="tray-content"><div className="tray-list">{[
{category:"Innovation",items:["Innovation Network","Research Commercialization Network","Startup Collaboration Network","Industry Innovation Network"]},
{category:"Commerce",items:["Retail Partner Network","Producer-to-Market Network","Regional Trade Network","Circular Commerce Network"]},
{category:"Learning",items:["Workforce Learning Network","Professional Education Network","Community Learning Network","Industry Training Network"]},
{category:"Knowledge",items:["Open Knowledge Network","Research Publishing Network","Expert Collaboration Network","Evidence Exchange Network"]},
{category:"Technology",items:["Developer Platform Network","Technology Partner Network","Digital Infrastructure Network","Open Source Collaboration Network"]},
{category:"Creative Industries",items:["Creative Production Network","Independent Media Network","Design Collaboration Network","Creator Distribution Network"]},
{category:"Community Development",items:["Local Enterprise Network","Community Services Network","Social Impact Network","Regional Development Network"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open enterprises list">Enterprises</button><div className="tray-content"><div className="tray-list">{[
{category:"Digital Businesses",items:["Digital Product Business","Software Subscription Business","Digital Platform Business","Digital Marketplace Business"]},
{category:"Professional Services",items:["Consulting Practice","Creative Agency","Software Services Firm","Managed Services Firm"]},
{category:"Commerce",items:["Online Retail Business","Wholesale Business","Subscription Commerce Business","Specialty Retail Business"]},
{category:"Media and Publishing",items:["Digital Publication","Content Studio","Educational Publisher","Industry News Organization"]},
{category:"Education and Training",items:["Online Learning Provider","Professional Training Organization","Corporate Learning Provider","Community Learning Organization"]},
{category:"Research Organizations",items:["Independent Research Institute","Market Research Firm","Applied Research Organization","Public Interest Research Organization"]},
{category:"Community Organizations",items:["Professional Association","Member Community","Volunteer Organization","Community Services Organization"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open operations list">Operations</button><div className="tray-content"><div className="tray-list">{[
{category:"Digital Products",items:["Digital Product Operations","Product Portfolio Operations","Platform Operations","Product Launch Operations"]},
{category:"Customer",items:["Customer Operations","Customer Lifecycle Operations","Customer Experience Operations","Customer Enablement Operations"]},
{category:"Marketing",items:["Marketing Operations","Demand Generation Operations","Brand and Communications Operations","Market Expansion Operations"]},
{category:"Knowledge",items:["Knowledge Operations","Research and Intelligence Operations","Knowledge Governance Operations","Organizational Learning Operations"]},
{category:"Data",items:["Data Operations","Analytics Operations","Data Platform Operations","Data Governance Operations"]},
{category:"Content",items:["Content Operations","Editorial Operations","Multilingual Content Operations","Content Distribution Operations"]},
{category:"Service",items:["Service Operations","Service Reliability Operations","Incident Response Operations","Service Improvement Operations"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open programs list">Programs</button><div className="tray-content"><div className="tray-list">{[
{category:"Marketing",items:["Market Growth Program","Brand Development Program","Demand Generation Program","Market Expansion Program"]},
{category:"Product",items:["Product Development","Product Discovery Program","Product Modernization Program","Product Adoption Program"]},
{category:"Customer",items:["Customer Success","Customer Onboarding Program","Customer Retention Program","Customer Experience Improvement"]},
{category:"Knowledge",items:["Knowledge Operations","Organizational Intelligence Program","Research and Evidence Program","Knowledge Governance Program"]},
{category:"Data",items:["Data Operations","Data Quality Improvement Program","Analytics Enablement Program","Data Governance Program"]},
{category:"Reliability",items:["Service Reliability","Incident Readiness Program","Operational Resilience Program","Service Improvement Program"]},
{category:"Content",items:["Content Operations","Editorial Development Program","Content Localization Program","Content Lifecycle Program"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open processes list">Processes</button><div className="tray-content"><div className="tray-list">{[
{category:"Marketing",items:["Campaign Lifecycle","Audience Development","Marketing Optimization"]},
{category:"Research",items:["Continuous Intelligence","Research Program","Evidence Maintenance"]},
{category:"Content",items:["Editorial Lifecycle","Content Localization Program","Content Refresh and Governance"]},
{category:"Data",items:["Data Product Lifecycle","Data Quality Management","Continuous Analytics"]},
{category:"Software Delivery",items:["Feature Delivery Lifecycle","Defect Resolution Lifecycle","Release and Maintenance"]},
{category:"Business Operations",items:["Customer Support Lifecycle","Procurement and Approval","Customer Onboarding"]},
{category:"Monitoring",items:["Incident Management","Service Reliability Improvement","Change Impact Monitoring"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open full flow list">Full Flow</button><div className="tray-content"><div className="tray-list">{[
{category:"Research and Reporting",items:["Research brief to sourced report","Competitor landscape report","Literature review and evidence synthesis","Product comparison and recommendation"]},
{category:"Content Production",items:["Brief to reviewed article","Source material to presentation","Campaign brief to content package","Document translation and quality review"]},
{category:"Data Processing and Analysis",items:["Raw files to validated dataset","Documents to structured records","Dataset to analysis report","Recurring data quality assessment"]},
{category:"Software Development",items:["Feature request to implementation proposal","Bug report to verified fix","Code changes to review report","Repository to technical documentation"]},
{category:"Marketing",items:["Market research and audience insights","Campaign strategy and planning","Campaign brief to content campaign","Marketing performance analysis"]},
{category:"Business Operations",items:["Support request to resolution proposal","Meeting transcript to action plan","Invoice intake to approval package","Customer inquiry to reviewed response"]},
{category:"Monitoring and Response",items:["Service signals to incident brief","Document changes to impact report","Incoming events to triaged alerts","Incident report to response plan"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray composite-tray"><button className="tray-handle" aria-label="Open composite component list">Composite Components</button><div className="tray-content"><div className="tray-list composite-list"><details><summary>Coordination Patterns</summary><ul>{["Research and verify", "Create and critique", "Divide and consolidate", "Plan and execute"].map(name=><li key={name}>{name}</li>)}</ul></details>{[
{category:"Knowledge and Research",items:["Document retrieval and synthesis","Multi-source research","Evidence collection and citation","Knowledge ingestion and indexing"]},
{category:"Content Production",items:["Brief to draft","Editing and refinement","Translation and localization","Multi-format publishing preparation"]},
{category:"Data Processing",items:["Structured data extraction","Cleaning and normalization","Enrichment and classification","Dataset merging and deduplication"]},
{category:"Evaluation and Quality",items:["Schema and contract validation","Factual consistency review","Rubric-based scoring","Candidate comparison and ranking"]},
{category:"Actions and Integrations",items:["API request and response mapping","Cross-system record synchronization","Event filtering and dispatch","Action execution and confirmation"]},
{category:"Memory and Context",items:["Conversation summarization","Task context assembly","Persistent fact storage and retrieval","Context selection and compression"]}
].map(({category,items})=><details key={category}><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details>)}</div></div></aside><aside className="component-tray"><button className="tray-handle" aria-label="Open component list">Components</button><div className="tray-content"><div className="tray-list">{catalog.map(group=><details key={group.name}><summary>{group.name}</summary><ul>{group.items.map(item=><li key={item.id}>{item.name}{item.legacy&&<small> · legacy</small>}</li>)}</ul></details>)}</div></div></aside></div><div className="tray-stack instance-stack"><div className="stack-label">INSTANCE · Regional Workforce Intelligence<small>Turning research into sourced evidence for regional workforce decisions</small></div>{instanceLayers.map(({layer,category,items})=><aside key={layer} className="component-tray"><button className="tray-handle" aria-label={'Open instance '+layer}>{layer}<span>{items.length}</span></button><div className="tray-content"><div className="tray-list"><details open><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul></details></div></div></aside>)}</div><div className="tray-stack instance-stack referral-stack"><div className="stack-label">INSTANCE · Real Estate Referral Venture<small>Turning a real estate referral program into a profitable venture</small></div>{referralLayers.map(({layer,category,items})=><aside key={layer} className="component-tray"><button className="tray-handle" aria-label={'Open referral '+layer}>{layer}<span>{items.length}</span></button><div className="tray-content"><div className="tray-list"><details open><summary>{category}</summary><ul>{items.map(name=><li key={name}>{name}</li>)}</ul><p className="selection-note">Proposed selection{['Confederations','Federation','Alliances','Ecosystems'].includes(layer)?' · Optional partner network; not a launch requirement.':layer==='Full Flow'?' · Referral matching, consent, outcome tracking, and unit economics still need definitions.':''}</p></details></div></div></aside>)}</div></main>;
}
function Playground(){
 const [version,setVersion]=useState(()=>new URLSearchParams(window.location.search).get('version')==='2'?2:1);
 const switchVersion=value=>{setVersion(value);const url=new URL(window.location.href);url.searchParams.set('version',String(value));window.history.replaceState(null,'',url);};
 return <><nav className="version-switch" aria-label="Canvas version">{[1,2].map(value=><button key={value} aria-pressed={version===value} onClick={()=>switchVersion(value)}>V{value}</button>)}</nav><section hidden={version!==1}><VersionOne/></section><section hidden={version!==2}><VersionTwo/></section></>;
}
createRoot(document.getElementById('root')).render(<Playground/>);

import {iconCollection} from './ui/icons';
import {MessageBubble} from './ui/MessageBubble';
import {ReactFlow,ReactFlowProvider} from '@xyflow/react';
import {X} from './ui/icons';
import BlockNode from './ui/BlockNode';
import React,{useState} from 'react';
import {Button,Input,Textarea,Select} from './ui/components';

export default function UICatalog(){
 const [text,setText]=useState(''),[notes,setNotes]=useState(''),[selection,setSelection]=useState('first'),[checked,setChecked]=useState(false);
 const components=[
  ['Button',<Button key="button">Button</Button>],
  ['Icon button',<Button key="icon" className="icon-button" aria-label="Close"><X size={18}/></Button>],
  ['Node',<div key="node" className="catalog-node"><ReactFlowProvider><ReactFlow nodes={[{id:'catalog-node',type:'block',position:{x:20,y:20},data:{kind:0}}]} edges={[]} nodeTypes={{block:BlockNode}} nodesDraggable={false} nodesConnectable={false} panOnDrag={false} zoomOnScroll={false} zoomOnPinch={false} zoomOnDoubleClick={false} preventScrolling={false}/></ReactFlowProvider></div>],
  ['Input bubble',<div key="input-bubble" className="catalog-bubble"><MessageBubble direction="input" newest item={{round:1,time:'09:00',text:'Component input'}}/></div>],
  ['Output bubble',<div key="output-bubble" className="catalog-bubble"><MessageBubble newest item={{time:'09:00',text:'Component output'}}/></div>],
  ['Text input',<Input key="input" aria-label="Text input" placeholder="Text input" value={text} onChange={e=>setText(e.target.value)}/>],
  ['Textarea',<Textarea key="textarea" aria-label="Textarea" placeholder="Textarea" rows={3} value={notes} onChange={e=>setNotes(e.target.value)}/>],
  ['Select',<Select key="select" aria-label="Select" value={selection} onChange={e=>setSelection(e.target.value)}><option value="first">First option</option><option value="second">Second option</option></Select>],
  ['Icons',<ul key="icons" className="catalog-icons" aria-label="Icon collection">{Object.entries(iconCollection).map(([name,Icon])=><li key={name}><Icon size={24} weight="regular" aria-hidden="true"/><span>{name.replace(/([a-z])([A-Z])/g,'$1 $2')}</span></li>)}</ul>],
  ['Checkbox',<Input key="checkbox" type="checkbox" aria-label="Checkbox" checked={checked} onChange={e=>setChecked(e.target.checked)}/>],
 ];
 return <dl className="ui-catalog">{components.map(([name,component])=><div className="ui-catalog-entry" key={name}><dt>{name}</dt><dd>{component}</dd></div>)}</dl>;
}

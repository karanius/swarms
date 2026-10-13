import NodeFrame from './NodeFrame';
import React from 'react';
import {GearSix,Plug,PuzzlePiece,FlowArrow,TextAlignLeft,Trash} from './icons';
import {Handle,Position,NodeToolbar} from '@xyflow/react';
import {MagnifyingGlass,Files,ArrowsLeftRight,PencilLine,Stack,ShieldCheck,ArrowClockwise} from './icons';
export const blocks = [
  { name: 'Research', short: 'Research', description: 'Find sources and gather evidence', icon: MagnifyingGlass },
  { name: 'Read documents', short: 'Read', description: 'Extract information from files', icon: Files },
  { name: 'Compare', short: 'Compare', description: 'Find patterns and differences', icon: ArrowsLeftRight },
  { name: 'Write', short: 'Write', description: 'Turn findings into an output', icon: PencilLine },
  { name: 'Parallel team', short: 'Parallel', description: 'Work on multiple tasks together', icon: Stack },
  { name: 'Review', short: 'Review', description: 'Check the result before continuing', icon: ShieldCheck },
  { name: 'Repeat', short: 'Repeat', description: 'Return to a step and try again', icon: ArrowClockwise },
];
export default function BlockNode({ id, data, selected }) {
  const block = blocks[data.kind];
  const Icon = block.icon;
  return <NodeFrame inputs={data.inputs||[]} outputs={data.outputs||[]} onInputConfigure={data.onInputConfigure?()=>data.onInputConfigure(id):undefined} acceptsLogs={[0,2,3,5].includes(data.kind)&&data.runtimeRole!=='Code'} className={`${selected ? 'is-selected' : ''} ${data.liveState ? `live-${data.liveState}` : ''}`}>
    <NodeToolbar isVisible={selected} position={Position.Bottom} offset={44}><div className="canvas-node-toolbar nodrag nopan" aria-label="Node configuration">{[['settings','Node settings',GearSix],['mcp','MCP',Plug],['skills','Skills',PuzzlePiece],['cli','CLI',TextAlignLeft],['credentials','Credentials',ShieldCheck],['tracing','Tracing',FlowArrow]].map(([key,label,Icon])=><button key={key} title={label} aria-label={label} onClick={e=>{e.stopPropagation();data.onConfigure?.(id,key);}}><Icon size={19}/><span>{label}</span></button>)}<button aria-label="Delete node" title="Delete node" onClick={e=>{e.stopPropagation();data.remove?.();}}><Trash size={19}/><span>Delete</span></button></div></NodeToolbar>
    <Handle type="target" position={Position.Left} aria-label={`${block.name} input`} />
    <div className="node-top"><span className="node-icon"><Icon size={23} weight="regular" /></span><span className="node-kind">{data.runtimeRole||['Agent','File tool','Agent','Agent','Concurrent','Judge','Round robin'][data.kind]}</span></div>
    <h2>{data.label || block.name}</h2><p>{data.description||block.description}</p>{data.liveState&&<span className="node-live-status">{data.liveState==='running'?'EXO generating':data.liveState==='complete'?'Cycle complete':'EXO retrying'}</span>}

    <Handle type="source" position={Position.Right} aria-label={`${block.name} output`} />


  </NodeFrame>;
}

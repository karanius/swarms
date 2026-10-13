import React from 'react';
import IOInspector from './IOInspector';

// Every canvas node uses this shell; input/output inspection is part of the node contract.
export default function NodeFrame({children,className='',inputs=[],outputs=[],onInputConfigure,acceptsLogs=false}){
 return <div className={`block-node ${className}`}>
  {children}
  <IOInspector direction="input" items={inputs} onConfigure={onInputConfigure} acceptsLogs={acceptsLogs}/>
  <IOInspector direction="output" items={outputs}/>
 </div>;
}

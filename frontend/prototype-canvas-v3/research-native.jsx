import React from 'react';
// Jupyter owns its complete interface; the host supplies only a full-pane frame.
export default function Research(){
 return <iframe title="Jupyter Notebook research workspace" src="/research-jupyter/tree" style={{position:'absolute',inset:0,width:'100%',height:'100%',border:0}}/>;
}

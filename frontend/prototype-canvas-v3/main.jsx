import React from 'react';
import {createRoot} from 'react-dom/client';
import '@xyflow/react/dist/style.css';
import './style.css';
import VersionThree from './v3-canvas.jsx';
function Playground(){
 return <><nav className="version-switch" aria-label="Canvas version">{[1,2,3].map(value=><button key={value} aria-pressed={value===3} onClick={()=>{if(value!==3)window.location.assign('/prototype-canvas/?version='+value);}}>V{value}</button>)}</nav><VersionThree/></>;
}
createRoot(document.getElementById('root')).render(<Playground/>);

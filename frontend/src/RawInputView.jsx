import React,{useState} from 'react';
import {Files,DownloadSimple} from './ui/icons';
function Line({text}){const parts=text.split(/("(?:[^"\\]|\\.)*"\s*:)/g);return parts.map((part,i)=><span key={i} className={/^".*":$/.test(part.trim())?'raw-json-key':undefined}>{part}</span>);}
export default function RawInputView({text}){
 const [copyState,setCopyState]=useState('Copy');const lines=text.split('\n');
 async function copy(){try{await navigator.clipboard.writeText(text);setCopyState('Copied');}catch{setCopyState('Copy unavailable');}}
 function download(){const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='agent-input.txt';a.click();URL.revokeObjectURL(url);}
 return <div className="raw-input-view"><header><div><strong>Exact task and context</strong><span>Plain text with JSON records. Agent system instructions are separate.</span></div><div className="raw-input-actions"><button onClick={copy} aria-label="Copy raw input"><Files size={14}/>{copyState}</button><button onClick={download} aria-label="Download raw input"><DownloadSimple size={15}/></button></div></header><pre aria-label="Raw agent input"><code>{lines.map((line,index)=><span className="raw-input-line" data-line={index+1} key={index}><Line text={line}/>{index<lines.length-1?'\n':''}</span>)}</code></pre><footer>{lines.length} lines <span>{new TextEncoder().encode(text).length.toLocaleString()} bytes</span><span>Live composition</span></footer></div>;
}

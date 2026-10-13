import {Button,Input} from './ui/components';
import React from 'react';
import { X, DownloadSimple } from './ui/icons';

export default function ReadPanel({node,onChange,onClose}) {
  const path=node.data.read?.file_path || '';
  const spec={implementation:'swarms.structs.autonomous_loop_utils.read_file_tool',arguments:{file_path:path},requires:'Agent instance supplied by the execution adapter'};
  const download=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(spec,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`${node.id}.json`;a.click();URL.revokeObjectURL(url);};
  return <aside className="research-panel" aria-label="Read document settings"><header><div><h2>Read documents</h2><p>Configure the repository’s text reader.</p></div><Button className="icon-button" aria-label="Close read settings" onClick={onClose}><X size={18}/></Button></header><div className="research-fields">
    <p className="implementation-note">Uses <code>read_file_tool</code>. This function reads one text file per call. Configuration only; no file is read by this interface.</p>
    <label>File path<Input aria-label="File path" value={path} onChange={e=>onChange({file_path:e.target.value})} placeholder="notes/report.md"/><small>file_path: an absolute path or a path relative to the agent workspace.</small></label>
    <fieldset><legend>Path resolution</legend><p className="field-note">{path.startsWith('/') ? 'Absolute path: the reader uses this location directly.' : 'Relative path: the reader resolves this inside the supplied agent’s workspace.'}</p><p className="field-note">The browser cannot determine the Python agent’s workspace or verify that this file exists.</p></fieldset>
    <fieldset><legend>Supported input</legend><p className="field-note">UTF-8 text, including plain text, Markdown, JSON, CSV, and source files. Contents are returned as text; JSON and CSV are not parsed into structured records.</p><p className="field-note">This reader does not extract text from PDF, DOCX, images, or scanned documents. Those need a separate parser.</p></fieldset>
    <fieldset><legend>Returned content</legend><p className="field-note">Returns file text, truncated using the supplied agent’s context length and model. Reading failures return an error message. It also records the read operation in the agent’s conversation memory.</p><p className="field-note">Encoding and truncation are implementation behavior, not configurable arguments on this tool.</p></fieldset>
    <details open><summary>Python configuration mapping</summary><pre>{JSON.stringify(spec,null,2)}</pre></details>
    <Button className="export-button" onClick={download} disabled={!path.trim()}><DownloadSimple size={16}/>Export configuration</Button>
  </div></aside>;
}

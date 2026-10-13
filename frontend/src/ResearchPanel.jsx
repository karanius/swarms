import {Button,Input,Textarea,Select} from './ui/components';
import AgentOptions, {agentOptions,agentOptionDefaults} from './AgentOptions';
import {libraryPresets} from './libraryPresets';
import EffortSelect, {effortArgs} from './EffortSelect';
import ModelSelect,{profileArgs} from './ModelSelect';
import React from 'react';
import { X, DownloadSimple } from './ui/icons';

export const researchDefaults = { ...agentOptionDefaults,
  task: '', system_prompt: libraryPresets.research.text,
  reasoning_effort: 'high', model_name: 'gpt-6.1-sol', max_loops: 1, plan_enabled: false, output_type: 'str-all-except-first', mcp_urls: '', max_tokens: '', temperature: '',
};
export function researchSpec(node) {
  const c = { ...researchDefaults, ...node.data.research };
  const args = { agent_name: node.id, agent_description: 'Research specialist', system_prompt: c.system_prompt, model_name: c.model_name, ...effortArgs(c),...agentOptions(c),...profileArgs(c), max_loops: c.max_loops, plan_enabled: c.plan_enabled, output_type: c.output_type };
  if (c.mcp_urls.trim()) args.mcp_urls = c.mcp_urls.split('\n').map(s=>s.trim()).filter(Boolean);
  if (c.max_tokens !== '') args.max_tokens = Number(c.max_tokens);
  if (c.temperature !== '') args.temperature = Number(c.temperature);
  return { implementation: 'swarms.Agent', constructor: args, run: { task: c.task } };
}
export default function ResearchPanel({node,onChange,onClose}) {
  const c = {...researchDefaults,...node.data.research};
  const change = (key,value) => onChange({...c,[key]:value});
  const exportConfig = () => {
    const url=URL.createObjectURL(new Blob([JSON.stringify(researchSpec(node),null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download=`${node.id}.json`;a.click();URL.revokeObjectURL(url);
  };
  return <aside className="research-panel" aria-label="Research settings">
    <header><div><h2>{node.data.label || 'Research'}</h2><p>Configure this research agent.</p></div><Button className="icon-button" onClick={onClose} aria-label="Close research settings"><X size={18}/></Button></header>
    <div className="research-fields"><p className="implementation-note">Default instructions: {libraryPresets.research.type}. Source: <code>{libraryPresets.research.source}</code>. You can edit the text below.</p>
      <p className="implementation-note">Uses <code>swarms.Agent</code>, following the repository’s research example. Settings are stored on this node; execution is not connected.</p>
      <label>Research task<Textarea value={c.task} onChange={e=>change('task',e.target.value)} placeholder="What should this node investigate?" rows={3}/><small>Passed to Agent.run(task). Upstream input can be mapped later.</small></label>
      <label>Research instructions<Textarea value={c.system_prompt} onChange={e=>change('system_prompt',e.target.value)} rows={6}/><small>system_prompt: defines how this agent researches.</small></label>
      <label>Reasoning effort<EffortSelect aria-label="Reasoning effort" model={c.model_name} value={c.reasoning_effort} onChange={v=>change('reasoning_effort',v)}/><small>Default leaves effort unset. Higher effort uses more reasoning time.</small></label><label>Model<ModelSelect value={c.model_name} onChange={v=>onChange({...c,model_name:v,reasoning_effort:''})}/><small>model_name: provider-compatible model ID. Availability is not checked.</small></label>
      <fieldset><legend>Execution</legend><label>Loop mode<Select value={c.max_loops === 'auto' ? 'auto' : 'fixed'} onChange={e=>change('max_loops',e.target.value === 'auto' ? 'auto' : 1)}><option value="fixed">Fixed iterations</option><option value="auto">Autonomous until complete</option></Select></label>
      {c.max_loops !== 'auto' ? <label>Maximum iterations<Input type="number" min="1" step="1" value={c.max_loops} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>0)change('max_loops',n);}}/></label> : <p className="field-note">max_loops="auto" uses the agent’s autonomous loop. It is not a time or cost limit.</p>}
      <label className="check-field"><Input type="checkbox" checked={c.plan_enabled} onChange={e=>change('plan_enabled',e.target.checked)}/>Plan before executing</label><small>plan_enabled: an additional planning step.</small></fieldset>
      <fieldset><legend>Research tools</legend><label>MCP server URLs<Textarea value={c.mcp_urls} onChange={e=>change('mcp_urls',e.target.value)} placeholder="One server URL per line" rows={3}/><small>mcp_urls: tool servers the Python agent can connect to.</small></label><p className="field-note">No search tool is attached by default. URLs are configuration only here; this UI does not connect to servers. Python callable tools require a backend registry.</p></fieldset>
      <label>Returned output<Select value={c.output_type} onChange={e=>change('output_type',e.target.value)}>{['str-all-except-first','final','json','dict','list','yaml'].map(v=><option key={v}>{v}</option>)}</Select><small>output_type controls returned conversation data, not report quality or citation accuracy.</small></label>
      <details><summary>Model parameters</summary><label>Maximum output tokens<Input type="number" min="1" step="1" value={c.max_tokens} onChange={e=>change('max_tokens',e.target.value)} placeholder="Model default"/><small>max_tokens: left unset unless you specify a value.</small></label><label>Temperature<Input type="number" min="0" max="2" step="0.1" value={c.temperature} onChange={e=>change('temperature',e.target.value)} placeholder="Provider default"/><small>temperature: support and range depend on the model.</small></label></details>
      <AgentOptions config={c} onChange={change}/><details><summary>Python configuration mapping</summary><pre>{JSON.stringify(researchSpec(node),null,2)}</pre></details>
      <Button className="export-button" onClick={exportConfig}><DownloadSimple size={16}/>Export configuration</Button>
    </div>
  </aside>;
}

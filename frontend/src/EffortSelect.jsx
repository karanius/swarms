import {Select} from './ui/components';
import React,{useContext} from 'react';
import {ModelProfileContext} from './ModelSelect';
import {codexModels} from './ModelSelect';
export function effortOptions(model){return codexModels.some(([id])=>id===model)?['low','medium','high','xhigh','max']:[];}
export const effortArgs=c=>c.reasoning_effort&&effortOptions(c.model_name).includes(c.reasoning_effort)?{reasoning_effort:c.reasoning_effort}:{};
export default function EffortSelect({model,value='',onChange,...props}){const {profile}=useContext(ModelProfileContext);const levels=profile==='exo'?[]:effortOptions(model);const labels={low:'Light (low)',medium:'Medium',high:'High',xhigh:'Extra High',max:'Max'};return <Select {...props} value={value||''} onChange={e=>onChange(e.target.value)}><option value="">{profile==='exo'?'EXO model default':'Model default'}</option>{value&&!levels.includes(value)&&<option value={value} disabled>{value} (not verified for this model)</option>}{levels.map(v=><option key={v} value={v}>{labels[v]}</option>)}{levels.length>0&&!model.endsWith('luna')&&<option disabled>Ultra: subagent mode not connected</option>}</Select>;}

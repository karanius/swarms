import {Select} from './ui/components';
import React,{createContext,useContext} from 'react';
export const ModelProfileContext=createContext({profile:'codex',models:[],status:''});
export const profileArgs=c=>c.model_profile==='exo'?{llm_base_url:'http://127.0.0.1:52416/v1',model_name:`openai/${c.model_name}`,reasoning_effort:null}:{};
export const codexModels=[
 ['gpt-6.1-sol','GPT-6.1 Sol'],['gpt-6-astra','GPT-6 Astra'],['gpt-6-sol','GPT-6 Sol'],['gpt-6-luna','GPT-6 Luna'],['gpt-5.6-sol','GPT-5.6 Sol'],['gpt-5.6-terra','GPT-5.6 Terra'],['gpt-5.6-luna','GPT-5.6 Luna'],
];
export default function ModelSelect({value,onChange,...props}){const {profile,models,status}=useContext(ModelProfileContext);const list=profile==='exo'?models.map(m=>[m.id,m.name||m.id]):codexModels;return <Select {...props} value={value} onChange={e=>onChange(e.target.value)} disabled={profile==='exo'&&!list.length}>{!list.some(([id])=>id===value)&&<option value={value}>{profile==='exo'?(status||'Choose an EXO model'):'Choose a model'}</option>}{list.map(([id,label])=><option key={id} value={id}>{label}</option>)}</Select>;}


export function normalizeModelConfig(kind,config={}){
 if(config.model_profile==='exo')return config;
 const current=codexModels.some(([id])=>id===config.model_name);
 const roles={research:['gpt-6.1-sol','high'],compare:['gpt-6.1-sol','high'],write:['gpt-6-luna','high'],review:['gpt-6-astra','medium']};
 if(!roles[kind])return config;
 const [model,effort]=roles[kind];
 if(current)return config;
 const previous=config.reasoning_effort;
 return {...config,model_name:model,reasoning_effort:['low','medium','high','xhigh','max'].includes(previous)?previous:effort};
}

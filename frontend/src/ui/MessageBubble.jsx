import React from 'react';
export function MessageBubble({direction='output',item,newest=false}){
 return <div className={`node-${direction}-bubble ${newest?'newest':''}`}><div className={`${direction}-bubble-meta`}><span>{item.providerId?'Supplied logs':`${newest?'Latest':'Earlier'} ${direction}`}{direction==='input'&&item.round&&` / round ${item.round}`}</span><time>{item.time}</time></div><p>{item.text}</p></div>;
}

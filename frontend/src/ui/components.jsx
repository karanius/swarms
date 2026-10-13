import React from 'react';
import './components.css';
/** Shared native action, preserving consumer layout classes and button attributes. */
export function Button({className='',type='button',...props}){return <button type={type} className={`ui-button ${className}`.trim()} {...props}/>;}

/** Native fields preserve controlled values, labels, validation and consumer styles. */
export function Input({className='',...props}){return <input className={`ui-input ${className}`.trim()} {...props}/>;}
export function Textarea({className='',...props}){return <textarea className={`ui-textarea ${className}`.trim()} {...props}/>;}

/** Shared select retains native options and browser keyboard navigation. */
export function Select({className='',...props}){return <select className={`ui-select ${className}`.trim()} {...props}/>;}

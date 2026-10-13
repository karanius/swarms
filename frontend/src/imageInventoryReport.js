export function inventoryReport(job){
 if(!job?.inventory)return null;
 const i=job.inventory,v=job.verification;
 const number=n=>Number(n||0).toLocaleString('en-US');
 const sections=[
  {heading:'Summary',rows:[['Measure','Result'],['Image files',number(i.imageFiles)],['Entries examined',number(i.entries)],['Directories examined',number(i.directories)],['Unreadable paths',number(i.unreadable.length)],['Symbolic links skipped',number(i.symlinksSkipped)],['Coverage',v?.coverage||'Verification pending'],['Count consistency',v?v.consistent?'Folder and format totals agree':'Totals do not agree':'Verification pending']]},
  {heading:'Scan scope',list:i.roots,text:'Completed: '+i.completedAt+'\nRun ID: '+job.id},
  {heading:'Image formats',rows:[['Extension','Files'],...Object.entries(i.formats).sort((a,b)=>b[1]-a[1]).map(([ext,count])=>[ext,number(count)])]},
  {heading:'Folders with the most image files',text:'Top 50 folders, ordered by count. Counts refer to files directly within each folder.',rows:[['Folder','Files'],...Object.entries(i.folders).sort((a,b)=>b[1]-a[1]).slice(0,50).map(([folder,count])=>[folder,number(count)])]},
  {heading:'Coverage and counting rules',list:[i.unreadable.length?'Partial inventory: unreadable paths are listed below.':'No enumeration errors were recorded in the requested scope.','Files are recognized by extension; image contents were not opened or validated.','Copies and different paths count separately. This is not a count of unique photographs.','Software icons, repository assets, and other image files are included.','Symbolic links are not followed. Unrequested folders and external volumes are outside the scope.','Physical files in Photos libraries are not equivalent to logical Photos assets.','Cloud-only items may not be downloaded. Filesystem changes during scanning are not an atomic snapshot.','The report is generated from scanner evidence. The AI explanation does not change the count.']},
  {heading:'Unreadable paths',...(i.unreadable.length?{rows:[['Path','Reason'],...i.unreadable.map(r=>[r.path,r.reason])]}:{text:'None recorded.'})}
 ];
 const escape=value=>String(value??'').replaceAll('\\','\\\\').replaceAll('|','\\|').replace(/([`*_\[\]])/g,'\\$1').replaceAll('\r',' ').replaceAll('\n',' ').replace(/[<>]/g,c=>c==='<'?'&lt;':'&gt;');
 const table=rows=>[rows[0].map(escape).join(' | '),rows[0].map(()=>'---').join(' | '),...rows.slice(1).map(r=>r.map(escape).join(' | '))].map(row=>'| '+row+' |').join('\n');
 const markdown='# Image inventory\n\n'+sections.map(s=>'## '+s.heading+'\n\n'+[s.text,s.list?.map(item=>'- '+escape(item)).join('\n'),s.rows?table(s.rows):null].filter(Boolean).join('\n\n')).join('\n\n')+'\n';
 return {title:'Image inventory',sections,markdown};
}
export function downloadInventoryReport(report){
 const url=URL.createObjectURL(new Blob([report.markdown],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='image-inventory.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

// Host integration only: keep native Notebook's local navigation in its pane.
// No notebook DOM, controls, styles, or upstream sources are changed.
(()=>{
 document.documentElement.dataset.researchNavigation='ready';
 const internal=value=>{try{const url=new URL(String(value),location.href);return url.origin===location.origin&&url.pathname.startsWith('/research-jupyter/')?url:null;}catch{return null;}};
 const originalOpen=window.open.bind(window);
 window.open=(url,target,features)=>{const destination=url&&internal(url);if(destination){location.href=destination.href;return window;}return originalOpen(url,target,features);};
 document.addEventListener('click',event=>{const link=event.target.closest?.('a[href]');if(!link||link.target!=='_blank')return;const destination=internal(link.href);if(destination){event.preventDefault();event.stopPropagation();location.href=destination.href;}},true);
})();
// Paper 6's live inventory is a host-owned read-only view, independent of kernel execution.
(()=>{
 if(!decodeURIComponent(location.pathname).includes('Paper 6 - Rule Mining from Langflow Templates.ipynb'))return;
 window.addEventListener('message',event=>{if(event.origin!==location.origin||event.data?.type!=='corpus-inventory-height')return;for(const f of document.querySelectorAll('iframe[title="Live Langflow corpus inventory"]'))if(event.source===f.contentWindow)f.style.height=Math.min(650,Math.max(65,Number(event.data.height)||65))+'px';});
 const attach=()=>{for(const heading of document.querySelectorAll('h2')){if(heading.textContent.trim()!=='Live corpus inventory')continue;const cell=heading.closest('.jp-RenderedMarkdown');if(!cell||cell.querySelector('iframe'))continue;const frame=document.createElement('iframe');frame.src='/research-corpus-inventory.html';frame.title='Live Langflow corpus inventory';frame.style.cssText='width:100%;height:570px;border:0';cell.replaceChildren(frame);}};
 new MutationObserver(attach).observe(document.documentElement,{subtree:true,childList:true});attach();
})();
// Explicit Paper 6 figure: same-origin corpus explorer, no kernel trust required.
(()=>{
 if(!decodeURIComponent(location.pathname).includes('Paper 6 - Rule Mining from Langflow Templates.ipynb'))return;
 const attach=()=>{for(const heading of document.querySelectorAll('h2')){if(heading.textContent.trim()!=='Interactive corpus topology')continue;const cell=heading.closest('.jp-RenderedMarkdown');if(!cell||cell.querySelector('iframe'))continue;const frame=document.createElement('iframe');frame.src='/corpus-explorer/';frame.title='Langflow corpus topology explorer';frame.style.cssText='width:100%;height:760px;border:0';cell.replaceChildren(frame);}};
 new MutationObserver(attach).observe(document.documentElement,{subtree:true,childList:true});attach();
})();
// Separate Paper 6 pattern figure; the original corpus map remains unchanged.
(()=>{
 if(!decodeURIComponent(location.pathname).includes('Paper 6 - Rule Mining from Langflow Templates.ipynb'))return;
 const attach=()=>{for(const heading of document.querySelectorAll('h2')){if(heading.textContent.trim()!=='Connected pattern explorer')continue;const cell=heading.closest('.jp-RenderedMarkdown');if(!cell||cell.querySelector('iframe'))continue;const frame=document.createElement('iframe');frame.src='/pattern-explorer/';frame.title='Connected patterns and association evidence';frame.style.cssText='width:100%;height:1100px;border:0';cell.replaceChildren(frame);}};
 new MutationObserver(attach).observe(document.documentElement,{subtree:true,childList:true});attach();
})();
// Independent candidate-group figure: source-backed boundary inspection, no execution.
(()=>{
 if(!decodeURIComponent(location.pathname).includes('Paper 6 - Rule Mining from Langflow Templates.ipynb'))return;
 const attach=()=>{for(const heading of document.querySelectorAll('h2')){if(heading.textContent.trim()!=='Candidate group explorer')continue;const cell=heading.closest('.jp-RenderedMarkdown');if(!cell||cell.querySelector('iframe'))continue;const frame=document.createElement('iframe');frame.src='/candidate-explorer/';frame.title='Candidate groups and exposed boundaries';frame.style.cssText='width:100%;height:1350px;border:0';cell.replaceChildren(frame);}};
 new MutationObserver(attach).observe(document.documentElement,{subtree:true,childList:true});attach();
})();
// Paper6's exclusive collaborator is a separate host-owned research workspace.
(()=>{
 if(!decodeURIComponent(location.pathname).includes('Paper 6 - Rule Mining from Langflow Templates.ipynb'))return;
 const attach=()=>{for(const heading of document.querySelectorAll('h2')){if(heading.textContent.trim()!=='Dedicated research assistant')continue;const cell=heading.closest('.jp-RenderedMarkdown');if(!cell||cell.querySelector('iframe'))continue;const frame=document.createElement('iframe');frame.src='/paper6-assistant.html';frame.title='Exclusive Paper6 Langflow research assistant';frame.style.cssText='width:100%;height:1050px;border:0';cell.replaceChildren(frame);}};
 new MutationObserver(attach).observe(document.documentElement,{subtree:true,childList:true});attach();
})();

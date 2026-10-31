export function layerSceneModel(graph,upperGraph,items){
 const components=graph.nodes.filter(node=>node.type==='genericNode').map((node,index,array)=>({id:node.id,label:node.data.node?.display_name??node.data.type,type:node.data.type,position:[(index-(array.length-1)/2)*4.2,.28,0]}));
 const ids=new Set(components.map(node=>node.id));
 const composites=upperGraph.nodes.map(node=>{const item=items.find(item=>item.id===node.data.customItemId);return item?{id:node.id,itemId:item.id,label:node.data.label??item.name,children:node.data.childNodeIds??item.realization?.childNodeIds??item.assembly.nodes.map(child=>child.id),contract:node.data.contract??item.contract}:null;}).filter(Boolean).map((node,index,array)=>({...node,position:[(index-(array.length-1)/2)*4.5,4.6,.5]}));
 const edges=graph.edges.filter(edge=>ids.has(edge.source)&&ids.has(edge.target)).map(edge=>({id:edge.id,source:edge.source,target:edge.target,kind:'data-flow'}));
 for(const composite of composites)for(const child of composite.children)if(ids.has(child))edges.push({id:composite.id+':'+child,source:child,target:composite.id,kind:'membership'});
 return {components,composites,edges};
}

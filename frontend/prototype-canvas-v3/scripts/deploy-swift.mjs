// Deployment binds a new instance to Langflow's existing persistent flow controller.
export async function deploySwift(instance,request=fetch){
 if(instance.state!=='assembled')throw Error('Assemble the instance before deployment.');
 const response=await request('/api/v1/flows/',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:instance.name+' · '+instance.id.slice(-8),data:instance.data,is_component:false,description:'Assembled from Swift template '+instance.templateRef.version})});
 if(!response.ok)throw Error('Instance deployment failed ('+response.status+').');
 const flow=await response.json();
 return {...instance,state:'deployed',deployment:{runtime:'langflow',flowId:flow.id},flow};
}

export default {name:"Market Growth Program",category:"Marketing",status:"hypothetical",nodes:[
{id:'intelligence',position:{x:260,y:100},data:{label:'Continuous Intelligence'}},
{id:'audience',position:{x:530,y:100},data:{label:'Audience Development'}},
{id:'editorial',position:{x:800,y:100},data:{label:'Editorial Lifecycle'}},
{id:'campaign',position:{x:800,y:330},data:{label:'Campaign Lifecycle'}},
{id:'analytics',position:{x:530,y:330},data:{label:'Continuous Analytics'}},
{id:'optimization',position:{x:260,y:330},data:{label:'Marketing Optimization'}}
],edges:[
{id:'intel-audience',source:'intelligence',target:'audience',label:'Market findings'},
{id:'audience-editorial',source:'audience',target:'editorial',label:'Audience priorities'},
{id:'editorial-campaign',source:'editorial',target:'campaign',label:'Content assets'},
{id:'campaign-analytics',source:'campaign',target:'analytics',label:'Requires measured campaign data'},
{id:'analytics-optimization',source:'analytics',target:'optimization',label:'Performance insights'},
{id:'optimization-audience',source:'optimization',target:'audience',label:'Refine targeting',style:{strokeDasharray:'5 5'}}
]};

export default {name:"Shared Research and Infrastructure Initiative",status:"hypothetical",nodes:[
{id:'research',position:{x:320,y:100},data:{label:'Research Collaboration Confederation'}},
{id:'workforce',position:{x:760,y:100},data:{label:'Workforce Development Confederation'}},
{id:'infrastructure',position:{x:760,y:400},data:{label:'Digital Infrastructure Confederation'}},
{id:'resources',position:{x:320,y:400},data:{label:'Resource Stewardship Confederation'}}
],edges:[
{id:'research-workforce',source:'research',target:'workforce',label:'Research and emerging skill needs'},
{id:'workforce-infrastructure',source:'workforce',target:'infrastructure',label:'Specialist capacity'},
{id:'infrastructure-research',source:'infrastructure',target:'research',label:'Shared computing access'},
{id:'resources-infrastructure',source:'resources',target:'infrastructure',label:'Resource constraints and guidance'},
{id:'research-resources',source:'research',target:'resources',label:'Efficiency research findings'}
]};

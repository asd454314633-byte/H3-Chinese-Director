// SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import {app} from '../../../scripts/app.js';
import {api} from '../../../scripts/api.js';
export function enabled(){return app.graph?.extra?.h3_prebake_production?.enabled===true}
export function storyId(node){
 if(!enabled())return null;
 return node.properties.h3_prebake_story_id ||= 'H3_PREBAKE_'+crypto.randomUUID().replaceAll('-','');
}
async function request(name,data){
 const response=await api.fetchApi('/h3/prebake/'+name,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
 const result=await response.json();if(!response.ok)throw Error('PreBake '+(result.error||response.status));return result;
}
export async function restoreProductionIdentity(node){
 if(!enabled())return null;
 const result=await request('story',{action:'restore',story_id:storyId(node)});
 if(result.binding){node.properties.h3_prebake_binding=result.binding;node.properties.h3_prebake_revisions=[...result.binding.revisions]}
 else if(node.properties.h3_prebake_binding)throw Error('服务端故事绑定缺失；拒绝切换目录，请检查原存档');
 return result.binding;
}
export async function syncProductionTexts(node){
 if(!enabled()||!node.__sixRoot)return;
 const binding=node.properties.h3_prebake_binding;if(!binding)return;
 const texts=[...node.__sixRoot.querySelectorAll('.six-prompt')].map(a=>a.value);
 if(texts.length!==6)return;
 const result=await request('invalidate',{context:binding,texts});
 node.properties.h3_prebake_binding=result.binding;node.properties.h3_prebake_revisions=[...result.binding.revisions];node.properties.h3_prebake_texts=[...texts];
}
export async function restoreProductionExecution(node){
 if(!enabled()||!node.__sixUI)return;
 const root=node.__sixRoot,ui=node.__sixUI;
 const result=await request('story',{action:'restore',story_id:storyId(node)});
 if(!result.binding)return;
 const binding=node.properties.h3_prebake_binding;
 if(['story_id','group_id','project_id','execution_version'].some(k=>binding[k]!==result.binding[k]))throw Error('恢复期间故事版本改变；请重新加载');
 let pending=false,blocked=false;
 for(let i=0;i<6;i++){
  const state=result.segments?.[i],card=ui.cards[i];if(!state)continue;
  const a=state.attempt||{},receipt=state.receipt||{};
  const active=['PREPARED','PENDING','CANCELLING','BLOCKED'].includes(a.status);pending ||= active;blocked ||= a.status==='BLOCKED';
  const label=active?'后台任务恢复中：'+a.status:state.video_status;
  card.status.textContent=label||'未生成';
  if(state.video_status==='SUCCESS'&&receipt.status==='SUCCESS'&&receipt.prompt_id===a.prompt_id&&receipt.group_id===binding.group_id&&receipt.project_id===binding.project_id&&receipt.revision===state.revision&&receipt.cache_key===state.cache_key){
   if(card.videoRef?.prompt_id!==receipt.prompt_id){
    if(receipt.video_output_ref)ui.setSegmentVideo(i,receipt.video_output_ref);
    else try{await ui.bindSegmentVideo(i,{prompt_id:receipt.prompt_id})}catch(error){card.videoLabel.textContent='已接受的历史任务；服务器history已不可用，无法恢复视频预览';}
   }
   card.status.textContent='上次执行成功（服务端恢复）';
  }else if(!active){
   card.video.pause();card.video.removeAttribute('src');card.video.load();card.video.hidden=true;card.videoRef=null;card.videoLabel.textContent='暂无本段有效视频';
   if(state.video_status==='SUCCESS'){card.status.textContent='恢复阻断：成功回执不完整';pending=true;blocked=true}
  }
 }
 node.__h3RecoveredPending=pending;
 root.dispatchEvent(new Event('sixchange'));
 if(pending){
  root.querySelector('.six-status').textContent='后台任务仍在运行或等待确认；不重复提交。终态后自动恢复结果。';
  clearTimeout(node.__h3RecoveryTimer);
  node.__h3RecoveryStarted ||= performance.now();
  if(!blocked&&performance.now()-node.__h3RecoveryStarted<335000)node.__h3RecoveryTimer=setTimeout(()=>{if(node.__sixRoot===root&&app.graph._nodes.includes(node))restoreProductionExecution(node).catch(error=>{node.__h3RecoveredPending=true;root.querySelector('.six-status').textContent='恢复阻断：'+error.message})},1000);
  else root.querySelector('.six-status').textContent='恢复阻断：任务未确认结束或回执不完整。未提交任何新任务。';
 }
 return result;
}
function setState(root,index,state){
 if(!root)return;
 const cards=root.querySelectorAll('.six-card');
 let label=cards[index]?.querySelector('.six-prebake-state');
 if(!label){label=document.createElement('small');label.className='six-prebake-state';cards[index]?.querySelector('h3')?.after(label)}
 if(label)label.textContent='PreBake: '+state;
}
function contextFor(index,options,text){
 const node=app.graph._nodes.find(n=>n.type==='H3SixDirectorState'&&n.properties.h3_six_director);
 if(!node?.__sixRoot)throw Error('PreBake requires real six-panel UI');
 const root=node.__sixRoot,areas=[...root.querySelectorAll('.six-prompt')];
 if(areas.length!==6)throw Error('Six final text mapping missing');
 const texts=areas.map(a=>a.value);if(texts[index]!==text)throw Error('Final UI text changed before freeze');
 const revisions=node.properties.h3_prebake_revisions ||= [0,0,0,0,0,0];
 const previous=node.properties.h3_prebake_texts ||= ['','','','','',''];
 texts.forEach((t,i)=>{if(t!==previous[i]){revisions[i]++;previous[i]=t;setState(root,i,'STALE')}});
 const gid=node.properties.h3_prebake_binding?.group_id||node.__sixUI?.group?.id||node.properties.h3_prebake_last_plan?.group_id||storyId(node);
 if(!gid||gid.length>64||!/^[A-Za-z0-9_-]+$/.test(gid))throw Error('Invalid isolated PreBake story identity');
 return {root,texts,context:{project_id:node.properties.h3_prebake_binding?.project_id||null,group_id:gid,revisions:[...revisions],fps:24},node};
}
export async function prepareProduction(snapshot,text,index,options,update,waitForCompletion){
 if(!enabled())return null;
 if(options.continuous!==true){update('PreBake FALLBACK：非六段连续路径');return null}
 const {root,texts,context,node}=contextFor(index,options,text);
 const resolveFps=(value)=>{if(!Array.isArray(value))return Number(value);const n=snapshot.output[value[0]];if(n?.class_type?.startsWith('Primitive'))return Number(n.inputs.value);if(n?.class_type==='Any Switch (rgthree)')return resolveFps(Object.entries(n.inputs).sort().find(([,v])=>v!=null)?.[1]);throw Error('PreBake cannot resolve actual output fps')};
 const fpsInput=snapshot.output['764']?.inputs?.fps;context.fps=resolveFps(fpsInput);if(!Number.isFinite(context.fps)||context.fps<=0)throw Error('Invalid actual output fps');
 await node.__h3EditSync;
 const bound=node.properties.h3_prebake_binding;
 const generated=node.__sixUI?.group?.id;
 const newStory=bound&&generated&&generated!==bound.group_id;
 const identity=newStory?'H3_PREBAKE_'+crypto.randomUUID().replaceAll('-',''):storyId(node);
 const selectedStart=Number(root.querySelector('.six-start').value);
 const selectedMode=root.querySelector('.six-inheritance').value;
 const result=await request('story',{action:'bind',story_id:identity,previous_story_id:newStory?storyId(node):null,group_id:newStory?generated:context.group_id,project_id:newStory?generated:(bound?.project_id||options.project_id||'H3_SIX_V288'),execution_version:newStory?null:bound?.execution_version,start_index:selectedStart,start_mode:selectedMode});
 node.properties.h3_prebake_story_id=identity;node.properties.h3_prebake_binding=result.binding;
 Object.assign(context,result.binding,{fps:context.fps});
 // Server revisions survive refresh; local values describe only newly edited texts.
 context.revisions=result.binding.revisions.map((revision,i)=>Math.max(revision,revisionsFor(node,i,texts[i])));
 const prepareNode=Object.values(snapshot.output).find(n=>n.class_type==='H3ContinuationPrepare')?.inputs||{};
 const cleanRebase=prepareNode.clean_rebase_enabled===true&&Number(prepareNode.clean_rebase_segment)===index;
 const requirePredecessor=index>0&&options.continuous===true&&!options.independent&&!cleanRebase;
 const planned=await request('plan',{graph:snapshot.output,texts,context,requested_index:index,require_predecessor:requirePredecessor});
 await restoreProductionIdentity(node);
 for(const p of planned.plans)setState(root,p.index,p.status);
 const current=planned.plans[index];
 if(current.status==='DYNAMIC_FALLBACK'){update('PreBake FALLBACK：'+current.reason);return {fallback:true,context,reason:current.reason,index,text,cache_key:current.cache_key}}
 if(current.status==='ERROR')throw Error(current.reason);
 if(index>0&&options.continuous===true&&!options.independent&&!cleanRebase){
  const response=await api.fetchApi('/h3/six/store?project_id='+encodeURIComponent(context.project_id)+'&segment_index='+(index-1));
  const state=await response.json();if(!response.ok)throw Error('PreBake predecessor is not eligible: '+(state.error||response.status));
 }
 // Bind real video receipts to one stable story across manual 1/2 acceptance and later 3..6 batch.
 const state=await api.fetchApi('/h3/six/native-merge?project_id='+encodeURIComponent(context.project_id));const merge=await state.json();
 if(merge.group_id!==context.group_id){
  if(index>0&&!options.independent)throw Error('Current story has no accepted predecessor group');
  const response=await api.fetchApi('/h3/six/native-merge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id:context.project_id,action:'begin',group_id:context.group_id})});if(!response.ok)throw Error('Unable to begin exact Native group');
 }
 const missing=planned.plans.filter(p=>['STATIC_ELIGIBLE','CACHE_STALE'].includes(p.status));
 for(let j=0;j<missing.length;j++){
  const p=missing[j];setState(root,p.index,'BAKING');update('PreBake：烘焙第'+(p.index+1)+'段');
  const graph=structuredClone(p.bake_graph);
  if(j===missing.length-1){graph.PREBAKE_TE={class_type:'H3SelectiveTEUnload',inputs:{conditioning:['136',0]}};graph.PREBAKE_BAKE.inputs.conditioning=['PREBAKE_TE',0];graph.PREBAKE_BAKE.inputs.require_te_released=true}
  const submitted=await api.queuePrompt(0,{output:graph,workflow:snapshot.workflow});
  if(!submitted?.prompt_id)throw Error('No Bake prompt_id; no retry');
  const monitor=waitForCompletion(submitted.prompt_id);try{await monitor.promise}finally{monitor.cleanup()}
  setState(root,p.index,'CACHED');
  (node.properties.h3_prebake_bake_receipts ||= []).push({segment:p.index,prompt_id:submitted.prompt_id,cache_key:p.cache_key});
 }
 // Later textarea edits remain authoritative. Never generate this segment from a superseded Bake.
 if(root.querySelectorAll('.six-prompt')[index].value!==text)throw Error('本段最终文字在Bake期间修改；旧缓存不会执行，请重新执行本段');
 const prepared={context,contract_json:current.contract_json,cache_key:current.cache_key,index,text,root,require_predecessor:requirePredecessor};
 node.properties.h3_prebake_last_plan={group_id:context.group_id,plans:planned.plans.map(p=>({index:p.index,status:p.status,cache_key:p.cache_key,reason:p.reason}))};
 update('PreBake CACHED；TE已释放，准备生成');return prepared;
}
function revisionsFor(node,index,text){return node.properties.h3_prebake_revisions?.[index]||0}
export async function cachedGraph(graph,p){if(!p)return graph;const result=await request(p.fallback?'fallback':'generate',{graph,context:p.context,index:p.index,text:p.text,cache_key:p.cache_key,contract_json:p.contract_json,require_predecessor:p.require_predecessor,anchor_clean_rebase:true});p.attempt_id=result.attempt_id;return result.graph}
export async function acceptProduction(p,prompt_id){
 if(!p)return;
 await request('accepted',{context:p.context,index:p.index,prompt_id,cache_key:p.cache_key});setState(p.root,p.index,'CACHED / VIDEO_SUCCESS');
}

export async function submitProduction(p,graph,workflow,client_id){return request('submit',{context:p.context,index:p.index,attempt_id:p.attempt_id,graph,workflow,client_id})}
export async function productionStatus(p,prompt_id,cancel=false){return request(cancel?'cancel':'attempt-status',{context:p.context,index:p.index,attempt_id:p.attempt_id,prompt_id})}

# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""HTTP adapter; reference decisions belong only to ReferenceContractV2."""
import json
from . import v28_reference_contract as RC


def sanitize_graph(graph, context=None):
    nodes = [n for n in graph.values() if n.get('class_type')=='MiniMaxH3ReferenceToVideo']
    if nodes and all(n.get('_meta',{}).get('h3_reference_receipt_v2') for n in nodes):
        return {'graph':RC.SERVER.verify_graph(graph,context),'receipts':[n['_meta']['h3_reference_receipt_v2'] for n in nodes],'source_updates':[]}
    if context is None:
        identity=RC.digest(sorted(graph))
        context={'project_id':'direct_'+identity,'workflow_id':'direct_'+identity,'segment_id':1,
                 'generation_mode':'MANUAL_FULL','workflow_revision':0,'edit_epoch':'direct'}
    return RC.SERVER.compile_graph(graph,context)


def request_middleware():
    from aiohttp import web
    @web.middleware
    async def admission(request,handler):
        receipts=[]
        if request.method=='POST' and request.path=='/prompt':
            try:
                body=await request.json()
                graph=body.get('prompt',{})
                conditions=[n for n in graph.values() if n.get('class_type')=='MiniMaxH3ReferenceToVideo']
                if conditions:
                    workflow=body.get('extra_data',{}).get('extra_pnginfo',{}).get('workflow')
                    context=(workflow or {}).get('extra',{}).get('h3_reference_context') if isinstance(workflow,dict) else body.get('reference_context')
                    if workflow is not None and (context is None or any(not n.get('_meta',{}).get('h3_reference_receipt_v2') for n in conditions)):
                        RC.fail('H3_REFERENCE_RECEIPT_INVALID','旧页面/旧工作流，请刷新并重新编译')
                    result=sanitize_graph(graph,context)
                    body['prompt']=result['graph'];receipts=result['receipts']
                    request._read_bytes=json.dumps(body,ensure_ascii=False).encode('utf-8')
            except (ValueError,TypeError,KeyError) as exc:
                return web.json_response({'error':{'type':str(exc).split(':',1)[0],'message':str(exc)}},status=400)
        response=await handler(request)
        if receipts and response.status==200:
            try: prompt_id=json.loads(response.body).get('prompt_id')
            except (ValueError,TypeError,AttributeError): prompt_id=None
            RC.SERVER.queue_accepted(receipts,prompt_id)
            if prompt_id:
                from . import v28_project as PJ
                from . import v28_orchestrator as OR
                for receipt in receipts:
                    pid=receipt['reference_contract']['project_id']
                    if PJ.exists(pid) and (PJ.project_dir(pid)/OR.PENDING_NAME).is_file():
                        OR.confirm_submitted(pid,prompt_id=prompt_id)
        return response
    return admission

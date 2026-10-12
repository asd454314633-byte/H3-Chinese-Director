# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import pathlib,json,hashlib,subprocess,urllib.request,datetime
T=pathlib.Path(__file__).parent;R=T/'runtime';ID='<REDACTED_RUNTIME_ID>'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ev=read(R/'user/default/CN_STATIC_EVIDENCE.json');errors=[]
from PIL import Image
for case in ev['results']:
 for nodeid in case['closure']:
  n=ev['graphs'][case['name']][nodeid]
  if n['class_type'] in ['LoadImageCrop','LoadImage','LoadVideo']:
   name=n['inputs'].get('image',n['inputs'].get('file',''));p=R/'input'/name
   if not p.is_file():errors.append({'case':case['name'],'node':nodeid,'missing':name})
   elif n['class_type']!='LoadVideo':
    with Image.open(p) as image:image.verify()
assert not errors,errors
history=read(T/'evidence/ONE_REAL_HISTORY.json').get(ID)
failure=[m[1] for m in history['status']['messages'] if m[0]=='execution_error'] if history else []
write(T/'evidence/ONE_REAL_FAILURE.json',failure)
real='FAIL';output=None;probe=None;decode=None
if history and history['status']['status_str']=='success' and history['status']['completed']:
 out=history['outputs']['961'];videos=[v for key in ['images','videos'] for v in out.get(key,[]) if v['filename'].lower().endswith(('.mp4','.webm','.mov','.mkv'))];assert len(videos)==1
 v=videos[0];output=R/'output'/v['subfolder']/v['filename'];assert output.is_file()
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)],text=True,encoding='utf-8'))
 d=subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],capture_output=True,text=True)
 decode={'exit_code':d.returncode,'stderr':d.stderr};real='PASS' if d.returncode==0 else 'FAIL'
 write(T/'evidence/ONE_REAL_MEDIA.json',{'prompt_id':ID,'file':str(output),'sha256':sha(output),'ffprobe':probe,'full_decode':decode})
flags={'GUIDE_SWITCH':'PASS','POSE_SWITCH':'PASS','POSE_EMPTY_AUTO_OFF':'PASS','CLEAN_REBASE_SWITCH':'PASS','REQUIRED_INPUT_ERRORS':0,'POSE_OFF_UNION2_EXECUTION_CLOSURE':'NO','POSE_EMPTY_GET_VIDEO_COMPONENTS_EXECUTION':'NO','ONE_REAL_VIDEO_ACCEPTANCE':real,'FULL_SWITCH_UI_8207':'PASS' if real=='PASS' else 'HOLD','PRODUCTION_8197_CHANGED':'NO','READY_FOR_8197_PROMOTION':'NO','GENERATION_CORE_CHANGED':'NO','PREBAKE_CHANGED':'NO','CONTINUATION_CORE_CHANGED':'NO','NODE1058_CHANGED':'NO','COMFY_CORE_CHANGED':'NO'}
write(T/'evidence/FINAL_VERDICT.json',flags)
lines=['# 8207 中文开关与素材总控验收','', '左侧保留六段剧情导演台；右侧保留参考素材，新增关键画面三张图片、动作视频上传及三个中文开关。没有重做界面。','', '## 静态验收','', '真实 BrowserOS neo 页面通过原 app.graphToPrompt 检查 10 个状态，未提交 GPU 作业。覆盖关键画面关/1/2/3张/空图，动作关/有效视频/空视频，连续增强关/开。','', '所有状态必需字段和引用连接错误为 0；执行闭包内素材逐一检查存在，图片解码通过。LoadImageCrop 自带 VALIDATE_INPUTS，允许已有子目录图片路径，不使用其仅列根目录的下拉枚举作为错误判据。','', '关闭开关保留文件；空素材自动关闭并中文提示；错误路径、缺失视频、图片冒充视频均在提交前拦截；清空浏览器存储再重载图后状态一致。新增技术名词在普通开关区中不显示。','', '## 唯一真实视频','',f'本次仅一次提交：`{ID}`。关键画面=开，动作控制=开，连续增强=开；仅第1段，continuous=false，原执行器正常 Queue。PreBake 自动走原非连续 FALLBACK，不写共用缓存，不重复验证第4段 Clean Rebase。', '',f'视频验收：{real}。输出：{output or "尚无成功输出"}。', '', '## 冻结保护','', '生产基线逐文件 SHA256 无漂移。新副本既有源码仅六段前端的两个端口 guard 允许8207显示原面板；新增 WEB_DIRECTORY 注册与前端扩展。所有生成核心、PreBake、Continuation、Node1058、Comfy核心保持原字节。候选工作流只改分支mode、Guide旧UI所有权属性、中文UI标识和两面板位置，拓扑和子图完全一致。','', '候选默认关键画面/动作控制关闭，素材通过右侧上传；连续增强沿用原第4段策略。开关随工作流保存，重新加载从节点属性恢复。未保存的图修改仍按原Comfy工作流保存规则处理。','', '```ini']+[f'{k}={v}' for k,v in flags.items()]+['```','']
if failure:
 lines+=['## 真实失败与已完成的修复','', '唯一一次任务已通过 Queue 服务端校验；历史 executed 包含视频加载、GetVideoComponents、RT-DETR、SDPose、Union2加载与应用。随后在原 MiniMaxH3PDDAccApply 节点1006失败：隔离复制时遗漏了包内两个130048字节的basis safetensors。已从生产只读复制原文件到新副本，逐文件SHA256相同；没有修改PDD代码。未重跑，不能据文件补齐宣称真实验收成功。','', failure[0]['exception_message'],'', '参考素材误报也已处理：补齐隔离输入副本中原参考图/音频；前端仅在确认文件存在后恢复下拉选项，嵌套路径按filename/subfolder分开访问。新上传素材同时登记前端选择项。最终前端再次完成静态验收，生产未改。','']
(T/'UI_ACCEPTANCE_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
paths=[T/'candidate/V29_NEXTGEN_CHINESE_DIRECTOR_UI_8207_CANDIDATE.json',T/'frontend/chinese_director.js',R/'custom_nodes/H3_ChineseDirectorUI/__init__.py',R/'custom_nodes/H3_ChineseDirectorUI/js/chinese_director.js',R/'custom_nodes/H3_Prompt_Sidecar/web/h3_six_segment_director.js',T/'UI_GRAPH_MAPPING.json',T/'UI_PROTECTED_DIFF.json',T/'UI_RUNTIME_MANIFEST.json',T/'evidence/STATIC_G2P_ACCEPTANCE.json',T/'evidence/ONE_REAL_HISTORY.json',T/'UI_ACCEPTANCE_REPORT.md']
paths += [T/'evidence/PDD_DEPENDENCY_RESTORED.json',T/'evidence/FINAL_CANDIDATE_LOAD.json',R/'custom_nodes/ComfyUI-MiniMax-H3-PDD-Acc/adaln_basis/basis_ref2va.safetensors',R/'custom_nodes/ComfyUI-MiniMax-H3-PDD-Acc/adaln_basis/basis_fl2va.safetensors']
write(T/'UI_FREEZE_MANIFEST.json',{'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'port':8207,'production_promotion':False,'real_attempts':1,'prompt_id':ID,'flags':flags,'sha256':{str(p.relative_to(T)):sha(p) for p in paths}})
print(json.dumps(flags));print(str(output))

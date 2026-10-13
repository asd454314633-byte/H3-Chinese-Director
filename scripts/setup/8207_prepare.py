# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import pathlib,json,hashlib,shutil,datetime
T=pathlib.Path(__file__).parent
import sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from h3_8207_paths import (task_root as _h3_task_root, python_exe as _h3_python_exe,
                          production_workflow as _h3_production_workflow,
                          ui_freeze_json as _h3_ui_freeze_json)
P=_h3_task_root()
OLD=P
R=T/'runtime'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v): (T/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
T.mkdir(exist_ok=True)
for d in ['evidence','frontend','baseline','candidate','tests','logs']: (T/d).mkdir(exist_ok=True)
production={}
excluded={'.git','__pycache__','input','output','temp','user','models','logs','node_modules','.pytest_cache','venv'}
for s in P.rglob('*'):
 rel=s.relative_to(P)
 if rel.parts[0] in excluded or any(x in {'.git','__pycache__','node_modules'} for x in rel.parts) or not s.is_file() or s.suffix.lower() in {'.pyc','.log','.lock','.safetensors','.pt','.pth','.bin'}: continue
 # Code-only mirror; the same source assets used by the verified previous mirror.
 if not (OLD/rel).exists() and rel.parts[0] not in {'custom_nodes','comfy','comfy_extras','comfy_api','comfy_api_nodes','comfy_execution','comfy_config','api_server','app','blueprints','middleware','utils','alembic_db'}: continue
 production[str(rel)]=sha(s)
 dest=R/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(s,dest)
for d in ['input','output','temp','user/default/workflows','logs','models']: (R/d).mkdir(parents=True,exist_ok=True)
settings=P/'user/default/comfy.settings.json'
if settings.exists(): shutil.copy2(settings,R/'user/default/comfy.settings.json')
wf=_h3_production_workflow()
assert sha(wf).upper()=='AE0C4298109781985EAF59799D36705CA21DC03CC66405BF70EB172B75A240CA'
shutil.copy2(wf,T/'baseline/V29_PRODUCTION_READONLY.json')
production[str(wf)]=sha(wf)
write('baseline/PRODUCTION_HASHES.json',production)
freeze=_h3_ui_freeze_json()
f=json.loads(freeze.read_text(encoding='utf-8-sig'))
drift=[]
for n,h in f['runtime_source_hashes'].items():
 p=OLD/n
 if not p.exists() or sha(p)!=h: drift.append({'file':n,'expected':h,'actual':sha(p) if p.exists() else None})
write('baseline/OLD_8207_FREEZE_AUDIT.json',{'manifest':str(freeze),'drift':drift,'current_source_for_new_mirror':str(P),'historical_status_not_authoritative':True})
w=json.loads(wf.read_text(encoding='utf-8-sig'))
for n in w['nodes']:
 if n['id'] in [965,983,985,988,984,986,989,1059,1060,1061,1062,1063]: n['mode']=4
 if n['id']==965:
  n['widgets_values'][1]=json.dumps({'schema_version':1,'fps':24,'guides':[{'id':f'g{i+1}','enabled':False,'type':'image','time_seconds':t} for i,t in enumerate([0,2.5,5.5])]})
 if n['type']=='H3SixDirectorState':
  n['properties']['h3_chinese_ui']={'schema':1,'active_segment':0,'segments':[[{'image':'','seconds':t} for t in [0,2.5,5.5]] for _ in range(6)]}
w.setdefault('extra',{})['h3_chinese_director_ui']={'enabled':True,'version':1,'isolated_port':8207}
name='V29_NEXTGEN_CHINESE_DIRECTOR_UI_8207_CANDIDATE.json'
(T/'candidate'/name).write_text(json.dumps(w,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(T/'candidate'/name,R/'user/default/workflows'/name)
write('UI_RUNTIME_MANIFEST.json',{'task_root':str(T),'runtime_root':str(R),'port':8207,'production_workflow_sha256':sha(wf),'source_files':len(production),'models':'shared read-only references via unmodified extra_model_paths.yaml','input':str(R/'input'),'output':str(R/'output'),'temp':str(R/'temp'),'user':str(R/'user'),'database':'sqlite:///:memory:','core_modified':False,'started':False})
print(json.dumps({'mirror_files':len(production),'old_freeze_drift':len(drift),'candidate_sha256':sha(T/'candidate'/name)}))

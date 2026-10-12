# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import pathlib,json,hashlib,shutil,datetime,urllib.request
T=pathlib.Path(__file__).parent;R=T/'runtime';P=pathlib.Path(r'<REDACTED_LOCAL_PATH>/D')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
c=T/'candidate/V29_NEXTGEN_CHINESE_DIRECTOR_UI_8207_CANDIDATE.json';w=read(c)
for n in w['nodes']:
 if n['id']==992:n['pos']=[50,80]
 if n['id']==159:n['pos']=[1200,80]
write(c,w);shutil.copy2(c,R/'user/default/workflows'/c.name)
b=read(T/'baseline/PRODUCTION_HASHES.json');pd=[];rd=[]
for rel,h in b.items():
 p=pathlib.Path(rel) if pathlib.Path(rel).is_absolute() else P/rel
 if not p.exists() or sha(p)!=h:pd.append(rel)
 if pathlib.Path(rel).is_absolute() or pathlib.Path(rel).suffix.lower()=='.gguf':continue
 p=R/rel
 if not p.exists() or sha(p)!=h:rd.append(rel)
orig=read(T/'baseline/V29_PRODUCTION_READONLY.json');on={n['id']:n for n in orig['nodes']}
diff=[]
for n in w['nodes']:
 for k in set(n)|set(on[n['id']]):
  if n.get(k)!=on[n['id']].get(k):diff.append({'node':n['id'],'field':k,'before':on[n['id']].get(k),'after':n.get(k)})
assert w['links']==orig['links'] and w.get('definitions')==orig.get('definitions')
assert pd==[],pd
assert rd==[r'custom_nodes\H3_Prompt_Sidecar\web\h3_six_segment_director.js'],rd
write(T/'UI_PROTECTED_DIFF.json',{'production_drift':pd,'existing_runtime_changes':rd,'candidate_node_changes':diff,'candidate_extra_changes':{k:v for k,v in w['extra'].items() if orig['extra'].get(k)!=v},'topology_changed':False,'subgraphs_changed':False,'GENERATION_CORE_CHANGED':'NO','PREBAKE_CHANGED':'NO','CONTINUATION_CORE_CHANGED':'NO','NODE1058_CHANGED':'NO','COMFY_CORE_CHANGED':'NO','PRODUCTION_8197_CHANGED':'NO'})
ev=read(R/'user/default/CN_STATIC_EVIDENCE.json');shutil.copy2(R/'user/default/CN_STATIC_EVIDENCE.json',T/'evidence/STATIC_G2P_ACCEPTANCE.json')
assert len(ev['results'])==10 and all(not x['required_input_errors'] for x in ev['results'])
write(T/'UI_GRAPH_MAPPING.json',{'scope':'8207 only; existing node modes/widgets; original serializer and executor','guide':{'switch':'关键画面','timeline':965,'image_slots':[983,985,988],'guard_slots':[984,986,989],'off':'all mode=4; files retained','empty':'auto off with Chinese notice','ownership':'legacy h3_guide_branch tags removed in candidate only'},'pose':{'switch':'动作控制','branch':[1059,1060,1061,1062,1063],'video':1061,'off_or_empty':'all mode=4; no Union2/GetVideoComponents execution closure'},'rebase':{'switch':'连续增强','subgraph':1056,'classes':['H3ContinuationPrepare','H3ContinuationTrimOnce'],'widget':'clean_rebase_enabled','fixed_segment':3},'surface':{'left':992,'right':159,'new_uploads_right':4,'new_uploads_left':0}})
m=read(T/'UI_RUNTIME_MANIFEST.json');m.update(started=True,visible_console=True,listener_pid=m.get('listener_pid'),console_launcher_pid=m.get('console_launcher_pid'),prebake_cache_interface_changed=False,single_acceptance_continuous=False);write(T/'UI_RUNTIME_MANIFEST.json',m)  # PID 取自本机运行时收据，公开版不落任何机器专属进程号
print(json.dumps({'production_changes':pd,'runtime_changes':rd,'candidate_fields':len(diff),'static_cases':len(ev['results'])}))

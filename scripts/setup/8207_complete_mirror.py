# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
import pathlib,json,hashlib,shutil
T=pathlib.Path(__file__).parent;P=pathlib.Path(r'<REDACTED_LOCAL_PATH>/D');R=T/'runtime'
allowed={'custom_nodes','comfy','comfy_extras','comfy_api','comfy_api_nodes','comfy_execution','comfy_config','api_server','app','blueprints','middleware','utils','alembic_db','director_runtime'}
baseline=json.loads((T/'baseline/PRODUCTION_HASHES.json').read_text(encoding='utf-8'))
added=[]
for s in P.rglob('*'):
 rel=s.relative_to(P)
 if rel.parts[0] not in allowed or not s.is_file() or any(x in {'.git','__pycache__','node_modules'} for x in rel.parts) or s.suffix.lower() in {'.pyc','.log','.lock','.safetensors','.pt','.pth','.bin'}:continue
 dest=R/rel
 if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,dest);added.append(str(rel))
 if str(rel) not in baseline:baseline[str(rel)]=hashlib.sha256(s.read_bytes()).hexdigest()
(T/'baseline/PRODUCTION_HASHES.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'filled':len(added),'files':added[:20]}))

# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""The sole owner of reference decisions, numbering and server admission.

Source slots belong to the user. Only this module turns them into active labels.
Signed canonical graphs are verified, never interpreted a second time.
"""
import copy
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
from pathlib import Path
from . import v28_paths as P

TOKEN = re.compile(r'<\s*Picture\s+(\d+)\s*>|(?:图片|图|槽位|slot|picture)\s*(\d+)|第\s*(\d+)\s*张(?:\s*图)?', re.I)
PICTURE = re.compile(r'<\s*Picture\s+(\d+)\s*>', re.I)
SOCKET = re.compile(r'ref_images\.ref_image_(\d+)$')
AUX_SOCKET = re.compile(r'(?:ref_audios\.ref_audio_|ref_videos\.ref_video_|ref_video_audios\.ref_video_audio_)\d+$')
NEGATIVE = re.compile(r'不要(?:使用|用|参与)|不要(?=(?:图|图片|槽位|<))|不得使用|排除|不用|忽略|不要参与|仅作为反例|不是(?:身份)?参考|不(?:是|作为).{0,8}参考|do\s+not\s+use|not\s+a\s+reference|ignore|exclude', re.I)
POSITIVE = re.compile(r'作为|参考|身份|服装|场景|风格|人物|首帧|尾帧|姿势|姿态|身体|动作|定义|画面|构图|背景|仅|只用|使用|保留|identity|costume|clothing|scene|style|reference|keyframe|frame|subject|\bis\b|\bin\b|\bfrom\b|\bonly\b|\buse\b', re.I)
CLAUSE = re.compile(r'[;；。\n,，]+|\bbut\b|但是|但(?=不要|排除)', re.I)


def digest(value):
    # JSON numbers have one value domain across Python and the browser. In
    # particular 10.0 -> JSON.parse -> JSON.stringify -> 10 is identical.
    def normalize(item):
        if isinstance(item,float) and item.is_integer(): return int(item)
        if isinstance(item,dict): return {k:normalize(v) for k,v in item.items()}
        if isinstance(item,(list,tuple)): return [normalize(v) for v in item]
        return item
    data = value if isinstance(value, bytes) else json.dumps(normalize(value), ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def fail(code, message):
    raise ValueError(f'{code}: {message}')


def decisions(text, source_slots, *, inherited=None):
    """Finite explicit grammar. Unclear or contradictory roles fail closed."""
    slots = {int(x) for x in source_slots}
    no_refs = bool(re.search(r'无图片|无参考|不使用任何参考|不使用参考图|\bnone\b|no\s+(?:image\s+)?references?',str(text),re.I))
    observations = {s: ({'EXCLUDE'} if no_refs else set()) for s in slots}
    roles = {s: [] for s in slots}
    previous_mentions=[]
    for clause in CLAUSE.split(str(text or '')):
        mentions = sorted({int(next(x for x in m.groups() if x is not None)) for m in TOKEN.finditer(clause)})
        if not mentions:
            if previous_mentions and re.match(r'\s*(?:同时|不作为首帧|不做首帧|作为|仅参考|只参考)',clause):
                for slot in previous_mentions:roles[slot][-1]+='，'+clause.strip()
            continue
        previous_mentions=mentions
        if set(mentions) - slots:
            fail('REFERENCE_SLOT_MISSING', f'未连接的源槽：{sorted(set(mentions)-slots)}')
        negative = bool(NEGATIVE.search(clause))
        # A negation of usage is authoritative within its own clause. Separate
        # positive clauses still produce a conflict instead of overriding it.
        state = 'EXCLUDE' if negative else ('INCLUDE' if POSITIVE.search(clause) else 'AMBIGUOUS')
        for slot in mentions:
            observations[slot].add(state)
            roles[slot].append(clause.strip())
    result = []
    for slot in sorted(slots):
        states = observations[slot]
        state = next(iter(states)) if len(states) == 1 else ('AMBIGUOUS' if states else 'UNMENTIONED')
        if state == 'AMBIGUOUS':
            fail('REFERENCE_ROLE_CONFLICT', f'图{slot}职责冲突或不明确，请明确使用或排除')
        result.append({'source_slot_id': slot, 'decision': state, 'role_text': '\n'.join(roles[slot])})
    if inherited is not None:
        only = bool(re.search(r'仅(?:使用|用)?|只(?:使用|用)|\bonly\b', text, re.I))
        current = {r['source_slot_id']: r for r in result}
        for old in inherited:
            row = current[old['source_slot_id']]
            if row['decision'] == 'UNMENTIONED' and not only and not no_refs and not TOKEN.search(text):
                row.update(copy.deepcopy(old))
    return result


def active_map(rows):
    return [{'ui_slot': r['source_slot_id'], 'h3_picture': i}
            for i, r in enumerate((x for x in rows if x['decision'] == 'INCLUDE'), 1)]


def source_notation(text, source_map):
    slots = {int(r['ui_slot']) for r in source_map}
    def sub(m):
        slot = int(next(x for x in m.groups() if x is not None))
        if slot not in slots: fail('REFERENCE_SLOT_MISSING', f'未连接图{slot}')
        return f'<Picture {slot}>'
    return TOKEN.sub(sub,str(text))


def director_sections(role_input, source_map):
    rows = decisions(role_input,[x['ui_slot'] for x in source_map])
    definitions,retention = [],[]
    for row in rows:
        if row['decision'] != 'INCLUDE': continue
        slot = row['source_slot_id']
        role = source_notation(row['role_text'],source_map)
        definitions.append(f'<Subject {slot}> is the user-defined reference content from <Picture {slot}>. Explicit role: {role}.')
        retention.append(f'<Subject {slot}>: fully_preserved - preserve exactly the explicitly defined reference role.')
    return '\n'.join(definitions) or 'N/A', '\n'.join(retention) or 'N/A', rows


def source_labels(text, mapping):
    """Explicit active-domain edit back to the immutable source domain."""
    by_label = {int(r['h3_picture']): int(r['ui_slot']) for r in mapping}
    def sub(m):
        if int(m[1]) not in by_label:
            fail('REFERENCE_LABEL_MISSING', f'Picture {m[1]}不在当前合同')
        return m[0][:m.start(1)-m.start()] + str(by_label[int(m[1])]) + m[0][m.end(1)-m.start():]
    return PICTURE.sub(sub, text)


def render_reference_tokens(text, rows):
    """Change reference notation only, never replace actions or dialogue."""
    mapping = {r['ui_slot']: r['h3_picture'] for r in active_map(rows)}
    excluded = {r['source_slot_id'] for r in rows if r['decision'] != 'INCLUDE'}
    def sub(m):
        slot = int(m[1])
        if slot in excluded:
            return f'source slot {slot}'  # excluded source is not an H3 Picture label
        if slot not in mapping:
            fail('REFERENCE_LABEL_MISSING', f'Picture {slot}没有明确正向职责')
        return m[0][:m.start(1)-m.start()] + str(mapping[slot]) + m[0][m.end(1)-m.start():]
    return PICTURE.sub(sub, text)


def segment_prompt(text, rows, *, inherited=False):
    """The contract renders the reference sections and labels as one operation."""
    from . import v28_h3_format as F
    sections = F.parse_sections(text)
    if inherited:
        kept = {r['source_slot_id'] for r in rows if r['decision'] == 'INCLUDE'}
        lines = []
        for line in sections['subject_definitions'].splitlines():
            referenced = {int(m[1]) for m in PICTURE.finditer(line)}
            if referenced and not referenced & kept:
                subjects = re.findall(r'<Subject\s+\d+>', line)
                if subjects:
                    lines.extend(f'{s} is the established subject from the preceding segment, without a new image reference.' for s in subjects)
                continue
            lines.append(line)
        covered = {int(m[1]) for line in lines for m in PICTURE.finditer(line)}
        for slot in sorted(kept - covered):
            lines.append(f'<Subject {100+slot}> is the visible reference content explicitly selected from <Picture {slot}> for this segment.')
            sections['retention_analysis'] += f'\n<Subject {100+slot}>: fully_preserved - the explicitly selected reference role.'
        sections['subject_definitions'] = '\n'.join(lines) or 'N/A'
        sections['retention_analysis'] = '\n'.join(line for line in sections['retention_analysis'].splitlines()
            if not PICTURE.search(line) or any(int(m[1]) in kept for m in PICTURE.finditer(line))) or 'N/A'
        text = F.render(sections)
    return render_reference_tokens(text, rows)


def draft(text, source_map, *, mode='MANUAL_FULL', segment_id=1, duration=10, role_input=None, previous=None):
    slots = [int(x['ui_slot']) for x in source_map]
    if role_input is not None:
        exclusions = '\n'.join(clause for clause in CLAUSE.split(text) if NEGATIVE.search(clause) and TOKEN.search(clause))
        role_input = str(role_input) + '\n' + exclusions
    rows = decisions(text if role_input is None else role_input, slots, inherited=previous)
    canonical = segment_prompt(text, rows, inherited=previous is not None)
    mapping = active_map(rows)
    return {'schema_version': 2, 'segment_id': int(segment_id), 'generation_mode': mode,
            'duration_seconds': float(duration), 'reference_decisions': rows,
            'active_reference_index': mapping, 'prompt_picture_label': mapping,
            'canonical_prompt': canonical, 'canonical_prompt_sha256': digest(canonical.encode()),
            'source_references': [{'source_slot_id': int(r['ui_slot'])} for r in source_map]}


def locate_text(graph, condition):
    node_id, field, visited = str(condition), 'prompt', set()
    while node_id not in visited:
        visited.add(node_id)
        node = graph.get(node_id, {})
        value = node.get('inputs', {}).get(field)
        if isinstance(value, str):
            return node_id, field, value
        if not isinstance(value, list) or len(value) != 2:
            fail('REFERENCE_PROMPT_SOURCE', '无法确定Prompt来源')
        node_id = str(value[0])
        kind = graph.get(node_id, {}).get('class_type')
        fields = {'H3VideoPromptRole': 'base_prompt', 'H3Audio8ReferencePreflight': 'prompt',
                  'PrimitiveString': 'value', 'PrimitiveStringMultiline': 'value'}
        if kind not in fields:
            fail('REFERENCE_PROMPT_SOURCE', f'不支持的Prompt来源：{kind}')
        field = fields[kind]
    fail('REFERENCE_PROMPT_SOURCE', 'Prompt来源循环')


def asset_path(filename):
    # ComfyUI annotated input paths; neither a client path nor traversal is trusted.
    name = str(filename)
    suffix = re.search(r' \[(input|output|temp)\]$', name)
    folder = suffix[1] if suffix else 'input'
    if suffix: name = name[:suffix.start()]
    root = (P.COMFY_ROOT / folder).resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        fail('REFERENCE_ASSET_MISSING', f'素材不存在或路径不合法：{name}')
    return path


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()


def source_snapshot(graph, rows):
    result = []
    for row in rows:
        node_id = str(row['source_node_id'])
        visited, nodes, files = set(), {}, []
        def visit(nid):
            if nid in visited: return
            visited.add(nid)
            node = graph.get(nid)
            if not node: fail('H3_REFERENCE_RECEIPT_INVALID', f'来源节点{nid}已改变')
            nodes[nid] = {'class_type': node['class_type'], 'inputs': node.get('inputs', {})}
            for key, value in node.get('inputs', {}).items():
                if isinstance(value, list) and len(value) == 2 and str(value[0]) in graph:
                    visit(str(value[0]))
                elif key in ('image', 'audio', 'video', 'file', 'filename') and isinstance(value, str) and value:
                    path = asset_path(value)
                    files.append({'asset_identity': str(path), 'asset_sha256': file_hash(path)})
        visit(node_id)
        if len(files) != 1:
            fail('REFERENCE_ASSET_AMBIGUOUS', f'源槽{row["source_slot_id"]}必须唯一对应一个真实图片文件')
        result.append(dict(row, **files[0], source_execution_digest=digest(nodes)))
    return result


def reference_edges(inputs):
    return {k: inputs[k] for k in sorted(inputs) if SOCKET.fullmatch(k) or AUX_SOCKET.fullmatch(k) or k in ('ref_audio', 'ref_video')}


def runtime_clock(graph):
    ids=(str(P.NODE['duration_sec']),str(P.NODE['frames_expr']))
    return {nid:{'class_type':graph[nid]['class_type'],'inputs':graph[nid].get('inputs',{})} for nid in ids if nid in graph}


class ReferenceContractV2:
    def __init__(self):
        self._secret = secrets.token_bytes(32)
        self._owners = {}
        self._accepted = {}
        self._lock = threading.RLock()

    def _key(self, context):
        return (str(P.PROJECTS_ROOT), context['project_id'], context['workflow_id'])

    def _project_state(self, context):
        from . import v28_project as PJ
        pid = context['project_id']
        if not PJ.exists(pid): return None, None
        segments = PJ.read(pid, 'RESOLVED_SEGMENTS.json', default=[]) or []
        sid = int(context['segment_id'])
        if not 1 <= sid <= len(segments): fail('H3_REFERENCE_RECEIPT_INVALID', '段号不在当前项目')
        state = {'segments': segments, 'source': PJ.read(pid, 'PROMPT_SOURCE.json', default={}),
                 'manual': PJ.read(pid, 'MANUAL_PROMPTS.json', default={})}
        return segments[sid-1], digest(state)

    def compile_graph(self, graph, context):
        from . import v28_h3_format as F
        context = copy.deepcopy(context)
        context['edit_revision'] = context.get('edit_revision', context.get('workflow_revision'))
        for key in ('project_id', 'workflow_id', 'segment_id', 'generation_mode', 'workflow_revision'):
            if key not in context: fail('REFERENCE_CONTEXT_REQUIRED', f'缺少{key}')
        out, receipts, updates = copy.deepcopy(graph), [], []
        segment, project_digest = self._project_state(context)
        original_texts = {}
        clock=runtime_clock(out)
        seconds=clock.get(str(P.NODE["duration_sec"]),{}).get("inputs",{}).get("value")
        for nid, node in out.items():
            if node.get('class_type') != 'MiniMaxH3ReferenceToVideo': continue
            source, field, text = locate_text(out, nid)
            text = original_texts.setdefault((source,field),text)
            keys = sorted((k for k in node['inputs'] if SOCKET.fullmatch(k)), key=lambda k: int(SOCKET.fullmatch(k)[1]))
            slots = [int(SOCKET.fullmatch(k)[1])+1 for k in keys]
            if segment:
                contract = copy.deepcopy(segment.get('reference_contract'))
                if not contract: fail('REFERENCE_RECOMPILE_REQUIRED', '历史项目请重新编译，不能信任旧客户端memo')
                if contract['canonical_prompt'] != text or contract['generation_mode'] != context['generation_mode']:
                    fail('H3_REFERENCE_RECEIPT_INVALID', '当前Prompt或模式不等于已编译预览')
                expected = [r['source_slot_id'] for r in contract['source_references']]
                if slots != expected: fail('H3_REFERENCE_RECEIPT_INVALID', '连接源槽已改变，请重新规划预览')
            else:
                # Compare physical interpretations, not whether a graph is
                # sparse. Dense/source domains may coincide or be uniquely
                # distinguishable; competing physical selections fail closed.
                mapping=[{'ui_slot':slot,'h3_picture':i} for i,slot in enumerate(slots,1)]
                candidates={}
                for source_text in (text, source_labels(text,mapping) if all(int(m[1])<=len(slots) for m in PICTURE.finditer(text)) else None):
                    if source_text is None: continue
                    try:
                        candidate=draft(source_text,mapping,mode=context['generation_mode'],
                            segment_id=context['segment_id'],duration=context.get('duration_seconds',seconds if seconds is not None else 10))
                    except ValueError: continue
                    key=digest({'canonical':candidate['canonical_prompt'],'active':candidate['active_reference_index']})
                    candidates[key]=candidate
                if len(candidates)!=1:
                    fail('LEGACY_REFERENCE_AMBIGUOUS','旧图缺可信source域且有零种或多种物理解释，请明确源槽后重新编译')
                contract=next(iter(candidates.values()))
            raw_sources = [{'source_slot_id': s, 'source_node_id': str(node['inputs'][k][0]),
                            'source_output_index': node['inputs'][k][1], 'source_socket': k} for s,k in zip(slots,keys)]
            sources = source_snapshot(out, raw_sources)
            auxiliary_rows = [{'source_slot_id':name,'source_node_id':str(node['inputs'][name][0]),'source_output_index':node['inputs'][name][1],'source_socket':name} for name in sorted(node['inputs']) if AUX_SOCKET.fullmatch(name) or name in ('ref_audio','ref_video')]
            auxiliary_sources = source_snapshot(out, auxiliary_rows)
            if seconds is not None and float(seconds)!=contract['duration_seconds']:
                fail('H3_REFERENCE_RECEIPT_INVALID','实际时长与段落合同不一致，请重新编译')
            contract.update(context, runtime_clock=clock, source_references=sources, auxiliary_sources=auxiliary_sources, condition_node=str(nid), prompt_source_node=source,
                            prompt_source_field=field, project_state_digest=project_digest,
                            canonicalized=True, reference_contract_version=2)
            contract['source_to_active'] = {str(r['ui_slot']):r['h3_picture'] for r in contract['active_reference_index']}
            active = {r['ui_slot'] for r in contract['active_reference_index']}
            edges = [node['inputs'][r['source_socket']] for r in sources if r['source_slot_id'] in active]
            for k in keys: del node['inputs'][k]
            for i, edge in enumerate(edges): node['inputs'][f'ref_images.ref_image_{i}'] = edge
            out[source]['inputs'][field] = contract['canonical_prompt']
            contract['graph_reference_edges'] = reference_edges(node['inputs'])
            contract['graph_reference_edges_digest'] = digest(contract['graph_reference_edges'])
            contract['media_labels'] = {kind: sorted({1 if name in ('ref_audio','ref_video') else int(name.rsplit('_',1)[1])+1 for name in node['inputs'] if name==flat or name.startswith(prefixes)}) for kind,flat,prefixes in (('Audio','ref_audio',('ref_audios.ref_audio_','ref_video_audios.ref_video_audio_')),('Video','ref_video',('ref_videos.ref_video_',)))}
            contract['canonical_prompt_sha256'] = digest(contract['canonical_prompt'].encode())
            problems = F.audit_prompt(contract['canonical_prompt'], reference_contract=contract,
                duration_seconds=contract['duration_seconds'], segment_id=contract['segment_id'], generation_mode=contract['generation_mode'])
            if problems: fail('OFFICIAL_H3_FORMAT_INVALID', '; '.join(problems))
            # One owner revision covers the complete semantic batch, source
            # execution and UI edit epoch, independent of the selected segment.
            identity = {'project':project_digest,'sources':sources,'auxiliary_sources':auxiliary_sources,'clock':clock,'workflow_revision':context['workflow_revision'],
                        'mode':context['generation_mode'], 'edit_epoch':context.get('edit_epoch')}
            if not project_digest: identity['canonical'] = contract['canonical_prompt']
            with self._lock:
                key = self._key(context)
                owner = self._owners.setdefault(key, {'revision':0,'identity':None,'receipts':{}})
                if owner['identity'] != digest(identity):
                    owner.update(revision=owner['revision']+1, identity=digest(identity), receipts={})
                contract['compile_revision'] = owner['revision']
                contract_digest = digest(contract)
                receipt = owner['receipts'].get(contract_digest)
                if receipt is None or receipt['expires_at'] <= time.time():
                    payload = {'schema_version':2,'reference_contract':contract,'contract_digest':contract_digest,
                               'issued_at':time.time(), 'expires_at':time.time()+900}
                    receipt = dict(payload, signature=hmac.new(self._secret, digest(payload).encode(), hashlib.sha256).hexdigest())
                    owner['receipts'][contract_digest] = receipt
            node.setdefault('_meta', {})['h3_reference_receipt_v2'] = copy.deepcopy(receipt)
            receipts.append(receipt)
            updates.append({'source_node':source,'field':field,'canonical_prompt':contract['canonical_prompt'], 'receipt':receipt})
        return {'graph':out,'receipts':receipts,'source_updates':updates}

    def verify_graph(self, graph, context=None, *, raw=False):
        out = copy.deepcopy(graph)
        for nid,node in out.items():
            if node.get('class_type') != 'MiniMaxH3ReferenceToVideo': continue
            receipt = node.get('_meta', {}).get('h3_reference_receipt_v2')
            if not isinstance(receipt, dict): fail('H3_REFERENCE_RECEIPT_INVALID', '缺少服务端V2签名，请重新预览')
            payload = {k:receipt[k] for k in ('schema_version','reference_contract','contract_digest','issued_at','expires_at') if k in receipt}
            signature = hmac.new(self._secret, digest(payload).encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, str(receipt.get('signature',''))):
                fail('H3_REFERENCE_RECEIPT_INVALID', '签名不合法或服务已经重启，请重新预览')
            if receipt.get('expires_at', 0) <= time.time():
                fail('H3_REFERENCE_RECEIPT_INVALID', '签名已过期，请再次点击连续生成')
            c = receipt['reference_contract']
            if digest(c) != receipt['contract_digest'] or c['condition_node'] != str(nid):
                fail('H3_REFERENCE_RECEIPT_INVALID', '合同摘要或N136身份不一致')
            with self._lock:
                owner = self._owners.get(self._key(c))
                if not owner or owner['revision'] != c['compile_revision']:
                    fail('H3_REFERENCE_RECEIPT_INVALID', '旧编译revision已失效')
            if runtime_clock(out) != c.get('runtime_clock',{}):
                fail('H3_REFERENCE_RECEIPT_INVALID','实际时长或帧数派生链已改变')
            _, current_project = self._project_state(c)
            if current_project != c['project_state_digest']:
                fail('H3_REFERENCE_RECEIPT_INVALID', '项目草稿已改变，请重新编译')
            if context is not None and any(context.get(k) != c.get(k) for k in
                    ('project_id','workflow_id','segment_id','generation_mode','workflow_revision','edit_epoch')):
                fail('H3_REFERENCE_RECEIPT_INVALID', 'workflow/模式/段号/编辑版本已改变')
            source,field,text = locate_text(out,nid)
            if source != c['prompt_source_node'] or field != c['prompt_source_field'] or text != c['canonical_prompt']:
                fail('H3_REFERENCE_RECEIPT_INVALID', '最终Prompt或来源已改变')
            if source_snapshot(out, [{k:r[k] for k in ('source_slot_id','source_node_id','source_output_index','source_socket')} for r in c['source_references']]) != c['source_references']:
                fail('H3_REFERENCE_RECEIPT_INVALID', '素材内容或来源执行链已改变')
            auxiliary_rows=[{k:r[k] for k in ('source_slot_id','source_node_id','source_output_index','source_socket')} for r in c.get('auxiliary_sources',[])]
            if source_snapshot(out,auxiliary_rows) != c.get('auxiliary_sources',[]):
                fail('H3_REFERENCE_RECEIPT_INVALID','音视频素材内容或来源已改变')
            if {k:v for k,v in reference_edges(node['inputs']).items() if not SOCKET.fullmatch(k)} != {k:v for k,v in c['graph_reference_edges'].items() if not SOCKET.fullmatch(k)}:
                fail('H3_REFERENCE_RECEIPT_INVALID','音视频引用边已改变')
            if raw:
                expected = {r['source_socket']:[r['source_node_id'],r['source_output_index']] for r in c['source_references']}
                actual = {k:v for k,v in node['inputs'].items() if SOCKET.fullmatch(k)}
                if actual != expected: fail('H3_REFERENCE_RECEIPT_INVALID', '源槽连线已改变')
                for k in actual: del node['inputs'][k]
                node['inputs'].update(c['graph_reference_edges'])
            if reference_edges(node['inputs']) != c['graph_reference_edges'] or digest(reference_edges(node['inputs'])) != c['graph_reference_edges_digest']:
                fail('H3_REFERENCE_RECEIPT_INVALID', 'N136最终引用边已改变')
        return out

    def queue_accepted(self, receipts, prompt_id):
        if not prompt_id: return
        with self._lock:
            for receipt in receipts:
                c = receipt['reference_contract']
                self._accepted[(c['project_id'],str(prompt_id))] = copy.deepcopy(c)

    def accepted(self, project_id, prompt_id):
        with self._lock:
            return self._accepted.get((project_id,str(prompt_id)))


SERVER = ReferenceContractV2()

# SANITIZED_PUBLIC_COPY — 本文件由私有原件经内容级脱敏生成：已移除个人素材/媒体、个人创作提示词、本机绝对路径、身份与凭据、运行状态；历史结论、日期、耗时与验收结果未作任何篡改。
"""Exercise workflow sockets against the installed rgthree switch implementation."""
import ast
import json
import unittest
from pathlib import Path

class NativeSwitchContract(unittest.TestCase):
    def test_native_values_reach_switch_outputs(self):
        src = Path(__file__).parents[2] / 'rgthree-comfy/py/any_switch.py'
        tree = ast.parse(src.read_text(encoding='utf-8'))
        cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'RgthreeAnySwitch')
        method = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == 'switch')
        scope = {'is_none': lambda value: value is None}
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(src), 'exec'), scope)
        path = Path('<REDACTED_LOCAL_PATH>/D')
        workflow = json.loads(path.read_text(encoding='utf-8'))
        nodes = {n['id']: n for n in workflow['nodes']}
        for node_id in (930, 885, 870):
            with self.subTest(node=node_id):
                socket = next(i for i in nodes[node_id]['inputs'] if i.get('label') == 'Native20 诊断')
                value = object()
                self.assertIs(scope['switch'](None, **{socket['name']: value})[0], value)

if __name__ == '__main__':
    unittest.main()

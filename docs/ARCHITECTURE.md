# 架构说明（ARCHITECTURE）

## 0. 一句话

**一层中文语义控制层 + 一层执行层 + 一层生命周期治理层**，跑在 ComfyUI 引擎之上。

```
┌──────────────────────────────────────────────────────────────┐
│ 用户只接触这一层                                                │
│   N159 H3OperationSelector 「H3 全中文傻瓜导演台」                │
│   + 六段剧情面板（H3SixDirectorState / six_prompt_state）        │
│   + 中文开关层（extra.h3_chinese_switches）                     │
└───────────────┬──────────────────────────────────────────────┘
                │ 中文语义 → 原生枚举
┌───────────────▼──────────────────────────────────────────────┐
│ 选择器矩阵（本地作者原创编排）                                   │
│  Generation / Image / Ref2va-Backend / Ref2va-Attention /      │
│  Speed / Fl2v-Route / Size / Guide-Mode / Memory-Opt / OP      │
└───────────────┬──────────────────────────────────────────────┘
                │ 原生枚举
┌───────────────▼──────────────────────────────────────────────┐
│ 执行层（ComfyUI Core + 第三方节点）                             │
│  MiniMaxH3ImageToVideo / MiniMaxH3ReferenceToVideo /           │
│  SamplerCustomAdvanced / LTXV*AVLatent / VAE / CreateVideo /   │
│  MiniMaxH3PDDAccApply / Ref2VAVSAGatePatch / BlockSparse...    │
└───────────────┬──────────────────────────────────────────────┘
                │ 钩子 / 生命周期
┌───────────────▼──────────────────────────────────────────────┐
│ 生命周期治理层（本地作者自研）                                   │
│  h3_adaptive_host_warm_inplace   Adaptive pre-TE release       │
│  h3_selective_te_unload          TE 选择性卸载                  │
│  h3_selective_diffusion_unload   diffusion 选择性卸载           │
│  h3_partial_diffusion_evict      VAE 前部分驱逐                 │
│  h3_conditioning_prebake         六段 conditioning 缓存         │
└──────────────────────────────────────────────────────────────┘
```

## 1. 三条数据通路

| 通路 | 输入 | 关键节点 | 说明 |
|---|---|---|---|
| 文生 / 单图 / 首尾帧（FL2V） | 图片 + 文字 | `MiniMaxH3ImageToVideo`、`H3Fl2vRouteSelector` | 走 FL2V 路线与对应 LoRA |
| 参考视频（Ref2VA / V2V / RV2V） | 参考图/视频/音频 | `MiniMaxH3ReferenceToVideo`、`H3V2VInit`、`H3WindowLoop` | 仅开参考视频=V2V；参考视频+图片/音频=RV2V |
| 接续生产 | 上一段 latent | `LTXVSeparateAVLatent` → `LTXVConcatAVLatent`（子图 `New Subgraph连续-封装`） | 跨段一致性来源 |

## 2. 六段导演台状态机

```
six_prompt_state = {
  texts: [6],            // 六段中文剧情（公开版为空串占位）
  goal, settings,        // 全局目标与设定（公开版为空串）
  model,                 // 编译风格档位（dark_roast 等）
  execution: { continuous, start_index, start_mode, project_id },
  video_refs: [6]        // 每段参考素材槽（公开版为 null）
}
```

- `continuous=false` 为安全默认；显式批量按钮会临时开启连续。
- `start_mode="resume"` 支持从中断段继续。
- 六段全部 SUCCESS 后触发自动合并。

## 3. Conditioning PreBake

- 缓存键：`story_id + 段号 + 文字修订号 + 参考槽 SHA + H3/TE/VAE 身份`
- 命中：复用 H3 host warm（约 19.525 GiB 量级，实测可更低），hook 不执行。
- 未命中：`Node136` 入口先精确释放 H3 host warm → 加载 TE → encode → 卸载 TE → sampling 后 partial evict 并保留 H3 host warm。
- 失效：改段文字 → 该段及**后续**所有旧视频回执失效；旧 group/prompt/latent 回执被拒绝。
- 未知/动态 ancestry → 自动 fallback 到常规路径。

## 4. 内存生命周期（治理层）

三条真实路径：

1. **cache 命中**：复用 host warm，hook 不执行。
2. **cache 未命中**：释放 host warm → 加载 TE → encode → 卸载 TE → 采样 → partial evict → 保留 host warm。
3. **冷启动**：完整装载路径（首次 H3 加载约 20.9 GB 字节量级）。

边界（**不美化**）：热路径 Commit 峰值约 90.2%，`MEMORY_MARGIN = LIMITED`；本仓库不宣称内存无忧，也不建议继续叠加常驻内存优化而不做验收。

## 5. 前端

- 入口：`custom_nodes/local_author/8197_production_line/H3_ChineseDirectorUI/js/chinese_director.js`
- 六段面板：`custom_nodes/local_author/8197_production_line/H3_Prompt_Sidecar/web/h3_six_segment_director.js`、`h3_six_execute.js`、`h3_six_width_contract.js`
- 合并面板：`H3_Prompt_Sidecar/web/h3_native_merge.js`
- 关键帧时间线：`H3_NextgenDirector/js/h3_guide_timeline.js`（8197 生产未启用该路线；8207 线候选不在公开包内）
- GUIDE 权威归一：总控台 `setSwitch` 与 `H3GuideModeSelector` 同源，helper sync 无法再把 GUIDE OFF 翻回。
- 版本锁定：`COMFYUI_FRONTEND_VERSION_LOCK = 1.52.7`。

## 6. 公开范围：只有 8197 冻结生产线

本仓库**只发布 8197 冻结生产线**（工作流 + `custom_nodes/local_author/8197_production_line/` 源码）。
8207 是独立运行/实验线，**不包含在本 8197 正式包内**；2026-10-14 起已另设 [8207 公开实验仓库](https://github.com/asd454314633-byte/H3-8207-Experimental) 发布脱敏源码预览。两仓的发布版本、依赖和验收结论均独立，历史本机工程档案仍未公开。
下表仅登记本仓库历史工程分工及 8197 验收边界，**不得直接套用到 8207 公开预览版**：

| | 8197 线（本仓正式包） | 8207 线（独立实验预览，不在本包） |
|---|---|---|
| 定位 | 冻结生产 | 独立运行 / 实验 |
| 目录 | `custom_nodes/local_author/8197_production_line/` | 不在公开包内（作者本机 `8207_line`） |
| 前端 | 含 GUIDE 权威补丁 | 冻结件**不含**该补丁，已停止使用 |
| 验收 | 六段真实生成 + 自动合并 PASS | **未做同等 GPU 验收**，不得引用 8197 结论 |

## 7. 目录与职责映射

| 目录 | 职责 |
|---|---|
| `workflows/current/` | **唯一公开工作流**：`V29_chinese_director_production_8197.json`（8197 生产基线） |
| `custom_nodes/local_author/` | 本地作者自研节点（Python + web JS，含前端控制层；公开包内仅 8197 冻结生产线） |
| `scripts/setup\|verify\|sanitize/` | 安装、验证、脱敏 |
| `config/examples/` | 模型路径映射与 UI 冻结清单模板（运行回执字段已占位符化） |
| `benchmarks/` | 真实测试耗时表（证据列以 `LOCAL_ARCHIVE:` 指向生产侧本机归档） |
| `manifests/nodes.csv` | 自研/第三方节点归属与许可台账 |
| `tests/`、`fixtures/synthetic/` | 不含私有素材的结构性测试与非工作流夹具 |

**公开包内不存在**：`workflows/history/`（历代工作流）、`history/`（历史报告/变更台账/决策记录）、
`manifests/public_files.csv`、`manifests/exclusions.csv`、`manifests/exclusions_summary.csv`、
`custom_nodes/local_author/8207_line/`（8207 实验线镜像源码）、
可导入的第二套工作流（含合成工作流夹具）。这些都留在作者本机生产归档中，不进入公共发布。

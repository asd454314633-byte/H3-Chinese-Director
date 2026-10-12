# 模型清单（MODELS.md）

> **本仓库不包含任何模型权重。** 不含 `.safetensors` / `.ckpt` / `.pt` / `.pth` / `.gguf` / 分片 / 模型缓存，也不使用 Git LFS 绕过该原则。
> 请按下表自行到**原发布方**下载，并遵守其许可、地域与商业使用条款。
> 表中文件名取自工作流节点实际保存值（`UNETLoader` / `CLIPLoader` / `VAELoader` / `LoraLoaderModelOnly` / `ModelPatchLoader`），可直接对照。

## 1. MiniMax-H3 官方权重

上游模型库：<https://huggingface.co/Comfy-Org/MiniMax-H3>
（官方说明同步见 <https://huggingface.co/MiniMaxAI/MiniMax-H3>；提示词写作指南见官方 `docs/VIDEO_PROMPT`）

### 扩散模型（diffusion_models）

| 文件名 | 工作流用途 | 安装目录 |
|---|---|---|
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | Ref2VA 主扩散模型（一采主力） | `ComfyUI/models/diffusion_models/` |
| `minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors` | FastH3 VSA 4 步（8193 生产极速版） | 同上 |
| `fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors` | FastH3 8 步 v2 | 同上 |
| `minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors` | Turbo v4 | 同上 |
| `MiniMax-H3-Ref2VA-Acc-8Step.safetensors` | Ref2VA 8 步加速档 | 同上 |
| `fasth3_vsa_gate.safetensors` | FastH3 VSA gate | 同上 |

官方直链示例：
`https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors`

### 文本编码器（text_encoders）

| 文件名 | 安装目录 |
|---|---|
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `ComfyUI/models/text_encoders/` |

官方直链：
`https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`

### VAE（vae）

| 文件名 | 说明 | 安装目录 |
|---|---|---|
| `minimax_h3_video_vae_fp16.safetensors` | 官方视频 VAE FP16 | `ComfyUI/models/vae/` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | 官方视频 VAE INT8-convrot | 同上 |
| `minimax_h3_audio_vae_fp32.safetensors` | 官方音频 VAE FP32 | 同上 |
| `taeh3.safetensors` | 轻量预览 VAE（可选） | 同上 |

### LoRA（loras）

| 文件名 | 说明 |
|---|---|
| `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | FL2V turbo 8 步 |
| `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | Ref2V turbo 4 步 |
| `minimax_h3_ref2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` | Ref2V turbo 8 步 768p |

安装目录：`ComfyUI/models/loras/MINIMAX/`（工作流中以 `MINIMAX\<file>` 前缀引用）

### ControlNet（controlnet）

| 文件名 | 说明 |
|---|---|
| `minimax_h3_fun_controlnet_union_2.0_pruned_int8_convrot.safetensors` | Fun ControlNet Union 2.0（8207 线候选使用） |

安装目录：`ComfyUI/models/controlnet/`

> Kijai 的 int8 convrot 视频 VAE 等非官方变体请到其 HuggingFace 页面获取，许可与限制以发布方为准。

## 2. SDPose 多人姿态（子图依赖）

上游：<https://huggingface.co/Comfy-Org/SDPose>

| 文件名 | 安装目录 |
|---|---|
| `sdpose_wholebody_fp16.safetensors` | `ComfyUI/models/checkpoints/` |
| `rt_detr_v4-x-hgnet_fp16.safetensors` | `ComfyUI/models/diffusion_models/` |

## 3. 量化 / 加速相关（按需）

- INT8 / NVFP4 / convrot 变体均为**同一模型的量化版本**，不是本仓库产物。
- PDD（分区扩散）加速由第三方节点 `ComfyUI-MiniMax-H3-PDD-Acc` 提供，不额外下载权重（其分区指纹随节点包分发）。
- VSA / BlockSparse / Sage Attention 等注意力实现由对应第三方节点提供，按节点仓库说明安装（部分需要额外编译或 `triton`）。

## 4. 核验方式

- 下载后建议核对文件大小与发布方页面标注一致；发布方若提供 `SHA256`，请以其为准。
- **本仓库不提供也不声称权重哈希**：仓库内不含权重，无法也无必要给出哈希。
- 加载验证：导入 `workflows/current/V29_chinese_director_production_8197.json` 后，ComfyUI 前端不应出现红色缺失模型节点；若 `UNETLoader` / `CLIPLoader` / `VAELoader` 下拉为空，说明对应权重未放到正确目录。

## 5. 授权与合规提醒

- 模型权重的许可、地域可用性与商业使用限制**以原发布方条款为准**，本仓库不作任何担保。
- 本仓库仅提供**工作流与代码**，不提供权重分发、镜像或代下载。

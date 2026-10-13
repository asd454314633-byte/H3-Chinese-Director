# docs/evidence — 上游钉住副本（第三方内容声明）

本目录下存放的是**上游第三方作品的逐字节副本**，用途只有一个：让本仓库的复核脚本能在
**离线**环境下重跑，而不是让使用者在联网时机后再核对一次哈希。

## sdpose_blueprint_pinned.json

| 项 | 值 |
|---|---|
| 文件 | `sdpose_blueprint_pinned.json`（33,268 B） |
| 上游仓库 | <https://github.com/Comfy-Org/workflow_templates> |
| 上游作者 | **Comfy-Org** |
| 上游文件 | `blueprints/video_to_pose_map_sdpose_multi_person.json` |
| 上游许可 | **MIT**（仓库根 LICENSE；GitHub API `license.spdx_id == "MIT"`，2026-10-13 核实） |
| 钉住提交 | `cdccb2ee7a7cd0baee4630cf7186283a98ab408f` |
| 钉住 blob SHA1 | `6f6d7ab146a5b143f70bc98d444a7a64829a94ea` |
| 钉住 SHA256 | `92e31fb99f4a005a9263c296429c99eb0847567d64b1f3a35fa42839e0cbfec2` |
| 本副本状态 | **逐字节未修改**（不做任何字段改动，否则哈希不再匹配） |

### 许可声明（依上游 MIT 要求随附）

> 本副本是上游 MIT 许可作品的**原样复制**，版权归上游作者 Comfy-Org 所有
> （具体署名句以上游仓库 `LICENSE` 文件所载为准：
> <https://github.com/Comfy-Org/workflow_templates/blob/main/LICENSE>）。
>
> 依 MIT 许可，允许免费使用、复制、修改、合并、出版、分发、再许可与销售本副本，
> 但**必须**在所有副本或实质性部分中包含上述版权声明与下列许可声明：
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this
> software and associated documentation files (the "Software"), to deal in the Software
> without restriction, including without limitation the rights to use, copy, modify, merge,
> publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
> to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or
> substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
> INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
> PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
> FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
> OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
> DEALINGS IN THE SOFTWARE.

### 归属与修改

- 本仓库**不对该副本主张原创**，也**不**用本仓库的 MIT 覆盖它 —— 它的许可来自上游。
- 本仓库实际使用的是它的**派生件**（唯一工作流内 `definitions.subgraphs[1]`），
  逐项修改清单见 [`THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md) §4。
- 删除本副本**不影响**生产运行，只会让 `scripts/verify/verify_sdpose_blueprint.py`
  无法离线复核（会退回需要联网的模式）。

## 许可边界提醒

ComfyUI 宿主是 GPL-3.0，但 GPL **不自动延伸**到这个独立发布的 MIT 仓库。
判定依据是**该仓库自己的 LICENSE 文件**，不是宿主的许可。

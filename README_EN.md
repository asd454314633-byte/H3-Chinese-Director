# H3 Chinese Director (H3-Chinese-Director)

An **all-Chinese centralised "director console"** for **MiniMax-H3 video generation**: a self-developed
control layer that chains
*six-segment story editing → continuous video generation scheduling → previous-segment AV-latent
continuation → Conditioning PreBake cache → automatic six-segment merge → workflow safety gating
and run-receipt validation → VRAM/RAM lifecycle engineering* into one production pipeline.

> **This repository publishes exactly ONE workflow**:
> `workflows/current/V29_chinese_director_production_8197.json` (the 8197 frozen production build).
> Historic workflows, the 8207 experimental workflows and the historical engineering archive are
> **no longer distributed publicly**; they stay in the author's local production archive only.

> This project is **original engineering led by the local author**: the Chinese director console
> (evolved from V16 to V29), the self-developed ComfyUI nodes, the frontend control layer, the
> cache/receipt safety mechanisms and the memory-lifecycle optimisations were all designed,
> implemented, debugged and accepted by this repository's author.
> **The MiniMax-H3 model, the ComfyUI engine, and third-party PDD / VSA / attention-optimisation
> nodes are NOT the author's original work** — see
> [`docs/UPSTREAM_ATTRIBUTION.md`](docs/UPSTREAM_ATTRIBUTION.md) and
> [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

> ⚠️ **Originality boundary — do not read this as "100% original".** This repository **contains
> third-party material and third-party derivatives**, and **two dependencies are NOT shipped and
> must be installed by you**:
> 1. The **SDPose multi-person pose subgraph** inside the single workflow is a **derivative** of the
>    official blueprint from `Comfy-Org/workflow_templates` (MIT), pinned and with the local
>    modifications itemised — **not** an original subgraph. See `THIRD_PARTY_NOTICES.md` §4.
> 2. The **official MiniMax H3 prompt-writing Skill** files are **verbatim upstream originals**;
>    their licence is unresolved (`LICENSE_HOLD`) and they have been **removed from this public
>    package** — you must supply your own copy at runtime. See §External dependencies below.
> 3. **ComfyUI-H3-AudioRefine** (Adudeguyman, MIT) is an **external dependency**; no `vendor/`
>    directory is shipped. See §External dependencies below.
>
> This repository therefore does **not** claim that "all subgraphs are fully original" or that it
> "contains no third-party content".

## What this repository is / is not

- **Not** a model release: **no model weights are included** (no `.safetensors`, `.ckpt`, `.pt`,
  `.pth`, `.gguf`, shards or caches). Only upstream download URLs, versions, filenames, install
  directories and verification notes are provided — see [`docs/MODELS.md`](docs/MODELS.md).
- **Not** a ComfyUI distribution: the ComfyUI framework, Python venvs, Torch installs and
  third-party node packages are **not** vendored.
- **Not** a history dump: no `workflows/history/`, no `history/` reports, no historical file
  manifests — so that old JSON/log files cannot smuggle personal creative content back into public.
- **Is** an importable, hackable, reproducible **Chinese director console: one frozen V29 workflow +
  self-developed nodes + frontend + install/verify scripts + structural tests**.

## Original contributions (summary)

| # | Capability | Attribution | Code |
|---|---|---|---|
| 1 | All-Chinese centralised console (single entry point `N159 H3OperationSelector`) | Original | `custom_nodes/local_author/**/h3_workflow_helpers/` |
| 2 | Six-segment story editing & state (`H3SixDirectorState` / `six_prompt_state`) | Original | same + `H3_Prompt_Sidecar/web/` |
| 3 | Continuous generation scheduling (`continuous` / `start_index` / `start_mode`) | Original | same + `chinese_director.js` |
| 4 | Previous-segment AV-latent continuation (`LTXVSeparateAVLatent` → `LTXVConcatAVLatent`) | Original workflow orchestration | subgraph `New Subgraph连续-封装` |
| 5 | Conditioning PreBake cache, invalidation & recovery | Original | `h3_conditioning_prebake/` |
| 6 | Automatic six-segment video merge | Original | `H3_Prompt_Sidecar/`, ManualChainMerge route |
| 7 | Workflow safety gating & run-receipt validation (rejects stale group/prompt/latent receipts) | Original | `h3_conditioning_prebake/`, workflow `extra.h3_*` contracts |
| 8 | VRAM/RAM lifecycle engineering (Adaptive Host Warm, `H3SelectiveTEUnload`, `H3PartialDiffusionEvictBeforeVAE`, PDD 308-patch compatibility) | Original (built on top of upstream H3 runtime) | `h3_adaptive_host_warm_inplace/`, `h3_selective_te_unload/`, `h3_partial_diffusion_evict/` |
| 9 | Multi-route model / sampler / reference management (selector matrix) | Original workflow orchestration | `H3*Selector` node family |
| 10 | Self-developed frontend control layer (Chinese UI, six-segment panel, switch persistence, GUIDE authority normalisation) | Original | `H3_ChineseDirectorUI/js/`, each package's `web/*.js` |

Full per-item evidence (purpose → design → exact source path → delta vs upstream → versions →
tests → attribution type → verification status) is in
[`AUTHOR_CONTRIBUTIONS.md`](AUTHOR_CONTRIBUTIONS.md).

## Quick start

1. Install upstream ComfyUI + Python/PyTorch/CUDA → [`docs/INSTALL_WINDOWS_8207.md`](docs/INSTALL_WINDOWS_8207.md)
2. Install the required third-party custom nodes at the pinned versions → [`docs/UPSTREAM_ATTRIBUTION.md`](docs/UPSTREAM_ATTRIBUTION.md)
3. Download model weights yourself → [`docs/MODELS.md`](docs/MODELS.md)
4. Copy `custom_nodes/local_author/8197_production_line/*` into your `ComfyUI/custom_nodes/`
5. Import the **one and only** published workflow
   `workflows/current/V29_chinese_director_production_8197.json` and use **only** the single
   "H3 全中文傻瓜导演台" entry node on the canvas
6. Model-free tests: `python scripts/verify/verify_workflow_structure.py`,
   `python tests/test_workflow_structure.py`, `python tests/test_public_release_scope.py`

### External dependencies (not shipped — you must install them)

| Dependency | Upstream | Licence | Install | Behaviour when missing |
|---|---|---|---|---|
| Official MiniMax H3 prompt-writing Skill | `MiniMax-AI/MiniMax-H3` → `skills/h3-prompt-writing/` | **`LICENSE_HOLD`** (GitHub API `license == null`; HF MiniMax Community License Agreement with regional/commercial restrictions) | obtain your own copy, then `python scripts/setup/install_minimax_official_skill.py --source <copy>`, or set `H3_MINIMAX_OFFICIAL_SKILL_DIR=<copy>` | raises `H3OfficialGuideMissing` **only when the official guide is actually parsed** (message includes provenance, licence note and install command). `H3_V28_Director` still imports fine. |
| ComfyUI-H3-AudioRefine | `Adudeguyman/ComfyUI-H3-AudioRefine` @ `fd5a8dfe8b4c636b1877abd07d11ebc985eddbed` | **MIT** © 2026 Adudeguyman | `python scripts/setup/install_h3_audio_refine.py --source <copy>` (this installer supports local `--source` and `--dest` only; no download flag) | raises `H3AudioRefineMissing` with upstream URL, licence, commit and `git clone` command. **No stub class, no silent skip.** |

Both installers are **offline by default** and `--verify` only checks. **Their default destinations are inside the cloned repository**, not automatically inside an existing ComfyUI installation. If the nodes have already been copied to ComfyUI, specify `--dest` pointing to `ComfyUI/custom_nodes/H3_V28_Director/skills/official-minimax-h3-prompt` or `ComfyUI/custom_nodes/H3_AudioUpgrade/vendor` respectively, or set `H3_MINIMAX_OFFICIAL_SKILL_DIR` / `H3_AUDIO_REFINE_DIR`. See the Windows install guide for exact commands.

> **8197 acceptance does not imply 8207 acceptance.** 8197 is the frozen production line; 8207 is an
> independent runtime/experiment line kept in the author's local archive only — its sources are **not**
> part of this public package. Only the 8197 workflow and the 8197 production-line sources are
> published here. See [`docs/INSTALL_WINDOWS_8207.md`](docs/INSTALL_WINDOWS_8207.md).

## Privacy & sanitisation

Every file here is a `SANITIZED_PUBLIC_COPY`. Sanitisation is **content-level** — not renaming, not
a `.gitignore`, not deleting one image. Removed: all user images/video/audio/reference assets and
their filenames, base64/data-URI blobs, thumbnails and preview caches; all personal creative prompts
(six-segment stories, character settings, dialogue, positive/negative prompts, continuation caches,
test inputs); all machine-specific paths and identities; all secrets and credentials; all user
runtime state (last sampling inputs, prompt_id/group_id/receipts, latent sources, last selection,
UI session).

**Kept:** node types, link topology, parameter names, verified generic defaults, genuinely
functional system templates and compilation rules, upstream public URLs, software versions,
`127.0.0.1` examples. **Never altered:** real durations, dates, error causes or acceptance verdicts —
but per-node raw run receipts (prompt_id, pid, timestamps, asset filenames) are not published.
Every one of the 181 top-level nodes and the 15 nodes inside the 2 embedded subgraphs of the single
V29 workflow was audited item by item; the assertions live in `tests/`.
See [`docs/SECURITY_AND_PRIVACY.md`](docs/SECURITY_AND_PRIVACY.md).

## Benchmarks

Real six-segment generation (8197 frozen production):
`132.926 / 92.423 / 90.368 / 87.255 / 91.070 / 90.277` s; automatic merge 41.5 s,
996 frames / 24 fps / 608×1056. GPU sampling peak 22016 MiB, minimum free RAM 5.94 GiB,
commit sampling peak 95.05 GiB. Single-run values, repeated measurements, theoretical estimates and
unverified claims are **labelled separately** in [`benchmarks/runs.csv`](benchmarks/runs.csv);
failures and HOLD verdicts are retained. The `evidence_file` column uses a `LOCAL_ARCHIVE:` prefix
pointing at the author's local production archive (not shipped publicly); the numbers themselves are
unchanged.

## Licence

- Author's original parts: **MIT License** ([`LICENSE`](LICENSE)). `LICENSE` enumerates exactly
  what the grant covers.
- **No MIT grant is made over any third-party original in this repository:**
  - Official MiniMax H3 prompt-writing Skill → `LICENSE_HOLD`; removed from the public package,
    used as an external dependency only.
  - SDPose multi-person pose subgraph → shipped inside the single workflow, but it is a
    **derivative** of `Comfy-Org/workflow_templates` (**MIT**) and is distributed under that
    upstream MIT licence with a modification notice. It is **not** claimed as original.
  - ComfyUI-H3-AudioRefine → upstream **MIT © 2026 Adudeguyman**, installed externally, keeping
    its own notice and copyright.
- The ComfyUI host is GPL-3.0, but GPL does **not** automatically extend to independent
  third-party repositories such as the MIT-licensed `workflow_templates`. Importing, monkey-patching
  or overriding the upstream runtime is **runtime coupling**, not copying or deriving its source.
- Third-party dependencies and models: their own licences, listed in
  [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and `docs/UPSTREAM_ATTRIBUTION.md`.
  Anything whose licence could not be verified from an authoritative source is marked
  `LICENSE_HOLD` and **no legal conclusion is asserted** — see [`REMAINING_HOLD.md`](docs/acceptance/REMAINING_HOLD.md).
- **No weights are shipped**; users download them under the upstream authors' licence, regional and
  commercial terms.

---
name: breeze-voice-workflow
description: 使用本地 Breeze-TTS-2 原版 PyTorch 做授权声音克隆、逐句配音及后期变速、排句、混音。适用于已有或待准备的 NVIDIA 环境；不适用于 GGUF 便携版。
---

# Breeze 配音与混音

按用户目标选择克隆、音色设计、修补某句或后期处理，可单独调用、组合或替换工具；不规定执行顺序、种子、语速、音量或成品结构。需要命令时查 [使用示例](references/usage.md)。

需要旁白、角色或情绪示例时，读 [音色包：原始描述与配置](references/voice-pack.md)，按需选用或改写，不将片中参数当作全局默认。

- `scripts/tts_clone.py`：逐句生成；路径通过 `--repo/--model/--work-dir` 指定，模式由参考录音和 instruction 决定。`--only` 选句，`--validate-only` 只查输入。
- `scripts/timeline.py`：变速、裁静音和顺序／节拍排句。`scripts/mix.py`：按 plan.json 混音，可无 BGM。示例在 [assets](assets/)，参数按素材与需求调整。
- 克隆需有权使用的参考录音及准确逐字稿；本脚本参考音频为 24 kHz 单声道、临时目录用纯英文路径。保留原始输入；覆盖已有配音须明确指定 `--overwrite`。
- 快速阶段增加编译／预热显存；`--eager` 关闭它们，与 attention 的 eager 设置不同。根据显存、兼容性与任务取舍，不照搬历史性能数字。
- 需新环境时使用独立 Conda 环境及 `uv pip`，按源码兼容要求选版本。成品按实际任务检查漏字、剪切、响度等；ASR 仅辅助，后期变速不等于推理加速。

模型权重及自托管输出限研究／非商业用途，商用核对官方授权。如实说明本次验证范围；[现有验证记录](references/validation.md)仅作背景。

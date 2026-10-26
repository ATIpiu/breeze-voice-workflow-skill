# 按需使用的命令示例

以下是独立示例，不是必须按顺序执行的流程。按用户目标选择工具、模式与参数，也可使用已有工具替代。

2026-10-25 · 从实际项目脚本去敏、改为可配置路径的版本。

这不是 GGUF 便携版的插件，也不是完整的一键安装环境。需要已有 Breeze 原版 PyTorch 源码、原版 checkpoint、匹配的 NVIDIA / CUDA Python 环境，以及 FFmpeg。官方安装与许可：https://github.com/breezeblue-ai/breeze-tts

包内没有模型、私人录音及其逐字稿、成品音频、音乐或账号信息。assets 中是占位示例；[音色包](voice-pack.md)另外保留作者授权公开的片中描述、参考句与台词。仅克隆本人或已经获授权的声音。模型权重及自托管输出限研究、非商业用途，具体按模型许可执行。

## 1. 环境与文件

- 使用独立 Conda 环境；Python 依赖用 uv pip 管理，版本以所选源码 requirements.txt 和显卡兼容要求为准。
- 历史项目环境快照：Python 3.12.13、torch 2.8.0+cu128、transformers 4.57.3、triton-windows 3.4.0.post21；这是核对时本机已装版本，不是新环境的完整依赖锁，也不能保证换机可直接复现。
- 当前本机源码 requirements.txt 的 torch 要求与上述旧环境不同，勿在旧项目里直接升级覆盖。新环境先按官方说明准备。
- 后期脚本需要 numpy、soundfile 和 PATH 可找到的 ffmpeg；也可用 --ffmpeg 指定完整路径。
- 新建纯英文目录，例如 D:\BreezeWork。在该目录准备你自己的 24 kHz 单声道 ref.wav、准确的 UTF-8 ref.txt；不要直接使用 assets/ref.example.txt 的占位文字。
- 将 assets/lines_say.example.json 复制成 lines_say.json，按一句一条填写；id 只能包含英文字母、数字、下划线、短横线。

## 2. 检查输入，再克隆

激活原版模型的 Python 环境，在 Skill 根目录运行。把 --repo 和 --model 改成真实位置。--model 指向原版完整 checkpoint，不是 .gguf 文件。

```powershell
python scripts/tts_clone.py --repo D:\Breeze\breeze-tts --model D:\Breeze\Breeze-TTS-2 --lines lines_say.json --ref ref.wav --ref-text ref.txt --out vo_raw --seeds 42 --cfg 1 --eager --work-dir D:\BreezeWork\temp --validate-only
```

输入检查不会加载模型，也不检查模型推理效果。去掉末尾 --validate-only 后正式运行同一条命令。正式运行会检查参考音频采样率、声道和是否为空。

输出如 vo_raw/L01_s42.wav。--eager 关闭快速阶段；去掉后启用 fast_all，首次编译/预热需要更多显存。两种情况都使用 eager attention。Windows 兼容变量 TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER 默认设为 0；这是历史项目配置，不代表所有新版本都需要。

补某句可加 --only L02。为保护已有结果，必须换新输出目录，或明确加 --overwrite。脚本先生成临时 WAV，非空才复制到输出目录。它会临时复制参考音频到 --work-dir 的纯英文路径，结束后清理临时副本。

Voice Design：去掉 --ref 和 --ref-text，改用 --instruction "成年男性，普通话，吐字清楚。" --cfg 4。参考音频加 --instruction 是 Voice Direction。本包参数与官方 infer.py / GGUF 参数不同，请勿混用。

## 3. 变速、裁静音和排时间轴

```powershell
python scripts/timeline.py --lines lines_say.json --input vo_raw --out prepared --seed 42 --speed 1.25 --gap 0.25
```

输出 prepared/vo/*.wav 和 prepared/plan.json。变速之后按振幅阈值 0.012 裁静音，开头留 20 ms、末尾留 80 ms；空音频会报错。轻声可能被误裁，必须检查起音尾字。--out 必须是新目录。

可选加 --bpm 80：每句起点放到后续节拍，不会压缩句子或让它们互相覆盖。这是通用排版方式，不是原片定制的分组、音乐剪段或关键词时间轴。原项目的音乐、固定小节、画面数据均已剥离。

需要背景音乐可再加 --bgm D:\MyAudio\licensed-bgm.wav。plan.json 中会记录使用者自己填的音乐路径，不要直接公开含私人目录的运行结果。短音乐在混音时会循环，循环点不保证无缝；请事先准备合适的音乐长度并按音乐许可使用。台词 text 不会生成逐字时间戳。

## 4. 混音

```powershell
python scripts/mix.py --plan prepared\plan.json --out final_mix.wav
```

plan.json 的相对音频路径以 plan.json 所在文件夹为基准。没有 BGM 也能运行。逐句有效样本 RMS 对齐到 0.12；有 BGM 时压低 7 dB，时间常数为 80 / 400 ms；最后 loudnorm 目标 I=-14、TP=-1.5、LRA=11。输出为 48 kHz 双声道 PCM WAV。

本公开版不包含原项目 SFX、BGM 剪段、音乐暂停和画面事件功能。final_mix.wav 必须是新文件；音轨超出 plan.total 会报错，不会默默截断。总时长限一小时，脚本会在内存中混音，长音频可能占用大量内存，建议先做短片段。

```powershell
ffmpeg -i final_mix.wav -af ebur128=peak=true -f null -
```

响度目标不等于实测值，输出后重新测量和试听。1.25 倍速是后期语速调整，不是模型推理提速。

## 5. 验证范围

见 [validation.md](validation.md)。原项目确实用过声音克隆；本公开去敏版另做参数检查和合成信号后期流程验证，不把这些检查称作重新跑过模型克隆。未随包分发 ASR 模型或检查脚本；转写与逐字对齐请另配适合自己环境的工具。

# Breeze Voice Workflow Skill

本地 Breeze-TTS-2 原版配音与后期 Skill：声音克隆、逐句 WAV、变速裁静音、节拍排句与 BGM 混音。

入口：[SKILL.md](breeze-voice-workflow/SKILL.md) · [使用说明](breeze-voice-workflow/references/usage.md) · [验证范围](breeze-voice-workflow/references/validation.md)

将完整的 `breeze-voice-workflow` 文件夹放入所用客户端的 skills 目录；使用 `$breeze-voice-workflow` 调用。脚本在 `scripts/`，示例在 `assets/`。已有原版 PyTorch 环境可直接按使用说明填写路径；本包不是 GGUF 插件或一键环境安装器。

去敏包不包含个人路径、私人录音、实际逐字稿、音乐、模型或凭据。脚本来源为实际项目的可移植改写版；后期合成信号验证已通过，公开版未重跑真实克隆与快速路径基准。模型权重与自托管输出限研究／非商业用途，商用请核对官方授权。

[博客教程](https://blog.atipiu.org/notes/breeze-tts-2-local-guide/) · [官方模型源码与许可](https://github.com/breezeblue-ai/breeze-tts)

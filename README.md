# Breeze Voice Workflow Skill

[打开博客与教程](https://atipiu.github.io/breeze-voice-workflow-skill/) · [下载独立 HTML](https://atipiu.github.io/breeze-voice-workflow-skill/breeze-tts-2-local-guide.html) · [Skill 下载](https://github.com/ATIpiu/breeze-voice-workflow-skill/releases/latest)

[Codex 重置提醒](https://blog.atipiu.org/codex-reset/) · [博客首页独立 HTML](https://atipiu.github.io/breeze-voice-workflow-skill/atipiu-blog.html)。首页和文章列表的 Codex 入口直接连接 Linux 笔记本上的订阅服务；静态站构建不会把这个地址改写到 GitHub Pages。首页 HTML 内嵌样式、交互与搜索索引，其他文章及在线订阅需要联网打开。发布前运行 `python tools/build_site.py` 和 `python tools/check_site.py`。

本地 Breeze-TTS-2 原版配音与后期 Skill：声音克隆、逐句 WAV、变速裁静音、节拍排句与 BGM 混音。

入口：[SKILL.md](breeze-voice-workflow/SKILL.md) · [使用说明](breeze-voice-workflow/references/usage.md) · [音色包：旁白、角色与情绪](breeze-voice-workflow/references/voice-pack.md) · [验证范围](breeze-voice-workflow/references/validation.md)

将完整的 `breeze-voice-workflow` 文件夹放入所用客户端的 skills 目录；使用 `$breeze-voice-workflow` 调用。脚本在 `scripts/`，示例在 `assets/`。已有原版 PyTorch 环境可直接按使用说明填写路径；本包不是 GGUF 插件或一键环境安装器。

去敏包不包含个人路径、私人录音及其逐字稿、音乐、模型或凭据。音色包保留作者授权公开的描述、参考句与示例台词，不含音频。脚本来源为实际项目的可移植改写版；后期合成信号验证已通过，公开版未重跑真实克隆与快速路径基准。模型权重与自托管输出限研究／非商业用途，商用请核对官方授权。

[博客教程](https://blog.atipiu.org/notes/breeze-tts-2-local-guide/) · [官方模型源码与许可](https://github.com/breezeblue-ai/breeze-tts)

`docs/` 是 GitHub Pages 网站。最新博客采用用户提供的 Astro + React 版本，源码在 [`astro-blog/`](astro-blog/README.md)：进入该目录执行 `npm ci`、`npm run build` 和 `python3 ops/check-build.py`，再把 `dist/` 同步至仓库 `docs/`，提交即可发布。旧的 `website/` 与 Python 构建器保留为历史来源，不再用于当前站点发布。Breeze 教程的旧链接、53个锚点、音频与单文件下载继续保留。服务器配置、研究临时文件、凭据与私人素材不在公开网站源码中。

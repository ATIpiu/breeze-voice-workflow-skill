# ATIPIU 博客（Astro）

采用用户提供的 atipiu-blog-astro.zip 网站源码与公开素材；研究资料、运维凭据和服务器配置不在公开源码中。

当前站点保持 GitHub Pages 发布，blog.atipiu.org 的原有博客地址继续跳转到本站；/codex-reset/ 保持由笔记本服务提供，管理员页面与接口继续关闭。

使用 Node.js 24：运行 `npm ci`、`npm run build`，再运行 `python3 ops/check-build.py` 检查链接、旧锚点和订阅入口。构建结果在 dist/，发布时同步到仓库 docs/ 并保留 .nojekyll。

Astro 配置和输出处理支持 /breeze-voice-workflow-skill/ 子路径。实时状态仅从订阅服务公开的 /api/status 读取；不会访问管理接口或传递邮箱、密钥。

旧版单文件 HTML 下载保留为独立导出，最新网站源码以本目录为准。

# ATIPIU 博客（Astro）

采用用户提供的 atipiu-blog-astro.zip 网站源码与公开素材；研究资料、运维凭据和服务器配置不在公开源码中。

正式首页为 https://blog.atipiu.org/ ，直接使用域名根路径。VPS Nginx 提供静态站点，/codex-reset/ 继续转发到笔记本服务，管理员页面与接口继续关闭。GitHub Pages 保留兼容副本，页面 canonical、RSS 和站点地图统一指向正式域名。

使用 Node.js 24：运行 `npm ci`、`npm run build`，再运行 `python3 ops/check-build.py` 检查链接、旧锚点和订阅入口。正式站构建结果在 dist/。发布时上传到服务器的新版本目录，检查后切换 current 软链接。GitHub Pages 副本使用 `npm run build:pages`、`python3 ops/check-build.py --pages`，将 dist-pages/ 同步到仓库 docs/ 并保留 .nojekyll。

Astro 默认输出域名根路径，副本构建单独适配 /breeze-voice-workflow-skill/ 子路径。实时状态仅从订阅服务公开的 /api/status 读取；不会访问管理接口或传递邮箱、密钥。

首页社媒入口在 src/components/SocialLinks.astro，二维码在 public/assets/social/。小红书、抖音二维码直接裁自作者提供的原图，B 站二维码编码经核对的个人空间链接；均支持放大与保存，并提供独立主页链接。

旧版单文件 HTML 下载保留为独立导出，最新网站源码以本目录为准。

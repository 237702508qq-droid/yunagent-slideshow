# 云桌面 AI Agent 记忆增强方案 — 可交互网页演示

基于 **HyperFrames Slideshow**（hyperframes 0.8.41 standalone harness）制作的 10 页商务汇报演示，
主题：在 **VDI 云桌面** 内为办公 AI Agent 构建「桌面记忆」（记忆双用途：Agent 直接调用 + 模型整理为个人上下文）。

**在线访问**：https://237702508qq-droid.github.io/yunagent-slideshow/

---

## 打开方式

### 方式一：在线（推荐）
直接打开上面的 GitHub Pages 地址。

### 方式二：本地
```bash
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000/
```
> 必须通过 HTTP 服务打开（浏览器 `file://` 下 iframe 跨域受限，播放器无法驱动组合）。

## 操作方式

| 按键 / 操作 | 作用 |
|---|---|
| `→` / `Space` | 下一步（fragment 逐条揭示，逐步推进） |
| `←` / `Backspace` | 上一步（在分支内则返回主线原位） |
| 点击「深入 →」按钮 / 分支卡片 | 进入分支页（hotspot 分支） |
| `P` | 演讲者模式（新开观众页 + 备注视图，BroadcastChannel 同步） |
| 右下角胶囊 | 前后翻页、页码、Present |

## 页面结构（10 主线页 + 2 分支页）

| # | 标题 | 交互 |
|---|---|---|
| P1 | 让云桌面里的 AI Agent 真正「懂你」（封面） | — |
| P2 | 提示词给得再多，Agent 依然经常走偏——两个典型问题 | 4 个 fragment |
| P3 | Agent 不「懂你」，只能「抽卡」；对话框之外一片空白 | 4 个 fragment |
| P4 | 在 VDI 桌面启用「桌面记忆」——一套操作数据，两种增强产出 | 4 fragment + **hotspot：三层架构分支** |
| P5 | 两个问题，一次解决：不再「抽卡」，模糊指令也能达成 | 4 fragment + **hotspot：改造前后对比分支** |
| P6 | 越用越懂你——四类工作画像持续沉淀为「个人上下文」 | 3 个 fragment |
| P7 | 对企业的三大回报：买的不是「又一个 AI 助手」 | 4 个 fragment |
| P8 | 云桌面（VDI）是「桌面记忆」的最佳载体 | 4 个 fragment |
| P9 | 四道防线，数据不出云桌面 | 5 个 fragment |
| P10 | 三步落地：从试点验证到全员推广 | 2 个 fragment |
| B1 | 采集 → 记忆 → 增强（三层架构详解） | 分支页（从 P4 进入） |
| B2 | 同一条指令：5 分钟人工纠偏 → 30 秒直接交付 | 分支页（从 P5 进入） |

## 目录结构

```
slideshow/
├── index.html              # 交付入口（standalone harness + island + hotspot bridge）
├── composition/index.html  # HyperFrames 组合（12 scene + JSON island + root 时间线）
├── vendor/                 # 本地化运行时（无 CDN，完全离线可用）
│   ├── gsap.min.js
│   ├── hyperframes-player.global.js   # 已打补丁：runtime 指向 ../vendor/
│   ├── hyperframes-slideshow.global.js
│   └── hyperframe.runtime.iife.js
├── assets/                 # PIL 生成的配图（10 张，深蓝商务风）
├── scripts/
│   ├── gen_images.py       # 配图生成（PIL）
│   ├── selfcheck.py        # 静态自查（island schema / fragment 时间 / island 同步 / node --check）
│   ├── browsertest.cjs     # 浏览器实测（headless Chromium，24 项断言）
│   └── qa_shots.cjs        # QA 截图
└── qa/                     # 关键页截图
```

## 技术要点

- **JSON island** 声明 slides / notes / fragments / hotspots / slideSequences（composition 与 wrapper 各一份，保持同步）
- **root 组合 + 12 scene 时间线**：fragment reveal 编码在 root 时间线上（reveal 在 hold 点前 0.35s 结束，seek 即终态）
- **hotspot 分支**：island 驱动的光标 pill（P4 / P5）+ 组合内可点击卡片（postMessage → `controller.enterBranch`）
- **配图**：全部由 `scripts/gen_images.py` 用 PIL 绘制（Noto Sans CJK），无外部素材依赖
- **验证**：`selfcheck.py` 全绿；`npx hyperframes lint/check` Runtime 0 errors；浏览器实测 24/24 PASS

## 重新生成 / 修改

```bash
python3 scripts/gen_images.py        # 重新生成配图
python3 scripts/selfcheck.py         # 静态自查
node scripts/browsertest.cjs         # 浏览器实测（需先 python3 -m http.server 8791）
npx hyperframes lint composition     # 官方 lint（Runtime/Motion/Layout 检查用 check）
```

修改 slides/fragments/notes 时，注意 **composition/index.html 与 index.html 里的 island 要同步**。

## 部署（GitHub Pages）

本仓库通过 contents API 逐文件上传部署（`git push` 在本环境会超时）：

```bash
gh repo create yunagent-slideshow --public
python3 scripts/gh_upload.py                       # PUT repos/.../contents/<path> 逐文件上传
gh api --method POST repos/<owner>/yunagent-slideshow/pages \
  --input pages-config.json                        # {"source":{"branch":"main","path":"/"}}
```

部署后验证：首页与关键资源全部 200，且 `DECK_URL=<线上URL> node scripts/browsertest.cjs` 24/24 PASS。

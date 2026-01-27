# Raindrop to Gitee Sync

这是一个 GitHub Actions 自动化工具，旨在将 [Raindrop.io](https://raindrop.io/) 的书签自动同步到私有的 [Gitee](https://gitee.com/) 仓库中，并转换为 Obsidian 友好的 Markdown 格式。

## ✨ 功能特性

- **自动同步**: 默认每 5 分钟检查一次 Raindrop 更新。
- **Markdown 转换**: 将书签元数据（标题、链接、摘要、标签、封面等）转换为 Markdown 文件。
- **Obsidian 友好**: 生成的文件可以直接用于 Obsidian 知识库 (Second Brain)。
- **包含笔记**: 自动同步 Raindrop 中的高亮 (Highlights) 和笔记 (Notes)。
- **扁平化存储**: 按照 `YYYY-MM-DD-Title.md` 格式命名，避免文件名冲突。
- **增量更新**: 脚本默认检查最近 3 天的书签，避免全量重复抓取。

## ⚙️ 配置指南

要使用此工作流，您需要在 GitHub 仓库中配置以下 Secrets：

### 1. 准备 Token

1.  **Raindrop API Token**:
    - 前往 [Raindrop Integrations](https://app.raindrop.io/settings/integrations)。
    - 创建一个新的 App，获取 `Test Data` 中的 Token。

2.  **Gitee Personal Access Token (PAT)**:
    - 前往 [Gitee 私人令牌](https://gitee.com/profile/personal_access_tokens)。
    - 生成新令牌，**必须勾选 `projects` 权限** (用于读写私有仓库)。

### 2. 设置 GitHub Secrets

在 GitHub 仓库中导航到 `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`，添加以下变量：

| Secret Name | 说明 | 示例值 |
| :--- | :--- | :--- |
| `RAINDROP_API_TOKEN` | Raindrop 的 API 令牌 | `0a1b2c...` |
| `GITEE_USER` | Gitee 仓库的 **Owner** (必须匹配仓库 URL) | `Koyfin` (如果是个人仓库则填用户名) |
| `GITEE_REPO` | Gitee 仓库名称 | `SecondBrain` |
| `GITEE_TOKEN` | Gitee 私人令牌 (PAT) | `d7e8f9...` |
| `DEDAO_API_TOKEN` | (可选) 得到/罗辑实验室 Token，用于 AI 总结 | `eyJ...` |

> ⚠️ **注意**: `GITEE_USER` 必须与 Gitee 仓库 URL 中的 Owner 严格一致。如果仓库地址是 `gitee.com/Company/Project`，则 `GITEE_USER` 必须填 `Company`，不能填您的个人登录名（除非二者相同）。

## 🚀 工作原理

1.  **Trigger**: GitHub Action 定时触发 (Schedule) 或手动触发 (Workflow Dispatch)。
2.  **Clone**: 工作流使用 `git clone` 拉取您的 Gitee 私有仓库。
    - 鉴权逻辑：`https://oauth2:TOKEN@gitee.com/USER/REPO.git`。
3.  **Sync**: 运行 Python 脚本 `raindrop_api_sync.py`。
    - 调用 Raindrop API 获取最新书签。
    - 生成 Markdown 文件写入本地目录。
4.  **Push**: 如果有新文件生成，工作流会自动 Commit 并 Push 回 Gitee 的 `main` 分支。

## 🛠️ 文件结构

- `export_raindrop.py`: 核心同步脚本。
- `.github/workflows/raindrop_sync.yml`: GitHub Action 配置文件。

## 📝生成的 Markdown 示例

```markdown
---
title: "文章标题"
url: https://example.com/article
domain: example.com
created: 2024-01-27
source: raindrop
folder: Unsorted
tags:
  - AI
  - Coding
---

# 文章标题

🔗 [https://example.com/article](https://example.com/article)
📁 **分类**: Unsorted
📅 **创建**: 2024-01-27

## 📝 摘要

这是一个摘要...

## ✨ 高亮标注

> 这是一个精彩的段落。

## 💡 我的笔记

这是我的一点感想。
```

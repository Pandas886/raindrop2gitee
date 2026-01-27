---
title: "Vercel 把自己 10 年 React 秘籍做成 Skill 开源了！"
url: https://mp.weixin.qq.com/s/_jGhBJFLwVaSKtFSUzfl4w
domain: mp.weixin.qq.com
created: 2026-01-27
source: raindrop
folder: Unsorted
tags:
  - React
  - Next.js
  - 性能优化
  - 代码重构
  - Vercel
  - Nodejs技术栈
---

# Vercel 把自己 10 年 React 秘籍做成 Skill 开源了！

🔗 [https://mp.weixin.qq.com/s/_jGhBJFLwVaSKtFSUzfl4w](https://mp.weixin.qq.com/s/_jGhBJFLwVaSKtFSUzfl4w)
📁 **分类**: Unsorted
📅 **创建**: 2026-01-27

## 📝 摘要

点击上方 程序员成长指北，关注公众号回复1，加入高级Node交流群文章转载自：Nodejs技术栈Next.j

## 🖼️ 封面

![cover](https://mmbiz.qpic.cn/mmbiz_jpg/zPkNS9m6iatKyuwpAsvNQGDTdhQoeKETHLrI6hSlc9ibSEdwm3B7ImeTyAePfG3VYe2HjDZI0icEQuoamuEibarrgw/0?wx_fmt=jpeg)


## 🤖 AI 深度总结

**Vercel开源Agent Skills：React/Next.js开发的AI专家指南
Vercel开源Agent Skills：React/Next.js开发的AI专家指南
**

### **🔍 核心项目概述**

Vercel团队将10年React和Next.js开发经验整理为**"Agent Skills"（代理技能）**，这是一套专门为AI设计的开发指南。该技能包通过结构化规则使AI能够像Vercel资深工程师一样进行代码优化，核心文件为`react-best-practices/SKILL.md`，包含**40+条优化规则**，分为**8个类别**，并按影响优先级排序以指导自动化重构和代码生成。

### **🎯 技能包应用场景**

该指南适用于以下开发场景：
- 编写新的React组件或Next.js页面
- 实现数据获取（客户端或服务端）
- 代码审查中的性能问题检测
- 重构现有React/Next.js代码
- 优化包体积或加载时间

### **⚡ 优先级分级优化策略**

Vercel将优化规则按影响程度分为四级，指导AI优先解决关键问题：

| 优先级 | 描述 | 核心优化方向 |
| :----- | :--- | :----------- |
| **CRITICAL（关键级）** | 必须首先解决 | 消除请求瀑布流、优化打包体积 |
| **HIGH（高优先）** | 显著提升性能 | 服务端性能优化 |
| **MEDIUM（中等）** | 常规体验优化 | 客户端数据获取、渲染优化 |
| **LOW（低优先）** | 细节改进 | JS语法的微小优化 |

### **🛠️ 关键优化规则实例解析**

#### **(一) 拒绝"瀑布流"请求（Critical）**
- **问题**：AI常写出串行`await`导致不必要等待，例如在条件分支前提前请求数据
- **优化原则**：**尽早启动Promise，尽可能晚地await**
- **代码对比**：
  ```javascript
  // ❌ 错误示范：无条件等待
  async function handleRequest(userId, skip) {
    const userData = await fetchUserData(userId); // 提前等待非必要请求
    if (skip) return { skipped: true };
    return process(userData);
  }

  // ✅ 正确示范：按需等待
  async function handleRequest(userId, skip) {
    if (skip) return { skipped: true };
    const userData = await fetchUserData(userId); // 仅在需要时等待
    return process(userData);
  }
  ```
#### **(二) 警惕"木桶效应"般的导入（Critical）**
- **问题**：通过桶文件（Barrel File）导入导致加载大量未使用模块
- **优化方案**：直接引用源文件，只导入所需组件
- **代码对比**：
  ```javascript
  // ❌ 错误示范：导入整个库
  import { Button, TextField } from '@mui/material';
  import { Menu, X } from 'lucide-react';

  // ✅ 正确示范：精准导入
  import Button from '@mui/material/Button';
  import Menu from 'lucide-react/dist/esm/icons/menu';
  ```
#### **(三) 服务端组件的"序列化"陷阱（High）**
- **问题**：向客户端组件传递完整大型对象，增加数据传输成本
- **优化原则**：**边界之上，寸土寸金**，只传递客户端必需字段
- **代码对比**：
  ```javascript
  // ❌ 错误示范：传递完整对象
  async function Page() {
    const user = await fetchUser(); // 返回50+字段的大型对象
    return <UserProfile user={user} />; // 仅使用1个字段
  }

  // ✅ 正确示范：精准传递所需字段
  async function Page() {
    const user = await fetchUser();
    return <UserProfile username={user.name} />; // 只传递name字段
  }
  ```
#### **(四) 避免滥用useEffect监听（Medium）**
- **问题**：多个组件重复注册相同事件监听器，导致资源浪费
- **优化方案**：使用`useSWRSubscription`或全局Map进行监听器去重，确保同一事件底层只注册一次

### **🚀 AI编程新趋势：Context Engineering（上下文工程）**

Vercel的`agent-skills`揭示了AI编程的演进方向：
- **传统方式**：通过Prompt告诉AI**做什么**
- **新范式**：通过Skill（技能包）告诉AI**像谁一样思考**

当在Cursor等AI编程工具中以`@Rules`形式加载该技能包后，AI助手将具备Vercel工程团队10年的实战经验。

### **📌 开源资源**

该技能包已开源，地址：  
https://github.com/vercel-labs/agent-skills/blob/react-best-practices/skills/react-best-practices/SKILL.md
### **🔍 核心项目概述**

Vercel团队将10年React和Next.js开发经验整理为**"Agent Skills"（代理技能）**，这是一套专门为AI设计的开发指南。该技能包通过结构化规则使AI能够像Vercel资深工程师一样进行代码优化，核心文件为`react-best-practices/SKILL.md`，包含**40+条优化规则**，分为**8个类别**，并按影响优先级排序以指导自动化重构和代码生成。

### **🎯 技能包应用场景**

该指南适用于以下开发场景：
- 编写新的React组件或Next.js页面
- 实现数据获取（客户端或服务端）
- 代码审查中的性能问题检测
- 重构现有React/Next.js代码
- 优化包体积或加载时间

### **⚡ 优先级分级优化策略**

Vercel将优化规则按影响程度分为四级，指导AI优先解决关键问题：

| 优先级 | 描述 | 核心优化方向 |
| :----- | :--- | :----------- |
| **CRITICAL（关键级）** | 必须首先解决 | 消除请求瀑布流、优化打包体积 |
| **HIGH（高优先）** | 显著提升性能 | 服务端性能优化 |
| **MEDIUM（中等）** | 常规体验优化 | 客户端数据获取、渲染优化 |
| **LOW（低优先）** | 细节改进 | JS语法的微小优化 |

### **🛠️ 关键优化规则实例解析**

#### **(一) 拒绝"瀑布流"请求（Critical）**
- **问题**：AI常写出串行`await`导致不必要等待，例如在条件分支前提前请求数据
- **优化原则**：**尽早启动Promise，尽可能晚地await**
- **代码对比**：
  ```javascript
  // ❌ 错误示范：无条件等待
  async function handleRequest(userId, skip) {
    const userData = await fetchUserData(userId); // 提前等待非必要请求
    if (skip) return { skipped: true };
    return process(userData);
  }

  // ✅ 正确示范：按需等待
  async function handleRequest(userId, skip) {
    if (skip) return { skipped: true };
    const userData = await fetchUserData(userId); // 仅在需要时等待
    return process(userData);
  }
  ```
#### **(二) 警惕"木桶效应"般的导入（Critical）**
- **问题**：通过桶文件（Barrel File）导入导致加载大量未使用模块
- **优化方案**：直接引用源文件，只导入所需组件
- **代码对比**：
  ```javascript
  // ❌ 错误示范：导入整个库
  import { Button, TextField } from '@mui/material';
  import { Menu, X } from 'lucide-react';

  // ✅ 正确示范：精准导入
  import Button from '@mui/material/Button';
  import Menu from 'lucide-react/dist/esm/icons/menu';
  ```
#### **(三) 服务端组件的"序列化"陷阱（High）**
- **问题**：向客户端组件传递完整大型对象，增加数据传输成本
- **优化原则**：**边界之上，寸土寸金**，只传递客户端必需字段
- **代码对比**：
  ```javascript
  // ❌ 错误示范：传递完整对象
  async function Page() {
    const user = await fetchUser(); // 返回50+字段的大型对象
    return <UserProfile user={user} />; // 仅使用1个字段
  }

  // ✅ 正确示范：精准传递所需字段
  async function Page() {
    const user = await fetchUser();
    return <UserProfile username={user.name} />; // 只传递name字段
  }
  ```
#### **(四) 避免滥用useEffect监听（Medium）**
- **问题**：多个组件重复注册相同事件监听器，导致资源浪费
- **优化方案**：使用`useSWRSubscription`或全局Map进行监听器去重，确保同一事件底层只注册一次

### **🚀 AI编程新趋势：Context Engineering（上下文工程）**

Vercel的`agent-skills`揭示了AI编程的演进方向：
- **传统方式**：通过Prompt告诉AI**做什么**
- **新范式**：通过Skill（技能包）告诉AI**像谁一样思考**

当在Cursor等AI编程工具中以`@Rules`形式加载该技能包后，AI助手将具备Vercel工程团队10年的实战经验。

### **📌 开源资源**

该技能包已开源，地址：  
https://github.com/vercel-labs/agent-skills/blob/react-best-practices/skills/react-best-practices/SKILL.md
### **🔍 核心项目概述**

Vercel团队将10年React和Next.js开发经验整理为**"Agent Skills"（代理技能）**，这是一套专门为AI设计的开发指南。该技能包通过结构化规则使AI能够像Vercel资深工程师一样进行代码优化，核心文件为`react-best-practices/SKILL.md`，包含**40+条优化规则**，分为**8个类别**，并按影响优先级排序以指导自动化重构和代码生成。

### **🎯 技能包应用场景**

该指南适用于以下开发场景：
- 编写新的React组件或Next.js页面
- 实现数据获取（客户端或服务端）
- 代码审查中的性能问题检测
- 重构现有React/Next.js代码
- 优化包体积或加载时间

### **⚡ 优先级分级优化策略**

Vercel将优化规则按影响程度分为四级，指导AI优先解决关键问题：

| 优先级 | 描述 | 核心优化方向 |
| :----- | :--- | :----------- |
| **CRITICAL（关键级）** | 必须首先解决 | 消除请求瀑布流、优化打包体积 |
| **HIGH（高优先）** | 显著提升性能 | 服务端性能优化 |
| **MEDIUM（中等）** | 常规体验优化 | 客户端数据获取、渲染优化 |
| **LOW（低优先）** | 细节改进 | JS语法的微小优化 |

### **🛠️ 关键优化规则实例解析**

#### **(一) 拒绝"瀑布流"请求（Critical）**
- **问题**：AI常写出串行`await`导致不必要等待，例如在条件分支前提前请求数据
- **优化原则**：**尽早启动Promise，尽可能晚地await**
- **代码对比**：
  ```javascript
  // ❌ 错误示范：无条件等待
  async function handleRequest(userId, skip) {
    const userData = await fetchUserData(userId); // 提前等待非必要请求
    if (skip) return { skipped: true };
    return process(userData);
  }

  // ✅ 正确示范：按需等待
  async function handleRequest(userId, skip) {
    if (skip) return { skipped: true };
    const userData = await fetchUserData(userId); // 仅在需要时等待
    return process(userData);
  }
  ```
#### **(二) 警惕"木桶效应"般的导入（Critical）**
- **问题**：通过桶文件（Barrel File）导入导致加载大量未使用模块
- **优化方案**：直接引用源文件，只导入所需组件
- **代码对比**：
  ```javascript
  // ❌ 错误示范：导入整个库
  import { Button, TextField } from '@mui/material';
  import { Menu, X } from 'lucide-react';

  // ✅ 正确示范：精准导入
  import Button from '@mui/material/Button';
  import Menu from 'lucide-react/dist/esm/icons/menu';
  ```
#### **(三) 服务端组件的"序列化"陷阱（High）**
- **问题**：向客户端组件传递完整大型对象，增加数据传输成本
- **优化原则**：**边界之上，寸土寸金**，只传递客户端必需字段
- **代码对比**：
  ```javascript
  // ❌ 错误示范：传递完整对象
  async function Page() {
    const user = await fetchUser(); // 返回50+字段的大型对象
    return <UserProfile user={user} />; // 仅使用1个字段
  }

  // ✅ 正确示范：精准传递所需字段
  async function Page() {
    const user = await fetchUser();
    return <UserProfile username={user.name} />; // 只传递name字段
  }
  ```
#### **(四) 避免滥用useEffect监听（Medium）**
- **问题**：多个组件重复注册相同事件监听器，导致资源浪费
- **优化方案**：使用`useSWRSubscription`或全局Map进行监听器去重，确保同一事件底层只注册一次

### **🚀 AI编程新趋势：Context Engineering（上下文工程）**

Vercel的`agent-skills`揭示了AI编程的演进方向：
- **传统方式**：通过Prompt告诉AI**做什么**
- **新范式**：通过Skill（技能包）告诉AI**像谁一样思考**

当在Cursor等AI编程工具中以`@Rules`形式加载该技能包后，AI助手将具备Vercel工程团队10年的实战经验。

### **📌 开源资源**

该技能包已开源，地址：  
https://github.com/vercel-labs/agent-skills/blob/react-best-practices/skills/react-best-practices/SKILL.md

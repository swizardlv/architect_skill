---
name: architecture-refinement
description: "Use when polishing architecture document formatting, fixing typography and markdown issues, or rendering interactive HTML architecture boards"
---

# Architecture Refinement (架构文档精修与看板渲染)

## 概述

高质量的架构交付不仅依赖于内在逻辑的严密，也依赖于外在表达的清晰规范。
架构精修技能提供自动化排版检查、标点与代码块修饰，并将全套分层架构资产渲染为高可视化的单页交互式 HTML 架构看板。

## 适用场景 (When to Use)

- 完成架构文档撰写后，执行正式交付前的格式审查与标点规范化；
- 检查 Mermaid 图表中是否存在未转义字符或格式损坏；
- 将分散在各个目录的架构图纸、表格与决策合成全景看板供人类架构师审查。

## 附属工具与脚本

本技能目录下包含以下可执行自动化脚本：

1. **文档排版与修饰工具**：`scripts/document_polisher.py`
   - 自动检查全角/半角标点混用、规范中英文空格、验证 Markdown 标题层级。
2. **交互式架构看板渲染器**：`scripts/render_architecture_board.py`
   - 扫描目标工作区中的架构 Markdown 资产，将其聚合渲染为现代风格的单页 HTML 看板（内置 Mermaid 图表实时交互、层级导航与高亮展示）。

## 执行步骤与检查清单

### 步骤一：格式与排版规范自查
- 检查是否存在未闭合的代码块或损坏的表格语法；
- 检查 Mermaid 节点文本中是否包含未包裹引号的圆括号、方括号或斜杠；
- 运行排版检查工具：
  ```bash
  python3 skills/architecture-refinement/scripts/document_polisher.py <target_markdown_file>
  ```

### 步骤二：渲染交互式架构看板
- 对目标架构资产目录执行全景看板渲染：
  ```bash
  python3 skills/architecture-refinement/scripts/render_architecture_board.py <source_docs_dir> <output_html_path>
  ```
- 验证生成的 HTML 画板在浏览器中能够正常缩放、平移并清晰显示所有分层架构图。

## 门禁与红线 (Hard Gate & Red Flags)

<HARD-GATE>
交付给利益相关者的架构设计文档，严禁包含任何渲染崩溃的 Mermaid 语法错误。
交付前必须确认看板或文档在主流渲染引擎中可正常解析。
</HARD-GATE>

| 偷懒想法 (Red Flag) | 真实法则 (Reality) |
| :--- | :--- |
| “图表有点乱，只要代码能跑就行” | 架构资产是沟通媒介，损坏的图表不仅影响专业度，更会导致团队对边界产生严重误解。 |

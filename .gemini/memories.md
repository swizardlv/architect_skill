# 项目错题本与系统记忆 (memories.md)

> [!NOTE]
> 本文件记录了架构生命周期编排体系开发与演进协作中被纠正的错题、避坑指南与硬门禁原则。Agent 在每次会话开始时必须吸取这些教训，严禁形式主义与虚假绿灯。

## 1. 纠错与防范列表 (Bug & Logic Corrections)

| 场景与问题描述 | 触发原因归类 | 预防/解决指令 (直接用于开局) |
| :--- | :--- | :--- |
| **画板白屏/卡在载入中（JS SyntaxError）**：HTML 生成时换行符未安全转义，导致前端 JS 语法解析中断，但审计机制打出 76 分 PASS 虚假绿灯。 | 判断逻辑严重缺失：评审只验静态 Markdown 文本行数与正则，未对最终 HTML 交付物执行运行时可解释性与 JS 语法检验。 | “所有交付的 HTML/JS 画板必须经过真实的 `node --check` 语法断言与 `window.__CANVAS_DATA__` 数据挂载检查，存在任何语法错误严禁通过评审。” |
| **底层通用脚本反向硬编码业务案例名**：每换一个新案例就去改 `render_architecture_board.py` 加 `if "Surgical" ... if "OrbitalSat" ...`。 | 逻辑有问题：将具体业务案例耦合进通用架构引擎，违背数据驱动原则，导致每次验证都要手动改脚本代码。 | “通用技能库（skills/）与调度引擎（scripts/）严禁硬编码任何具体业务案例名称；所有项目名称与元数据必须纯数据驱动，由第一份需求文档标题或参数自动推导。” |
| **OpenAPI / Walking Skeleton 页面渲染异常**：YAML/JSON 特殊格式与多行内容在画板中解析崩溃。 | 逻辑有问题：未覆盖复杂引号、多行文本与非 Markdown 格式的边界转义测试。 | “单元测试必须包含特殊字符、多行换行、JSON 嵌套引号的集成防退化断言（test_rendered_board_handles_newlines_and_quotes）。” |
| **Mermaid 图表在离线/内网环境下加载失败**：外部 CDN 不可用时直接白屏或图表崩溃。 | 信息与容错逻辑不足：没有优雅降级机制与离线源码 fallback。 | “前端图表必须包含离线环境降级提示与原始 Mermaid 确定性源码查看器，确保断网可用。” |

## 2. 高效实践与提问模板 (Best Practices & Prompt Templates)

- **真实性审计优先**：不能仅以字数、行数、关键词覆盖作为通过标准，必须对交付工件的可运行性进行真实执行链检验（如 Node 语法检查、pytest 物理测试）。
- **反污染静态防护**：在 `test_skills_spec.py` 中建立 `test_zero_hardcoded_case_names_in_skills_and_scripts`，凡是将业务名称写进通用脚本的代码，提交前自动拦截。

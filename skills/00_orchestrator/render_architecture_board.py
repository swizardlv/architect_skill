"""架构可视化画板渲染引擎 (Architecture Board HTML Renderer).

吸收 Archify 等现代化架构工具的精髓，将系统建模产出的 Mermaid/C4 图表
统一编译为单文件、自包含、支持深浅主题切换、平移缩放 (Pan & Zoom) 与
高质量导出的交互式 HTML 架构全景画板。
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def extract_mermaid_code(file_path: Path) -> str:
    """从 .mmd 或 .md 文件中提取纯净的 Mermaid 图表源码."""
    if not file_path.exists():
        return ""
    content = file_path.read_text(encoding="utf-8").strip()
    if file_path.suffix.lower() == ".mmd":
        return content

    # 若为 markdown 文件，正则提取 ```mermaid 代码块
    matches = re.findall(r"```mermaid\s*\n(.*?)\n```", content, re.DOTALL)
    if matches:
        return matches[0].strip()
    return ""


def validate_mermaid_syntax(code: str) -> Tuple[bool, str]:
    """静态检查 Mermaid 代码的语法基础合法性，防止前端渲染报错.

    Returns:
        Tuple[bool, str]: (是否通过, 错误信息描述)
    """
    cleaned = code.strip()
    if not cleaned:
        return False, "Mermaid 代码为空"

    # 检查合法开头
    valid_headers = (
        "graph", "flowchart", "sequencediagram", "classdiagram",
        "statediagram", "statediagram-v2", "erdiagram", "gantt",
        "pie", "gitgraph", "c4context", "c4container", "c4component", "c4deployment"
    )
    first_line = cleaned.splitlines()[0].strip().lower()
    if not any(first_line.startswith(h) for h in valid_headers):
        return False, f"未知的 Mermaid 图表声明: '{first_line}'，必须以有效图类型开头"

    # 检查常见的破坏性语法: 未在引号内的裸 < 或 > 处于节点标签中导致 HTML 解析失败
    # 例如: Ingest[数据 < 2小时] 应为 Ingest["数据 < 2小时"]
    unquoted_tag_pattern = re.compile(r'\[([^"\]]*?[<>][^"\]]*?)\]')
    matches = unquoted_tag_pattern.findall(cleaned)
    if matches:
        return False, f"节点文本包含未加双引号的 '<' 或 '>' 字符: '{matches[0]}'，必须使用双引号包裹，如 [\"文本 < 标签\"]"

    return True, ""



def build_interactive_html(
    project_name: str,
    diagrams: List[Dict[str, str]],
    metadata: Optional[Dict[str, str]] = None,
) -> str:
    """构建现代化自包含的 HTML 架构画板."""
    meta = metadata or {}
    status_tag = meta.get("status", "VALIDATED")

    diagrams_json = json.dumps(diagrams, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(project_name)} - 架构全景交互画板</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
  <style>
    :root {{
      --bg-primary: #0f172a;
      --bg-secondary: #1e293b;
      --bg-board: #0b0f19;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0ea5e9;
      --border: #334155;
      --card-bg: #1e293b;
    }}
    [data-theme="light"] {{
      --bg-primary: #f8fafc;
      --bg-secondary: #f1f5f9;
      --bg-board: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #64748b;
      --accent: #0284c7;
      --accent-hover: #0369a1;
      --border: #cbd5e1;
      --card-bg: #ffffff;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: background-color 0.2s, color 0.2s;
    }}
    header {{
      height: 56px;
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      flex-shrink: 0;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 16px;
      font-weight: 600;
    }}
    .badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 9999px;
      background-color: #10b981;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .controls {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    button, .btn {{
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 500;
      border-radius: 6px;
      border: 1px solid var(--border);
      background-color: var(--bg-primary);
      color: var(--text-primary);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }}
    button:hover, .btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
    }}
    .btn-primary {{
      background-color: var(--accent);
      color: #ffffff !important;
      border-color: var(--accent);
    }}
    .btn-primary:hover {{
      background-color: var(--accent-hover);
    }}
    nav.tabs {{
      height: 44px;
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      padding: 0 16px;
      gap: 8px;
      overflow-x: auto;
      flex-shrink: 0;
    }}
    .tab {{
      padding: 6px 14px;
      font-size: 13px;
      border-radius: 6px;
      color: var(--text-secondary);
      cursor: pointer;
      white-space: nowrap;
      border: 1px solid transparent;
      transition: all 0.15s;
    }}
    .tab:hover {{
      color: var(--text-primary);
      background-color: rgba(255, 255, 255, 0.05);
    }}
    .tab.active {{
      color: var(--accent);
      background-color: var(--bg-primary);
      border-color: var(--border);
      font-weight: 600;
    }}
    main {{
      flex: 1;
      position: relative;
      background-color: var(--bg-board);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    #viewer-container {{
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: grab;
    }}
    #viewer-container:active {{
      cursor: grabbing;
    }}
    .mermaid-render {{
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .zoom-toolbar {{
      position: absolute;
      bottom: 24px;
      right: 24px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      z-index: 10;
    }}
    .zoom-toolbar button {{
      width: 32px;
      height: 32px;
      padding: 0;
      justify-content: center;
      border: none;
      background: transparent;
    }}
    .empty-state {{
      text-align: center;
      color: var(--text-secondary);
      padding: 40px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span>📐 {html.escape(project_name)}</span>
      <span class="badge">{html.escape(status_tag)}</span>
      <span style="font-size: 12px; color: var(--text-secondary); font-weight: normal;">Archify-Style Interactive Board</span>
    </div>
    <div class="controls">
      <button id="theme-toggle" title="切换浅色/深色主题">🌓 主题</button>
      <button id="export-svg" class="btn" title="导出当前视图为高清矢量 SVG">📥 导出 SVG</button>
      <button id="reset-view" class="btn btn-primary" title="重置视角到居中">🎯 重置视角</button>
    </div>
  </header>

  <nav class="tabs" id="tab-nav"></nav>

  <main>
    <div id="viewer-container">
      <div id="graph-target" class="mermaid-render"></div>
    </div>
    <div class="zoom-toolbar">
      <button id="zoom-in" title="放大">+</button>
      <button id="zoom-out" title="缩小">−</button>
      <button id="zoom-reset" title="适应画布">⟲</button>
    </div>
  </main>

  <script>
    const diagrams = {diagrams_json};
    let currentIdx = 0;
    let panZoomInstance = null;
    let currentTheme = localStorage.getItem("archify_theme") || "dark";

    document.documentElement.setAttribute("data-theme", currentTheme);

    function initMermaid(theme) {{
      if (typeof mermaid === "undefined") return;
      mermaid.initialize({{
        startOnLoad: false,
        theme: theme === "dark" ? "dark" : "default",
        securityLevel: "loose",
        flowchart: {{ useMaxWidth: false, htmlLabels: true, curve: "basis" }},
        themeVariables: theme === "dark" ? {{
          darkMode: true,
          background: "#0b0f19",
          primaryColor: "#1e3a8a",
          primaryTextColor: "#f8fafc",
          primaryBorderColor: "#3b82f6",
          lineColor: "#64748b",
          secondaryColor: "#1e293b",
          tertiaryColor: "#0f172a"
        }} : {{
          darkMode: false,
          background: "#ffffff",
          primaryColor: "#eff6ff",
          primaryTextColor: "#0f172a",
          primaryBorderColor: "#2563eb",
          lineColor: "#475569"
        }}
      }});
    }}

    function renderDiagram(index) {{
      currentIdx = index;
      const nav = document.getElementById("tab-nav");
      Array.from(nav.children).forEach((el, i) => {{
        el.className = "tab " + (i === index ? "active" : "");
      }});

      const target = document.getElementById("graph-target");
      if (panZoomInstance) {{
        panZoomInstance.destroy();
        panZoomInstance = null;
      }}
      target.innerHTML = "";

      if (!diagrams || diagrams.length === 0) {{
        target.innerHTML = '<div class="empty-state">当前工作区暂无可渲染的架构图表。请先运行状态机生成 02-models/ 下的图元资产。</div>';
        return;
      }}

      const item = diagrams[index];
      const code = item.code.trim();
      const uniqueId = "render_" + Math.random().toString(36).substr(2, 9);

      if (typeof mermaid === "undefined") {{
        const escapedCode = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        target.innerHTML = `
          <div class="empty-state" style="max-width: 680px; text-align: left; background: var(--card-bg); padding: 24px; border-radius: 8px; border: 1px solid var(--border);">
            <div style="font-size: 16px; font-weight: 600; color: #f59e0b; margin-bottom: 8px;">
              ⚠️ 当前处于离线/物理隔离专网环境 (Mermaid 脚本未就绪)
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.6;">
              检测到外部 CDN (<a href="https://cdn.jsdelivr.net" target="_blank" style="color: var(--accent);">cdn.jsdelivr.net</a>) 无法连通。
              图表数据完整无损，您可以在本地内网搭建静态代理，或在下方直接查阅该图的确定性 Mermaid 架构源码：
            </div>
            <pre style="background: var(--bg-board); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; overflow-x: auto; color: var(--text-primary); border: 1px solid var(--border);">${{escapedCode}}</pre>
          </div>
        `;
        return;
      }}

      mermaid.render(uniqueId, code).then(({{ svg }}) => {{
        target.innerHTML = svg;
        const svgElement = target.querySelector("svg");
        if (svgElement) {{
          svgElement.style.width = "100%";
          svgElement.style.height = "100%";
          panZoomInstance = svgPanZoom(svgElement, {{
            zoomEnabled: true,
            controlIconsEnabled: false,
            fit: true,
            center: true,
            minZoom: 0.2,
            maxZoom: 10
          }});
        }}
      }}).catch(err => {{
        target.innerHTML = '<div class="empty-state" style="color:#ef4444;">图表渲染语法异常:<br><pre>' + err.message + '</pre></div>';
      }});
    }}

    // 初始化导航 Tab
    const tabNav = document.getElementById("tab-nav");
    diagrams.forEach((d, i) => {{
      const tab = document.createElement("div");
      tab.className = "tab " + (i === 0 ? "active" : "");
      tab.textContent = d.title;
      tab.onclick = () => renderDiagram(i);
      tabNav.appendChild(tab);
    }});

    // 控制按钮逻辑
    document.getElementById("theme-toggle").onclick = () => {{
      currentTheme = currentTheme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", currentTheme);
      localStorage.setItem("archify_theme", currentTheme);
      initMermaid(currentTheme);
      renderDiagram(currentIdx);
    }};

    document.getElementById("zoom-in").onclick = () => panZoomInstance && panZoomInstance.zoomIn();
    document.getElementById("zoom-out").onclick = () => panZoomInstance && panZoomInstance.zoomOut();
    document.getElementById("zoom-reset").onclick = () => {{
      if (panZoomInstance) {{
        panZoomInstance.reset();
        panZoomInstance.fit();
        panZoomInstance.center();
      }}
    }};
    document.getElementById("reset-view").onclick = () => {{
      if (panZoomInstance) {{
        panZoomInstance.reset();
        panZoomInstance.fit();
        panZoomInstance.center();
      }}
    }};

    document.getElementById("export-svg").onclick = () => {{
      const svgEl = document.querySelector("#graph-target svg");
      if (!svgEl) return;
      const serializer = new XMLSerializer();
      const source = serializer.serializeToString(svgEl);
      const blob = new Blob([source], {{ type: "image/svg+xml;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = (diagrams[currentIdx]?.title || "architecture-diagram") + ".svg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }};

    // 启动首次渲染
    initMermaid(currentTheme);
    renderDiagram(0);
  </script>
</body>
</html>
"""
    return html_template


def render_board(
    workspace_root: Path | str,
    output_path: Optional[Path | str] = None,
    project_name: str = "Architecture Lifecycle Canvas",
) -> Path:
    """搜集工作区下的模型图表并渲染为自包含 HTML 画板.

    Args:
        workspace_root: 架构资产根目录 (通常为 docs/architecture)
        output_path: 编译输出的 HTML 文件路径
        project_name: 项目显示名称

    Returns:
        Path: 生成的 HTML 绝对路径
    """
    ws = Path(workspace_root).resolve()
    # 优先使用全新系统架构设计目录 02-architecture-design，若无则使用 02-models
    models_dir = ws / "02-architecture-design"
    if not models_dir.exists() and (ws / "02-models").exists():
        models_dir = ws / "02-models"
    models_dir.mkdir(parents=True, exist_ok=True)

    # 支持优先专用图元文件，其次回退到相关规范文件
    fsm_file = models_dir / "lifecycle-fsm.mmd"
    if not fsm_file.exists():
        fsm_file = models_dir / "domain-logical-model.md"

    context_file = models_dir / "c4-context.mmd"
    if not context_file.exists():
        context_file = models_dir / "aod.mmd"

    container_file = models_dir / "c4-container-overview.mmd"
    if not container_file.exists():
        container_file = models_dir / "component-model.mmd"

    diagram_sources: List[Tuple[str, Path]] = [
        ("🌐 AOD / C4 Context (L1 全局概览)", context_file),
        ("⚙️ Component Model / C4 Container (L2 逻辑组件拓扑)", container_file),
        ("🔄 Lifecycle FSM (L3 状态与不变量流转)", fsm_file),
        ("⏱️ Interaction Sequence (L4 交互时序协议)", models_dir / "interaction-sequence.mmd"),
        ("🌊 Data Flow Pipeline (L5 数据分级管道)", models_dir / "data-flow.mmd"),
    ]

    diagrams: List[Dict[str, str]] = []
    for title, file_path in diagram_sources:
        if file_path.exists():
            code = extract_mermaid_code(file_path)
            if code:
                is_valid, err_msg = validate_mermaid_syntax(code)
                if not is_valid:
                    print(f"⚠️ [Mermaid语法警告] {file_path.name} 存在语法隐患: {err_msg}", file=sys.stderr)
                diagrams.append({"title": title, "code": code, "file": file_path.name})

    # 若未找到任何图，读取 sample 默认图保证展示
    if not diagrams:
        diagrams.append({
            "title": "⚙️ 待生成架构拓扑",
            "code": "graph TD\n    A[启动架构状态机] --> B[调用 02_structural_modeling 技能]\n    B --> C[生成 5 维高保真模型]\n",
            "file": "placeholder.mmd"
        })

    html_content = build_interactive_html(
        project_name=project_name,
        diagrams=diagrams,
        metadata={"status": "ACTIVE"},
    )

    out = Path(output_path).resolve() if output_path else ws / "architecture_board.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_content, encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    target_ws = sys.argv[1] if len(sys.argv) > 1 else "."
    proj_name = sys.argv[2] if len(sys.argv) > 2 else Path(target_ws).resolve().parent.parent.name
    generated_path = render_board(target_ws, project_name=proj_name)
    print(f"Architecture board generated at: {generated_path}")

